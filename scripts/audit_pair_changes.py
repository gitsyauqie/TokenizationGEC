#!/usr/bin/env python3
"""Describe observed pair changes; never infer correctness or historical generators."""
import argparse
from collections import Counter
from contextlib import ExitStack
import csv
import hashlib
import itertools
import json
from pathlib import Path
import random
import re
import sys
from common import new_output, sha256, write_json

FLAGS = ('exact_same', 'whitespace_only', 'case_only_after_whitespace',
         'punctuation_only_after_whitespace', 'digit_sequence_changed',
         'source_word_count_smaller', 'source_word_count_larger',
         'source_word_count_same', 'target_under_6_words',
         'target_over_1000_characters', 'target_replacement_character')

def inspect_pair(source, target):
    s, t = ' '.join(source.split()), ' '.join(target.split())
    sw, tw = len(s.split()), len(t.split())
    flags = set()
    if source == target:
        flags.add('exact_same')
    elif s == t:
        flags.add('whitespace_only')
    elif s.lower() == t.lower():
        flags.add('case_only_after_whitespace')
    elif re.findall(r'\w+', s) == re.findall(r'\w+', t):
        flags.add('punctuation_only_after_whitespace')
    if re.findall(r'\d+', s) != re.findall(r'\d+', t):
        flags.add('digit_sequence_changed')
    flags.add('source_word_count_' + ('smaller' if sw < tw else 'larger' if sw > tw else 'same'))
    if tw < 6: flags.add('target_under_6_words')
    if len(target) > 1000: flags.add('target_over_1000_characters')
    if '\ufffd' in target: flags.add('target_replacement_character')
    return flags


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--audit', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    if args.out.exists():
        ap.error('Output already exists. Choose a fresh run directory; do not delete old results.')
    audit = json.loads(args.audit.read_text(encoding='utf-8'))
    verified = {}
    for split in ('train', 'valid', 'test'):
        info = audit['splits'][split]
        if info.get('errors'): raise ValueError('Original audit reports errors: ' + split)
        for key in ('source', 'target', 'category'):
            entry = info['files'][key]
            if sha256(entry['path']) != entry['sha256']:
                raise ValueError('Input hash differs from Step01: ' + entry['path'])
            verified[split + '/' + key] = entry
    counts, flags_by_group, buckets, seen, rngs = Counter(), {}, {}, Counter(), {}
    for split in ('train', 'valid', 'test'):
        print('Scanning ' + split, flush=True)
        info = audit['splits'][split]
        with ExitStack() as stack:
            handles = [stack.enter_context(open(info['files'][k]['path'], encoding='utf-8-sig'))
                       for k in ('source', 'target', 'category')]
            n = 0
            for idx, values in enumerate(itertools.zip_longest(*handles)):
                if any(v is None for v in values): raise ValueError('Length mismatch: ' + split)
                source, target, category = [v.rstrip('\r\n') for v in values]
                if not all(v.strip() for v in (source, target, category)):
                    raise ValueError('Blank field: %s ID %d' % (split, idx))
                group = (split, category)
                counts[group] += 1
                flags = inspect_pair(source, target)
                flags_by_group.setdefault(group, Counter()).update(flags)
                n += 1
                # Validation-only targeted examples, not a representative quality sample.
                if split == 'valid':
                    for flag in sorted(flags - {'source_word_count_same'}):
                        key = (category, flag)
                        seen[key] += 1
                        if key not in buckets:
                            buckets[key] = []
                            seed = int(hashlib.sha256(('20261008|' + category + '|' + flag).encode()).hexdigest(), 16)
                            rngs[key] = random.Random(seed)
                        bucket = buckets[key]
                        item = [idx, category, flag, source, target]
                        if len(bucket) < 3: bucket.append(item)
                        else:
                            j = rngs[key].randrange(seen[key])
                            if j < 3: bucket[j] = item
            if n != info['n_pairs']: raise ValueError('Row count changed: ' + split)
            observed = {c: v for (sp, c), v in counts.items() if sp == split}
            if observed != info['categories']: raise ValueError('Category counts changed: ' + split)
    # Detect input changes during the scan before publishing outputs.
    for entry in verified.values():
        if sha256(entry['path']) != entry['sha256']: raise ValueError('Input changed during scan')
    out = new_output(args.out)
    with (out/'counts.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['split','original_category','n','flag','rows','percent'])
        for group in sorted(counts):
            for flag in FLAGS:
                value = flags_by_group[group][flag]
                w.writerow([*group, counts[group], flag, value, round(100 * value / counts[group], 6)])
    with (out/'validation_examples.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['id_zero_based','original_category','sampling_flag','source','target','review_notes'])
        for key in sorted(buckets):
            for row in sorted(buckets[key]): w.writerow(row + [''])
    write_json(out/'provenance.json', {
        'audit_sha256': sha256(args.audit), 'script_sha256': sha256(__file__),
        'common_sha256': sha256(Path(__file__).with_name('common.py')),
        'python': sys.version, 'inputs': verified,
        'claude_history': 'User reports Claude API use; historical prompt and configuration unavailable.',
        'generator_attribution': 'Original labels retained; a label or suffix does not verify a generator/version.',
        'sampling': 'VALID only, max 3 per category/flag, deterministic reservoir; examples may repeat across flags; not prevalence sample.',
        'gold_policy': 'No normalization written back; no reference validation, row exclusion, resplit, scoring or training.'})
    report = ['# Observed pair changes — not GEC scores', '',
              'All nine raw files match Step01 hashes before and after scanning. This is a hash manifest, not a physical backup.', '',
              '| Split | Rows | Exact same | Whitespace only | Digit sequence changed | Target <6 words |',
              '|---|---:|---:|---:|---:|---:|']
    for split in ('train','valid','test'):
        total = sum(n for (sp, _), n in counts.items() if sp == split)
        combined = Counter()
        for (sp, _), values in flags_by_group.items():
            if sp == split: combined.update(values)
        report.append('| %s | %d | %d | %d | %d | %d |' % (split,total,combined['exact_same'],combined['whitespace_only'],combined['digit_sequence_changed'],combined['target_under_6_words']))
    report.extend(['', '## Definitions and limits', '',
        '- Whitespace normalization is used only to classify differences. Raw texts are preserved.',
        '- Exact/whitespace/case/punctuation classes are mutually exclusive in that priority order. Other flags overlap; do not sum them.',
        '- Punctuation-only means matching case-sensitive Python Unicode word-token lists after whitespace normalization; underscores belong to word tokens. It is a surface heuristic.',
        '- Digit sequence changed compares ordered digit runs. This is not proof of a factual error; punctuation changes in numbers also need review.',
        '- Word counts use whitespace splitting. Smaller/larger source counts do not identify semantic deletion/insertion or a generator.',
        '- Short/long targets and replacement characters are review flags, not rejection rules or evidence of OCR.',
        '- Original category labels are retained. No historical prompt, model version, or linguistic correctness is inferred.',
        '- Test aggregates describe the existing benchmark only. Do not use them to tune filtering thresholds or choose favorable test examples.',
        '- Examples are validation-only and intentionally flag-targeted; repeated IDs and unequal category weights preclude quality-prevalence estimates.', '',
        'Send REPORT.md, counts.csv, provenance.json and validation_examples.csv. Examples contain raw validation text.', ''])
    (out/'REPORT.md').write_text('\n'.join(report), encoding='utf-8')
    print(out/'REPORT.md')

if __name__ == '__main__':
    main()
