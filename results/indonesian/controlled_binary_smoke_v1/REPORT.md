# Binarization and optional GPU smoke

| Condition | Status | Parameters |
|---|---|---:|
| spbpe_5k | BINARY_AND_GPU_SMOKE_PASSED | 14135296 |
| spbpe_20k | BINARY_AND_GPU_SMOKE_PASSED | 21815296 |
| wp_5k | BINARY_AND_GPU_SMOKE_PASSED | 14135296 |
| wp_20k | BINARY_AND_GPU_SMOKE_PASSED | 21815296 |
| spuni_5k | BINARY_AND_GPU_SMOKE_PASSED | 14135296 |
| spuni_20k | BINARY_AND_GPU_SMOKE_PASSED | 21815296 |

All six completed: True
Parameter counts equal within each vocabulary budget: True
Shared max source/target positions:4096. No skip-invalid or truncation flags.
GPU smoke uses a short batch and each side longest singleton. It does not prove every possible full-training batch fits GPU memory.
No performance metric, full training or checkpoint selection. Do not reuse smoke weights; no checkpoints are saved.
If blocked, inspect status.json and the condition preprocess.log; do not silently reduce length or drop rows.
Send REPORT.md, status.json, provenance.json. If blocked, also send relevant preprocess.log.
