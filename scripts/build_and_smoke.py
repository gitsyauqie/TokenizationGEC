#!/usr/bin/env python3
"""Binarize all six prepared conditions, verify dictionaries, optionally smoke GPU.
No full training, checkpoint selection, test access, or benchmark scores.
"""
import argparse
from collections import defaultdict
import csv
import gc
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from common import new_output,sha256,write_json
TAGS=['spbpe_5k','spbpe_20k','wp_5k','wp_20k','spuni_5k','spuni_20k']
MAX_POS=4096


def architecture(data):
    return [str(data),'--task','translation','--source-lang','source','--target-lang','target',
        '--arch','transformer','--encoder-layers','4','--decoder-layers','4',
        '--encoder-attention-heads','8','--decoder-attention-heads','8',
        '--encoder-embed-dim','256','--decoder-embed-dim','256',
        '--encoder-ffn-embed-dim','2048','--decoder-ffn-embed-dim','2048',
        '--dropout','0.3','--attention-dropout','0.1','--share-decoder-input-output-embed',
        '--criterion','label_smoothed_cross_entropy','--label-smoothing','0.1',
        '--max-source-positions',str(MAX_POS),'--max-target-positions',str(MAX_POS),
        '--seed','42','--max-tokens','4096','--dataset-impl','mmap','--num-workers','0']


def preflight(prepared):
    dm=json.loads((prepared/'data_manifest.json').read_text())
    tm=json.loads((prepared/'tokenizer_manifest.json').read_text())
    status={x['tag']:x for x in json.loads((prepared/'status.json').read_text())}
    if set(status)!=set(TAGS) or set(tm)!=set(TAGS):raise ValueError('Need all six conditions')
    with (prepared/'lengths_and_roundtrip.csv').open() as f:rows=list(csv.DictReader(f))
    table={(x['tag'],x['split'],x['side']):x for x in rows}
    if len(rows)!=24 or len(table)!=24:raise ValueError('Need 24 unique length rows')
    for tag in TAGS:
        if status[tag]['status']!='PREPARED_PENDING_LENGTH_AND_UNK_REVIEW':raise ValueError('Tokenizer not prepared: '+tag)
        for split in ('train','valid'):
            for side in ('source','target'):
                x=table[(tag,split,side)]
                if int(x['n'])!=dm['splits'][split]['retained_n']:raise ValueError('Row counts disagree')
                if int(x['max_tokens_with_eos'])>MAX_POS:raise ValueError('Position limit insufficient; do not skip rows')
                if int(x['roundtrip_mismatch_without_unknown']) or (split=='train' and int(x['unknown_rows'])):
                    raise ValueError('Tokenizer gate not passed')
        for rel,digest in tm[tag]['files'].items():
            if sha256(prepared/rel)!=digest:raise ValueError('Prepared artifact changed: '+rel)
    for rel,digest in dm['surface_files'].items():
        if sha256(prepared/rel)!=digest:raise ValueError('Surface changed: '+rel)
    return dm,tm,table


def check_binary(data,encoded,expected_dict,expected_vocab,table,tag):
    import numpy as np
    import torch
    from fairseq.data import Dictionary,indexed_dataset
    dictionaries={side:Dictionary.load(str(data/('dict.'+side+'.txt'))) for side in ('source','target')}
    for side,d in dictionaries.items():
        if d.symbols!=expected_dict.symbols or len(d)!=expected_vocab:raise ValueError('Dictionary changed in binarization')
        if (d.bos(),d.pad(),d.eos(),d.unk())!=(0,1,2,3):raise ValueError('Special IDs differ')
    checked=[]
    for split in ('train','valid'):
        for side in ('source','target'):
            d=dictionaries[side];ds=indexed_dataset.make_dataset(str(data/(split+'.source-target.'+side)),impl='mmap',fix_lua_indexing=False)
            if ds is None:raise ValueError('Missing binary dataset')
            x=table[(tag,split,side)]
            if len(ds)!=int(x['n']) or int(np.sum(ds.sizes))!=int(x['tokens'])+len(ds) or int(np.max(ds.sizes))!=int(x['max_tokens_with_eos']):
                raise ValueError('Binary lengths/totals mismatch')
            ids=set(range(min(16,len(ds))))|set(range(max(0,len(ds)-16),len(ds)))|{int(np.argmax(ds.sizes))}
            sampled=0
            with (encoded/(split+'.'+side)).open(encoding='utf-8') as f:
                for i,line in enumerate(f):
                    if i not in ids:continue
                    expected=d.encode_line(line,add_if_not_exist=False,append_eos=True)
                    if not torch.equal(ds[i].long(),expected.long()):raise ValueError('Binary sample order/content mismatch')
                    sampled+=1
            if sampled!=len(ids):raise ValueError('Sample coverage mismatch')
            checked.append({'split':split,'side':side,'n':len(ds),'tokens_including_eos':int(np.sum(ds.sizes)),'sampled_exact_rows':sampled})
            del ds
    return checked


def smoke(task,model,args):
    import numpy as np
    import torch
    from fairseq import utils
    if not torch.cuda.is_available():raise RuntimeError('CUDA unavailable; choose --cpu-only for binarization without GPU smoke')
    task.load_dataset('train',epoch=1)
    ds=task.dataset('train')
    longest_src=int(np.argmax(ds.src_sizes));longest_tgt=int(np.argmax(ds.tgt_sizes))
    short=np.flatnonzero((ds.src_sizes<=128)&(ds.tgt_sizes<=128))[:8].tolist()
    if not short:raise ValueError('No short examples for smoke')
    batches=[('short_batch',short),('longest_source',[longest_src]),('longest_target',[longest_tgt])]
    model=model.cuda();model.train();criterion=task.build_criterion(args).cuda()
    optimizer=torch.optim.Adam(model.parameters(),lr=5e-4,betas=(0.9,0.98))
    scaler=torch.cuda.amp.GradScaler(init_scale=128.0)
    logs=[]
    for label,ids in batches:
        optimizer.zero_grad(set_to_none=True);torch.cuda.reset_peak_memory_stats()
        sample=utils.move_to_cuda(ds.collater([ds[i] for i in ids]));start=time.monotonic()
        with torch.cuda.amp.autocast():
            loss,denom,logging_output=criterion(model,sample)
            loss=loss/max(1,denom)
        if not torch.isfinite(loss).item():raise ValueError('Nonfinite smoke loss')
        scaler.scale(loss).backward();scaler.unscale_(optimizer)
        if any(not torch.isfinite(p.grad).all().item() for p in model.parameters() if p.grad is not None):
            raise ValueError('Nonfinite gradients during smoke; no result accepted')
        norm=torch.nn.utils.clip_grad_norm_(model.parameters(),0.1)
        scaler.step(optimizer);scaler.update();torch.cuda.synchronize()
        logs.append({'batch':label,'derived_ids':ids,'sentences':len(ids),'tokens':int(sample['ntokens']),
            'normalized_loss':float(loss.detach()),'gradient_norm_before_clip':float(norm),
            'seconds':time.monotonic()-start,'peak_allocated_bytes':torch.cuda.max_memory_allocated(),
            'peak_reserved_bytes':torch.cuda.max_memory_reserved()})
        del sample,loss
    del optimizer,criterion,model,ds
    gc.collect();torch.cuda.empty_cache()
    return logs


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--prepared',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--workers',type=int,default=8)
    group=ap.add_mutually_exclusive_group(required=True)
    group.add_argument('--gpu',help='One available physical GPU ID; used sequentially')
    group.add_argument('--cpu-only',action='store_true')
    a=ap.parse_args()
    if a.out.exists():ap.error('Output exists; preserve it and use a new run directory')
    if a.workers<1:ap.error('workers must be positive')
    if a.gpu is not None:
        if not a.gpu.isdigit():ap.error('Select one numeric GPU ID')
        os.environ['CUDA_VISIBLE_DEVICES']=a.gpu
    else:os.environ['CUDA_VISIBLE_DEVICES']=''
    import fairseq,torch
    from fairseq import options,tasks,utils
    from fairseq.data import Dictionary
    if fairseq.__version__!='0.10.2':ap.error('Expected Fairseq0.10.2; report version before changing environment')
    prepared=a.prepared.resolve()
    print('Checking prepared hashes, vocabularies and length gates',flush=True)
    dm,tm,table=preflight(prepared)
    out=new_output(a.out).resolve();states=[];parameter_groups=defaultdict(list)
    gpu_info=None
    if a.gpu is not None and torch.cuda.is_available():
        props=torch.cuda.get_device_properties(0);gpu_info={'physical_id':a.gpu,'name':props.name,'total_memory':props.total_memory}
    for tag in TAGS:
        state={'tag':tag,'status':'BLOCKED'};states.append(state)
        folder=out/tag;folder.mkdir();data=folder/'bin'
        try:
            vocab=tm[tag]['vocab_size'];d=Dictionary.load(str(prepared/tag/'dict.shared.txt'))
            if len(d)!=vocab or d.symbols[:4]!=['<s>','<pad>','</s>','<unk>']:raise ValueError('Unexpected dictionary layout')
            cmd=[sys.executable,'-m','fairseq_cli.preprocess','--source-lang','source','--target-lang','target',
                '--trainpref',str(prepared/tag/'encoded/train'),'--validpref',str(prepared/tag/'encoded/valid'),
                '--joined-dictionary','--srcdict',str(prepared/tag/'dict.shared.txt'),
                '--destdir',str(data),'--dataset-impl','mmap','--workers',str(a.workers)]
            write_json(folder/'preprocess_command.json',cmd)
            print('Binarizing '+tag,flush=True)
            with (folder/'preprocess.log').open('w') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
            state['binary_checks']=check_binary(data,prepared/tag/'encoded',d,vocab,table,tag)
            args=options.parse_args_and_arch(options.get_training_parser(),architecture(data))
            utils.set_torch_seed(42)
            task=tasks.setup_task(args);model=task.build_model(args)
            total=sum(p.numel() for p in model.parameters());state['vocab_size']=vocab;state['parameters']=total
            if model.decoder.embed_tokens.weight is not model.decoder.output_projection.weight:raise ValueError('Decoder embeddings not tied')
            parameter_groups[vocab].append(total)
            write_json(folder/'architecture_args.json',vars(args))
            if a.gpu is not None:
                print('GPU smoke '+tag+' (3 batches only)',flush=True)
                state['smoke']=smoke(task,model,args)
                state['status']='BINARY_AND_GPU_SMOKE_PASSED'
            else:state['status']='BINARY_VERIFIED_GPU_NOT_TESTED'
            del model,task;gc.collect()
            if torch.cuda.is_available():torch.cuda.empty_cache()
            state['binary_sha256']={str(p.relative_to(out)):sha256(p) for p in data.iterdir() if p.suffix in ('.bin','.idx','.txt')}
        except Exception as exc:
            state['reason']=type(exc).__name__+': '+str(exc)
            # Stop after failure: do not repeat a GPU/environment problem on all six conditions.
            write_json(out/'status.json',states)
            print(tag+': BLOCKED — '+state['reason'],flush=True)
            break
        write_json(out/'status.json',states);print(tag+': '+state['status'],flush=True)
    equal=len(parameter_groups)==2 and all(len(v)==3 and len(set(v))==1 for v in parameter_groups.values())
    all_done=len(states)==6 and all(x['status']!='BLOCKED' for x in states)
    # Recheck all prepared artifact hashes after conversion; detects concurrent changes.
    try:preflight(prepared)
    except Exception as exc:all_done=False;write_json(out/'input_changed.json',{'error':str(exc)})
    write_json(out/'provenance.json',{'script_sha256':sha256(__file__),'common_sha256':sha256(Path(__file__).with_name('common.py')),
        'prepared':str(prepared),'data_manifest_sha256':sha256(prepared/'data_manifest.json'),
        'tokenizer_manifest_sha256':sha256(prepared/'tokenizer_manifest.json'),
        'fairseq':fairseq.__version__,'torch':torch.__version__,'gpu':gpu_info,'cpu_only':a.cpu_only,
        'max_positions':MAX_POS,'parameters_equal_within_vocab':equal,'all_six_completed':all_done,
        'scope':'No test or full training. AMP PyTorch3-batch smoke is not the Fairseq full trainer/memory-efficient-fp16 validation. No model checkpoints saved. Sparse binary content checks + full length totals, not a full content equality proof.'})
    md=['# Binarization and optional GPU smoke','','| Condition | Status | Parameters |','|---|---|---:|']
    for x in states:md.append('| '+x['tag']+' | '+x['status']+' | '+str(x.get('parameters',''))+' |')
    md+=['','All six completed: '+str(all_done), 'Parameter counts equal within each vocabulary budget: '+str(equal),
        'Shared max source/target positions:4096. No skip-invalid or truncation flags.',
        'GPU smoke uses a short batch and each side longest singleton. It does not prove every possible full-training batch fits GPU memory.',
        'No performance metric, full training or checkpoint selection. Do not reuse smoke weights; no checkpoints are saved.',
        'If blocked, inspect status.json and the condition preprocess.log; do not silently reduce length or drop rows.',
        'Send REPORT.md, status.json, provenance.json. If blocked, also send relevant preprocess.log.', '']
    (out/'REPORT.md').write_text('\n'.join(md),encoding='utf-8')
    print(out/'REPORT.md')
    return 0 if all_done and equal else 2

if __name__=='__main__':sys.exit(main())
