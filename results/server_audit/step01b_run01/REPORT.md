# Step 1b: row-level overlap

Counts below are affected ROWS, not unique sentences. Flags overlap and must not be summed.

| Split | Flag | Rows | % of split |
|---|---|---:|---:|
| train | any_flag | 281 | 0.0262 |
| train | duplicate_pair_after_first_in_split | 281 | 0.0262 |
| valid | any_flag | 2717 | 2.0272 |
| valid | target_in_train | 2707 | 2.0198 |
| valid | source_in_train | 64 | 0.0478 |
| valid | pair_in_train | 53 | 0.0395 |
| valid | duplicate_pair_after_first_in_split | 6 | 0.0045 |
| test | any_flag | 2991 | 2.2317 |
| test | target_in_train | 2721 | 2.0302 |
| test | target_in_valid | 395 | 0.2947 |
| test | source_in_train | 63 | 0.0470 |
| test | pair_in_train | 57 | 0.0425 |
| test | source_in_valid | 15 | 0.0112 |
| test | pair_in_valid | 14 | 0.0104 |
| test | duplicate_pair_after_first_in_split | 5 | 0.0037 |

Affected IDs use zero-based raw-file order and are for investigation only.
Do not delete rows or resplit automatically. These IDs do not define a new clean benchmark.
No source/target text is exported. Send REPORT.md, JSON and affected_ids CSV files.
