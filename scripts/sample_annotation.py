#!/usr/bin/env python3
"""Step20 (M5): draw a fixed random sample for manual error analysis.

For each selected category, N test rows are sampled uniformly (seeded) from the frozen 10-epoch
predictions of two runs (default: SP-BPE 5K and 20K, seed 42). Each row carries the source, the
reference, both outputs in a BLIND order (A/B; the key is written to a separate file), and the
gold and system edits from the M4 alignment. No model is run and no file outside --out is written.
"""
import argparse
import csv
import hashlib
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from gec_metrics import extract_edits  # noqa: E402


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def read_lines(path):
    with open(path, encoding='utf-8') as f:
        rows = [x.rstrip('\n') for x in f]
    return rows[:-1] if rows and rows[-1] == '' else rows


def fmt_edits(src_tokens, edits):
    out = []
    for s, e, rep in sorted(edits, key=lambda x: (x[0], x[1], x[2])):
        old = ' '.join(src_tokens[s:e]) or '∅'
        new = ' '.join(rep) or '∅'
        out.append('%s → %s' % (old, new))
    return ' | '.join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--runs', nargs=2, default=['spbpe_5k_seed42', 'spbpe_20k_seed42'])
    ap.add_argument('--categories', nargs='+', default=['diksi', 'kelengkapan_kalimat', 'pleonasme_claude', 'ambigu_claude'])
    ap.add_argument('--n', type=int, default=50)
    ap.add_argument('--seed', type=int, default=20261030)
    ap.add_argument('--expected-n', type=int, default=134025)
    a = ap.parse_args()
    root = a.root.resolve(); test = root / 'controlled_test_v1'; out = a.out.resolve()
    if out.exists():
        ap.error('Output exists; choose a fresh directory.')
    src = read_lines(test / 'test.source'); ref = read_lines(test / 'test.target'); cats = read_lines(test / 'test.category')
    if not (len(src) == len(ref) == len(cats) == a.expected_n):
        raise ValueError('Test coverage invalid')
    stored = {'%s_seed%d' % (r['tag'], r['seed']): r for r in json.loads((test / 'all_scores.json').read_text())}
    hyps = {}
    for run in a.runs:
        pred = test / run / 'predictions.jsonl'
        if sha256(pred) != stored[run]['predictions_sha256']:
            raise ValueError('Prediction hash mismatch: ' + run)
        rows = [json.loads(x) for x in pred.open(encoding='utf-8')]
        if [r['id'] for r in rows] != list(range(len(src))):
            raise ValueError('ID order mismatch: ' + run)
        hyps[run] = [r['hypothesis'] for r in rows]
    rng = random.Random(a.seed)
    items, key = [], []
    for c in a.categories:
        ids = [i for i, x in enumerate(cats) if x == c]
        if len(ids) < a.n:
            raise ValueError('Category %s has only %d rows' % (c, len(ids)))
        for i in sorted(rng.sample(ids, a.n)):
            order = list(a.runs); rng.shuffle(order)
            s, r = src[i].split(), ref[i].split()
            gold = extract_edits(s, r)[0]
            row = {'test_id': i, 'category': c, 'source': src[i], 'reference': ref[i],
                   'gold_edits': fmt_edits(s, gold) or '(none)'}
            for slot, run in zip('AB', order):
                h = hyps[run][i]; he = extract_edits(s, h.split())[0]
                row['output_%s' % slot] = h
                row['edits_%s' % slot] = fmt_edits(s, he) or '(unchanged)'
                row['%s_equals_reference' % slot] = int(h == ref[i])
                row['%s_equals_source' % slot] = int(h == src[i])
                row['%s_matched_gold_edits' % slot] = '%d/%d' % (len(he & gold), len(gold))
            items.append(row); key.append({'test_id': i, 'A': order[0], 'B': order[1]})
    rng.shuffle(items)
    for k, row in enumerate(items, 1):
        row['item'] = k
    out.mkdir(parents=True)
    cols = ['item', 'test_id', 'category', 'source', 'reference', 'gold_edits',
            'output_A', 'edits_A', 'A_matched_gold_edits', 'A_equals_reference', 'A_equals_source',
            'output_B', 'edits_B', 'B_matched_gold_edits', 'B_equals_reference', 'B_equals_source']
    with open(out / 'annotation_sample.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(items)
    with open(out / 'blind_key.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['test_id', 'A', 'B']); w.writeheader(); w.writerows(sorted(key, key=lambda x: x['test_id']))
    (out / 'provenance.json').write_text(json.dumps({
        'script_sha256': sha256(__file__), 'runs': a.runs, 'categories': a.categories, 'n_per_category': a.n,
        'seed': a.seed, 'test_target_sha256': sha256(test / 'test.target'),
        'note': 'Uniform random sample per category (seeded); A/B order randomized per item; key in blind_key.csv.'}, indent=2) + '\n')
    print('Wrote %d items -> %s' % (len(items), out / 'annotation_sample.csv'))


if __name__ == '__main__':
    main()
