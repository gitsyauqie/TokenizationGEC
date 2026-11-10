#!/usr/bin/env python3
"""M7: Turkish replication (GECTurk) of the controlled tokenizer study.

Same tokenizer trainers, vocabulary budgets, Transformer, optimisation, decoding and metrics as the
Indonesian experiment (functions are imported from prepare_controlled.py, train_controlled.py and
build_and_smoke.py), with two pre-declared differences: case is PRESERVED (Turkish dotted/dotless i
makes Python lowercasing unsafe) and every run trains 20 epochs with full-validation chrF2 after each
epoch; the earliest best-validation epoch is selected. Test is touched only by `test`, once per run.

Stages (run from paper6_revision_20261007; each stage refuses to overwrite and can be re-run to resume):
  prepare   surface text, 6 tokenizers fitted on train source+target, encoded train/valid/test, categories
  binarize  fairseq-preprocess with the full shared dictionary; exact parameter counts per condition
  train     one condition x seed: 20 epochs, validation each epoch, best checkpoint kept (OOM-safe)
  test      generate the frozen best checkpoint on the full test set; writes the Indonesian-style layout
            (<out>/controlled_test_v1/...) so paired_stats.py / gec_metrics.py / tokenization_stats.py run unchanged
"""
import argparse
import csv
import fcntl
import itertools
import json
import os
from collections import Counter
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import sha256, write_json, parse_gen  # noqa: E402

TAGS = ['spbpe_5k', 'spbpe_20k', 'wp_5k', 'wp_20k', 'spuni_5k', 'spuni_20k']
BUDGETS = {'5k': 5000, '20k': 20000}
SEEDS = (42, 43, 44)
CASE = 'preserve'
EPOCHS = 20
SPLITS = {'train': 'train', 'valid': 'dev', 'test': 'test'}


def atomic_json(path, value):
    tmp = Path(str(path) + '.tmp'); write_json(tmp, value); os.replace(tmp, path)


def read_raw(path):
    # newline='' : only '\n' ends a record, so a stray '\r' or U+2028 inside a sentence cannot shift alignment
    with open(path, encoding='utf-8-sig', newline='') as f:
        return [x[:-1] if x.endswith('\n') else x for x in f]


def read_surface(path):
    rows = Path(path).read_text(encoding='utf-8').split('\n')
    if rows[-1] != '':
        raise ValueError('Missing final newline: %s' % path)
    return rows[:-1]


def parse_m2(path):
    """Return list of (sentence, [rule labels]) in file order."""
    out, sent, rules = [], None, []
    for line in read_raw(path) + ['']:
        if line.startswith('S '):
            sent, rules = line[2:], []
        elif line.startswith('A '):
            parts = line[2:].split('|||')
            if len(parts) > 1 and parts[1] not in ('noop', 'UNK', 'Um'):
                rules.append(parts[1])
        elif line.strip() == '' and sent is not None:
            out.append((sent, rules)); sent = None
    return out


def category_of(rules):
    distinct = sorted(set(rules))
    if not distinct:
        return 'none'
    return distinct[0] if len(distinct) == 1 else 'multi'


# ------------------------------------------------------------------ prepare
def cmd_prepare(a):
    from prepare_controlled import train_tokenizer, encode_split, SPECIALS  # identical trainer configs
    from eval_reconstruction import surface
    import sentencepiece, tokenizers
    versions = {'sentencepiece': sentencepiece.__version__, 'tokenizers': tokenizers.__version__}
    if versions != {'sentencepiece': '0.2.0', 'tokenizers': '0.20.3'} and not a.allow_versions:
        raise ValueError('Unexpected tokenizer library versions: %s' % versions)
    data = a.data.resolve(); out = (a.out / 'prepared').resolve()
    if out.exists():
        raise ValueError('prepared/ exists; preserve it or choose a new --out')
    raw_files = {}
    for split, stem in SPLITS.items():
        for side, ext in (('source', 'src'), ('target', 'tgt')):
            p = data / 'raw' / ('%s.%s' % (stem, ext)); raw_files['%s/%s' % (split, side)] = {'path': str(p), 'sha256': sha256(p)}
    global CASE
    CASE = a.case
    if a.categories == 'm2':
        m2 = {'valid': data / 'gec_tr' / 'gec_tr_source_annot_val.txt', 'test': data / 'raw' / 'test.m2',
              'train': data / 'gec_tr' / 'gec_tr_source_annot_train.txt'}
    else:   # one label per line in raw/<stem>.cat (used for the IGED data-size control)
        m2 = {split: data / 'raw' / ('%s.cat' % stem) for split, stem in SPLITS.items()}
    for k, p in m2.items():
        raw_files['%s/%s' % (k, a.categories)] = {'path': str(p), 'sha256': sha256(p)}
    (out / 'surface').mkdir(parents=True)
    stats, excluded = {}, []
    for split, stem in SPLITS.items():
        src = read_raw(data / 'raw' / ('%s.src' % stem)); tgt = read_raw(data / 'raw' / ('%s.tgt' % stem))
        if len(src) != len(tgt):
            raise ValueError('%s: source/target line counts differ (%d/%d)' % (split, len(src), len(tgt)))
        if a.categories == 'm2':
            ann = parse_m2(m2[split])
        else:
            ann = [(x, None) for x in src]; labels = read_raw(m2[split])
        aligned = len(ann) == len(src) if a.categories == 'm2' else len(labels) == len(src)
        mism = sum(' '.join(s.split()) != ' '.join(x[0].split()) for s, x in zip(src, ann)) if aligned else None
        if split != 'train' and (not aligned or mism > 0.01 * len(src)):
            raise ValueError('%s: M2 does not align with raw source (M2 %d sentences, raw %d, mismatched %s)'
                             % (split, len(ann), len(src), mism))
        if a.categories == 'files':
            if not aligned or any(not x.strip() for x in labels):
                raise ValueError('%s: category file does not match the raw source' % split)
            cats = labels
        else:
            cats = [category_of(r) for _, r in ann] if aligned else ['unlabelled'] * len(src)
        rows = []
        for i, (x, y, c) in enumerate(zip(src, tgt, cats)):
            sx, sy = surface(x, CASE), surface(y, CASE)
            if not sx or not sy:
                excluded.append([split, i, c, 'empty after surface tokenization']); continue
            rows.append((i, sx, sy, c))
        for k, side in enumerate(('original_id', 'source', 'target', 'category')):
            (out / 'surface' / ('%s.%s' % (split, side))).write_text('\n'.join(str(r[k]) for r in rows) + '\n', encoding='utf-8')
        stats[split] = {'original_n': len(src), 'retained_n': len(rows), 'excluded_n': len(src) - len(rows),
                        'm2_sentences': len(ann), 'm2_aligned': aligned, 'm2_text_mismatches': mism,
                        'categories': dict(Counter(r[3] for r in rows)), 'identical_pairs': sum(r[1] == r[2] for r in rows)}
        print('%s: %d pairs kept of %d; %d categories; M2 mismatches %s' % (split, len(rows), len(src), len(stats[split]['categories']), mism), flush=True)
    with open(out / 'excluded_ids.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['split', 'original_id_zero_based', 'category', 'reason']); w.writerows(excluded)
    corpus = out / 'surface' / 'train.source_plus_target.txt'
    with corpus.open('w', encoding='utf-8') as dst:
        for side in ('source', 'target'):
            dst.write((out / 'surface' / ('train.%s' % side)).read_text(encoding='utf-8'))
    text = corpus.read_text(encoding='utf-8').split('\n')
    max_bytes = max(len(x.encode()) for x in text); max_word = max((len(w) for x in text for w in x.split()), default=1)
    models, lengths = {}, []
    for tag in TAGS:
        family, size = tag.split('_')[0], BUDGETS[tag.split('_')[1]]; folder = out / tag; folder.mkdir()
        print('Tokenizer ' + tag, flush=True)
        encode, pieces, _ = train_tokenizer(family, size, corpus, folder, max_bytes, max_word)
        enc = folder / 'encoded'; enc.mkdir()
        for split, side in itertools.product(SPLITS, ('source', 'target')):
            info, ex = encode_split(encode, out / 'surface', enc, split, side)
            lengths.append(dict(tag=tag, split=split, side=side, **{k: info.get(k, 0) for k in (
                'n', 'tokens', 'max_tokens_with_eos', 'unknown_rows', 'roundtrip_mismatch_with_unknown', 'roundtrip_mismatch_without_unknown')}))
            if info.get('roundtrip_mismatch_without_unknown', 0):
                raise ValueError('%s %s.%s: roundtrip mismatch without unknown: %s' % (tag, split, side, ex[:2]))
            if info.get('max_tokens_with_eos', 0) > 4096:
                raise ValueError('%s %s.%s exceeds the 4096-position limit; rows are never truncated' % (tag, split, side))
            if split == 'train' and info.get('unknown_rows', 0):
                raise ValueError('%s: unknown tokens in training text' % tag)
        models[tag] = {'family': family, 'vocab_size': len(pieces), 'special_ids': dict(zip(SPECIALS, range(4))),
                       'files': {str(p.relative_to(out)): sha256(p) for p in sorted(folder.rglob('*')) if p.is_file()}}
    write_json(out / 'tokenizer_manifest.json', models)
    write_json(out / 'data_manifest.json', {'raw_inputs': raw_files, 'splits': stats, 'case': CASE,
        'surface_rule': r'[^\W_]+|[^\w\s]|_', 'category': ('single GECTurk rule label per sentence; "multi" if several distinct rules; "none" if no edit'
                     if a.categories == 'm2' else 'label from raw/<split>.cat'),
        'corpus_sha256': sha256(corpus), 'versions': versions,
        'surface_files': {str(p.relative_to(out)): sha256(p) for p in sorted((out / 'surface').iterdir())}})
    with open(out / 'lengths_and_roundtrip.json', 'w') as f:
        json.dump(lengths, f, indent=1)
    write_json(out / 'provenance.json', {'script_sha256': sha256(__file__), 'prepare_controlled_sha256': sha256(HERE / 'prepare_controlled.py'),
                                         'eval_reconstruction_sha256': sha256(HERE / 'eval_reconstruction.py')})
    print('PREPARE DONE', flush=True)


# ------------------------------------------------------------------ binarize
def cmd_binarize(a):
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    out = a.out.resolve(); prepared = out / 'prepared'; binary = out / 'binary'
    tm = json.loads((prepared / 'tokenizer_manifest.json').read_text())
    for tag, m in tm.items():
        for rel, d in m['files'].items():
            if sha256(prepared / rel) != d:
                raise ValueError('Prepared artifact changed: ' + rel)
    binary.mkdir(exist_ok=True)
    counts = {}
    for tag in TAGS:
        dest = binary / tag / 'bin'
        if (binary / tag / 'status.json').exists():
            counts[tag] = json.loads((binary / tag / 'status.json').read_text()); continue
        if dest.exists():
            shutil.rmtree(dest)
        dest.mkdir(parents=True)
        enc = prepared / tag / 'encoded'
        cmd = [sys.executable, '-m', 'fairseq_cli.preprocess', '--source-lang', 'source', '--target-lang', 'target',
               '--trainpref', str(enc / 'train'), '--validpref', str(enc / 'valid'), '--testpref', str(enc / 'test'),
               '--joined-dictionary', '--srcdict', str(prepared / tag / 'dict.shared.txt'),
               '--destdir', str(dest), '--dataset-impl', 'mmap', '--workers', str(a.workers)]
        with open(binary / tag / 'preprocess.log', 'w') as log:
            subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=True)
        check_preprocess(binary / tag / 'preprocess.log', dest, prepared / tag / 'dict.shared.txt', tm[tag]['vocab_size'])
        n_params = count_parameters(dest) if not a.skip_param_count else None
        st = {'tag': tag, 'parameters': n_params, 'sha256': {p.name: sha256(p) for p in sorted(dest.iterdir()) if p.is_file()}}
        atomic_json(binary / tag / 'status.json', st); counts[tag] = st
        print('%s binarized; parameters=%s' % (tag, n_params), flush=True)
    for budget in ('5k', '20k'):
        p = {counts[t]['parameters'] for t in TAGS if t.endswith('_' + budget)}
        if None not in p and len(p) != 1:
            raise ValueError('Parameter counts differ within %s: %s' % (budget, p))
    print('BINARIZE DONE', flush=True)


def check_preprocess(log, dest, shared, vocab):
    import re
    if (dest / 'dict.source.txt').read_bytes() != shared.read_bytes() or (dest / 'dict.target.txt').read_bytes() != shared.read_bytes():
        raise ValueError('Fairseq dictionary differs from the tokenizer vocabulary: ' + str(dest))
    if len(shared.read_text(encoding='utf-8').splitlines()) + 4 != vocab:
        raise ValueError('Dictionary size mismatch: ' + str(shared))
    found = 0
    for line in log.read_text(encoding='utf-8', errors='replace').splitlines():
        m = re.search(r'\[(source|target)\] \S*/(train|valid|test)\.(?:source|target): (\d+) sents, (\d+) tokens, ([\d.e+-]+)% replaced', line)
        if m:
            found += 1
            if m.group(2) == 'train' and float(m.group(5)) != 0.0:
                raise ValueError('Unknown tokens in binarized training data: ' + line)
    if found != 6:
        raise ValueError('Expected 6 binarization summaries in %s, found %d' % (log, found))


def count_parameters(data):
    from fairseq import options, tasks
    from build_and_smoke import architecture
    args = options.parse_args_and_arch(options.get_training_parser(), architecture(data) + ['--cpu'])
    task = tasks.setup_task(args)
    model = task.build_model(args)
    if model.decoder.embed_tokens.weight is not model.decoder.output_projection.weight:
        raise ValueError('Decoder embeddings not tied')
    return int(sum(p.numel() for p in model.parameters()))


def load_case(out):
    global CASE
    CASE = json.loads((out / 'prepared' / 'data_manifest.json').read_text())['case']
    return CASE


def check_versions():
    import fairseq, sacrebleu, sentencepiece, tokenizers
    v = {'fairseq': fairseq.__version__, 'sacrebleu': sacrebleu.__version__,
         'tokenizers': tokenizers.__version__, 'sentencepiece': sentencepiece.__version__}
    if v != {'fairseq': '0.10.2', 'sacrebleu': '1.5.1', 'tokenizers': '0.20.3', 'sentencepiece': '0.2.0'}:
        raise ValueError('Unexpected package versions: %s' % v)
    from eval_reconstruction import self_check
    self_check(sacrebleu)
    return v


# ------------------------------------------------------------------ train
def evaluate_case(gen, ref, cats, decode, sb):
    from eval_reconstruction import surface, metric_scores
    streams = parse_gen(gen, len(ref))
    hyp = [surface(decode(streams['H'][i].split()), CASE) for i in range(len(ref))]
    score = metric_scores(hyp, ref, sb); subs = []
    for c in sorted(set(cats)):
        ids = [i for i, x in enumerate(cats) if x == c]
        subs.append(dict(category=c, **metric_scores([hyp[i] for i in ids], [ref[i] for i in ids], sb)))
    return score, subs, hyp


def cmd_train(a):
    os.environ['CUDA_VISIBLE_DEVICES'] = a.gpu
    os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
    import sacrebleu
    check_versions()
    from train_controlled import train_args, generation_args, decoder_for, next_log, run_child
    from extend_controlled import oom_retry, copy_verified, checkpoint_state
    out = a.out.resolve(); prepared = out / 'prepared'; data = out / 'binary' / a.tag / 'bin'; load_case(out)
    st = json.loads((out / 'binary' / a.tag / 'status.json').read_text())
    for name, d in st['sha256'].items():
        if sha256(data / name) != d:
            raise ValueError('Binary changed: ' + name)
    folder = out / 'training' / ('%s_seed%d' % (a.tag, a.seed)); resume = folder / 'resume'; logs = folder / 'logs'
    for p in (folder, resume, logs):
        p.mkdir(parents=True, exist_ok=True)
    config = {'tag': a.tag, 'seed': a.seed, 'epochs': EPOCHS, 'case': CASE, 'selection': 'full validation chrF2; strict improvement; earliest epoch wins ties',
              'train_controlled_sha256': sha256(HERE / 'train_controlled.py'), 'binary_status_sha256': sha256(out / 'binary' / a.tag / 'status.json')}
    with (folder / 'RUN.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        cpath = folder / 'config.json'
        if cpath.exists() and json.loads(cpath.read_text()) != config:
            raise ValueError('Configuration changed; refusing unsafe resume')
        atomic_json(cpath, config)
        ref = [x for x in (prepared / 'surface' / 'valid.target').read_text(encoding='utf-8').split('\n')[:-1]]
        cats = (prepared / 'surface' / 'valid.category').read_text(encoding='utf-8').split('\n')[:-1]
        decode = decoder_for(a.tag, prepared)
        statepath = folder / 'state.json'; last = resume / 'checkpoint_last.pt'
        state = json.loads(statepath.read_text()) if statepath.exists() else {'tag': a.tag, 'seed': a.seed, 'trained_epoch': 0, 'history': [], 'best': None}
        if state.get('status') == 'COMPLETE':
            print('Already complete', flush=True); return
        for epoch in range(len(state['history']) + 1, EPOCHS + 1):
            start = time.monotonic()
            if state['trained_epoch'] < epoch:
                if epoch > 1 and not last.exists():
                    raise ValueError('Resume checkpoint missing; refusing restart from scratch')
                cmd = [sys.executable, str(HERE / 'train_controlled.py'), '--fairseq-train'] + train_args(data, resume, epoch, a.seed)

                def train_once(holder, epoch=epoch, cmd=cmd):
                    lg = next_log(logs, 'train_epoch%02d' % epoch, '.log'); holder.append(lg)
                    atomic_json(logs / (lg.stem + '.command.json'), cmd)
                    print('%s seed%d epoch %d/%d training' % (a.tag, a.seed, epoch, EPOCHS), flush=True)
                    run_child(cmd, lg, lock.fileno())
                oom_retry(a, '%s epoch %d training' % (a.tag, epoch), train_once)
                info = checkpoint_state(last)
                if info['next_epoch'] != epoch + 1:
                    raise ValueError('Unexpected iterator state after epoch %d: %s' % (epoch, info))
                state['trained_epoch'] = epoch; state['pending_checkpoint_sha256'] = sha256(last)
                state['pending_train_seconds'] = time.monotonic() - start
                atomic_json(statepath, state)
            if sha256(last) != state['pending_checkpoint_sha256']:
                raise ValueError('Pending validation checkpoint changed')
            vstart = time.monotonic(); cmd = generation_args(data, last)

            def valid_once(holder, epoch=epoch, cmd=cmd):
                g = next_log(logs, 'valid_epoch%02d' % epoch, '.out'); holder.append(g.with_suffix('.stderr.log'))
                print('%s seed%d epoch %d validation' % (a.tag, a.seed, epoch), flush=True)
                run_child(cmd, g, lock.fileno(), g.with_suffix('.stderr.log'))
                return g
            gen = oom_retry(a, '%s epoch %d validation' % (a.tag, epoch), valid_once)
            score, subs, _ = evaluate_case(gen, ref, cats, decode, sacrebleu)
            rec = {'epoch': epoch, **score, 'category_scores': subs, 'checkpoint_sha256': sha256(last),
                   'train_seconds': state.get('pending_train_seconds'), 'validation_seconds': time.monotonic() - vstart}
            if state['best'] is None or score['chrf2_pct'] > state['best']['chrf2_pct']:
                copy_verified(last, folder / 'checkpoint_best.pt', state['pending_checkpoint_sha256'])
                state['best'] = {'epoch': epoch, **score, 'checkpoint_sha256': state['pending_checkpoint_sha256']}
            state['history'].append(rec); atomic_json(statepath, state); gen.unlink()
            print('%s seed%d epoch %d: valid chrF2=%.4f EM=%.4f (best epoch %d)' % (a.tag, a.seed, epoch, score['chrf2_pct'],
                  score['exact_match_pct'], state['best']['epoch']), flush=True)
        if sha256(folder / 'checkpoint_best.pt') != state['best']['checkpoint_sha256']:
            raise ValueError('Best checkpoint integrity failure')
        for p in resume.glob('*.pt'):
            p.unlink()
        state['status'] = 'COMPLETE'; atomic_json(statepath, state)
        print('TRAIN DONE %s seed%d best epoch %d' % (a.tag, a.seed, state['best']['epoch']), flush=True)


# ------------------------------------------------------------------ test
def cmd_test(a):
    os.environ['CUDA_VISIBLE_DEVICES'] = a.gpu
    import sacrebleu
    check_versions()
    from train_controlled import generation_args, decoder_for
    from extend_controlled import oom_retry
    from eval_reconstruction import metric_scores
    out = a.out.resolve(); prepared = out / 'prepared'; load_case(out)
    tdir = out / 'controlled_test_v1'; tdir.mkdir(exist_ok=True)
    src = (prepared / 'surface' / 'test.source').read_text(encoding='utf-8').split('\n')[:-1]
    ref = (prepared / 'surface' / 'test.target').read_text(encoding='utf-8').split('\n')[:-1]
    cats = (prepared / 'surface' / 'test.category').read_text(encoding='utf-8').split('\n')[:-1]
    for side, rows in (('source', src), ('target', ref), ('category', cats)):
        p = tdir / ('test.%s' % side)
        if not p.exists():
            p.write_text('\n'.join(rows) + '\n', encoding='utf-8')
    def score_all(h):
        r = {'overall': metric_scores(h, ref, sacrebleu), 'categories': []}
        for c in sorted(set(cats)):
            ids = [i for i, x in enumerate(cats) if x == c]
            r['categories'].append(dict(category=c, **metric_scores([h[i] for i in ids], [ref[i] for i in ids], sacrebleu)))
        return r
    if not (tdir / 'baselines.json').exists():
        atomic_json(tdir / 'baselines.json', {'COPY_INPUT': score_all(src), 'REFERENCE_ORACLE_SANITY': score_all(ref)})
    runs = [(t, s) for t in TAGS for s in SEEDS] if a.all else [(a.tag, a.seed)]
    for tag, seed in runs:
        name = '%s_seed%d' % (tag, seed); folder = tdir / name; folder.mkdir(exist_ok=True)
        tr = out / 'training' / name
        state = json.loads((tr / 'state.json').read_text())
        if state.get('status') != 'COMPLETE':
            print('SKIP %s: training not complete' % name, flush=True); continue
        best = tr / 'checkpoint_best.pt'
        if sha256(best) != state['best']['checkpoint_sha256']:
            raise ValueError('Best checkpoint hash mismatch: ' + name)
        if (folder / 'scores.json').exists():
            continue
        data = out / 'binary' / tag / 'bin'; gen = folder / 'generation.out'
        cmd = generation_args(data, best); cmd[cmd.index('--gen-subset') + 1] = 'test'
        atomic_json(folder / 'command.json', cmd); start = time.monotonic()

        def test_once(holder, cmd=cmd, gen=gen, folder=folder):
            holder.append(folder / 'generation.stderr.log')
            print('%s test generation' % name, flush=True)
            with gen.open('w') as f, (folder / 'generation.stderr.log').open('w') as err:
                subprocess.run(cmd, stdout=f, stderr=err, check=True)
        oom_retry(a, name + ' test', test_once)
        decode = decoder_for(tag, prepared)
        from eval_reconstruction import surface
        streams = parse_gen(gen, len(ref))
        hyp = [surface(decode(streams['H'][i].split()), CASE) for i in range(len(ref))]
        pred = folder / 'predictions.jsonl'
        with pred.open('w', encoding='utf-8') as f:
            for i, h in enumerate(hyp):
                f.write(json.dumps({'id': i, 'category': cats[i], 'hypothesis': h}, ensure_ascii=False) + '\n')
        res = {'tag': tag, 'seed': seed, 'selected_epoch': state['best']['epoch'], 'checkpoint_sha256': state['best']['checkpoint_sha256'],
               **score_all(hyp), 'seconds': time.monotonic() - start, 'generation_sha256': sha256(gen), 'predictions_sha256': sha256(pred)}
        atomic_json(folder / 'scores.json', res)
        print('%s TEST chrF2=%.4f EM=%.4f' % (name, res['overall']['chrf2_pct'], res['overall']['exact_match_pct']), flush=True)
    done = []
    for t in TAGS:
        for s in SEEDS:
            p = tdir / ('%s_seed%d' % (t, s)) / 'scores.json'
            if p.exists():
                done.append(json.loads(p.read_text()))
    if len(done) == 18:
        atomic_json(tdir / 'all_scores.json', done)
        print('ALL 18 TEST RUNS COMPLETE -> all_scores.json', flush=True)


def cmd_status(a):
    out = a.out.resolve(); rows = []
    for t in TAGS:
        for sd in SEEDS:
            f = out / 'training' / ('%s_seed%d' % (t, sd)) / 'state.json'
            if not f.exists():
                rows.append('%-10s seed%d  not started' % (t, sd)); continue
            st = json.loads(f.read_text()); h = st['history']
            secs = [x['train_seconds'] + x['validation_seconds'] for x in h if x.get('train_seconds')]
            per = sum(secs) / len(secs) / 60 if secs else float('nan')
            test = (out / 'controlled_test_v1' / ('%s_seed%d' % (t, sd)) / 'scores.json').exists()
            rows.append('%-10s seed%d  %-8s epoch %2d/%d  best epoch %s (valid chrF2 %.2f)  %.1f min/epoch  test %s'
                        % (t, sd, st.get('status', 'ACTIVE'), len(h), EPOCHS, st['best']['epoch'] if st['best'] else '-',
                           st['best']['chrf2_pct'] if st['best'] else float('nan'), per, 'done' if test else '-'))
    print('\n'.join(rows))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='stage', required=True)
    p = sub.add_parser('prepare'); p.add_argument('--data', type=Path, required=True); p.add_argument('--out', type=Path, required=True)
    p.add_argument('--case', choices=('preserve', 'lower'), default='preserve', help='preserve for Turkish (default); lower for Indonesian')
    p.add_argument('--categories', choices=('m2', 'files'), default='m2', help='m2: GECTurk rule labels; files: raw/<split>.cat')
    p.add_argument('--allow-versions', action='store_true', help=argparse.SUPPRESS)
    p = sub.add_parser('binarize'); p.add_argument('--out', type=Path, required=True); p.add_argument('--workers', type=int, default=8)
    p.add_argument('--skip-param-count', action='store_true', help=argparse.SUPPRESS)
    p = sub.add_parser('status'); p.add_argument('--out', type=Path, required=True)
    for name in ('train', 'test'):
        p = sub.add_parser(name); p.add_argument('--out', type=Path, required=True); p.add_argument('--gpu', required=True)
        p.add_argument('--tag', choices=TAGS); p.add_argument('--seed', type=int, choices=SEEDS)
        p.add_argument('--oom-retries', type=int, default=144); p.add_argument('--oom-wait', type=int, default=600)
        p.add_argument('--min-free-mb', type=int, default=6000)
        if name == 'test':
            p.add_argument('--all', action='store_true')
    a = ap.parse_args()
    if a.stage in ('train', 'test') and not getattr(a, 'all', False) and (a.tag is None or a.seed is None):
        ap.error('--tag and --seed are required (or --all for test)')
    {'prepare': cmd_prepare, 'binarize': cmd_binarize, 'train': cmd_train, 'test': cmd_test, 'status': cmd_status}[a.stage](a)


if __name__ == '__main__':
    main()
