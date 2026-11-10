#!/usr/bin/env bash
# Inference only: preserves markers, requires fresh output path, no skipped IDs.
set -euo pipefail
if [[ $# -ne 4 ]]; then
  echo 'Usage: GPU=0 bash regenerate_raw.sh BIN_DIR CHECKPOINT SPLIT OUTPUT.out' >&2
  exit 1
fi
bin=$1
checkpoint=$2
split=$3
output=$4
[[ -d "$bin" && -f "$checkpoint" ]] || { echo 'Missing bin/checkpoint' >&2; exit 1; }
[[ ! -e "$output" && ! -e "$output.stderr.log" ]] || { echo 'Output exists; choose a new path' >&2; exit 1; }
command -v fairseq-generate >/dev/null
mkdir -p "$(dirname "$output")"
# Fairseq defaults to no BPE removal when --remove-bpe is absent.
# Keep the legacy test generation beam=5 and default length settings for rescue.
CUDA_VISIBLE_DEVICES=${GPU:-0} fairseq-generate "$bin" \
  --path "$checkpoint" --gen-subset "$split" --beam 5 --nbest 1 \
  > "$output" 2> "$output.stderr.log"
echo "Saved $output; validate all S/T/H IDs before using any score."
