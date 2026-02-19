# Excitement Variant Analysis Insights (MA(W), current run W=5)

## 1) Dataset and Integrity Summary
- Books analyzed: **20** (reused split: 16 train / 4 test novels).
- All three label variants passed shape, range, and alignment checks (`len(label)==T`, labels in `[0,4]`, integer-like).
- `winsize_5` block-constancy check passed (no within-block variation for 5-chunk blocks).

## 2) Variant Comparison Findings
- Test split global metrics by variant (lower RMSE/MAE better; higher R2/corr better):
  - `indep_winsize_5`: RMSE=0.749, MAE=0.613, R2=0.075, corr=0.306, MA(5) MAE=0.270
  - `winsize_5`: RMSE=0.989, MAE=0.768, R2=0.152, corr=0.411, MA(5) MAE=0.621
  - `base`: RMSE=1.193, MAE=1.041, R2=0.136, corr=0.380, MA(5) MAE=0.460

- Pairwise label agreement indicates the variants are materially different sources, not trivial rewrites.
- See: `tables/variant_pairwise_agreement_global.csv` and `tables/variant_pairwise_agreement_per_book.csv`.

## 3) indep_winsize_5 Verdict (Primary Focus)
- Chunk-level reliability: **limited/moderate**. Raw pointwise error remains substantial.
- Trend-level utility (MA(5)): **useful as a coarse proxy** for trajectory/pacing interpretation.
- indep global train: RMSE=0.727, MAE=0.593, R2=0.193, corr=0.440, MA(5) MAE=0.244.
- indep global test: RMSE=0.749, MAE=0.613, R2=0.075, corr=0.306, MA(5) MAE=0.270.

## 4) Book-Level Highlights (indep_winsize_5, test novels)
- 1342 | Pride and Prejudice: RMSE=0.726, MAE=0.588, R2=0.043, corr=0.263, MA(5) MAE=0.260.
- 768 | Wuthering Heights: RMSE=0.747, MAE=0.615, R2=0.088, corr=0.327, MA(5) MAE=0.264.
- 113 | The Secret Garden: RMSE=0.747, MAE=0.611, R2=-0.002, corr=0.205, MA(5) MAE=0.272.
- 16 | Peter Pan: RMSE=0.816, MAE=0.678, R2=0.076, corr=0.283, MA(5) MAE=0.309.

## 5) Use Now vs Avoid Now (indep_winsize_5)
- Use now: relative trend profiling, chapter-level pacing summaries, cross-book smoothed trajectory comparison.
- Avoid now: chunk-level absolute scoring, spike-triggered threshold decisions, fine-grained event detection from raw predictions.

## 6) Next Experiments + Acceptance Criteria
1. Compare Ridge/ElasticNet against current linear GD head on the same split.
2. Add temporal features (`x_t - x_{t-1}`, short rolling context) while keeping linear head.
3. Try imbalance-aware objectives for rare labels.
4. Accept a new model only if both improve: test RMSE and worst-case test-novel RMSE.

## Provenance
- Figures: `outputs/excitement_variant_analysis/figures/*.png`
- Tables: `outputs/excitement_variant_analysis/tables/*.csv`
- Models: `outputs/excitement_variant_analysis/model/*.npz`
