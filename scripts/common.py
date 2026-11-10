"""Strict I/O and diagnostics. These are NOT an official GEC edit scorer."""
import hashlib
import json
import re
from pathlib import Path


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def lines(path):
    with open(path, encoding='utf-8-sig') as f:
        return [s.rstrip('\r\n') for s in f]


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2,
                                    allow_nan=False) + '\n', encoding='utf-8')


def new_output(path):
    p = Path(path)
    p.mkdir(parents=True, exist_ok=False)
    return p


def canonical(s, case='preserve'):
    # Same punctuation-aware surface tokenization for EVERY condition.
    # Does not join incorrectly detached affixes. No accent stripping/NFKC.
    if case == 'lower':
        s = s.lower()
    return ' '.join(re.findall(r'\w+|[^\w\s]', s, flags=re.UNICODE))


def decode(s, mode):
    if mode == 'bpe':
        return re.sub(r'@@$', '', s.replace('@@ ', ''))
    if mode == 'wordpiece':
        # Keep punctuation spacing: canonical() treats it identically for all.
        return s.replace(' ##', '')
    if mode == 'sentencepiece':
        # Critical: remove token separator spaces BEFORE replacing U+2581.
        return ''.join(s.split()).replace('▁', ' ').strip()
    if mode == 'text':
        return s
    raise ValueError('Unknown decoder: ' + mode)


def parse_gen(path, n):
    streams = {'S': {}, 'T': {}, 'H': {}}
    with open(path, encoding='utf-8') as f:
        for ln, line in enumerate(f, 1):
            if not re.match(r'^[STH]-', line):
                continue
            parts = line.rstrip('\r\n').split('\t', 2)
            kind = parts[0][0]
            try:
                idx = int(parts[0][2:])
            except ValueError:
                raise ValueError(f'{path}:{ln}: invalid record ID')
            minimum = 3 if kind == 'H' else 2
            if len(parts) < minimum:
                raise ValueError(f'{path}:{ln}: malformed {kind} record')
            if idx in streams[kind]:
                raise ValueError(f'{path}:{ln}: duplicate {kind}-{idx}; use nbest=1')
            if kind == 'H':
                float(parts[1])  # Validate score field; do not choose last hypothesis.
                text = parts[2]
            else:
                text = '\t'.join(parts[1:])
            streams[kind][idx] = text
    expected = set(range(n))
    for kind, records in streams.items():
        actual = set(records)
        if actual != expected:
            raise ValueError(f'{path}: {kind} coverage mismatch; expected={n}, '
                             f'actual={len(actual)}, missing={sorted(expected-actual)[:10]}, '
                             f'extra={sorted(actual-expected)[:10]}')
    return streams


def legacy_counts(h, r):
    a, b = set(h.split()), set(r.split())
    return len(a & b), len(a), len(b)


def diagnostic_metrics(src, ref, hyp):
    if not src or not (len(src) == len(ref) == len(hyp)):
        raise ValueError('Nonempty aligned source/reference/hypothesis required')
    tp = nh = nr = exact = changed = clean = over = erroneous = fixed = 0
    for s, r, h in zip(src, ref, hyp):
        t, a, b = legacy_counts(h, r)
        tp += t; nh += a; nr += b
        exact += h == r
        changed += h != s
        if s == r:
            clean += 1
            over += h != s
        else:
            erroneous += 1
            fixed += h == r
    return {
        'n': len(src),
        'legacy_word_set_f1_pct': 200 * tp / (nh + nr) if nh + nr else 0.0,
        'exact_match_pct': 100 * exact / len(src),
        'changed_sentence_pct': 100 * changed / len(src),
        'n_clean': clean, 'n_erroneous': erroneous,
        'clean_overcorrection_pct': 100 * over / clean if clean else None,
        'erroneous_exact_correction_pct': 100 * fixed / erroneous if erroneous else None,
    }
