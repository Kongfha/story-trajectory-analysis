# Other Experiments: Twist Signal and PCA Tracks

## Scope
This document summarizes additional experiments completed in the project that are not part of the primary final claim. The primary claim is centered on Teacher-Guided Semantic Basis Projection. The experiments below remain valuable, but they are intentionally separated to keep narrative focus clear.

## Twist Signal Track
Twist Signal experiments model local novelty dynamics from embedding trajectories using `s_t` and acceleration `a_t`. This branch supports exploratory narrative-change analysis and peak detection.

Key outputs:
- `../outputs/features.csv`
- `../outputs/clusters_kmeans.csv`
- `../outputs/clusters_hier.csv`
- `../outputs/dtw_distance_k7.npy`
- `../outputs/eda/`

## PCA Component Track
PCA experiments analyze unsupervised axes of variance and their temporal behavior across books. This is useful for structural diagnostics and exploratory component interpretation.

Key outputs:
- `../outputs/pca/global_pca_fit.npz`
- `../outputs/pca/global_pca_fit_meta.json`
- `../outputs/pca/global_pca_variance_summary.csv`
- `../outputs/pca_analysis/`

## Why This Is Secondary in the Final Narrative
The final narrative aims to evaluate supervised extraction of one specific semantic basis from embeddings using teacher labels. Twist Signal and PCA branches address different questions. They are retained as supporting evidence of broad project exploration and as future integration candidates, but they are not used as primary evidence for the teacher-guided semantic basis claim.
