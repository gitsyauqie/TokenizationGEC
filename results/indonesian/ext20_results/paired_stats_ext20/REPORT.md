# Step16 — paired statistics (M3) — extended runs, test at epoch 20

All 134025 test rows; 19 systems (18 runs + COPY_INPUT). Stored scores reproduced exactly before resampling.
Bootstrap B=2000 (stratified by category; cluster variant over 133782 identical-reference clusters). Approximate randomization R=10000.

## Primary comparisons, seed-mean (A − B)

| A | B | Metric | Δ | 95% CI | Cluster 95% CI | p (AR) | p (Holm) | Seeds A>B |
|---|---|---|---:|---|---|---:|---:|---:|
| spbpe_5k | spbpe_20k | chrf2_pct | +0.0602 | [+0.0488, +0.0718] | [+0.0485, +0.0719] | 0.0001 | 0.0006 | 3/3 |
| spbpe_5k | spbpe_20k | bleu | +0.2356 | [+0.2107, +0.2603] | [+0.2109, +0.2621] | 0.0001 | 0.0006 | 3/3 |
| spbpe_5k | spbpe_20k | exact_match_pct | +2.9955 | [+2.8477, +3.1392] | [+2.8432, +3.1517] | 0.0001 | 0.0006 | 3/3 |
| wp_5k | wp_20k | chrf2_pct | +0.1873 | [+0.1751, +0.1989] | [+0.1754, +0.2000] | 0.0001 | 0.0006 | 3/3 |
| wp_5k | wp_20k | bleu | +0.4612 | [+0.4368, +0.4862] | [+0.4355, +0.4887] | 0.0001 | 0.0006 | 3/3 |
| wp_5k | wp_20k | exact_match_pct | +4.0443 | [+3.8955, +4.2017] | [+3.8805, +4.2131] | 0.0001 | 0.0006 | 3/3 |
| spuni_5k | spuni_20k | chrf2_pct | +0.0859 | [+0.0737, +0.0979] | [+0.0740, +0.0975] | 0.0001 | 0.0006 | 3/3 |
| spuni_5k | spuni_20k | bleu | +0.1188 | [+0.0958, +0.1424] | [+0.0962, +0.1415] | 0.0001 | 0.0006 | 3/3 |
| spuni_5k | spuni_20k | exact_match_pct | +1.6962 | [+1.5678, +1.8413] | [+1.5670, +1.8375] | 0.0001 | 0.0006 | 3/3 |
| spbpe_5k | wp_5k | chrf2_pct | -0.0373 | [-0.0456, -0.0293] | [-0.0459, -0.0289] | 0.0001 | 0.0006 | 1/3 |
| spbpe_5k | wp_5k | bleu | -0.0620 | [-0.0795, -0.0446] | [-0.0801, -0.0437] | 0.0001 | 0.0006 | 1/3 |
| spbpe_5k | wp_5k | exact_match_pct | -0.2684 | [-0.3788, -0.1522] | [-0.3806, -0.1514] | 0.0001 | 0.0006 | 1/3 |
| spbpe_5k | spuni_5k | chrf2_pct | -0.0115 | [-0.0209, -0.0015] | [-0.0211, -0.0022] | 0.0173 | 0.0173 | 1/3 |
| spbpe_5k | spuni_5k | bleu | +0.0178 | [-0.0016, +0.0389] | [-0.0018, +0.0378] | 0.0842 | 0.0842 | 2/3 |
| spbpe_5k | spuni_5k | exact_match_pct | +0.5044 | [+0.3850, +0.6325] | [+0.3801, +0.6289] | 0.0001 | 0.0006 | 2/3 |
| wp_5k | spuni_5k | chrf2_pct | +0.0258 | [+0.0163, +0.0359] | [+0.0163, +0.0359] | 0.0001 | 0.0006 | 2/3 |
| wp_5k | spuni_5k | bleu | +0.0798 | [+0.0600, +0.0996] | [+0.0599, +0.1003] | 0.0001 | 0.0006 | 2/3 |
| wp_5k | spuni_5k | exact_match_pct | +0.7727 | [+0.6529, +0.8966] | [+0.6541, +0.8988] | 0.0001 | 0.0006 | 3/3 |

## Probability of highest seed-mean score (bootstrap)

| Budget | Metric | Tag | Seed-mean | P(best) |
|---|---|---|---:|---:|
| 5k | chrf2_pct | spbpe_5k | 96.3854 | 0.000 |
| 5k | chrf2_pct | wp_5k | 96.4227 | 1.000 |
| 5k | chrf2_pct | spuni_5k | 96.3969 | 0.000 |
| 5k | bleu | spbpe_5k | 92.7139 | 0.000 |
| 5k | bleu | wp_5k | 92.7758 | 1.000 |
| 5k | bleu | spuni_5k | 92.6960 | 0.000 |
| 5k | exact_match_pct | spbpe_5k | 48.3460 | 0.000 |
| 5k | exact_match_pct | wp_5k | 48.6143 | 1.000 |
| 5k | exact_match_pct | spuni_5k | 47.8416 | 0.000 |
| 20k | chrf2_pct | spbpe_20k | 96.3252 | 0.989 |
| 20k | chrf2_pct | wp_20k | 96.2354 | 0.000 |
| 20k | chrf2_pct | spuni_20k | 96.3110 | 0.011 |
| 20k | bleu | spbpe_20k | 92.4783 | 0.000 |
| 20k | bleu | wp_20k | 92.3146 | 0.000 |
| 20k | bleu | spuni_20k | 92.5772 | 1.000 |
| 20k | exact_match_pct | spbpe_20k | 45.3505 | 0.000 |
| 20k | exact_match_pct | wp_20k | 44.5700 | 0.000 |
| 20k | exact_match_pct | spuni_20k | 46.1454 | 1.000 |

## Per-seed primary tests (chrF2 and exact match)

| A | B | Seed | Metric | Δ | 95% CI | p (AR) | p (Holm, 18) |
|---|---|---:|---|---:|---|---:|---:|
| spbpe_5k | spbpe_20k | 42 | chrf2_pct | +0.0886 | [+0.0728, +0.1038] | 0.0001 | 0.0018 |
| spbpe_5k | spbpe_20k | 43 | chrf2_pct | +0.0767 | [+0.0614, +0.0922] | 0.0001 | 0.0018 |
| spbpe_5k | spbpe_20k | 44 | chrf2_pct | +0.0152 | [-0.0002, +0.0317] | 0.0621 | 0.1242 |
| spbpe_5k | spbpe_20k | 42 | exact_match_pct | +2.3511 | [+2.1496, +2.5495] | 0.0001 | 0.0018 |
| spbpe_5k | spbpe_20k | 43 | exact_match_pct | +3.2763 | [+3.0919, +3.4583] | 0.0001 | 0.0018 |
| spbpe_5k | spbpe_20k | 44 | exact_match_pct | +3.3591 | [+3.1696, +3.5359] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 42 | chrf2_pct | +0.2296 | [+0.2142, +0.2446] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 43 | chrf2_pct | +0.1552 | [+0.1390, +0.1709] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 44 | chrf2_pct | +0.1770 | [+0.1614, +0.1926] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 42 | exact_match_pct | +4.3835 | [+4.1984, +4.5857] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 43 | exact_match_pct | +3.8179 | [+3.6187, +4.0075] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 44 | exact_match_pct | +3.9314 | [+3.7448, +4.1254] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 42 | chrf2_pct | +0.0649 | [+0.0499, +0.0801] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 43 | chrf2_pct | +0.0592 | [+0.0418, +0.0771] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 44 | chrf2_pct | +0.1338 | [+0.1190, +0.1497] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 42 | exact_match_pct | +1.9728 | [+1.7847, +2.1668] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 43 | exact_match_pct | +1.2222 | [+1.0371, +1.4042] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 44 | exact_match_pct | +1.8937 | [+1.7093, +2.0818] | 0.0001 | 0.0018 |
| spbpe_5k | wp_5k | 42 | chrf2_pct | -0.0833 | [-0.0958, -0.0712] | 0.0001 | 0.0018 |
| spbpe_5k | wp_5k | 43 | chrf2_pct | +0.0290 | [+0.0149, +0.0429] | 0.0001 | 0.0018 |
| spbpe_5k | wp_5k | 44 | chrf2_pct | -0.0576 | [-0.0703, -0.0437] | 0.0001 | 0.0018 |
| spbpe_5k | wp_5k | 42 | exact_match_pct | -0.1276 | [-0.2962, +0.0359] | 0.1342 | 0.4026 |
| spbpe_5k | wp_5k | 43 | exact_match_pct | +0.0754 | [-0.0918, +0.2447] | 0.3633 | 0.7265 |
| spbpe_5k | wp_5k | 44 | exact_match_pct | -0.7528 | [-0.9170, -0.5857] | 0.0001 | 0.0018 |
| spbpe_5k | spuni_5k | 42 | chrf2_pct | -0.0052 | [-0.0187, +0.0081] | 0.4581 | 0.4581 |
| spbpe_5k | spuni_5k | 43 | chrf2_pct | +0.1117 | [+0.0973, +0.1261] | 0.0001 | 0.0018 |
| spbpe_5k | spuni_5k | 44 | chrf2_pct | -0.1412 | [-0.1546, -0.1278] | 0.0001 | 0.0018 |
| spbpe_5k | spuni_5k | 42 | exact_match_pct | +0.3231 | [+0.1544, +0.5007] | 0.0004 | 0.0018 |
| spbpe_5k | spuni_5k | 43 | exact_match_pct | +1.2453 | [+1.0729, +1.4281] | 0.0001 | 0.0018 |
| spbpe_5k | spuni_5k | 44 | exact_match_pct | -0.0552 | [-0.2231, +0.1142] | 0.5281 | 0.7265 |
| wp_5k | spuni_5k | 42 | chrf2_pct | +0.0782 | [+0.0648, +0.0920] | 0.0001 | 0.0018 |
| wp_5k | spuni_5k | 43 | chrf2_pct | +0.0827 | [+0.0675, +0.0977] | 0.0001 | 0.0018 |
| wp_5k | spuni_5k | 44 | chrf2_pct | -0.0835 | [-0.0962, -0.0699] | 0.0001 | 0.0018 |
| wp_5k | spuni_5k | 42 | exact_match_pct | +0.4507 | [+0.2858, +0.6223] | 0.0001 | 0.0018 |
| wp_5k | spuni_5k | 43 | exact_match_pct | +1.1699 | [+1.0020, +1.3423] | 0.0001 | 0.0018 |
| wp_5k | spuni_5k | 44 | exact_match_pct | +0.6976 | [+0.5312, +0.8774] | 0.0001 | 0.0018 |

## Category chrF2: 5K − 20K and condition − COPY (seed-mean, descriptive, unadjusted)

| Category | n | A | B | Δ chrF2 | 95% CI | Excludes 0 |
|---|---:|---|---|---:|---|---|
| afiksasi | 26322 | spbpe_5k | spbpe_20k | +0.1348 | [+0.1130, +0.1575] | yes |
| afiksasi | 26322 | wp_5k | wp_20k | +0.1527 | [+0.1286, +0.1786] | yes |
| afiksasi | 26322 | spuni_5k | spuni_20k | +0.0627 | [+0.0354, +0.0897] | yes |
| afiksasi | 26322 | spbpe_5k | COPY_INPUT | +13.9729 | [+13.8086, +14.1094] | yes |
| afiksasi | 26322 | spbpe_20k | COPY_INPUT | +13.8381 | [+13.6697, +13.9750] | yes |
| afiksasi | 26322 | wp_5k | COPY_INPUT | +13.9232 | [+13.7593, +14.0581] | yes |
| afiksasi | 26322 | wp_20k | COPY_INPUT | +13.7705 | [+13.6106, +13.9034] | yes |
| afiksasi | 26322 | spuni_5k | COPY_INPUT | +13.9100 | [+13.7522, +14.0450] | yes |
| afiksasi | 26322 | spuni_20k | COPY_INPUT | +13.8474 | [+13.6938, +13.9751] | yes |
| ambigu | 6603 | spbpe_5k | spbpe_20k | -0.0632 | [-0.1116, -0.0098] | yes |
| ambigu | 6603 | wp_5k | wp_20k | -0.0592 | [-0.1032, -0.0145] | yes |
| ambigu | 6603 | spuni_5k | spuni_20k | -0.0171 | [-0.0707, +0.0349] | no |
| ambigu | 6603 | spbpe_5k | COPY_INPUT | +1.6097 | [+1.4281, +1.7628] | yes |
| ambigu | 6603 | spbpe_20k | COPY_INPUT | +1.6729 | [+1.4800, +1.8318] | yes |
| ambigu | 6603 | wp_5k | COPY_INPUT | +1.6056 | [+1.4303, +1.7581] | yes |
| ambigu | 6603 | wp_20k | COPY_INPUT | +1.6648 | [+1.4820, +1.8218] | yes |
| ambigu | 6603 | spuni_5k | COPY_INPUT | +1.6511 | [+1.4759, +1.7964] | yes |
| ambigu | 6603 | spuni_20k | COPY_INPUT | +1.6683 | [+1.5061, +1.8078] | yes |
| ambigu_claude | 349 | spbpe_5k | spbpe_20k | -0.8683 | [-1.2309, -0.5388] | yes |
| ambigu_claude | 349 | wp_5k | wp_20k | -0.1716 | [-0.4810, +0.1450] | no |
| ambigu_claude | 349 | spuni_5k | spuni_20k | +0.0527 | [-0.3118, +0.3922] | no |
| ambigu_claude | 349 | spbpe_5k | COPY_INPUT | -1.7510 | [-2.2310, -1.2953] | yes |
| ambigu_claude | 349 | spbpe_20k | COPY_INPUT | -0.8827 | [-1.2357, -0.5514] | yes |
| ambigu_claude | 349 | wp_5k | COPY_INPUT | -1.3567 | [-1.7752, -0.9395] | yes |
| ambigu_claude | 349 | wp_20k | COPY_INPUT | -1.1851 | [-1.6109, -0.7637] | yes |
| ambigu_claude | 349 | spuni_5k | COPY_INPUT | -1.4442 | [-2.0226, -0.9200] | yes |
| ambigu_claude | 349 | spuni_20k | COPY_INPUT | -1.4969 | [-2.0182, -1.0005] | yes |
| diksi | 14123 | spbpe_5k | spbpe_20k | -0.3407 | [-0.3774, -0.3037] | yes |
| diksi | 14123 | wp_5k | wp_20k | -0.1822 | [-0.2146, -0.1500] | yes |
| diksi | 14123 | spuni_5k | spuni_20k | -0.1606 | [-0.1922, -0.1300] | yes |
| diksi | 14123 | spbpe_5k | COPY_INPUT | -1.2536 | [-1.3165, -1.1966] | yes |
| diksi | 14123 | spbpe_20k | COPY_INPUT | -0.9129 | [-0.9787, -0.8497] | yes |
| diksi | 14123 | wp_5k | COPY_INPUT | -1.1570 | [-1.2208, -1.1010] | yes |
| diksi | 14123 | wp_20k | COPY_INPUT | -0.9748 | [-1.0406, -0.9156] | yes |
| diksi | 14123 | spuni_5k | COPY_INPUT | -1.1520 | [-1.2146, -1.0929] | yes |
| diksi | 14123 | spuni_20k | COPY_INPUT | -0.9913 | [-1.0544, -0.9342] | yes |
| diksi_claude | 349 | spbpe_5k | spbpe_20k | -0.9555 | [-1.3856, -0.5367] | yes |
| diksi_claude | 349 | wp_5k | wp_20k | -0.4114 | [-0.7890, -0.0741] | yes |
| diksi_claude | 349 | spuni_5k | spuni_20k | +0.0273 | [-0.3040, +0.3727] | no |
| diksi_claude | 349 | spbpe_5k | COPY_INPUT | +0.5696 | [+0.0457, +1.1024] | yes |
| diksi_claude | 349 | spbpe_20k | COPY_INPUT | +1.5252 | [+1.0997, +1.9487] | yes |
| diksi_claude | 349 | wp_5k | COPY_INPUT | +0.9599 | [+0.4410, +1.4643] | yes |
| diksi_claude | 349 | wp_20k | COPY_INPUT | +1.3713 | [+0.8933, +1.8441] | yes |
| diksi_claude | 349 | spuni_5k | COPY_INPUT | +1.0488 | [+0.5513, +1.5444] | yes |
| diksi_claude | 349 | spuni_20k | COPY_INPUT | +1.0215 | [+0.4827, +1.5495] | yes |
| kelengkapan_kalimat | 15877 | spbpe_5k | spbpe_20k | -0.4139 | [-0.4495, -0.3767] | yes |
| kelengkapan_kalimat | 15877 | wp_5k | wp_20k | -0.1866 | [-0.2210, -0.1540] | yes |
| kelengkapan_kalimat | 15877 | spuni_5k | spuni_20k | -0.1611 | [-0.1932, -0.1304] | yes |
| kelengkapan_kalimat | 15877 | spbpe_5k | COPY_INPUT | -0.5765 | [-0.6433, -0.5169] | yes |
| kelengkapan_kalimat | 15877 | spbpe_20k | COPY_INPUT | -0.1625 | [-0.2308, -0.1021] | yes |
| kelengkapan_kalimat | 15877 | wp_5k | COPY_INPUT | -0.4246 | [-0.4926, -0.3670] | yes |
| kelengkapan_kalimat | 15877 | wp_20k | COPY_INPUT | -0.2380 | [-0.3071, -0.1785] | yes |
| kelengkapan_kalimat | 15877 | spuni_5k | COPY_INPUT | -0.4221 | [-0.4887, -0.3643] | yes |
| kelengkapan_kalimat | 15877 | spuni_20k | COPY_INPUT | -0.2610 | [-0.3221, -0.2071] | yes |
| pembentukan_kata | 16373 | spbpe_5k | spbpe_20k | +0.5799 | [+0.5525, +0.6083] | yes |
| pembentukan_kata | 16373 | wp_5k | wp_20k | +0.8503 | [+0.8182, +0.8813] | yes |
| pembentukan_kata | 16373 | spuni_5k | spuni_20k | +0.3877 | [+0.3641, +0.4127] | yes |
| pembentukan_kata | 16373 | spbpe_5k | COPY_INPUT | +13.3384 | [+13.1820, +13.4917] | yes |
| pembentukan_kata | 16373 | spbpe_20k | COPY_INPUT | +12.7585 | [+12.5932, +12.9084] | yes |
| pembentukan_kata | 16373 | wp_5k | COPY_INPUT | +13.3312 | [+13.1674, +13.4848] | yes |
| pembentukan_kata | 16373 | wp_20k | COPY_INPUT | +12.4809 | [+12.3226, +12.6307] | yes |
| pembentukan_kata | 16373 | spuni_5k | COPY_INPUT | +13.2950 | [+13.1352, +13.4457] | yes |
| pembentukan_kata | 16373 | spuni_20k | COPY_INPUT | +12.9073 | [+12.7500, +13.0579] | yes |
| pleonasme | 2717 | spbpe_5k | spbpe_20k | +0.1473 | [+0.0879, +0.2064] | yes |
| pleonasme | 2717 | wp_5k | wp_20k | +0.0822 | [+0.0199, +0.1401] | yes |
| pleonasme | 2717 | spuni_5k | spuni_20k | +0.1220 | [+0.0687, +0.1742] | yes |
| pleonasme | 2717 | spbpe_5k | COPY_INPUT | +2.7995 | [+2.6904, +2.9073] | yes |
| pleonasme | 2717 | spbpe_20k | COPY_INPUT | +2.6522 | [+2.5457, +2.7586] | yes |
| pleonasme | 2717 | wp_5k | COPY_INPUT | +2.7671 | [+2.6611, +2.8735] | yes |
| pleonasme | 2717 | wp_20k | COPY_INPUT | +2.6849 | [+2.5795, +2.7873] | yes |
| pleonasme | 2717 | spuni_5k | COPY_INPUT | +2.8211 | [+2.7135, +2.9241] | yes |
| pleonasme | 2717 | spuni_20k | COPY_INPUT | +2.6990 | [+2.5921, +2.8031] | yes |
| pleonasme_claude | 350 | spbpe_5k | spbpe_20k | -1.1557 | [-1.4980, -0.8509] | yes |
| pleonasme_claude | 350 | wp_5k | wp_20k | -0.0255 | [-0.4139, +0.3819] | no |
| pleonasme_claude | 350 | spuni_5k | spuni_20k | -0.3712 | [-0.6405, -0.1120] | yes |
| pleonasme_claude | 350 | spbpe_5k | COPY_INPUT | -2.4106 | [-2.8895, -1.9779] | yes |
| pleonasme_claude | 350 | spbpe_20k | COPY_INPUT | -1.2549 | [-1.5968, -0.9250] | yes |
| pleonasme_claude | 350 | wp_5k | COPY_INPUT | -1.8892 | [-2.3535, -1.4608] | yes |
| pleonasme_claude | 350 | wp_20k | COPY_INPUT | -1.8637 | [-2.3221, -1.4180] | yes |
| pleonasme_claude | 350 | spuni_5k | COPY_INPUT | -2.2597 | [-2.7138, -1.8557] | yes |
| pleonasme_claude | 350 | spuni_20k | COPY_INPUT | -1.8885 | [-2.3149, -1.4819] | yes |
| preposisi | 16774 | spbpe_5k | spbpe_20k | -0.1184 | [-0.1467, -0.0905] | yes |
| preposisi | 16774 | wp_5k | wp_20k | -0.1128 | [-0.1468, -0.0806] | yes |
| preposisi | 16774 | spuni_5k | spuni_20k | -0.0860 | [-0.1235, -0.0524] | yes |
| preposisi | 16774 | spbpe_5k | COPY_INPUT | +2.9312 | [+2.8128, +3.0308] | yes |
| preposisi | 16774 | spbpe_20k | COPY_INPUT | +3.0496 | [+2.9312, +3.1508] | yes |
| preposisi | 16774 | wp_5k | COPY_INPUT | +2.9250 | [+2.8035, +3.0264] | yes |
| preposisi | 16774 | wp_20k | COPY_INPUT | +3.0378 | [+2.9296, +3.1313] | yes |
| preposisi | 16774 | spuni_5k | COPY_INPUT | +2.9892 | [+2.8683, +3.0894] | yes |
| preposisi | 16774 | spuni_20k | COPY_INPUT | +3.0751 | [+2.9786, +3.1594] | yes |
| reduplikasi | 8927 | spbpe_5k | spbpe_20k | +0.1457 | [+0.1130, +0.1808] | yes |
| reduplikasi | 8927 | wp_5k | wp_20k | +0.1303 | [+0.0953, +0.1649] | yes |
| reduplikasi | 8927 | spuni_5k | spuni_20k | +0.1532 | [+0.1166, +0.1902] | yes |
| reduplikasi | 8927 | spbpe_5k | COPY_INPUT | +1.5417 | [+1.4314, +1.6365] | yes |
| reduplikasi | 8927 | spbpe_20k | COPY_INPUT | +1.3959 | [+1.2691, +1.5056] | yes |
| reduplikasi | 8927 | wp_5k | COPY_INPUT | +1.5304 | [+1.4153, +1.6260] | yes |
| reduplikasi | 8927 | wp_20k | COPY_INPUT | +1.4000 | [+1.2789, +1.5037] | yes |
| reduplikasi | 8927 | spuni_5k | COPY_INPUT | +1.5936 | [+1.4870, +1.6810] | yes |
| reduplikasi | 8927 | spuni_20k | COPY_INPUT | +1.4404 | [+1.3313, +1.5307] | yes |
| sintaksis_frasa | 25261 | spbpe_5k | spbpe_20k | +0.3333 | [+0.2981, +0.3682] | yes |
| sintaksis_frasa | 25261 | wp_5k | wp_20k | +0.5869 | [+0.5481, +0.6264] | yes |
| sintaksis_frasa | 25261 | spuni_5k | spuni_20k | +0.3461 | [+0.3110, +0.3824] | yes |
| sintaksis_frasa | 25261 | spbpe_5k | COPY_INPUT | +8.6221 | [+8.4825, +8.7548] | yes |
| sintaksis_frasa | 25261 | spbpe_20k | COPY_INPUT | +8.2888 | [+8.1535, +8.4199] | yes |
| sintaksis_frasa | 25261 | wp_5k | COPY_INPUT | +8.7354 | [+8.5951, +8.8709] | yes |
| sintaksis_frasa | 25261 | wp_20k | COPY_INPUT | +8.1484 | [+8.0205, +8.2761] | yes |
| sintaksis_frasa | 25261 | spuni_5k | COPY_INPUT | +8.5377 | [+8.3979, +8.6716] | yes |
| sintaksis_frasa | 25261 | spuni_20k | COPY_INPUT | +8.1916 | [+8.0621, +8.3177] | yes |

Interpretation limits: intervals are conditional on the trained checkpoints; they do not measure training-seed variance. Seed agreement (Seeds A>B) and the per-seed table carry that information separately.

Send back: REPORT.md, paired_overall.csv, paired_per_seed.csv, prob_best.csv, paired_categories.csv, provenance.json.
