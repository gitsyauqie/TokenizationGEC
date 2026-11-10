# Diagnosis mismatch — no GEC scores

Missing IDs are reported, not filled or excluded for scoring. Counts concern present S/T records.

| Run | Stream | Missing | Underscore | NFKC | Accents | Both | Unknown (unverified) | Unexplained |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| bpe_20k | S | 0 | 0 | 0 | 0 | 0 | 11 | 0 |
| bpe_20k | T | 0 | 0 | 0 | 0 | 0 | 20 | 0 |
| bpe_30k | S | 0 | 0 | 0 | 0 | 0 | 12 | 0 |
| bpe_30k | T | 0 | 0 | 0 | 0 | 0 | 34 | 0 |
| bpe_30k_seed1 | S | 0 | 0 | 0 | 0 | 0 | 12 | 0 |
| bpe_30k_seed1 | T | 0 | 0 | 0 | 0 | 0 | 34 | 0 |
| bpe_30k_seed2 | S | 0 | 0 | 0 | 0 | 0 | 12 | 0 |
| bpe_30k_seed2 | T | 0 | 0 | 0 | 0 | 0 | 34 | 0 |
| bpe_30k_seed3 | S | 0 | 0 | 0 | 0 | 0 | 12 | 0 |
| bpe_30k_seed3 | T | 0 | 0 | 0 | 0 | 0 | 34 | 0 |
| bpe_5k | S | 1 | 0 | 0 | 0 | 0 | 11 | 0 |
| bpe_5k | T | 1 | 0 | 0 | 0 | 0 | 14 | 0 |
| legacy_bpe | S | 0 | 0 | 0 | 0 | 0 | 11 | 0 |
| legacy_bpe | T | 0 | 0 | 0 | 0 | 0 | 16 | 0 |
| legacy_unigram | S | 0 | 0 | 86 | 0 | 0 | 3 | 0 |
| legacy_unigram | T | 0 | 0 | 91 | 0 | 0 | 8 | 0 |
| legacy_wordpiece | S | 2 | 82 | 0 | 15 | 0 | 309 | 0 |
| legacy_wordpiece | T | 2 | 94 | 0 | 15 | 0 | 315 | 0 |
| uni_20k | S | 0 | 0 | 86 | 0 | 0 | 3 | 0 |
| uni_20k | T | 0 | 0 | 91 | 0 | 0 | 21 | 0 |
| uni_30k | S | 0 | 0 | 86 | 0 | 0 | 3 | 0 |
| uni_30k | T | 0 | 0 | 91 | 0 | 0 | 45 | 0 |
| uni_5k | S | 0 | 0 | 86 | 0 | 0 | 3 | 0 |
| uni_5k | T | 0 | 0 | 91 | 0 | 0 | 4 | 0 |
| wp_10k | S | 0 | 85 | 0 | 16 | 0 | 12 | 0 |
| wp_10k | T | 0 | 98 | 0 | 16 | 0 | 18 | 0 |
| wp_20k | S | 0 | 85 | 0 | 16 | 0 | 13 | 0 |
| wp_20k | T | 0 | 98 | 0 | 16 | 0 | 49 | 0 |
| wp_30k | S | 0 | 85 | 0 | 16 | 0 | 24 | 0 |
| wp_30k | T | 0 | 97 | 0 | 16 | 0 | 103 | 0 |
| wp_5k | S | 0 | 85 | 0 | 16 | 0 | 12 | 0 |
| wp_5k | T | 0 | 98 | 0 | 16 | 0 | 14 | 0 |
| wp_5k_seed1 | S | 0 | 85 | 0 | 16 | 0 | 12 | 0 |
| wp_5k_seed1 | T | 0 | 98 | 0 | 16 | 0 | 14 | 0 |
| wp_5k_seed2 | S | 0 | 85 | 0 | 16 | 0 | 12 | 0 |
| wp_5k_seed2 | T | 0 | 98 | 0 | 16 | 0 | 14 | 0 |
| wp_5k_seed3 | S | 0 | 85 | 0 | 16 | 0 | 12 | 0 |
| wp_5k_seed3 | T | 0 | 98 | 0 | 16 | 0 | 14 | 0 |

Send REPORT.md and diagnosis.json. JSON contains bounded source/target examples.
NFKC/accent equivalence is descriptive, not permission to normalize gold or hypotheses.
Unknown-marker rows require dictionary/tokenizer round-trip verification before scoring.
