# Story Trajectory Analysis

## Project Overview
This project builds story trajectories from public-domain books and analyzes narrative change patterns over time.

Pipeline goals:
- Download and clean Gutenberg texts.
- Convert each story into chunk-level embedding time series.
- Compute a **Twist Signal** and derived acceleration signal.
- Build story-level features and cluster books by trajectory behavior.
- Support EDA, visualization, and insight generation on top of saved artifacts.

## What Is the Twist Signal?
For each chunk embedding `e_t`, the pipeline computes a local context embedding from previous chunks, then scores novelty relative to that context.

Definitions:
- `context_mean[t]`: mean embedding over recent previous chunks (window size `k`).
- `s_t = 1 - cosine(e_t, context_mean[t])`.
- `a_t = |s_t - s_{t-1}|`.

Interpretation:
- `s_t` (Twist Signal): how different the current chunk is from recent context.
- `a_t`: how sharply novelty changes from one step to the next.

## Current Dataset Snapshot
Current run status (from local artifacts):
- Corpus size: **20 books**.
- Feature rows: **60** (`20 books * 3 k-values`).
- `k` values: `[5, 7, 11]`.
- Current embedding model (from `data/processed/*/index.json`): `sentence-transformers/all-mpnet-base-v2`.
- DTW matrix: `outputs/dtw_distance_k7.npy` shape `(20, 20)`.

Primary metadata source:
- `data/metadata.csv`
- `data/book_catalog.json`

## Repository Structure
- `00_download_and_clean.ipynb`: Gutenberg download + cleaning + metadata write.
- `01_chunk_and_embed.ipynb`: chunking + embedding + per-book processed artifacts.
- `02_transform_and_cluster.ipynb`: Twist Signal, PCA, clustering, DTW.
- `03_eda_and_visualization.ipynb`: EDA, visualization, and insight extraction.
- `04_novel_stacked_twist_signal.ipynb`: all-novel stacked Twist Signal panels (`k=5,7,11`) + consolidated per-novel interpretation export.
- `05_llm_judge_signal_analysis.ipynb`: `k=7` LLM-judge alignment analysis with processed event score, overlays, and insight exports.
- `06_pca_component_insights.ipynb`: corpus/book-level PCA component interpretation, robustness checks, and PCA-signal linkage outputs.
- `07_excitement_linear_projection.ipynb`: LLM excitement label visualization and linear embedding-to-excitement projection diagnostics.
- `08_excitement_label_variant_analysis.ipynb`: compares 3 excitement label variants (`base`, `winsize_5`, `indep_winsize_5`) and deep-dives on `indep_winsize_5`.
- `09_indep_excitement_clustering.ipynb`: unsupervised clustering on `label_indep_winsize_5.npy` using interpretable features plus DTW trajectory-shape validation.
- `prompts/llm_judge/`: Gemini LLM-judge prompt templates + output schema.
- `tools/llm_judge/`: helper scripts to build per-book prompt payloads and validate JSON outputs.
- `data/raw/`: cleaned book text files (abbreviated title filenames).
- `data/processed/{processed_dir}/`: per-book chunk, embedding, label, signal, peak, PCA artifacts.
- `outputs/`: global outputs (`features.csv`, cluster CSVs, DTW matrix, summary).
- `outputs/eda/`: EDA figures, tables, and insight narrative.
- `outputs/eda/novel_stacks/`: grouped 20-book stacked figures, supporting tables, and validation outputs.
- `outputs/excitement_linear/`: figures, metrics tables, model weights, and interpretation for the linear excitement projection workflow.
- `outputs/excitement_variant_analysis/`: variant comparison tables/figures, per-variant linear weights, and indep-focused insights.
- `outputs/excitement_indep_clustering/`: indep-focused clustering tables/figures, compact insights, and extended report with embedded figures.
- `docs/`: pipeline, schema dictionary, EDA planning, output interpretation, and Gemini judge prompt docs.

## Pipeline Run Order
Run notebooks in this order:
1. `00_download_and_clean.ipynb`
2. `01_chunk_and_embed.ipynb`
3. `02_transform_and_cluster.ipynb`
4. `03_eda_and_visualization.ipynb`
5. `04_novel_stacked_twist_signal.ipynb`
6. `05_llm_judge_signal_analysis.ipynb`
7. `06_pca_component_insights.ipynb` (requires `02` PCA artifacts)
8. `07_excitement_linear_projection.ipynb` (requires per-book `embeddings.npy` and `label.npy`)
9. `08_excitement_label_variant_analysis.ipynb` (reuses split from `outputs/excitement_linear/tables/split_manifest.csv`)
10. `09_indep_excitement_clustering.ipynb` (requires `label_indep_winsize_5.npy` for all books; unsupervised on all 20 novels; `MA_WINDOW=5` for smoothing-derived features)

## Key Outputs for EDA/Insight Work
Core files:
- `outputs/features.csv`: one row per `(book_id, k)` with Twist Signal-derived metrics + metadata.
- `outputs/clusters_kmeans.csv`: feature-based KMeans labels.
- `outputs/clusters_hier.csv`: hierarchical labels (`feature_ward` and `dtw_average`).
- `outputs/dtw_distance_k7.npy`: pairwise DTW distances on resampled `s_t` for `k=7`.
- `outputs/pca/global_pca_fit.npz`: persisted fitted PCA arrays (`components`, `mean`, EVR arrays).
- `outputs/pca/global_pca_fit_meta.json`: PCA fit metadata (`seed`, rows used, model name, timestamps).
- `outputs/pca/global_pca_variance_summary.csv`: EVR + cumulative EVR table (PC1..PC5).

Per-book files:
- `data/processed/{processed_dir}/label.npy`
- `data/processed/{processed_dir}/label_winsize_5.npy`
- `data/processed/{processed_dir}/label_indep_winsize_5.npy`
- `data/processed/{processed_dir}/signals_k{K}.npz`
- `data/processed/{processed_dir}/peaks_k{K}.json`
- `data/processed/{processed_dir}/pca_d2.npy`
- `data/processed/{processed_dir}/pca_d5.npy`

Advanced per-novel stacked outputs:
- `outputs/eda/novel_stacks/figures/novel_{book_id}_{processed_dir}_stacked_k5_k7_k11.png`
- `outputs/eda/novel_stacks/tables/novel_stacked_stats.csv`
- `outputs/eda/novel_stacks/tables/novel_stacked_manifest.csv`
- `outputs/eda/novel_stacks/tables/novel_stacked_highlights.csv`
- `docs/NOVEL_STACKED_OUTPUT_INTERPRETATION.md`
- `docs/GEMINI_LLM_JUDGE_PROMPT_PACKAGE.md`
- `docs/LLM_JUDGE_SIGNAL_ANALYSIS.md`
- `outputs/llm_judge/analysis/insights_k7.md`

PCA component insight outputs:
- `outputs/pca_analysis/tables/book_component_stats.csv`
- `outputs/pca_analysis/tables/book_component_signal_assoc.csv`
- `outputs/pca_analysis/tables/component_exemplar_chunks.csv`
- `outputs/pca_analysis/tables/component_genre_association.csv`
- `outputs/pca_analysis/tables/temporal_trend_stats.csv`
- `outputs/pca_analysis/tables/corpus_assoc_bootstrap.csv`
- `outputs/pca_analysis/tables/projection_consistency_checks.csv`
- `outputs/pca_analysis/tables/pca_integrity_checks.csv`
- `outputs/pca_analysis/figures/*.png`
- `outputs/pca_analysis/insights.md`

Excitement linear projection outputs:
- `outputs/excitement_linear/figures/*.png`
- `outputs/excitement_linear/tables/split_manifest.csv`
- `outputs/excitement_linear/tables/global_metrics.csv`
- `outputs/excitement_linear/tables/per_novel_metrics.csv`
- `outputs/excitement_linear/tables/presentation_mae.csv`
- `outputs/excitement_linear/tables/integrity_checks.csv`
- `outputs/excitement_linear/tables/figure_support_stats.csv`
- `outputs/excitement_linear/model/linear_weights.npz`
- `outputs/excitement_linear/interpretation.md`

Excitement variant analysis outputs:
- `outputs/excitement_variant_analysis/figures/*.png`
- `outputs/excitement_variant_analysis/tables/integrity_checks.csv`
- `outputs/excitement_variant_analysis/tables/split_manifest_used.csv`
- `outputs/excitement_variant_analysis/tables/label_distribution_by_variant.csv`
- `outputs/excitement_variant_analysis/tables/variant_pairwise_agreement_global.csv`
- `outputs/excitement_variant_analysis/tables/variant_pairwise_agreement_per_book.csv`
- `outputs/excitement_variant_analysis/tables/model_global_metrics_by_variant.csv`
- `outputs/excitement_variant_analysis/tables/model_per_novel_metrics_by_variant.csv`
- `outputs/excitement_variant_analysis/tables/indep_winsize_5_support_stats.csv`
- `outputs/excitement_variant_analysis/model/linear_weights_base.npz`
- `outputs/excitement_variant_analysis/model/linear_weights_winsize_5.npz`
- `outputs/excitement_variant_analysis/model/linear_weights_indep_winsize_5.npz`
- `outputs/excitement_variant_analysis/insights.md`

Indep excitement clustering outputs:
- `outputs/excitement_indep_clustering/tables/indep_book_features.csv`
- `outputs/excitement_indep_clustering/tables/indep_book_features_zscore.csv`
- `outputs/excitement_indep_clustering/tables/cluster_quality_by_method.csv`
- `outputs/excitement_indep_clustering/tables/cluster_assignments_feature.csv`
- `outputs/excitement_indep_clustering/tables/cluster_assignments_dtw.csv`
- `outputs/excitement_indep_clustering/tables/cluster_profile_summary.csv`
- `outputs/excitement_indep_clustering/tables/cluster_representatives.csv`
- `outputs/excitement_indep_clustering/tables/cluster_method_agreement.csv`
- `outputs/excitement_indep_clustering/tables/kmeans_elbow_curve.csv`
- `outputs/excitement_indep_clustering/tables/genre_by_feature_cluster_counts.csv`
- `outputs/excitement_indep_clustering/tables/genre_by_feature_cluster_proportions.csv`
- `outputs/excitement_indep_clustering/tables/feature_cluster_signature_top_features.csv`
- `outputs/excitement_indep_clustering/tables/figure_legend_checks.csv`
- `outputs/excitement_indep_clustering/tables/integrity_checks.csv`
- `outputs/excitement_indep_clustering/figures/*.png` (including elbow, k-sweep, genre, contingency, and cluster-member panels)
- `outputs/excitement_indep_clustering/insights.md`
- `outputs/excitement_indep_clustering/cluster_report.md`

## Known Limitations
- Clustering settings are baseline defaults (`n_clusters=4`) and not heavily tuned.
- DTW hierarchical clustering can produce imbalanced clusters.
- Rank/genre metadata in catalog are useful labels but should not be treated as objective ground truth.
- Insight claims should be validated across parameter sensitivity and method variants.

## Next-Step Roadmap
1. Expand interactive trajectory views (book-level + cluster-level dashboards).
2. Add cluster stability checks across seeds, `k` values, and feature subsets.
3. Build archetype-level summaries with confidence scoring.
4. Add reproducible report export (tables + figures + narrative markdown).
