# Step16 — paired statistics (M3) — frozen 10-epoch runs

All 134025 test rows; 19 systems (18 runs + COPY_INPUT). Stored scores reproduced exactly before resampling.
Bootstrap B=2000 (stratified by category; cluster variant over 133782 identical-reference clusters). Approximate randomization R=10000.

## Primary comparisons, seed-mean (A − B)

| A | B | Metric | Δ | 95% CI | Cluster 95% CI | p (AR) | p (Holm) | Seeds A>B |
|---|---|---|---:|---|---|---:|---:|---:|
| spbpe_5k | spbpe_20k | chrf2_pct | +0.1868 | [+0.1735, +0.1997] | [+0.1739, +0.1998] | 0.0001 | 0.0006 | 3/3 |
| spbpe_5k | spbpe_20k | bleu | +0.4313 | [+0.4049, +0.4573] | [+0.4048, +0.4578] | 0.0001 | 0.0006 | 3/3 |
| spbpe_5k | spbpe_20k | exact_match_pct | +3.2317 | [+3.0788, +3.3747] | [+3.0826, +3.3857] | 0.0001 | 0.0006 | 3/3 |
| wp_5k | wp_20k | chrf2_pct | +0.2440 | [+0.2308, +0.2570] | [+0.2312, +0.2571] | 0.0001 | 0.0006 | 3/3 |
| wp_5k | wp_20k | bleu | +0.5051 | [+0.4799, +0.5300] | [+0.4787, +0.5324] | 0.0001 | 0.0006 | 3/3 |
| wp_5k | wp_20k | exact_match_pct | +3.5493 | [+3.3944, +3.7105] | [+3.3934, +3.7115] | 0.0001 | 0.0006 | 3/3 |
| spuni_5k | spuni_20k | chrf2_pct | +0.1097 | [+0.0979, +0.1216] | [+0.0973, +0.1217] | 0.0001 | 0.0006 | 3/3 |
| spuni_5k | spuni_20k | bleu | +0.1102 | [+0.0866, +0.1328] | [+0.0861, +0.1329] | 0.0001 | 0.0006 | 2/3 |
| spuni_5k | spuni_20k | exact_match_pct | +1.2311 | [+1.0908, +1.3714] | [+1.0892, +1.3794] | 0.0001 | 0.0006 | 3/3 |
| spbpe_5k | wp_5k | chrf2_pct | +0.0079 | [-0.0010, +0.0168] | [-0.0012, +0.0173] | 0.0825 | 0.0825 | 1/3 |
| spbpe_5k | wp_5k | bleu | +0.0156 | [-0.0024, +0.0346] | [-0.0029, +0.0356] | 0.1014 | 0.1014 | 1/3 |
| spbpe_5k | wp_5k | exact_match_pct | +0.0880 | [-0.0326, +0.2057] | [-0.0353, +0.2042] | 0.1429 | 0.1429 | 1/3 |
| spbpe_5k | spuni_5k | chrf2_pct | +0.0371 | [+0.0263, +0.0483] | [+0.0274, +0.0482] | 0.0001 | 0.0006 | 2/3 |
| spbpe_5k | spuni_5k | bleu | +0.1183 | [+0.0978, +0.1406] | [+0.0977, +0.1401] | 0.0001 | 0.0006 | 2/3 |
| spbpe_5k | spuni_5k | exact_match_pct | +0.8026 | [+0.6735, +0.9337] | [+0.6719, +0.9357] | 0.0001 | 0.0006 | 2/3 |
| wp_5k | spuni_5k | chrf2_pct | +0.0292 | [+0.0188, +0.0398] | [+0.0183, +0.0398] | 0.0001 | 0.0006 | 2/3 |
| wp_5k | spuni_5k | bleu | +0.1026 | [+0.0815, +0.1239] | [+0.0810, +0.1251] | 0.0001 | 0.0006 | 3/3 |
| wp_5k | spuni_5k | exact_match_pct | +0.7145 | [+0.5924, +0.8374] | [+0.5893, +0.8480] | 0.0001 | 0.0006 | 3/3 |

## Family x vocabulary interaction: (A5K − A20K) − (B5K − B20K), seed-mean

| A | B | Metric | Interaction | 95% CI | p (boot) | Seeds > 0 |
|---|---|---|---:|---|---:|---:|
| spbpe | spuni | chrf2_pct | +0.0771 | [+0.0616, +0.0937] | 0.0000 | 2/3 |
| spbpe | spuni | bleu | +0.3211 | [+0.2920, +0.3500] | 0.0000 | 3/3 |
| spbpe | spuni | exact_match_pct | +2.0006 | [+1.8218, +2.1737] | 0.0000 | 3/3 |
| wp | spuni | chrf2_pct | +0.1343 | [+0.1200, +0.1485] | 0.0000 | 3/3 |
| wp | spuni | bleu | +0.3949 | [+0.3659, +0.4224] | 0.0000 | 3/3 |
| wp | spuni | exact_match_pct | +2.3182 | [+2.1528, +2.4963] | 0.0000 | 3/3 |
| spbpe | wp | chrf2_pct | -0.0572 | [-0.0721, -0.0423] | 0.0000 | 1/3 |
| spbpe | wp | bleu | -0.0738 | [-0.1023, -0.0467] | 0.0000 | 1/3 |
| spbpe | wp | exact_match_pct | -0.3176 | [-0.4880, -0.1512] | 0.0000 | 2/3 |

## Probability of highest seed-mean score (bootstrap)

| Budget | Metric | Tag | Seed-mean | P(best) |
|---|---|---|---:|---:|
| 5k | chrf2_pct | spbpe_5k | 96.1701 | 0.962 |
| 5k | chrf2_pct | wp_5k | 96.1622 | 0.038 |
| 5k | chrf2_pct | spuni_5k | 96.1331 | 0.000 |
| 5k | bleu | spbpe_5k | 92.1871 | 0.950 |
| 5k | bleu | wp_5k | 92.1714 | 0.051 |
| 5k | bleu | spuni_5k | 92.0688 | 0.000 |
| 5k | exact_match_pct | spbpe_5k | 45.0167 | 0.922 |
| 5k | exact_match_pct | wp_5k | 44.9287 | 0.077 |
| 5k | exact_match_pct | spuni_5k | 44.2141 | 0.000 |
| 20k | chrf2_pct | spbpe_20k | 95.9833 | 0.000 |
| 20k | chrf2_pct | wp_20k | 95.9182 | 0.000 |
| 20k | chrf2_pct | spuni_20k | 96.0234 | 1.000 |
| 20k | bleu | spbpe_20k | 91.7557 | 0.000 |
| 20k | bleu | wp_20k | 91.6663 | 0.000 |
| 20k | bleu | spuni_20k | 91.9586 | 1.000 |
| 20k | exact_match_pct | spbpe_20k | 41.7850 | 0.000 |
| 20k | exact_match_pct | wp_20k | 41.3793 | 0.000 |
| 20k | exact_match_pct | spuni_20k | 42.9830 | 1.000 |

## Per-seed primary tests (chrF2 and exact match)

| A | B | Seed | Metric | Δ | 95% CI | p (AR) | p (Holm, 18) |
|---|---|---:|---|---:|---|---:|---:|
| spbpe_5k | spbpe_20k | 42 | chrf2_pct | +0.1347 | [+0.1184, +0.1507] | 0.0001 | 0.0018 |
| spbpe_5k | spbpe_20k | 43 | chrf2_pct | +0.2213 | [+0.2041, +0.2393] | 0.0001 | 0.0018 |
| spbpe_5k | spbpe_20k | 44 | chrf2_pct | +0.2044 | [+0.1874, +0.2203] | 0.0001 | 0.0018 |
| spbpe_5k | spbpe_20k | 42 | exact_match_pct | +2.7480 | [+2.5532, +2.9413] | 0.0001 | 0.0018 |
| spbpe_5k | spbpe_20k | 43 | exact_match_pct | +3.0315 | [+2.8383, +3.2159] | 0.0001 | 0.0018 |
| spbpe_5k | spbpe_20k | 44 | exact_match_pct | +3.9157 | [+3.7179, +4.1112] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 42 | chrf2_pct | +0.2455 | [+0.2281, +0.2616] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 43 | chrf2_pct | +0.1825 | [+0.1651, +0.1997] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 44 | chrf2_pct | +0.3042 | [+0.2880, +0.3211] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 42 | exact_match_pct | +4.1313 | [+3.9381, +4.3306] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 43 | exact_match_pct | +2.6846 | [+2.4958, +2.8838] | 0.0001 | 0.0018 |
| wp_5k | wp_20k | 44 | exact_match_pct | +3.8321 | [+3.6299, +4.0313] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 42 | chrf2_pct | +0.1397 | [+0.1231, +0.1556] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 43 | chrf2_pct | +0.0037 | [-0.0129, +0.0211] | 0.6654 | 1.0000 |
| spuni_5k | spuni_20k | 44 | chrf2_pct | +0.1857 | [+0.1701, +0.2016] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 42 | exact_match_pct | +1.3139 | [+1.1259, +1.5027] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 43 | exact_match_pct | +0.5536 | [+0.3633, +0.7484] | 0.0001 | 0.0018 |
| spuni_5k | spuni_20k | 44 | exact_match_pct | +1.8258 | [+1.6445, +2.0108] | 0.0001 | 0.0018 |
| spbpe_5k | wp_5k | 42 | chrf2_pct | -0.0575 | [-0.0700, -0.0456] | 0.0001 | 0.0018 |
| spbpe_5k | wp_5k | 43 | chrf2_pct | +0.0991 | [+0.0830, +0.1152] | 0.0001 | 0.0018 |
| spbpe_5k | wp_5k | 44 | chrf2_pct | -0.0178 | [-0.0325, -0.0045] | 0.0100 | 0.0400 |
| spbpe_5k | wp_5k | 42 | exact_match_pct | -0.0612 | [-0.2313, +0.1127] | 0.4857 | 0.4857 |
| spbpe_5k | wp_5k | 43 | exact_match_pct | +1.0110 | [+0.8416, +1.1729] | 0.0001 | 0.0018 |
| spbpe_5k | wp_5k | 44 | exact_match_pct | -0.6857 | [-0.8595, -0.5073] | 0.0001 | 0.0018 |
| spbpe_5k | spuni_5k | 42 | chrf2_pct | +0.0395 | [+0.0245, +0.0543] | 0.0001 | 0.0018 |
| spbpe_5k | spuni_5k | 43 | chrf2_pct | +0.1025 | [+0.0876, +0.1178] | 0.0001 | 0.0018 |
| spbpe_5k | spuni_5k | 44 | chrf2_pct | -0.0308 | [-0.0461, -0.0156] | 0.0002 | 0.0018 |
| spbpe_5k | spuni_5k | 42 | exact_match_pct | +1.1811 | [+1.0050, +1.3684] | 0.0001 | 0.0018 |
| spbpe_5k | spuni_5k | 43 | exact_match_pct | +1.3341 | [+1.1565, +1.5065] | 0.0001 | 0.0018 |
| spbpe_5k | spuni_5k | 44 | exact_match_pct | -0.1074 | [-0.2836, +0.0717] | 0.2396 | 0.4792 |
| wp_5k | spuni_5k | 42 | chrf2_pct | +0.0970 | [+0.0821, +0.1117] | 0.0001 | 0.0018 |
| wp_5k | spuni_5k | 43 | chrf2_pct | +0.0034 | [-0.0112, +0.0186] | 0.6605 | 1.0000 |
| wp_5k | spuni_5k | 44 | chrf2_pct | -0.0129 | [-0.0266, +0.0026] | 0.0773 | 0.2319 |
| wp_5k | spuni_5k | 42 | exact_match_pct | +1.2423 | [+1.0699, +1.4184] | 0.0001 | 0.0018 |
| wp_5k | spuni_5k | 43 | exact_match_pct | +0.3231 | [+0.1470, +0.4917] | 0.0004 | 0.0018 |
| wp_5k | spuni_5k | 44 | exact_match_pct | +0.5783 | [+0.4014, +0.7596] | 0.0001 | 0.0018 |

## Category chrF2: 5K − 20K and condition − COPY (seed-mean, descriptive, unadjusted)

| Category | n | A | B | Δ chrF2 | 95% CI | Excludes 0 |
|---|---:|---|---|---:|---|---|
| afiksasi | 26322 | spbpe_5k | spbpe_20k | +0.1800 | [+0.1539, +0.2072] | yes |
| afiksasi | 26322 | wp_5k | wp_20k | +0.1413 | [+0.1132, +0.1712] | yes |
| afiksasi | 26322 | spuni_5k | spuni_20k | -0.0018 | [-0.0299, +0.0247] | no |
| afiksasi | 26322 | spbpe_5k | COPY_INPUT | +13.6714 | [+13.4946, +13.8169] | yes |
| afiksasi | 26322 | spbpe_20k | COPY_INPUT | +13.4914 | [+13.3026, +13.6425] | yes |
| afiksasi | 26322 | wp_5k | COPY_INPUT | +13.5800 | [+13.3987, +13.7271] | yes |
| afiksasi | 26322 | wp_20k | COPY_INPUT | +13.4387 | [+13.2658, +13.5817] | yes |
| afiksasi | 26322 | spuni_5k | COPY_INPUT | +13.5241 | [+13.3499, +13.6726] | yes |
| afiksasi | 26322 | spuni_20k | COPY_INPUT | +13.5259 | [+13.3566, +13.6656] | yes |
| ambigu | 6603 | spbpe_5k | spbpe_20k | -0.0336 | [-0.0943, +0.0271] | no |
| ambigu | 6603 | wp_5k | wp_20k | -0.0796 | [-0.1300, -0.0305] | yes |
| ambigu | 6603 | spuni_5k | spuni_20k | -0.0642 | [-0.1294, -0.0106] | yes |
| ambigu | 6603 | spbpe_5k | COPY_INPUT | +1.3794 | [+1.1477, +1.5647] | yes |
| ambigu | 6603 | spbpe_20k | COPY_INPUT | +1.4130 | [+1.1536, +1.6199] | yes |
| ambigu | 6603 | wp_5k | COPY_INPUT | +1.3402 | [+1.0903, +1.5438] | yes |
| ambigu | 6603 | wp_20k | COPY_INPUT | +1.4198 | [+1.1829, +1.6106] | yes |
| ambigu | 6603 | spuni_5k | COPY_INPUT | +1.4033 | [+1.1569, +1.5974] | yes |
| ambigu | 6603 | spuni_20k | COPY_INPUT | +1.4675 | [+1.2483, +1.6452] | yes |
| ambigu_claude | 349 | spbpe_5k | spbpe_20k | -0.3410 | [-0.7004, +0.0146] | no |
| ambigu_claude | 349 | wp_5k | wp_20k | -0.0245 | [-0.3390, +0.3036] | no |
| ambigu_claude | 349 | spuni_5k | spuni_20k | +0.2724 | [-0.0708, +0.6601] | no |
| ambigu_claude | 349 | spbpe_5k | COPY_INPUT | -1.4172 | [-1.8436, -1.0191] | yes |
| ambigu_claude | 349 | spbpe_20k | COPY_INPUT | -1.0762 | [-1.4448, -0.7421] | yes |
| ambigu_claude | 349 | wp_5k | COPY_INPUT | -1.3398 | [-1.6986, -0.9818] | yes |
| ambigu_claude | 349 | wp_20k | COPY_INPUT | -1.3153 | [-1.7093, -0.9245] | yes |
| ambigu_claude | 349 | spuni_5k | COPY_INPUT | -1.4091 | [-2.1123, -0.8873] | yes |
| ambigu_claude | 349 | spuni_20k | COPY_INPUT | -1.6816 | [-2.4536, -1.0898] | yes |
| diksi | 14123 | spbpe_5k | spbpe_20k | -0.0909 | [-0.1302, -0.0510] | yes |
| diksi | 14123 | wp_5k | wp_20k | -0.0169 | [-0.0482, +0.0147] | no |
| diksi | 14123 | spuni_5k | spuni_20k | -0.0545 | [-0.0855, -0.0246] | yes |
| diksi | 14123 | spbpe_5k | COPY_INPUT | -1.1246 | [-1.2075, -1.0498] | yes |
| diksi | 14123 | spbpe_20k | COPY_INPUT | -1.0337 | [-1.1337, -0.9465] | yes |
| diksi | 14123 | wp_5k | COPY_INPUT | -1.0851 | [-1.1770, -1.0023] | yes |
| diksi | 14123 | wp_20k | COPY_INPUT | -1.0682 | [-1.1553, -0.9909] | yes |
| diksi | 14123 | spuni_5k | COPY_INPUT | -1.0748 | [-1.1668, -0.9930] | yes |
| diksi | 14123 | spuni_20k | COPY_INPUT | -1.0202 | [-1.1061, -0.9442] | yes |
| diksi_claude | 349 | spbpe_5k | spbpe_20k | -0.4449 | [-0.7900, -0.0687] | yes |
| diksi_claude | 349 | wp_5k | wp_20k | -0.2042 | [-0.6021, +0.1541] | no |
| diksi_claude | 349 | spuni_5k | spuni_20k | -0.0948 | [-0.4230, +0.2477] | no |
| diksi_claude | 349 | spbpe_5k | COPY_INPUT | +0.4112 | [-0.0753, +0.8699] | no |
| diksi_claude | 349 | spbpe_20k | COPY_INPUT | +0.8561 | [+0.4114, +1.2922] | yes |
| diksi_claude | 349 | wp_5k | COPY_INPUT | +0.5346 | [+0.0437, +1.0038] | yes |
| diksi_claude | 349 | wp_20k | COPY_INPUT | +0.7388 | [+0.2656, +1.2353] | yes |
| diksi_claude | 349 | spuni_5k | COPY_INPUT | +0.6682 | [+0.2522, +1.0875] | yes |
| diksi_claude | 349 | spuni_20k | COPY_INPUT | +0.7630 | [+0.3166, +1.1817] | yes |
| kelengkapan_kalimat | 15877 | spbpe_5k | spbpe_20k | -0.2251 | [-0.2612, -0.1883] | yes |
| kelengkapan_kalimat | 15877 | wp_5k | wp_20k | -0.1431 | [-0.1788, -0.1081] | yes |
| kelengkapan_kalimat | 15877 | spuni_5k | spuni_20k | -0.0782 | [-0.1112, -0.0456] | yes |
| kelengkapan_kalimat | 15877 | spbpe_5k | COPY_INPUT | -0.5546 | [-0.6409, -0.4811] | yes |
| kelengkapan_kalimat | 15877 | spbpe_20k | COPY_INPUT | -0.3295 | [-0.4218, -0.2522] | yes |
| kelengkapan_kalimat | 15877 | wp_5k | COPY_INPUT | -0.5114 | [-0.6037, -0.4338] | yes |
| kelengkapan_kalimat | 15877 | wp_20k | COPY_INPUT | -0.3683 | [-0.4505, -0.2929] | yes |
| kelengkapan_kalimat | 15877 | spuni_5k | COPY_INPUT | -0.4435 | [-0.5240, -0.3761] | yes |
| kelengkapan_kalimat | 15877 | spuni_20k | COPY_INPUT | -0.3654 | [-0.4470, -0.2971] | yes |
| pembentukan_kata | 16373 | spbpe_5k | spbpe_20k | +0.8048 | [+0.7709, +0.8378] | yes |
| pembentukan_kata | 16373 | wp_5k | wp_20k | +0.9826 | [+0.9471, +1.0185] | yes |
| pembentukan_kata | 16373 | spuni_5k | spuni_20k | +0.4932 | [+0.4653, +0.5203] | yes |
| pembentukan_kata | 16373 | spbpe_5k | COPY_INPUT | +13.2049 | [+13.0277, +13.3677] | yes |
| pembentukan_kata | 16373 | spbpe_20k | COPY_INPUT | +12.4001 | [+12.2212, +12.5651] | yes |
| pembentukan_kata | 16373 | wp_5k | COPY_INPUT | +13.1256 | [+12.9467, +13.2906] | yes |
| pembentukan_kata | 16373 | wp_20k | COPY_INPUT | +12.1430 | [+11.9702, +12.3024] | yes |
| pembentukan_kata | 16373 | spuni_5k | COPY_INPUT | +13.1697 | [+12.9915, +13.3308] | yes |
| pembentukan_kata | 16373 | spuni_20k | COPY_INPUT | +12.6765 | [+12.5013, +12.8424] | yes |
| pleonasme | 2717 | spbpe_5k | spbpe_20k | +0.0673 | [-0.0311, +0.1463] | no |
| pleonasme | 2717 | wp_5k | wp_20k | +0.1498 | [+0.0753, +0.2402] | yes |
| pleonasme | 2717 | spuni_5k | spuni_20k | +0.1230 | [+0.0642, +0.1819] | yes |
| pleonasme | 2717 | spbpe_5k | COPY_INPUT | +2.6128 | [+2.4804, +2.7400] | yes |
| pleonasme | 2717 | spbpe_20k | COPY_INPUT | +2.5456 | [+2.4352, +2.6594] | yes |
| pleonasme | 2717 | wp_5k | COPY_INPUT | +2.6559 | [+2.5380, +2.7708] | yes |
| pleonasme | 2717 | wp_20k | COPY_INPUT | +2.5061 | [+2.3767, +2.6277] | yes |
| pleonasme | 2717 | spuni_5k | COPY_INPUT | +2.6467 | [+2.5156, +2.7716] | yes |
| pleonasme | 2717 | spuni_20k | COPY_INPUT | +2.5237 | [+2.3821, +2.6642] | yes |
| pleonasme_claude | 350 | spbpe_5k | spbpe_20k | -0.5801 | [-0.8949, -0.2829] | yes |
| pleonasme_claude | 350 | wp_5k | wp_20k | +0.1445 | [-0.1907, +0.5243] | no |
| pleonasme_claude | 350 | spuni_5k | spuni_20k | -0.0260 | [-0.2803, +0.2174] | no |
| pleonasme_claude | 350 | spbpe_5k | COPY_INPUT | -1.9739 | [-2.4114, -1.5839] | yes |
| pleonasme_claude | 350 | spbpe_20k | COPY_INPUT | -1.3938 | [-1.6960, -1.1103] | yes |
| pleonasme_claude | 350 | wp_5k | COPY_INPUT | -1.6735 | [-2.0513, -1.3153] | yes |
| pleonasme_claude | 350 | wp_20k | COPY_INPUT | -1.8180 | [-2.2523, -1.4247] | yes |
| pleonasme_claude | 350 | spuni_5k | COPY_INPUT | -1.7902 | [-2.1755, -1.4585] | yes |
| pleonasme_claude | 350 | spuni_20k | COPY_INPUT | -1.7641 | [-2.1585, -1.4149] | yes |
| preposisi | 16774 | spbpe_5k | spbpe_20k | -0.0548 | [-0.0862, -0.0237] | yes |
| preposisi | 16774 | wp_5k | wp_20k | -0.0821 | [-0.1160, -0.0509] | yes |
| preposisi | 16774 | spuni_5k | spuni_20k | -0.1317 | [-0.1710, -0.0973] | yes |
| preposisi | 16774 | spbpe_5k | COPY_INPUT | +2.7173 | [+2.5732, +2.8365] | yes |
| preposisi | 16774 | spbpe_20k | COPY_INPUT | +2.7721 | [+2.6251, +2.8964] | yes |
| preposisi | 16774 | wp_5k | COPY_INPUT | +2.7099 | [+2.5566, +2.8337] | yes |
| preposisi | 16774 | wp_20k | COPY_INPUT | +2.7921 | [+2.6524, +2.9039] | yes |
| preposisi | 16774 | spuni_5k | COPY_INPUT | +2.7286 | [+2.5770, +2.8511] | yes |
| preposisi | 16774 | spuni_20k | COPY_INPUT | +2.8602 | [+2.7369, +2.9652] | yes |
| reduplikasi | 8927 | spbpe_5k | spbpe_20k | +0.1523 | [+0.1178, +0.1896] | yes |
| reduplikasi | 8927 | wp_5k | wp_20k | +0.1279 | [+0.0989, +0.1605] | yes |
| reduplikasi | 8927 | spuni_5k | spuni_20k | +0.1159 | [+0.0819, +0.1485] | yes |
| reduplikasi | 8927 | spbpe_5k | COPY_INPUT | +1.4143 | [+1.2713, +1.5397] | yes |
| reduplikasi | 8927 | spbpe_20k | COPY_INPUT | +1.2620 | [+1.0985, +1.4061] | yes |
| reduplikasi | 8927 | wp_5k | COPY_INPUT | +1.4066 | [+1.2546, +1.5385] | yes |
| reduplikasi | 8927 | wp_20k | COPY_INPUT | +1.2786 | [+1.1261, +1.4097] | yes |
| reduplikasi | 8927 | spuni_5k | COPY_INPUT | +1.4223 | [+1.2644, +1.5551] | yes |
| reduplikasi | 8927 | spuni_20k | COPY_INPUT | +1.3063 | [+1.1587, +1.4359] | yes |
| sintaksis_frasa | 25261 | spbpe_5k | spbpe_20k | +0.5074 | [+0.4695, +0.5424] | yes |
| sintaksis_frasa | 25261 | wp_5k | wp_20k | +0.6762 | [+0.6361, +0.7163] | yes |
| sintaksis_frasa | 25261 | spuni_5k | spuni_20k | +0.4247 | [+0.3889, +0.4609] | yes |
| sintaksis_frasa | 25261 | spbpe_5k | COPY_INPUT | +8.0542 | [+7.9083, +8.1905] | yes |
| sintaksis_frasa | 25261 | spbpe_20k | COPY_INPUT | +7.5467 | [+7.4084, +7.6843] | yes |
| sintaksis_frasa | 25261 | wp_5k | COPY_INPUT | +8.1209 | [+7.9687, +8.2659] | yes |
| sintaksis_frasa | 25261 | wp_20k | COPY_INPUT | +7.4448 | [+7.3046, +7.5754] | yes |
| sintaksis_frasa | 25261 | spuni_5k | COPY_INPUT | +7.9056 | [+7.7572, +8.0427] | yes |
| sintaksis_frasa | 25261 | spuni_20k | COPY_INPUT | +7.4809 | [+7.3371, +7.6127] | yes |

Interpretation limits: intervals are conditional on the trained checkpoints; they do not measure training-seed variance. Seed agreement (Seeds A>B) and the per-seed table carry that information separately.

Send back: REPORT.md, paired_overall.csv, paired_per_seed.csv, prob_best.csv, paired_categories.csv, provenance.json.
