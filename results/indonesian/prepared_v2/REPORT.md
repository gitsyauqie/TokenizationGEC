# Controlled pilot preparation — no model training

New derived train/valid files; original inputs untouched. Test data not read.

| Split | Original n | Retained n | Exact API-marker exclusions |
|---|---:|---:|---:|
| train | 1072192 | 1072191 | 1 |
| valid | 134024 | 134023 | 1 |

| Tokenizer | Status |
|---|---|
| spbpe_5k | PREPARED_PENDING_LENGTH_AND_UNK_REVIEW:  |
| spbpe_20k | PREPARED_PENDING_LENGTH_AND_UNK_REVIEW:  |
| wp_5k | PREPARED_PENDING_LENGTH_AND_UNK_REVIEW:  |
| wp_20k | PREPARED_PENDING_LENGTH_AND_UNK_REVIEW:  |
| spuni_5k | PREPARED_PENDING_LENGTH_AND_UNK_REVIEW:  |
| spuni_20k | PREPARED_PENDING_LENGTH_AND_UNK_REVIEW:  |

Do not launch training yet. Review maximum lengths, unknown rows and unexpected roundtrip mismatches first.
Full shared dictionaries contain requested vocabulary including 4 Fairseq specials, but Fairseq loading/model parameter counts must still be verified.
No automatic sentence dropping, truncation or replacement from references. Validation unknowns remain documented.
Send REPORT.md, status.json, data_manifest.json, tokenizer_manifest.json, lengths_and_roundtrip.csv, excluded_ids.csv and provenance.json.
If a tokenizer is blocked, also send its roundtrip_examples.json if present. No need to download full encoded corpus.
