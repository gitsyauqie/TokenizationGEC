#!/usr/bin/env python3
"""CPU-only audit. No checkpoint loading, mutation of data, or training."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import itertools
import json
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys

from common import new_output, sha256, write_json


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).digest()


def norm(text):
    return ' '.join(text.split())


def scan_split(raw, split, src_ext, tgt_ext):
    paths = {'source': raw / f'{split}.{src_ext}',
             'target': raw / f'{split}.{tgt_ext}'}
    category = raw / f'{split}.category'
    groups = raw / f'{split}.group_id'
    if category.exists():
        paths['category'] = category
    if groups.exists():
        paths['group_id'] = groups
    report = {'files': {}, 'errors': [], 'n_pairs': 0, 'n_unchanged': 0,
              'blank_source': 0, 'blank_target': 0, 'categories': {},
              'group_provenance_available': groups.exists(),
              'normalization': 'strip/collapse whitespace, preserve case/Unicode'}
    hashes = {k: set() for k in ('source', 'target', 'pair', 'group_id')}
    for key, p in paths.items():
        if not p.is_file():
            report['errors'].append(f'Missing: {p}')
        else:
            report['files'][key] = {'path': str(p), 'sha256': sha256(p),
                                    'bytes': p.stat().st_size}
    if report['errors']:
        return report, hashes
    handles = {k: p.open(encoding='utf-8-sig') for k, p in paths.items()}
    counts = Counter(); cats = Counter(); lengths = Counter(); maximum = 0
    try:
        for row in itertools.zip_longest(*handles.values()):
            values = dict(zip(handles, row))
            for k, value in values.items():
                counts[k] += value is not None
            if any(v is None for v in row):
                continue
            s, t = norm(values['source']), norm(values['target'])
            report['n_pairs'] += 1
            report['n_unchanged'] += s == t
            report['blank_source'] += not s
            report['blank_target'] += not t
            for k, val in [('source', s), ('target', t),
                           ('pair', json.dumps([s, t], ensure_ascii=False))]:
                hashes[k].add(digest(val))
            if 'group_id' in values:
                g = values['group_id'].strip()
                if not g:
                    report['errors'].append(f'Empty group ID at row {report["n_pairs"]}')
                else:
                    hashes['group_id'].add(digest(g))
            if 'category' in values:
                cats[values['category'].strip()] += 1
            length = max(len(s.split()), len(t.split()))
            maximum = max(maximum, length)
            lengths['gt_256_words'] += length > 256
            lengths['gt_512_words'] += length > 512
            lengths['gt_1024_words'] += length > 1024
    finally:
        for f in handles.values():
            f.close()
    report['line_counts'] = dict(counts)
    if len(set(counts.values())) != 1 or not counts or not report['n_pairs']:
        report['errors'].append('Empty data or mismatched line counts; do not score/train')
    if report['blank_source'] or report['blank_target']:
        report['errors'].append('Blank source/target rows require explicit review')
    if '' in cats:
        report['errors'].append('Blank category labels')
    report['categories'] = dict(cats)
    report['lengths'] = dict(lengths, max_words=maximum)
    report['unique'] = {k: len(v) for k, v in hashes.items()}
    report['duplicate_pair_rows'] = report['n_pairs'] - len(hashes['pair'])
    return report, hashes


def inventory(project):
    result = []
    # Only nominated experiment directory; no arbitrary home/account scans.
    for p in sorted(project.rglob('*')):
        if not p.is_file() or any(x in p.parts for x in ('.git', '__pycache__')):
            continue
        if p.suffix not in ('.out', '.log', '.pt', '.model', '.codes', '.json', '.csv') \
                and not p.name.startswith(('dict.', 'log_')):
            continue
        entry = {'path': str(p), 'bytes': p.stat().st_size}
        if p.name.startswith('dict.'):
            entry['sha256'] = sha256(p)
            with p.open(encoding='utf-8') as f:
                entry['dictionary_lines'] = sum(1 for _ in f)
            entry['note'] = 'Stored lines; Fairseq may add special symbols internally'
        elif p.suffix in ('.model', '.codes', '.json', '.csv') and p.stat().st_size < 20_000_000:
            entry['sha256'] = sha256(p)
        if p.suffix in ('.out', '.log') or p.name.startswith('log_'):
            # Scan complete generation files: header can appear after many log lines.
            nrec = Counter(); markers = Counter(); headers = []
            with p.open(encoding='utf-8', errors='replace') as f:
                for line in f:
                    if re.match(r'^[STH]-\d+\t', line):
                        kind = line[0]; nrec[kind] += 1
                        if kind in ('S', 'T', 'H'):
                            for key, marker in [('bpe', '@@'), ('wp', '##'), ('sp', '▁')]:
                                markers[key] += marker in line
                    if len(headers) < 8 and any(x in line for x in
                        ('Namespace(', "'common':", 'num. model params', 'num_updates', 'best_checkpoint_metric')):
                        headers.append(line.strip()[:16000])
            entry.update(records=dict(nrec), marker_lines=dict(markers), config_evidence=headers)
        result.append(entry)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project', required=True, type=Path)
    ap.add_argument('--raw', required=True, type=Path)
    ap.add_argument('--src-ext', default='source')
    ap.add_argument('--tgt-ext', default='target')
    ap.add_argument('--valid-name', default='valid')
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args()
    if not args.project.is_dir() or not args.raw.is_dir():
        ap.error('Project/raw directory does not exist; correct paths before running')
    # Inventory before creating output so audit does not inventory itself.
    items = inventory(args.project.resolve())
    out = new_output(args.out)
    environment = {'python': sys.version, 'executable': sys.executable,
                   'platform': platform.platform(), 'packages': {},
                   'commands': {k: shutil.which(k) for k in
                                ('fairseq-train', 'fairseq-generate', 'fairseq-preprocess')}}
    for package in ('torch', 'fairseq', 'tokenizers', 'sentencepiece', 'subword-nmt',
                    'sacrebleu', 'numpy', 'scipy', 'Sastrawi', 'nltk'):
        try:
            environment['packages'][package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            environment['packages'][package] = None
    if shutil.which('nvidia-smi'):
        try:
            gpu = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,driver_version',
                                  '--format=csv,noheader'], capture_output=True, text=True, timeout=15)
            environment['gpu'] = gpu.stdout.strip() or gpu.stderr.strip()
        except subprocess.TimeoutExpired:
            environment['gpu'] = 'nvidia-smi timed out'
    report = {'created_utc': datetime.now(timezone.utc).isoformat(),
              'script_sha256': sha256(__file__), 'splits': {}, 'overlap': {},
              'warnings': ['No near-duplicate/document leakage proof without group provenance.',
                           'Exact target overlap flags shared clean sentences; investigate before retraining.']}
    sets = {}
    for split in ('train', args.valid_name, 'test'):
        print(f'Auditing split {split} ...', flush=True)
        report['splits'][split], sets[split] = scan_split(args.raw, split, args.src_ext, args.tgt_ext)
    for a, b in itertools.combinations(sets, 2):
        report['overlap'][f'{a}__{b}'] = {k: len(sets[a][k] & sets[b][k]) for k in sets[a]}
    write_json(out / 'audit.json', report)
    write_json(out / 'environment.json', environment)
    write_json(out / 'inventory.json', items)
    legacy_evidence = []
    base = args.project.resolve().parent
    candidates = [base / name for name in ('evaluate_model_new.py',
                  'logfile_indogec_IGED_basicBPE.txt', 'combine_dataset_for_fairseq.py')]
    candidates += list(base.glob('data-bin*/dict.*.txt'))
    evidence_dir = out / 'legacy_evidence'
    evidence_dir.mkdir()
    for p in candidates:
        if p.is_file():
            entry = {'path': str(p), 'sha256': sha256(p), 'bytes': p.stat().st_size}
            if p.name.startswith('dict.'):
                with p.open(encoding='utf-8') as f:
                    entry['dictionary_lines'] = sum(1 for _ in f)
            elif p.suffix == '.py':
                shutil.copy2(p, evidence_dir / p.name)
            else:
                with p.open(encoding='utf-8', errors='replace') as f:
                    entry['config_evidence'] = [s.strip()[:16000] for s in itertools.islice(f, 100)
                        if 'Namespace(' in s or 'num. model params' in s]
            legacy_evidence.append(entry)
    write_json(out / 'legacy_evidence.json', legacy_evidence)
    blocked = any(r['errors'] for r in report['splits'].values())
    md = ['# Server audit — Paper 6', '',
          '**Status: ' + ('BLOCKED: data integrity errors' if blocked else 'REVIEW REQUIRED; not training approval') + '**', '',
          '| Split | Source | Target | Aligned pairs | Duplicate pair rows |',
          '|---|---:|---:|---:|---:|']
    for split, r in report['splits'].items():
        c = r.get('line_counts', {})
        md.append(f'| {split} | {c.get("source", "missing")} | {c.get("target", "missing")} | '
                  f'{r["n_pairs"]} | {r.get("duplicate_pair_rows", "unknown")} |')
        md.extend(f'\n- ERROR {split}: {e}' for e in r['errors'])
    md += ['', '## Cross-split overlap (unique whitespace-normalized values)', '',
           '```json', json.dumps(report['overlap'], indent=2), '```', '',
           'Next: send this file plus audit.json, environment.json and inventory.json.',
           'Do not launch training yet. Full sentence contents are not exported by this audit.',
           'Paths/config excerpts are included; inspect them before sharing outside the research team.']
    (out / 'REPORT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(f'Report saved to {out}/REPORT.md')
    return 2 if blocked else 0


if __name__ == '__main__':
    raise SystemExit(main())
