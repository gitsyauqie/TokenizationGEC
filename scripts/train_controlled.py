#!/usr/bin/env python3
"""10-epoch controlled pilot. Full VALID chrF2 selects one best model per condition.
Single GPU, sequential conditions; no test access. Restart same command to resume.
"""
import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from common import sha256,lines,parse_gen,write_json
from build_and_smoke import architecture,TAGS
from eval_reconstruction import surface,metric_scores,self_check


def atomic_json(path,value):
    temp=path.with_suffix(path.suffix+'.tmp');write_json(temp,value);os.replace(temp,path)


def train_args(data,save,epoch,seed):
    args=architecture(data)
    args[args.index('--seed')+1]=str(seed)
    args[args.index('--max-tokens')+1]='3200'
    return args+['--batch-size','64','--required-batch-size-multiple','1',
        '--optimizer','adam','--adam-betas','(0.9, 0.98)','--clip-norm','0.1',
        '--lr','0.0005','--lr-scheduler','inverse_sqrt','--warmup-updates','4000',
        '--update-freq','2','--max-epoch',str(epoch),'--patience','-1',
        '--fp16','--fp16-init-scale','128','--disable-validation',
        '--save-dir',str(save),'--save-interval','1','--save-interval-updates','1000',
        '--keep-interval-updates','1','--no-epoch-checkpoints',
        '--distributed-world-size','1','--log-format','json','--log-interval','100','--no-progress-bar']


def generation_args(data,last):
    return [sys.executable,'-m','fairseq_cli.generate',str(data),'--path',str(last),
        '--gen-subset','valid','--source-lang','source','--target-lang','target',
        '--beam','5','--nbest','1','--max-len-a','1.2','--max-len-b','10',
        '--max-source-positions','4096','--max-target-positions','4096',
        '--max-tokens','3200','--batch-size','16','--required-batch-size-multiple','1',
        '--num-workers','0','--fp16','--seed','42','--no-progress-bar']


def next_log(folder,prefix,suffix):
    for i in range(1,100000):
        p=folder/('%s_attempt%03d%s'%(prefix,i,suffix))
        if not p.exists():return p
    raise RuntimeError('Too many attempts')


def run_child(command,stdout,lock_fd,stderr=None):
    print('Running '+stdout.name,flush=True)
    with stdout.open('x',encoding='utf-8') as log:
        if stderr is None:
            subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True,pass_fds=(lock_fd,))
        else:
            with stderr.open('x',encoding='utf-8') as err:
                subprocess.run(command,stdout=log,stderr=err,check=True,pass_fds=(lock_fd,))


def preflight(prepared,binary):
    dm=json.loads((prepared/'data_manifest.json').read_text())
    tm=json.loads((prepared/'tokenizer_manifest.json').read_text())
    pv=json.loads((binary/'provenance.json').read_text())
    ss=json.loads((binary/'status.json').read_text());status={x['tag']:x for x in ss}
    if not pv['all_six_completed'] or not pv['parameters_equal_within_vocab']:raise ValueError('Binary gates incomplete')
    if len(ss)!=6 or set(status)!=set(TAGS):raise ValueError('Missing or duplicate binary conditions')
    if sha256(prepared/'data_manifest.json')!=pv['data_manifest_sha256'] or sha256(prepared/'tokenizer_manifest.json')!=pv['tokenizer_manifest_sha256']:
        raise ValueError('Prepared manifests changed since smoke')
    for rel,digest in dm['surface_files'].items():
        if sha256(prepared/rel)!=digest:raise ValueError('Surface changed: '+rel)
    for tag in TAGS:
        if status[tag]['status']!='BINARY_AND_GPU_SMOKE_PASSED':raise ValueError('GPU smoke missing: '+tag)
        for rel,digest in status[tag]['binary_sha256'].items():
            if sha256(binary/rel)!=digest:raise ValueError('Binary changed: '+rel)
        for rel,digest in tm[tag]['files'].items():
            if sha256(prepared/rel)!=digest:raise ValueError('Tokenizer/encoded artifact changed: '+rel)
    return dm,tm,status


def decoder_for(tag,prepared):
    if tag.startswith('wp_'):
        from tokenizers import Tokenizer
        tokenizer=Tokenizer.from_file(str(prepared/tag/'tokenizer.json'))
        return lambda pieces:tokenizer.decoder.decode(pieces)
    import sentencepiece as spm
    tokenizer=spm.SentencePieceProcessor(model_file=str(prepared/tag/'tokenizer.model'))
    return lambda pieces:tokenizer.decode(pieces)


def evaluate(gen,reference,categories,decode,sb):
    streams=parse_gen(gen,len(reference))
    hyp=[surface(decode(streams['H'][i].split()),'lower') for i in range(len(reference))]
    score=metric_scores(hyp,reference,sb);subs=[]
    for cat in sorted(set(categories)):
        ids=[i for i,c in enumerate(categories) if c==cat]
        subs.append(dict(category=cat,**metric_scores([hyp[i] for i in ids],[reference[i] for i in ids],sb)))
    return score,subs


def copy_best(last,best):
    digest=sha256(last);temp=best.with_suffix('.pt.tmp');shutil.copy2(last,temp)
    if sha256(temp)!=digest:raise ValueError('Best checkpoint copy failed')
    os.replace(temp,best);return digest


def finish_run(folder,state):
    best=folder/'checkpoint_best.pt'
    if not best.exists() or sha256(best)!=state['best']['checkpoint_sha256']:
        raise ValueError('Best checkpoint integrity failure; resume checkpoints retained')
    state['status']='COMPLETE';atomic_json(folder/'state.json',state)
    # Only known temporary checkpoint names in this runner-owned directory.
    for p in (folder/'resume').glob('*.pt'):
        if re.fullmatch(r'checkpoint_last\.pt|checkpoint_\d+_\d+\.pt',p.name):p.unlink()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--prepared',type=Path,required=True)
    ap.add_argument('--binary',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--gpu',required=True)
    ap.add_argument('--seed',type=int,choices=(42,43,44),default=42)
    ap.add_argument('--check-only',action='store_true',help='Verify artifacts, versions and CLI flags; do not train')
    a=ap.parse_args()
    if not a.gpu.isdigit():ap.error('Select one numeric GPU ID')
    os.environ['CUDA_VISIBLE_DEVICES']=a.gpu
    os.environ.setdefault('TOKENIZERS_PARALLELISM','false')
    import fairseq,torch,sacrebleu,tokenizers,sentencepiece
    versions={'fairseq':fairseq.__version__,'torch':torch.__version__,'sacrebleu':sacrebleu.__version__,
              'tokenizers':tokenizers.__version__,'sentencepiece':sentencepiece.__version__}
    if versions['fairseq']!='0.10.2' or versions['sacrebleu']!='1.5.1' or versions['tokenizers']!='0.20.3' or versions['sentencepiece']!='0.2.0':
        raise ValueError('Unexpected package versions: '+str(versions))
    if not torch.cuda.is_available():raise ValueError('CUDA unavailable')
    prepared=a.prepared.resolve();binary=a.binary.resolve();out=a.out.resolve()
    config={'prepared':str(prepared),'binary':str(binary),'seed':a.seed,'epochs':10,
        'selection':'full VALID corpus chrF2; strict improvement; earliest epoch wins ties',
        'script_sha256':sha256(__file__),'dependencies':{n:sha256(Path(__file__).with_name(n)) for n in ['common.py','build_and_smoke.py','eval_reconstruction.py']},
        'binary_status_sha256':sha256(binary/'status.json'),'binary_provenance_sha256':sha256(binary/'provenance.json'),
        'versions':versions,'max_tokens':3200,'max_sentences':64,'update_freq':2,'warmup_updates':4000,
        'gpu_policy':'one selected GPU, sequential; GPU identity may differ on resume',
        'limits':'Epoch-matched exposure, not equal updates or FLOPs. Historical split/reference limitations remain. No test access.'}
    if out.exists() and not (out/'config.json').exists():raise ValueError('Existing output is not a recognized run; choose fresh path')
    out.mkdir(parents=True,exist_ok=True)
    with (out/'RUN.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if (out/'config.json').exists():
            if json.loads((out/'config.json').read_text())!=config:raise ValueError('Run configuration changed; refusing unsafe resume')
        else:atomic_json(out/'config.json',config)
        print('Checking all prepared/binary artifact hashes',flush=True)
        dm,tm,states=preflight(prepared,binary);self_check(sacrebleu)
        # Parse Fairseq train/generation flags before launching long-running work.
        from fairseq import options
        options.parse_args_and_arch(options.get_training_parser(),train_args(binary/TAGS[0]/'bin',out/'unused',1,a.seed))
        options.parse_args_and_arch(options.get_generation_parser(),generation_args(binary/TAGS[0]/'bin',out/'unused.pt')[3:])
        ref=[surface(x,'lower') for x in lines(prepared/'surface/valid.target')]
        source=[surface(x,'lower') for x in lines(prepared/'surface/valid.source')]
        cats=lines(prepared/'surface/valid.category')
        if len(ref)!=dm['splits']['valid']['retained_n'] or len(source)!=len(ref) or len(cats)!=len(ref):raise ValueError('Validation coverage differs')
        atomic_json(out/'baselines.json',{'COPY_INPUT':metric_scores(source,ref,sacrebleu),'REFERENCE_ORACLE_SANITY':metric_scores(ref,ref,sacrebleu),
            'copy_category_scores':[dict(category=c,**metric_scores([s for s,k in zip(source,cats) if k==c],[r for r,k in zip(ref,cats) if k==c],sacrebleu)) for c in sorted(set(cats))]})
        if a.check_only:
            print('PRECHECK PASSED: artifacts, versions, metric sanity and CLI flags. No training performed.',flush=True)
            return
        for tag in TAGS:
            folder=out/(tag+'_seed'+str(a.seed));folder.mkdir(exist_ok=True)
            logs=folder/'logs';logs.mkdir(exist_ok=True);resume=folder/'resume';resume.mkdir(exist_ok=True)
            statepath=folder/'state.json'
            state=json.loads(statepath.read_text()) if statepath.exists() else {'tag':tag,'seed':a.seed,'status':'ACTIVE','history':[],'trained_epoch':0,'best':None}
            if state['status']=='COMPLETE':finish_run(folder,state);continue
            decode=decoder_for(tag,prepared);data=binary/tag/'bin';last=resume/'checkpoint_last.pt'
            for epoch in range(len(state['history'])+1,11):
                start=time.monotonic();train_seconds=0
                print('%s seed%d epoch%d/10'%(tag,a.seed,epoch),flush=True)
                if state['trained_epoch']<epoch:
                    if epoch>1 and not last.exists():raise ValueError('Resume checkpoint missing; refusing restart from scratch')
                    trainlog=next_log(logs,'train_epoch%02d'%epoch,'.log')
                    command=[sys.executable,str(Path(__file__).resolve()),'--fairseq-train']+train_args(data,resume,epoch,a.seed)
                    atomic_json(logs/(trainlog.stem+'.command.json'),command)
                    run_child(command,trainlog,lock.fileno());train_seconds=time.monotonic()-start
                    if not last.exists():raise ValueError('Fairseq did not save checkpoint_last')
                    state['trained_epoch']=epoch;state['pending_checkpoint_sha256']=sha256(last);state['pending_train_seconds']=train_seconds
                    atomic_json(statepath,state)
                if sha256(last)!=state['pending_checkpoint_sha256']:raise ValueError('Pending validation checkpoint changed')
                gen=next_log(logs,'valid_epoch%02d'%epoch,'.out')
                command=generation_args(data,last)
                atomic_json(logs/(gen.stem+'.command.json'),command)
                run_child(command,gen,lock.fileno(),gen.with_suffix('.stderr.log'))
                score,category_scores=evaluate(gen,ref,cats,decode,sacrebleu)
                record={'epoch':epoch,**score,'category_scores':category_scores,'generation_sha256':sha256(gen),
                        'checkpoint_sha256':sha256(last),'train_seconds':state['pending_train_seconds'],
                        'validation_and_overhead_seconds':time.monotonic()-start-train_seconds}
                if state['best'] is None or score['chrf2_pct']>state['best']['chrf2_pct']:
                    best_hash=copy_best(last,folder/'checkpoint_best.pt')
                    state['best']={'epoch':epoch,**score,'checkpoint_sha256':best_hash}
                state['history'].append(record);atomic_json(statepath,state)
                atomic_json(folder/'best_validation.json',state['best'])
                gen.unlink() # successful generation can be regenerated from best; failed output retained
                elapsed=[x['train_seconds']+x['validation_and_overhead_seconds'] for x in state['history']]
                atomic_json(out/'progress.json',{'tag':tag,'epoch':epoch,'best':state['best'],
                    'last_epoch_seconds':elapsed[-1],'rough_remaining_seconds_this_condition':sum(elapsed)/len(elapsed)*(10-epoch),
                    'note':'Includes full-validation generation/scoring; estimate only, excludes remaining conditions and interrupted attempts.'})
                print('Validation chrF2=%.4f; best epoch=%d; elapsed=%.1f min'%(score['chrf2_pct'],state['best']['epoch'],elapsed[-1]/60),flush=True)
            finish_run(folder,state)
        summary=[]
        for tag in TAGS:
            state=json.loads((out/(tag+'_seed'+str(a.seed))/'state.json').read_text())
            summary.append({'tag':tag,'seed':a.seed,**state['best']})
        atomic_json(out/'best_models.json',summary)
        (out/'REPORT.md').write_text('# Pilot complete\n\n10 epochs per condition; best selected on full validation chrF2 only. One checkpoint_best.pt per condition retained.\n\n'
            +'\n'.join('- %s: epoch%d, chrF2 %.4f, BLEU %.4f, exact %.4f%%'%(x['tag'],x['epoch'],x['chrf2_pct'],x['bleu'],x['exact_match_pct']) for x in summary)
            +'\n\nThese are validation results, not final test scores or independent confirmation.\n',encoding='utf-8')


def strict_fairseq_train():
    from fairseq.trainer import Trainer
    from fairseq_cli import train
    original=Trainer.train_step
    def strict(self,samples,raise_oom=True):return original(self,samples,raise_oom=True)
    Trainer.train_step=strict # this subprocess only; installed Fairseq files untouched
    sys.argv=['fairseq-train']+sys.argv[2:]
    train.cli_main()

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--fairseq-train':strict_fairseq_train()
    else:main()
