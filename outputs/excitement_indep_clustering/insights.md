# indep_winsize_5 Clustering Insights (MA(W), current run W=5)

## 1) Setup and Integrity
- Books analyzed: **20**
- Input checks passed: label existence, shape normalization, range `[0,4]`, integer-like, and embedding length alignment.
- Feature set size: **33** numeric features per book.

## 2) Model Selection Results
- Feature branch selected: `kmeans` with `k=5` (silhouette=0.260, DB=0.888, CH=8.1).
- KMeans stability (mean pairwise ARI across seeds): 0.893.
- DTW branch selected: `average-linkage` with `k=2` (silhouette=0.085).

## 3) Cross-Method Agreement
- Adjusted Rand Index (feature vs DTW): **0.059**
- Normalized Mutual Information: **0.241**
- Agreement table: `outputs/excitement_indep_clustering/tables/cluster_method_agreement.csv`.

## 4) Feature-Branch Cluster Archetypes
- Cluster 1 (n=5): mean_early (delta_z=-1.11); p90_y (delta_z=-1.11); mean_ma5 (delta_z=-0.98). Representative: 1260 | Jane Eyre.
- Cluster 2 (n=6): prop_label_2 (delta_z=+1.08); prop_label_0 (delta_z=-0.95); p10_y (delta_z=+0.94). Representative: 768 | Wuthering Heights.
- Cluster 3 (n=6): std_diff (delta_z=+1.25); jump_ge_2_rate (delta_z=+1.16); mean_abs_diff (delta_z=+1.15). Representative: 1661 | The Adventures of Sherlock Holmes.
- Cluster 4 (n=1): prop_label_4 (delta_z=+3.62); mean_late (delta_z=+3.21); slope_position (delta_z=+2.58). Representative: 1513 | Romeo and Juliet.
- Cluster 5 (n=2): max_y (delta_z=-3.00); range_y (delta_z=-3.00); lag1_autocorr (delta_z=-1.84). Representative: 11 | Alice's Adventures in Wonderland.

## 5) DTW-Branch Shape Archetypes
- Cluster 1 (n=19): prop_label_4 (delta_z=-0.19); mean_late (delta_z=-0.17); slope_position (delta_z=-0.14). DTW medoid: 11 | Alice's Adventures in Wonderland.
- Cluster 2 (n=1): prop_label_4 (delta_z=+3.62); mean_late (delta_z=+3.21); slope_position (delta_z=+2.58). DTW medoid: 1513 | Romeo and Juliet.

## 6) Practical Reading
- Use feature clusters as primary interpretable archetypes.
- Use DTW clusters as trajectory-shape validation; disagreement flags uncertain archetypes.
- MA5 centroid plots are better for coarse pacing patterns than raw per-chunk spikes.

## 7) Next Steps
1. Add bootstrap stability over book-resampling for selected k.
2. Compare clustering using raw vs MA5-only feature subsets.
3. Add external validation against genre/twist metadata as weak labels.

## Provenance
- Figures: `outputs/excitement_indep_clustering/figures/*.png`
- Tables: `outputs/excitement_indep_clustering/tables/*.csv`
