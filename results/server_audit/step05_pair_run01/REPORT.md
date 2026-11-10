# Observed pair changes — not GEC scores

All nine raw files match Step01 hashes before and after scanning. This is a hash manifest, not a physical backup.

| Split | Rows | Exact same | Whitespace only | Digit sequence changed | Target <6 words |
|---|---:|---:|---:|---:|---:|
| train | 1072192 | 3 | 4204 | 15835 | 23935 |
| valid | 134024 | 1 | 556 | 1965 | 2922 |
| test | 134025 | 1 | 561 | 2021 | 3005 |

## Definitions and limits

- Whitespace normalization is used only to classify differences. Raw texts are preserved.
- Exact/whitespace/case/punctuation classes are mutually exclusive in that priority order. Other flags overlap; do not sum them.
- Punctuation-only means matching case-sensitive Python Unicode word-token lists after whitespace normalization; underscores belong to word tokens. It is a surface heuristic.
- Digit sequence changed compares ordered digit runs. This is not proof of a factual error; punctuation changes in numbers also need review.
- Word counts use whitespace splitting. Smaller/larger source counts do not identify semantic deletion/insertion or a generator.
- Short/long targets and replacement characters are review flags, not rejection rules or evidence of OCR.
- Original category labels are retained. No historical prompt, model version, or linguistic correctness is inferred.
- Test aggregates describe the existing benchmark only. Do not use them to tune filtering thresholds or choose favorable test examples.
- Examples are validation-only and intentionally flag-targeted; repeated IDs and unequal category weights preclude quality-prevalence estimates.

Send REPORT.md, counts.csv, provenance.json and validation_examples.csv. Examples contain raw validation text.
