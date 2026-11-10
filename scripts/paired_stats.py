#!/usr/bin/env python3
"""Step16 (M3): paired uncertainty and significance for the frozen 18-run controlled test.

Reads saved predictions only: no training, inference, checkpoint selection, row dropping or
reference repair. Every metric is recomputed from per-sentence sufficient statistics and must
reproduce the stored controlled_test_v1 scores before any resampling is done.

Methods
- Paired bootstrap (Koehn 2004), stratified by the 12 original category labels; one shared set
  of resampled rows for all 19 systems, so every comparison is paired.
- Cluster bootstrap sensitivity: rows with an identical normalized reference form one cluster.
- Approximate randomization (Riezler & Maxwell 2005): per-sentence swap of the two systems'
  outputs; two-sided p = (1 + #|d*| >= |d|) / (R + 1). The same swap masks are applied to all
  three seed pairs, giving per-seed and seed-mean p-values.
- Holm correction within each metric over the six primary seed-mean comparisons, and separately
  over the 18 primary per-seed tests.
All inference is conditional on the three trained models per condition and on the fixed
tokenizer fits; it is not an estimate of training-seed variance.
"""
import argparse
import csv
import hashlib
import json
import math
import os
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
METRICS = ['chrf2_pct', 'bleu', 'exact_match_pct']
CHRF_ORDER, BETA, BLEU_ORDER = 6, 2.0, 4
K = 3 * CHRF_ORDER + 2 * BLEU_ORDER + 3   # 18 chrF + 8 BLEU + sys_len, ref_len, exact
C_BLEU_CORRECT, C_BLEU_TOTAL, C_SYS, C_REF, C_EXACT = 18, 22, 26, 27, 28
TOL = 1e-6


# ---------------------------------------------------------------- sufficient statistics
def _char_ngrams(s, n):
    return Counter(s[i:i + n] for i in range(len(s) - n + 1))


def _word_ngrams(tokens, n):
    return Counter(' '.join(tokens[i:i + n]) for i in range(len(tokens) - n + 1))


def sentence_stats(pair):
    """SacreBLEU 1.5.1 statistics: chrF (order 6, whitespace removed) and BLEU (tokenize none)."""
    h, r = pair
    out = [0] * K
    hs, rs = ''.join(h.split()), ''.join(r.split())
    for i in range(CHRF_ORDER):
        a, b = _char_ngrams(hs, i + 1), _char_ngrams(rs, i + 1)
        out[3 * i] = sum(a.values())
        out[3 * i + 1] = sum(b.values())
        out[3 * i + 2] = sum((a & b).values())
    ht, rt = h.split(), r.split()
    for i in range(BLEU_ORDER):
        a, b = _word_ngrams(ht, i + 1), _word_ngrams(rt, i + 1)
        out[C_BLEU_CORRECT + i] = sum((a & b).values())
        out[C_BLEU_TOTAL + i] = max(len(ht) - i, 0)
    out[C_SYS], out[C_REF], out[C_EXACT] = len(ht), len(rt), int(h == r)
    return out


def _chunk_stats(chunk):
    return [sentence_stats(p) for p in chunk]


def compute_stats(hyp, ref, workers):
    pairs = list(zip(hyp, ref))
    size = 2000
    chunks = [pairs[i:i + size] for i in range(0, len(pairs), size)]
    if workers > 1:
        with Pool(workers) as pool:
            parts = pool.map(_chunk_stats, chunks)
    else:
        parts = [_chunk_stats(c) for c in chunks]
    return np.array([row for part in parts for row in part], dtype=np.float64)


# ---------------------------------------------------------------- vectorized corpus metrics
def chrf_from(T):
    T = np.atleast_2d(T)
    prec = np.zeros(T.shape[0]); rec = np.zeros(T.shape[0]); eff = np.zeros(T.shape[0])
    for i in range(CHRF_ORDER):
        hy, rf, m = T[:, 3 * i], T[:, 3 * i + 1], T[:, 3 * i + 2]
        ok = (hy > 0) & (rf > 0)
        prec += np.where(ok, m / np.where(hy > 0, hy, 1), 0.0)
        rec += np.where(ok, m / np.where(rf > 0, rf, 1), 0.0)
        eff += ok
    prec = np.where(eff > 0, prec / np.maximum(eff, 1), 0.0)
    rec = np.where(eff > 0, rec / np.maximum(eff, 1), 0.0)
    b2 = BETA ** 2
    denom = b2 * prec + rec
    score = np.where((prec + rec) > 0, (1 + b2) * prec * rec / np.where(denom > 0, denom, 1), 0.0)
    return 100.0 * score


def bleu_from(T):
    T = np.atleast_2d(T)
    logsum = np.zeros(T.shape[0]); smooth = np.ones(T.shape[0])
    for n in range(BLEU_ORDER):
        c, t = T[:, C_BLEU_CORRECT + n], T[:, C_BLEU_TOTAL + n]
        if np.any(t == 0):
            raise ValueError('Zero %d-gram total: BLEU order truncation not supported here' % (n + 1))
        zero = c == 0
        smooth = np.where(zero, smooth * 2, smooth)
        p = np.where(zero, 100.0 / (smooth * t), 100.0 * c / t)
        logsum += np.log(p)
    sys_len, ref_len = T[:, C_SYS], T[:, C_REF]
    bp = np.where(sys_len < ref_len, np.exp(1 - ref_len / np.maximum(sys_len, 1)), 1.0)
    bp = np.where(sys_len == 0, 0.0, bp)
    return bp * np.exp(logsum / BLEU_ORDER)


def metrics_from(T, n):
    return {'chrf2_pct': chrf_from(T), 'bleu': bleu_from(T),
            'exact_match_pct': 100.0 * np.atleast_2d(T)[:, C_EXACT] / n}


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
        running = max(running, min(1.0, (m - rank) * pvals[i]))
        adj[i] = running
    return adj


def ci(x):
    lo, hi = np.percentile(x, [2.5, 97.5])
    return float(lo), float(hi)


def write_csv(path, rows):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)


def check(label, got, want):
    if abs(got - want) > TOL:
        raise ValueError('%s does not reproduce stored score: recomputed=%.10f stored=%.10f'
                         % (label, got, want))


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', type=Path, required=True, help='paper6_revision_20261007')
    ap.add_argument('--out', type=Path, required=True, help='fresh output directory')
    ap.add_argument('--test-dir', default='controlled_test_v1')
    ap.add_argument('--cache', type=Path, default=None, help='statistics cache (default <root>/paired_stats_cache)')
    ap.add_argument('--bootstrap', type=int, default=2000)
    ap.add_argument('--permutations', type=int, default=10000)
    ap.add_argument('--chunk', type=int, default=100)
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--seed', type=int, default=20261026)
    ap.add_argument('--expected-n', type=int, default=134025)
    ap.add_argument('--exclude-ids', type=Path, default=None,
                    help='file with zero-based test IDs to drop AFTER the full-test reproduction gate (sensitivity analysis)')
    ap.add_argument('--extended-epoch', type=int, default=0,
                    help='read extended_seed<S>/<tag>_seed<S>/test_epochNN instead of the frozen 10-epoch runs')
    a = ap.parse_args()
    t0 = time.time()
    root = a.root.resolve(); test = root / a.test_dir
    out = a.out.resolve()
    if out.exists():
        ap.error('Output exists; choose a fresh directory. Statistics are reused from --cache.')
    cache = (a.cache or root / 'paired_stats_cache').resolve(); cache.mkdir(parents=True, exist_ok=True)

    # ---- inputs and integrity
    source = read_lines(test / 'test.source'); ref = read_lines(test / 'test.target')
    cats = read_lines(test / 'test.category'); n = len(ref)
    if n != a.expected_n or len(source) != n or len(cats) != n:
        raise ValueError('Test coverage invalid: %d/%d/%d' % (len(source), n, len(cats)))
    def run_dir(tag, seed):
        if a.extended_epoch:
            return root / ('extended_seed%d' % seed) / ('%s_seed%d' % (tag, seed)) / ('test_epoch%02d' % a.extended_epoch)
        return test / ('%s_seed%d' % (tag, seed))
    if a.extended_epoch:
        stored_runs = {}
        for tag in TAGS:
            for seed in SEEDS:
                d = json.loads((run_dir(tag, seed) / 'scores.json').read_text())
                if d.get('epoch') != a.extended_epoch or d['tag'] != tag or d['seed'] != seed:
                    raise ValueError('Unexpected extended scores.json for %s seed %d' % (tag, seed))
                stored_runs[(tag, seed)] = d
    else:
        stored_runs = {(r['tag'], r['seed']): r for r in json.loads((test / 'all_scores.json').read_text())}
    baselines = json.loads((test / 'baselines.json').read_text())
    if set(stored_runs) != {(t, s) for t in TAGS for s in SEEDS}:
        raise ValueError('all_scores.json does not hold exactly the 18 expected runs')
    inputs = {str(p.relative_to(root)): sha256(p) for p in
              [test / 'test.source', test / 'test.target', test / 'test.category',
               test / 'all_scores.json', test / 'baselines.json']}

    systems = {}   # name -> hypotheses
    systems['COPY_INPUT'] = source
    for tag in TAGS:
        for seed in SEEDS:
            name = '%s_seed%d' % (tag, seed)
            folder = run_dir(tag, seed); pred = folder / 'predictions.jsonl'
            stored = json.loads((folder / 'scores.json').read_text())
            digest = sha256(pred)
            if digest != stored['predictions_sha256'] or digest != stored_runs[(tag, seed)]['predictions_sha256']:
                raise ValueError('Prediction hash mismatch: ' + name)
            hyp = []
            with pred.open(encoding='utf-8') as f:
                for i, line in enumerate(f):
                    rec = json.loads(line)
                    if rec['id'] != i or rec['category'] != cats[i]:
                        raise ValueError('ID/category order mismatch in %s at row %d' % (name, i))
                    hyp.append(rec['hypothesis'])
            if len(hyp) != n:
                raise ValueError('Prediction coverage mismatch: ' + name)
            systems[name] = hyp; inputs[str(pred.relative_to(root))] = digest
    print('Inputs verified: %d systems x %d rows' % (len(systems), n), flush=True)

    # ---- per-sentence statistics (cached by content hash)
    ref_hash = inputs[str((test / 'test.target').relative_to(root))]
    S = {}
    for name, hyp in systems.items():
        key = hashlib.sha256((ref_hash + '|' + '\n'.join(hyp)).encode('utf-8')).hexdigest()[:24]
        path = cache / ('%s_%s.npy' % (name, key))
        if path.exists():
            S[name] = np.load(path)
        else:
            print('Statistics: ' + name, flush=True)
            S[name] = compute_stats(hyp, ref, a.workers); np.save(path, S[name])
        if S[name].shape != (n, K):
            raise ValueError('Bad statistics shape: ' + name)
    del systems

    # ---- order rows by category so each stratum is a contiguous slice
    labels = sorted(set(cats))
    perm = np.array(sorted(range(n), key=lambda i: (cats[i], i)))
    for name in S:
        S[name] = S[name][perm]
    sorted_cats = [cats[i] for i in perm]
    slices = {}
    start = 0
    for c in labels:
        size = sum(1 for x in sorted_cats if x == c)
        slices[c] = (start, start + size); start += size

    # ---- reproduction gate: every stored overall and category score
    def full_metrics(name, lo=0, hi=n):
        return {k: float(v[0]) for k, v in metrics_from(S[name][lo:hi].sum(0), hi - lo).items()}
    for tag in TAGS:
        for seed in SEEDS:
            name = '%s_seed%d' % (tag, seed); stored = stored_runs[(tag, seed)]
            got = full_metrics(name)
            for k in METRICS:
                check(name + ' overall ' + k, got[k], stored['overall'][k])
            for c in stored['categories']:
                lo, hi = slices[c['category']]
                if hi - lo != c['n']:
                    raise ValueError('Category size mismatch %s %s' % (name, c['category']))
                gotc = full_metrics(name, lo, hi)
                for k in METRICS:
                    check('%s %s %s' % (name, c['category'], k), gotc[k], c[k])
    copy = baselines['COPY_INPUT']; got = full_metrics('COPY_INPUT')
    for k in METRICS:
        check('COPY_INPUT overall ' + k, got[k], copy['overall'][k])
    for c in copy['categories']:
        lo, hi = slices[c['category']]; gotc = full_metrics('COPY_INPUT', lo, hi)
        for k in METRICS:
            check('COPY_INPUT %s %s' % (c['category'], k), gotc[k], c[k])
    print('Reproduction gate passed: all overall and category scores match stored values', flush=True)

    excluded_info = None
    if a.exclude_ids:
        ex = set(int(x) for x in a.exclude_ids.read_text().split() if x.strip())
        if not ex or min(ex) < 0 or max(ex) >= n:
            raise ValueError('Exclusion IDs empty or out of range')
        keep = np.array([int(i) not in ex for i in perm])
        perm = perm[keep]
        for name in S:
            S[name] = S[name][keep]
        sorted_cats = [cats[i] for i in perm]
        slices = {}; start = 0
        for c in labels:
            size = sum(1 for x in sorted_cats if x == c)
            if size == 0:
                raise ValueError('Exclusion removes the whole category ' + c)
            slices[c] = (start, start + size); start += size
        n = len(perm)

        def full_metrics(name, lo=0, hi=None):
            hi = n if hi is None else hi
            return {k: float(v[0]) for k, v in metrics_from(S[name][lo:hi].sum(0), hi - lo).items()}
        excluded_info = {'file': str(a.exclude_ids), 'sha256': sha256(a.exclude_ids), 'n_excluded': len(ex), 'n_kept': n}
        print('Sensitivity subset: %d rows excluded, %d kept' % (len(ex), n), flush=True)

    names = list(S)
    rng = np.random.default_rng(a.seed)

    # ---- stratified paired bootstrap: overall + per-category resampled statistics
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
                T = W @ S[nm][lo:hi]
                boot_cat[c][nm][b0:b0 + b] = T; boot_all[nm][b0:b0 + b] += T
        print('Stratified bootstrap %d/%d' % (b0 + b, B), flush=True)

    # ---- cluster bootstrap (identical normalized reference), overall only
    sorted_ref = [ref[i] for i in perm]
    cluster_index = {}
    cid = np.array([cluster_index.setdefault(r, len(cluster_index)) for r in sorted_ref])
    ncl = len(cluster_index)
    boot_cl = {nm: np.zeros((B, K)) for nm in names}
    boot_cl_rows = []
    for b0 in range(0, B, a.chunk):
        b = min(a.chunk, B - b0)
        draws = rng.integers(0, ncl, size=(b, ncl)) + (np.arange(b)[:, None] * ncl)
        Wc = np.bincount(draws.ravel(), minlength=b * ncl).reshape(b, ncl).astype(np.float64)
        W = Wc[:, cid]
        rows_drawn = W.sum(1)
        for nm in names:
            boot_cl[nm][b0:b0 + b] = W @ S[nm]
        boot_cl_rows.extend(rows_drawn.tolist())
        print('Cluster bootstrap %d/%d' % (b0 + b, B), flush=True)
    boot_cl_rows = np.array(boot_cl_rows)

    def mets(T, nrows):
        return metrics_from(T, nrows)

    m_all = {nm: mets(boot_all[nm], n) for nm in names}
    m_cl = {nm: {'chrf2_pct': chrf_from(boot_cl[nm]), 'bleu': bleu_from(boot_cl[nm]),
                 'exact_match_pct': 100.0 * boot_cl[nm][:, C_EXACT] / boot_cl_rows} for nm in names}
    point = {nm: full_metrics(nm) for nm in names}
    run = lambda tag, seed: '%s_seed%d' % (tag, seed)

    # ---- approximate randomization (shared masks across the three seed pairs)
    def approx_rand(A, Bt):
        pairs = [(run(A, s), run(Bt, s)) for s in SEEDS]
        D = [S[y] - S[x] for x, y in pairs]
        baseA = [S[x].sum(0) for x, _ in pairs]; baseB = [S[y].sum(0) for _, y in pairs]
        obs = {k: [point[x][k] - point[y][k] for x, y in pairs] for k in METRICS}
        exceed = {k: np.zeros(len(SEEDS) + 1) for k in METRICS}
        R = a.permutations
        for r0 in range(0, R, a.chunk):
            r = min(a.chunk, R - r0)
            M = (rng.random((r, n)) < 0.5).astype(np.float64)
            deltas = {k: [] for k in METRICS}
            for j in range(len(SEEDS)):
                shift = M @ D[j]
                mA = metrics_from(baseA[j] + shift, n); mB = metrics_from(baseB[j] - shift, n)
                for k in METRICS:
                    deltas[k].append(mA[k] - mB[k])
            for k in METRICS:
                for j in range(len(SEEDS)):
                    exceed[k][j] += np.sum(np.abs(deltas[k][j]) >= abs(obs[k][j]) - 1e-12)
                mean_d = np.mean(deltas[k], axis=0); mean_obs = float(np.mean(obs[k]))
                exceed[k][-1] += np.sum(np.abs(mean_d) >= abs(mean_obs) - 1e-12)
        return {k: ((exceed[k] + 1) / (R + 1)).tolist() for k in METRICS}

    overall_rows, seed_rows = [], []
    for group, comps in [('primary', PRIMARY), ('secondary', SECONDARY)]:
        for A, Bt, kind in comps:
            print('Approximate randomization %s vs %s' % (A, Bt), flush=True)
            p = approx_rand(A, Bt)
            for k in METRICS:
                seed_d = [m_all[run(A, s)][k] - m_all[run(Bt, s)][k] for s in SEEDS]
                seed_dc = [m_cl[run(A, s)][k] - m_cl[run(Bt, s)][k] for s in SEEDS]
                mean_d = np.mean(seed_d, axis=0); mean_dc = np.mean(seed_dc, axis=0)
                obs = [point[run(A, s)][k] - point[run(Bt, s)][k] for s in SEEDS]
                lo, hi = ci(mean_d); clo, chi = ci(mean_dc)
                overall_rows.append(dict(group=group, kind=kind, model_a=A, model_b=Bt, metric=k,
                    delta_mean=float(np.mean(obs)), ci95_low=lo, ci95_high=hi,
                    cluster_ci95_low=clo, cluster_ci95_high=chi, p_ar=p[k][-1],
                    seeds_a_better=sum(o > 0 for o in obs), share_boot_a_better=float(np.mean(mean_d > 0))))
                for j, s in enumerate(SEEDS):
                    lo, hi = ci(seed_d[j])
                    seed_rows.append(dict(group=group, kind=kind, model_a=A, model_b=Bt, seed=s, metric=k,
                        delta=obs[j], ci95_low=lo, ci95_high=hi, p_ar=p[k][j]))
    for group in ('primary', 'secondary'):
        for k in METRICS:
            idx = [i for i, r in enumerate(overall_rows) if r['group'] == group and r['metric'] == k]
            for i, v in zip(idx, holm([overall_rows[i]['p_ar'] for i in idx])):
                overall_rows[i]['p_holm'] = v
            idx = [i for i, r in enumerate(seed_rows) if r['group'] == group and r['metric'] == k]
            for i, v in zip(idx, holm([seed_rows[i]['p_ar'] for i in idx])):
                seed_rows[i]['p_holm'] = v

    # ---- probability of being best (seed-mean) among families at each budget
    best_rows = []
    for budget in ('5k', '20k'):
        tags = [t for t in TAGS if t.endswith('_' + budget)]
        for k in METRICS:
            means = np.stack([np.mean([m_all[run(t, s)][k] for s in SEEDS], axis=0) for t in tags])
            winner = np.argmax(means, axis=0)
            for j, t in enumerate(tags):
                best_rows.append(dict(budget=budget, metric=k, tag=t,
                    point_seed_mean=float(np.mean([point[run(t, s)][k] for s in SEEDS])),
                    prob_best=float(np.mean(winner == j))))

    # ---- category level: 5K-20K and condition-COPY (seed-mean deltas, stratified bootstrap)
    cat_rows = []
    for c in labels:
        lo_, hi_ = slices[c]; nc = hi_ - lo_
        mc = {nm: mets(boot_cat[c][nm], nc) for nm in names}
        pc = {nm: full_metrics(nm, lo_, hi_) for nm in names}
        comps = [(A, Bt, 'vocab') for A, Bt, kind in PRIMARY if kind == 'vocab']
        comps += [(t, 'COPY_INPUT', 'vs_copy') for t in TAGS]
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

    # ---- family x vocabulary interaction (m14): (A5K - A20K) - (B5K - B20K), seed-mean, bootstrap only
    inter_rows = []
    for fa, fb in [('spbpe', 'spuni'), ('wp', 'spuni'), ('spbpe', 'wp')]:
        for k in METRICS:
            did = np.mean([(m_all[run(fa + '_5k', s)][k] - m_all[run(fa + '_20k', s)][k])
                           - (m_all[run(fb + '_5k', s)][k] - m_all[run(fb + '_20k', s)][k]) for s in SEEDS], axis=0)
            obs = [(point[run(fa + '_5k', s)][k] - point[run(fa + '_20k', s)][k])
                   - (point[run(fb + '_5k', s)][k] - point[run(fb + '_20k', s)][k]) for s in SEEDS]
            lo, hi = ci(did)
            inter_rows.append(dict(family_a=fa, family_b=fb, metric=k, interaction=float(np.mean(obs)), ci95_low=lo, ci95_high=hi,
                                   p_boot_two_sided=float(min(1.0, 2 * min(np.mean(did <= 0), np.mean(did >= 0)))),
                                   seeds_positive=sum(o > 0 for o in obs)))

    # ---- outputs
    out.mkdir(parents=True)
    write_csv(out / 'paired_interaction.csv', inter_rows)
    write_csv(out / 'paired_overall.csv', overall_rows)
    write_csv(out / 'paired_per_seed.csv', seed_rows)
    write_csv(out / 'prob_best.csv', best_rows)
    write_csv(out / 'paired_categories.csv', cat_rows)
    prov = {'script_sha256': sha256(__file__), 'inputs_sha256': inputs, 'python': sys.version,
            'numpy': np.__version__, 'platform': platform.platform(), 'n': n, 'n_clusters_identical_reference': ncl,
            'bootstrap_replicates': B, 'permutations': a.permutations, 'rng_seed': a.seed,
            'statistics': 'Per-sentence SacreBLEU 1.5.1 sufficient statistics (chrF order 6 beta 2 whitespace removed; BLEU tokenize none, exp smoothing); exact match on stored common-surface strings. Reproduces every stored overall and category score within %g.' % TOL,
            'bootstrap': 'Paired percentile bootstrap stratified by original category; identical resampled rows for all systems and seeds. Cluster variant resamples identical-reference clusters, overall only.',
            'randomization': 'Approximate randomization with per-sentence output swaps; identical masks for the three seed pairs; two-sided (1+exceed)/(R+1).',
            'multiplicity': 'Holm within metric: six primary seed-mean tests; 18 primary per-seed tests; secondary tests corrected separately.',
            'limits': 'Conditional on the trained checkpoints and tokenizer fits; not training-seed uncertainty. Rows with related but non-identical references remain dependent. Category intervals are descriptive and unadjusted.',
            'exclusion': excluded_info,
            'interaction': 'Seed-mean (A5K-A20K)-(B5K-B20K) with stratified-bootstrap percentile CI and two-sided bootstrap p; no AR.',
            'seconds': time.time() - t0}
    (out / 'provenance.json').write_text(json.dumps(prov, indent=2) + '\n', encoding='utf-8')

    f2 = lambda x: '%+.4f' % x
    md = ['# Step16 — paired statistics (M3)' + (' — extended runs, test at epoch %d' % a.extended_epoch if a.extended_epoch else ' — frozen 10-epoch runs')
          + (' — SENSITIVITY: %d test rows excluded (%s)' % (excluded_info['n_excluded'], a.exclude_ids.name) if excluded_info else ''), '',
          'All %d test rows; %d systems (18 runs + COPY_INPUT). Stored scores reproduced exactly before resampling.' % (n, len(names)),
          'Bootstrap B=%d (stratified by category; cluster variant over %d identical-reference clusters). Approximate randomization R=%d.' % (B, ncl, a.permutations), '',
          '## Primary comparisons, seed-mean (A − B)', '',
          '| A | B | Metric | Δ | 95% CI | Cluster 95% CI | p (AR) | p (Holm) | Seeds A>B |',
          '|---|---|---|---:|---|---|---:|---:|---:|']
    for r in overall_rows:
        if r['group'] != 'primary':
            continue
        md.append('| %s | %s | %s | %s | [%s, %s] | [%s, %s] | %.4f | %.4f | %d/3 |' % (
            r['model_a'], r['model_b'], r['metric'], f2(r['delta_mean']), f2(r['ci95_low']), f2(r['ci95_high']),
            f2(r['cluster_ci95_low']), f2(r['cluster_ci95_high']), r['p_ar'], r['p_holm'], r['seeds_a_better']))
    md += ['', '## Family x vocabulary interaction: (A5K − A20K) − (B5K − B20K), seed-mean', '',
           '| A | B | Metric | Interaction | 95% CI | p (boot) | Seeds > 0 |', '|---|---|---|---:|---|---:|---:|']
    for r in inter_rows:
        md.append('| %s | %s | %s | %s | [%s, %s] | %.4f | %d/3 |' % (r['family_a'], r['family_b'], r['metric'], f2(r['interaction']),
                  f2(r['ci95_low']), f2(r['ci95_high']), r['p_boot_two_sided'], r['seeds_positive']))
    md += ['', '## Probability of highest seed-mean score (bootstrap)', '', '| Budget | Metric | Tag | Seed-mean | P(best) |', '|---|---|---|---:|---:|']
    for r in best_rows:
        md.append('| %s | %s | %s | %.4f | %.3f |' % (r['budget'], r['metric'], r['tag'], r['point_seed_mean'], r['prob_best']))
    md += ['', '## Per-seed primary tests (chrF2 and exact match)', '', '| A | B | Seed | Metric | Δ | 95% CI | p (AR) | p (Holm, 18) |', '|---|---|---:|---|---:|---|---:|---:|']
    for r in seed_rows:
        if r['group'] == 'primary' and r['metric'] != 'bleu':
            md.append('| %s | %s | %d | %s | %s | [%s, %s] | %.4f | %.4f |' % (r['model_a'], r['model_b'], r['seed'], r['metric'],
                      f2(r['delta']), f2(r['ci95_low']), f2(r['ci95_high']), r['p_ar'], r['p_holm']))
    md += ['', '## Category chrF2: 5K − 20K and condition − COPY (seed-mean, descriptive, unadjusted)', '',
           '| Category | n | A | B | Δ chrF2 | 95% CI | Excludes 0 |', '|---|---:|---|---|---:|---|---|']
    for r in cat_rows:
        if r['metric'] == 'chrf2_pct':
            md.append('| %s | %d | %s | %s | %s | [%s, %s] | %s |' % (r['category'], r['n'], r['model_a'], r['model_b'],
                      f2(r['delta_mean']), f2(r['ci95_low']), f2(r['ci95_high']), 'yes' if r['ci_excludes_zero'] else 'no'))
    md += ['', 'Interpretation limits: intervals are conditional on the trained checkpoints; they do not measure training-seed variance. '
           'Seed agreement (Seeds A>B) and the per-seed table carry that information separately.', '',
           'Send back: REPORT.md, paired_overall.csv, paired_per_seed.csv, prob_best.csv, paired_categories.csv, provenance.json.', '']
    (out / 'REPORT.md').write_text('\n'.join(md), encoding='utf-8')
    print('DONE in %.1f min -> %s' % ((time.time() - t0) / 60, out / 'REPORT.md'), flush=True)


if __name__ == '__main__':
    main()
