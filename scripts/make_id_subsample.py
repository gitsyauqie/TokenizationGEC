#!/usr/bin/env python3
"""M7b data-size control: an IGED training set of the same size as GECTurk.

Draws a category-stratified random sample of 96,919 training pairs (GECTurk's training size) and
20,769 validation pairs (GECTurk's dev size) from the retained Indonesian surface files of the main
experiment, and writes them in the raw layout read by tr_pipeline.py (raw/train|dev|test.src|tgt|cat).
The test set is the full 134,025-pair IGED test set used in the main results, so test predictions can
be compared row by row with the main runs. Allocation per category is proportional (largest remainder);
rows keep their original order. Nothing is re-normalised: the inputs are already in the shared,
lowercased surface form, and tr_pipeline.py --case lower leaves them unchanged.
"""
import argparse
import csv
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path

N_TRAIN, N_DEV, N_TEST, SEED = 96919, 20769, 134025, 20261101


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def lines(p):
    rows = Path(p).read_text(encoding='utf-8').split('\n')
    if rows[-1] != '':
        raise ValueError('Missing final newline: %s' % p)
    return rows[:-1]


def stratified(cats, k, rng):
    by = defaultdict(list)
    for i, c in enumerate(cats):
        by[c].append(i)
    n = len(cats); quota = {c: k * len(v) / n for c, v in by.items()}
    take = {c: int(q) for c, q in quota.items()}
    for c in sorted(by, key=lambda c: (-(quota[c] - take[c]), c))[:k - sum(take.values())]:
        take[c] += 1
    chosen = []
    for c in sorted(by):
        chosen += rng.sample(by[c], take[c])
    return sorted(chosen), take


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', type=Path, required=True, help='paper6_revision_20261007')
    ap.add_argument('--out', type=Path, required=True, help='new data folder, e.g. ../data/iged_sub97k')
    a = ap.parse_args()
    root = a.root.resolve(); out = a.out.resolve()
    if out.exists():
        ap.error('Output exists; choose a new folder')
    prep = root / 'controlled_pilot_v2'
    dm = json.loads((prep / 'data_manifest.json').read_text())
    for rel, d in dm['surface_files'].items():
        if sha256(prep / rel) != d:
            raise ValueError('Indonesian surface file changed: ' + rel)
    rng = random.Random(SEED); (out / 'raw').mkdir(parents=True)
    report = {'seed': SEED, 'source': str(prep), 'splits': {}}
    for split, stem, k in (('train', 'train', N_TRAIN), ('valid', 'dev', N_DEV)):
        src, tgt, cat = (lines(prep / 'surface' / ('%s.%s' % (split, s))) for s in ('source', 'target', 'category'))
        if not (len(src) == len(tgt) == len(cat) == dm['splits'][split]['retained_n']):
            raise ValueError('Row counts differ from the manifest: ' + split)
        ids, take = stratified(cat, k, rng)
        for ext, rows in (('src', src), ('tgt', tgt), ('cat', cat)):
            (out / 'raw' / ('%s.%s' % (stem, ext))).write_text(''.join(rows[i] + '\n' for i in ids), encoding='utf-8')
        with open(out / ('%s_ids.csv' % stem), 'w', newline='') as f:
            w = csv.writer(f); w.writerow(['subsample_id', 'retained_id_zero_based']); w.writerows(enumerate(ids))
        report['splits'][split] = {'from': len(src), 'kept': len(ids), 'per_category': take}
    test = root / 'controlled_test_v1'
    src, tgt, cat = (lines(test / ('test.%s' % s)) for s in ('source', 'target', 'category'))
    if not len(src) == len(tgt) == len(cat) == N_TEST:
        raise ValueError('Unexpected IGED test size')
    for ext, rows in (('src', src), ('tgt', tgt), ('cat', cat)):
        (out / 'raw' / ('test.%s' % ext)).write_text(''.join(r + '\n' for r in rows), encoding='utf-8')
    report['splits']['test'] = {'from': len(src), 'kept': len(src)}
    report['inputs_sha256'] = {**{rel: d for rel, d in dm['surface_files'].items()},
                               **{'controlled_test_v1/test.%s' % s: sha256(test / ('test.%s' % s)) for s in ('source', 'target', 'category')}}
    report['outputs_sha256'] = {p.name: sha256(p) for p in sorted((out / 'raw').iterdir())}
    (out / 'subsample_manifest.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    for s, v in report['splits'].items():
        print('%s: %d of %d' % (s, v['kept'], v['from']))
    print('SUBSAMPLE DONE -> ' + str(out))


if __name__ == '__main__':
    main()
