#!/usr/bin/env python3
"""Count the observed API-failure marker, without editing data or inferring quality."""
import argparse
from collections import Counter
from contextlib import ExitStack
import csv
import hashlib
import itertools
import json
from pathlib import Path
import re
import sys
from common import new_output, sha256, write_json


def classify(text):
    # Exact observed phrase, allowing surrounding quotes/case/whitespace only.
    value = ' '.join(text.strip().strip('\"\'“”‘’').split()).casefold()
    if value == 'error in api call':
        return 'exact_observed_marker'
    if re.search(r'\berror\s+in\s+api\s+call\b', value):
        return 'phrase_candidate_needs_review'
    return ''


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--audit', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    if args.out.exists(): ap.error('Output exists; use a fresh run directory.')
    audit = json.loads(args.audit.read_text(encoding='utf-8'))
    inputs = {}
    for split in ('train','valid','test'):
        info = audit['splits'][split]
        if info.get('errors'): raise ValueError('Step01 has errors: ' + split)
        for k in ('source','target','category'):
            item = info['files'][k]
            if sha256(item['path']) != item['sha256']: raise ValueError('Hash mismatch: ' + item['path'])
            inputs[split+'/'+k] = item
    counts, totals = {}, Counter()
    affected, examples, sampled = [], [], Counter()
    unique_targets = {s:set() for s in ('train','valid','test')}
    for split in ('train','valid','test'):
        print('Scanning ' + split, flush=True)
        info = audit['splits'][split]
        with ExitStack() as stack:
            fs = [stack.enter_context(open(info['files'][k]['path'],encoding='utf-8-sig')) for k in ('source','target','category')]
            n = 0
            for idx, values in enumerate(itertools.zip_longest(*fs)):
                if any(x is None for x in values): raise ValueError('File length mismatch: ' + split)
                src,tgt,cat = [x.rstrip('\r\n') for x in values]
                if not all(x.strip() for x in (src,tgt,cat)): raise ValueError('Blank input field')
                group=(split,cat);totals[group]+=1;n+=1
                c=counts.setdefault(group,Counter())
                sf,tf=classify(src),classify(tgt)
                if sf:c['source_'+sf]+=1
                if tf:c['target_'+tf]+=1
                if sf or tf:
                    c['any_flag']+=1
                    affected.append([split,idx,cat,sf,tf])
                    if split=='valid' and sampled[(cat,sf,tf)]<5:
                        examples.append([idx,cat,sf,tf,src,tgt]);sampled[(cat,sf,tf)]+=1
                if sf=='exact_observed_marker' or tf=='exact_observed_marker':c['any_exact_marker']+=1
                if sf=='exact_observed_marker':unique_targets[split].add(hashlib.sha256(tgt.encode('utf-8')).hexdigest())
            if n!=info['n_pairs']:raise ValueError('Row count mismatch: '+split)
            if {c:v for (s,c),v in totals.items() if s==split}!=info['categories']:raise ValueError('Category counts mismatch')
    for item in inputs.values():
        if sha256(item['path'])!=item['sha256']:raise ValueError('Input changed during scan')
    out=new_output(args.out)
    columns=['source_exact_observed_marker','target_exact_observed_marker','any_exact_marker',
             'source_phrase_candidate_needs_review','target_phrase_candidate_needs_review','any_flag']
    with (out/'counts.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['split','original_category','n']+columns)
        for group in sorted(totals):w.writerow([*group,totals[group]]+[counts[group][k] for k in columns])
    with (out/'affected_ids.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['split','id_zero_based','original_category','source_flag','target_flag']);w.writerows(affected)
    with (out/'validation_examples.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['id_zero_based','original_category','source_flag','target_flag','source','target']);w.writerows(examples)
    summary={}
    for split in ('train','valid','test'):
        c=Counter()
        for (s,_),v in counts.items():
            if s==split:c.update(v)
        summary[split]={'n':sum(v for (s,_),v in totals.items() if s==split),**{k:c[k] for k in columns},
                        'distinct_raw_targets_for_source_exact_marker':len(unique_targets[split])}
    write_json(out/'summary.json',summary)
    write_json(out/'provenance.json',{'script_sha256':sha256(__file__),'common_sha256':sha256(Path(__file__).with_name('common.py')),
        'audit_sha256':sha256(args.audit),'python':sys.version,'inputs':inputs,
        'trigger':'Observed validation ID 133463 in Step05; exact source Error in API call.',
        'scope':'Observed marker only; other failure messages may exist and are not ruled out.',
        'policy':'No exclusions, resplits, reference changes or model scoring. Test IDs only, no test text exported.',
        'examples':'First 5 valid rows per category/source-flag/target-flag; targeted inspection, not prevalence sample.'})
    report=['# Observed API-failure marker audit','','| Split | n | Exact source marker | Exact target marker | Any exact marker | Any flag | Distinct targets for exact source marker |',
            '|---|---:|---:|---:|---:|---:|---:|']
    for s,x in summary.items():report.append('| %s | %d | %d | %d | %d | %d | %d |'%(s,x['n'],x['source_exact_observed_marker'],x['target_exact_observed_marker'],x['any_exact_marker'],x['any_flag'],x['distinct_raw_targets_for_source_exact_marker']))
    report+=['','Exact marker permits only surrounding quote, whitespace and case differences. Longer strings containing the phrase are candidates requiring review.',
             'Source and target counts overlap; use union counts rather than summing. Flags do not remove rows.',
             'Multiple distinct targets for one marker are an input/reference ambiguity, not a recoverable linguistic corruption.',
             'Zero detected markers does not certify dataset quality or absence of other API failures.',
             'Send REPORT.md, counts.csv, affected_ids.csv, summary.json, provenance.json and validation_examples.csv.','']
    (out/'REPORT.md').write_text('\n'.join(report),encoding='utf-8')
    print(out/'REPORT.md')

if __name__=='__main__':main()
