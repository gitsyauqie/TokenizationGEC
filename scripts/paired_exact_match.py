#!/usr/bin/env python3
"""Exploratory paired exact-match intervals, not training-seed or GEC uncertainty."""
import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np
from common import decode, lines, new_output, parse_gen, sha256, write_json
from eval_reconstruction import surface


def pair_counts(a,b):
    if len(a)!=len(b) or not len(a): raise ValueError('Paired coverage mismatch')
    return int(np.sum(a & ~b)),int(np.sum(~a & b)),int(np.sum(a & b)),int(np.sum(~a & ~b))


def interval(a_only,b_only,n,seed,reps=50000):
    # Exact compression of paired row resampling for the difference of binary outcomes.
    rng=np.random.default_rng(seed)
    draws=rng.multinomial(n,[a_only/n,b_only/n,(n-a_only-b_only)/n],size=reps)
    delta=100.0*(draws[:,0]-draws[:,1])/n
    return [float(x) for x in np.percentile(delta,[2.5,97.5])]


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--scores-dir',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    if a.out.exists():ap.error('Output exists; use a fresh run directory.')
    cfg=json.loads(a.manifest.read_text());pv=json.loads((a.scores_dir/'provenance.json').read_text())
    if sha256(a.manifest)!=pv['manifest_sha256']:raise ValueError('Manifest changed')
    if sha256(Path(__file__).with_name('common.py'))!=pv['common_sha256']:raise ValueError('Decoder changed')
    if sha256(Path(__file__).with_name('eval_reconstruction.py'))!=pv['script_sha256']:raise ValueError('Scoring surface code changed')
    if cfg['expected_sha256']!=pv['raw_sha256'] or cfg['case']!=pv['case']:raise ValueError('Input policy changed')
    resolve=lambda p:(a.manifest.resolve().parent/p).resolve()
    for k in ('source','target','category'):
        if sha256(resolve(cfg[k]))!=pv['raw_sha256'][k]:raise ValueError('Raw hash changed: '+k)
    src,tgt,cats=[lines(resolve(cfg[k])) for k in ('source','target','category')]
    n=len(tgt)
    if not n or len(src)!=n or len(cats)!=n:raise ValueError('Raw length mismatch')
    target=[surface(t,cfg['case']) for t in tgt]
    masks={'COPY_INPUT':np.array([surface(s,cfg['case'])==t for s,t in zip(src,target)],dtype=bool)}
    statuses={r['run_id']:r for r in json.loads((a.scores_dir/'run_status.json').read_text())}
    with (a.scores_dir/'scores.csv').open() as f:scored={r['run_id']:r for r in csv.DictReader(f)}
    chosen=[]
    for run in cfg['runs']:
        if run.get('training_seed')!=42 or statuses[run['id']]['status']!='SCORED':continue
        name=run['id'];gen=resolve(run['generation']);digest=sha256(gen)
        if digest!=statuses[name]['generation_sha256']:raise ValueError('Generation changed: '+name)
        print('Reading '+name,flush=True)
        streams=parse_gen(gen,n)
        mask=np.array([surface(decode(streams['H'][i],run['decoder']),cfg['case'])==target[i] for i in range(n)],dtype=bool)
        del streams
        if sha256(gen)!=digest:raise ValueError('Generation changed while reading')
        masks[name]=mask;chosen.append(name)
    if len(chosen)<2:raise ValueError('Need at least two previously scored seed42 runs')
    for name,mask in masks.items():
        if int(scored[name]['n'])!=n or abs(100*float(mask.mean())-float(scored[name]['exact_match_pct']))>1e-8:
            raise ValueError('Exact match does not reproduce Step07: '+name)
    groups={c:np.array([i for i,x in enumerate(cats) if x==c]) for c in sorted(set(cats))}
    rows=[];subrows=[]
    for na,nb in itertools.combinations(sorted(masks),2):
        ac,bc,both,neither=pair_counts(masks[na],masks[nb])
        seed=int(hashlib.sha256(('20261008|'+na+'|'+nb).encode()).hexdigest()[:16],16)
        lo,hi=interval(ac,bc,n,seed)
        rows.append(dict(model_a=na,model_b=nb,n=n,a_only_exact=ac,b_only_exact=bc,both_exact=both,neither_exact=neither,
                         delta_a_minus_b_pp=100*(ac-bc)/n,exploratory_iid_ci95_low=lo,exploratory_iid_ci95_high=hi))
        for cat,ids in groups.items():
            x,y,z,w=pair_counts(masks[na][ids],masks[nb][ids])
            subrows.append(dict(model_a=na,model_b=nb,category=cat,n=len(ids),a_only_exact=x,b_only_exact=y,
                                both_exact=z,neither_exact=w,delta_a_minus_b_pp=100*(x-y)/len(ids)))
    for k in ('source','target','category'):
        if sha256(resolve(cfg[k]))!=pv['raw_sha256'][k]:raise ValueError('Raw changed during run')
    out=new_output(a.out)
    for file,data in [('paired_exact.csv',rows),('paired_exact_categories.csv',subrows)]:
        with (out/file).open('w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
    write_json(out/'provenance.json',{'script_sha256':sha256(__file__),'manifest_sha256':sha256(a.manifest),
        'step07_provenance_sha256':sha256(a.scores_dir/'provenance.json'),'step07_scores_sha256':sha256(a.scores_dir/'scores.csv'),
        'step07_status_sha256':sha256(a.scores_dir/'run_status.json'),'numpy':np.__version__,'models':sorted(masks),
        'raw_sha256':pv['raw_sha256'],'replicates':50000,'seed':'sha256 of 20261008|model_a|model_b first 16 hex digits',
        'method':'Paired row bootstrap of binary exact-match differences, multinomial sufficient counts, percentile nominal 95% intervals.',
        'limits':'Post-hoc exploratory; all eligible seed42 pairs and COPY_INPUT. No multiplicity adjustment, document clustering, training-seed uncertainty, BLEU/chrF inference or causal comparison. Unknown row dependence can understate uncertainty.'})
    (out/'REPORT.md').write_text('# Exploratory paired exact match\n\n'
        +str(len(chosen))+' previously scored seed42 runs + COPY_INPUT; '+str(n)+' unchanged test rows.\n\n'
        +str(len(rows))+' paired comparisons. All exact-match rates reproduce Step07.\n\n'
        'Positive delta means A matches more full reference sentences than B. A-only/B-only counts reveal disagreements hidden by aggregate rates.\n\n'
        'Intervals assume independent rows, not documents; repeated targets/unknown document groups can violate this assumption. '
        'Intervals are exploratory, unadjusted for multiple comparisons, and conditional on fixed checkpoints. '
        'They cannot establish a universally best tokenizer, training-seed robustness or significance for chrF/BLEU.\n\n'
        'Send REPORT.md, paired_exact.csv, paired_exact_categories.csv and provenance.json.\n',encoding='utf-8')
    print(out/'REPORT.md')

if __name__=='__main__':main()
