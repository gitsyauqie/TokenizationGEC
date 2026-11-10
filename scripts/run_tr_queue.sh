#!/usr/bin/env bash
# M7 queue: trains, then tests, Turkish conditions one after another on ONE GPU. Usage (from paper6_revision_20261007):
#   nohup bash scripts/run_tr_queue.sh 0 spbpe_5k:42 wp_5k:42 ... > training_logs/tr_queue_gpu0.log 2>&1 < /dev/null &
# Each item is TAG:SEED. Rerunning the same command resumes; finished runs are skipped quickly.
set -u
GPU="$1"; shift
OUT="${OUT:-gecturk_m7}"
PY="${PY:-python}"   # e.g. PY=/ssd-data1/sq2023/.conda/envs/fairseq/bin/python
mkdir -p training_logs
for item in "$@"; do
  IFS=: read -r TAG SEED <<< "$item"
  LOG="training_logs/tr_${TAG}_seed${SEED}.log"
  echo "$(date '+%F %T') START ${TAG} seed${SEED} gpu${GPU} python=$PY"
  if "$PY" -u scripts/tr_pipeline.py train --out "$OUT" --tag "$TAG" --seed "$SEED" --gpu "$GPU" >> "$LOG" 2>&1 < /dev/null \
     && "$PY" -u scripts/tr_pipeline.py test --out "$OUT" --tag "$TAG" --seed "$SEED" --gpu "$GPU" >> "$LOG" 2>&1 < /dev/null; then
    echo "$(date '+%F %T') DONE  ${TAG} seed${SEED}"
  else
    echo "$(date '+%F %T') FAIL  ${TAG} seed${SEED} (see ${LOG}); continuing with next item"
  fi
done
echo "$(date '+%F %T') QUEUE FINISHED gpu${GPU}"
