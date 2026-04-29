# Constraints Spec

## Scope

This spec defines lightweight constraint-oriented evaluations that check whether model output satisfies explicit structural requirements.

The initial v1 focus is `length adherence`, because it is quick to implement and often operationally useful.

This suite is intentionally simple and should remain separate from semantic-quality metrics.

## Inputs

Required inputs:

- `text`: generated output
- one or more target constraints

Supported v1 constraint types:

- maximum word count
- minimum word count
- target word-count range
- maximum character count
- minimum character count
- target character-count range

Optional future extensions:

- sentence-count constraints
- line-count constraints
- JSON-schema structural constraints
- regex or format constraints

## Core Metric

### Length Adherence

Length adherence measures whether generated text satisfies a specified word or character budget.

This is especially relevant for:

- summaries
- snippets
- push notifications
- UI-constrained text fields
- any downstream system with hard size limits

### Required Outputs

For each evaluated text, return:

- `word_count`
- `character_count`
- whether the text satisfies each active constraint

If a target range is supplied, also return:

- signed deviation from the nearest valid boundary
- absolute deviation

Example interpretations:

- negative deviation may mean too short
- positive deviation may mean too long

The sign convention should be documented consistently.

## Aggregate Reporting

When evaluating a dataset of generations, report:

- adherence rate
- average deviation among failures
- distribution of word counts or character counts

This makes the metric useful not just per example, but also across model variants and prompts.

## Recommended Output Structure

Suggested fields:

- `word_count`
- `character_count`
- `passes_word_constraint`
- `passes_character_constraint`
- `word_deviation`
- `character_deviation`

For corpus-level evaluation:

- `adherence_rate`
- `num_examples`
- `num_pass`
- `num_fail`
- summary statistics for counts and deviations

## Why This Belongs In V1

This is one of the cheapest useful evals in the paper:

- no model dependency
- no labeling dependency
- directly tied to real product requirements

It should therefore be part of the first implementation pass.

## Future Extensions

Possible future additions:

- instruction adherence beyond length
- formatting adherence
- schema validity
- citation-presence checks

These are adjacent, but should be added only after the basic length checks are stable.

## Non-Goals for V1

- semantic consistency
- factuality
- relevance
- learned quality scoring

Those belong to other evaluation suites and should not be mixed into this constraints module.
