#!/usr/bin/env python3
"""Recalculate descriptive claims from the supplied draft table, NOT new experiments."""
import argparse
import csv
from pathlib import Path
from common import new_output, write_json, sha256


def ranks(values):
    ordered = sorted(enumerate(values), key=lambda p: p[1])
    result = [0.0] * len(values)
    i = 0
    while i < len(ordered):
        j = i + 1
        while j < len(ordered) and ordered[j][1] == ordered[i][1]:
            j += 1
        rank = (i + 1 + j) / 2
        for k in range(i, j):
            result[ordered[k][0]] = rank
        i = j
    return result


def spearman(x, y):
    a, b = ranks(x), ranks(y)
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    numerator = sum((u - ma) * (v - mb) for u, v in zip(a, b))
    denominator = (sum((u - ma)**2 for u in a) * sum((v - mb)**2 for v in b))**.5
    return numerator / denominator if denominator else None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--csv', required=True, type=Path)
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args()
    with args.csv.open(encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r['fb'] = float(r['fb']); r['f1_pct'] = float(r['f1_pct']); r['vocab'] = int(r['vocab'])
    out = new_output(args.out)
    report = {'source': 'TRANSCRIBED DRAFT TABLE; not validated experimental results',
              'csv_sha256': sha256(args.csv), 'correlations': {}}
    for name, families in [('all', ('bpe', 'wp', 'uni')), ('bpe_wp_pooled', ('bpe', 'wp')),
                           ('bpe', ('bpe',)), ('wp', ('wp',)), ('uni', ('uni',))]:
        subset = [r for r in rows if r['family'] in families]
        report['correlations'][name] = {'n': len(subset),
            'rho': spearman([r['fb'] for r in subset], [r['f1_pct'] for r in subset])}
    best, worst = max(rows, key=lambda r: r['f1_pct']), min(rows, key=lambda r: r['f1_pct'])
    report.update(best=best, worst=worst, gap_pp=best['f1_pct'] - worst['f1_pct'])
    write_json(out / 'draft_table_audit.json', report)
    md = ['# Draft table arithmetic audit', '',
          '**Input: numbers transcribed from user-supplied draft, not server results.**', '',
          '| Group | n configurations | Spearman rho |', '|---|---:|---:|']
    for name, result in report['correlations'].items():
        md.append(f'| {name} | {result["n"]} | {result["rho"]:.6f} |')
    md += ['', f'Best–worst difference: {report["gap_pp"]:.2f} percentage points.',
           'P-values are deliberately not inferred from the draft. Four sizes per family are exploratory.',
           'Seeds are not additional independent tokenizer configurations.']
    (out / 'REPORT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(out / 'REPORT.md')


if __name__ == '__main__':
    main()
