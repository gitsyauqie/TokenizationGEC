#!/usr/bin/env python3
"""Step22 (m13): IDs of test rows that overlap the training split, for a sensitivity analysis.

Definition used in the manuscript (Step05 audit): whitespace-collapsed raw text, case preserved.
- target overlap: the test target string occurs as a training target;
- pair overlap: the (source, target) pair occurs in training.
A stricter variant compares targets after the shared surface normalization (lowercase, punctuation split).
Raw files are verified against the Step01 audit hashes. Read-only; writes only to --out.
"""
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from eval_reconstruction import surface  # noqa: E402


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def lines(path):
    with open(path, encoding='utf-8-sig') as f:
        return [x.rstrip('\r\n') for x in f]


def digest(text):
    return hashlib.sha1(text.encode('utf-8')).digest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--audit', default='server_results/step01_run01/audit.json')
    ap.add_argument('--expect-target', type=int, default=2721)
    ap.add_argument('--expect-pair', type=int, default=57)
    a = ap.parse_args()
    root = a.root.resolve(); out = a.out.resolve()
    if out.exists():
        ap.error('Output exists; choose a fresh directory.')
    audit = json.loads((root / a.audit).read_text())
    files = {}
    for split in ('train', 'test'):
        for k in ('source', 'target', 'category'):
            e = audit['splits'][split]['files'][k]
            if sha256(e['path']) != e['sha256']:
                raise ValueError('Raw file changed since Step01: ' + e['path'])
            files[(split, k)] = e['path']
    ws = lambda x: ' '.join(x.split())
    print('Reading training split', flush=True)
    tr_s, tr_t = lines(files[('train', 'source')]), lines(files[('train', 'target')])
    t_set = set(digest(ws(t)) for t in tr_t)
    p_set = set(digest(json.dumps([ws(s), ws(t)], ensure_ascii=False)) for s, t in zip(tr_s, tr_t))
    n_set = set(digest(surface(t, 'lower')) for t in tr_t)
    del tr_s, tr_t
    te_s, te_t, te_c = (lines(files[('test', k)]) for k in ('source', 'target', 'category'))
    ids = {'target': [], 'pair': [], 'target_surface': []}
    for i, (s, t) in enumerate(zip(te_s, te_t)):
        if digest(ws(t)) in t_set:
            ids['target'].append(i)
        if digest(json.dumps([ws(s), ws(t)], ensure_ascii=False)) in p_set:
            ids['pair'].append(i)
        if digest(surface(t, 'lower')) in n_set:
            ids['target_surface'].append(i)
    out.mkdir(parents=True)
    summary = {'n_test': len(te_t), 'definition': 'whitespace-collapsed raw text, case preserved (Step05); target_surface = shared surface normalization',
               'counts': {k: len(v) for k, v in ids.items()},
               'by_category': {k: dict(Counter(te_c[i].strip() for i in v)) for k, v in ids.items()},
               'pair_subset_of_target': set(ids['pair']) <= set(ids['target']),
               'expected': {'target': a.expect_target, 'pair': a.expect_pair},
               'matches_manuscript': len(ids['target']) == a.expect_target and len(ids['pair']) == a.expect_pair,
               'script_sha256': sha256(__file__), 'audit_sha256': sha256(root / a.audit)}
    for k, v in ids.items():
        (out / ('overlap_%s_ids.txt' % k)).write_text('\n'.join(map(str, v)) + '\n')
    (out / 'summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(summary['counts']), 'matches manuscript:', summary['matches_manuscript'], flush=True)


if __name__ == '__main__':
    main()
