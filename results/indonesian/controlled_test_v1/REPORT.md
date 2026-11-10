# Controlled test evaluation

All18 validation-selected checkpoints evaluated on134025 original test rows. No checkpoint reselection. Mean ± sample SD over3 seeds.

| Condition | chrF2 | BLEU | Exact match % |
|---|---:|---:|---:|
| spbpe_5k | 96.1701 ± 0.0286 | 92.1871 ± 0.0670 | 45.0167 ± 0.3129 |
| spbpe_20k | 95.9833 ± 0.0237 | 91.7557 ± 0.0605 | 41.7850 ± 0.9008 |
| wp_5k | 96.1622 ± 0.0534 | 92.1714 ± 0.1065 | 44.9287 ± 0.5934 |
| wp_20k | 95.9182 ± 0.0377 | 91.6663 ± 0.0802 | 41.3793 ± 0.2819 |
| spuni_5k | 96.1331 ± 0.0556 | 92.0688 ± 0.1210 | 44.2141 ± 0.4828 |
| spuni_20k | 96.0234 ± 0.0658 | 91.9586 ± 0.0895 | 42.9830 ± 0.3730 |

These are synthetic reconstruction metrics, not edit F0.5. Sample SD is not a confidence interval. Reference quality and historical split overlap remain limitations. Paired uncertainty analysis is a separate next step.
