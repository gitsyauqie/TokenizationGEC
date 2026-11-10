# Reference audit for revised Paper 6

Checked 26 October 2026. `verified_references.tex` contains 18 bibliographic entries for selective use; this file does not change the manuscript.

## Findings affecting the paper's argument

1. **Do not claim that prior Indonesian GEC never varied tokenization or vocabulary.** Musyafa et al. (2022), Table 4, compares BPEChar 30K, 10K and 1K. CASTLE's publisher abstract/experimental setup also explicitly investigates whitespace, BPE, Unigram and WordPiece. The defensible contribution is the present common-surface, capacity-matched-within-budget, three-seed comparison of three implementations at two vocabulary budgets, together with copy-baseline and category analysis. Sources: [Musyafa 2022](https://www.mdpi.com/2076-3417/12/20/10380), [CASTLE](https://www.sciencedirect.com/science/article/abs/pii/S0957417425038485).
2. **Distinguish historical WordPiece from the actual trainer.** The pinned Hugging Face 0.20.3 WordPiece trainer wraps `BpeTrainer`. Consequently the draft's claim that this implementation selects merges by maximizing likelihood is inappropriate. Cite Schuster and Nakajima for the historical method, and the pinned implementation for reproducibility. [Official source](https://raw.githubusercontent.com/huggingface/tokenizers/v0.20.3/tokenizers/src/models/wordpiece/trainer.rs). Current unversioned documentation has changed and is less useful than this pinned source.
3. **CASTLE citation is genuine.** Publisher record confirms six authors in the draft's order, Expert Systems with Applications 299, Part D, 130233, 1 March 2026; DOI 10.1016/j.eswa.2025.130233. DOI includes 2025 while issue year is 2026: this is not an error. Source: [publisher abstract record](https://www.sciencedirect.com/science/article/abs/pii/S0957417425038485). Direct full-text fetch returned 403; citation metadata is available in indexed publisher record. Do not use reconstructed GitHub metrics as published paper results.
4. **Remove the old Sastrawi thesis attribution unless independently substantiated.** The draft combines A. D. Suhartini's alleged 2011 thesis citation with the Sastrawi repository URL, which does not establish that this thesis authored the software. The present experiments do not use morphological boundary metrics, so neither Sastrawi nor Zemberek needs to remain as methodological evidence.
5. **The anonymous low-resource survey citation is misattributed.** The title and DOI are real, but authors are Syauqie Muhammad Marier, Xiangfan Chen, Linan Zhu, and Xiangjie Kong (PeerJ Computer Science 11:e3044, 2025, DOI 10.7717/peerj-cs.3044). Do not cite it as Anonymous. [Publisher PDF](https://peerj.com/articles/cs-3044.pdf). Omitted from the compact bibliography to avoid redundant self-citation; it can be restored accurately if needed.
6. **Vemula et al. 2025 is genuine, not an invented citation.** ACL record verifies title/authors and work on Telugu, with preliminary Hindi/English experiments. It is relevant recent context, but its language-model findings must not be presented as established GEC outcomes. [ACL record](https://aclanthology.org/2025.ijcnlp-srw.20/).
7. **No Turkish result is currently supported by the controlled experiment record.** GECTurk is a genuine benchmark and can appear as a prospective extension. Its citation cannot substantiate claimed completed Turkish replication or justify excluding WordPiece from edit evaluation without a tested detokenization protocol. [GECTurk](https://aclanthology.org/2023.findings-ijcnlp.26/).
8. **Evaluation citations must match what was actually measured.** chrF and BLEU are text-similarity metrics, not edit-correction accuracy; SacreBLEU supports reproducible implementation reporting. M2 and ERRANT are relevant when explaining future edit-based evaluation, but must not imply these scores were computed in the current study. Exact match needs its own explicit definition, not a borrowed F-score citation.

## Core primary sources verified

| Citation key | Primary source | Role |
|---|---|---|
| sennrich2016 | [ACL 2016](https://aclanthology.org/P16-1162/) | BPE in neural sequence transduction |
| kudo2018 | [ACL 2018](https://aclanthology.org/P18-1007/) | Unigram model; distinguish deterministic use from sampled regularization |
| kudo2018sentencepiece | [EMNLP demo](https://aclanthology.org/D18-2012/) | Actual SP-BPE and SP-Unigram software |
| schuster2012 | [Google Research author record](https://research.google/pubs/japanese-and-korean-voice-search/) | WordPiece origin |
| hfwordpiece | [Pinned official source](https://github.com/huggingface/tokenizers/blob/v0.20.3/tokenizers/src/models/wordpiece/trainer.rs) | Actual training implementation |
| bostrom2020 | [Findings EMNLP](https://aclanthology.org/2020.findings-emnlp.414/) | Morphology and task-sensitive tokenizer comparison, English/Japanese LM setting |
| vaswani2017 | [NeurIPS](https://papers.nips.cc/paper/7181-attention-is-all-you-need) | Transformer architecture |
| ott2019 | [NAACL demo](https://aclanthology.org/N19-4009/) | Fairseq |
| papineni2002 | [ACL 2002](https://aclanthology.org/P02-1040/) | BLEU |
| popovic2015 | [WMT 2015](https://aclanthology.org/W15-3049/) | chrF |
| post2018 | [WMT 2018](https://aclanthology.org/W18-6319/) | SacreBLEU and reporting comparability |
| dahlmeier2012 | [NAACL 2012](https://aclanthology.org/N12-1067/) | M2 edit-based scoring context |
| bryant2017 | [ACL 2017](https://aclanthology.org/P17-1074/) | ERRANT and error-type evaluation context |
| musyafa2022 | [Publisher](https://www.mdpi.com/2076-3417/12/20/10380) | Indonesian synthetic GEC; previous vocabulary comparison |
| musyafa2024 | [Publisher PDF](https://peerj.com/articles/cs-2122.pdf) | Indonesian GEC and synthetic data methods |
| marier2026castle | [Publisher](https://www.sciencedirect.com/science/article/abs/pii/S0957417425038485) | IGED predecessor; distinct architecture study |
| gecturk | [ACL](https://aclanthology.org/2023.findings-ijcnlp.26/) | Future cross-language extension only |
| unigramdominance2025 | [ACL](https://aclanthology.org/2025.ijcnlp-srw.20/) | Recent morphology/tokenization context |

## Scope of audit

Foundational and manuscript-relevant entries above were verified; older citations to knowledge-guided classification/NER and the Lin/Toraman/Icelandic papers were not needed for the revised argument and are not certified here. Removing an irrelevant citation does not mean it is fabricated. No citation-count claims are made: importance is assessed by direct methodological relevance and foundational role.
