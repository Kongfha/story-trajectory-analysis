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
