# EDA Insights: Twist Signal

## Exploratory Observations
- k=7 mean_s ranges from 0.142 to 0.222 across books.
- k=7 max_a ranges from 0.208 to 0.491.
- DTW distance matrix mean is 0.618 with nearest-neighbor mean 0.550.
- Feature-based clusters are more balanced than DTW-average hierarchical clusters in current settings.

Top books by mean_s (k=7):
- 35 | The Time Machine | mean_s=0.222 | genre=Sci-Fi
- 345 | Dracula | mean_s=0.222 | genre=Horror
- 175 | The Phantom of the Opera | mean_s=0.210 | genre=Gothic

Top books by max_a (k=7):
- 84 | Frankenstein; Or, The Modern Prometheus | max_a=0.491 | genre=Sci-Fi
- 113 | The Secret Garden | max_a=0.467 | genre=Children's Fiction
- 43 | The Strange Case of Dr. Jekyll and Mr. Hyde | max_a=0.434 | genre=Horror

Low mean_s books (k=7):
- 1342 | Pride and Prejudice | mean_s=0.142 | genre=Romance
- 1257 | The Three Musketeers | mean_s=0.164 | genre=Adventure
- 768 | Wuthering Heights | mean_s=0.165 | genre=Gothic

## Deeper Interpretation Hypotheses
- Hypothesis (Medium confidence): books with higher max_a show sharper local narrative transitions and may correspond to stronger labeled twist intensity.
- Hypothesis (Medium confidence): feature-space clusters separate multiple trajectory regimes, while DTW-average currently collapses many books into a dominant basin.
- Hypothesis (Low confidence): genre labels partially align with trajectory clusters, but overlap suggests shared pacing motifs across genres.

## Caveats and Validation Next Steps
- Caveat: clustering defaults are baseline and not hyperparameter-optimized.
- Caveat: interpretations should be rechecked across k values and alternative distance/linkage settings.
- Caveat: metadata rank labels are helpful but subjective and should not be treated as strict ground truth.
