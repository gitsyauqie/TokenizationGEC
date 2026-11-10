# Retrospective synthetic reconstruction metrics

Not GEC edit F0.5 or a controlled retraining experiment. All scores use original full test rows.
chrF2 and BLEU are corpus scores; category scores are descriptive, not averaged into the overall score.
All metrics use the same lower/preserve policy and punctuation/underscore surface rule as verified Step02.

| Run | n | chrF2 /100 | BLEU /100 | Exact match % |
|---|---:|---:|---:|---:|
| COPY_INPUT | 134025 | 90.0785 | 76.5212 | 0.4223 |
| REFERENCE_ORACLE_SANITY | 134025 | 100.0000 | 100.0000 | 100.0000 |
| bpe_20k | 134025 | 95.4695 | 90.6834 | 38.1891 |
| bpe_30k | 134025 | 95.3032 | 90.1948 | 36.1597 |
| bpe_30k_seed1 | 134025 | 95.3052 | 90.2172 | 36.6469 |
| bpe_30k_seed2 | 134025 | 95.2269 | 90.0973 | 36.1433 |
| bpe_30k_seed3 | 134025 | 95.1960 | 90.0631 | 35.9888 |
| uni_20k | 134025 | 95.5712 | 91.1246 | 41.4430 |
| uni_30k | 134025 | 94.8325 | 89.7939 | 35.9328 |
| uni_5k | 134025 | 95.4388 | 91.1988 | 43.8336 |
| wp_10k | 134025 | 95.2943 | 90.6560 | 39.2957 |
| wp_20k | 134025 | 95.0438 | 90.2025 | 36.7700 |
| wp_30k | 134025 | 94.6475 | 89.6031 | 34.7293 |
| wp_5k | 134025 | 95.2627 | 90.8957 | 42.9696 |
| wp_5k_seed1 | 134025 | 95.2387 | 90.8340 | 42.3302 |
| wp_5k_seed2 | 134025 | 95.2785 | 90.8812 | 42.3466 |
| wp_5k_seed3 | 134025 | 95.3247 | 90.9716 | 42.0936 |

## Blocked runs
- bpe_5k: Not verified at Step02: ValueError: /ssd-data1/sq2023/DidugaCASTLE_asli_n_paper6/Paper6/tokensweep/gen/bpe_5k.out: S coverage mismatch; expected=134025, actual=134024, missing=[1589], extra=[]
- legacy_bpe: Not verified at Step02: ValueError: Legacy tokenizer provenance not established; kept separate
- legacy_unigram: Not verified at Step02: ValueError: Legacy tokenizer provenance not established; kept separate
- legacy_wordpiece: Not verified at Step02: ValueError: Legacy tokenizer provenance not established; kept separate

No significance or seed-averaged claim is computed. A model matching a flawed reference can still score highly.
Send REPORT.md, scores.csv, category_scores.csv, run_status.json, provenance.json.
