# EDA and Visualization Plan

## EDA Goals
- Understand global behavior of Twist Signal features across the 20-book corpus.
- Compare cluster structures across methods (`kmeans`, `feature_ward`, `dtw_average`).
- Connect model-derived behavior (`s_t`, `a_t`, peaks, DTW) with catalog metadata labels.
- Produce reusable figures and tables for follow-up research notebooks/reports.

## Analysis Questions
1. Which books show highest novelty and acceleration intensity?
2. How much do feature distributions shift across `k = 5, 7, 11`?
3. Are cluster assignments aligned with metadata labels (genre, format, publication period, origin)?
4. Which books are nearest neighbors by DTW distance?
5. Which books look like outliers under Twist Signal dynamics?
6. How consistent are conclusions across feature-based and DTW-based grouping?

## Visualization Backlog (Priority-Ordered)
1. **Corpus composition**
- Count plots: `genre_primary`, `format`, `origin_country`, `original_language`
- Publication-year histogram

2. **Twist Signal feature distributions**
- Histograms/boxplots/violin by `k` for `mean_s`, `std_s`, `max_s`, `mean_a`, `std_a`, `max_a`
- Correlation heatmap for numeric features
- Interactive scatter(s) for selected feature pairs

3. **Cluster diagnostics**
- Cluster size by method and `k`
- Cluster composition by metadata categories
- Cross-tab agreement: KMeans vs feature_ward

4. **DTW structure**
- DTW heatmap with labels
- Nearest-neighbor table (top 1-3)
- MDS projection from DTW matrix

5. **Book-level trajectory deep dives**
- `s_t` and `a_t` line plots for representative books
- Peak markers overlaid on acceleration
- Metadata and `twist_peak_reason` annotation panel

## Insight Framework
Two interpretation tiers:

1. **Exploratory Observations**
- Descriptive summaries of what is directly visible in current outputs.
- No causal claims.
- Focus on distributions, rankings, and grouping patterns.

2. **Deeper Interpretation (Hypotheses)**
- Candidate narrative archetypes and cross-book storyline behavior patterns.
- Must include confidence level and caveat line for each claim.

Confidence labels:
- `High`: pattern appears across methods/parameters and has strong separation.
- `Medium`: pattern appears in one method or one parameterization with moderate support.
- `Low`: tentative pattern requiring further validation.

## Validation Before Claiming Insights
Required checks before stronger claims:
1. Compare conclusions across `k = 5, 7, 11`.
2. Compare KMeans vs hierarchical outcomes.
3. Re-check key findings with and without selected metadata fields.
4. Track outlier sensitivity (books with very high/low `T` or extreme max values).
5. Validate DTW findings against feature-space findings.

Optional advanced checks:
- Bootstrap sampling on feature rows.
- Alternative distance metrics (cosine/euclidean on normalized time series).
- Stability diagnostics over random seeds for clustering.

## Deliverables and Iteration Loop
Iteration loop:
1. Run `03_eda_and_visualization.ipynb`.
2. Export figures/tables to `outputs/eda/`.
3. Review `outputs/eda/insights.md`.
4. Convert low-confidence interpretations into explicit follow-up tests.

Primary deliverables:
- `outputs/eda/figures/*`
- `outputs/eda/tables/*`
- `outputs/eda/insights.md`

Metadata-guided analyses to always include:
- Categorical: `genre_primary`, `format`, `origin_country`, `original_language`
- Temporal: `first_publication_year`
- Human-labeled ranks: `recognizability_rank`, `genre_clarity_rank`, `twist_peak_rank`
- Relation between these labels and Twist Signal features + cluster assignments
