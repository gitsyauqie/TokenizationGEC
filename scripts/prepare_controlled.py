#!/usr/bin/env python3
"""Prepare a NEW synthetic-reconstruction pilot; no GPU/model training/test reads.
SentencePiece BPE/Unigram and HF WordPiece, common train-only fitting corpus.
"""
import argparse
from collections import Counter
from contextlib import ExitStack
import csv
import itertools
import json
import os
from pathlib import Path
import re
import shutil
import sys
os.environ.setdefault('TOKENIZERS_PARALLELISM','false')
from common import new_output, sha256, write_json
SPECIALS=['<s>','<pad>','</s>','<unk>']


def surface(s):
    return ' '.join(re.findall(r'[^\W_]+|[^\w\s]|_',s.lower()))


def failure_marker(s):
    return ' '.join(s.strip().strip('\"\'“”‘’').split()).casefold()=='error in api call'


def prepare_text(audit,out):
    raw=out/'surface';raw.mkdir()
    stats={};excluded=[];inputs={};max_bytes=0;max_word_chars=0
    for split in ('train','valid'):
        info=audit['splits'][split]
        if info.get('errors'):raise ValueError('Step01 errors: '+split)
        for k in ('source','target','category'):
            entry=info['files'][k]
            if sha256(entry['path'])!=entry['sha256']:raise ValueError('Hash mismatch: '+entry['path'])
            inputs[split+'/'+k]=entry
        count=Counter();retained=Counter();n=0;kept=0
        with ExitStack() as stack:
            fs=[stack.enter_context(open(info['files'][k]['path'],encoding='utf-8-sig')) for k in ('source','target','category')]
            outs=[stack.enter_context((raw/(split+'.'+k)).open('w',encoding='utf-8')) for k in ('source','target','category')]
            ids=stack.enter_context((raw/(split+'.ids.csv')).open('w',newline='',encoding='utf-8'))
            iw=csv.writer(ids);iw.writerow(['derived_id_zero_based','original_id_zero_based','original_category'])
            for idx,values in enumerate(itertools.zip_longest(*fs)):
                if any(x is None for x in values):raise ValueError('Unequal input lengths')
                src,tgt,cat=[x.rstrip('\r\n') for x in values]
                if not all(x.strip() for x in (src,tgt,cat)):raise ValueError('Blank raw field')
                n+=1;count[cat]+=1
                if failure_marker(src) or failure_marker(tgt):
                    excluded.append([split,idx,cat,'exact_observed_api_failure_marker']);continue
                ss,tt=surface(src),surface(tgt)
                if not ss or not tt:raise ValueError('Empty surface at %s %d'%(split,idx))
                iw.writerow([kept,idx,cat]);kept+=1;retained[cat]+=1
                for f,v in zip(outs,(ss,tt,cat)):f.write(v+'\n')
                if split=='train':
                    max_bytes=max(max_bytes,len(ss.encode()),len(tt.encode()))
                    max_word_chars=max(max_word_chars,max(len(w) for w in (ss+' '+tt).split()))
            if n!=info['n_pairs'] or dict(count)!=info['categories']:raise ValueError('Step01 count mismatch')
        stats[split]={'original_n':n,'retained_n':kept,'excluded_n':n-kept,'original_categories':dict(count),'retained_categories':dict(retained)}
    corpus=raw/'train.source_plus_target.txt'
    with corpus.open('w',encoding='utf-8') as dst:
        for k in ('source','target'):
            with (raw/('train.'+k)).open(encoding='utf-8') as src:
                for line in src:dst.write(line)
    with (out/'excluded_ids.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['split','original_id_zero_based','original_category','reason']);w.writerows(excluded)
    return stats,inputs,corpus,max_bytes,max_word_chars


def training_alphabet(corpus):
    counts=Counter()
    with Path(corpus).open(encoding='utf-8') as f:
        for line in f:counts.update(line.rstrip('\r\n'))
    return ''.join(sorted(c for c in counts if not c.isspace())),counts


def train_tokenizer(family,size,corpus,folder,max_bytes,max_word_chars):
    if family in ('spbpe','spuni'):
        import sentencepiece as spm
        prefix=folder/'tokenizer'
        required,counts=training_alphabet(corpus)
        write_json(folder/'required_character_inventory.json',{
            'source':'retained training source + target only; no validation/test',
            'corpus_sha256':sha256(corpus),
            'characters':[{'character':c,'codepoint':'U+%04X'%ord(c),'count':counts[c]} for c in required]})
        params=dict(input=str(corpus),model_prefix=str(prefix),model_type='bpe' if family=='spbpe' else 'unigram',
                    vocab_size=size,character_coverage=1.0,required_chars=required,normalization_rule_name='identity',
                    remove_extra_whitespaces=False,add_dummy_prefix=True,input_sentence_size=0,
                    shuffle_input_sentence=False,num_threads=1,max_sentence_length=max(4192,max_bytes+1),
                    split_by_whitespace=True,split_by_unicode_script=False,split_by_number=False,
                    split_digits=False,byte_fallback=False,hard_vocab_limit=True,bos_id=0,pad_id=1,eos_id=2,unk_id=3)
        write_json(folder/'trainer_config.json',params)
        spm.SentencePieceTrainer.train(**params)
        tokenizer=spm.SentencePieceProcessor(model_file=str(prefix)+'.model')
        pieces=[tokenizer.id_to_piece(i) for i in range(tokenizer.get_piece_size())]
        missing=[c for c in required if tokenizer.piece_to_id(c)==tokenizer.unk_id()]
        if missing:raise ValueError('Required training characters absent: '+repr(missing))
        def encode(text):
            ids=tokenizer.encode(text,out_type=int)
            return [pieces[i] for i in ids],tokenizer.decode(ids),3 in ids
        artifact=Path(str(prefix)+'.model')
    else:
        from tokenizers import Tokenizer,models,trainers,pre_tokenizers,decoders
        config={'vocab_size':size,'min_frequency':1,'normalizer':None,'pre_tokenizer':'WhitespaceSplit',
                'decoder':'WordPiece(cleanup=False)','special_tokens':SPECIALS,'continuing_subword_prefix':'##',
                'max_input_chars_per_word':max(100000,max_word_chars)}
        write_json(folder/'trainer_config.json',config)
        tokenizer=Tokenizer(models.WordPiece(unk_token='<unk>',max_input_chars_per_word=config['max_input_chars_per_word']))
        tokenizer.pre_tokenizer=pre_tokenizers.WhitespaceSplit()
        tokenizer.decoder=decoders.WordPiece(prefix='##',cleanup=False)
        tokenizer.train([str(corpus)],trainers.WordPieceTrainer(vocab_size=size,min_frequency=1,
                        special_tokens=SPECIALS,continuing_subword_prefix='##',show_progress=True))
        artifact=folder/'tokenizer.json';tokenizer.save(str(artifact))
        pieces=[tokenizer.id_to_token(i) for i in range(tokenizer.get_vocab_size())]
        def encode(text):
            enc=tokenizer.encode(text,add_special_tokens=False)
            return enc.tokens,tokenizer.decode(enc.ids,skip_special_tokens=False),3 in enc.ids
    if len(pieces)!=size or pieces[:4]!=SPECIALS:raise ValueError('Requested vocabulary size/special IDs not achieved')
    if len(set(pieces))!=len(pieces) or any(not x or any(c.isspace() for c in x) for x in pieces):raise ValueError('Invalid Fairseq vocabulary symbols')
    # Full vocabulary, not observed-token subset. Fairseq injects the first four specials.
    with (folder/'dict.shared.txt').open('w',encoding='utf-8') as f:
        for token in pieces[4:]:f.write(token+' 1\n')
    return encode,pieces,artifact


def encode_split(encode,raw,dest,split,side):
    stats=Counter();examples=[]
    with (raw/(split+'.'+side)).open(encoding='utf-8') as src,(dest/(split+'.'+side)).open('w',encoding='utf-8') as dst:
        for idx,line in enumerate(src):
            text=line.rstrip('\r\n');tokens,decoded,unknown=encode(text)
            if not tokens:raise ValueError('Empty encoding')
            dst.write(' '.join(tokens)+'\n');stats['n']+=1;stats['tokens']+=len(tokens)
            stats['max_tokens_with_eos']=max(stats['max_tokens_with_eos'],len(tokens)+1)
            stats['over_1024_with_eos']+=len(tokens)+1>1024
            stats['over_2048_with_eos']+=len(tokens)+1>2048
            stats['unknown_rows']+=bool(unknown)
            # Check exact common surface, not forgiving normalized output.
            if decoded!=text:
                key='roundtrip_mismatch_with_unknown' if unknown else 'roundtrip_mismatch_without_unknown'
                stats[key]+=1
                if len(examples)<5:examples.append({'derived_id_zero_based':idx,'kind':key,'source_surface':text,'decoded':decoded})
    return dict(stats),examples


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--audit',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--reuse-from',type=Path,help='Verified previous preparation; reuse surface and WordPiece artifacts only.')
    args=ap.parse_args()
    if args.out.exists():ap.error('Output exists. Preserve it and select a new run directory.')
    import sentencepiece,tokenizers
    versions={'sentencepiece':sentencepiece.__version__,'tokenizers':tokenizers.__version__}
    if versions!={'sentencepiece':'0.2.0','tokenizers':'0.20.3'}:ap.error('Expected server versions 0.2.0 / 0.20.3; report versions instead of upgrading environment: '+str(versions))
    audit=json.loads(args.audit.read_text(encoding='utf-8'))
    # Check all inputs before writing a new directory. Test files are not opened.
    for split in ('train','valid'):
        for v in audit['splits'][split]['files'].values():
            if sha256(v['path'])!=v['sha256']:raise ValueError('Raw input hash changed')
    reuse=None
    if args.reuse_from:
        reuse=args.reuse_from.resolve()
        dm=json.loads((reuse/'data_manifest.json').read_text())
        prior=json.loads((reuse/'provenance.json').read_text())
        tm=json.loads((reuse/'tokenizer_manifest.json').read_text())
        previous_status={x['tag']:x for x in json.loads((reuse/'status.json').read_text())}
        if prior['audit_sha256']!=sha256(args.audit) or prior['common_sha256']!=sha256(Path(__file__).with_name('common.py')):
            raise ValueError('Reuse audit/common provenance differs')
        if prior['versions']!=versions or dm['case']!='lower' or dm['surface_rule']!=r'[^\W_]+|[^\w\s]|_':
            raise ValueError('Reuse preprocessing/version mismatch')
        for split in ('train','valid'):
            for key in ('source','target','category'):
                if dm['raw_inputs'][split+'/'+key]['sha256']!=audit['splits'][split]['files'][key]['sha256']:
                    raise ValueError('Reuse raw provenance mismatch')
        for rel,digest in dm['surface_files'].items():
            if sha256(reuse/rel)!=digest:raise ValueError('Reusable surface changed: '+rel)
        if sha256(reuse/'surface/train.source_plus_target.txt')!=dm['corpus_sha256']:
            raise ValueError('Reusable fitting corpus changed')
        for tag in ('wp_5k','wp_20k'):
            if previous_status[tag]['status']!='PREPARED_PENDING_LENGTH_AND_UNK_REVIEW':raise ValueError('WordPiece not previously prepared')
            for rel,digest in tm[tag]['files'].items():
                if sha256(reuse/rel)!=digest:raise ValueError('Reusable WordPiece changed: '+rel)
    out=new_output(args.out)
    if reuse:
        print('Reusing verified common surface and WordPiece files',flush=True)
        shutil.copytree(reuse/'surface',out/'surface')
        for rel,digest in dm['surface_files'].items():
            if sha256(out/rel)!=digest:raise ValueError('Surface copy mismatch: '+rel)
        shutil.copy2(reuse/'excluded_ids.csv',out/'excluded_ids.csv')
        stats,inputs=dm['splits'],dm['raw_inputs']
        corpus=out/'surface/train.source_plus_target.txt'
        max_bytes=0;max_word_chars=0
        with corpus.open(encoding='utf-8') as f:
            for line in f:
                text=line.rstrip('\r\n')
                max_bytes=max(max_bytes,len(text.encode()))
                max_word_chars=max(max_word_chars,max(map(len,text.split())))
    else:
        print('Preparing shared train/valid surface corpus',flush=True)
        stats,inputs,corpus,max_bytes,max_word_chars=prepare_text(audit,out)
    write_json(out/'data_manifest.json',{'splits':stats,'raw_inputs':inputs,'surface_rule':r'[^\W_]+|[^\w\s]|_',
        'case':'lower','unicode':'no NFKC or accent removal','exclusion':'exact observed API-failure marker only, new derived copy',
        'test':'not read or encoded','corpus_sha256':sha256(corpus),
        'surface_files':{str(p.relative_to(out)):sha256(p) for p in sorted((out/'surface').iterdir())}})
    statuses=[];lengths=[];models={}
    for family,size in itertools.product(('spbpe','wp','spuni'),(5000,20000)):
        tag=family+'_'+str(size//1000)+'k';folder=out/tag
        if reuse and family=='wp':
            shutil.copytree(reuse/tag,folder)
            for rel,digest in tm[tag]['files'].items():
                if sha256(out/rel)!=digest:raise ValueError('WordPiece copy mismatch')
            models[tag]=tm[tag]
            with (reuse/'lengths_and_roundtrip.csv').open() as f:
                for row in csv.DictReader(f):
                    if row['tag']==tag:lengths.append({k:(v if k in ('tag','split','side') else int(v)) for k,v in row.items()})
            statuses.append(dict(tag=tag,status='PREPARED_PENDING_LENGTH_AND_UNK_REVIEW',vocab_size=size,reused_from=str(reuse/tag)))
            write_json(out/'status.json',statuses)
            print(tag+': reused unchanged',flush=True)
            continue
        folder.mkdir()
        state={'tag':tag,'status':'BLOCKED'};statuses.append(state)
        print('Training tokenizer '+tag+' (CPU; not model training)',flush=True)
        try:
            encode,pieces,artifact=train_tokenizer(family,size,corpus,folder,max_bytes,max_word_chars)
            encoded=folder/'encoded';encoded.mkdir();examples={};blocking=[]
            for split,side in itertools.product(('train','valid'),('source','target')):
                info,ex=encode_split(encode,out/'surface',encoded,split,side)
                if info['n']!=stats[split]['retained_n']:raise ValueError('Encoded row count differs')
                lengths.append(dict(tag=tag,split=split,side=side,**{k:info.get(k,0) for k in
                    ('n','tokens','max_tokens_with_eos','over_1024_with_eos','over_2048_with_eos','unknown_rows','roundtrip_mismatch_with_unknown','roundtrip_mismatch_without_unknown')}))
                examples[split+'.'+side]=ex
                if info.get('roundtrip_mismatch_without_unknown',0):blocking.append(split+'.'+side+': unexplained roundtrip mismatch')
                if split=='train' and info.get('unknown_rows',0):blocking.append('Training text contains unknown tokens')
            write_json(folder/'roundtrip_examples.json',examples)
            models[tag]={'family':family,'vocab_size':len(pieces),'special_ids':dict(zip(SPECIALS,range(4))),
                'files':{str(p.relative_to(out)):sha256(p) for p in sorted(folder.rglob('*')) if p.is_file()}}
            if blocking:raise ValueError('; '.join(blocking))
            state.update(status='PREPARED_PENDING_LENGTH_AND_UNK_REVIEW',vocab_size=len(pieces))
        except Exception as exc:state['reason']=type(exc).__name__+': '+str(exc)
        write_json(out/'status.json',statuses)
        print(tag+': '+state['status'],flush=True)
    for item in inputs.values():
        if sha256(item['path'])!=item['sha256']:raise ValueError('Raw inputs changed during preparation')
    if lengths:
        with (out/'lengths_and_roundtrip.csv').open('w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,fieldnames=list(lengths[0]));writer.writeheader();writer.writerows(lengths)
    write_json(out/'tokenizer_manifest.json',models)
    write_json(out/'provenance.json',{'script_sha256':sha256(__file__),'common_sha256':sha256(Path(__file__).with_name('common.py')),
        'audit_sha256':sha256(args.audit),'versions':versions,'python':sys.version,'models':list(models),
        'reused_from':str(reuse) if reuse else None,
        'repair':'SentencePiece required_chars explicitly covers retained train alphabet; validation/test characters are not added.',
        'scope':'New pilot preparation only. Full retained train source then train target for tokenizer fitting; no valid/test fitting.',
        'implementation_change':'SentencePiece BPE replaces historical subword-nmt merge-budget BPE; do not merge result tables as identical conditions.',
        'limits':'Historical split/group overlap and reference quality retained; derived data is not a clean GEC benchmark. Fixed tokenizer artifacts reused across later training seeds; deterministic retraining across platforms not guaranteed.'})
    md=['# Controlled pilot preparation — no model training','',
        'New derived train/valid files; original inputs untouched. Test data not read.','',
        '| Split | Original n | Retained n | Exact API-marker exclusions |','|---|---:|---:|---:|']
    for split,x in stats.items():md.append('| %s | %d | %d | %d |'%(split,x['original_n'],x['retained_n'],x['excluded_n']))
    md+=['','| Tokenizer | Status |','|---|---|']
    for x in statuses:md.append('| '+x['tag']+' | '+x['status']+': '+x.get('reason','')+' |')
    md+=['','Do not launch training yet. Review maximum lengths, unknown rows and unexpected roundtrip mismatches first.',
         'Full shared dictionaries contain requested vocabulary including 4 Fairseq specials, but Fairseq loading/model parameter counts must still be verified.',
         'No automatic sentence dropping, truncation or replacement from references. Validation unknowns remain documented.',
         'Send REPORT.md, status.json, data_manifest.json, tokenizer_manifest.json, lengths_and_roundtrip.csv, excluded_ids.csv and provenance.json.',
         'If a tokenizer is blocked, also send its roundtrip_examples.json if present. No need to download full encoded corpus.','']
    (out/'REPORT.md').write_text('\n'.join(md),encoding='utf-8')
    print(out/'REPORT.md')

if __name__=='__main__':main()
