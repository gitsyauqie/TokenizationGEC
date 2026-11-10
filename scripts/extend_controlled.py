#!/usr/bin/env python3
"""M1b: continue a frozen controlled run beyond epoch 10 under the identical training recipe.

The frozen checkpoint_best.pt (with optimizer, LR schedule and iterator state) is COPIED into a new
folder and training resumes exactly as train_controlled.py would have continued it. For the 15 runs
whose validation-selected checkpoint is the epoch-10 state, this is a direct continuation. For the
three runs selected at epoch 8 or 9, the remaining epochs up to 10 are retrained from that state
(Fairseq reseeds by update number, so this reproduces the original recipe up to GPU nondeterminism)
and epoch 10 is re-validated as a reproducibility check. Original checkpoints, states and test results are never modified.
Full-validation chrF2/BLEU/EM is recorded every --validate-every epochs and at --until.
With --test, the checkpoint at --until (pre-declared) is generated on the full test set and
scored with the same surface rule and metrics as controlled_test_v1.
One condition per process; run several processes on different GPUs. Rerun the same
command to resume; a larger --until extends a finished run.
"""
import argparse
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import sha256, lines  # noqa: E402
from train_controlled import (TAGS, atomic_json, decoder_for, evaluate, generation_args,  # noqa: E402
                              next_log, preflight, run_child, train_args)
from eval_reconstruction import self_check, surface  # noqa: E402


def copy_verified(src, dst, digest):
    tmp = dst.with_suffix(dst.suffix + '.tmp')
    shutil.copy2(src, tmp)
    if sha256(tmp) != digest:
        raise ValueError('Checkpoint copy hash mismatch: ' + str(src))
    os.replace(tmp, dst)


def oom_in(path):
    try:
        return 'out of memory' in Path(path).read_text(encoding='utf-8', errors='ignore')[-50000:]
    except FileNotFoundError:
        return False


def wait_for_memory(gpu, need_mb, poll):
    """Shared server: wait until the selected GPU has enough free memory before launching a child."""
    while True:
        try:
            out = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits', '-i', gpu],
                                 capture_output=True, text=True, check=True).stdout
            free = int(out.strip().splitlines()[0])
        except Exception:
            return  # nvidia-smi unavailable: rely on the OOM retry below
        if free >= need_mb:
            return
        print('%s GPU %s: %d MiB free (< %d); waiting %d s' % (time.strftime('%F %T'), gpu, free, need_mb, poll), flush=True)
        time.sleep(poll)


def oom_retry(a, label, attempt):
    """Run attempt(holder); holder[0] must name the file receiving the child's stderr. A CUDA OOM caused by
    other users' jobs is retried after a wait; the recipe is unchanged (no batch skipping, no new settings).
    Training resumes from Fairseq's latest checkpoint_last.pt, as train_controlled.py does after interruption."""
    for i in range(a.oom_retries + 1):
        wait_for_memory(a.gpu, a.min_free_mb, a.oom_wait)
        holder = []
        try:
            return attempt(holder)
        except subprocess.CalledProcessError:
            if i < a.oom_retries and holder and oom_in(holder[0]):
                print('%s %s: CUDA out of memory (shared GPU); retry %d/%d after %d s'
                      % (time.strftime('%F %T'), label, i + 1, a.oom_retries, a.oom_wait), flush=True)
                time.sleep(a.oom_wait)
                continue
            raise


def checkpoint_state(path):
    import torch
    c = torch.load(str(path), map_location='cpu')
    it = c.get('extra_state', {}).get('train_iterator', {})
    return {'has_optimizer': bool(c.get('last_optimizer_state')), 'next_epoch': it.get('epoch'),
            'num_updates': c['optimizer_history'][-1].get('num_updates')}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', type=Path, required=True, help='paper6_revision_20261007')
    ap.add_argument('--tag', required=True, choices=TAGS)
    ap.add_argument('--gpu', required=True)
    ap.add_argument('--seed', type=int, default=42, choices=(42, 43, 44))
    ap.add_argument('--until', type=int, default=20)
    ap.add_argument('--validate-every', type=int, default=2)
    ap.add_argument('--out', type=Path, default=None, help='default <root>/extended_seed<seed>')
    ap.add_argument('--test', action='store_true', help='evaluate the --until checkpoint on the full test set')
    ap.add_argument('--check-only', action='store_true')
    ap.add_argument('--oom-retries', type=int, default=144, help='CUDA OOM retries per step (shared server)')
    ap.add_argument('--oom-wait', type=int, default=600, help='seconds between OOM retries / memory polls')
    ap.add_argument('--min-free-mb', type=int, default=6000, help='free GPU memory required before each launch')
    ap.add_argument('--keep-resume', action='store_true',
                    help='keep resume/checkpoint_last.pt after finishing (default: delete it once the identical '
                         'checkpoint_epochNN.pt copy is verified; it is restored automatically when extending)')
    a = ap.parse_args()
    if not a.gpu.isdigit():
        ap.error('Select one numeric GPU ID')
    if a.until <= 10 or a.validate_every < 1:
        ap.error('--until must exceed 10 and --validate-every must be >= 1')
    os.environ['CUDA_VISIBLE_DEVICES'] = a.gpu
    os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
    import fairseq, torch, sacrebleu, tokenizers, sentencepiece
    versions = {'fairseq': fairseq.__version__, 'torch': torch.__version__, 'sacrebleu': sacrebleu.__version__,
                'tokenizers': tokenizers.__version__, 'sentencepiece': sentencepiece.__version__}

    root = a.root.resolve()
    prepared, binary = root / 'controlled_pilot_v2', root / 'controlled_binary_smoke_v1'
    frozen = json.loads((root / 'frozen_test_checkpoint_manifest.json').read_text())
    run = [r for r in frozen['runs'] if r['tag'] == a.tag and r['seed'] == a.seed]
    if len(run) != 1:
        raise ValueError('Frozen run not found')
    run = run[0]
    start_epoch = run['epoch']
    if start_epoch not in (8, 9, 10):
        raise ValueError('Unexpected frozen checkpoint epoch: %s' % start_epoch)
    cfg10 = json.loads((root / ('controlled_training_seed%d' % a.seed) / 'config.json').read_text())
    if versions != cfg10['versions']:
        raise ValueError('Environment differs from original training: ' + str(versions))
    if sha256(HERE / 'train_controlled.py') != cfg10['script_sha256']:
        raise ValueError('train_controlled.py changed since original training')

    out = (a.out or root / ('extended_seed%d' % a.seed)).resolve()
    folder = out / ('%s_seed%d' % (a.tag, a.seed))
    resume, logs = folder / 'resume', folder / 'logs'
    for p in (folder, resume, logs):
        p.mkdir(parents=True, exist_ok=True)
    config = {'tag': a.tag, 'seed': a.seed, 'source_checkpoint': run['checkpoint'],
              'source_checkpoint_sha256': run['checkpoint_sha256'], 'validate_every': a.validate_every,
              'recipe': 'train_controlled.train_args unchanged; one Fairseq process per epoch resuming checkpoint_last.pt',
              'source_epoch': start_epoch,
              'train_controlled_sha256': cfg10['script_sha256'],
              'versions': versions,
              'policy': 'Continuation of the frozen validation-selected state (epochs after it retrained if it precedes 10). Main paper results remain the 10-epoch frozen runs. '
                        'Test checkpoint is the pre-declared --until epoch; no test-based selection.'}
    with (folder / 'RUN.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        cpath = folder / 'config.json'
        if cpath.exists():
            if json.loads(cpath.read_text()) != config:
                raise ValueError('Configuration changed; refusing unsafe resume')
        else:
            atomic_json(cpath, config)
        print('Checking prepared/binary hashes', flush=True)
        preflight(prepared, binary); self_check(sacrebleu)
        data = binary / a.tag / 'bin'
        from fairseq import options
        options.parse_args_and_arch(options.get_training_parser(), train_args(data, resume, start_epoch + 1, a.seed))
        options.parse_args_and_arch(options.get_generation_parser(), generation_args(data, resume / 'x.pt')[3:])

        statepath = folder / 'state.json'; last = resume / 'checkpoint_last.pt'
        if statepath.exists():
            state = json.loads(statepath.read_text())
        else:
            src = root / run['checkpoint']
            if sha256(src) != run['checkpoint_sha256']:
                raise ValueError('Frozen checkpoint hash mismatch')
            copy_verified(src, last, run['checkpoint_sha256'])
            info = checkpoint_state(last)
            if not info['has_optimizer'] or info['next_epoch'] != start_epoch + 1:
                raise ValueError('Checkpoint lacks optimizer or expected iterator state: ' + str(info))
            state = {'tag': a.tag, 'seed': a.seed, 'start': info, 'start_epoch': start_epoch, 'trained_epoch': start_epoch,
                     'pending_checkpoint_sha256': run['checkpoint_sha256'], 'history': [], 'train_seconds': {},
                     'script_sha256': []}
            atomic_json(statepath, state)
        digest = sha256(__file__)
        if digest not in state.setdefault('script_sha256', []):
            state['script_sha256'].append(digest); atomic_json(statepath, state)
        print('Start state: %s; trained_epoch=%d' % (state['start'], state['trained_epoch']), flush=True)
        if a.until < state['trained_epoch']:
            raise ValueError('--until %d is below the epoch already trained (%d); refusing to mislabel checkpoints'
                             % (a.until, state['trained_epoch']))
        if a.check_only:
            print('CHECK PASSED: hashes, versions, recipe, checkpoint state and CLI flags. No training.', flush=True)
            return

        if not last.exists() and a.until > state['trained_epoch']:
            src = folder / ('checkpoint_epoch%02d.pt' % state['trained_epoch'])
            if not src.exists():
                raise ValueError('Resume checkpoint missing and no epoch copy to restore from')
            copy_verified(src, last, state['pending_checkpoint_sha256'])
            print('Restored resume checkpoint from ' + src.name, flush=True)
        ref = [surface(x, 'lower') for x in lines(prepared / 'surface/valid.target')]
        cats = lines(prepared / 'surface/valid.category')
        decode = decoder_for(a.tag, prepared)
        validated = {r['epoch'] for r in state['history']}
        for epoch in range(start_epoch + 1, a.until + 1):
            if state['trained_epoch'] < epoch:
                # An interrupted epoch leaves a mid-epoch checkpoint_last.pt (interval saves); Fairseq resumes it,
                # exactly as train_controlled.py does. Otherwise the file must be the recorded end-of-epoch state.
                if state.get('training_started') != epoch and sha256(last) != state['pending_checkpoint_sha256']:
                    raise ValueError('Resume checkpoint changed outside this runner')
                state['training_started'] = epoch; atomic_json(statepath, state)
                start = time.monotonic()
                cmd = [sys.executable, str(HERE / 'train_controlled.py'), '--fairseq-train'] + train_args(data, resume, epoch, a.seed)

                def train_once(holder, epoch=epoch, cmd=cmd):
                    trainlog = next_log(logs, 'train_epoch%02d' % epoch, '.log'); holder.append(trainlog)
                    atomic_json(logs / (trainlog.stem + '.command.json'), cmd)
                    print('%s epoch %d/%d training' % (a.tag, epoch, a.until), flush=True)
                    run_child(cmd, trainlog, lock.fileno())
                oom_retry(a, '%s epoch %d training' % (a.tag, epoch), train_once)
                info = checkpoint_state(last)
                if info['next_epoch'] != epoch + 1:
                    raise ValueError('Unexpected iterator state after epoch %d: %s' % (epoch, info))
                state['trained_epoch'] = epoch; state['pending_checkpoint_sha256'] = sha256(last)
                state['train_seconds'][str(epoch)] = time.monotonic() - start
                atomic_json(statepath, state)
            if (epoch % a.validate_every == 0 or epoch == a.until) and epoch not in validated and state['trained_epoch'] == epoch:
                start = time.monotonic()
                cmd = generation_args(data, last)

                def valid_once(holder, epoch=epoch, cmd=cmd):
                    g = next_log(logs, 'valid_epoch%02d' % epoch, '.out'); holder.append(g.with_suffix('.stderr.log'))
                    atomic_json(logs / (g.stem + '.command.json'), cmd)
                    print('%s epoch %d validation' % (a.tag, epoch), flush=True)
                    run_child(cmd, g, lock.fileno(), g.with_suffix('.stderr.log'))
                    return g
                gen = oom_retry(a, '%s epoch %d validation' % (a.tag, epoch), valid_once)
                score, subs = evaluate(gen, ref, cats, decode, sacrebleu)
                state['history'].append({'epoch': epoch, **score, 'category_scores': subs,
                                         'generation_sha256': sha256(gen), 'checkpoint_sha256': sha256(last),
                                         'validation_seconds': time.monotonic() - start})
                validated.add(epoch); atomic_json(statepath, state); gen.unlink()
                print('%s epoch %d: valid chrF2=%.4f EM=%.4f' % (a.tag, epoch, score['chrf2_pct'], score['exact_match_pct']), flush=True)
        final = folder / ('checkpoint_epoch%02d.pt' % a.until)
        if not final.exists():
            copy_verified(last, final, state['pending_checkpoint_sha256'])
        for p in resume.glob('checkpoint_*_*.pt'):
            p.unlink()  # Fairseq interval-update checkpoints
        if not a.keep_resume and last.exists():
            if sha256(final) != state['pending_checkpoint_sha256']:
                raise ValueError('Epoch copy does not match the trained state; resume checkpoint retained')
            last.unlink()  # identical to the verified epoch copy; restored from it if the run is extended

        if a.test:
            tdir = root / 'controlled_test_v1'
            tprep = json.loads((tdir / a.tag / 'prepared.json').read_text())
            for rel, digest in tprep['sha256'].items():
                if sha256(tdir / a.tag / rel) != digest:
                    raise ValueError('Test binary changed: ' + rel)
            tref = lines(tdir / 'test.target'); tcats = lines(tdir / 'test.category')
            if len(tref) != 134025 or len(tcats) != 134025:
                raise ValueError('Test coverage invalid')
            tout = folder / ('test_epoch%02d' % a.until); tout.mkdir(exist_ok=True)
            scorepath = tout / 'scores.json'
            if not scorepath.exists():
                start = time.monotonic()
                gen = tout / 'generation.out'
                cmd = generation_args(tdir / a.tag / 'bin', final); cmd[cmd.index('--gen-subset') + 1] = 'test'
                atomic_json(tout / 'command.json', cmd)

                def test_once(holder):
                    holder.append(tout / 'generation.stderr.log')
                    print('%s test generation (epoch %d)' % (a.tag, a.until), flush=True)
                    with gen.open('w') as f, (tout / 'generation.stderr.log').open('w') as err:
                        subprocess.run(cmd, stdout=f, stderr=err, check=True, pass_fds=(lock.fileno(),))
                oom_retry(a, '%s test generation' % a.tag, test_once)
                from common import parse_gen
                streams = parse_gen(gen, len(tref))
                hyp = [surface(decode(streams['H'][i].split()), 'lower') for i in range(len(tref))]
                pred = tout / 'predictions.jsonl'
                with pred.open('w', encoding='utf-8') as f:
                    for i, h in enumerate(hyp):
                        f.write(json.dumps({'id': i, 'category': tcats[i], 'hypothesis': h}, ensure_ascii=False) + '\n')
                from eval_reconstruction import metric_scores
                overall = metric_scores(hyp, tref, sacrebleu)
                cat_scores = []
                for c in sorted(set(tcats)):
                    ids = [i for i, x in enumerate(tcats) if x == c]
                    cat_scores.append(dict(category=c, **metric_scores([hyp[i] for i in ids], [tref[i] for i in ids], sacrebleu)))
                atomic_json(scorepath, {'tag': a.tag, 'seed': a.seed, 'epoch': a.until, 'overall': overall,
                                        'categories': cat_scores, 'checkpoint_sha256': sha256(final),
                                        'generation_sha256': sha256(gen), 'predictions_sha256': sha256(pred),
                                        'seconds': time.monotonic() - start})
                print('%s TEST epoch %d: chrF2=%.4f EM=%.4f' % (a.tag, a.until, overall['chrf2_pct'], overall['exact_match_pct']), flush=True)
        print('DONE %s until epoch %d' % (a.tag, a.until), flush=True)


if __name__ == '__main__':
    main()
