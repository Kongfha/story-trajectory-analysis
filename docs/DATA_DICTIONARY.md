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
