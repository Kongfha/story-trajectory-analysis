# Verdict
- Chunk-level precision verdict: **not strong enough yet** for reliable absolute excitement scoring.
- Trend-level interpretation verdict (smoothed): **usable as a coarse proxy** for excitement dynamics across a novel.
- Bottom line: the model captures direction and pacing shape after smoothing, but misses too many raw chunk-level fluctuations to be used as a precise per-chunk label replacer.
- Smoothing notation in this report uses **MA(W)** where `W` is notebook-configured (`MA_WINDOW`). For the current run, `W=9` per `outputs/excitement_linear/tables/presentation_mae.csv`.

# Evidence by Figure
1. `outputs/excitement_linear/figures/train_loss_curve.png`
- Train and test MSE both drop quickly then plateau.
- Small train/test gap supports a generalization-stable but capacity-limited model.

2. `outputs/excitement_linear/figures/prediction_scatter_train_test.png`
- There is diagonal trend (signal exists), but the vertical spread is wide.
- This indicates moderate association, not high-fidelity point prediction.

3. `outputs/excitement_linear/figures/residual_hist_train_test.png`
- Residual spread is broad on both splits.
- Test residual mean is slightly positive, indicating slight overprediction on test novels.

4. `outputs/excitement_linear/figures/novel_overlay_test_16.png`
5. `outputs/excitement_linear/figures/novel_overlay_test_113.png`
6. `outputs/excitement_linear/figures/novel_overlay_test_768.png`
7. `outputs/excitement_linear/figures/novel_overlay_test_1342.png`
- Raw curves mismatch frequently at chunk level.
- MA(W) curves align better in direction and local pacing, but spikes and sharp transitions are often damped or missed (current run: `W=9`).

8. `outputs/excitement_linear/figures/mae_raw_vs_moving_average.png`
- Smoothing substantially reduces MAE for both train and test.
- This reinforces that the model is more useful for trend interpretation than raw pointwise estimation.

# Quantitative Summary
- Source: `outputs/excitement_linear/tables/global_metrics.csv`
  - Test RMSE: **1.193**
  - Test MAE: **1.041**
  - Test R2: **0.136**
  - Train RMSE: **1.203**
  - Train MAE: **1.064**
  - Train R2: **0.173**
- Interpretation: train/test are close, so underfitting is more likely than overfitting.

- Source: `outputs/excitement_linear/tables/presentation_mae.csv` (`ma_window` is runtime-configurable and equals `9` in the current run)
  - Train MAE raw: **1.064** vs MA(W): **0.328** (`W=9`)
  - Test MAE raw: **1.041** vs MA(W): **0.349** (`W=9`)

- Additional diagnostics from current outputs and model weights:
  - Raw correlation is moderate: test `corr(y, y_hat) ≈ 0.38`.
  - Smoothed correlation is stronger: test `corr(MA(W, y), MA(W, y_hat)) ≈ 0.70` (current run: `W=9`).
  - This supports trend-level use more than chunk-level use.

- Test-novel coverage from `outputs/excitement_linear/tables/per_novel_metrics.csv`
  - 16 | Peter Pan: RMSE `1.191`, MAE `1.033`, R2 `0.086`
  - 113 | The Secret Garden: RMSE `1.136`, MAE `0.968`, R2 `0.168`
  - 768 | Wuthering Heights: RMSE `1.234`, MAE `1.077`, R2 `0.112`
  - 1342 | Pride and Prejudice: RMSE `1.192`, MAE `1.057`, R2 `0.053`

# What the Model Can and Cannot Be Used For
| Use now | Do not use yet |
|---|---|
| Relative trend profiling across chunks | Chunk-level absolute excitement scoring |
| Chapter/segment pacing summaries | Fine-grained spike detection |
| Cross-book comparison using smoothed trajectories | Threshold-based high-excitement decisions (e.g., alert when >=3) |

# Risks / Caveats
- Label imbalance is significant. Label `4` is rare (~`1.7%`), limiting extreme-excitement calibration.
- The model is a single linear map, so nonlinear semantics and context interactions are under-modeled.
- Smoothing improves interpretability but can hide abrupt local events.
- Current conclusions are based on one fixed 16/4 novel split; split variability is not yet reported.

# Next Experiments (Prioritized)
1. Add stronger linear baselines on the same split.
- Try Ridge and ElasticNet against current linear GD baseline.

2. Use objective functions that better match the target.
- Try weighted MSE or ordinal-aware losses to handle rare high labels.

3. Add lightweight temporal features.
- Add `x_t - x_{t-1}` and short rolling embedding context before the linear head.

4. Keep strict acceptance criteria for adoption.
- Accept an upgrade only if both conditions hold:
- Test RMSE improves materially.
- Worst-case test-novel RMSE improves.

5. If linear upgrades saturate, then test small nonlinear capacity.
- Try a compact MLP with early stopping and same novel-level split protocol.

# Provenance
- Figures: `outputs/excitement_linear/figures/*.png`
- Tables: `outputs/excitement_linear/tables/global_metrics.csv`, `outputs/excitement_linear/tables/per_novel_metrics.csv`, `outputs/excitement_linear/tables/presentation_mae.csv`
- Split: `outputs/excitement_linear/tables/split_manifest.csv`
