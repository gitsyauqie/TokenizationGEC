# TokenizationGEC

This repository holds the code and experiment records for the paper

> Vocabulary Budget and Tokenizer Family in Synthetic Grammatical Error Correction: A Controlled Study
> (under review; Indonesian and Turkish).

We compare SentencePiece BPE, WordPiece (Hugging Face `tokenizers` 0.20.3) and SentencePiece Unigram at vocabulary sizes of 5,000 and 20,000. All six conditions use the same Transformer encoder-decoder in Fairseq, trained from scratch with seeds 42, 43 and 44, which gives 18 Indonesian runs. The checkpoint of each run is chosen by validation chrF2 and frozen before any test output is produced. The same design is repeated on GECTurk. We also report an overlap sensitivity analysis, a continuation of training to 20 epochs, and an Indonesian control with the same training size as GECTurk.

If you use this repository, please cite the paper. GitHub's "Cite this repository" button reads [`CITATION.cff`](CITATION.cff). Until the paper is published, you can cite the repository:

```bibtex
@misc{marier2026tokenizationgec,
  author       = {Marier, Syauqie Muhammad},
  title        = {{TokenizationGEC}: code and experiment records for ``Vocabulary Budget and Tokenizer Family in Synthetic Grammatical Error Correction: A Controlled Study''},
  year         = {2026},
  howpublished = {\url{https://github.com/gitsyauqie/TokenizationGEC}}
}
```

## Data and Code Availability

Code. The scripts for data preparation, tokenizer training, model training, evaluation and statistics are in [`scripts/`](scripts). Unit tests are in [`tests/`](tests), and the code we used to build the IGED corpus is in [`createIGED/`](createIGED). Everything is released under the MIT license ([`LICENSE`](LICENSE)).

Experiment records. [`results/`](results) contains what is needed to check the numbers in the paper without retraining:
- validation chrF2 per epoch and the selected checkpoint of every run;
- the frozen test scores of all runs;
- paired bootstrap and approximate randomization results, and edit-level scores (precision, recall, F0.5, GLEU);
- tokenization statistics;
- manifests with SHA-256 hashes of scripts, data, tokenizers and checkpoints;
- the fitted tokenizers (SentencePiece `.model`, WordPiece `tokenizer.json`) and the shared dictionaries of the six conditions;
- the software versions (`fairseq 0.10.2`, `torch 2.4.1+cu121`, `sacrebleu 1.5.1`, `sentencepiece 0.2.0`, `tokenizers 0.20.3`).

Data. We do not redistribute the corpora, because redistribution depends on the permission of the data owners.
- IGED (Indonesian): we use the snapshot from our earlier work (Marier et al., CASTLE, Expert Systems with Applications 299, 130233, 2026, [doi:10.1016/j.eswa.2025.130233](https://doi.org/10.1016/j.eswa.2025.130233)). Our split can be rebuilt from the original row indices. Only two pairs were removed (one in training, one in validation, both exact API-failure markers), and they are listed in [`results/indonesian/prepared_v2/excluded_ids.csv`](results/indonesian/prepared_v2/excluded_ids.csv). The hashes of the input files are in `results/server_audit/step01_run01/audit.json`. Access to the snapshot follows the conditions of the data owners, so please contact the corresponding author.
- GECTurk (Turkish): a public corpus by Kara et al. (Findings of IJCNLP-AACL 2023, [doi:10.18653/v1/2023.findings-ijcnlp.26](https://doi.org/10.18653/v1/2023.findings-ijcnlp.26)). We use its released synthetic split (96,919 / 20,769 / 20,769 pairs).

Models. We do not include the checkpoints (about 14M parameters at the 5K vocabulary and 22M at 20K) because of their size. Their hashes are in [`results/indonesian/frozen_test_checkpoint_manifest.json`](results/indonesian/frozen_test_checkpoint_manifest.json), and they can be trained again from the data and scripts with the recorded seeds.

## Repository layout

| Path | Content |
|---|---|
| `scripts/` | Pipeline (see table below) |
| `tests/` | Unit tests for the audit, preparation, required-character and reconstruction gates |
| `createIGED/` | Code used to construct the IGED corpus |
| `results/indonesian/` | Main Indonesian experiment: `prepared_v2/` (manifests, tokenizers, dictionaries), `controlled_training_seed42|43|44/` (per-epoch validation state, selected checkpoints, config), `controlled_test_v1/` (frozen test scores), `paired_stats_v1/`, `gec_metrics_v1/`, `val_curves_m1a/`, `ext20_results/` (continuation to epoch 20), `m13m14_results/` (overlap sensitivity), `tokenization_stats_m6/` |
| `results/turkish_gecturk/` | GECTurk replication (same design, case preserved) |
| `results/size_control_m7b/` | Indonesian control with 96,919 training pairs (the GECTurk scale) |
| `results/server_audit/` | Step-by-step audit records (hashes, overlap, API-marker count, reconstruction checks); sentence-level example files are omitted |
| `results/createiged_audit/` | Checks on the IGED construction code |
| `docs/` | Audit findings, experiment plan, the SentencePiece rare-character fix, reference audit |

## Pipeline

Commands are run from the repository root, and `--help` on each Python script lists its arguments. Most scripts write to a new output directory and refuse to overwrite an existing one. 

| Step | Script | Purpose |
|---|---|---|
| 1 | `audit_server.py`, `audit_api_artifacts.py`, `overlap_details.py` | Input hashes, split sizes, exact overlap, API-failure marker count |
| 2 | `prepare_controlled.py` | Derive train/validation, fit the six tokenizers (explicit required-character inventory), round-trip checks |
| 3 | `build_and_smoke.py` | Fairseq binarization, shared dictionaries, short GPU smoke test |
| 4 | `train_controlled.py` | Ten-epoch training per condition and seed; validation chrF2 checkpoint selection |
| 5 | `evaluate_controlled_test.py`, `eval_reconstruction.py` | Frozen test evaluation of the 18 selected checkpoints |
| 6 | `paired_stats.py`, `gec_metrics.py` | Paired bootstrap intervals, approximate randomization, Holm adjustment, edit-level P/R/F0.5 and GLEU |
| 7 | `plot_val_curves.py`, `plot_training_budget.py` | Figures (validation curves; epoch 10 vs 20) |
| 8 | `extend_controlled.py`, `run_extend_queue.sh` | Continuation to epoch 20 |
| 9 | `overlap_ids.py`, `make_id_subsample.py`, `tokenization_stats.py`, `sample_annotation.py` | Overlap sensitivity, 96,919-pair control, segmentation statistics, error-analysis sample |
| 10 | `tr_pipeline.py`, `run_tr_queue.sh` | GECTurk replication |

Software versions are fixed in [`requirements.txt`](requirements.txt). Each run used a single GPU (an RTX 3090 in the recorded smoke tests). Training for the same number of epochs does not mean the same number of updates or FLOPs; see the paper for this point.

## Contact

Syauqie Muhammad Marier, GitHub [@gitsyauqie](https://github.com/gitsyauqie).
