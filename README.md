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
- `data/raw/`: cleaned book text files (abbreviated title filenames).
- `data/processed/{processed_dir}/`: per-book chunk, embedding, signal, peak, PCA artifacts.
- `outputs/`: global outputs (`features.csv`, cluster CSVs, DTW matrix, summary).
- `outputs/eda/`: EDA figures, tables, and insight narrative.
- `docs/`: pipeline, schema dictionary, EDA planning, and output interpretation docs.

## Pipeline Run Order
Run notebooks in this order:
1. `00_download_and_clean.ipynb`
2. `01_chunk_and_embed.ipynb`
3. `02_transform_and_cluster.ipynb`
4. `03_eda_and_visualization.ipynb`

## Key Outputs for EDA/Insight Work
Core files:
- `outputs/features.csv`: one row per `(book_id, k)` with Twist Signal-derived metrics + metadata.
- `outputs/clusters_kmeans.csv`: feature-based KMeans labels.
- `outputs/clusters_hier.csv`: hierarchical labels (`feature_ward` and `dtw_average`).
- `outputs/dtw_distance_k7.npy`: pairwise DTW distances on resampled `s_t` for `k=7`.

Per-book files:
- `data/processed/{processed_dir}/signals_k{K}.npz`
- `data/processed/{processed_dir}/peaks_k{K}.json`
- `data/processed/{processed_dir}/pca_d2.npy`
- `data/processed/{processed_dir}/pca_d5.npy`

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
