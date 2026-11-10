#!/usr/bin/env python3
"""CPU-only mismatch classification. No scores, row deletion or hypothesis repair."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import unicodedata
from common import canonical, decode, lines, new_output, sha256, write_json


def surface(text, case):
    if case == 'lower':
        text = text.lower()
    # Unlike old \w+, split underscore as punctuation for ALL tokenizers.
    return ' '.join(re.findall(r'[^\W_]+|[^\w\s]|_', text, re.UNICODE))


def strip_accents(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text)
                   if unicodedata.category(c) != 'Mn')


def classify(raw, decoded, case):
    if canonical(raw, case) == canonical(decoded, case):
        return 'exact_old_canonical'
    if surface(raw, case) == surface(decoded, case):
        return 'underscore_punctuation_only'
    if re.search(r'<+unk>+|\[UNK\]|⁇', decoded, re.IGNORECASE):
        # Marker presence is NOT proof that unknowns explain every difference.
        return 'unknown_marker_present_unverified'
    candidates = [
        ('nfkc_equivalent', lambda s: unicodedata.normalize('NFKC', s)),
        ('accent_stripping_equivalent', strip_accents),
        ('nfkc_and_accent_equivalent', lambda s: strip_accents(unicodedata.normalize('NFKC', s))),
    ]
    for label, transform in candidates:
        if surface(transform(raw), case) == surface(transform(decoded), case):
            return label
    return 'unexplained'


def read_records(path, n):
    records = {'S': {}, 'T': {}}
    h_ids = set()
    with open(path, encoding='utf-8') as f:
        for line_number, line in enumerate(f, 1):
            if not re.match(r'^[STH]-', line):
                continue
            parts = line.rstrip('\r\n').split('\t', 2)
            kind = parts[0][0]
            idx = int(parts[0][2:])
            if idx < 0 or idx >= n or len(parts) < (3 if kind == 'H' else 2):
                raise ValueError(f'Invalid record at line {line_number}')
            ids = h_ids if kind == 'H' else records[kind]
            if idx in ids:
                raise ValueError(f'Duplicate {kind}-{idx}; diagnosis stopped for this run')
            if kind == 'H':
                float(parts[1]); h_ids.add(idx)
            else:
                records[kind][idx] = '\t'.join(parts[1:])
    expected = set(range(n))
    coverage = {k: {'present': len(v), 'missing_ids': sorted(expected-set(v))}
                for k, v in dict(records, H=h_ids).items()}
    return records, coverage


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    cfg = json.loads(a.manifest.read_text(encoding='utf-8'))
    root = a.manifest.resolve().parent
    path = lambda name: (root / name).resolve()
    if cfg.get('case') not in ('preserve', 'lower'):
        ap.error('case must be explicit')
    for key, expected in cfg.get('expected_sha256', {}).items():
        if key not in ('source', 'target', 'category') or sha256(path(cfg[key])) != expected:
            ap.error('Input changed since audit: ' + key)
    raw = {'S': lines(path(cfg['source'])), 'T': lines(path(cfg['target']))}
    n = len(raw['S'])
    if not n or len(raw['T']) != n:
        ap.error('Raw source/target length mismatch or empty data')
    out = new_output(a.out)
    result = {'manifest_sha256': sha256(a.manifest), 'script_sha256': sha256(__file__),
              'common_sha256': sha256(Path(__file__).with_name('common.py')),
              'case': cfg['case'], 'n': n, 'runs': [],
              'warning': 'Classification only. No scores and no automatic acceptance of mismatches.'}
    for run in cfg['runs']:
        r = {'run_id': run['id'], 'decoder': run['decoder']}
        result['runs'].append(r)
        print('Diagnosing ' + run['id'], flush=True)
        try:
            generation = path(run['generation'])
            r['generation_sha256'] = sha256(generation)
            records, r['coverage'] = read_records(generation, n)
            r['streams'] = {}
            for kind in ('S', 'T'):
                counts = Counter(); examples = defaultdict(list); mismatch_ids = defaultdict(list)
                for idx, encoded in sorted(records[kind].items()):
                    decoded = decode(encoded, run['decoder'])
                    label = classify(raw[kind][idx], decoded, cfg['case'])
                    counts[label] += 1
                    if label != 'exact_old_canonical':
                        mismatch_ids[label].append(idx)
                        if len(examples[label]) < 5:
                            examples[label].append({'id': idx, 'raw': raw[kind][idx],
                                                    'encoded': encoded, 'decoded': decoded})
                r['streams'][kind] = {'counts': dict(counts), 'examples': dict(examples),
                                       'mismatch_ids': dict(mismatch_ids)}
            r['status'] = 'DIAGNOSIS_COMPLETE_NOT_SCORED'
        except (OSError, ValueError, KeyError) as e:
            r['status'] = 'ERROR'; r['error'] = str(e)
    write_json(out / 'diagnosis.json', result)
    md = ['# Diagnosis mismatch — no GEC scores', '',
          'Missing IDs are reported, not filled or excluded for scoring. Counts concern present S/T records.', '',
          '| Run | Stream | Missing | Underscore | NFKC | Accents | Both | Unknown (unverified) | Unexplained |',
          '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in result['runs']:
        if r['status'] == 'ERROR':
            md.append('\nERROR ' + r['run_id'] + ': ' + r['error'] + '\n'); continue
        for kind, stream in r['streams'].items():
            c = stream['counts']
            labels = ('underscore_punctuation_only', 'nfkc_equivalent', 'accent_stripping_equivalent',
                      'nfkc_and_accent_equivalent', 'unknown_marker_present_unverified', 'unexplained')
            md.append('| ' + ' | '.join([r['run_id'], kind,
                      str(len(r['coverage'][kind]['missing_ids']))] + [str(c.get(k, 0)) for k in labels]) + ' |')
    md += ['', 'Send REPORT.md and diagnosis.json. JSON contains bounded source/target examples.',
           'NFKC/accent equivalence is descriptive, not permission to normalize gold or hypotheses.',
           'Unknown-marker rows require dictionary/tokenizer round-trip verification before scoring.']
    (out / 'REPORT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    return 2 if any(r['status'] == 'ERROR' for r in result['runs']) else 0


if __name__ == '__main__':
    raise SystemExit(main())
