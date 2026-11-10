#!/usr/bin/env python3
"""Read-only row-level overlap audit anchored to the hashes from Step 1."""
import argparse
from collections import Counter
import csv
import hashlib
import itertools
import json
from pathlib import Path
from common import new_output, sha256, write_json


def keys(source, target):
    s, t = ' '.join(source.split()), ' '.join(target.split())
    h = lambda value: hashlib.sha256(value.encode('utf-8')).digest()
    return (h(s), h(t), h(json.dumps([s, t], ensure_ascii=False)))


def records(split):
    paths = [split['files'][k]['path'] for k in ('source', 'target', 'category')]
    handles = [open(p, encoding='utf-8-sig') for p in paths]
    try:
        for i, row in enumerate(itertools.zip_longest(*handles)):
            if any(v is None for v in row):
                raise ValueError('Mismatched line counts at ID ' + str(i))
            yield i, row[0], row[1], row[2].strip()
    finally:
        for f in handles:
            f.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--audit', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    audit = json.loads(a.audit.read_text())
    for name in ('train', 'valid', 'test'):
        split = audit['splits'][name]
        if split['errors']:
            raise ValueError('Step 1 contains data errors: ' + name)
        for key in ('source', 'target', 'category'):
            file = split['files'][key]
            if sha256(file['path']) != file['sha256']:
                raise ValueError('Data changed since Step 1: ' + file['path'])
    out = new_output(a.out)
    prior = {}
    result = {'normalization': 'collapse whitespace; preserve case and Unicode',
              'audit_sha256': sha256(a.audit), 'script_sha256': sha256(__file__),
              'warning': 'No document provenance; exact-overlap-free is not leakage-free.',
              'splits': {}}
    for name in ('train', 'valid', 'test'):
        print('Scanning ' + name, flush=True)
        seen = [set(), set(), set()]
        flags = Counter(); category_flags = Counter(); categories = Counter(); unchanged = Counter()
        with (out / (name + '_affected_ids.csv')).open('w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id_zero_based', 'category', 'flags'])
            n = 0
            for idx, src, tgt, cat in records(audit['splits'][name]):
                n += 1; categories[cat] += 1
                unchanged[cat] += ' '.join(src.split()) == ' '.join(tgt.split())
                rowkeys = keys(src, tgt)
                hit = []
                for prev, sets in prior.items():
                    for k, key in enumerate(('source', 'target', 'pair')):
                        if rowkeys[k] in sets[k]:
                            hit.append(key + '_in_' + prev)
                if rowkeys[2] in seen[2]:
                    hit.append('duplicate_pair_after_first_in_split')
                if hit:
                    flags['any_flag'] += 1
                    writer.writerow([idx, cat, ';'.join(hit)])
                for flag in hit:
                    flags[flag] += 1; category_flags[(cat, flag)] += 1
                for k, value in enumerate(rowkeys):
                    seen[k].add(value)
            if n != audit['splits'][name]['n_pairs']:
                raise ValueError('Unexpected row count: ' + name)
        result['splits'][name] = {'n': n, 'affected_rows': dict(flags),
            'affected_row_percent': {k: 100*v/n for k, v in flags.items()},
            'categories': dict(categories), 'unchanged_by_category': dict(unchanged),
            'by_category_and_flag': [{'category': c, 'flag': k, 'n': v}
                                     for (c, k), v in sorted(category_flags.items())]}
        prior[name] = seen
    write_json(out / 'overlap_details.json', result)
    md = ['# Step 1b: row-level overlap', '',
          'Counts below are affected ROWS, not unique sentences. Flags overlap and must not be summed.', '',
          '| Split | Flag | Rows | % of split |', '|---|---|---:|---:|']
    for name, r in result['splits'].items():
        for flag, count in r['affected_rows'].items():
            md.append(f'| {name} | {flag} | {count} | {100*count/r["n"]:.4f} |')
    md += ['', 'Affected IDs use zero-based raw-file order and are for investigation only.',
           'Do not delete rows or resplit automatically. These IDs do not define a new clean benchmark.',
           'No source/target text is exported. Send REPORT.md, JSON and affected_ids CSV files.']
    (out / 'REPORT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
