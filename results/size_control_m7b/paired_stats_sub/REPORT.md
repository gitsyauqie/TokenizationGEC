# Step16 — paired statistics (M3) — frozen 10-epoch runs

All 134025 test rows; 19 systems (18 runs + COPY_INPUT). Stored scores reproduced exactly before resampling.
Bootstrap B=2000 (stratified by category; cluster variant over 133782 identical-reference clusters). Approximate randomization R=10000.

## Primary comparisons, seed-mean (A − B)

| A | B | Metric | Δ | 95% CI | Cluster 95% CI | p (AR) | p (Holm) | Seeds A>B |
|---|---|---|---:|---|---|---:|---:|---:|
| spbpe_5k | spbpe_20k | chrf2_pct | +1.0483 | [+1.0259, +1.0721] | [+1.0256, +1.0706] | 0.0001 | 0.0006 | 3/3 |
| spbpe_5k | spbpe_20k | bleu | +1.6514 | [+1.6116, +1.6903] | [+1.6113, +1.6934] | 0.0001 | 0.0006 | 3/3 |
| spbpe_5k | spbpe_20k | exact_match_pct | +3.1895 | [+3.0479, +3.3270] | [+3.0506, +3.3406] | 0.0001 | 0.0006 | 3/3 |
| wp_5k | wp_20k | chrf2_pct | +0.7290 | [+0.7072, +0.7500] | [+0.7073, +0.7509] | 0.0001 | 0.0006 | 3/3 |
| wp_5k | wp_20k | bleu | +0.9208 | [+0.8832, +0.9562] | [+0.8854, +0.9575] | 0.0001 | 0.0006 | 3/3 |
| wp_5k | wp_20k | exact_match_pct | +1.4410 | [+1.3032, +1.5756] | [+1.3053, +1.5737] | 0.0001 | 0.0006 | 3/3 |
| spuni_5k | spuni_20k | chrf2_pct | +0.3970 | [+0.3795, +0.4152] | [+0.3788, +0.4156] | 0.0001 | 0.0006 | 3/3 |
| spuni_5k | spuni_20k | bleu | +0.5979 | [+0.5640, +0.6310] | [+0.5652, +0.6304] | 0.0001 | 0.0006 | 3/3 |
| spuni_5k | spuni_20k | exact_match_pct | +1.0028 | [+0.8593, +1.1411] | [+0.8612, +1.1471] | 0.0001 | 0.0006 | 3/3 |
| spbpe_5k | wp_5k | chrf2_pct | +0.1902 | [+0.1790, +0.2012] | [+0.1786, +0.2015] | 0.0001 | 0.0006 | 3/3 |
| spbpe_5k | wp_5k | bleu | +0.3502 | [+0.3276, +0.3721] | [+0.3258, +0.3737] | 0.0001 | 0.0006 | 3/3 |
| spbpe_5k | wp_5k | exact_match_pct | +1.0652 | [+0.9366, +1.1891] | [+0.9392, +1.1956] | 0.0001 | 0.0006 | 3/3 |
| spbpe_5k | spuni_5k | chrf2_pct | +0.1394 | [+0.1254, +0.1535] | [+0.1257, +0.1538] | 0.0001 | 0.0006 | 3/3 |
| spbpe_5k | spuni_5k | bleu | +0.3193 | [+0.2903, +0.3474] | [+0.2924, +0.3467] | 0.0001 | 0.0006 | 3/3 |
| spbpe_5k | spuni_5k | exact_match_pct | +0.0858 | [-0.0580, +0.2226] | [-0.0577, +0.2266] | 0.2384 | 0.2384 | 2/3 |
| wp_5k | spuni_5k | chrf2_pct | -0.0508 | [-0.0651, -0.0361] | [-0.0655, -0.0357] | 0.0001 | 0.0006 | 1/3 |
| wp_5k | spuni_5k | bleu | -0.0309 | [-0.0584, -0.0023] | [-0.0589, -0.0028] | 0.0315 | 0.0315 | 1/3 |
| wp_5k | spuni_5k | exact_match_pct | -0.9794 | [-1.1202, -0.8404] | [-1.1261, -0.8372] | 0.0001 | 0.0006 | 0/3 |

## Family x vocabulary interaction: (A5K − A20K) − (B5K − B20K), seed-mean

| A | B | Metric | Interaction | 95% CI | p (boot) | Seeds > 0 |
|---|---|---|---:|---|---:|---:|
| spbpe | spuni | chrf2_pct | +0.6514 | [+0.6324, +0.6712] | 0.0000 | 3/3 |
| spbpe | spuni | bleu | +1.0534 | [+1.0153, +1.0910] | 0.0000 | 3/3 |
| spbpe | spuni | exact_match_pct | +2.1867 | [+2.0141, +2.3735] | 0.0000 | 3/3 |
| wp | spuni | chrf2_pct | +0.3320 | [+0.3132, +0.3515] | 0.0000 | 2/3 |
| wp | spuni | bleu | +0.3229 | [+0.2875, +0.3611] | 0.0000 | 2/3 |
| wp | spuni | exact_match_pct | +0.4382 | [+0.2589, +0.6153] | 0.0000 | 2/3 |
| spbpe | wp | chrf2_pct | +0.3194 | [+0.3023, +0.3369] | 0.0000 | 3/3 |
| spbpe | wp | bleu | +0.7305 | [+0.6984, +0.7627] | 0.0000 | 3/3 |
| spbpe | wp | exact_match_pct | +1.7484 | [+1.5922, +1.9123] | 0.0000 | 3/3 |

## Probability of highest seed-mean score (bootstrap)

| Budget | Metric | Tag | Seed-mean | P(best) |
|---|---|---|---:|---:|
| 5k | chrf2_pct | spbpe_5k | 94.5766 | 1.000 |
| 5k | chrf2_pct | wp_5k | 94.3864 | 0.000 |
| 5k | chrf2_pct | spuni_5k | 94.4372 | 0.000 |
| 5k | bleu | spbpe_5k | 88.5193 | 1.000 |
| 5k | bleu | wp_5k | 88.1691 | 0.000 |
| 5k | bleu | spuni_5k | 88.2001 | 0.000 |
| 5k | exact_match_pct | spbpe_5k | 27.7122 | 0.883 |
| 5k | exact_match_pct | wp_5k | 26.6470 | 0.000 |
| 5k | exact_match_pct | spuni_5k | 27.6264 | 0.117 |
| 20k | chrf2_pct | spbpe_20k | 93.5282 | 0.000 |
| 20k | chrf2_pct | wp_20k | 93.6574 | 0.000 |
| 20k | chrf2_pct | spuni_20k | 94.0402 | 1.000 |
| 20k | bleu | spbpe_20k | 86.8680 | 0.000 |
| 20k | bleu | wp_20k | 87.2483 | 0.000 |
| 20k | bleu | spuni_20k | 87.6021 | 1.000 |
| 20k | exact_match_pct | spbpe_20k | 24.5228 | 0.000 |
| 20k | exact_match_pct | wp_20k | 25.2060 | 0.000 |
| 20k | exact_match_pct | spuni_20k | 26.6236 | 1.000 |

## Per-seed primary tests (chrF2 and exact match)

| A | B | Seed | Metric | Δ | 95% CI | p (AR) | p (Holm, 18) |
|---|---|---:|---|---:|---|---:|---:|
| spbpe_5k | spbpe_20k | 42 | chrf2_pct | +0.9364 | [+0.9104, +0.9627] | 0.0001 | 0.0018 |
| spbpe_5k | spbpe_20k | 43 | chrf2_pct | +1.0154 | [+0.9872, +1.0425] | 0.0001 | 0.0018 |
| spbpe_5k | spbpe_20k | 44 | chrf2_pct | +1.1933 | [+1.1647, +1.2216] | 0.0001 | 0.0018 |
| spbpe_5k | spbpe_20k | 42 | exact_match_pct | +3.4046 | [+3.2113, +3.5926] | 0.0001 | 0.0018 |
| spbpe_5k | spbpe_20k | 43 | exact_match_pct | +2.7719 | [+2.5756, +2.9629] | 0.0001 | 0.0018 |
| spbpe_5k | spbpe_20k | 44 | exact_match_pct | +3.3919 | [+3.2009, +3.5829] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 42 | chrf2_pct | +0.8836 | [+0.8527, +0.9158] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 43 | chrf2_pct | +0.6988 | [+0.6733, +0.7240] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 44 | chrf2_pct | +0.6044 | [+0.5831, +0.6248] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 42 | exact_match_pct | +2.0839 | [+1.9004, +2.2690] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 43 | exact_match_pct | +0.9177 | [+0.7334, +1.0991] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 44 | exact_match_pct | +1.3214 | [+1.1498, +1.5087] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 42 | chrf2_pct | +0.1599 | [+0.1406, +0.1800] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 43 | chrf2_pct | +0.3803 | [+0.3565, +0.4027] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 44 | chrf2_pct | +0.6507 | [+0.6256, +0.6767] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 42 | exact_match_pct | +0.4163 | [+0.2231, +0.6007] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 43 | exact_match_pct | +0.8513 | [+0.6775, +1.0409] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 44 | exact_match_pct | +1.7407 | [+1.5415, +1.9340] | 0.0001 | 0.0018 |
| spbpe_5k | wp_5k | 42 | chrf2_pct | +0.1231 | [+0.1064, +0.1400] | 0.0001 | 0.0018 |
| spbpe_5k | wp_5k | 43 | chrf2_pct | +0.2388 | [+0.2218, +0.2562] | 0.0001 | 0.0018 |
| spbpe_5k | wp_5k | 44 | chrf2_pct | +0.2087 | [+0.1914, +0.2259] | 0.0001 | 0.0018 |
| spbpe_5k | wp_5k | 42 | exact_match_pct | +1.1319 | [+0.9536, +1.3035] | 0.0001 | 0.0018 |
| spbpe_5k | wp_5k | 43 | exact_match_pct | +0.9543 | [+0.7812, +1.1356] | 0.0001 | 0.0018 |
| spbpe_5k | wp_5k | 44 | exact_match_pct | +1.1095 | [+0.9319, +1.2819] | 0.0001 | 0.0018 |
| spbpe_5k | spuni_5k | 42 | chrf2_pct | +0.1779 | [+0.1599, +0.1959] | 0.0001 | 0.0018 |
| spbpe_5k | spuni_5k | 43 | chrf2_pct | +0.1636 | [+0.1452, +0.1818] | 0.0001 | 0.0018 |
| spbpe_5k | spuni_5k | 44 | chrf2_pct | +0.0769 | [+0.0587, +0.0961] | 0.0001 | 0.0018 |
| spbpe_5k | spuni_5k | 42 | exact_match_pct | +0.6678 | [+0.4790, +0.8536] | 0.0001 | 0.0018 |
| spbpe_5k | spuni_5k | 43 | exact_match_pct | -0.7133 | [-0.9021, -0.5200] | 0.0001 | 0.0018 |
| spbpe_5k | spuni_5k | 44 | exact_match_pct | +0.3029 | [+0.1119, +0.4828] | 0.0024 | 0.0024 |
| wp_5k | spuni_5k | 42 | chrf2_pct | +0.0548 | [+0.0353, +0.0732] | 0.0001 | 0.0018 |
| wp_5k | spuni_5k | 43 | chrf2_pct | -0.0752 | [-0.0950, -0.0556] | 0.0001 | 0.0018 |
| wp_5k | spuni_5k | 44 | chrf2_pct | -0.1318 | [-0.1518, -0.1106] | 0.0001 | 0.0018 |
| wp_5k | spuni_5k | 42 | exact_match_pct | -0.4641 | [-0.6469, -0.2783] | 0.0001 | 0.0018 |
| wp_5k | spuni_5k | 43 | exact_match_pct | -1.6676 | [-1.8474, -1.4818] | 0.0001 | 0.0018 |
| wp_5k | spuni_5k | 44 | exact_match_pct | -0.8066 | [-0.9961, -0.6066] | 0.0001 | 0.0018 |

## Category chrF2: 5K − 20K and condition − COPY (seed-mean, descriptive, unadjusted)

| Category | n | A | B | Δ chrF2 | 95% CI | Excludes 0 |
|---|---:|---|---|---:|---|---|
| afiksasi | 26322 | spbpe_5k | spbpe_20k | +0.8908 | [+0.8412, +0.9407] | yes |
| afiksasi | 26322 | wp_5k | wp_20k | +0.5689 | [+0.5245, +0.6139] | yes |
| afiksasi | 26322 | spuni_5k | spuni_20k | +0.2268 | [+0.1888, +0.2656] | yes |
| afiksasi | 26322 | spbpe_5k | COPY_INPUT | +11.4434 | [+11.2129, +11.6467] | yes |
| afiksasi | 26322 | spbpe_20k | COPY_INPUT | +10.5525 | [+10.3104, +10.7733] | yes |
| afiksasi | 26322 | wp_5k | COPY_INPUT | +11.1131 | [+10.8815, +11.3173] | yes |
| afiksasi | 26322 | wp_20k | COPY_INPUT | +10.5442 | [+10.2987, +10.7661] | yes |
| afiksasi | 26322 | spuni_5k | COPY_INPUT | +11.0687 | [+10.8485, +11.2682] | yes |
| afiksasi | 26322 | spuni_20k | COPY_INPUT | +10.8419 | [+10.6029, +11.0497] | yes |
| ambigu | 6603 | spbpe_5k | spbpe_20k | +0.6936 | [+0.5842, +0.8111] | yes |
| ambigu | 6603 | wp_5k | wp_20k | +0.4518 | [+0.3538, +0.5568] | yes |
| ambigu | 6603 | spuni_5k | spuni_20k | +0.1867 | [+0.1087, +0.2734] | yes |
| ambigu | 6603 | spbpe_5k | COPY_INPUT | +0.3850 | [-0.0160, +0.7448] | no |
| ambigu | 6603 | spbpe_20k | COPY_INPUT | -0.3086 | [-0.7890, +0.1310] | no |
| ambigu | 6603 | wp_5k | COPY_INPUT | +0.3554 | [-0.0655, +0.7298] | no |
| ambigu | 6603 | wp_20k | COPY_INPUT | -0.0963 | [-0.5814, +0.3365] | no |
| ambigu | 6603 | spuni_5k | COPY_INPUT | +0.3178 | [-0.0755, +0.6646] | no |
| ambigu | 6603 | spuni_20k | COPY_INPUT | +0.1311 | [-0.3049, +0.5200] | no |
| ambigu_claude | 349 | spbpe_5k | spbpe_20k | +0.7863 | [+0.3457, +1.3639] | yes |
| ambigu_claude | 349 | wp_5k | wp_20k | +0.5821 | [+0.2679, +0.9874] | yes |
| ambigu_claude | 349 | spuni_5k | spuni_20k | +0.0126 | [-0.1856, +0.2272] | no |
| ambigu_claude | 349 | spbpe_5k | COPY_INPUT | -1.1629 | [-2.2111, -0.4489] | yes |
| ambigu_claude | 349 | spbpe_20k | COPY_INPUT | -1.9492 | [-3.5075, -0.8414] | yes |
| ambigu_claude | 349 | wp_5k | COPY_INPUT | -1.1657 | [-2.1711, -0.4672] | yes |
| ambigu_claude | 349 | wp_20k | COPY_INPUT | -1.7478 | [-3.0586, -0.7794] | yes |
| ambigu_claude | 349 | spuni_5k | COPY_INPUT | -1.6168 | [-3.0934, -0.5989] | yes |
| ambigu_claude | 349 | spuni_20k | COPY_INPUT | -1.6294 | [-3.2479, -0.5162] | yes |
| diksi | 14123 | spbpe_5k | spbpe_20k | +0.6471 | [+0.5769, +0.7186] | yes |
| diksi | 14123 | wp_5k | wp_20k | +0.3504 | [+0.2904, +0.4107] | yes |
| diksi | 14123 | spuni_5k | spuni_20k | +0.1465 | [+0.0957, +0.1997] | yes |
| diksi | 14123 | spbpe_5k | COPY_INPUT | -0.8827 | [-1.0683, -0.7041] | yes |
| diksi | 14123 | spbpe_20k | COPY_INPUT | -1.5299 | [-1.7644, -1.3128] | yes |
| diksi | 14123 | wp_5k | COPY_INPUT | -0.9527 | [-1.1475, -0.7720] | yes |
| diksi | 14123 | wp_20k | COPY_INPUT | -1.3031 | [-1.5307, -1.0910] | yes |
| diksi | 14123 | spuni_5k | COPY_INPUT | -1.0279 | [-1.2128, -0.8587] | yes |
| diksi | 14123 | spuni_20k | COPY_INPUT | -1.1744 | [-1.3786, -0.9791] | yes |
| diksi_claude | 349 | spbpe_5k | spbpe_20k | -0.0361 | [-0.2460, +0.1866] | no |
| diksi_claude | 349 | wp_5k | wp_20k | +0.1413 | [-0.0376, +0.3291] | no |
| diksi_claude | 349 | spuni_5k | spuni_20k | -0.0741 | [-0.2433, +0.0863] | no |
| diksi_claude | 349 | spbpe_5k | COPY_INPUT | -0.3750 | [-0.6126, -0.1572] | yes |
| diksi_claude | 349 | spbpe_20k | COPY_INPUT | -0.3389 | [-0.6984, -0.0143] | yes |
| diksi_claude | 349 | wp_5k | COPY_INPUT | -0.2645 | [-0.5356, -0.0286] | yes |
| diksi_claude | 349 | wp_20k | COPY_INPUT | -0.4058 | [-0.7230, -0.1001] | yes |
| diksi_claude | 349 | spuni_5k | COPY_INPUT | -0.3582 | [-0.6308, -0.1382] | yes |
| diksi_claude | 349 | spuni_20k | COPY_INPUT | -0.2841 | [-0.5355, -0.0536] | yes |
| kelengkapan_kalimat | 15877 | spbpe_5k | spbpe_20k | +0.5882 | [+0.5279, +0.6516] | yes |
| kelengkapan_kalimat | 15877 | wp_5k | wp_20k | +0.3333 | [+0.2779, +0.3903] | yes |
| kelengkapan_kalimat | 15877 | spuni_5k | spuni_20k | +0.1201 | [+0.0759, +0.1684] | yes |
| kelengkapan_kalimat | 15877 | spbpe_5k | COPY_INPUT | -0.5921 | [-0.7748, -0.4422] | yes |
| kelengkapan_kalimat | 15877 | spbpe_20k | COPY_INPUT | -1.1803 | [-1.3927, -0.9900] | yes |
| kelengkapan_kalimat | 15877 | wp_5k | COPY_INPUT | -0.6380 | [-0.8216, -0.4853] | yes |
| kelengkapan_kalimat | 15877 | wp_20k | COPY_INPUT | -0.9713 | [-1.1858, -0.7760] | yes |
| kelengkapan_kalimat | 15877 | spuni_5k | COPY_INPUT | -0.6987 | [-0.8726, -0.5549] | yes |
| kelengkapan_kalimat | 15877 | spuni_20k | COPY_INPUT | -0.8189 | [-1.0065, -0.6511] | yes |
| pembentukan_kata | 16373 | spbpe_5k | spbpe_20k | +2.6134 | [+2.5423, +2.6908] | yes |
| pembentukan_kata | 16373 | wp_5k | wp_20k | +1.7480 | [+1.6835, +1.8171] | yes |
| pembentukan_kata | 16373 | spuni_5k | spuni_20k | +0.7702 | [+0.7134, +0.8276] | yes |
| pembentukan_kata | 16373 | spbpe_5k | COPY_INPUT | +11.3823 | [+11.1425, +11.5995] | yes |
| pembentukan_kata | 16373 | spbpe_20k | COPY_INPUT | +8.7689 | [+8.4981, +9.0185] | yes |
| pembentukan_kata | 16373 | wp_5k | COPY_INPUT | +10.7810 | [+10.5322, +10.9991] | yes |
| pembentukan_kata | 16373 | wp_20k | COPY_INPUT | +9.0331 | [+8.7662, +9.2734] | yes |
| pembentukan_kata | 16373 | spuni_5k | COPY_INPUT | +11.6891 | [+11.4414, +11.9078] | yes |
| pembentukan_kata | 16373 | spuni_20k | COPY_INPUT | +10.9189 | [+10.6515, +11.1650] | yes |
| pleonasme | 2717 | spbpe_5k | spbpe_20k | +0.2364 | [+0.0978, +0.3760] | yes |
| pleonasme | 2717 | wp_5k | wp_20k | +0.1850 | [+0.0612, +0.3139] | yes |
| pleonasme | 2717 | spuni_5k | spuni_20k | -0.0898 | [-0.2043, +0.0252] | no |
| pleonasme | 2717 | spbpe_5k | COPY_INPUT | +1.3284 | [+1.0197, +1.5903] | yes |
| pleonasme | 2717 | spbpe_20k | COPY_INPUT | +1.0920 | [+0.7108, +1.4293] | yes |
| pleonasme | 2717 | wp_5k | COPY_INPUT | +1.4796 | [+1.1647, +1.7482] | yes |
| pleonasme | 2717 | wp_20k | COPY_INPUT | +1.2947 | [+0.9055, +1.6302] | yes |
| pleonasme | 2717 | spuni_5k | COPY_INPUT | +1.2945 | [+0.9986, +1.5563] | yes |
| pleonasme | 2717 | spuni_20k | COPY_INPUT | +1.3843 | [+1.0323, +1.7115] | yes |
| pleonasme_claude | 350 | spbpe_5k | spbpe_20k | +0.2767 | [+0.1147, +0.4420] | yes |
| pleonasme_claude | 350 | wp_5k | wp_20k | +0.1821 | [-0.0062, +0.3781] | no |
| pleonasme_claude | 350 | spuni_5k | spuni_20k | +0.0443 | [-0.1239, +0.1993] | no |
| pleonasme_claude | 350 | spbpe_5k | COPY_INPUT | -0.6660 | [-0.8918, -0.4686] | yes |
| pleonasme_claude | 350 | spbpe_20k | COPY_INPUT | -0.9427 | [-1.1908, -0.7142] | yes |
| pleonasme_claude | 350 | wp_5k | COPY_INPUT | -0.7110 | [-0.9363, -0.5142] | yes |
| pleonasme_claude | 350 | wp_20k | COPY_INPUT | -0.8932 | [-1.1575, -0.6710] | yes |
| pleonasme_claude | 350 | spuni_5k | COPY_INPUT | -0.8334 | [-1.0823, -0.6019] | yes |
| pleonasme_claude | 350 | spuni_20k | COPY_INPUT | -0.8777 | [-1.1443, -0.6465] | yes |
| preposisi | 16774 | spbpe_5k | spbpe_20k | +0.5801 | [+0.5148, +0.6497] | yes |
| preposisi | 16774 | wp_5k | wp_20k | +0.3879 | [+0.3259, +0.4594] | yes |
| preposisi | 16774 | spuni_5k | spuni_20k | +0.1532 | [+0.0981, +0.2097] | yes |
| preposisi | 16774 | spbpe_5k | COPY_INPUT | +1.4144 | [+1.1585, +1.6199] | yes |
| preposisi | 16774 | spbpe_20k | COPY_INPUT | +0.8343 | [+0.5388, +1.0781] | yes |
| preposisi | 16774 | wp_5k | COPY_INPUT | +1.4328 | [+1.1709, +1.6515] | yes |
| preposisi | 16774 | wp_20k | COPY_INPUT | +1.0449 | [+0.7456, +1.2978] | yes |
| preposisi | 16774 | spuni_5k | COPY_INPUT | +1.3971 | [+1.1522, +1.5922] | yes |
| preposisi | 16774 | spuni_20k | COPY_INPUT | +1.2438 | [+0.9631, +1.4724] | yes |
| reduplikasi | 8927 | spbpe_5k | spbpe_20k | +0.5976 | [+0.5191, +0.6815] | yes |
| reduplikasi | 8927 | wp_5k | wp_20k | +0.4304 | [+0.3573, +0.5109] | yes |
| reduplikasi | 8927 | spuni_5k | spuni_20k | +0.3387 | [+0.2837, +0.3942] | yes |
| reduplikasi | 8927 | spbpe_5k | COPY_INPUT | +0.8684 | [+0.5886, +1.1246] | yes |
| reduplikasi | 8927 | spbpe_20k | COPY_INPUT | +0.2708 | [-0.0698, +0.5805] | no |
| reduplikasi | 8927 | wp_5k | COPY_INPUT | +0.8481 | [+0.5588, +1.1086] | yes |
| reduplikasi | 8927 | wp_20k | COPY_INPUT | +0.4177 | [+0.0811, +0.7256] | yes |
| reduplikasi | 8927 | spuni_5k | COPY_INPUT | +0.8163 | [+0.5229, +1.0763] | yes |
| reduplikasi | 8927 | spuni_20k | COPY_INPUT | +0.4775 | [+0.1723, +0.7701] | yes |
| sintaksis_frasa | 25261 | spbpe_5k | spbpe_20k | +1.4699 | [+1.4192, +1.5264] | yes |
| sintaksis_frasa | 25261 | wp_5k | wp_20k | +1.2383 | [+1.1862, +1.2890] | yes |
| sintaksis_frasa | 25261 | spuni_5k | spuni_20k | +0.9949 | [+0.9428, +1.0429] | yes |
| sintaksis_frasa | 25261 | spbpe_5k | COPY_INPUT | +4.3567 | [+4.1700, +4.5380] | yes |
| sintaksis_frasa | 25261 | spbpe_20k | COPY_INPUT | +2.8868 | [+2.6697, +3.0840] | yes |
| sintaksis_frasa | 25261 | wp_5k | COPY_INPUT | +4.1112 | [+3.9217, +4.2905] | yes |
| sintaksis_frasa | 25261 | wp_20k | COPY_INPUT | +2.8729 | [+2.6656, +3.0691] | yes |
| sintaksis_frasa | 25261 | spuni_5k | COPY_INPUT | +4.0114 | [+3.8314, +4.1835] | yes |
| sintaksis_frasa | 25261 | spuni_20k | COPY_INPUT | +3.0165 | [+2.8142, +3.2067] | yes |

Interpretation limits: intervals are conditional on the trained checkpoints; they do not measure training-seed variance. Seed agreement (Seeds A>B) and the per-seed table carry that information separately.

Send back: REPORT.md, paired_overall.csv, paired_per_seed.csv, prob_best.csv, paired_categories.csv, provenance.json.
