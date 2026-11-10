# Step16 — paired statistics (M3) — frozen 10-epoch runs

All 20769 test rows; 19 systems (18 runs + COPY_INPUT). Stored scores reproduced exactly before resampling.
Bootstrap B=2000 (stratified by category; cluster variant over 20769 identical-reference clusters). Approximate randomization R=10000.

## Primary comparisons, seed-mean (A − B)

| A | B | Metric | Δ | 95% CI | Cluster 95% CI | p (AR) | p (Holm) | Seeds A>B |
|---|---|---|---:|---|---|---:|---:|---:|
| spbpe_5k | spbpe_20k | chrf2_pct | +0.5501 | [+0.5033, +0.6021] | [+0.5035, +0.6016] | 0.0001 | 0.0006 | 3/3 |
| spbpe_5k | spbpe_20k | bleu | +1.2860 | [+1.1953, +1.3792] | [+1.1948, +1.3786] | 0.0001 | 0.0006 | 3/3 |
| spbpe_5k | spbpe_20k | exact_match_pct | +4.9352 | [+4.6094, +5.2565] | [+4.6159, +5.2692] | 0.0001 | 0.0006 | 3/3 |
| wp_5k | wp_20k | chrf2_pct | +0.7203 | [+0.6616, +0.7849] | [+0.6588, +0.7832] | 0.0001 | 0.0006 | 3/3 |
| wp_5k | wp_20k | bleu | +1.5549 | [+1.4511, +1.6640] | [+1.4455, +1.6661] | 0.0001 | 0.0006 | 3/3 |
| wp_5k | wp_20k | exact_match_pct | +5.7522 | [+5.3943, +6.1117] | [+5.3975, +6.1261] | 0.0001 | 0.0006 | 3/3 |
| spuni_5k | spuni_20k | chrf2_pct | +0.6591 | [+0.6017, +0.7200] | [+0.6028, +0.7173] | 0.0001 | 0.0006 | 3/3 |
| spuni_5k | spuni_20k | bleu | +1.3905 | [+1.2869, +1.4907] | [+1.2841, +1.4940] | 0.0001 | 0.0006 | 3/3 |
| spuni_5k | spuni_20k | exact_match_pct | +4.8101 | [+4.4521, +5.1408] | [+4.4538, +5.1519] | 0.0001 | 0.0006 | 3/3 |
| spbpe_5k | wp_5k | chrf2_pct | +0.0301 | [+0.0106, +0.0498] | [+0.0118, +0.0493] | 0.0024 | 0.0024 | 3/3 |
| spbpe_5k | wp_5k | bleu | +0.0183 | [-0.0470, +0.0835] | [-0.0466, +0.0859] | 0.5836 | 0.5836 | 2/3 |
| spbpe_5k | wp_5k | exact_match_pct | -0.3290 | [-0.5986, -0.0626] | [-0.5986, -0.0353] | 0.0206 | 0.0206 | 0/3 |
| spbpe_5k | spuni_5k | chrf2_pct | +0.1282 | [+0.1000, +0.1586] | [+0.0984, +0.1580] | 0.0001 | 0.0006 | 3/3 |
| spbpe_5k | spuni_5k | bleu | +0.2945 | [+0.2204, +0.3676] | [+0.2200, +0.3713] | 0.0001 | 0.0006 | 3/3 |
| spbpe_5k | spuni_5k | exact_match_pct | +0.7158 | [+0.4108, +1.0128] | [+0.4219, +1.0193] | 0.0001 | 0.0006 | 3/3 |
| wp_5k | spuni_5k | chrf2_pct | +0.0980 | [+0.0683, +0.1289] | [+0.0686, +0.1268] | 0.0001 | 0.0006 | 3/3 |
| wp_5k | spuni_5k | bleu | +0.2761 | [+0.2042, +0.3474] | [+0.2021, +0.3503] | 0.0001 | 0.0006 | 3/3 |
| wp_5k | spuni_5k | exact_match_pct | +1.0448 | [+0.7591, +1.3097] | [+0.7671, +1.3418] | 0.0001 | 0.0006 | 3/3 |

## Family x vocabulary interaction: (A5K − A20K) − (B5K − B20K), seed-mean

| A | B | Metric | Interaction | 95% CI | p (boot) | Seeds > 0 |
|---|---|---|---:|---|---:|---:|
| spbpe | spuni | chrf2_pct | -0.1090 | [-0.1708, -0.0428] | 0.0010 | 1/3 |
| spbpe | spuni | bleu | -0.1044 | [-0.2230, +0.0175] | 0.0920 | 2/3 |
| spbpe | spuni | exact_match_pct | +0.1252 | [-0.3002, +0.5698] | 0.5920 | 1/3 |
| wp | spuni | chrf2_pct | +0.0612 | [-0.0064, +0.1299] | 0.0710 | 2/3 |
| wp | spuni | bleu | +0.1645 | [+0.0438, +0.2918] | 0.0110 | 2/3 |
| wp | spuni | exact_match_pct | +0.9421 | [+0.4959, +1.3867] | 0.0000 | 2/3 |
| spbpe | wp | chrf2_pct | -0.1702 | [-0.2200, -0.1227] | 0.0000 | 1/3 |
| spbpe | wp | bleu | -0.2689 | [-0.3729, -0.1620] | 0.0010 | 1/3 |
| spbpe | wp | exact_match_pct | -0.8169 | [-1.2166, -0.4060] | 0.0010 | 1/3 |

## Probability of highest seed-mean score (bootstrap)

| Budget | Metric | Tag | Seed-mean | P(best) |
|---|---|---|---:|---:|
| 5k | chrf2_pct | spbpe_5k | 99.4592 | 0.999 |
| 5k | chrf2_pct | wp_5k | 99.4290 | 0.001 |
| 5k | chrf2_pct | spuni_5k | 99.3310 | 0.000 |
| 5k | bleu | spbpe_5k | 97.5828 | 0.712 |
| 5k | bleu | wp_5k | 97.5644 | 0.288 |
| 5k | bleu | spuni_5k | 97.2883 | 0.000 |
| 5k | exact_match_pct | spbpe_5k | 89.3720 | 0.006 |
| 5k | exact_match_pct | wp_5k | 89.7010 | 0.994 |
| 5k | exact_match_pct | spuni_5k | 88.6562 | 0.000 |
| 20k | chrf2_pct | spbpe_20k | 98.9090 | 1.000 |
| 20k | chrf2_pct | wp_20k | 98.7087 | 0.000 |
| 20k | chrf2_pct | spuni_20k | 98.6719 | 0.000 |
| 20k | bleu | spbpe_20k | 96.2967 | 1.000 |
| 20k | bleu | wp_20k | 96.0095 | 0.000 |
| 20k | bleu | spuni_20k | 95.8978 | 0.000 |
| 20k | exact_match_pct | spbpe_20k | 84.4367 | 0.996 |
| 20k | exact_match_pct | wp_20k | 83.9488 | 0.003 |
| 20k | exact_match_pct | spuni_20k | 83.8461 | 0.002 |

## Per-seed primary tests (chrF2 and exact match)

| A | B | Seed | Metric | Δ | 95% CI | p (AR) | p (Holm, 18) |
|---|---|---:|---|---:|---|---:|---:|
| spbpe_5k | spbpe_20k | 42 | chrf2_pct | +0.5816 | [+0.5264, +0.6411] | 0.0001 | 0.0018 |
| spbpe_5k | spbpe_20k | 43 | chrf2_pct | +0.4412 | [+0.3852, +0.5059] | 0.0001 | 0.0018 |
| spbpe_5k | spbpe_20k | 44 | chrf2_pct | +0.6276 | [+0.5570, +0.7030] | 0.0001 | 0.0018 |
| spbpe_5k | spbpe_20k | 42 | exact_match_pct | +7.8001 | [+7.3090, +8.2816] | 0.0001 | 0.0018 |
| spbpe_5k | spbpe_20k | 43 | exact_match_pct | +3.1537 | [+2.7442, +3.5584] | 0.0001 | 0.0018 |
| spbpe_5k | spbpe_20k | 44 | exact_match_pct | +3.8519 | [+3.4137, +4.2854] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 42 | chrf2_pct | +0.4760 | [+0.4122, +0.5485] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 43 | chrf2_pct | +0.7477 | [+0.6755, +0.8248] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 44 | chrf2_pct | +0.9372 | [+0.8500, +1.0280] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 42 | exact_match_pct | +2.7011 | [+2.2869, +3.1297] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 43 | exact_match_pct | +5.1038 | [+4.6366, +5.5468] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 44 | exact_match_pct | +9.4516 | [+8.9364, +9.9475] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 42 | chrf2_pct | +0.7293 | [+0.6424, +0.8187] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 43 | chrf2_pct | +0.7338 | [+0.6394, +0.8312] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 44 | chrf2_pct | +0.5141 | [+0.4473, +0.5800] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 42 | exact_match_pct | +4.8823 | [+4.4345, +5.3541] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 43 | exact_match_pct | +4.6560 | [+4.1599, +5.1134] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 44 | exact_match_pct | +4.8919 | [+4.4249, +5.3782] | 0.0001 | 0.0018 |
| spbpe_5k | wp_5k | 42 | chrf2_pct | +0.0354 | [+0.0126, +0.0590] | 0.0032 | 0.0096 |
| spbpe_5k | wp_5k | 43 | chrf2_pct | +0.0222 | [-0.0134, +0.0581] | 0.2187 | 0.2187 |
| spbpe_5k | wp_5k | 44 | chrf2_pct | +0.0328 | [+0.0036, +0.0624] | 0.0241 | 0.0482 |
| spbpe_5k | wp_5k | 42 | exact_match_pct | -0.2456 | [-0.6019, +0.1107] | 0.2084 | 0.4168 |
| spbpe_5k | wp_5k | 43 | exact_match_pct | -0.5874 | [-0.9440, -0.2215] | 0.0022 | 0.0110 |
| spbpe_5k | wp_5k | 44 | exact_match_pct | -0.1541 | [-0.5249, +0.2070] | 0.4332 | 0.4332 |
| spbpe_5k | spuni_5k | 42 | chrf2_pct | +0.1161 | [+0.0783, +0.1580] | 0.0001 | 0.0018 |
| spbpe_5k | spuni_5k | 43 | chrf2_pct | +0.1437 | [+0.1000, +0.1905] | 0.0001 | 0.0018 |
| spbpe_5k | spuni_5k | 44 | chrf2_pct | +0.1247 | [+0.0810, +0.1664] | 0.0001 | 0.0018 |
| spbpe_5k | spuni_5k | 42 | exact_match_pct | +0.8859 | [+0.4767, +1.2808] | 0.0001 | 0.0018 |
| spbpe_5k | spuni_5k | 43 | exact_match_pct | +0.8474 | [+0.4525, +1.2520] | 0.0002 | 0.0018 |
| spbpe_5k | spuni_5k | 44 | exact_match_pct | +0.4141 | [+0.0000, +0.7994] | 0.0435 | 0.1305 |
| wp_5k | spuni_5k | 42 | chrf2_pct | +0.0807 | [+0.0431, +0.1221] | 0.0001 | 0.0018 |
| wp_5k | spuni_5k | 43 | chrf2_pct | +0.1215 | [+0.0794, +0.1686] | 0.0001 | 0.0018 |
| wp_5k | spuni_5k | 44 | chrf2_pct | +0.0919 | [+0.0450, +0.1373] | 0.0002 | 0.0018 |
| wp_5k | spuni_5k | 42 | exact_match_pct | +1.1315 | [+0.7559, +1.5119] | 0.0001 | 0.0018 |
| wp_5k | spuni_5k | 43 | exact_match_pct | +1.4348 | [+1.0111, +1.8009] | 0.0001 | 0.0018 |
| wp_5k | spuni_5k | 44 | exact_match_pct | +0.5682 | [+0.2021, +0.9294] | 0.0035 | 0.0140 |

## Category chrF2: 5K − 20K and condition − COPY (seed-mean, descriptive, unadjusted)

| Category | n | A | B | Δ chrF2 | 95% CI | Excludes 0 |
|---|---:|---|---|---:|---|---|
| multi | 3082 | spbpe_5k | spbpe_20k | +0.8889 | [+0.7656, +1.0205] | yes |
| multi | 3082 | wp_5k | wp_20k | +1.0558 | [+0.9154, +1.2169] | yes |
| multi | 3082 | spuni_5k | spuni_20k | +1.0209 | [+0.8680, +1.1929] | yes |
| multi | 3082 | spbpe_5k | COPY_INPUT | +1.2090 | [+0.9465, +1.4516] | yes |
| multi | 3082 | spbpe_20k | COPY_INPUT | +0.3202 | [-0.0178, +0.6356] | no |
| multi | 3082 | wp_5k | COPY_INPUT | +1.1231 | [+0.8466, +1.3778] | yes |
| multi | 3082 | wp_20k | COPY_INPUT | +0.0672 | [-0.3042, +0.4158] | no |
| multi | 3082 | spuni_5k | COPY_INPUT | +1.0022 | [+0.7183, +1.2592] | yes |
| multi | 3082 | spuni_20k | COPY_INPUT | -0.0187 | [-0.3705, +0.2962] | no |
| none | 10457 | spbpe_5k | spbpe_20k | +0.3515 | [+0.2989, +0.4068] | yes |
| none | 10457 | wp_5k | wp_20k | +0.5462 | [+0.4690, +0.6308] | yes |
| none | 10457 | spuni_5k | spuni_20k | +0.4764 | [+0.3957, +0.5604] | yes |
| none | 10457 | spbpe_5k | COPY_INPUT | -0.1686 | [-0.2446, -0.1131] | yes |
| none | 10457 | spbpe_20k | COPY_INPUT | -0.5201 | [-0.6182, -0.4394] | yes |
| none | 10457 | wp_5k | COPY_INPUT | -0.1819 | [-0.2489, -0.1314] | yes |
| none | 10457 | wp_20k | COPY_INPUT | -0.7281 | [-0.8464, -0.6308] | yes |
| none | 10457 | spuni_5k | COPY_INPUT | -0.2433 | [-0.3276, -0.1802] | yes |
| none | 10457 | spuni_20k | COPY_INPUT | -0.7198 | [-0.8393, -0.6136] | yes |
| rule_1 | 975 | spbpe_5k | spbpe_20k | +0.6908 | [+0.3871, +1.1501] | yes |
| rule_1 | 975 | wp_5k | wp_20k | +0.6096 | [+0.3228, +1.0592] | yes |
| rule_1 | 975 | spuni_5k | spuni_20k | +0.5380 | [+0.3147, +0.7964] | yes |
| rule_1 | 975 | spbpe_5k | COPY_INPUT | -0.3096 | [-0.6449, -0.1182] | yes |
| rule_1 | 975 | spbpe_20k | COPY_INPUT | -1.0003 | [-1.6176, -0.5418] | yes |
| rule_1 | 975 | wp_5k | COPY_INPUT | -0.2877 | [-0.6382, -0.0883] | yes |
| rule_1 | 975 | wp_20k | COPY_INPUT | -0.8973 | [-1.4971, -0.4622] | yes |
| rule_1 | 975 | spuni_5k | COPY_INPUT | -0.2868 | [-0.6361, -0.0934] | yes |
| rule_1 | 975 | spuni_20k | COPY_INPUT | -0.8248 | [-1.3960, -0.4447] | yes |
| rule_10 | 29 | spbpe_5k | spbpe_20k | +1.6508 | [+0.4616, +2.9205] | yes |
| rule_10 | 29 | wp_5k | wp_20k | +2.5995 | [+0.5528, +3.9628] | yes |
| rule_10 | 29 | spuni_5k | spuni_20k | +1.6440 | [+0.0472, +3.1158] | yes |
| rule_10 | 29 | spbpe_5k | COPY_INPUT | -9.7261 | [-20.2462, -0.0540] | yes |
| rule_10 | 29 | spbpe_20k | COPY_INPUT | -11.3769 | [-22.1568, -0.6762] | yes |
| rule_10 | 29 | wp_5k | COPY_INPUT | -9.8742 | [-20.3074, -0.1846] | yes |
| rule_10 | 29 | wp_20k | COPY_INPUT | -12.4737 | [-23.8497, -0.8563] | yes |
| rule_10 | 29 | spuni_5k | COPY_INPUT | -10.1649 | [-22.0787, -0.3167] | yes |
| rule_10 | 29 | spuni_20k | COPY_INPUT | -11.8090 | [-24.1928, -0.5547] | yes |
| rule_11 | 492 | spbpe_5k | spbpe_20k | +0.5015 | [+0.3173, +0.7043] | yes |
| rule_11 | 492 | wp_5k | wp_20k | +0.4519 | [+0.2500, +0.6995] | yes |
| rule_11 | 492 | spuni_5k | spuni_20k | +0.4156 | [+0.2147, +0.6489] | yes |
| rule_11 | 492 | spbpe_5k | COPY_INPUT | -0.3368 | [-0.4600, -0.2255] | yes |
| rule_11 | 492 | spbpe_20k | COPY_INPUT | -0.8384 | [-1.0744, -0.6290] | yes |
| rule_11 | 492 | wp_5k | COPY_INPUT | -0.1075 | [-0.1657, -0.0581] | yes |
| rule_11 | 492 | wp_20k | COPY_INPUT | -0.5594 | [-0.8038, -0.3601] | yes |
| rule_11 | 492 | spuni_5k | COPY_INPUT | -0.2307 | [-0.4192, -0.0933] | yes |
| rule_11 | 492 | spuni_20k | COPY_INPUT | -0.6462 | [-0.9241, -0.4036] | yes |
| rule_12 | 743 | spbpe_5k | spbpe_20k | +0.7636 | [+0.4951, +1.0975] | yes |
| rule_12 | 743 | wp_5k | wp_20k | +1.2737 | [+0.7854, +1.9013] | yes |
| rule_12 | 743 | spuni_5k | spuni_20k | +1.3056 | [+0.8789, +1.7756] | yes |
| rule_12 | 743 | spbpe_5k | COPY_INPUT | +3.9314 | [+3.5072, +4.2836] | yes |
| rule_12 | 743 | spbpe_20k | COPY_INPUT | +3.1678 | [+2.5163, +3.7129] | yes |
| rule_12 | 743 | wp_5k | COPY_INPUT | +3.8489 | [+3.4142, +4.2058] | yes |
| rule_12 | 743 | wp_20k | COPY_INPUT | +2.5752 | [+1.6813, +3.3111] | yes |
| rule_12 | 743 | spuni_5k | COPY_INPUT | +3.4901 | [+2.9615, +3.9191] | yes |
| rule_12 | 743 | spuni_20k | COPY_INPUT | +2.1845 | [+1.3792, +2.8266] | yes |
| rule_13 | 95 | spbpe_5k | spbpe_20k | +0.2801 | [-0.2604, +0.9450] | no |
| rule_13 | 95 | wp_5k | wp_20k | +0.9035 | [+0.1340, +1.9057] | yes |
| rule_13 | 95 | spuni_5k | spuni_20k | -0.2122 | [-0.5241, +0.1013] | no |
| rule_13 | 95 | spbpe_5k | COPY_INPUT | +1.2875 | [+0.2885, +2.0510] | yes |
| rule_13 | 95 | spbpe_20k | COPY_INPUT | +1.0075 | [-0.5790, +2.1731] | no |
| rule_13 | 95 | wp_5k | COPY_INPUT | +1.5585 | [+0.4099, +2.4574] | yes |
| rule_13 | 95 | wp_20k | COPY_INPUT | +0.6550 | [-1.3146, +1.9673] | no |
| rule_13 | 95 | spuni_5k | COPY_INPUT | +1.3616 | [+0.5776, +1.9777] | yes |
| rule_13 | 95 | spuni_20k | COPY_INPUT | +1.5738 | [+0.7605, +2.2758] | yes |
| rule_14 | 68 | spbpe_5k | spbpe_20k | +0.6666 | [+0.1324, +1.2938] | yes |
| rule_14 | 68 | wp_5k | wp_20k | -0.2375 | [-0.6608, +0.1993] | no |
| rule_14 | 68 | spuni_5k | spuni_20k | +0.0874 | [-0.8547, +1.5210] | no |
| rule_14 | 68 | spbpe_5k | COPY_INPUT | +4.1574 | [+3.5736, +4.8563] | yes |
| rule_14 | 68 | spbpe_20k | COPY_INPUT | +3.4909 | [+2.7366, +4.2747] | yes |
| rule_14 | 68 | wp_5k | COPY_INPUT | +4.0622 | [+3.5193, +4.7320] | yes |
| rule_14 | 68 | wp_20k | COPY_INPUT | +4.2997 | [+3.7246, +4.9678] | yes |
| rule_14 | 68 | spuni_5k | COPY_INPUT | +3.9575 | [+3.4422, +4.5952] | yes |
| rule_14 | 68 | spuni_20k | COPY_INPUT | +3.8701 | [+2.3945, +5.0074] | yes |
| rule_15 | 17 | spbpe_5k | spbpe_20k | -0.0849 | [-1.1151, +0.5774] | no |
| rule_15 | 17 | wp_5k | wp_20k | +0.4566 | [-0.6761, +1.7237] | no |
| rule_15 | 17 | spuni_5k | spuni_20k | -0.0147 | [-1.0294, +0.7822] | no |
| rule_15 | 17 | spbpe_5k | COPY_INPUT | +0.0000 | [+0.0000, +0.0000] | no |
| rule_15 | 17 | spbpe_20k | COPY_INPUT | +0.0849 | [-0.5774, +1.1151] | no |
| rule_15 | 17 | wp_5k | COPY_INPUT | +0.0000 | [-0.3572, +0.3758] | no |
| rule_15 | 17 | wp_20k | COPY_INPUT | -0.4566 | [-1.7040, +0.6334] | no |
| rule_15 | 17 | spuni_5k | COPY_INPUT | +0.0044 | [+0.0000, +0.0152] | no |
| rule_15 | 17 | spuni_20k | COPY_INPUT | +0.0191 | [-0.7768, +1.0345] | no |
| rule_16 | 21 | spbpe_5k | spbpe_20k | +0.7545 | [+0.1205, +1.4337] | yes |
| rule_16 | 21 | wp_5k | wp_20k | +1.0395 | [-0.1035, +2.4566] | no |
| rule_16 | 21 | spuni_5k | spuni_20k | +0.0526 | [-2.6953, +3.7256] | no |
| rule_16 | 21 | spbpe_5k | COPY_INPUT | +3.6739 | [+2.5138, +5.3326] | yes |
| rule_16 | 21 | spbpe_20k | COPY_INPUT | +2.9194 | [+1.5558, +4.7420] | yes |
| rule_16 | 21 | wp_5k | COPY_INPUT | +1.6730 | [-0.1656, +3.6050] | no |
| rule_16 | 21 | wp_20k | COPY_INPUT | +0.6335 | [-1.5194, +3.0385] | no |
| rule_16 | 21 | spuni_5k | COPY_INPUT | +1.3144 | [+0.3978, +2.5811] | yes |
| rule_16 | 21 | spuni_20k | COPY_INPUT | +1.2618 | [-2.0759, +4.0744] | no |
| rule_17 | 26 | spbpe_5k | spbpe_20k | +1.5475 | [+0.2668, +3.3871] | yes |
| rule_17 | 26 | wp_5k | wp_20k | +3.0176 | [+1.8361, +4.3161] | yes |
| rule_17 | 26 | spuni_5k | spuni_20k | -0.0170 | [-0.9611, +0.8793] | no |
| rule_17 | 26 | spbpe_5k | COPY_INPUT | -0.8478 | [-1.4838, -0.3388] | yes |
| rule_17 | 26 | spbpe_20k | COPY_INPUT | -2.3954 | [-4.2779, -1.0632] | yes |
| rule_17 | 26 | wp_5k | COPY_INPUT | -0.2362 | [-0.6226, +0.0000] | no |
| rule_17 | 26 | wp_20k | COPY_INPUT | -3.2538 | [-4.5375, -2.0718] | yes |
| rule_17 | 26 | spuni_5k | COPY_INPUT | -1.0439 | [-1.9031, -0.3356] | yes |
| rule_17 | 26 | spuni_20k | COPY_INPUT | -1.0269 | [-1.7391, -0.4040] | yes |
| rule_18 | 31 | spbpe_5k | spbpe_20k | -0.2956 | [-0.8993, +0.2646] | no |
| rule_18 | 31 | wp_5k | wp_20k | +0.7247 | [-0.2223, +1.7738] | no |
| rule_18 | 31 | spuni_5k | spuni_20k | +1.2960 | [+0.3883, +2.5956] | yes |
| rule_18 | 31 | spbpe_5k | COPY_INPUT | +4.1273 | [+3.2014, +5.3123] | yes |
| rule_18 | 31 | spbpe_20k | COPY_INPUT | +4.4229 | [+3.4147, +5.6814] | yes |
| rule_18 | 31 | wp_5k | COPY_INPUT | +3.5985 | [+2.5923, +4.8742] | yes |
| rule_18 | 31 | wp_20k | COPY_INPUT | +2.8737 | [+1.7036, +4.1974] | yes |
| rule_18 | 31 | spuni_5k | COPY_INPUT | +4.0569 | [+3.0762, +5.3142] | yes |
| rule_18 | 31 | spuni_20k | COPY_INPUT | +2.7609 | [+1.5274, +4.0317] | yes |
| rule_2 | 3 | spbpe_5k | spbpe_20k | +0.0000 | [+0.0000, +0.0000] | no |
| rule_2 | 3 | wp_5k | wp_20k | +0.0000 | [+0.0000, +0.0000] | no |
| rule_2 | 3 | spuni_5k | spuni_20k | +0.0000 | [+0.0000, +0.0000] | no |
| rule_2 | 3 | spbpe_5k | COPY_INPUT | +0.0000 | [+0.0000, +0.0000] | no |
| rule_2 | 3 | spbpe_20k | COPY_INPUT | +0.0000 | [+0.0000, +0.0000] | no |
| rule_2 | 3 | wp_5k | COPY_INPUT | +0.0000 | [+0.0000, +0.0000] | no |
| rule_2 | 3 | wp_20k | COPY_INPUT | +0.0000 | [+0.0000, +0.0000] | no |
| rule_2 | 3 | spuni_5k | COPY_INPUT | +0.0000 | [+0.0000, +0.0000] | no |
| rule_2 | 3 | spuni_20k | COPY_INPUT | +0.0000 | [+0.0000, +0.0000] | no |
| rule_20 | 467 | spbpe_5k | spbpe_20k | +0.5218 | [+0.3170, +0.7545] | yes |
| rule_20 | 467 | wp_5k | wp_20k | +0.6461 | [+0.3852, +0.9450] | yes |
| rule_20 | 467 | spuni_5k | spuni_20k | +0.6269 | [+0.3762, +0.9082] | yes |
| rule_20 | 467 | spbpe_5k | COPY_INPUT | -0.2645 | [-0.3577, -0.1826] | yes |
| rule_20 | 467 | spbpe_20k | COPY_INPUT | -0.7863 | [-1.0059, -0.5913] | yes |
| rule_20 | 467 | wp_5k | COPY_INPUT | -0.2695 | [-0.3593, -0.1811] | yes |
| rule_20 | 467 | wp_20k | COPY_INPUT | -0.9156 | [-1.2536, -0.6367] | yes |
| rule_20 | 467 | spuni_5k | COPY_INPUT | -0.3847 | [-0.5405, -0.2536] | yes |
| rule_20 | 467 | spuni_20k | COPY_INPUT | -1.0116 | [-1.2824, -0.7721] | yes |
| rule_21 | 6 | spbpe_5k | spbpe_20k | +1.5512 | [+0.6172, +2.5627] | yes |
| rule_21 | 6 | wp_5k | wp_20k | +2.8774 | [+0.3276, +7.8214] | yes |
| rule_21 | 6 | spuni_5k | spuni_20k | +0.1679 | [-0.8645, +1.0720] | no |
| rule_21 | 6 | spbpe_5k | COPY_INPUT | +0.0000 | [+0.0000, +0.0000] | no |
| rule_21 | 6 | spbpe_20k | COPY_INPUT | -1.5512 | [-2.5627, -0.6172] | yes |
| rule_21 | 6 | wp_5k | COPY_INPUT | +0.0000 | [+0.0000, +0.0000] | no |
| rule_21 | 6 | wp_20k | COPY_INPUT | -2.8774 | [-7.8214, -0.3276] | yes |
| rule_21 | 6 | spuni_5k | COPY_INPUT | -0.3447 | [-1.1065, +0.0000] | no |
| rule_21 | 6 | spuni_20k | COPY_INPUT | -0.5126 | [-1.1745, +0.0000] | no |
| rule_22 | 253 | spbpe_5k | spbpe_20k | +0.4005 | [+0.0809, +0.8899] | yes |
| rule_22 | 253 | wp_5k | wp_20k | +0.3492 | [-0.0197, +0.9149] | no |
| rule_22 | 253 | spuni_5k | spuni_20k | +0.3444 | [+0.0906, +0.7147] | yes |
| rule_22 | 253 | spbpe_5k | COPY_INPUT | -0.3168 | [-0.7795, -0.0496] | yes |
| rule_22 | 253 | spbpe_20k | COPY_INPUT | -0.7172 | [-1.6229, -0.1789] | yes |
| rule_22 | 253 | wp_5k | COPY_INPUT | -0.3433 | [-0.7425, -0.0919] | yes |
| rule_22 | 253 | wp_20k | COPY_INPUT | -0.6926 | [-1.6292, -0.1562] | yes |
| rule_22 | 253 | spuni_5k | COPY_INPUT | -0.3188 | [-0.7721, -0.0574] | yes |
| rule_22 | 253 | spuni_20k | COPY_INPUT | -0.6632 | [-1.4550, -0.1899] | yes |
| rule_23 | 217 | spbpe_5k | spbpe_20k | +0.2205 | [-0.0284, +0.4798] | no |
| rule_23 | 217 | wp_5k | wp_20k | -0.0472 | [-0.3859, +0.2880] | no |
| rule_23 | 217 | spuni_5k | spuni_20k | +0.2454 | [-0.1030, +0.6441] | no |
| rule_23 | 217 | spbpe_5k | COPY_INPUT | +0.3576 | [+0.0991, +0.5984] | yes |
| rule_23 | 217 | spbpe_20k | COPY_INPUT | +0.1371 | [-0.1564, +0.4082] | no |
| rule_23 | 217 | wp_5k | COPY_INPUT | +0.1287 | [-0.1731, +0.3916] | no |
| rule_23 | 217 | wp_20k | COPY_INPUT | +0.1759 | [-0.1315, +0.4624] | no |
| rule_23 | 217 | spuni_5k | COPY_INPUT | +0.2031 | [-0.0541, +0.4534] | no |
| rule_23 | 217 | spuni_20k | COPY_INPUT | -0.0422 | [-0.4282, +0.2818] | no |
| rule_24 | 50 | spbpe_5k | spbpe_20k | +0.3825 | [-0.2416, +0.9989] | no |
| rule_24 | 50 | wp_5k | wp_20k | +0.1055 | [-1.4375, +1.5719] | no |
| rule_24 | 50 | spuni_5k | spuni_20k | +1.1871 | [+0.2001, +2.2636] | yes |
| rule_24 | 50 | spbpe_5k | COPY_INPUT | +0.3550 | [-2.8434, +2.7585] | no |
| rule_24 | 50 | spbpe_20k | COPY_INPUT | -0.0275 | [-3.4425, +2.4868] | no |
| rule_24 | 50 | wp_5k | COPY_INPUT | -0.5542 | [-3.1336, +1.1751] | no |
| rule_24 | 50 | wp_20k | COPY_INPUT | -0.6597 | [-4.0320, +2.1901] | no |
| rule_24 | 50 | spuni_5k | COPY_INPUT | +0.9334 | [-1.7783, +3.1093] | no |
| rule_24 | 50 | spuni_20k | COPY_INPUT | -0.2537 | [-3.7651, +2.2740] | no |
| rule_25 | 12 | spbpe_5k | spbpe_20k | +0.9792 | [+0.0295, +2.4626] | yes |
| rule_25 | 12 | wp_5k | wp_20k | -0.2385 | [-1.4287, +0.6077] | no |
| rule_25 | 12 | spuni_5k | spuni_20k | +0.1651 | [-1.3807, +1.3705] | no |
| rule_25 | 12 | spbpe_5k | COPY_INPUT | +2.9840 | [+1.7823, +4.5837] | yes |
| rule_25 | 12 | spbpe_20k | COPY_INPUT | +2.0048 | [+0.4300, +4.0113] | yes |
| rule_25 | 12 | wp_5k | COPY_INPUT | +2.0526 | [+0.9178, +3.5585] | yes |
| rule_25 | 12 | wp_20k | COPY_INPUT | +2.2910 | [+1.2389, +3.9563] | yes |
| rule_25 | 12 | spuni_5k | COPY_INPUT | +2.0115 | [+0.7360, +3.8298] | yes |
| rule_25 | 12 | spuni_20k | COPY_INPUT | +1.8464 | [+0.4575, +3.6122] | yes |
| rule_3 | 7 | spbpe_5k | spbpe_20k | +1.6218 | [+0.4309, +3.1165] | yes |
| rule_3 | 7 | wp_5k | wp_20k | -0.2027 | [-0.7652, +0.0000] | no |
| rule_3 | 7 | spuni_5k | spuni_20k | +0.6082 | [-0.3700, +2.1528] | no |
| rule_3 | 7 | spbpe_5k | COPY_INPUT | +2.2300 | [+0.9810, +4.5712] | yes |
| rule_3 | 7 | spbpe_20k | COPY_INPUT | +0.6082 | [+0.1320, +1.8849] | yes |
| rule_3 | 7 | wp_5k | COPY_INPUT | +0.2027 | [+0.0000, +0.7652] | no |
| rule_3 | 7 | wp_20k | COPY_INPUT | +0.4055 | [+0.0000, +1.5304] | no |
| rule_3 | 7 | spuni_5k | COPY_INPUT | +1.6218 | [+0.3354, +4.3537] | yes |
| rule_3 | 7 | spuni_20k | COPY_INPUT | +1.0136 | [+0.1373, +2.8879] | yes |
| rule_4 | 22 | spbpe_5k | spbpe_20k | +0.1020 | [-0.2382, +0.4740] | no |
| rule_4 | 22 | wp_5k | wp_20k | +0.4277 | [+0.0000, +1.1285] | no |
| rule_4 | 22 | spuni_5k | spuni_20k | -0.3841 | [-0.9123, +0.0620] | no |
| rule_4 | 22 | spbpe_5k | COPY_INPUT | -0.2121 | [-0.4018, -0.0189] | yes |
| rule_4 | 22 | spbpe_20k | COPY_INPUT | -0.3141 | [-0.7441, +0.0000] | no |
| rule_4 | 22 | wp_5k | COPY_INPUT | -0.1362 | [-0.4125, +0.0000] | no |
| rule_4 | 22 | wp_20k | COPY_INPUT | -0.5639 | [-1.3267, +0.0000] | no |
| rule_4 | 22 | spuni_5k | COPY_INPUT | -0.6729 | [-1.4061, -0.0687] | yes |
| rule_4 | 22 | spuni_20k | COPY_INPUT | -0.2889 | [-0.7039, +0.0000] | no |
| rule_5 | 821 | spbpe_5k | spbpe_20k | +0.2963 | [+0.1171, +0.5021] | yes |
| rule_5 | 821 | wp_5k | wp_20k | +0.4733 | [+0.3149, +0.6575] | yes |
| rule_5 | 821 | spuni_5k | spuni_20k | +0.3702 | [+0.1334, +0.6480] | yes |
| rule_5 | 821 | spbpe_5k | COPY_INPUT | +3.5046 | [+3.0169, +3.9067] | yes |
| rule_5 | 821 | spbpe_20k | COPY_INPUT | +3.2082 | [+2.7103, +3.6343] | yes |
| rule_5 | 821 | wp_5k | COPY_INPUT | +3.5852 | [+3.1350, +3.9677] | yes |
| rule_5 | 821 | wp_20k | COPY_INPUT | +3.1120 | [+2.5809, +3.5674] | yes |
| rule_5 | 821 | spuni_5k | COPY_INPUT | +3.4440 | [+2.8967, +3.8856] | yes |
| rule_5 | 821 | spuni_20k | COPY_INPUT | +3.0738 | [+2.4190, +3.6005] | yes |
| rule_6 | 2648 | spbpe_5k | spbpe_20k | +0.4863 | [+0.3953, +0.5902] | yes |
| rule_6 | 2648 | wp_5k | wp_20k | +0.6429 | [+0.5214, +0.7782] | yes |
| rule_6 | 2648 | spuni_5k | spuni_20k | +0.5906 | [+0.4831, +0.7021] | yes |
| rule_6 | 2648 | spbpe_5k | COPY_INPUT | -0.1580 | [-0.4328, +0.0411] | no |
| rule_6 | 2648 | spbpe_20k | COPY_INPUT | -0.6443 | [-0.9879, -0.3860] | yes |
| rule_6 | 2648 | wp_5k | COPY_INPUT | -0.1636 | [-0.4420, +0.0316] | no |
| rule_6 | 2648 | wp_20k | COPY_INPUT | -0.8066 | [-1.1451, -0.5474] | yes |
| rule_6 | 2648 | spuni_5k | COPY_INPUT | -0.2862 | [-0.5988, -0.0639] | yes |
| rule_6 | 2648 | spuni_20k | COPY_INPUT | -0.8768 | [-1.2156, -0.6188] | yes |
| rule_7 | 132 | spbpe_5k | spbpe_20k | +0.1176 | [-0.0338, +0.2818] | no |
| rule_7 | 132 | wp_5k | wp_20k | +0.3157 | [+0.0477, +0.6732] | yes |
| rule_7 | 132 | spuni_5k | spuni_20k | +0.1081 | [-0.0935, +0.4163] | no |
| rule_7 | 132 | spbpe_5k | COPY_INPUT | -0.1274 | [-0.2791, -0.0247] | yes |
| rule_7 | 132 | spbpe_20k | COPY_INPUT | -0.2450 | [-0.4016, -0.1197] | yes |
| rule_7 | 132 | wp_5k | COPY_INPUT | -0.0608 | [-0.1518, -0.0031] | yes |
| rule_7 | 132 | wp_20k | COPY_INPUT | -0.3765 | [-0.7431, -0.1086] | yes |
| rule_7 | 132 | spuni_5k | COPY_INPUT | -0.1026 | [-0.1984, -0.0248] | yes |
| rule_7 | 132 | spuni_20k | COPY_INPUT | -0.2107 | [-0.5060, -0.0230] | yes |
| rule_8 | 70 | spbpe_5k | spbpe_20k | -0.0213 | [-0.2391, +0.1759] | no |
| rule_8 | 70 | wp_5k | wp_20k | +0.2215 | [+0.0423, +0.5011] | yes |
| rule_8 | 70 | spuni_5k | spuni_20k | +0.0328 | [-0.1279, +0.1913] | no |
| rule_8 | 70 | spbpe_5k | COPY_INPUT | -0.1102 | [-0.2840, +0.0000] | no |
| rule_8 | 70 | spbpe_20k | COPY_INPUT | -0.0889 | [-0.2425, -0.0017] | yes |
| rule_8 | 70 | wp_5k | COPY_INPUT | -0.0261 | [-0.0856, +0.0000] | no |
| rule_8 | 70 | wp_20k | COPY_INPUT | -0.2476 | [-0.5246, -0.0575] | yes |
| rule_8 | 70 | spuni_5k | COPY_INPUT | -0.0994 | [-0.2522, +0.0000] | no |
| rule_8 | 70 | spuni_20k | COPY_INPUT | -0.1322 | [-0.2587, -0.0297] | yes |
| rule_9 | 25 | spbpe_5k | spbpe_20k | +1.3988 | [+0.3522, +2.6805] | yes |
| rule_9 | 25 | wp_5k | wp_20k | +1.3242 | [+0.2720, +2.6172] | yes |
| rule_9 | 25 | spuni_5k | spuni_20k | +0.3779 | [-0.0324, +0.8058] | no |
| rule_9 | 25 | spbpe_5k | COPY_INPUT | +0.1945 | [+0.0202, +0.4207] | yes |
| rule_9 | 25 | spbpe_20k | COPY_INPUT | -1.2043 | [-2.4211, -0.1878] | yes |
| rule_9 | 25 | wp_5k | COPY_INPUT | -0.2338 | [-0.5036, -0.0435] | yes |
| rule_9 | 25 | wp_20k | COPY_INPUT | -1.5579 | [-2.8386, -0.4899] | yes |
| rule_9 | 25 | spuni_5k | COPY_INPUT | -0.5163 | [-1.6531, +0.0000] | no |
| rule_9 | 25 | spuni_20k | COPY_INPUT | -0.8942 | [-2.3495, +0.0247] | no |

Interpretation limits: intervals are conditional on the trained checkpoints; they do not measure training-seed variance. Seed agreement (Seeds A>B) and the per-seed table carry that information separately.

Send back: REPORT.md, paired_overall.csv, paired_per_seed.csv, prob_best.csv, paired_categories.csv, provenance.json.
