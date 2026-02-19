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

## Artifact Flow
File-level flow:
1. `data/raw/{raw_filename}.txt`
2. `data/processed/{processed_dir}/chunks.jsonl`
3. `data/processed/{processed_dir}/embeddings.npy`
4. `data/processed/{processed_dir}/index.json`
5. `data/processed/{processed_dir}/pca_d2.npy`, `pca_d5.npy`
6. `data/processed/{processed_dir}/signals_k{K}.npz`
7. `data/processed/{processed_dir}/peaks_k{K}.json`
8. `outputs/features.csv`
9. `outputs/clusters_kmeans.csv`, `outputs/clusters_hier.csv`
10. `outputs/dtw_distance_k7.npy`
11. `outputs/eda/*` from EDA notebook
12. `outputs/eda/novel_stacks/figures/*.png`
13. `outputs/eda/novel_stacks/tables/*.csv`
14. `docs/NOVEL_STACKED_OUTPUT_INTERPRETATION.md`

Directory keying:
- `processed_dir` is the canonical per-book key and is based on abbreviated title slug.

## Reproducibility and Caching
- Seeds are fixed in notebooks (`SEED=42`) for sampling/clustering consistency.
- Embedding stage supports cache reuse if existing artifacts match expected parameters.
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

## Extending the Pipeline
Recommended extension points:
- Add new signal variants while preserving `signals_k{K}.npz` compatibility.
- Add cluster methods and write separate output files instead of overwriting existing schemas.
- Add model-comparison runs by tagging outputs with model metadata.
- Add report-generation notebook/scripts that consume `outputs/` and `outputs/eda/`.
