# Pipeline Documentation

## Pipeline Stages
1. **Download and Clean (`00_download_and_clean.ipynb`)**
- Downloads Gutenberg plain-text books from configured URLs.
- Removes Gutenberg boilerplate.
- Saves cleaned raw text to `data/raw/{raw_filename}`.
- Writes metadata and catalog files.

2. **Chunk and Embed (`01_chunk_and_embed.ipynb`)**
- Splits each book into overlapping word windows.
- Encodes chunks with Sentence-Transformers.
- Saves chunk index + embeddings + run metadata under `data/processed/{processed_dir}/`.

3. **Transform and Cluster (`02_transform_and_cluster.ipynb`)**
- Fits PCA and saves low-dimensional trajectories.
- Persists global PCA fit artifacts (`outputs/pca/global_pca_fit.*`) for downstream reproducible analysis.
- Computes **Twist Signal** (`s_t`) and acceleration (`a_t`) for multiple `k` values.
- Detects top peaks and builds story-level features.
- Runs feature-based clustering and DTW-based similarity clustering.

4. **EDA and Visualization (`03_eda_and_visualization.ipynb`)**
- Loads outputs and metadata.
- Builds statistical + interactive views.
- Produces exploratory and deeper interpretation notes.
- Exports EDA figures/tables and insights.

5. **All-Novel Stacked Panels (`04_novel_stacked_twist_signal.ipynb`)**
- Loads per-book `signals_k{5,7,11}.npz` and `peaks_k{5,7,11}.json`.
- Generates one 3-row stacked figure per novel (`s_t` + `a_t` for each `k`).
- Exports grouped tables and a consolidated per-novel interpretation markdown.

6. **LLM Judge Overlay Prep (Prompt Package)**
- Builds long-context Gemini prompt payloads per novel from full raw text and chunk index lines.
- Produces strict JSON peak labels for overlay comparison (judge labels, not absolute ground truth).
- Validates output schema and spacing/range constraints before downstream plotting.

7. **LLM Judge Signal Analysis (`05_llm_judge_signal_analysis.ipynb`)**
- Focuses on `k=7` signal interpretation with smoothing + robust normalization + composite event score.
- Compares LLM peaks against existing pipeline peaks and processed event peaks.
- Exports analysis figures/tables and run-specific insight markdown under `outputs/llm_judge/analysis/`.

8. **PCA Component Insights (`06_pca_component_insights.ipynb`)**
- Loads persisted global PCA fit artifacts from `outputs/pca/`.
- Produces corpus-level PCA diagnostics and per-book PCA trajectory metrics.
- Links PCA dynamics to Twist Signal behavior for `k=5,7,11`.
- Runs permutation/bootstrapped robustness checks and exports integrity tables.
- Writes figures/tables/insight markdown under `outputs/pca_analysis/`.

9. **Excitement Linear Projection (`07_excitement_linear_projection.ipynb`)**
- Loads per-book embeddings (`embeddings.npy`), LLM excitement labels (`label.npy`), and metadata.
- Uses deterministic novel-level split with seed `42` (`16` train novels, `4` test novels).
- Trains a 1-layer linear perceptron (`y_hat = X @ W + b`) with MSE optimization.
- Exports diagnostics, raw-vs-smoothed overlay figures, metrics tables, and learned weights.
- Writes outputs under `outputs/excitement_linear/`.

10. **Excitement Label Variant Analysis (`08_excitement_label_variant_analysis.ipynb`)**
- Compares three label variants: `label.npy`, `label_winsize_5.npy`, and `label_indep_winsize_5.npy`.
- Reuses split manifest from `outputs/excitement_linear/tables/split_manifest.csv` for direct comparability.
- Trains one linear model per variant with matched optimization settings.
- Exports cross-variant agreement/distribution diagnostics plus an `indep_winsize_5` deep dive.
- Writes figures/tables/model artifacts under `outputs/excitement_variant_analysis/`.

11. **Indep Excitement Clustering (`09_indep_excitement_clustering.ipynb`)**
- Focuses on `label_indep_winsize_5.npy` for all books (unsupervised, no train/test split).
- Extracts per-book interpretable trajectory features (distribution, volatility, transition, temporal-shape, and MA-derived stats).
- Runs feature-branch clustering (`KMeans`, `Agglomerative Ward`) with `k=2..6` model sweep and stability checks.
- Runs DTW-branch clustering on resampled trajectories (`L=200`) for trajectory-shape validation.
- Computes cross-method agreement (ARI/NMI + contingency table) and exports representatives/profile summaries.
- Adds advanced diagnostics: elbow (`k=1..10`), feature/DTW k-sweep quality plots, genre-by-cluster summaries, feature-signature and contingency heatmaps.
- Adds legend integrity checks for feature-cluster visualizations.
- Writes outputs under `outputs/excitement_indep_clustering/`, including `insights.md` and `cluster_report.md`.

12. **Final Teacher-Guided Semantic Basis Report Packaging (`10_final_teacher_guided_semantic_basis_report.ipynb`)**
- Reuses stage-08 variant metrics and stage-09 clustering outputs as source-of-truth evidence.
- Builds final claim-safe support tables under `outputs/final_report/tables/`, including dataset profile, variant-rank diagnostics, CIW-5 per-book deep-dive metrics, and claim-evidence checklist.
- Generates curated storytelling figures under `outputs/final_report/figures/`, including variant-rank sensitivity, per-test-book CIW-5 breakdown, and contribution/use-case framing diagrams.
- Writes final narrative documents:
  - `docs/FINAL_REPORT.md` (primary narrative)
  - `docs/OTHER_EXPERIMENTS.md` (Twist/PCA appendix, explicitly secondary)
- Runs packaging integrity checks (source existence, table/figure completeness, image-link validity, claim-checklist completeness, selected-variant consistency, split consistency, and no em-dash policy in generated docs).

## Twist Signal Definition
Given chunk embeddings `e_t` and context window size `k`:

- Context mean: `context_mean[t] = mean(e_{t-k}, ..., e_{t-1})` using available prefix when `t < k`.
- Twist Signal: `s_t = 1 - cosine(e_t, context_mean[t])`.
- Acceleration: `a_t = |s_t - s_{t-1}|` with `a_0 = 0`.

Note: this method was formerly referenced as “Option B”; project docs now use **Twist Signal**.

## Parameters and Defaults
Current defaults in pipeline notebooks:
- Chunking:
  - `window_words=300`
  - `stride_words=100`
- Embedding:
  - `batch_size=64`
  - current run model observed in artifact indexes: `sentence-transformers/all-mpnet-base-v2`
- Twist Signal:
  - `k_values=[5, 7, 11]`
  - primary reporting at `k=7`
- PCA:
  - dimensions `2` and `5`
- Peaks:
  - top peaks `top_K=3`
  - minimum separation `3` chunks
- Clustering:
  - default clusters `n_clusters=4`
- DTW:
  - signal resample length `L=200`
- Excitement linear projection:
  - split: novel-level `16/4` with `SEED=42`
  - optimizer defaults: `EPOCHS=200`, `BATCH_SIZE=4096`, `LR=1e-2`, `WEIGHT_DECAY=1e-4`
  - presentation smoothing: runtime-configured `MA_WINDOW` (current run: `9`)
- Excitement variant analysis:
  - same split policy as `07` (manifest reuse)
  - trains one linear model per label variant
  - presentation smoothing: runtime-configured `MA_WINDOW` (current run: `5`)
- Indep excitement clustering:
  - label source: `label_indep_winsize_5.npy`
  - smoothing-derived features: runtime `MA_WINDOW` (current clustering run: `5`)
  - model sweep: `k=2..6`
  - DTW resample length: `L=200`
- Final report packaging:
  - method naming:
    - `NC-1` = No-Context Chunk Teacher Labels
    - `SW-5` = Shared-Window Labels
    - `CIW-5` = Context-Window Independent Labels
  - variant ranking rule: trend-fidelity first on test split (`mae_ma5`, then `mae`, then `rmse`)
  - selected variant for current run: `CIW-5`
  - report smoothing policy: `MA_WINDOW=5`

## Artifact Flow
File-level flow:
1. `data/raw/{raw_filename}.txt`
2. `data/processed/{processed_dir}/chunks.jsonl`
3. `data/processed/{processed_dir}/embeddings.npy`
4. `data/processed/{processed_dir}/label.npy`
5. `data/processed/{processed_dir}/label_winsize_5.npy`
6. `data/processed/{processed_dir}/label_indep_winsize_5.npy`
7. `data/processed/{processed_dir}/index.json`
8. `data/processed/{processed_dir}/pca_d2.npy`, `pca_d5.npy`
9. `outputs/pca/global_pca_fit.npz`
10. `outputs/pca/global_pca_fit_meta.json`
11. `outputs/pca/global_pca_variance_summary.csv`
12. `data/processed/{processed_dir}/signals_k{K}.npz`
13. `data/processed/{processed_dir}/peaks_k{K}.json`
14. `outputs/features.csv`
15. `outputs/clusters_kmeans.csv`, `outputs/clusters_hier.csv`
16. `outputs/dtw_distance_k7.npy`
17. `outputs/eda/*` from EDA notebook
18. `outputs/eda/novel_stacks/figures/*.png`
19. `outputs/eda/novel_stacks/tables/*.csv`
20. `docs/NOVEL_STACKED_OUTPUT_INTERPRETATION.md`
21. `outputs/llm_judge/prompts/*.json` (generated by helper script)
22. `outputs/llm_judge/analysis/figures/*.png`
23. `outputs/llm_judge/analysis/tables/*.csv`
24. `outputs/llm_judge/analysis/insights_k7.md`
25. `outputs/pca_analysis/figures/*.png`
26. `outputs/pca_analysis/tables/*.csv`
27. `outputs/pca_analysis/insights.md`
28. `outputs/excitement_linear/figures/*.png`
29. `outputs/excitement_linear/tables/*.csv`
30. `outputs/excitement_linear/model/linear_weights.npz`
31. `outputs/excitement_linear/interpretation.md`
32. `outputs/excitement_variant_analysis/figures/*.png`
33. `outputs/excitement_variant_analysis/tables/*.csv`
34. `outputs/excitement_variant_analysis/model/linear_weights_*.npz`
35. `outputs/excitement_variant_analysis/insights.md`
36. `outputs/excitement_indep_clustering/tables/*.csv`
37. `outputs/excitement_indep_clustering/figures/*.png`
38. `outputs/excitement_indep_clustering/insights.md`
39. `outputs/excitement_indep_clustering/cluster_report.md`
40. `outputs/final_report/figures/fig01_pipeline_overview.png`
41. `outputs/final_report/figures/fig02_variant_comparison_test_metrics.png`
42. `outputs/final_report/figures/fig03_ciw5_model_behavior.png`
43. `outputs/final_report/figures/fig04_ciw5_test_overlays_reference.png`
44. `outputs/final_report/figures/fig05_feature_cluster_map.png`
45. `outputs/final_report/figures/fig06_cluster_genre_composition.png`
46. `outputs/final_report/figures/fig07_cluster_signatures_and_agreement.png`
47. `outputs/final_report/figures/fig08_variant_rank_sensitivity.png`
48. `outputs/final_report/figures/fig09_ciw5_per_book_test_breakdown.png`
49. `outputs/final_report/figures/fig10_contribution_and_use_cases_map.png`
50. `outputs/final_report/figures/fig11_feature_cluster_member_trajectories_ma5.png`
51. `outputs/final_report/tables/dataset_profile_for_report.csv`
52. `outputs/final_report/tables/variant_selection_summary.csv`
53. `outputs/final_report/tables/variant_selection_diagnostics.csv`
54. `outputs/final_report/tables/ciw5_per_book_deepdive.csv`
55. `outputs/final_report/tables/key_results_registry.csv`
56. `outputs/final_report/tables/method_claims_checklist.csv`
57. `outputs/final_report/tables/cluster_summary_for_report.csv`
58. `outputs/final_report/tables/report_integrity_checks.csv`
59. `docs/FINAL_REPORT.md`
60. `docs/OTHER_EXPERIMENTS.md`

Directory keying:
- `processed_dir` is the canonical per-book key and is based on abbreviated title slug.

## Reproducibility and Caching
- Seeds are fixed in notebooks (`SEED=42`) for sampling/clustering consistency.
- Embedding stage supports cache reuse if existing artifacts match expected parameters.
- PCA fit metadata is persisted to `outputs/pca/global_pca_fit_meta.json` for downstream reproducibility checks.
- Metadata file links each `book_id` to `raw_filename` and `processed_dir`.
- If legacy numeric processed folders exist, migration/fallback logic can still resolve them.

## Failure Modes and Recovery
Common issues and recovery steps:
- **Missing raw file**:
  - Re-run `00_download_and_clean.ipynb`.
  - Verify `raw_filename` and `raw_path` in `data/metadata.csv`.
- **Missing or stale embedding cache**:
  - Re-run `01_chunk_and_embed.ipynb`.
  - Set recompute flag if parameters changed.
- **Mismatch between metadata and processed folders**:
  - Confirm `processed_dir` exists under `data/processed/`.
- **DTW shape/symmetry problems**:
  - Re-run `02_transform_and_cluster.ipynb` and verify generated matrix diagnostics.
- **Missing global PCA fit artifacts (`outputs/pca/global_pca_fit.*`)**:
  - Re-run `02_transform_and_cluster.ipynb`.
  - Confirm `outputs/pca/global_pca_variance_summary.csv` exists before running `06_pca_component_insights.ipynb`.
- **Missing or malformed `label.npy` for excitement projection**:
  - Confirm `data/processed/{processed_dir}/label.npy` exists for every book.
  - Ensure shape is one of `(T,)`, `(1,T)`, `(T,1)` and values are in `[0,4]`.
- **Embedding/label length mismatch for excitement projection**:
  - Verify `len(label) == embeddings.shape[0]` for each book before running `07_excitement_linear_projection.ipynb`.
- **Missing `presentation_mae.csv` when interpretation is generated**:
  - Re-run `07_excitement_linear_projection.ipynb` and confirm outputs under `outputs/excitement_linear/tables/`.
- **Missing variant label files for stage 08**:
  - Confirm `label.npy`, `label_winsize_5.npy`, and `label_indep_winsize_5.npy` exist for every `processed_dir`.
- **Variant label shape/range errors**:
  - Ensure each variant label file has shape `(T,)`, `(1,T)`, or `(T,1)` and values within `[0,4]`.
- **Variant split mismatch**:
  - Re-check `outputs/excitement_linear/tables/split_manifest.csv` integrity (`16` train, `4` test, no overlap).
- **Missing stage 08 outputs**:
  - Re-run `08_excitement_label_variant_analysis.ipynb` and verify all artifacts under `outputs/excitement_variant_analysis/`.
- **Missing `label_indep_winsize_5.npy` for stage 09**:
  - Ensure each `data/processed/{processed_dir}/` has `label_indep_winsize_5.npy`.
  - Check shape compatibility `(T,)`, `(1,T)`, `(T,1)` and integer-like values in `[0,4]`.
- **Stage 09 alignment mismatch (`len(label) != embeddings.shape[0]`)**:
  - Rebuild or correct the problematic label file for the affected `processed_dir`.
  - Re-run `09_indep_excitement_clustering.ipynb`.
- **Stage 09 output incompleteness**:
  - Re-run `09_indep_excitement_clustering.ipynb` and inspect `outputs/excitement_indep_clustering/tables/integrity_checks.csv`.
- **Stage 09 legend mismatch (feature scatter legend not matching cluster count)**:
  - Inspect `outputs/excitement_indep_clustering/tables/figure_legend_checks.csv`.
  - Re-run `09_indep_excitement_clustering.ipynb` and verify `feature_pca_scatter_feature_clusters.png` legend entries.
- **Stage 09 report image-link mismatch**:
  - Verify all files under `outputs/excitement_indep_clustering/figures/` exist.
  - Re-run `09_indep_excitement_clustering.ipynb` and confirm `cluster_report_embedded_figures_exist` passes in integrity checks.
- **Missing source artifacts for stage 10 packaging**:
  - Ensure stage-08 and stage-09 tables exist before running `10_final_teacher_guided_semantic_basis_report.ipynb`.
  - Required source roots:
    - `outputs/excitement_variant_analysis/tables/`
    - `outputs/excitement_indep_clustering/tables/`
- **Stage 10 selected variant mismatch**:
  - Inspect `outputs/final_report/tables/variant_selection_summary.csv`.
  - Confirm ranking is computed from test split with trend-fidelity priority (`mae_ma5`, then `mae`, then `rmse`).
  - Re-run `10_final_teacher_guided_semantic_basis_report.ipynb` if mismatch persists.
- **Stage 10 report integrity check failure**:
  - Inspect `outputs/final_report/tables/report_integrity_checks.csv`.
  - Verify missing figures/docs paths and rerun stage 10 after repairing source artifacts.
- **Stage 10 claim-evidence mapping failure**:
  - Inspect `outputs/final_report/tables/method_claims_checklist.csv`.
  - Resolve rows with `status != mapped` by fixing metric-key references or source file paths in the stage-10 notebook generator.
- **Stage 10 image-link resolution failure**:
  - Inspect `docs/FINAL_REPORT.md` and verify every embedded `../outputs/final_report/figures/*.png` path exists.
  - Re-run stage 10 and confirm `embedded_image_links_exist` passes in `outputs/final_report/tables/report_integrity_checks.csv`.

## Extending the Pipeline
Recommended extension points:
- Add new signal variants while preserving `signals_k{K}.npz` compatibility.
- Add cluster methods and write separate output files instead of overwriting existing schemas.
- Add model-comparison runs by tagging outputs with model metadata.
- Add report-generation notebook/scripts that consume `outputs/` and `outputs/eda/`.
- Add LLM-judge overlays using `prompts/llm_judge/` and `tools/llm_judge/` contracts.
