#!/usr/bin/env python3
"""Verify mismatched S/T through saved tokenizer + Fairseq dictionary, then
score complete modern runs against raw gold. CPU only. NOT edit-based GEC.
Legacy runs lacking known tokenizer provenance and incomplete runs stay blocked.
"""
import argparse
from collections import defaultdict
import csv
import importlib.metadata
import json
from pathlib import Path
import re
from common import (canonical, decode, diagnostic_metrics, lines, new_output,
                    parse_gen, sha256, write_json)


def surface(text, case):
    if case == 'lower':
        text = text.lower()
    return ' '.join(re.findall(r'[^\W_]+|[^\w\s]|_', text, re.UNICODE))


def render(dictionary, pieces, target=False, sentencepiece=False):
    ids = dictionary.encode_line(' '.join(pieces), add_if_not_exist=False)
    return dictionary.string(ids, bpe_symbol='sentencepiece' if sentencepiece else None,
                             escape_unk=target)


def make_tokenizer(path, family):
    if family == 'bpe':
        from subword_nmt.apply_bpe import BPE
        with path.open(encoding='utf-8') as f:
            tok = BPE(f)
        return lambda s: tok.process_line(s.strip()).split()
    if family == 'wp':
        from tokenizers import Tokenizer
        tok = Tokenizer.from_file(str(path))
        return lambda s: tok.encode(s.strip(), add_special_tokens=False).tokens
    import sentencepiece as spm
    tok = spm.SentencePieceProcessor(model_file=str(path))
    return lambda s: tok.encode(s.strip(), out_type=str)


def verify_stream(raw, encoded, decoder, case, tokenize, dictionary, target):
    mismatch = [i for i in range(len(raw))
                if canonical(raw[i], case) != canonical(decode(encoded[i], decoder), case)]
    # Independently rerun ALL mismatches + fixed controls; unknowns are not wildcards.
    ids = sorted(set(mismatch) | set(range(min(20, len(raw)))))
    failures = []; absent_pieces = defaultdict(int)
    for i in ids:
        pieces = tokenize(raw[i])
        for piece in pieces:
            if dictionary.index(piece) == dictionary.unk():
                absent_pieces[piece] += 1
        reconstructed = render(dictionary, pieces, target, decoder == 'text')
        if ' '.join(reconstructed.split()) != ' '.join(encoded[i].split()):
            failures.append({'id': i, 'raw': raw[i], 'observed': encoded[i],
                             'reconstructed': reconstructed})
    return {'mismatch_rows_checked': len(mismatch), 'total_rows_reencoded': len(ids),
            'failures': len(failures), 'failure_examples': failures[:5],
            'unknown_pieces_in_checked_rows': dict(absent_pieces)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest', type=Path, required=True)
    ap.add_argument('--diagnosis', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    root = args.manifest.resolve().parent
    cfg = json.loads(args.manifest.read_text())
    diagnosis = json.loads(args.diagnosis.read_text())
    if diagnosis['manifest_sha256'] != sha256(args.manifest):
        ap.error('Manifest differs from the one used for diagnosis')
    if cfg.get('case') not in ('lower', 'preserve'):
        ap.error('Explicit case policy required')
    resolve = lambda p: (root / p).resolve()
    for k in ('source', 'target', 'category'):
        if sha256(resolve(cfg[k])) != cfg['expected_sha256'][k]:
            ap.error('Raw input changed: ' + k)
    inventory_path = root / 'server_results/step01_run01/inventory.json'
    inventory = {r['path']: r.get('sha256') for r in json.loads(inventory_path.read_text())}
    previous = {r['run_id']: r for r in diagnosis['runs']}
    src, tgt, cats = [lines(resolve(cfg[k])) for k in ('source', 'target', 'category')]
    if not src or len(src) != len(tgt) or len(src) != len(cats):
        ap.error('Raw data not aligned')
    out = new_output(args.out)
    source = [surface(s, cfg['case']) for s in src]
    target = [surface(t, cfg['case']) for t in tgt]
    rows = []; subrows = []; statuses = []
    buckets = defaultdict(list)
    for i, c in enumerate(cats):
        buckets[c].append(i)
    def score(name, hyp):
        rows.append(dict(run_id=name, **diagnostic_metrics(source, target, hyp)))
        for cat, ids in sorted(buckets.items()):
            subrows.append(dict(run_id=name, category=cat, **diagnostic_metrics(
                [source[i] for i in ids], [target[i] for i in ids], [hyp[i] for i in ids])))
    score('COPY_INPUT', source); score('REFERENCE_ORACLE_SANITY', target)
    for run in cfg['runs']:
        name = run['id']; status = {'run_id': name, 'status': 'BLOCKED'}
        statuses.append(status)
        print('Checking ' + name, flush=True)
        try:
            match = re.fullmatch(r'(bpe|wp|uni)_(5|10|20|30)k(?:_seed[123])?', name)
            if not match:
                raise ValueError('Legacy tokenizer provenance not established; kept separate')
            family = match[1]; tag = name.split('_seed')[0]
            expected_decoder = {'bpe': 'bpe', 'wp': 'wordpiece', 'uni': 'text'}[family]
            if run['decoder'] != expected_decoder:
                raise ValueError('Unexpected decoder for this verified pipeline')
            gen = resolve(run['generation'])
            status['generation_sha256'] = sha256(gen)
            if status['generation_sha256'] != previous[name]['generation_sha256']:
                raise ValueError('Generation file changed after diagnosis')
            streams = parse_gen(gen, len(src))
            work = gen.parent.parent
            tokenizer_path = work / 'tok' / (tag + {'bpe': '.codes', 'wp': '.json', 'uni': '.model'}[family])
            dictionary_paths = [work / ('bin_' + tag) / ('dict.' + side + '.txt')
                                for side in ('source', 'target')]
            artifacts = [tokenizer_path] + dictionary_paths
            status['artifact_sha256'] = {}
            for p in artifacts:
                digest = sha256(p)
                if not inventory.get(str(p)) or digest != inventory[str(p)]:
                    raise ValueError('Artifact missing from audit or changed: ' + str(p))
                status['artifact_sha256'][str(p)] = digest
            from fairseq.data import Dictionary
            tokenize = make_tokenizer(tokenizer_path, family)
            dictionaries = [Dictionary.load(str(p)) for p in dictionary_paths]
            status['verification'] = {}
            for kind, raw, dictionary in zip(('S', 'T'), (src, tgt), dictionaries):
                status['verification'][kind] = verify_stream(raw, streams[kind], run['decoder'],
                    cfg['case'], tokenize, dictionary, kind == 'T')
            if any(r['failures'] for r in status['verification'].values()):
                raise ValueError('Tokenizer/dictionary round-trip differs; inspect failure_examples')
            decoded = [decode(streams['H'][i], run['decoder']) for i in range(len(src))]
            hyp = [surface(h, cfg['case']) for h in decoded]
            status['hypotheses_with_unknown_marker'] = sum(bool(re.search(
                r'<+unk>+|\[UNK\]|⁇', h, re.I)) for h in decoded)
            dest = out / name; dest.mkdir()
            (dest / 'hyp.decoded.txt').write_text('\n'.join(decoded)+'\n', encoding='utf-8')
            score(name, hyp)
            status['status'] = 'VERIFIED_FOR_RETROSPECTIVE_DIAGNOSTICS'
        except Exception as exc:
            status['error'] = type(exc).__name__ + ': ' + str(exc)
        print(name + ': ' + status['status'], flush=True)
    for filename, data in [('diagnostics.csv', rows), ('subcategory_diagnostics.csv', subrows)]:
        with (out / filename).open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(data[0])); w.writeheader(); w.writerows(data)
    write_json(out / 'verification.json', statuses)
    packages = {}
    for name in ('fairseq', 'torch', 'subword-nmt', 'sentencepiece', 'tokenizers'):
        try: packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: packages[name] = None
    write_json(out / 'provenance.json', {
        'script_sha256': sha256(__file__), 'manifest_sha256': sha256(args.manifest),
        'common_sha256': sha256(Path(__file__).with_name('common.py')),
        'diagnosis_sha256': sha256(args.diagnosis), 'inventory_sha256': sha256(inventory_path),
        'raw_sha256': cfg['expected_sha256'], 'packages': packages, 'case': cfg['case'],
        'surface_rule': r'[^\W_]+|[^\w\s]|_',
        'policy': 'Raw gold retained; no NFKC/accent stripping or unknown repair for scoring. '
                  'Each run scores all rows or none. Legacy/checkpoint/split confounds remain.'})
    md = ['# Verified retrospective diagnostics', '',
          '**Not edit-based GEC F0.5; not a controlled rerun.**', '',
          '| Run | n | Word-set F1 % | Exact match % |', '|---|---:|---:|---:|']
    for r in rows:
        md.append(f'| {r["run_id"]} | {r["n"]} | {r["legacy_word_set_f1_pct"]:.4f} | {r["exact_match_pct"]:.4f} |')
    md += ['', '## Blocked', '']
    md += ['- '+r['run_id']+': '+r['error'] for r in statuses if r['status']=='BLOCKED']
    md += ['', 'Scoring retains raw gold and model unknowns. Normalization differences are not erased.',
           'Send REPORT.md, both CSVs, verification.json and provenance.json. Do not send full hypothesis folders.']
    (out/'REPORT.md').write_text('\n'.join(md)+'\n', encoding='utf-8')
    return 2 if any(r['status']=='BLOCKED' for r in statuses) else 0


if __name__ == '__main__':
    raise SystemExit(main())
