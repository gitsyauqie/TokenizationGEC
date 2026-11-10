#!/usr/bin/env python3
"""Step21 (M6): how each fitted tokenizer segments the test data. No model, no training.

Per tokenizer (6 frozen fits) and per category:
- fertility: subword pieces per surface word, source and target;
- mean sequence length in pieces;
- for gold one-word substitutions (source word -> reference word, from the M4 alignment):
  piece edit distance between the two segmentations, the share of the correct word's pieces already
  present in the erroneous word, and the rate at which the correct word is a single piece.
Segmentation is computed per unique word; a gate checks on 3,000 sentences that concatenated word
segmentations equal the sentence segmentation used in training.
"""
import argparse
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from gec_metrics import extract_edits  # noqa: E402

TAGS = ['spbpe_5k', 'spbpe_20k', 'wp_5k', 'wp_20k', 'spuni_5k', 'spuni_20k']


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


def lev(a, b):
    prev = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        cur = [i] + [0] * len(b)
        for j in range(1, len(b) + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] != b[j - 1]))
        prev = cur
    return prev[-1]


def load_tokenizer(prepared, tag):
    if tag.startswith('wp_'):
        from tokenizers import Tokenizer
        tok = Tokenizer.from_file(str(prepared / tag / 'tokenizer.json'))
        return lambda text: tok.encode(text, add_special_tokens=False).tokens, sha256(prepared / tag / 'tokenizer.json')
    import sentencepiece as spm
    sp = spm.SentencePieceProcessor(model_file=str(prepared / tag / 'tokenizer.model'))
    return lambda text: sp.encode(text, out_type=str), sha256(prepared / tag / 'tokenizer.model')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--prepared', default='controlled_pilot_v2')
    ap.add_argument('--expected-n', type=int, default=134025)
    ap.add_argument('--max-mismatch-rate', type=float, default=0.0,
                    help='tolerated share of gate lines whose word-level segmentation differs (default 0: strict)')
    a = ap.parse_args()
    root = a.root.resolve(); test = root / 'controlled_test_v1'; prepared = root / a.prepared; out = a.out.resolve()
    if out.exists():
        ap.error('Output exists; choose a fresh directory.')
    src = read_lines(test / 'test.source'); ref = read_lines(test / 'test.target'); cats = read_lines(test / 'test.category')
    n = len(ref)
    if not (len(src) == n == len(cats) == a.expected_n):
        raise ValueError('Test coverage invalid')
    labels = sorted(set(cats))

    # gold one-word substitutions
    subs = defaultdict(list)
    n_edits = Counter()
    for i in range(n):
        s, r = src[i].split(), ref[i].split()
        for st, en, rep in extract_edits(s, r)[0]:
            n_edits[cats[i]] += 1
            if en - st == 1 and len(rep) == 1:
                subs[cats[i]].append((s[st], rep[0]))
    vocab = set(w for line in src + ref for w in line.split())
    print('Unique words: %d; one-word substitutions: %d' % (len(vocab), sum(len(v) for v in subs.values())), flush=True)

    overall, per_cat, hashes, gates = [], [], {}, {}
    for tag in TAGS:
        enc, digest = load_tokenizer(prepared, tag); hashes[tag] = digest
        seg = {w: enc(w) for w in vocab}
        checked, bad = 0, []
        for i in range(0, n, max(1, n // 3000)):
            for side, line in (('source', src[i]), ('target', ref[i])):
                checked += 1
                words = [p for w in line.split() for p in seg[w]]; sent = enc(line)
                if words != sent:
                    k = next((j for j, (x, y) in enumerate(zip(words, sent)) if x != y), min(len(words), len(sent)))
                    bad.append({'id': i, 'side': side, 'word_level': words[max(0, k - 4):k + 6], 'sentence_level': sent[max(0, k - 4):k + 6]})
        gates[tag] = {'checked_lines': checked, 'mismatched_lines': len(bad), 'examples': bad[:10]}
        print('%s: segmentation gate mismatches = %d of %d lines' % (tag, len(bad), checked), flush=True)
        if len(bad) > a.max_mismatch_rate * checked:
            raise ValueError('Word-level segmentation does not reproduce sentence segmentation for %s: %s' % (tag, bad[:3]))
        def stats(idx):
            ws = wt = ps = pt = single = 0
            for i in idx:
                a_, b_ = src[i].split(), ref[i].split()
                ws += len(a_); wt += len(b_)
                ps += sum(len(seg[w]) for w in a_); pt += sum(len(seg[w]) for w in b_)
                single += sum(len(seg[w]) == 1 for w in b_)
            return {'fertility_src': ps / ws, 'fertility_tgt': pt / wt, 'pieces_src_mean': ps / len(idx),
                    'pieces_tgt_mean': pt / len(idx), 'single_piece_word_rate_tgt': 100 * single / wt}
        overall.append({'tag': tag, 'n': n, **stats(range(n))})
        for c in labels:
            idx = [i for i in range(n) if cats[i] == c]
            row = {'category': c, 'tag': tag, 'n': len(idx), 'gold_edits': n_edits[c], 'one_word_subs': len(subs[c]), **stats(idx)}
            if subs[c]:
                d = [lev(seg[x], seg[y]) for x, y in subs[c]]
                sh = [sum((Counter(seg[x]) & Counter(seg[y])).values()) / len(seg[y]) for x, y in subs[c]]
                row.update({'sub_piece_edit_mean': sum(d) / len(d), 'sub_shared_pieces_pct': 100 * sum(sh) / len(sh),
                            'sub_correct_single_piece_pct': 100 * sum(len(seg[y]) == 1 for _, y in subs[c]) / len(subs[c]),
                            'sub_wrong_pieces_mean': sum(len(seg[x]) for x, _ in subs[c]) / len(subs[c]),
                            'sub_correct_pieces_mean': sum(len(seg[y]) for _, y in subs[c]) / len(subs[c])})
            per_cat.append(row)
        print(tag + ' done', flush=True)
    out.mkdir(parents=True)
    for name, rows in (('tok_overall.csv', overall), ('tok_category.csv', per_cat)):
        keys = []
        for r in rows:
            keys += [k for k in r if k not in keys]
        with open(out / name, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
    (out / 'provenance.json').write_text(json.dumps({'script_sha256': sha256(__file__), 'tokenizer_sha256': hashes,
        'test_source_sha256': sha256(test / 'test.source'), 'test_target_sha256': sha256(test / 'test.target'),
        'gate': 'Concatenated per-word segmentation equals sentence segmentation on ~3000 sampled sentences (source and target).',
        'gate_results': gates, 'max_mismatch_rate': a.max_mismatch_rate,
        'substitutions': 'Merged gold edits spanning one source word and one replacement word (M4 alignment).'}, indent=2) + '\n')
    print('DONE -> ' + str(out))


if __name__ == '__main__':
    main()
