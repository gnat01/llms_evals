# Classification Spec

## Scope

This spec defines the initial classification evaluation suite for binary classification tasks where the model emits:

- Ground-truth labels `y_true in {0, 1}`
- Predicted scores or probabilities `y_score in [0, 1]`

The suite is designed to support:

- Threshold-free ranking evaluation
- Thresholded decision evaluation
- Class-separation diagnostics
- Cost-sensitive operating-point selection

This suite assumes binary classification for v1. Multiclass and multilabel support are out of scope for now.

## Inputs

Required inputs:

- `y_true`: sequence of binary labels
- `y_score`: sequence of predicted probabilities or monotone scores for the positive class

Optional inputs:

- `threshold`: scalar in `[0, 1]` for hard classification
- `beta_values`: list or range of `beta` values for `F_beta`, default covering `0.1` through `2.0`
- `cost_fp`: cost assigned to false positives
- `cost_fn`: cost assigned to false negatives
- `num_bins`: histogram bins used for empirical score-distribution diagnostics

## Core Metrics

### Threshold-Free Metrics

These do not require a chosen threshold.

- `ROC-AUC`
  - Measures ranking quality across all thresholds.
  - Useful when class priors may shift or when downstream threshold selection is undecided.

- `PR-AUC`
  - Measures precision-recall tradeoff across all thresholds.
  - Should be emphasized when the positive class is rare or when false positives are expensive.

### Thresholded Metrics

These require a threshold to convert `y_score` into predicted labels.

- `precision`
- `recall`
- confusion matrix counts:
  - `tp`
  - `fp`
  - `tn`
  - `fn`

These should be computed at:

- A user-specified threshold, if provided
- Any threshold selected by a cost-sensitive rule, if cost inputs are provided

### F-Beta Sweep

The suite must compute `F_beta` for `beta` values spanning `0.1` to `2.0`.

Purpose:

- `beta < 1` emphasizes precision
- `beta > 1` emphasizes recall
- `beta = 1` gives standard `F1`

Recommended v1 behavior:

- Evaluate `F_beta` on a fixed grid over `beta in [0.1, 2.0]`
- Return both:
  - per-beta scores at the chosen threshold
  - the full score curve across beta values

This is mainly for completeness and for comparing operating preferences across tasks.

## Distribution-Separation Diagnostics

This is a mandatory part of the classification suite.

We split predicted scores into:

- `S0 = { y_score[i] | y_true[i] = 0 }`
- `S1 = { y_score[i] | y_true[i] = 1 }`

These score distributions should be analyzed empirically.

### Jensen-Shannon Divergence

`Jensen-Shannon divergence` between the empirical score distributions of class `0` and class `1` is mandatory.

Why it matters:

- It quantifies how separable the predicted-score distributions are.
- It is symmetric.
- It is more stable and interpretable than raw KL divergence in the presence of sparse bins.

Expected behavior:

- Build normalized histograms for `S0` and `S1`
- Apply smoothing if needed to avoid zero-probability instability
- Compute `JSD(P || Q)` on the resulting empirical distributions

This should be treated as a headline diagnostic, not an optional add-on.

### KL Divergence

Directional KL divergence is useful as a diagnostic but should not be the main separation metric.

Compute both:

- `KL(P || Q)`
- `KL(Q || P)`

where `P` and `Q` are the empirical score distributions for class `0` and class `1`.

Caveats:

- KL is asymmetric
- KL can be numerically brittle without smoothing
- KL is harder to interpret than JSD

For v1, KL should be clearly labeled as diagnostic.

## Cost-Sensitive Classification

This suite must support cost-sensitive evaluation because threshold choice is usually application-driven.

### Inputs

- `cost_fp`
- `cost_fn`

Optional future extension:

- class priors
- per-example weights
- business-value matrices

### Outputs

At minimum, the suite should support:

- expected cost at a chosen threshold
- threshold that minimizes expected cost over a threshold grid
- thresholded confusion counts and derived metrics at that operating point

Simple expected-cost formulation:

`expected_cost = cost_fp * fp + cost_fn * fn`

Possible normalized version:

`expected_cost_per_example = (cost_fp * fp + cost_fn * fn) / n`

### Why This Matters

Many production classifiers are not optimized for raw accuracy or even raw `F1`.
They are deployed at a threshold chosen to reflect business or safety asymmetries.
This makes cost-sensitive evaluation a first-class concern rather than an advanced feature.

## Plots and Diagnostics

The suite should specify outputs for both scalar metrics and visual diagnostics.

Recommended plots:

- ROC curve
- Precision-recall curve
- Precision and recall versus threshold
- Histogram or density plot of class-conditional score distributions
- Optional expected-cost versus threshold curve

These plots help determine whether a model is merely statistically decent or actually operable.

## Recommended Outputs

The evaluation result should contain:

- scalar summary metrics
- threshold-specific metrics
- distribution-separation metrics
- any selected operating threshold
- metadata about histogram binning and smoothing choices

Suggested top-level fields:

- `roc_auc`
- `pr_auc`
- `precision`
- `recall`
- `confusion_matrix`
- `f_beta`
- `f_beta_curve`
- `js_divergence`
- `kl_divergence_0_to_1`
- `kl_divergence_1_to_0`
- `cost_sensitive`
- `plots`

## Non-Goals for V1

The following are intentionally out of scope for this first version:

- multiclass metrics
- calibration metrics such as Brier score or ECE
- bootstrap confidence intervals
- statistical significance testing between models
- fairness slices and subgroup analysis

These are useful, but not needed for the first implementation pass.
