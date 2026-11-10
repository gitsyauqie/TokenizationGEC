#!/usr/bin/env python3
"""Step18 (M4): GEC-style metrics for the frozen 18-run controlled test.

Reads saved predictions only (no training, inference or checkpoint selection) and adds two
correction-oriented views to the reconstruction metrics:
- Edit-level precision, recall and F0.5. Edits are extracted on the shared surface tokens by a
  Levenshtein alignment of source->reference (gold) and source->hypothesis (system); an edit is a
  (source span, replacement tokens) pair and counts as correct only when it matches a gold edit
  exactly. Two edit granularities: MERGED (adjacent non-matching operations form one edit; primary)
  and ATOMIC (each substituted/deleted token is its own edit; consecutive insertions grouped).
  Conventions follow ERRANT: P=1 when no edits are proposed, R=1 when no gold edits exist.
  This is a language-agnostic approximation of M2/ERRANT scoring, not ERRANT itself.
- GLEU (Napoles et al. 2015; 2016 update with 2017 brevity-penalty fix), single reference, corpus level.
Uncertainty and significance reuse the M3 design: paired bootstrap stratified by category,
approximate randomization with shared swap masks across seeds, Holm over the six primary tests.
"""
import argparse
import csv
import hashlib
import json

import platform
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

TAGS = ['spbpe_5k', 'spbpe_20k', 'wp_5k', 'wp_20k', 'spuni_5k', 'spuni_20k']
SEEDS = [42, 43, 44]
PRIMARY = [('spbpe_5k', 'spbpe_20k', 'vocab'), ('wp_5k', 'wp_20k', 'vocab'),
           ('spuni_5k', 'spuni_20k', 'vocab'), ('spbpe_5k', 'wp_5k', 'family_5k'),
           ('spbpe_5k', 'spuni_5k', 'family_5k'), ('wp_5k', 'spuni_5k', 'family_5k')]
SECONDARY = [('spbpe_20k', 'wp_20k', 'family_20k'), ('spbpe_20k', 'spuni_20k', 'family_20k'),
             ('wp_20k', 'spuni_20k', 'family_20k')]
# columns: merged tp/fp/fn, atomic tp/fp/fn, GLEU c, r, (num,den) x 4, changed
C_M, C_A, C_G, C_CH = 0, 3, 6, 16
K = 17
METRICS = ['f05', 'precision', 'recall', 'f05_atomic', 'gleu']
TESTED = ['f05', 'gleu', 'f05_atomic']
BETA = 0.5


# ---------------------------------------------------------------- edits
def align_ops(a, b):
    """Minimal Levenshtein alignment of token lists a->b; deterministic tie-break M > S > D > I."""
    n, m = len(a), len(b)
    D = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        D[i][0] = i
    for j in range(1, m + 1):
        D[0][j] = j
    for i in range(1, n + 1):
        ai = a[i - 1]; row, prev = D[i], D[i - 1]
        for j in range(1, m + 1):
            sub = prev[j - 1] + (0 if ai == b[j - 1] else 1)
            row[j] = min(sub, prev[j] + 1, row[j - 1] + 1)
    ops = []; i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i - 1] == b[j - 1] and D[i][j] == D[i - 1][j - 1]:
            ops.append(('M', i - 1, j - 1)); i -= 1; j -= 1
        elif i > 0 and j > 0 and D[i][j] == D[i - 1][j - 1] + 1:
            ops.append(('S', i - 1, j - 1)); i -= 1; j -= 1
        elif i > 0 and D[i][j] == D[i - 1][j] + 1:
            ops.append(('D', i - 1, j)); i -= 1
        else:
            ops.append(('I', i, j - 1)); j -= 1
    ops.reverse()
    return ops


def extract_edits(src, tgt):
    """Return (merged, atomic) edit sets; each edit = (start, end, replacement tuple) on source indices."""
    if src == tgt:
        return set(), set()
    p = 0
    while p < len(src) and p < len(tgt) and src[p] == tgt[p]:
        p += 1
    q = 0
    while q < len(src) - p and q < len(tgt) - p and src[-1 - q] == tgt[-1 - q]:
        q += 1
    a, b = src[p:len(src) - q], tgt[p:len(tgt) - q]
    ops = align_ops(a, b)
    merged, atomic = set(), set()
    k = 0
    while k < len(ops):
        if ops[k][0] == 'M':
            k += 1; continue
        start_i, start_j = ops[k][1], ops[k][2]
        end_i, end_j = start_i, start_j
        run = []
        while k < len(ops) and ops[k][0] != 'M':
            op, i, j = ops[k]; run.append(ops[k])
            if op in ('S', 'D'):
                end_i = i + 1
            if op in ('S', 'I'):
                end_j = j + 1
            k += 1
        merged.add((start_i + p, end_i + p, tuple(b[start_j:end_j])))
        ins = None
        for op, i, j in run:
            if op == 'I':
                if ins is not None and ins[0] == i:
                    ins = (i, ins[1] + (b[j],))
                else:
                    if ins is not None:
                        atomic.add((ins[0] + p, ins[0] + p, ins[1]))
                    ins = (i, (b[j],))
            else:
                if ins is not None:
                    atomic.add((ins[0] + p, ins[0] + p, ins[1])); ins = None
                atomic.add((i + p, i + 1 + p, (b[j],) if op == 'S' else ()))
        if ins is not None:
            atomic.add((ins[0] + p, ins[0] + p, ins[1]))
    return merged, atomic


# ---------------------------------------------------------------- GLEU
def _ngrams(tokens, n):
    return Counter(tuple(tokens[i:i + n]) for i in range(len(tokens) + 1 - n))


def gleu_sentence_stats(src, ref, hyp):
    """Official gleu.py (Napoles et al., 2016/2017) statistics for one sentence, single reference."""
    out = [len(hyp), len(ref)]
    for n in range(1, 5):
        h, s, r = _ngrams(hyp, n), _ngrams(src, n), _ngrams(ref, n)
        s_diff = Counter(s)
        for k in set(s) & set(r):
            del s_diff[k]
        out.append(max(sum((h & r).values()) - sum((h & s_diff).values()), 0))
        out.append(max(len(hyp) + 1 - n, 0))
    return out


def sentence_stats(item):
    src, ref, hyp, gold = item
    s, r, h = src.split(), ref.split(), hyp.split()
    gm, ga = gold
    hm, ha = extract_edits(s, h)
    row = [len(hm & gm), len(hm - gm), len(gm - hm), len(ha & ga), len(ha - ga), len(ga - ha)]
    row += gleu_sentence_stats(s, r, h)
    row.append(int(hyp != src))
    return row


def _chunk(items):
    return [sentence_stats(x) for x in items]


def _gold_chunk(pairs):
    return [extract_edits(s.split(), r.split()) for s, r in pairs]


def pmap(fn, items, workers, size=2000):
    chunks = [items[i:i + size] for i in range(0, len(items), size)]
    if workers > 1:
        with Pool(workers) as pool:
            parts = pool.map(fn, chunks)
    else:
        parts = [fn(c) for c in chunks]
    return [x for part in parts for x in part]


# ---------------------------------------------------------------- vectorized corpus metrics
def prf(tp, fp, fn):
    p = np.where(fp > 0, tp / np.maximum(tp + fp, 1), 1.0)
    r = np.where(fn > 0, tp / np.maximum(tp + fn, 1), 1.0)
    b2 = BETA ** 2
    f = np.where((p + r) > 0, (1 + b2) * p * r / np.maximum(b2 * p + r, 1e-300), 0.0)
    return 100 * p, 100 * r, 100 * f


def gleu_from(T):
    c, r = T[:, C_G], T[:, C_G + 1]
    nums, dens = T[:, C_G + 2:C_G + 10:2], T[:, C_G + 3:C_G + 10:2]
    zero = (np.min(T[:, C_G:C_G + 10], axis=1) == 0)
    logp = np.sum(np.log(np.maximum(nums, 1e-300) / np.maximum(dens, 1e-300)), axis=1) / 4
    val = np.exp(np.minimum(0, 1 - r / np.maximum(c, 1e-300)) + logp)
    return np.where(zero, 0.0, 100 * val)


def metrics_from(T):
    T = np.atleast_2d(T)
    p, r, f = prf(T[:, C_M], T[:, C_M + 1], T[:, C_M + 2])
    _, _, fa = prf(T[:, C_A], T[:, C_A + 1], T[:, C_A + 2])
    return {'f05': f, 'precision': p, 'recall': r, 'f05_atomic': fa, 'gleu': gleu_from(T)}


# ---------------------------------------------------------------- helpers
def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def read_lines(path):
    with open(path, encoding='utf-8') as f:
        rows = [x.rstrip('\n') for x in f]
    if rows and rows[-1] == '':
        rows = rows[:-1]
    return rows


def holm(pvals):
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    adj = [0.0] * len(pvals); running = 0.0; m = len(pvals)
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvals[i])); adj[i] = running
    return adj


def ci(x):
    lo, hi = np.percentile(x, [2.5, 97.5]); return float(lo), float(hi)


def write_csv(path, rows):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--test-dir', default='controlled_test_v1')
    ap.add_argument('--cache', type=Path, default=None)
    ap.add_argument('--bootstrap', type=int, default=2000)
    ap.add_argument('--permutations', type=int, default=10000)
    ap.add_argument('--chunk', type=int, default=100)
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--seed', type=int, default=20261028)
    ap.add_argument('--expected-n', type=int, default=134025)
    ap.add_argument('--exclude-ids', type=Path, default=None,
                    help='file with zero-based test IDs to drop AFTER the full-test gates (sensitivity analysis)')
    ap.add_argument('--extended-epoch', type=int, default=0,
                    help='read extended_seed<S>/<tag>_seed<S>/test_epochNN instead of the frozen 10-epoch runs')
    a = ap.parse_args()
    t0 = time.time()
    root = a.root.resolve(); test = root / a.test_dir; out = a.out.resolve()
    if out.exists():
        ap.error('Output exists; choose a fresh directory.')
    cache = (a.cache or root / 'gec_metrics_cache').resolve(); cache.mkdir(parents=True, exist_ok=True)

    source = read_lines(test / 'test.source'); ref = read_lines(test / 'test.target')
    cats = read_lines(test / 'test.category'); n = len(ref)
    if n != a.expected_n or len(source) != n or len(cats) != n:
        raise ValueError('Test coverage invalid')
    def run_dir(tag, seed):
        if a.extended_epoch:
            return root / ('extended_seed%d' % seed) / ('%s_seed%d' % (tag, seed)) / ('test_epoch%02d' % a.extended_epoch)
        return test / ('%s_seed%d' % (tag, seed))
    if a.extended_epoch:
        stored = {}
        for tag in TAGS:
            for seed in SEEDS:
                d = json.loads((run_dir(tag, seed) / 'scores.json').read_text())
                if d.get('epoch') != a.extended_epoch or d['tag'] != tag or d['seed'] != seed:
                    raise ValueError('Unexpected extended scores.json for %s seed %d' % (tag, seed))
                stored[(tag, seed)] = d
    else:
        stored = {(r['tag'], r['seed']): r for r in json.loads((test / 'all_scores.json').read_text())}
    inputs = {str(p.relative_to(root)): sha256(p) for p in [test / 'test.source', test / 'test.target', test / 'test.category']}
    systems = {'COPY_INPUT': source, 'REFERENCE_ORACLE': ref}
    for tag in TAGS:
        for seed in SEEDS:
            name = '%s_seed%d' % (tag, seed); pred = run_dir(tag, seed) / 'predictions.jsonl'
            digest = sha256(pred)
            if digest != stored[(tag, seed)]['predictions_sha256']:
                raise ValueError('Prediction hash mismatch: ' + name)
            hyp = []
            with pred.open(encoding='utf-8') as f:
                for i, line in enumerate(f):
                    rec = json.loads(line)
                    if rec['id'] != i or rec['category'] != cats[i]:
                        raise ValueError('ID/category mismatch %s row %d' % (name, i))
                    hyp.append(rec['hypothesis'])
            if len(hyp) != n:
                raise ValueError('Coverage mismatch ' + name)
            systems[name] = hyp; inputs[str(pred.relative_to(root))] = digest
            # exact match must reproduce the stored score (same strings as controlled_test_v1)
            em = 100.0 * sum(h == r for h, r in zip(hyp, ref)) / n
            if abs(em - stored[(tag, seed)]['overall']['exact_match_pct']) > 1e-6:
                raise ValueError('Exact match does not reproduce stored score: ' + name)
    print('Inputs verified: %d systems x %d rows' % (len(systems), n), flush=True)

    print('Gold edits (source -> reference)', flush=True)
    gold = pmap(_gold_chunk, list(zip(source, ref)), a.workers)
    gold_counts = np.array([len(g[0]) for g in gold])
    key0 = hashlib.sha256((sha256(__file__) + inputs[str((test / 'test.target').relative_to(root))]).encode()).hexdigest()[:16]
    S = {}
    for name, hyp in systems.items():
        key = hashlib.sha256((key0 + '\n'.join(hyp)).encode('utf-8')).hexdigest()[:24]
        path = cache / ('%s_%s.npy' % (name, key))
        if path.exists():
            S[name] = np.load(path)
        else:
            print('Statistics: ' + name, flush=True)
            S[name] = np.array(pmap(_chunk, list(zip(source, ref, hyp, gold)), a.workers), dtype=np.float64)
            np.save(path, S[name])
    del systems

    # sanity gates
    m_or = metrics_from(S['REFERENCE_ORACLE'].sum(0)); m_cp = metrics_from(S['COPY_INPUT'].sum(0))
    if abs(m_or['f05'][0] - 100) > 1e-9 or abs(m_or['f05_atomic'][0] - 100) > 1e-9 or abs(m_or['gleu'][0] - 100) > 1e-9:
        raise ValueError('Oracle sanity failed: %s' % {k: float(v[0]) for k, v in m_or.items()})
    if m_cp['f05'][0] != 0 or m_cp['recall'][0] != 0 or S['COPY_INPUT'][:, C_M + 1].sum() != 0:
        raise ValueError('COPY sanity failed')
    print('Sanity gates passed (oracle F0.5 = GLEU = 100; COPY proposes no edits)', flush=True)
    del S['REFERENCE_ORACLE']

    labels = sorted(set(cats))
    kept = list(range(n)); excluded_info = None
    if a.exclude_ids:
        ex = set(int(x) for x in a.exclude_ids.read_text().split() if x.strip())
        if not ex or min(ex) < 0 or max(ex) >= n:
            raise ValueError('Exclusion IDs empty or out of range')
        kept = [i for i in range(n) if i not in ex]
        excluded_info = {'file': str(a.exclude_ids), 'sha256': sha256(a.exclude_ids), 'n_excluded': len(ex), 'n_kept': len(kept)}
        print('Sensitivity subset: %d rows excluded, %d kept' % (len(ex), len(kept)), flush=True)
    perm = np.array(sorted(kept, key=lambda i: (cats[i], i)))
    n = len(perm)
    for k in S:
        S[k] = S[k][perm]
    sorted_cats = [cats[i] for i in perm]; gold_sorted = gold_counts[perm]
    slices = {}; start = 0
    for c in labels:
        size = sum(1 for x in sorted_cats if x == c); slices[c] = (start, start + size); start += size
    names = list(S); rng = np.random.default_rng(a.seed)
    run = lambda tag, seed: '%s_seed%d' % (tag, seed)
    point = {nm: {k: float(v[0]) for k, v in metrics_from(S[nm].sum(0)).items()} for nm in names}

    # stratified paired bootstrap
    B = a.bootstrap
    boot_all = {nm: np.zeros((B, K)) for nm in names}
    boot_cat = {c: {nm: np.zeros((B, K)) for nm in names} for c in labels}
    for b0 in range(0, B, a.chunk):
        b = min(a.chunk, B - b0)
        for c in labels:
            lo, hi = slices[c]; nc = hi - lo
            draws = rng.integers(0, nc, size=(b, nc)) + (np.arange(b)[:, None] * nc)
            W = np.bincount(draws.ravel(), minlength=b * nc).reshape(b, nc).astype(np.float64)
            for nm in names:
                T = W @ S[nm][lo:hi]; boot_cat[c][nm][b0:b0 + b] = T; boot_all[nm][b0:b0 + b] += T
        print('Bootstrap %d/%d' % (b0 + b, B), flush=True)
    m_all = {nm: metrics_from(boot_all[nm]) for nm in names}

    def approx_rand(A, Bt):
        pairs = [(run(A, s), run(Bt, s)) for s in SEEDS]
        D = [S[y] - S[x] for x, y in pairs]
        baseA = [S[x].sum(0) for x, _ in pairs]; baseB = [S[y].sum(0) for _, y in pairs]
        obs = {k: [point[x][k] - point[y][k] for x, y in pairs] for k in TESTED}
        exceed = {k: np.zeros(len(SEEDS) + 1) for k in TESTED}
        R = a.permutations
        for r0 in range(0, R, a.chunk):
            r = min(a.chunk, R - r0)
            M = (rng.random((r, n)) < 0.5).astype(np.float64)
            deltas = {k: [] for k in TESTED}
            for j in range(len(SEEDS)):
                shift = M @ D[j]
                mA = metrics_from(baseA[j] + shift); mB = metrics_from(baseB[j] - shift)
                for k in TESTED:
                    deltas[k].append(mA[k] - mB[k])
            for k in TESTED:
                for j in range(len(SEEDS)):
                    exceed[k][j] += np.sum(np.abs(deltas[k][j]) >= abs(obs[k][j]) - 1e-12)
                exceed[k][-1] += np.sum(np.abs(np.mean(deltas[k], axis=0)) >= abs(float(np.mean(obs[k]))) - 1e-12)
        return {k: ((exceed[k] + 1) / (R + 1)).tolist() for k in TESTED}

    # per-run and per-condition scores
    run_rows = []
    for nm in names:
        row = {'run': nm}; row.update({k: point[nm][k] for k in METRICS})
        row['changed_pct'] = 100.0 * S[nm][:, C_CH].sum() / n
        row['tp'], row['fp'], row['fn'] = [int(S[nm][:, C_M + i].sum()) for i in range(3)]
        run_rows.append(row)
    cond_rows = []
    for tag in TAGS:
        row = {'tag': tag}
        for k in METRICS + ['changed_pct']:
            vals = [next(r[k] for r in run_rows if r['run'] == run(tag, s)) for s in SEEDS]
            row[k + '_mean'] = float(np.mean(vals)); row[k + '_sd'] = float(np.std(vals, ddof=1))
        cond_rows.append(row)

    overall_rows, seed_rows = [], []
    for group, comps in [('primary', PRIMARY), ('secondary', SECONDARY)]:
        for A, Bt, kind in comps:
            print('Approximate randomization %s vs %s' % (A, Bt), flush=True)
            p = approx_rand(A, Bt)
            for k in METRICS:
                seed_d = [m_all[run(A, s)][k] - m_all[run(Bt, s)][k] for s in SEEDS]
                obs = [point[run(A, s)][k] - point[run(Bt, s)][k] for s in SEEDS]
                lo, hi = ci(np.mean(seed_d, axis=0))
                overall_rows.append(dict(group=group, kind=kind, model_a=A, model_b=Bt, metric=k,
                    delta_mean=float(np.mean(obs)), ci95_low=lo, ci95_high=hi,
                    p_ar=(p[k][-1] if k in TESTED else ''), seeds_a_better=sum(o > 0 for o in obs)))
                for j, s in enumerate(SEEDS):
                    lo, hi = ci(seed_d[j])
                    seed_rows.append(dict(group=group, kind=kind, model_a=A, model_b=Bt, seed=s, metric=k,
                        delta=obs[j], ci95_low=lo, ci95_high=hi, p_ar=(p[k][j] if k in TESTED else '')))
    for group in ('primary', 'secondary'):
        for k in TESTED:
            for rows in (overall_rows, seed_rows):
                idx = [i for i, r in enumerate(rows) if r['group'] == group and r['metric'] == k]
                for i, v in zip(idx, holm([rows[i]['p_ar'] for i in idx])):
                    rows[i]['p_holm'] = v
    for rows in (overall_rows, seed_rows):
        for r in rows:
            r.setdefault('p_holm', '')

    inter_rows = []
    for fa, fb in [('spbpe', 'spuni'), ('wp', 'spuni'), ('spbpe', 'wp')]:
        for k in ('f05', 'gleu'):
            did = np.mean([(m_all[run(fa + '_5k', s)][k] - m_all[run(fa + '_20k', s)][k])
                           - (m_all[run(fb + '_5k', s)][k] - m_all[run(fb + '_20k', s)][k]) for s in SEEDS], axis=0)
            obs = [(point[run(fa + '_5k', s)][k] - point[run(fa + '_20k', s)][k])
                   - (point[run(fb + '_5k', s)][k] - point[run(fb + '_20k', s)][k]) for s in SEEDS]
            lo, hi = ci(did)
            inter_rows.append(dict(family_a=fa, family_b=fb, metric=k, interaction=float(np.mean(obs)), ci95_low=lo, ci95_high=hi,
                                   p_boot_two_sided=float(min(1.0, 2 * min(np.mean(did <= 0), np.mean(did >= 0)))),
                                   seeds_positive=sum(o > 0 for o in obs)))

    # categories
    cat_rows, cat_scores = [], []
    for c in labels:
        lo_, hi_ = slices[c]; nc = hi_ - lo_
        mc = {nm: metrics_from(boot_cat[c][nm]) for nm in names}
        pc = {nm: {k: float(v[0]) for k, v in metrics_from(S[nm][lo_:hi_].sum(0)).items()} for nm in names}
        for tag in TAGS:
            row = {'category': c, 'n': nc, 'gold_edits_per_sentence': float(gold_sorted[lo_:hi_].mean()), 'tag': tag}
            for k in METRICS:
                vals = [pc[run(tag, s)][k] for s in SEEDS]
                row[k + '_mean'] = float(np.mean(vals)); row[k + '_sd'] = float(np.std(vals, ddof=1))
            row['changed_pct_mean'] = float(np.mean([100 * S[run(tag, s)][lo_:hi_, C_CH].mean() for s in SEEDS]))
            cat_scores.append(row)
        cat_scores.append({'category': c, 'n': nc, 'gold_edits_per_sentence': float(gold_sorted[lo_:hi_].mean()),
                           'tag': 'COPY_INPUT', **{k + '_mean': pc['COPY_INPUT'][k] for k in METRICS},
                           **{k + '_sd': 0.0 for k in METRICS}, 'changed_pct_mean': 0.0})
        comps = [(A, Bt, 'vocab') for A, Bt, kind in PRIMARY if kind == 'vocab'] + [(t, 'COPY_INPUT', 'vs_copy') for t in TAGS]
        for A, Bt, kind in comps:
            for k in METRICS:
                if Bt == 'COPY_INPUT':
                    d = np.mean([mc[run(A, s)][k] - mc['COPY_INPUT'][k] for s in SEEDS], axis=0)
                    obs = [pc[run(A, s)][k] - pc['COPY_INPUT'][k] for s in SEEDS]
                else:
                    d = np.mean([mc[run(A, s)][k] - mc[run(Bt, s)][k] for s in SEEDS], axis=0)
                    obs = [pc[run(A, s)][k] - pc[run(Bt, s)][k] for s in SEEDS]
                lo, hi = ci(d)
                cat_rows.append(dict(category=c, n=nc, kind=kind, model_a=A, model_b=Bt, metric=k,
                    delta_mean=float(np.mean(obs)), ci95_low=lo, ci95_high=hi,
                    seeds_a_better=sum(o > 0 for o in obs), ci_excludes_zero=bool(lo > 0 or hi < 0)))

    out.mkdir(parents=True)
    write_csv(out / 'gec_interaction.csv', inter_rows)
    write_csv(out / 'gec_runs.csv', run_rows); write_csv(out / 'gec_conditions.csv', cond_rows)
    write_csv(out / 'gec_paired_overall.csv', overall_rows); write_csv(out / 'gec_paired_per_seed.csv', seed_rows)
    write_csv(out / 'gec_category_scores.csv', cat_scores); write_csv(out / 'gec_paired_categories.csv', cat_rows)
    prov = {'script_sha256': sha256(__file__), 'inputs_sha256': inputs, 'python': sys.version, 'numpy': np.__version__,
            'platform': platform.platform(), 'n': n, 'bootstrap': B, 'permutations': a.permutations, 'rng_seed': a.seed,
            'gold_edits_total_merged': int(gold_counts.sum()), 'exclusion': excluded_info,
            'edits': 'Levenshtein token alignment on shared surface tokens (common prefix/suffix trimmed), tie-break match>sub>del>ins; MERGED = adjacent non-match ops form one edit (primary); ATOMIC = per-token sub/del, grouped consecutive insertions. Exact (span, replacement) match. ERRANT conventions for empty sets.',
            'gleu': 'Napoles et al. gleu.py (2016 multi-reference update, 2017 brevity fix), single reference, corpus statistics.',
            'gates': 'Exact match reproduces stored scores; oracle F0.5 = GLEU = 100; COPY proposes no edits.',
            'limits': 'Approximation of M2/ERRANT, not ERRANT; no partial credit for overlapping edits; single reference; intervals conditional on trained checkpoints.',
            'seconds': time.time() - t0}
    (out / 'provenance.json').write_text(json.dumps(prov, indent=2) + '\n', encoding='utf-8')

    f2 = lambda x: '%+.3f' % x
    md = ['# Step18 — GEC metrics (M4)' + (' — extended runs, test at epoch %d' % a.extended_epoch if a.extended_epoch else ' — frozen 10-epoch runs')
          + (' — SENSITIVITY: %d test rows excluded (%s)' % (excluded_info['n_excluded'], a.exclude_ids.name) if excluded_info else ''), '',
          '%d test rows; %d gold (merged) edits, %.2f per sentence. Gates passed: exact match reproduced, oracle = 100, COPY proposes no edits.' % (n, int(gold_sorted.sum()), gold_sorted.mean()), '',
          '## Conditions (mean ± SD over seeds)', '',
          '| Condition | P | R | F0.5 | F0.5 atomic | GLEU | Changed % |', '|---|---:|---:|---:|---:|---:|---:|']
    for r in cond_rows:
        md.append('| %s | %.2f ± %.2f | %.2f ± %.2f | %.2f ± %.2f | %.2f ± %.2f | %.2f ± %.2f | %.2f |' % (
            r['tag'], r['precision_mean'], r['precision_sd'], r['recall_mean'], r['recall_sd'], r['f05_mean'], r['f05_sd'],
            r['f05_atomic_mean'], r['f05_atomic_sd'], r['gleu_mean'], r['gleu_sd'], r['changed_pct_mean']))
    md.append('| COPY_INPUT | %.2f | %.2f | %.2f | %.2f | %.2f | 0.00 |' % (point['COPY_INPUT']['precision'], point['COPY_INPUT']['recall'],
              point['COPY_INPUT']['f05'], point['COPY_INPUT']['f05_atomic'], point['COPY_INPUT']['gleu']))
    md += ['', '## Primary comparisons, seed-mean (A − B)', '', '| A | B | Metric | Δ | 95% CI | p (AR) | p (Holm) | Seeds A>B |', '|---|---|---|---:|---|---:|---:|---:|']
    for r in overall_rows:
        if r['group'] == 'primary':
            md.append('| %s | %s | %s | %s | [%s, %s] | %s | %s | %d/3 |' % (r['model_a'], r['model_b'], r['metric'], f2(r['delta_mean']),
                      f2(r['ci95_low']), f2(r['ci95_high']), ('%.4f' % r['p_ar']) if r['p_ar'] != '' else '—',
                      ('%.4f' % r['p_holm']) if r['p_holm'] != '' else '—', r['seeds_a_better']))
    md += ['', '## Secondary (20K families)', '', '| A | B | Metric | Δ | 95% CI | p (Holm) |', '|---|---|---|---:|---|---:|']
    for r in overall_rows:
        if r['group'] == 'secondary' and r['metric'] in TESTED:
            md.append('| %s | %s | %s | %s | [%s, %s] | %.4f |' % (r['model_a'], r['model_b'], r['metric'], f2(r['delta_mean']),
                      f2(r['ci95_low']), f2(r['ci95_high']), r['p_holm']))
    md += ['', '## Category F0.5 and GLEU: 5K − 20K (seed-mean, descriptive)', '', '| Category | n | Gold edits/sent | A | Δ F0.5 | 95% CI | Δ GLEU | 95% CI |', '|---|---:|---:|---|---:|---|---:|---|']
    for c in labels:
        for A, Bt, kind in PRIMARY:
            if kind != 'vocab':
                continue
            f = next(r for r in cat_rows if r['category'] == c and r['model_a'] == A and r['model_b'] == Bt and r['metric'] == 'f05')
            g = next(r for r in cat_rows if r['category'] == c and r['model_a'] == A and r['model_b'] == Bt and r['metric'] == 'gleu')
            gs = next(r for r in cat_scores if r['category'] == c)
            md.append('| %s | %d | %.2f | %s | %s | [%s, %s] | %s | [%s, %s] |' % (c, f['n'], gs['gold_edits_per_sentence'], A,
                      f2(f['delta_mean']), f2(f['ci95_low']), f2(f['ci95_high']), f2(g['delta_mean']), f2(g['ci95_low']), f2(g['ci95_high'])))
    md += ['', '## Family x vocabulary interaction (A5K − A20K) − (B5K − B20K), seed-mean', '', '| A | B | Metric | Interaction | 95% CI | p (boot) | Seeds > 0 |', '|---|---|---|---:|---|---:|---:|']
    for r in inter_rows:
        md.append('| %s | %s | %s | %s | [%s, %s] | %.4f | %d/3 |' % (r['family_a'], r['family_b'], r['metric'], f2(r['interaction']),
                  f2(r['ci95_low']), f2(r['ci95_high']), r['p_boot_two_sided'], r['seeds_positive']))
    md += ['', 'Send back: REPORT.md, all gec_*.csv files and provenance.json.', '']
    (out / 'REPORT.md').write_text('\n'.join(md), encoding='utf-8')
    print('DONE in %.1f min -> %s' % ((time.time() - t0) / 60, out / 'REPORT.md'), flush=True)


if __name__ == '__main__':
    main()
