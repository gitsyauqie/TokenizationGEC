#!/usr/bin/env bash
# M1b queue: runs conditions one after another on ONE GPU. Usage (from paper6_revision_20261007):
#   nohup bash scripts/run_extend_queue.sh 8 spbpe_5k:42:2 wp_5k:42:2 ... > training_logs/extend_queue_gpu8.log 2>&1 < /dev/null &
# Each item is TAG:SEED:VALIDATE_EVERY. Rerunning the same command resumes; finished runs are skipped quickly.
set -u
GPU="$1"; shift
UNTIL="${UNTIL:-20}"
mkdir -p training_logs
for item in "$@"; do
  IFS=: read -r TAG SEED EVERY <<< "$item"
  LOG="training_logs/extend_${TAG}_seed${SEED}.log"
  echo "$(date '+%F %T') START ${TAG} seed${SEED} gpu${GPU} until${UNTIL} every${EVERY}"
  if python -u scripts/extend_controlled.py --root . --tag "$TAG" --seed "$SEED" --gpu "$GPU" \
       --until "$UNTIL" --validate-every "$EVERY" --test >> "$LOG" 2>&1 < /dev/null; then
    echo "$(date '+%F %T') DONE  ${TAG} seed${SEED}"
  else
    echo "$(date '+%F %T') FAIL  ${TAG} seed${SEED} (see ${LOG}); continuing with next item"
  fi
done
echo "$(date '+%F %T') QUEUE FINISHED gpu${GPU}"
