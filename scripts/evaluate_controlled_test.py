#!/usr/bin/env python3
"""Frozen 18-checkpoint test evaluation. No training or checkpoint selection."""
import argparse
from collections import Counter
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import statistics
from common import sha256,lines,parse_gen
from train_controlled import atomic_json,preflight,decoder_for,generation_args,TAGS
from eval_reconstruction import surface,metric_scores,self_check


def checked(path,digest):
    if sha256(path)!=digest:raise ValueError('Hash mismatch: '+str(path))


def score_all(hyp,ref,cats,sb):
    result={'overall':metric_scores(hyp,ref,sb),'categories':[]}
    for cat in sorted(set(cats)):
        ids=[i for i,c in enumerate(cats) if c==cat]
        result['categories'].append(dict(category=cat,**metric_scores([hyp[i] for i in ids],[ref[i] for i in ids],sb)))
    return result


def binary_parity(data,encoded,expected,n):
    from fairseq.data import Dictionary,indexed_dataset
    for side in ('source','target'):
        d=Dictionary.load(str(data/('dict.'+side+'.txt')))
        if d.symbols!=expected.symbols:raise ValueError('Dictionary identity differs')
        ds=indexed_dataset.make_dataset(str(data/('test.source-target.'+side)),impl='mmap',fix_lua_indexing=False)
        if ds is None or len(ds)!=n:raise ValueError('Binary coverage differs')
        count=0
        with (encoded/('test.'+side)).open(encoding='utf-8') as f:
            for i,line in enumerate(f):
                ids=d.encode_line(line,add_if_not_exist=False,append_eos=True)
                if not ids.equal(ds[i].long()):raise ValueError('Binary ID/order mismatch at '+str(i))
                count+=1
        if count!=n:raise ValueError('Encoded coverage differs')


def prepare_condition(tag,prepared,folder,source,ref):
    from fairseq.data import Dictionary
    folder.mkdir(exist_ok=True);encoded=folder/'encoded';encoded.mkdir(exist_ok=True)
    done=folder/'prepared.json'
    if done.exists():
        state=json.loads(done.read_text())
        for rel,digest in state['sha256'].items():checked(folder/rel,digest)
        return state
    d=Dictionary.load(str(prepared/tag/'dict.shared.txt'))
    if tag.startswith('wp_'):
        from tokenizers import Tokenizer
        tok=Tokenizer.from_file(str(prepared/tag/'tokenizer.json'))
        def encode(text):
            e=tok.encode(text,add_special_tokens=False)
            return e.tokens,tok.decode(e.ids,skip_special_tokens=False),3 in e.ids
    else:
        import sentencepiece as spm
        tok=spm.SentencePieceProcessor(model_file=str(prepared/tag/'tokenizer.model'))
        def encode(text):
            ids=tok.encode(text,out_type=int)
            return tok.encode(text,out_type=str),tok.decode(ids),3 in ids
    stats={}
    for side,texts in [('source',source),('target',ref)]:
        counts=Counter();maximum=0
        with (encoded/('test.'+side)).open('w',encoding='utf-8') as f:
            for text in texts:
                pieces,decoded,unknown=encode(text)
                if not pieces:raise ValueError('Empty encoding')
                # SP unknown pieces may be literal unseen characters; Fairseq maps them to UNK.
                counts['unknown_rows']+=bool(unknown)
                counts['roundtrip_mismatch_without_unknown']+=decoded!=text and not unknown
                counts['roundtrip_mismatch_with_unknown']+=decoded!=text and unknown
                maximum=max(maximum,len(pieces)+1);counts['n']+=1
                f.write(' '.join(pieces)+'\n')
        counts['max_tokens_with_eos']=maximum;stats[side]=dict(counts)
    atomic_json(folder/'encoding_diagnostics.json',stats)
    if any(x.get('roundtrip_mismatch_without_unknown',0) or x['max_tokens_with_eos']>3200 for x in stats.values()):
        raise ValueError('Test encoding/length gate failed. No rows skipped. Send encoding_diagnostics.json')
    data=folder/'bin'
    cmd=[sys.executable,'-m','fairseq_cli.preprocess','--source-lang','source','--target-lang','target',
         '--testpref',str(encoded/'test'),'--joined-dictionary','--srcdict',str(prepared/tag/'dict.shared.txt'),
         '--destdir',str(data),'--dataset-impl','mmap','--workers','2']
    atomic_json(folder/'preprocess_command.json',cmd)
    with (folder/'preprocess.log').open('w') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
    binary_parity(data,encoded,d,len(ref))
    artifacts=list(encoded.iterdir())+list(data.iterdir())
    state={'diagnostics':stats,'sha256':{str(p.relative_to(folder)):sha256(p) for p in artifacts if p.is_file()}}
    atomic_json(done,state);return state


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,required=True,help='Revision directory')
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--gpu',default='0')
    ap.add_argument('--prepare-only',action='store_true')
    a=ap.parse_args()
    if not a.gpu.isdigit():ap.error('Select one numeric GPU ID')
    os.environ['CUDA_VISIBLE_DEVICES']=a.gpu
    os.environ['TOKENIZERS_PARALLELISM']='false'
    import fairseq,torch,sacrebleu,sentencepiece,tokenizers
    versions={'fairseq':fairseq.__version__,'torch':torch.__version__,'sacrebleu':sacrebleu.__version__,
              'sentencepiece':sentencepiece.__version__,'tokenizers':tokenizers.__version__}
    root=a.root.resolve();out=a.out.resolve();prepared=root/'controlled_pilot_v2';binary=root/'controlled_binary_smoke_v1'
    manifest=root/'frozen_test_checkpoint_manifest.json';audit=root/'server_results/step01_run01/audit.json'
    frozen=json.loads(manifest.read_text());runs=frozen['runs']
    if len(runs)!=18 or {(r['tag'],r['seed']) for r in runs}!={(t,s) for t in TAGS for s in (42,43,44)}:raise ValueError('Need 18 unique frozen runs')
    for seed in (42,43,44):
        configpath=root/('controlled_training_seed%d'%seed)/'config.json'
        checked(configpath,frozen['metadata_sha256'][str(configpath.relative_to(root))])
        cfg=json.loads(configpath.read_text())
        checked(Path(__file__).with_name('train_controlled.py'),cfg['script_sha256'])
        for name,digest in cfg['dependencies'].items():checked(Path(__file__).with_name(name),digest)
        checked(binary/'status.json',cfg['binary_status_sha256'])
        checked(binary/'provenance.json',cfg['binary_provenance_sha256'])
        if versions!=cfg['versions']:raise ValueError('Environment differs from training: '+str(versions))
    config={'script_sha256':sha256(__file__),'manifest_sha256':sha256(manifest),'audit_sha256':sha256(audit),
            'root':str(root),'versions':versions,'dependencies':{n:sha256(Path(__file__).with_name(n)) for n in ['common.py','train_controlled.py','build_and_smoke.py','eval_reconstruction.py']},
            'policy':'Full original test; fixed validation-selected checkpoints; original IDs; no row dropping, gold repair or tokenizer fitting.'}
    if out.exists() and not (out/'config.json').exists():raise ValueError('Existing unrecognized output; choose fresh path')
    out.mkdir(exist_ok=True,parents=True)
    with (out/'RUN.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if (out/'config.json').exists():
            if json.loads((out/'config.json').read_text())!=config:raise ValueError('Configuration changed; unsafe resume')
        else:atomic_json(out/'config.json',config)
        print('Verifying training artifacts and all 18 checkpoints',flush=True)
        preflight(prepared,binary);self_check(sacrebleu)
        for r in runs:checked(root/r['checkpoint'],r['checkpoint_sha256'])
        info=json.loads(audit.read_text())['splits']['test']
        if info.get('errors'):raise ValueError('Audit contains test errors')
        raw={}
        for side in ('source','target','category'):
            entry=info['files'][side];checked(entry['path'],entry['sha256'])
            with open(entry['path'],encoding='utf-8-sig') as f:raw[side]=[x.rstrip('\r\n') for x in f]
        n=info['n_pairs']
        if n!=134025 or any(len(v)!=n or any(not x.strip() for x in v) for v in raw.values()):raise ValueError('Raw coverage invalid')
        if dict(Counter(raw['category']))!=info['categories']:raise ValueError('Category inventory differs')
        source=[surface(x,'lower') for x in raw['source']];ref=[surface(x,'lower') for x in raw['target']];cats=raw['category']
        if not all(source) or not all(ref):raise ValueError('Empty surface')
        atomic_json(out/'baselines.json',{'COPY_INPUT':score_all(source,ref,cats,sacrebleu),'REFERENCE_ORACLE_SANITY':score_all(ref,ref,cats,sacrebleu)})
        for side,values in [('source',source),('target',ref),('category',cats)]:
            (out/('test.'+side)).write_text('\n'.join(values)+'\n',encoding='utf-8')
        preparation={}
        for tag in TAGS:
            print('Preparing/checking test '+tag,flush=True)
            preparation[tag]=prepare_condition(tag,prepared,out/tag,source,ref)
        atomic_json(out/'preparation.json',preparation)
        from fairseq import options
        sample=generation_args(out/TAGS[0]/'bin',root/runs[0]['checkpoint']);sample[sample.index('--gen-subset')+1]='test'
        options.parse_args_and_arch(options.get_generation_parser(),sample[3:])
        if a.prepare_only:
            print('TEST PREPARATION PASSED. No model inference performed.',flush=True);return
        if not torch.cuda.is_available():raise ValueError('CUDA unavailable')
        results=[]
        for r in runs:
            name='%s_seed%d'%(r['tag'],r['seed']);folder=out/name;folder.mkdir(exist_ok=True)
            resultpath=folder/'scores.json';pred=folder/'predictions.jsonl';gen=folder/'generation.out'
            if resultpath.exists():
                result=json.loads(resultpath.read_text());checked(pred,result['predictions_sha256']);checked(gen,result['generation_sha256'])
                results.append(result);continue
            start=time.monotonic();cmd=generation_args(out/r['tag']/'bin',root/r['checkpoint']);cmd[cmd.index('--gen-subset')+1]='test'
            atomic_json(folder/'command.json',cmd)
            print('Generating '+name,flush=True)
            # Interrupted generation is rerun in full; no incomplete predictions are scored.
            with gen.open('w') as f,(folder/'generation.stderr.log').open('w') as err:
                subprocess.run(cmd,stdout=f,stderr=err,check=True,pass_fds=(lock.fileno(),))
            streams=parse_gen(gen,n);decode=decoder_for(r['tag'],prepared)
            hyp=[surface(decode(streams['H'][i].split()),'lower') for i in range(n)]
            with pred.open('w',encoding='utf-8') as f:
                for i,h in enumerate(hyp):f.write(json.dumps({'id':i,'category':cats[i],'hypothesis':h},ensure_ascii=False)+'\n')
            result={'tag':r['tag'],'seed':r['seed'],'selected_epoch':r['epoch'],'checkpoint_sha256':r['checkpoint_sha256'],
                    **score_all(hyp,ref,cats,sacrebleu),'seconds':time.monotonic()-start,'generation_sha256':sha256(gen),'predictions_sha256':sha256(pred)}
            atomic_json(resultpath,result);results.append(result)
            atomic_json(out/'progress.json',{'completed':len(results),'total':18,'last_run':name,'last_seconds':result['seconds']})
            print(name+' complete: chrF2=%.4f'%result['overall']['chrf2_pct'],flush=True)
        summary=[]
        for tag in TAGS:
            row={'tag':tag}
            for metric in ('chrf2_pct','bleu','exact_match_pct'):
                values=[r['overall'][metric] for r in results if r['tag']==tag]
                row[metric+'_mean']=statistics.mean(values);row[metric+'_sample_sd']=statistics.stdev(values)
            summary.append(row)
        atomic_json(out/'all_scores.json',results);atomic_json(out/'summary.json',summary)
        (out/'REPORT.md').write_text('# Controlled test evaluation\n\nAll18 validation-selected checkpoints evaluated on134025 original test rows. No checkpoint reselection. Mean ± sample SD over3 seeds.\n\n| Condition | chrF2 | BLEU | Exact match % |\n|---|---:|---:|---:|\n'+'\n'.join('| %s | %.4f ± %.4f | %.4f ± %.4f | %.4f ± %.4f |'%(r['tag'],r['chrf2_pct_mean'],r['chrf2_pct_sample_sd'],r['bleu_mean'],r['bleu_sample_sd'],r['exact_match_pct_mean'],r['exact_match_pct_sample_sd']) for r in summary)+'\n\nThese are synthetic reconstruction metrics, not edit F0.5. Sample SD is not a confidence interval. Reference quality and historical split overlap remain limitations. Paired uncertainty analysis is a separate next step.\n',encoding='utf-8')
        print('ALL 18 TEST RUNS COMPLETE',flush=True)

if __name__=='__main__':main()
