# Re-evaluation diagnostics

**Not publication-ready GEC scores. No M2 F0.5 is computed here.**

Common case policy: `lower`. Reference: canonical raw target, never per-tokenizer T lines.

| Run | n | Word-set F1 (legacy diagnostic) | Exact match % |
|---|---:|---:|---:|
| COPY_INPUT | 134025 | 89.3582 | 0.4223 |
| REFERENCE_ORACLE_SANITY | 134025 | 100.0000 | 100.0000 |

## Blocked runs

- bpe_20k: Decoded S/T does not match canonical raw data; inspect decoding, normalization, dataset order or unknown tokens. No score produced.
- bpe_30k: Decoded S/T does not match canonical raw data; inspect decoding, normalization, dataset order or unknown tokens. No score produced.
- bpe_30k_seed1: Decoded S/T does not match canonical raw data; inspect decoding, normalization, dataset order or unknown tokens. No score produced.
- bpe_30k_seed2: Decoded S/T does not match canonical raw data; inspect decoding, normalization, dataset order or unknown tokens. No score produced.
- bpe_30k_seed3: Decoded S/T does not match canonical raw data; inspect decoding, normalization, dataset order or unknown tokens. No score produced.
- bpe_5k: /ssd-data1/sq2023/DidugaCASTLE_asli_n_paper6/Paper6/tokensweep/gen/bpe_5k.out: S coverage mismatch; expected=134025, actual=134024, missing=[1589], extra=[]
- legacy_bpe: Decoded S/T does not match canonical raw data; inspect decoding, normalization, dataset order or unknown tokens. No score produced.
- legacy_unigram: Decoded S/T does not match canonical raw data; inspect decoding, normalization, dataset order or unknown tokens. No score produced.
- legacy_wordpiece: /ssd-data1/sq2023/DidugaCASTLE_asli_n_paper6/Paper6/tokensweep/gen/legacy_wordpiece.out: S coverage mismatch; expected=134025, actual=134023, missing=[1589, 113021], extra=[]
- uni_20k: Decoded S/T does not match canonical raw data; inspect decoding, normalization, dataset order or unknown tokens. No score produced.
- uni_30k: Decoded S/T does not match canonical raw data; inspect decoding, normalization, dataset order or unknown tokens. No score produced.
- uni_5k: Decoded S/T does not match canonical raw data; inspect decoding, normalization, dataset order or unknown tokens. No score produced.
- wp_10k: Decoded S/T does not match canonical raw data; inspect decoding, normalization, dataset order or unknown tokens. No score produced.
- wp_20k: Decoded S/T does not match canonical raw data; inspect decoding, normalization, dataset order or unknown tokens. No score produced.
- wp_30k: Decoded S/T does not match canonical raw data; inspect decoding, normalization, dataset order or unknown tokens. No score produced.
- wp_5k: Decoded S/T does not match canonical raw data; inspect decoding, normalization, dataset order or unknown tokens. No score produced.
- wp_5k_seed1: Decoded S/T does not match canonical raw data; inspect decoding, normalization, dataset order or unknown tokens. No score produced.
- wp_5k_seed2: Decoded S/T does not match canonical raw data; inspect decoding, normalization, dataset order or unknown tokens. No score produced.
- wp_5k_seed3: Decoded S/T does not match canonical raw data; inspect decoding, normalization, dataset order or unknown tokens. No score produced.

Send REPORT.md, both CSVs, provenance.json and run_status.json.
Hypothesis text stays in per-run folders; it need not be shared at this stage.
