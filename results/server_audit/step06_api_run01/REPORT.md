# Observed API-failure marker audit

| Split | n | Exact source marker | Exact target marker | Any exact marker | Any flag | Distinct targets for exact source marker |
|---|---:|---:|---:|---:|---:|---:|
| train | 1072192 | 1 | 0 | 1 | 1 | 1 |
| valid | 134024 | 1 | 0 | 1 | 1 | 1 |
| test | 134025 | 0 | 0 | 0 | 0 | 0 |

Exact marker permits only surrounding quote, whitespace and case differences. Longer strings containing the phrase are candidates requiring review.
Source and target counts overlap; use union counts rather than summing. Flags do not remove rows.
Multiple distinct targets for one marker are an input/reference ambiguity, not a recoverable linguistic corruption.
Zero detected markers does not certify dataset quality or absence of other API failures.
Send REPORT.md, counts.csv, affected_ids.csv, summary.json, provenance.json and validation_examples.csv.
