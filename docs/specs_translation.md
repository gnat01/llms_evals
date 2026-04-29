# Translation Spec

## Scope

This spec defines the initial translation evaluation suite.

The primary v1 goal is to implement `chrF` as a strong, lightweight, reference-based translation metric with good practical value.

This spec does not propose re-implementing learned metrics such as `BLEURT`, `COMET`, or `COMETKiwi`. Those may be supported later via integration hooks, but not as native implementations in v1.

## Inputs

Required inputs:

- `references`: sequence of reference translations
- `candidates`: sequence of model-generated translations

Optional inputs:

- `max_order`: maximum character n-gram order, commonly up to `6`
- `beta`: weight controlling the balance between precision and recall
- `whitespace_normalization`: whether to normalize spacing before scoring
- `case_sensitive`: whether scoring preserves case

The evaluator assumes one candidate per reference for v1.
Multi-reference support may be added later.

## Core Metric

### chrF

`chrF` is the primary translation metric for v1.

It is a character n-gram F-score that compares candidate translations against reference translations using character-level overlap rather than token-level overlap.

Why it is worth implementing:

- It is far simpler than learned metrics
- It avoids tokenizer dependency
- It is robust across languages with rich morphology
- It is strong enough to be a practical baseline

### Conceptual Definition

For each character n-gram order:

- compute character-level precision
- compute character-level recall

Then combine them using an F-score-style harmonic mean with parameter `beta`.

At a high level:

- higher precision means candidate text matches the reference more tightly
- higher recall means candidate text covers more of the reference
- `beta > 1` weights recall more heavily

### Recommended V1 Behavior

- Implement standard `chrF`
- Use a sensible default n-gram order, typically up to `6`
- Return:
  - corpus-level `chrF`
  - optional per-example `chrF`

Per-example scores are useful for error inspection and ranking bad translations.

## Output Requirements

Minimum outputs:

- `chrf`
- `num_examples`
- configuration metadata:
  - `max_order`
  - `beta`
  - normalization flags

Optional outputs:

- `per_example_scores`
- aggregate summary stats such as mean, median, min, max

## Why Not Native BLEURT or COMET in V1

The paper mentions `BLEURT`, `COMET`, and `COMETKiwi` as strong translation evals, but they should not be quick native implementations for this repo.

Reasons:

- They depend on pretrained models
- They require nontrivial packaging and checkpoints
- They move the project from metric implementation into model integration

Thus the v1 translation spec should remain focused on `chrF`.

## Future Extensions

Possible future additions:

- `BLEURT` integration wrapper
- `COMET` integration wrapper
- `COMETKiwi` integration wrapper
- multi-reference support
- sentence-level ranking utilities

These extensions should be treated as separate workstreams from the initial metric implementation.

## Non-Goals for V1

- BLEU
- learned metric re-implementation
- MT-specific significance testing
- tokenizer-dependent metrics

The objective is a compact, reliable first translation metric, not a full MT benchmark framework.
