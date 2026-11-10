#!/usr/bin/env python3
"""Sample VALIDATION pairs for correction-quality review; inspect metadata headers.
No predictions, training, scoring, gold edits or test-based selection are produced.
"""
import argparse
from collections import Counter
import csv
import itertools
import json
from pathlib import Path
import random
from common import new_output, sha256, write_json


def sample_pairs(paths, per_category, seed):
    rng = random.Random(seed); counts = Counter(); samples = {}
    handles = [open(p, encoding='utf-8-sig') for p in paths]
    try:
        for idx, row in enumerate(itertools.zip_longest(*handles)):
            if any(v is None for v in row):
                raise ValueError('Validation files have different lengths')
            src, tgt, category = [s.rstrip('\r\n') for s in row]
            if not src.strip() or not tgt.strip() or not category.strip():
                raise ValueError('Empty validation field at ID ' + str(idx))
            counts[category] += 1
            bucket = samples.setdefault(category, [])
            value = (idx, src, tgt, category)
            if len(bucket) < per_category:
                bucket.append(value)
            else:
                j = rng.randrange(counts[category])
                if j < per_category:
                    bucket[j] = value
    finally:
        for f in handles: f.close()
    return sorted((r for b in samples.values() for r in b)), dict(counts)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--audit', type=Path, required=True)
    ap.add_argument('--base', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    audit = json.loads(args.audit.read_text())
    files = audit['splits']['valid']['files']
    paths = [files[k]['path'] for k in ('source', 'target', 'category')]
    for key, path in zip(('source', 'target', 'category'), paths):
        if sha256(path) != files[key]['sha256']:
            raise ValueError('Validation data changed: ' + path)
    rows, counts = sample_pairs(paths, 10, 20261008)
    out = new_output(args.out)
    with (out/'validation_review.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['id_zero_based','source','target','original_category',
                    'source_has_error','target_is_valid','meaning_preserved','review_notes'])
        for row in rows: w.writerow(list(row)+['','','',''])
    candidates = []
    for folder in ('error_categories', 'fairseq_data', 'data'):
        root = args.base/folder
        if root.is_dir():
            candidates.extend(root.rglob('*.csv'))
    metadata = []
    for path in sorted(set(candidates))[:100]:
        entry = {'path': str(path), 'bytes': path.stat().st_size}
        try:
            with path.open(encoding='utf-8-sig') as f:
                entry['header'] = next(csv.reader(f), [])
        except (OSError, UnicodeError, csv.Error) as exc:
            entry['error'] = str(exc)
        metadata.append(entry)
    write_json(out/'metadata_headers.json', {'files': metadata,
        'candidates_found': len(set(candidates)), 'inspected_limit': 100,
        'note': 'CSV headers only, selected directories only; absence does not prove no edit metadata exists.'})
    write_json(out/'provenance.json', {'audit_sha256':sha256(args.audit),
        'script_sha256':sha256(__file__), 'split':'valid','seed':20261008,
        'per_category':10,'population_counts':counts,'n_sample':len(rows),
        'raw_sha256':{k:files[k]['sha256'] for k in ('source','target','category')},
        'selection':'Reservoir sampling within each original category; not prevalence-weighted.'})
    (out/'REPORT.md').write_text(
        '# Validation-pair review preparation\n\n'
        f'{len(rows)} validation pairs sampled, maximum 10 per original category.\n\n'
        'Review fields are blank: these pairs are NOT automatically validated gold.\n'
        'Send validation_review.csv, metadata_headers.json and provenance.json.\n'
        'CSV contains raw corpus text. No model outputs or test examples are included.\n'
        'This small stratified sample cannot certify the whole dataset or estimate overall quality unweighted.\n',
        encoding='utf-8')
    print(out/'REPORT.md')


if __name__=='__main__': main()
