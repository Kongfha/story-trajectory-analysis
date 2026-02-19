# Data Dictionary

## Core Keys and Joins
Primary keys used across outputs:
- `id` / `pg_id` in `data/metadata.csv`: Gutenberg book identifier.
- `book_id` in output tables: same numeric identifier as `id`.
- `processed_dir`: canonical per-book folder key under `data/processed/`.

Join rules:
- `outputs/features.csv.book_id` joins to `data/metadata.csv.id`.
- `outputs/clusters_*.csv.book_id` joins to `data/metadata.csv.id`.

## `data/metadata.csv`
Purpose: master catalog + run metadata per book.

Current columns:
- `id` (int): canonical book id used by pipeline.
- `pg_id` (int): Gutenberg id (same as `id` in current run).
- `title` (str)
- `author` (str)
- `first_publication_year` (int)
- `origin_country` (str)
- `original_language` (str)
- `format` (str)
- `genre_primary` (str)
- `genre_secondary` (JSON-string list)
- `short_tags` (JSON-string list)
- `recognizability_rank` (int)
- `genre_clarity_rank` (int)
- `twist_peak_rank` (int)
- `twist_peak_reason` (str)
- `notes` (str)
- `ebook_page_url` (str)
- `plain_text_utf8_url` (str)
- `raw_filename` (str)
- `raw_path` (str)
- `processed_dir` (str)
- `processed_path` (str)
- `length` (int): word count after cleaning
- `char_length` (int)
- `source_url` (str)
- `status` (str)
- `citations` (JSON-string list)

## Per-Book Processed Artifacts
Location pattern:
- `data/processed/{processed_dir}/...`

### `chunks.jsonl`
One JSON object per chunk:
- `chunk_index` (int)
- `start_word` (int)
- `end_word` (int)
- `text_preview` (str)

### `embeddings.npy`
- Shape: `(T, D)`
- Dtype: `float32`
- `T`: chunk count, `D`: embedding dimension

### `label.npy`
Purpose: LLM excitement label per chunk used by `07_excitement_linear_projection.ipynb`.

Contract:
- Accepted input shapes: `(T,)`, `(1, T)`, `(T, 1)`; normalized to `(T,)` in notebook loaders.
- Dtype: numeric (`int` or float-castable).
- Expected value range: integer labels in `[0, 4]`.
- Alignment rule: `len(label) == embeddings.shape[0]` for each book.

### `label_winsize_5.npy`
Purpose: LLM excitement labels produced from 5-chunk grouped prompts where each 5-chunk block is assigned one shared score.

Contract:
- Accepted input shapes: `(T,)`, `(1, T)`, `(T, 1)`; normalized to `(T,)` in notebook loaders.
- Dtype: numeric (`int` or float-castable).
- Expected value range: integer labels in `[0, 4]`.
- Alignment rule: `len(label_winsize_5) == embeddings.shape[0]`.
- Block behavior expectation: labels are constant inside each contiguous 5-chunk block.

### `label_indep_winsize_5.npy`
Purpose: LLM excitement labels produced from 5-chunk grouped prompts with independent per-chunk scoring within each group.

Contract:
- Accepted input shapes: `(T,)`, `(1, T)`, `(T, 1)`; normalized to `(T,)` in notebook loaders.
- Dtype: numeric (`int` or float-castable).
- Expected value range: integer labels in `[0, 4]`.
- Alignment rule: `len(label_indep_winsize_5) == embeddings.shape[0]`.

### `index.json`
Typical fields:
- `book_id` (int)
- `processed_dir` (str)
- `T` (int)
- `D` (int)
- `window_words` (int)
- `stride_words` (int)
- `model_name` (str)
- `batch_size` (int)
- `dtype` (str)
- `created_at` (str ISO timestamp)

### `signals_k{K}.npz`
NPZ keys:
- `s`: Twist Signal array, shape `(T,)`, dtype `float32`
- `a`: acceleration array, shape `(T,)`, dtype `float32`

### `peaks_k{K}.json`
Fields:
- `book_id` (int)
- `k` (int)
- `top_K` (int)
- `separation` (int)
- `peak_indices` (list[int])
- `peak_positions_norm` (list[float])
- `signal` (str, currently `a_t`)

### PCA Files
- `pca_d2.npy`: shape `(T, 2)`
- `pca_d5.npy`: shape `(T, 5)`

## Global PCA Artifacts (`outputs/pca/`)

### `global_pca_fit.npz`
Purpose: persisted fitted PCA model arrays used to reproduce per-book projection checks and downstream PCA analysis.

NPZ keys and shapes:
- `components`: shape `(5, D)`, dtype `float32`
- `explained_variance`: shape `(5,)`, dtype `float32`
- `explained_variance_ratio`: shape `(5,)`, dtype `float32`
- `singular_values`: shape `(5,)`, dtype `float32`
- `mean`: shape `(D,)`, dtype `float32`

### `global_pca_fit_meta.json`
Purpose: reproducibility metadata for the global PCA fit.

Fields:
- `seed` (int)
- `n_components` (int)
- `svd_solver` (str)
- `fit_rows_used` (int)
- `fit_rows_total` (int)
- `embedding_dim` (int)
- `model_name` (str or null)
- `created_at` (str ISO timestamp)

### `global_pca_variance_summary.csv`
Columns:
- `pc` (str: `PC1`..`PC5`)
- `explained_variance_ratio` (float)
- `cumulative_explained_variance_ratio` (float; monotonic non-decreasing)

## `outputs/features.csv`
Purpose: story-level feature matrix per `(book_id, k)` enriched with metadata.

Core feature columns:
- `book_id`, `k`, `T`
- `mean_s`, `std_s`, `max_s`
- `mean_a`, `std_a`, `max_a`
- `num_peaks`
- `peak_pos_1`, `peak_pos_2`, `peak_pos_3`
- `auc_proxy_mean_s`

Also includes metadata columns such as:
- `title`, `author`, `genre_primary`, `format`, `origin_country`, rank fields, tags, citations, `processed_dir`, etc.

Expected cardinality:
- Rows = `num_books * len(k_values)`
- Current run: `20 * 3 = 60`

## `outputs/clusters_kmeans.csv`
Purpose: feature-based KMeans labels.

Columns:
- `book_id`
- `k`
- `n_clusters`
- `cluster`
- metadata context fields (`title`, `author`, `genre_primary`, `format`, `processed_dir`, etc.)

Expected cardinality:
- One row per `(book_id, k)`
- Current run: `60` rows

## `outputs/clusters_hier.csv`
Purpose: hierarchical cluster labels from two modes.

Columns:
- `book_id`
- `k`
- `mode` (`feature_ward` or `dtw_average`)
- `n_clusters`
- `cluster`
- metadata context fields (`title`, `author`, `genre_primary`, `format`, `processed_dir`, etc.)

Expected cardinality:
- `feature_ward`: one row per `(book_id, k)`
- `dtw_average`: one row per book for primary `k`
- Current run: `60 + 20 = 80` rows

## `outputs/dtw_distance_k7.npy`
Purpose: pairwise DTW distance matrix on resampled Twist Signal (`k=7`).

Contract:
- Shape `(N, N)` where `N = number of books`
- Symmetric
- Diagonal approximately zero
- Current run shape: `(20, 20)`

## Excitement Linear Projection Outputs (`outputs/excitement_linear/`)

### `tables/split_manifest.csv`
Purpose: deterministic novel-level split assignment used for training/evaluation.

Columns:
- `book_id` (int)
- `title` (str)
- `processed_dir` (str)
- `T` (int)
- `split` (`train` or `test`)

Contract:
- Expected split cardinality for current setup: `16` train novels and `4` test novels.
- No overlap between train/test book ids.

### `tables/global_metrics.csv`
Purpose: global regression metrics aggregated by split.

Columns:
- `split` (`train` or `test`)
- `n_samples` (int)
- `n_novels` (int)
- `mse` (float)
- `rmse` (float)
- `mae` (float)
- `r2` (float)

### `tables/per_novel_metrics.csv`
Purpose: per-novel regression metrics from the learned linear projection.

Columns:
- `book_id` (int)
- `title` (str)
- `processed_dir` (str)
- `split` (`train` or `test`)
- `T` (int)
- `mse` (float)
- `rmse` (float)
- `mae` (float)
- `r2` (float; may be `NaN` for constant-label edge cases)
- `mae_ma` (float): moving-average MAE using current `MA_WINDOW`.

### `tables/presentation_mae.csv`
Purpose: presentation-friendly train/test MAE comparison between raw and smoothed trajectories.

Columns:
- `split` (`train` or `test`)
- `ma_window` (int): smoothing window used in current run (`MA_WINDOW` from notebook).
- `mae_raw` (float)
- `mae_moving_average` (float)
- `n_samples` (int)

### `tables/integrity_checks.csv`
Purpose: run-level and per-book integrity checks for alignment, split integrity, model shapes, and output completeness.

Columns:
- `check` (str)
- `expected` (str or numeric)
- `actual` (str or numeric)
- `pass` (bool)

### `tables/figure_support_stats.csv`
Purpose: per-book supporting statistics used when interpreting overlay/scatter/residual figures.

Columns:
- `book_id` (int)
- `split` (`train` or `test`)
- `T` (int)
- `y_true_mean`, `y_true_std` (float)
- `y_pred_mean`, `y_pred_std` (float)
- `pred_min`, `pred_max` (float)
- `res_mean`, `res_std` (float)
- `res_p05`, `res_p95` (float)
- `corr_true_pred` (float)
- `title` (str)

### `model/linear_weights.npz`
Purpose: persisted learned linear transformation from embedding space to scalar excitement prediction.

NPZ keys:
- `W`: shape `(768, 1)`, dtype `float32`
- `b`: shape `(1,)`, dtype `float32`
- `x_mean`: shape `(768,)`, dtype `float32`
- `x_std`: shape `(768,)`, dtype `float32`
- `seed`: scalar array (`int32`)
- `lr`: scalar array (`float32`)
- `epochs`: scalar array (`int32`)
- `batch_size`: scalar array (`int32`)
- `weight_decay`: scalar array (`float32`)

### `figures/*.png`
Purpose: diagnostics and per-novel overlays for model fit and trend alignment.

Canonical outputs:
- `labels_all_20_novels_grid.png`
- `labels_all_20_novels_overlay_normpos.png`
- `train_loss_curve.png`
- `prediction_scatter_train_test.png`
- `residual_hist_train_test.png`
- `mae_raw_vs_moving_average.png`
- `novel_overlay_test_{book_id}.png` (4 files, test novels)
- `novel_overlay_train_{book_id}.png` (2 files, selected train novels)

### `interpretation.md`
Purpose: narrative interpretation of diagnostics and overlays with explicit verdict on chunk-level vs trend-level usability.

Evidence linkage:
- References figures and tables under the same `outputs/excitement_linear/` namespace.
- Uses `presentation_mae.csv.ma_window` to document current smoothing window (runtime-configurable via `MA_WINDOW`).

## Excitement Variant Analysis Outputs (`outputs/excitement_variant_analysis/`)

### `tables/integrity_checks.csv`
Purpose: consolidated validation for stage-08 inputs and outputs.

Checks include:
- variant label file existence
- shape normalization compatibility
- value range `[0,4]` and integer-like checks
- `len(label_variant) == T` alignment
- split integrity reuse checks
- output completeness and overlay counts
- MA-window contract check (`ma_window == 5` for current run)

Columns:
- `check` (str)
- `expected` (str or numeric)
- `actual` (str or numeric)
- `pass` (bool)

### `tables/split_manifest_used.csv`
Purpose: split manifest copy used by stage 08 (reused from stage 07 output).

Columns:
- `book_id` (int)
- `title` (str)
- `processed_dir` (str)
- `T` (int)
- `split` (`train` or `test`)

### `tables/label_distribution_by_variant.csv`
Purpose: label frequency summaries for `base`, `winsize_5`, and `indep_winsize_5`.

Columns:
- `variant` (`base`, `winsize_5`, `indep_winsize_5`)
- `label` (`0..4`)
- `count` (int)
- `proportion` (float)
- `scope` (`global` or `book`)
- `book_id` (int or null for global rows)
- `processed_dir` (str or null for global rows)
- `title` (str or null for global rows)

### `tables/variant_pairwise_agreement_global.csv`
Purpose: global chunk-level pairwise agreement between label variants.

Columns:
- `variant_a` (str)
- `variant_b` (str)
- `mae` (float)
- `exact_match` (float)
- `corr` (float)
- `n_samples` (int)

### `tables/variant_pairwise_agreement_per_book.csv`
Purpose: per-book pairwise agreement between label variants.

Columns:
- `book_id` (int)
- `processed_dir` (str)
- `variant_a` (str)
- `variant_b` (str)
- `mae` (float)
- `exact_match` (float)
- `corr` (float)
- `T` (int)

### `tables/model_global_metrics_by_variant.csv`
Purpose: split-level regression metrics for each variant-specific linear model.

Columns:
- `variant` (str)
- `split` (`train` or `test`)
- `n_samples` (int)
- `n_novels` (int)
- `mse` (float)
- `rmse` (float)
- `mae` (float)
- `r2` (float)
- `corr` (float)
- `ma_window` (int)
- `mae_ma` (float)

### `tables/model_per_novel_metrics_by_variant.csv`
Purpose: per-book regression metrics for each variant-specific linear model.

Columns:
- `variant` (str)
- `book_id` (int)
- `title` (str)
- `processed_dir` (str)
- `split` (`train` or `test`)
- `T` (int)
- `mse` (float)
- `rmse` (float)
- `mae` (float)
- `r2` (float)
- `corr` (float)
- `mae_ma` (float)

### `tables/indep_winsize_5_support_stats.csv`
Purpose: per-book support stats for `indep_winsize_5` interpretation figures.

Columns:
- `book_id` (int)
- `split` (`train` or `test`)
- `T` (int)
- `y_true_mean`, `y_true_std` (float)
- `y_pred_mean`, `y_pred_std` (float)
- `pred_min`, `pred_max` (float)
- `res_mean`, `res_std` (float)
- `res_p05`, `res_p95` (float)
- `corr_true_pred` (float)
- `title` (str)

### `model/linear_weights_base.npz`
### `model/linear_weights_winsize_5.npz`
### `model/linear_weights_indep_winsize_5.npz`
Purpose: per-variant learned linear projection weights.

NPZ keys:
- `W`: shape `(768, 1)`, dtype `float32`
- `b`: shape `(1,)`, dtype `float32`
- `x_mean`: shape `(768,)`, dtype `float32`
- `x_std`: shape `(768,)`, dtype `float32`
- `seed`: scalar array (`int32`)
- `lr`: scalar array (`float32`)
- `epochs`: scalar array (`int32`)
- `batch_size`: scalar array (`int32`)
- `weight_decay`: scalar array (`float32`)
- `variant`: scalar string array

### `figures/*.png`
Purpose: cross-variant diagnostics and indep-focused deep-dive visuals.

Canonical outputs:
- `labels_grid_base.png`
- `labels_grid_winsize_5.png`
- `labels_grid_indep_winsize_5.png`
- `label_overlay_normpos_by_variant.png`
- `label_distribution_by_variant.png`
- `variant_pairwise_agreement_bar.png`
- `train_loss_curves_by_variant.png`
- `model_metric_comparison_by_variant.png`
- `indep_prediction_scatter_train_test.png`
- `indep_residual_hist_train_test.png`
- `indep_mae_raw_vs_moving_average.png`
- `indep_novel_overlay_test_{book_id}.png` (4 files)
- `indep_novel_overlay_train_{book_id}.png` (2 files)

### `insights.md`
Purpose: narrative summary of variant comparison and explicit `indep_winsize_5` verdict.

Contract notes:
- Uses MA(W) wording with current run `W=5`.
- Must include “use now / avoid now” guidance and next-step acceptance criteria.

## Indep Excitement Clustering Outputs (`outputs/excitement_indep_clustering/`)

### `tables/indep_book_features.csv`
Purpose: one-row-per-book feature matrix extracted from `label_indep_winsize_5.npy`.

Columns:
- `book_id`, `title`, `processed_dir`
- `T`
- `mean_y`, `std_y`, `median_y`, `iqr_y`, `min_y`, `max_y`
- `p10_y`, `p90_y`, `range_y`
- `prop_label_0`, `prop_label_1`, `prop_label_2`, `prop_label_3`, `prop_label_4`
- `entropy_labels`
- `mean_abs_diff`, `std_diff`, `p95_abs_diff`, `jump_ge_2_rate`
- `up_rate`, `down_rate`, `flat_rate`
- `lag1_autocorr`, `sign_change_rate`
- `corr_with_position`, `slope_position`
- `mean_early`, `mean_mid`, `mean_late`
- `mean_ma5`, `std_ma5`, `p95_ma5`

Contract:
- Exactly one row per book (`20` rows in current corpus).
- No NaN/inf in numeric columns.

### `tables/indep_book_features_zscore.csv`
Purpose: z-scored version of clustering features (across books).

Columns:
- Same schema as `indep_book_features.csv` with numeric columns standardized.

### `tables/cluster_quality_by_method.csv`
Purpose: model-selection diagnostics across clustering branches and candidate `k`.

Columns:
- `branch` (`feature` or `dtw`)
- `method` (`kmeans`, `ward`, or `average`)
- `k` (int, tested `2..6`)
- `silhouette` (float)
- `davies_bouldin` (float; `NaN` for DTW branch where not used)
- `calinski_harabasz` (float; `NaN` for DTW branch where not used)
- `kmeans_stability_ari` (float; populated for KMeans rows)

### `tables/cluster_assignments_feature.csv`
Purpose: final cluster assignment per book from selected feature-branch solution.

Columns:
- `book_id`, `title`, `processed_dir`
- `method`
- `k`
- `cluster`

### `tables/cluster_assignments_dtw.csv`
Purpose: final cluster assignment per book from selected DTW-branch solution.

Columns:
- `book_id`, `title`, `processed_dir`
- `method`
- `k`
- `cluster`

### `tables/cluster_profile_summary.csv`
Purpose: cluster-level feature profiling with effect-size style deltas versus corpus.

Columns:
- `branch` (`feature` or `dtw`)
- `cluster` (int)
- `cluster_size` (int)
- `feature` (str)
- `mean_raw` (float)
- `median_raw` (float)
- `mean_z` (float)
- `delta_z_vs_corpus` (float)
- `abs_delta_z` (float)
- `rank_abs_delta` (int)

### `tables/cluster_representatives.csv`
Purpose: representative-book selection per cluster for interpretation.

Columns:
- `branch` (`feature` or `dtw`)
- `cluster` (int)
- `role` (`centroid_medoid`, `cluster_medoid`, `high_volatility`, `low_volatility`)
- `book_id`, `title`, `processed_dir`
- `score_name` (str)
- `score_value` (float)

### `tables/cluster_method_agreement.csv`
Purpose: cross-method agreement metrics plus contingency table export.

Columns:
- `row_type` (`metric` or `contingency`)
- `metric` (`ari`, `nmi`, or null for contingency rows)
- `value` (float; populated for metric rows)
- `feature_cluster` (int or null)
- `dtw_cluster` (int or null)
- `count` (int; populated for contingency rows)

### `tables/kmeans_elbow_curve.csv`
Purpose: KMeans elbow diagnostics computed on feature z-space.

Columns:
- `k` (int, `1..10`)
- `inertia` (float)
- `delta_inertia` (float; previous-k inertia drop)
- `pct_drop_from_prev` (float)

Contract:
- `k` coverage must include all integers from `1` to `10`.
- `inertia` should be monotonic non-increasing across increasing `k`.

### `tables/genre_by_feature_cluster_counts.csv`
Purpose: feature-cluster by genre contingency table (counts).

Schema:
- Index column: `cluster` (int)
- Data columns: one column per `genre_primary` value.
- Cell values: integer counts of books.

### `tables/genre_by_feature_cluster_proportions.csv`
Purpose: row-normalized feature-cluster by genre table.

Schema:
- Index column: `cluster` (int)
- Data columns: one column per `genre_primary` value.
- Cell values: proportions in `[0,1]`; each row sums to `1.0` (within numeric tolerance).

### `tables/feature_cluster_signature_top_features.csv`
Purpose: selected top signature features used for feature-cluster interpretation/heatmap.

Columns:
- `branch` (`feature`)
- `cluster` (int)
- `cluster_size` (int)
- `feature` (str)
- `mean_raw` (float)
- `median_raw` (float)
- `mean_z` (float)
- `delta_z_vs_corpus` (float)
- `abs_delta_z` (float)
- `rank_abs_delta` (int; within-cluster rank)
- `global_feature_rank` (int; rank by max `abs_delta_z` across feature clusters)

### `tables/figure_legend_checks.csv`
Purpose: programmatic verification that figure legends match expected cluster entries.

Columns:
- `figure` (str)
- `expected_entries` (int)
- `actual_entries` (int)
- `pass` (bool)
- `labels` (str; serialized legend labels)

### `tables/integrity_checks.csv`
Purpose: validation summary for stage 09.

Checks include:
- label existence/shape/range/integer-like checks for all books
- label/embedding length alignment
- feature and clustering output integrity
- selected `k` range checks
- elbow monotonicity and k-coverage checks
- feature-scatter legend entry checks
- genre table consistency checks
- cluster-report embedded figure existence checks
- output completeness checks
- MA-window contract check (`MA_WINDOW=5` for current run)

Columns:
- `check` (str)
- `expected` (str or numeric)
- `actual` (str or numeric)
- `pass` (bool)

### `figures/*.png`
Purpose: visual diagnostics for features, cluster structure, and trajectory archetypes.

Canonical outputs:
- `feature_correlation_heatmap.png`
- `feature_pca_scatter_feature_clusters.png`
- `feature_elbow_kmeans_inertia.png`
- `feature_k_sweep_quality_metrics.png`
- `dtw_k_sweep_silhouette.png`
- `genre_by_feature_cluster_counts.png`
- `genre_by_feature_cluster_proportions.png`
- `cluster_feature_signature_heatmap_top12.png`
- `cluster_method_contingency_heatmap.png`
- `feature_cluster_member_trajectories_ma5.png`
- `cluster_centroid_trajectories_raw.png`
- `cluster_centroid_trajectories_ma5.png`
- `dtw_distance_heatmap.png`
- `dtw_dendrogram.png`
- `cluster_size_comparison.png`

### `insights.md`
Purpose: indep-focused clustering narrative with selected feature/DTW solutions, agreement reading, archetype summaries, and next-step guidance.

Contract notes:
- Uses MA(W) wording with current run `W=5`.
- Must include cluster-selection rationale and representative-book interpretation.

### `cluster_report.md`
Purpose: extended clustering interpretation report with embedded figure gallery and evidence-linked conclusions.

Contract notes:
- Uses relative image links to `figures/*.png`.
- Must include sections for verdict, diagnostics, feature-cluster interpretation, genre composition, feature-vs-DTW agreement, and practical guidance.

## PCA Analysis Outputs (`outputs/pca_analysis/`)

### `tables/book_component_stats.csv`
Purpose: per-book PCA trajectory summary statistics.

Core columns:
- `book_id`, `processed_dir`, `title`, `genre_primary`, `T`
- `mean_pc1..mean_pc5`
- `std_pc1..std_pc5`
- `corr_pc1_position..corr_pc5_position`
- `sign_change_rate_pc1..sign_change_rate_pc5`
- `sign_change_rate_mean`
- `mean_speed`, `p95_speed`, `speed_std`

### `tables/book_component_signal_assoc.csv`
Purpose: per-book association metrics between PCA trajectory speed and Twist Signal for each `k`.

Columns:
- `book_id`, `processed_dir`, `title`, `genre_primary`
- `k`
- `T`
- `corr_speed_s`
- `corr_speed_a`
- `mean_speed`
- `p95_speed`

Expected cardinality:
- One row per `(book_id, k)` for books with valid `signals_k{K}.npz`
- With complete artifacts: `num_books * 3`

### `tables/component_exemplar_chunks.csv`
Purpose: high-scoring positive/negative chunk exemplars per PCA component for interpretation.

Columns:
- `book_id`, `processed_dir`, `title`, `genre_primary`
- `chunk_index`
- `pc` (`PC1`..`PC5`)
- `direction` (`positive` or `negative`)
- `score`
- `text_preview`

Selection constraints:
- Minimum chunk spacing (same book/component/direction): `>= 5`
- Maximum selected chunks per book/component/direction: `3`
- Target selected rows per component+direction: up to `15`

### `tables/component_genre_association.csv`
Purpose: genre-level PCA component aggregation with effect-size style normalization.

Columns:
- `genre_primary`
- `pc`
- `genre_mean`
- `genre_book_count`
- `corpus_mean`
- `corpus_std`
- `delta_vs_corpus_mean`
- `effect_size_vs_corpus`

### `tables/temporal_trend_stats.csv`
Purpose: per-book temporal trend significance for `corr(PC, normalized_position)`.

Columns:
- `book_id`, `processed_dir`, `title`, `genre_primary`
- `pc`
- `corr_pc_position`
- `perm_pvalue` (two-sided permutation p-value)
- `perm_qvalue` (Benjamini-Hochberg adjusted within each component family)

### `tables/corpus_assoc_bootstrap.csv`
Purpose: bootstrap confidence intervals for corpus-level medians of PCA-speed to Twist Signal correlations.

Columns:
- `k`
- `metric` (`corr_speed_s` or `corr_speed_a`)
- `median`
- `ci_lower`
- `ci_upper`
- `n_books`

### `tables/projection_consistency_checks.csv`
Purpose: sampled consistency checks between recomputed PCA projection and stored `pca_d5.npy`.

Columns:
- `book_id`, `processed_dir`
- `checked` (bool)
- `max_abs_diff`
- `mean_abs_diff`
- `detail`

### `tables/pca_integrity_checks.csv`
Purpose: run-level validation summary covering shape, association, statistical, exemplar, and end-to-end checks.

Columns:
- `check` (str)
- `passed` (bool)
- `detail` (str)

### `tables/book_artifact_integrity.csv`
Purpose: per-book missing/mismatch artifact logging during PCA analysis loading.

Columns:
- `book_id`, `processed_dir`
- `issue`
- `severity` (`warning` or `error`)

### `tables/book_signal_assoc_issues.csv`
Purpose: per-book and per-`k` skip logging for signal-association calculations.

Columns:
- `book_id`, `processed_dir`, `k`
- `issue`
- `severity`

### `figures/*.png`
Representative files:
- `pca_variance_diagnostics.png`
- `component_score_distributions.png`
- `component_pairwise_by_genre.png`
- `temporal_trend_summary.png`
- `bootstrap_assoc_summary.png`
- `book_deep_dive_speed_signal_k7.png`

### `insights.md`
Purpose: narrative summary of component interpretation, book-level highlights, and sensitivity/caveats.

## Type and Parsing Notes
Fields serialized as JSON-like strings in CSV:
- `genre_secondary`
- `short_tags`
- `citations`

Recommended parsing strategy:
- Try `json.loads` first.
- Fallback to `ast.literal_eval` if needed.
- Normalize lists to either list objects or comma-separated strings depending on task.

## Validation Rules
Minimum checks for every run:
1. `metadata.id` is unique and non-null.
2. `metadata.processed_dir` exists for all rows.
3. Every `processed_dir` contains required per-book artifact files.
4. `features.csv` has complete `(book_id, k)` coverage.
5. No NaN/inf in numeric Twist Signal feature columns.
6. `dtw_distance_k7.npy` passes square/symmetric/zero-diagonal checks.
