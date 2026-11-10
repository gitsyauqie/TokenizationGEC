# Verified retrospective diagnostics

**Not edit-based GEC F0.5; not a controlled rerun.**

| Run | n | Word-set F1 % | Exact match % |
|---|---:|---:|---:|
| COPY_INPUT | 134025 | 89.3594 | 0.4223 |
| REFERENCE_ORACLE_SANITY | 134025 | 100.0000 | 100.0000 |
| bpe_20k | 134025 | 96.7373 | 38.1891 |
| bpe_30k | 134025 | 96.5081 | 36.1597 |
| bpe_30k_seed1 | 134025 | 96.5339 | 36.6469 |
| bpe_30k_seed2 | 134025 | 96.4757 | 36.1433 |
| bpe_30k_seed3 | 134025 | 96.4547 | 35.9888 |
| uni_20k | 134025 | 96.8976 | 41.4430 |
| uni_30k | 134025 | 96.2406 | 35.9328 |
| uni_5k | 134025 | 97.1205 | 43.8336 |
| wp_10k | 134025 | 96.8489 | 39.2957 |
| wp_20k | 134025 | 96.5695 | 36.7700 |
| wp_30k | 134025 | 96.2078 | 34.7293 |
| wp_5k | 134025 | 97.0927 | 42.9696 |
| wp_5k_seed1 | 134025 | 97.0956 | 42.3302 |
| wp_5k_seed2 | 134025 | 97.1015 | 42.3466 |
| wp_5k_seed3 | 134025 | 97.1423 | 42.0936 |

## Blocked

- bpe_5k: ValueError: /ssd-data1/sq2023/DidugaCASTLE_asli_n_paper6/Paper6/tokensweep/gen/bpe_5k.out: S coverage mismatch; expected=134025, actual=134024, missing=[1589], extra=[]
- legacy_bpe: ValueError: Legacy tokenizer provenance not established; kept separate
- legacy_unigram: ValueError: Legacy tokenizer provenance not established; kept separate
- legacy_wordpiece: ValueError: Legacy tokenizer provenance not established; kept separate

Scoring retains raw gold and model unknowns. Normalization differences are not erased.
Send REPORT.md, both CSVs, verification.json and provenance.json. Do not send full hypothesis folders.
