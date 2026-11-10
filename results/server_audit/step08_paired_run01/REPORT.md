# Exploratory paired exact match

9 previously scored seed42 runs + COPY_INPUT; 134025 unchanged test rows.

45 paired comparisons. All exact-match rates reproduce Step07.

Positive delta means A matches more full reference sentences than B. A-only/B-only counts reveal disagreements hidden by aggregate rates.

Intervals assume independent rows, not documents; repeated targets/unknown document groups can violate this assumption. Intervals are exploratory, unadjusted for multiple comparisons, and conditional on fixed checkpoints. They cannot establish a universally best tokenizer, training-seed robustness or significance for chrF/BLEU.

Send REPORT.md, paired_exact.csv, paired_exact_categories.csv and provenance.json.
