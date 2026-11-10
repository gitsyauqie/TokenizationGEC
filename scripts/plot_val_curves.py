#!/usr/bin/env python3
"""M1a: validation curves (10 epochs x 18 runs) from controlled_training_seed*/state_*.json.
Writes val_curves.csv, fig_val_curves.pdf/.png. No training or inference."""
import csv, glob, json, statistics as st, sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root = Path(sys.argv[1]); out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
data = {}
for f in glob.glob(str(root / 'controlled_training_seed4*' / 'state_*.json')):
    d = json.loads(Path(f).read_text()); assert d['status'] == 'COMPLETE'
    data[(d['tag'], d['seed'])] = [e for e in d['history']]
SEEDS = (42, 43, 44); FAM = [('spbpe', 'SP-BPE', '#2a78d6'), ('wp', 'WordPiece', '#eb6834'), ('spuni', 'SP-Unigram', '#1baf7a')]
assert len(data) == 18 and all(len(v) == 10 for v in data.values())
ep = list(range(1, 11))
def series(tag, m): return [[data[(tag, s)][i][m] for s in SEEDS] for i in range(10)]
rows = []
for fam, _, _ in FAM:
    for v in ('5k', '20k'):
        for i in range(10):
            vals = {m: [data[(fam + '_' + v, s)][i][m] for s in SEEDS] for m in ('chrf2_pct', 'bleu', 'exact_match_pct')}
            rows.append(dict(tag=fam + '_' + v, epoch=i + 1, **{m + '_mean': st.mean(x) for m, x in vals.items()},
                             **{m + '_sd': st.stdev(x) for m, x in vals.items()}))
with open(out / 'val_curves.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

plt.rcParams.update({'font.size': 8, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.edgecolor': '#8a8a85', 'axes.labelcolor': '#1f1f1e', 'xtick.color': '#55554f',
                     'ytick.color': '#55554f', 'axes.grid': True, 'grid.color': '#e6e5e0', 'grid.linewidth': 0.6})
fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.5), constrained_layout=True)
for fam, label, col in FAM:
    for v, ls, mk in (('5k', '-', 'o'), ('20k', '--', 's')):
        s = series(fam + '_' + v, 'chrf2_pct'); mean = [st.mean(x) for x in s]
        ax[0].plot(ep[1:], mean[1:], ls=ls, marker=mk, ms=3, lw=1.4, color=col, label='%s %s' % (label, v.upper()))
    for k, m in ((1, 'chrf2_pct'), (2, 'exact_match_pct')):
        a = series(fam + '_5k', m); b = series(fam + '_20k', m)
        gap = [[x - y for x, y in zip(ai, bi)] for ai, bi in zip(a, b)]
        mean = [st.mean(g) for g in gap]; lo = [min(g) for g in gap]; hi = [max(g) for g in gap]
        ax[k].fill_between(ep, lo, hi, color=col, alpha=0.12, lw=0)
        ax[k].plot(ep, mean, marker='o', ms=3, lw=1.4, color=col, label=label)
ax[0].set(title='(a) Validation chrF2', xlabel='Epoch', ylabel='chrF2')
ax[1].set(title='(b) chrF2 gap, 5K − 20K', xlabel='Epoch', ylabel='Δ chrF2 (points)')
ax[2].set(title='(c) Exact-match gap, 5K − 20K', xlabel='Epoch', ylabel='Δ EM (pp)')
for a in ax: a.set_xticks(ep); a.title.set_fontsize(8.5)
ax[0].set_xticks(ep[1:]); ax[0].set_xlim(1.6, 10.4); ax[0].set_title('(a) Validation chrF2 (epochs 2–10)', fontsize=8.5)
ax[1].axhline(0, color='#8a8a85', lw=0.8); ax[2].axhline(0, color='#8a8a85', lw=0.8)
ax[0].legend(fontsize=6, frameon=False, ncol=1, loc='lower right')
ax[1].legend(fontsize=6.5, frameon=False, loc='upper right')
fig.savefig(out / 'fig_val_curves.pdf'); fig.savefig(out / 'fig_val_curves.png', dpi=200)
print('ok', out)
