#!/usr/bin/env python3
"""Replaces legacy eval_gen.py for AUDIT diagnostics, not publication GEC scores.

Requires raw S/T files and explicit decoder per run. Missing/duplicate IDs or
source/reference mismatches BLOCK scoring; there is no permissive override.
"""
import argparse
from collections import defaultdict
import csv
import json
from pathlib import Path
import sys

from common import (canonical, decode, diagnostic_metrics, lines, new_output,
                    parse_gen, sha256, write_json)


def validate_streams(streams, source, target, mode, case):
    diagnostics = {}
    for kind, raw in [('S', source), ('T', target)]:
        bad = [i for i, s in enumerate(raw)
               if canonical(decode(streams[kind][i], mode), case) != canonical(s, case)]
        diagnostics[kind] = {'mismatches': len(bad), 'first_ids': bad[:20],
            'examples': [{'id': i, 'raw': raw[i], 'encoded': streams[kind][i],
                          'decoded': decode(streams[kind][i], mode)} for i in bad[:3]]}
    return diagnostics


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    cfg = json.loads(args.manifest.read_text(encoding='utf-8'))
    if cfg.get('case') not in ('preserve', 'lower'):
        ap.error('manifest.case must explicitly be preserve or lower (applies to all runs)')
    root = args.manifest.resolve().parent
    resolve = lambda v: (root / v).resolve()
    for key, expected in cfg.get('expected_sha256', {}).items():
        if key not in ('source', 'target', 'category') or sha256(resolve(cfg[key])) != expected:
            ap.error('Input hash differs from Step 1 or invalid hash key: ' + key)
    raw_s, raw_t = lines(resolve(cfg['source'])), lines(resolve(cfg['target']))
    if not raw_s or len(raw_s) != len(raw_t):
        ap.error('raw source/target must be nonempty and aligned')
    if any(not s.strip() for s in raw_s + raw_t):
        ap.error('blank raw rows require data audit first')
    cats = lines(resolve(cfg['category'])) if cfg.get('category') else ['ALL'] * len(raw_s)
    if len(cats) != len(raw_s) or any(not c.strip() for c in cats):
        ap.error('category length mismatch or empty labels')
    runs = cfg.get('runs', [])
    tags = [r['id'] for r in runs]
    if not runs or len(set(tags)) != len(tags):
        ap.error('runs must be nonempty and have unique IDs')
    if set(tags) & {'COPY_INPUT', 'REFERENCE_ORACLE_SANITY'}:
        ap.error('run IDs cannot use reserved baseline names')
    import re
    if any(not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', tag) for tag in tags):
        ap.error('run IDs must be safe directory names')
    out = new_output(args.out)
    write_json(out / 'manifest_used.json', cfg)
    provenance = {'manifest_sha256': sha256(args.manifest),
                  'script_sha256': sha256(__file__),
                  'common_sha256': sha256(Path(__file__).with_name('common.py')),
                  'source_sha256': sha256(resolve(cfg['source'])),
                  'target_sha256': sha256(resolve(cfg['target'])),
                  'category_sha256': sha256(resolve(cfg['category'])) if cfg.get('category') else None,
                  'case': cfg['case'], 'surface_tokenization': r'Unicode \w+|[^\w\s]',
                  'warning': 'Diagnostics only. Legacy word-set F1 is NOT edit-based GEC F1.'}
    source = [canonical(s, cfg['case']) for s in raw_s]
    target = [canonical(s, cfg['case']) for s in raw_t]
    rows = []; subrows = []; statuses = []
    def add(tag, hypotheses):
        row = dict(run_id=tag, **diagnostic_metrics(source, target, hypotheses))
        rows.append(row)
        bucket = defaultdict(list)
        for i, cat in enumerate(cats):
            bucket[cat].append(i)
        for cat, ids in sorted(bucket.items()):
            subrows.append(dict(run_id=tag, category=cat,
                **diagnostic_metrics([source[i] for i in ids], [target[i] for i in ids],
                                     [hypotheses[i] for i in ids])))
    add('COPY_INPUT', source)
    add('REFERENCE_ORACLE_SANITY', target)
    for run in runs:
        tag = run['id']; status = {'run_id': tag, 'status': 'BLOCKED'}
        statuses.append(status)
        try:
            path = resolve(run['generation'])
            status['generation_sha256'] = sha256(path)
            status['run_metadata'] = {k: v for k, v in run.items()
                                      if k not in ('id', 'generation')}
            streams = parse_gen(path, len(raw_s))
            diag = validate_streams(streams, raw_s, raw_t, run['decoder'], cfg['case'])
            status['alignment'] = diag
            if any(x['mismatches'] for x in diag.values()):
                raise ValueError('Decoded S/T does not match canonical raw data; inspect decoding, '
                                 'normalization, dataset order or unknown tokens. No score produced.')
            decoded = [decode(streams['H'][i], run['decoder']) for i in range(len(raw_s))]
            hyp = [canonical(h, cfg['case']) for h in decoded]
            unknown = sum(any(x in h for x in ('<unk>', '[UNK]', '⁇')) for h in decoded)
            status['hypotheses_with_unknowns'] = unknown
            status['empty_hypotheses'] = sum(not h for h in hyp)
            status['status'] = 'DIAGNOSTIC_ONLY'
            add(tag, hyp)
            dest = out / tag; dest.mkdir()
            (dest / 'hyp.decoded.txt').write_text('\n'.join(decoded) + '\n', encoding='utf-8')
            (dest / 'hyp.canonical.txt').write_text('\n'.join(hyp) + '\n', encoding='utf-8')
        except (ValueError, KeyError, OSError) as exc:
            status['error'] = str(exc)
        print(f'{tag}: {status["status"]}', flush=True)
    for name, data in [('diagnostics.csv', rows), ('subcategory_diagnostics.csv', subrows)]:
        with (out / name).open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(data[0])); w.writeheader(); w.writerows(data)
    write_json(out / 'provenance.json', provenance)
    write_json(out / 'run_status.json', statuses)
    blocked = [r for r in statuses if r['status'] == 'BLOCKED']
    md = ['# Re-evaluation diagnostics', '',
          '**Not publication-ready GEC scores. No M2 F0.5 is computed here.**', '',
          f'Common case policy: `{cfg["case"]}`. Reference: canonical raw target, never per-tokenizer T lines.', '',
          '| Run | n | Word-set F1 (legacy diagnostic) | Exact match % |', '|---|---:|---:|---:|']
    md += [f'| {r["run_id"]} | {r["n"]} | {r["legacy_word_set_f1_pct"]:.4f} | '
           f'{r["exact_match_pct"]:.4f} |' for r in rows]
    md += ['', '## Blocked runs', '']
    md += [f'- {r["run_id"]}: {r.get("error", "unknown")}' for r in blocked] or ['None.']
    md += ['', 'Send REPORT.md, both CSVs, provenance.json and run_status.json.',
           'Hypothesis text stays in per-run folders; it need not be shared at this stage.']
    (out / 'REPORT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    return 2 if blocked else 0


if __name__ == '__main__':
    raise SystemExit(main())
