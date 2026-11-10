#!/usr/bin/env python3
"""M1b figure: seed-42 validation chrF2 to epoch 20, and test 5K-20K gaps at epoch 10 vs 20 (three seeds).
Usage: plot_training_budget.py <revision_root> <ext20_results_dir> <out_dir>"""
import json, glob, csv, statistics as st, sys
from pathlib import Path
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
root, ext, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=True)
FAM = [('spbpe', 'SP-BPE', '#2a78d6'), ('wp', 'WordPiece', '#eb6834'), ('spuni', 'SP-Unigram', '#1baf7a')]
SEEDS = (42, 43, 44)
orig = {}
for f in glob.glob(str(root / 'controlled_training_seed4*' / 'state_*.json')):
    d = json.loads(Path(f).read_text()); orig[(d['tag'], d['seed'])] = d
t10 = {(r['tag'], r['seed']): r['overall'] for r in json.loads((root / 'controlled_test_v1' / 'all_scores.json').read_text())}
t20 = {}
for fam, _, _ in FAM:
    for v in ('5k', '20k'):
        for s in SEEDS:
            tag = '%s_%s' % (fam, v)
            t20[(tag, s)] = json.loads((ext / ('extended_seed%d' % s) / ('%s_seed%d' % (tag, s)) / 'test_epoch20' / 'scores.json').read_text())['overall']
rows = []
plt.rcParams.update({'font.size': 8, 'axes.spines.top': False, 'axes.spines.right': False, 'axes.edgecolor': '#8a8a85',
                     'xtick.color': '#55554f', 'ytick.color': '#55554f', 'axes.grid': True, 'grid.color': '#e6e5e0', 'grid.linewidth': 0.6})
fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.5), constrained_layout=True)
for fam, label, col in FAM:
    for v, ls, mk in (('5k', '-', 'o'), ('20k', '--', 's')):
        tag = '%s_%s' % (fam, v)
        pts = [(h['epoch'], h['chrf2_pct']) for h in orig[(tag, 42)]['history'] if h['epoch'] >= 2]
        ex = json.loads((ext / 'extended_seed42' / ('%s_seed42' % tag) / 'state.json').read_text())
        pts += sorted((h['epoch'], h['chrf2_pct']) for h in ex['history'])
        for e, c in pts:
            rows.append({'panel': 'a_valid_seed42', 'tag': tag, 'epoch': e, 'value': c})
        ax[0].plot([p[0] for p in pts], [p[1] for p in pts], ls=ls, marker=mk, ms=2.6, lw=1.3, color=col, label='%s %s' % (label, v.upper()))
    for k, m in ((1, 'chrf2_pct'), (2, 'exact_match_pct')):
        means = []
        for x, T in ((0, t10), (1, t20)):
            gaps = [T[(fam + '_5k', s)][m] - T[(fam + '_20k', s)][m] for s in SEEDS]
            means.append(st.mean(gaps))
            ax[k].scatter([x + {'spbpe': -0.08, 'wp': 0, 'spuni': 0.08}[fam]] * 3, gaps, s=9, color=col, alpha=0.45, lw=0)
            for s, g in zip(SEEDS, gaps):
                rows.append({'panel': 'test_gap_' + m, 'tag': fam, 'epoch': (10, 20)[x], 'seed': s, 'value': g})
        off = {'spbpe': -0.08, 'wp': 0, 'spuni': 0.08}[fam]
        ax[k].plot([0 + off, 1 + off], means, marker='o', ms=4, lw=1.5, color=col, label=label)
ax[0].axvline(10, color='#8a8a85', lw=0.8, ls=':')
ax[0].set(title='(a) Validation chrF2, seed 42', xlabel='Epoch', ylabel='chrF2'); ax[0].set_xticks([2, 4, 6, 8, 10, 12, 14, 16, 18, 20])
ax[1].set(title='(b) Test chrF2 gap, 5K − 20K', ylabel='Δ chrF2 (points)'); ax[2].set(title='(c) Test EM gap, 5K − 20K', ylabel='Δ EM (pp)')
for a in ax[1:]:
    a.set_xticks([0, 1]); a.set_xticklabels(['Epoch 10', 'Epoch 20']); a.set_xlim(-0.4, 1.4); a.axhline(0, color='#8a8a85', lw=0.8)
for a in ax: a.title.set_fontsize(8.5)
ax[0].legend(fontsize=5.6, frameon=False, loc='lower right'); ax[1].legend(fontsize=6.5, frameon=False, loc='upper right')
fig.savefig(out / 'fig_training_budget.pdf'); fig.savefig(out / 'fig_training_budget.png', dpi=200)
with open(out / 'training_budget.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['panel', 'tag', 'epoch', 'seed', 'value']); w.writeheader(); w.writerows(rows)
print('ok')
