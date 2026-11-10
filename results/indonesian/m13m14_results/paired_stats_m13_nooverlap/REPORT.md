# Step16 — paired statistics (M3) — frozen 10-epoch runs — SENSITIVITY: 2721 test rows excluded (overlap_target_ids.txt)

All 131304 test rows; 19 systems (18 runs + COPY_INPUT). Stored scores reproduced exactly before resampling.
Bootstrap B=2000 (stratified by category; cluster variant over 131163 identical-reference clusters). Approximate randomization R=10000.

## Primary comparisons, seed-mean (A − B)

| A | B | Metric | Δ | 95% CI | Cluster 95% CI | p (AR) | p (Holm) | Seeds A>B |
|---|---|---|---:|---|---|---:|---:|---:|
| spbpe_5k | spbpe_20k | chrf2_pct | +0.1920 | [+0.1789, +0.2045] | [+0.1795, +0.2047] | 0.0001 | 0.0006 | 3/3 |
| spbpe_5k | spbpe_20k | bleu | +0.4385 | [+0.4128, +0.4632] | [+0.4131, +0.4638] | 0.0001 | 0.0006 | 3/3 |
| spbpe_5k | spbpe_20k | exact_match_pct | +3.2520 | [+3.1017, +3.3972] | [+3.1028, +3.3993] | 0.0001 | 0.0006 | 3/3 |
| wp_5k | wp_20k | chrf2_pct | +0.2441 | [+0.2307, +0.2580] | [+0.2315, +0.2574] | 0.0001 | 0.0006 | 3/3 |
| wp_5k | wp_20k | bleu | +0.5063 | [+0.4798, +0.5322] | [+0.4810, +0.5332] | 0.0001 | 0.0006 | 3/3 |
| wp_5k | wp_20k | exact_match_pct | +3.5658 | [+3.4086, +3.7151] | [+3.4133, +3.7267] | 0.0001 | 0.0006 | 3/3 |
| spuni_5k | spuni_20k | chrf2_pct | +0.1098 | [+0.0972, +0.1223] | [+0.0973, +0.1224] | 0.0001 | 0.0006 | 3/3 |
| spuni_5k | spuni_20k | bleu | +0.1106 | [+0.0862, +0.1343] | [+0.0867, +0.1352] | 0.0001 | 0.0006 | 2/3 |
| spuni_5k | spuni_20k | exact_match_pct | +1.2361 | [+1.0860, +1.3757] | [+1.1002, +1.3777] | 0.0001 | 0.0006 | 3/3 |
| spbpe_5k | wp_5k | chrf2_pct | +0.0101 | [+0.0012, +0.0189] | [+0.0012, +0.0193] | 0.0298 | 0.0298 | 1/3 |
| spbpe_5k | wp_5k | bleu | +0.0178 | [-0.0013, +0.0363] | [-0.0006, +0.0365] | 0.0588 | 0.0588 | 1/3 |
| spbpe_5k | wp_5k | exact_match_pct | +0.0840 | [-0.0325, +0.2046] | [-0.0391, +0.1988] | 0.1620 | 0.1620 | 1/3 |
| spbpe_5k | spuni_5k | chrf2_pct | +0.0390 | [+0.0285, +0.0492] | [+0.0285, +0.0497] | 0.0001 | 0.0006 | 2/3 |
| spbpe_5k | spuni_5k | bleu | +0.1208 | [+0.0981, +0.1419] | [+0.0999, +0.1430] | 0.0001 | 0.0006 | 2/3 |
| spbpe_5k | spuni_5k | exact_match_pct | +0.8080 | [+0.6717, +0.9368] | [+0.6789, +0.9347] | 0.0001 | 0.0006 | 2/3 |
| wp_5k | spuni_5k | chrf2_pct | +0.0289 | [+0.0184, +0.0402] | [+0.0186, +0.0394] | 0.0001 | 0.0006 | 2/3 |
| wp_5k | spuni_5k | bleu | +0.1030 | [+0.0819, +0.1256] | [+0.0835, +0.1247] | 0.0001 | 0.0006 | 3/3 |
| wp_5k | spuni_5k | exact_match_pct | +0.7240 | [+0.5951, +0.8467] | [+0.5999, +0.8575] | 0.0001 | 0.0006 | 3/3 |

## Family x vocabulary interaction: (A5K − A20K) − (B5K − B20K), seed-mean

| A | B | Metric | Interaction | 95% CI | p (boot) | Seeds > 0 |
|---|---|---|---:|---|---:|---:|
| spbpe | spuni | chrf2_pct | +0.0822 | [+0.0660, +0.0979] | 0.0000 | 3/3 |
| spbpe | spuni | bleu | +0.3279 | [+0.3000, +0.3565] | 0.0000 | 3/3 |
| spbpe | spuni | exact_match_pct | +2.0159 | [+1.8402, +2.1949] | 0.0000 | 3/3 |
| wp | spuni | chrf2_pct | +0.1343 | [+0.1191, +0.1488] | 0.0000 | 3/3 |
| wp | spuni | bleu | +0.3957 | [+0.3656, +0.4261] | 0.0000 | 3/3 |
| wp | spuni | exact_match_pct | +2.3297 | [+2.1407, +2.5097] | 0.0000 | 3/3 |
| spbpe | wp | chrf2_pct | -0.0522 | [-0.0668, -0.0371] | 0.0000 | 1/3 |
| spbpe | wp | bleu | -0.0678 | [-0.0956, -0.0396] | 0.0000 | 1/3 |
| spbpe | wp | exact_match_pct | -0.3138 | [-0.4823, -0.1459] | 0.0000 | 2/3 |

## Probability of highest seed-mean score (bootstrap)

| Budget | Metric | Tag | Seed-mean | P(best) |
|---|---|---|---:|---:|
| 5k | chrf2_pct | spbpe_5k | 96.2192 | 0.988 |
| 5k | chrf2_pct | wp_5k | 96.2091 | 0.012 |
| 5k | chrf2_pct | spuni_5k | 96.1802 | 0.000 |
| 5k | bleu | spbpe_5k | 92.2657 | 0.964 |
| 5k | bleu | wp_5k | 92.2479 | 0.036 |
| 5k | bleu | spuni_5k | 92.1449 | 0.000 |
| 5k | exact_match_pct | spbpe_5k | 45.1030 | 0.911 |
| 5k | exact_match_pct | wp_5k | 45.0189 | 0.088 |
| 5k | exact_match_pct | spuni_5k | 44.2949 | 0.000 |
| 20k | chrf2_pct | spbpe_20k | 96.0272 | 0.000 |
| 20k | chrf2_pct | wp_20k | 95.9650 | 0.000 |
| 20k | chrf2_pct | spuni_20k | 96.0704 | 1.000 |
| 20k | bleu | spbpe_20k | 91.8272 | 0.000 |
| 20k | bleu | wp_20k | 91.7416 | 0.000 |
| 20k | bleu | spuni_20k | 92.0343 | 1.000 |
| 20k | exact_match_pct | spbpe_20k | 41.8510 | 0.000 |
| 20k | exact_match_pct | wp_20k | 41.4532 | 0.000 |
| 20k | exact_match_pct | spuni_20k | 43.0589 | 1.000 |

## Per-seed primary tests (chrF2 and exact match)

| A | B | Seed | Metric | Δ | 95% CI | p (AR) | p (Holm, 18) |
|---|---|---:|---|---:|---|---:|---:|
| spbpe_5k | spbpe_20k | 42 | chrf2_pct | +0.1401 | [+0.1241, +0.1561] | 0.0001 | 0.0018 |
| spbpe_5k | spbpe_20k | 43 | chrf2_pct | +0.2209 | [+0.2041, +0.2381] | 0.0001 | 0.0018 |
| spbpe_5k | spbpe_20k | 44 | chrf2_pct | +0.2150 | [+0.1984, +0.2313] | 0.0001 | 0.0018 |
| spbpe_5k | spbpe_20k | 42 | exact_match_pct | +2.7745 | [+2.5848, +2.9702] | 0.0001 | 0.0018 |
| spbpe_5k | spbpe_20k | 43 | exact_match_pct | +3.0464 | [+2.8476, +3.2261] | 0.0001 | 0.0018 |
| spbpe_5k | spbpe_20k | 44 | exact_match_pct | +3.9351 | [+3.7348, +4.1255] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 42 | chrf2_pct | +0.2465 | [+0.2297, +0.2624] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 43 | chrf2_pct | +0.1829 | [+0.1648, +0.2000] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 44 | chrf2_pct | +0.3031 | [+0.2870, +0.3199] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 42 | exact_match_pct | +4.1568 | [+3.9625, +4.3525] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 43 | exact_match_pct | +2.6976 | [+2.4957, +2.8940] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 44 | exact_match_pct | +3.8430 | [+3.6373, +4.0380] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 42 | chrf2_pct | +0.1361 | [+0.1188, +0.1539] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 43 | chrf2_pct | +0.0060 | [-0.0109, +0.0231] | 0.4920 | 0.9839 |
| spuni_5k | spuni_20k | 44 | chrf2_pct | +0.1874 | [+0.1717, +0.2033] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 42 | exact_match_pct | +1.3130 | [+1.1165, +1.5118] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 43 | exact_match_pct | +0.5491 | [+0.3511, +0.7373] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 44 | exact_match_pct | +1.8461 | [+1.6565, +2.0213] | 0.0001 | 0.0018 |
| spbpe_5k | wp_5k | 42 | chrf2_pct | -0.0532 | [-0.0659, -0.0413] | 0.0001 | 0.0018 |
| spbpe_5k | wp_5k | 43 | chrf2_pct | +0.0968 | [+0.0802, +0.1128] | 0.0001 | 0.0018 |
| spbpe_5k | wp_5k | 44 | chrf2_pct | -0.0133 | [-0.0270, +0.0001] | 0.0550 | 0.2200 |
| spbpe_5k | wp_5k | 42 | exact_match_pct | -0.0541 | [-0.2301, +0.1219] | 0.5425 | 0.5425 |
| spbpe_5k | wp_5k | 43 | exact_match_pct | +1.0099 | [+0.8377, +1.1828] | 0.0001 | 0.0018 |
| spbpe_5k | wp_5k | 44 | exact_match_pct | -0.7037 | [-0.8812, -0.5293] | 0.0001 | 0.0018 |
| spbpe_5k | spuni_5k | 42 | chrf2_pct | +0.0426 | [+0.0276, +0.0579] | 0.0001 | 0.0018 |
| spbpe_5k | spuni_5k | 43 | chrf2_pct | +0.1007 | [+0.0859, +0.1163] | 0.0001 | 0.0018 |
| spbpe_5k | spuni_5k | 44 | chrf2_pct | -0.0263 | [-0.0406, -0.0119] | 0.0004 | 0.0020 |
| spbpe_5k | spuni_5k | 42 | exact_match_pct | +1.1987 | [+1.0182, +1.3770] | 0.0001 | 0.0018 |
| spbpe_5k | spuni_5k | 43 | exact_match_pct | +1.3427 | [+1.1637, +1.5247] | 0.0001 | 0.0018 |
| spbpe_5k | spuni_5k | 44 | exact_match_pct | -0.1173 | [-0.2963, +0.0564] | 0.1944 | 0.3888 |
| wp_5k | spuni_5k | 42 | chrf2_pct | +0.0959 | [+0.0810, +0.1117] | 0.0001 | 0.0018 |
| wp_5k | spuni_5k | 43 | chrf2_pct | +0.0039 | [-0.0109, +0.0191] | 0.6170 | 0.9839 |
| wp_5k | spuni_5k | 44 | chrf2_pct | -0.0130 | [-0.0266, +0.0014] | 0.0796 | 0.2388 |
| wp_5k | spuni_5k | 42 | exact_match_pct | +1.2528 | [+1.0692, +1.4318] | 0.0001 | 0.0018 |
| wp_5k | spuni_5k | 43 | exact_match_pct | +0.3328 | [+0.1538, +0.5081] | 0.0003 | 0.0018 |
| wp_5k | spuni_5k | 44 | exact_match_pct | +0.5864 | [+0.4021, +0.7608] | 0.0001 | 0.0018 |

## Category chrF2: 5K − 20K and condition − COPY (seed-mean, descriptive, unadjusted)

| Category | n | A | B | Δ chrF2 | 95% CI | Excludes 0 |
|---|---:|---|---|---:|---|---|
| afiksasi | 25982 | spbpe_5k | spbpe_20k | +0.1805 | [+0.1553, +0.2071] | yes |
| afiksasi | 25982 | wp_5k | wp_20k | +0.1413 | [+0.1137, +0.1691] | yes |
| afiksasi | 25982 | spuni_5k | spuni_20k | -0.0021 | [-0.0307, +0.0255] | no |
| afiksasi | 25982 | spbpe_5k | COPY_INPUT | +13.6264 | [+13.4610, +13.7758] | yes |
| afiksasi | 25982 | spbpe_20k | COPY_INPUT | +13.4458 | [+13.2713, +13.6019] | yes |
| afiksasi | 25982 | wp_5k | COPY_INPUT | +13.5357 | [+13.3658, +13.6886] | yes |
| afiksasi | 25982 | wp_20k | COPY_INPUT | +13.3944 | [+13.2262, +13.5407] | yes |
| afiksasi | 25982 | spuni_5k | COPY_INPUT | +13.4793 | [+13.3058, +13.6296] | yes |
| afiksasi | 25982 | spuni_20k | COPY_INPUT | +13.4814 | [+13.3196, +13.6293] | yes |
| ambigu | 6587 | spbpe_5k | spbpe_20k | -0.0323 | [-0.0959, +0.0295] | no |
| ambigu | 6587 | wp_5k | wp_20k | -0.0800 | [-0.1314, -0.0317] | yes |
| ambigu | 6587 | spuni_5k | spuni_20k | -0.0648 | [-0.1294, -0.0099] | yes |
| ambigu | 6587 | spbpe_5k | COPY_INPUT | +1.3821 | [+1.1579, +1.5627] | yes |
| ambigu | 6587 | spbpe_20k | COPY_INPUT | +1.4144 | [+1.1769, +1.6154] | yes |
| ambigu | 6587 | wp_5k | COPY_INPUT | +1.3417 | [+1.1071, +1.5353] | yes |
| ambigu | 6587 | wp_20k | COPY_INPUT | +1.4217 | [+1.2053, +1.6083] | yes |
| ambigu | 6587 | spuni_5k | COPY_INPUT | +1.4051 | [+1.1651, +1.5936] | yes |
| ambigu | 6587 | spuni_20k | COPY_INPUT | +1.4699 | [+1.2733, +1.6412] | yes |
| ambigu_claude | 309 | spbpe_5k | spbpe_20k | -0.2794 | [-0.6160, +0.0756] | no |
| ambigu_claude | 309 | wp_5k | wp_20k | +0.0314 | [-0.3007, +0.3760] | no |
| ambigu_claude | 309 | spuni_5k | spuni_20k | +0.2744 | [-0.1041, +0.6680] | no |
| ambigu_claude | 309 | spbpe_5k | COPY_INPUT | -1.3748 | [-1.7903, -0.9700] | yes |
| ambigu_claude | 309 | spbpe_20k | COPY_INPUT | -1.0954 | [-1.4756, -0.7421] | yes |
| ambigu_claude | 309 | wp_5k | COPY_INPUT | -1.2916 | [-1.6602, -0.9545] | yes |
| ambigu_claude | 309 | wp_20k | COPY_INPUT | -1.3230 | [-1.7512, -0.9221] | yes |
| ambigu_claude | 309 | spuni_5k | COPY_INPUT | -1.4249 | [-2.1609, -0.8273] | yes |
| ambigu_claude | 309 | spuni_20k | COPY_INPUT | -1.6993 | [-2.4945, -1.0857] | yes |
| diksi | 13835 | spbpe_5k | spbpe_20k | -0.0822 | [-0.1221, -0.0393] | yes |
| diksi | 13835 | wp_5k | wp_20k | -0.0207 | [-0.0545, +0.0136] | no |
| diksi | 13835 | spuni_5k | spuni_20k | -0.0579 | [-0.0890, -0.0261] | yes |
| diksi | 13835 | spbpe_5k | COPY_INPUT | -1.1048 | [-1.1955, -1.0327] | yes |
| diksi | 13835 | spbpe_20k | COPY_INPUT | -1.0226 | [-1.1280, -0.9365] | yes |
| diksi | 13835 | wp_5k | COPY_INPUT | -1.0735 | [-1.1760, -0.9911] | yes |
| diksi | 13835 | wp_20k | COPY_INPUT | -1.0528 | [-1.1427, -0.9784] | yes |
| diksi | 13835 | spuni_5k | COPY_INPUT | -1.0581 | [-1.1578, -0.9794] | yes |
| diksi | 13835 | spuni_20k | COPY_INPUT | -1.0002 | [-1.0887, -0.9286] | yes |
| diksi_claude | 65 | spbpe_5k | spbpe_20k | -0.3831 | [-1.2316, +0.4676] | no |
| diksi_claude | 65 | wp_5k | wp_20k | -0.7862 | [-1.8511, +0.0681] | no |
| diksi_claude | 65 | spuni_5k | spuni_20k | +0.2287 | [-0.5272, +0.9284] | no |
| diksi_claude | 65 | spbpe_5k | COPY_INPUT | +0.6656 | [-0.3417, +1.7033] | no |
| diksi_claude | 65 | spbpe_20k | COPY_INPUT | +1.0486 | [+0.2300, +1.9470] | yes |
| diksi_claude | 65 | wp_5k | COPY_INPUT | +0.5289 | [-0.8891, +1.8781] | no |
| diksi_claude | 65 | wp_20k | COPY_INPUT | +1.3151 | [+0.4431, +2.3275] | yes |
| diksi_claude | 65 | spuni_5k | COPY_INPUT | +0.8741 | [+0.0873, +1.7400] | yes |
| diksi_claude | 65 | spuni_20k | COPY_INPUT | +0.6453 | [-0.1879, +1.6002] | no |
| kelengkapan_kalimat | 15674 | spbpe_5k | spbpe_20k | -0.2207 | [-0.2575, -0.1846] | yes |
| kelengkapan_kalimat | 15674 | wp_5k | wp_20k | -0.1419 | [-0.1761, -0.1076] | yes |
| kelengkapan_kalimat | 15674 | spuni_5k | spuni_20k | -0.0797 | [-0.1134, -0.0459] | yes |
| kelengkapan_kalimat | 15674 | spbpe_5k | COPY_INPUT | -0.5471 | [-0.6301, -0.4733] | yes |
| kelengkapan_kalimat | 15674 | spbpe_20k | COPY_INPUT | -0.3265 | [-0.4159, -0.2451] | yes |
| kelengkapan_kalimat | 15674 | wp_5k | COPY_INPUT | -0.5059 | [-0.5948, -0.4280] | yes |
| kelengkapan_kalimat | 15674 | wp_20k | COPY_INPUT | -0.3640 | [-0.4446, -0.2907] | yes |
| kelengkapan_kalimat | 15674 | spuni_5k | COPY_INPUT | -0.4394 | [-0.5159, -0.3699] | yes |
| kelengkapan_kalimat | 15674 | spuni_20k | COPY_INPUT | -0.3597 | [-0.4391, -0.2881] | yes |
| pembentukan_kata | 16137 | spbpe_5k | spbpe_20k | +0.8084 | [+0.7741, +0.8416] | yes |
| pembentukan_kata | 16137 | wp_5k | wp_20k | +0.9848 | [+0.9475, +1.0229] | yes |
| pembentukan_kata | 16137 | spuni_5k | spuni_20k | +0.4929 | [+0.4636, +0.5227] | yes |
| pembentukan_kata | 16137 | spbpe_5k | COPY_INPUT | +13.1976 | [+13.0106, +13.3604] | yes |
| pembentukan_kata | 16137 | spbpe_20k | COPY_INPUT | +12.3892 | [+12.2023, +12.5559] | yes |
| pembentukan_kata | 16137 | wp_5k | COPY_INPUT | +13.1189 | [+12.9291, +13.2854] | yes |
| pembentukan_kata | 16137 | wp_20k | COPY_INPUT | +12.1341 | [+11.9521, +12.2955] | yes |
| pembentukan_kata | 16137 | spuni_5k | COPY_INPUT | +13.1610 | [+12.9750, +13.3239] | yes |
| pembentukan_kata | 16137 | spuni_20k | COPY_INPUT | +12.6680 | [+12.4836, +12.8354] | yes |
| pleonasme | 2404 | spbpe_5k | spbpe_20k | +0.0572 | [-0.0392, +0.1402] | no |
| pleonasme | 2404 | wp_5k | wp_20k | +0.1368 | [+0.0576, +0.2309] | yes |
| pleonasme | 2404 | spuni_5k | spuni_20k | +0.1079 | [+0.0487, +0.1756] | yes |
| pleonasme | 2404 | spbpe_5k | COPY_INPUT | +2.6409 | [+2.4889, +2.7770] | yes |
| pleonasme | 2404 | spbpe_20k | COPY_INPUT | +2.5837 | [+2.4545, +2.6964] | yes |
| pleonasme | 2404 | wp_5k | COPY_INPUT | +2.6873 | [+2.5572, +2.8056] | yes |
| pleonasme | 2404 | wp_20k | COPY_INPUT | +2.5505 | [+2.4039, +2.6804] | yes |
| pleonasme | 2404 | spuni_5k | COPY_INPUT | +2.6943 | [+2.5511, +2.8208] | yes |
| pleonasme | 2404 | spuni_20k | COPY_INPUT | +2.5863 | [+2.4311, +2.7259] | yes |
| pleonasme_claude | 59 | spbpe_5k | spbpe_20k | -0.4661 | [-1.0207, +0.0531] | no |
| pleonasme_claude | 59 | wp_5k | wp_20k | -0.1203 | [-0.5835, +0.2847] | no |
| pleonasme_claude | 59 | spuni_5k | spuni_20k | +0.1942 | [-0.6727, +1.0308] | no |
| pleonasme_claude | 59 | spbpe_5k | COPY_INPUT | -1.7301 | [-2.5870, -1.0250] | yes |
| pleonasme_claude | 59 | spbpe_20k | COPY_INPUT | -1.2640 | [-2.0208, -0.6664] | yes |
| pleonasme_claude | 59 | wp_5k | COPY_INPUT | -1.5258 | [-2.4631, -0.7763] | yes |
| pleonasme_claude | 59 | wp_20k | COPY_INPUT | -1.4055 | [-2.0796, -0.7482] | yes |
| pleonasme_claude | 59 | spuni_5k | COPY_INPUT | -1.8769 | [-3.0187, -0.9458] | yes |
| pleonasme_claude | 59 | spuni_20k | COPY_INPUT | -2.0711 | [-3.0146, -1.2358] | yes |
| preposisi | 16543 | spbpe_5k | spbpe_20k | -0.0528 | [-0.0859, -0.0218] | yes |
| preposisi | 16543 | wp_5k | wp_20k | -0.0807 | [-0.1146, -0.0483] | yes |
| preposisi | 16543 | spuni_5k | spuni_20k | -0.1289 | [-0.1646, -0.0963] | yes |
| preposisi | 16543 | spbpe_5k | COPY_INPUT | +2.7109 | [+2.5776, +2.8345] | yes |
| preposisi | 16543 | spbpe_20k | COPY_INPUT | +2.7637 | [+2.6210, +2.8957] | yes |
| preposisi | 16543 | wp_5k | COPY_INPUT | +2.7029 | [+2.5593, +2.8314] | yes |
| preposisi | 16543 | wp_20k | COPY_INPUT | +2.7836 | [+2.6543, +2.9055] | yes |
| preposisi | 16543 | spuni_5k | COPY_INPUT | +2.7213 | [+2.5841, +2.8457] | yes |
| preposisi | 16543 | spuni_20k | COPY_INPUT | +2.8502 | [+2.7313, +2.9629] | yes |
| reduplikasi | 8789 | spbpe_5k | spbpe_20k | +0.1535 | [+0.1197, +0.1938] | yes |
| reduplikasi | 8789 | wp_5k | wp_20k | +0.1293 | [+0.0982, +0.1575] | yes |
| reduplikasi | 8789 | spuni_5k | spuni_20k | +0.1159 | [+0.0792, +0.1491] | yes |
| reduplikasi | 8789 | spbpe_5k | COPY_INPUT | +1.4112 | [+1.2500, +1.5352] | yes |
| reduplikasi | 8789 | spbpe_20k | COPY_INPUT | +1.2577 | [+1.0706, +1.4004] | yes |
| reduplikasi | 8789 | wp_5k | COPY_INPUT | +1.4039 | [+1.2322, +1.5364] | yes |
| reduplikasi | 8789 | wp_20k | COPY_INPUT | +1.2746 | [+1.1078, +1.4031] | yes |
| reduplikasi | 8789 | spuni_5k | COPY_INPUT | +1.4185 | [+1.2440, +1.5488] | yes |
| reduplikasi | 8789 | spuni_20k | COPY_INPUT | +1.3026 | [+1.1416, +1.4308] | yes |
| sintaksis_frasa | 24920 | spbpe_5k | spbpe_20k | +0.5058 | [+0.4688, +0.5437] | yes |
| sintaksis_frasa | 24920 | wp_5k | wp_20k | +0.6712 | [+0.6281, +0.7132] | yes |
| sintaksis_frasa | 24920 | spuni_5k | spuni_20k | +0.4240 | [+0.3901, +0.4597] | yes |
| sintaksis_frasa | 24920 | spbpe_5k | COPY_INPUT | +8.0428 | [+7.9017, +8.1857] | yes |
| sintaksis_frasa | 24920 | spbpe_20k | COPY_INPUT | +7.5370 | [+7.4030, +7.6724] | yes |
| sintaksis_frasa | 24920 | wp_5k | COPY_INPUT | +8.1094 | [+7.9632, +8.2518] | yes |
| sintaksis_frasa | 24920 | wp_20k | COPY_INPUT | +7.4382 | [+7.3036, +7.5693] | yes |
| sintaksis_frasa | 24920 | spuni_5k | COPY_INPUT | +7.8960 | [+7.7576, +8.0355] | yes |
| sintaksis_frasa | 24920 | spuni_20k | COPY_INPUT | +7.4719 | [+7.3418, +7.6073] | yes |

Interpretation limits: intervals are conditional on the trained checkpoints; they do not measure training-seed variance. Seed agreement (Seeds A>B) and the per-seed table carry that information separately.

Send back: REPORT.md, paired_overall.csv, paired_per_seed.csv, prob_best.csv, paired_categories.csv, provenance.json.
