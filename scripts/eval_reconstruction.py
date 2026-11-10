#!/usr/bin/env python3
"""Retrospective reconstruction metrics on previously verified full test predictions.
Not GEC edit F0.5, human validation, a controlled rerun, or causal tokenizer evidence.
"""
import argparse
from collections import defaultdict
import csv
import json
from pathlib import Path
import re
import sys
from common import decode, lines, new_output, parse_gen, sha256, write_json


def surface(text, case):
    if case == 'lower': text = text.lower()
    return ' '.join(re.findall(r'[^\W_]+|[^\w\s]|_', text, flags=re.UNICODE))


def metric_scores(hyp, ref, sacrebleu):
    if not hyp or len(hyp) != len(ref): raise ValueError('Metric input coverage mismatch')
    bleu = sacrebleu.corpus_bleu(hyp, [ref], tokenize='none', lowercase=False,
                                smooth_method='exp', force=True, use_effective_order=False).score
    # SacreBLEU 1.5.1 chrF.score is 0..1, unlike BLEU; version is strictly pinned.
    chrf = 100.0 * sacrebleu.corpus_chrf(hyp, [ref], order=6, beta=2, remove_whitespace=True).score
    return {'n':len(ref),'chrf2_pct':chrf,'bleu':bleu,
            'exact_match_pct':100.0*sum(h==t for h,t in zip(hyp,ref))/len(ref)}


def self_check(sb):
    ref=['saya membaca buku baru di rumah hari ini .']
    same=metric_scores(ref,ref,sb)
    changed=metric_scores(['buku baru membaca saya di rumah hari ini .'],ref,sb)
    if any(abs(same[k]-100)>1e-6 for k in ('chrf2_pct','bleu','exact_match_pct')):
        raise ValueError('Oracle metric sanity failed; check version/scaling')
    if not (changed['chrf2_pct']<100 and changed['bleu']<100 and changed['exact_match_pct']==0):
        raise ValueError('Word-order sensitivity sanity failed')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--verified',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    if a.out.exists():ap.error('Output exists; select a fresh run directory.')
    import sacrebleu
    if sacrebleu.__version__!='1.5.1':ap.error('Expected existing server sacrebleu==1.5.1; report installed version rather than changing environment: '+sacrebleu.__version__)
    self_check(sacrebleu)
    cfg=json.loads(a.manifest.read_text(encoding='utf-8'))
    pv=json.loads((a.verified/'provenance.json').read_text(encoding='utf-8'))
    old=json.loads((a.verified/'verification.json').read_text(encoding='utf-8'))
    if sha256(a.manifest)!=pv['manifest_sha256']:raise ValueError('Manifest changed since verification')
    if sha256(Path(__file__).with_name('common.py'))!=pv['common_sha256']:raise ValueError('Common decoding code changed since verification')
    if cfg['case']!=pv['case'] or cfg['case'] not in ('lower','preserve'):raise ValueError('Case policy mismatch')
    if pv['surface_rule']!=r'[^\W_]+|[^\w\s]|_':raise ValueError('Surface rule mismatch')
    if cfg['expected_sha256']!=pv['raw_sha256']:raise ValueError('Raw provenance mismatch')
    runmap={r['id']:r for r in cfg['runs']}
    statuses={r['run_id']:r for r in old}
    if len(runmap)!=len(cfg['runs']) or len(statuses)!=len(old) or set(runmap)!=set(statuses):raise ValueError('Run IDs duplicated or inconsistent')
    resolve=lambda p:(a.manifest.resolve().parent/p).resolve()
    for k in ('source','target','category'):
        if sha256(resolve(cfg[k]))!=cfg['expected_sha256'][k]:raise ValueError('Raw data hash mismatch: '+k)
    src,tgt,cats=[lines(resolve(cfg[k])) for k in ('source','target','category')]
    if not src or len(src)!=len(tgt) or len(src)!=len(cats) or not all(x.strip() for x in src+tgt+cats):raise ValueError('Invalid raw coverage')
    source=[surface(x,cfg['case']) for x in src];target=[surface(x,cfg['case']) for x in tgt]
    groups=defaultdict(list)
    for i,c in enumerate(cats):groups[c].append(i)
    out=new_output(a.out)
    rows=[];subrows=[];result_status=[]
    def score(name,hyp):
        result=[dict(run_id=name,**metric_scores(hyp,target,sacrebleu))]
        subs=[]
        for cat,ids in sorted(groups.items()):
            subs.append(dict(run_id=name,category=cat,**metric_scores([hyp[i] for i in ids],[target[i] for i in ids],sacrebleu)))
        # Append only after all metrics succeed; no partially scored run.
        rows.extend(result);subrows.extend(subs)
    print('Scoring COPY_INPUT',flush=True);score('COPY_INPUT',source)
    print('Scoring REFERENCE_ORACLE_SANITY',flush=True);score('REFERENCE_ORACLE_SANITY',target)
    for name,run in runmap.items():
        previous=statuses[name];state={'run_id':name,'status':'BLOCKED'};result_status.append(state)
        if previous['status']!='VERIFIED_FOR_RETROSPECTIVE_DIAGNOSTICS':
            state['reason']='Not verified at Step02: '+previous.get('error',previous['status']);continue
        print('Scoring '+name,flush=True)
        try:
            if run['expected_n']!=len(src):raise ValueError('Manifest n mismatch')
            gen=resolve(run['generation']);digest=sha256(gen)
            if digest!=previous['generation_sha256']:raise ValueError('Generation changed since verification')
            for p,h in previous['artifact_sha256'].items():
                if sha256(p)!=h:raise ValueError('Tokenizer/dictionary changed: '+p)
            if any(x['failures'] for x in previous['verification'].values()):raise ValueError('Prior verification has failures')
            streams=parse_gen(gen,len(src))
            hyp=[surface(decode(streams['H'][i],run['decoder']),cfg['case']) for i in range(len(src))]
            del streams
            if sha256(gen)!=digest:raise ValueError('Generation changed during parsing')
            score(name,hyp);state.update(status='SCORED',generation_sha256=digest)
        except Exception as exc:state['reason']=type(exc).__name__+': '+str(exc)
        print(name+': '+state['status'],flush=True)
    for k in ('source','target','category'):
        if sha256(resolve(cfg[k]))!=cfg['expected_sha256'][k]:raise ValueError('Raw data changed during evaluation; discard incomplete output')
    baseline=rows[0]
    for x in rows:
        for k in ('chrf2_pct','bleu','exact_match_pct'):x['delta_copy_'+k]=x[k]-baseline[k]
    for name,data in [('scores.csv',rows),('category_scores.csv',subrows)]:
        with (out/name).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    write_json(out/'run_status.json',result_status)
    write_json(out/'provenance.json',{'script_sha256':sha256(__file__),'common_sha256':sha256(Path(__file__).with_name('common.py')),
        'manifest_sha256':sha256(a.manifest),'verification_sha256':sha256(a.verified/'verification.json'),
        'prior_provenance_sha256':sha256(a.verified/'provenance.json'),'raw_sha256':cfg['expected_sha256'],
        'python':sys.version,'sacrebleu':sacrebleu.__version__,'case':cfg['case'],'surface_rule':pv['surface_rule'],
        'metrics':{'chrF2':'char order 6, beta 2, remove whitespace, corpus aggregation, 1.5.1 score multiplied by 100',
                   'BLEU':'common surface tokens, tokenize none, exp smoothing, effective_order false, corpus aggregation',
                   'exact_match':'same common surface tokens; NOT byte-identical raw strings'},
        'policy':'Full original test, single raw reference, no row exclusions, NFKC/accent removal, unknown repair or category remapping. Higher is better. Not edit-based GEC F0.5.',
        'remaining_limits':'Reference quality, non-identical training/checkpoint protocols, incomplete sweep, overlap and historical generator provenance remain unresolved.'})
    md=['# Retrospective synthetic reconstruction metrics','','Not GEC edit F0.5 or a controlled retraining experiment. All scores use original full test rows.',
        'chrF2 and BLEU are corpus scores; category scores are descriptive, not averaged into the overall score.',
        'All metrics use the same lower/preserve policy and punctuation/underscore surface rule as verified Step02.','',
        '| Run | n | chrF2 /100 | BLEU /100 | Exact match % |','|---|---:|---:|---:|---:|']
    for x in rows:md.append('| %s | %d | %.4f | %.4f | %.4f |'%(x['run_id'],x['n'],x['chrf2_pct'],x['bleu'],x['exact_match_pct']))
    md+=['','## Blocked runs']
    for x in result_status:
        if x['status']=='BLOCKED':md.append('- '+x['run_id']+': '+x['reason'])
    md+=['','No significance or seed-averaged claim is computed. A model matching a flawed reference can still score highly.',
         'Send REPORT.md, scores.csv, category_scores.csv, run_status.json, provenance.json.','']
    (out/'REPORT.md').write_text('\n'.join(md),encoding='utf-8')
    print(out/'REPORT.md')

if __name__=='__main__':main()
