# Copyright And Plagiarism Spec

## Scope

This spec defines an initial suite for detecting exact, near-exact, and approximate textual overlap relevant to copyright regurgitation and plagiarism-style analysis.

The suite should support two distinct stages:

- precise overlap measurement
- scalable candidate retrieval

These stages should not be conflated.

## Inputs

Required inputs depend on the mode.

### Pairwise Scoring Mode

Used when comparing a generated output against a known reference text.

Required:

- `source_text`
- `reference_text`

### Corpus Retrieval Mode

Used when searching for possible copied or near-duplicate matches across a larger corpus.

Required:

- `query_text`
- collection of `candidate_texts`

Optional:

- shingle size
- hash size
- Hamming-distance threshold
- LSH banding parameters

## Measurement Layer

These metrics quantify overlap once a candidate pair is already known.

### Longest Common Subsequence

Compute `LCS` between source and reference.

Recommended output:

- raw `lcs_length`
- normalized `lcs_ratio`

Normalization should be explicit. For this project, the default should align with the paper’s framing:

- normalize by prompt length or source length

This metric is useful for exact or nearly exact copied spans.

### Edit Distance

Compute edit distance between source and reference.

Recommended outputs:

- raw `edit_distance`
- normalized `edit_distance_ratio`

This gives a direct notion of how many insertions, deletions, and substitutions are needed to transform one text into the other.

### Edit Similarity

Return an edit-based similarity score derived from edit distance.

This should be scaled so that:

- larger values imply more similar texts
- the normalization convention is documented clearly

This is useful because raw edit distance alone is hard to compare across texts of different lengths.

## Approximate Similarity Layer

These methods are meant for fast candidate generation and large-scale duplicate detection.

### SimHash

`SimHash` is a mandatory approximate-duplicate metric in this suite.

Purpose:

- compact document fingerprinting
- fast near-duplicate lookup
- efficient comparison via Hamming distance

Recommended outputs:

- `simhash`
- `hamming_distance`
- optional boolean match under a configurable threshold

Important note:

SimHash is best used for approximate retrieval or filtering, not as the final legal or semantic overlap score.

### LSH

`LSH` is also part of the suite, but it should be framed correctly.

Purpose:

- scalable retrieval of likely matches
- candidate generation before exact scoring

LSH is not itself the final plagiarism score.
It is an indexing strategy that helps reduce the number of expensive pairwise comparisons.

Recommended use:

- build LSH buckets over shingles, MinHash signatures, or similar locality-preserving fingerprints
- retrieve likely candidates for a query text
- rerank or validate candidates using stronger pairwise metrics such as LCS and edit-based scores

## Recommended Pipeline Structure

The suite should support the following conceptual workflow:

1. Generate approximate candidates using `SimHash`, `LSH`, or both.
2. For each retrieved candidate, compute exact or near-exact overlap scores:
   - `LCS`
   - normalized edit distance
   - edit similarity
3. Produce final ranked matches with both approximate and exact metrics.

This layered design reflects the difference between:

- retrieval-stage utilities
- final overlap quantification

## Output Requirements

### Pairwise Mode

Suggested outputs:

- `lcs_length`
- `lcs_ratio`
- `edit_distance`
- `edit_distance_ratio`
- `edit_similarity`
- optional `simhash`
- optional `hamming_distance`

### Retrieval Mode

Suggested outputs:

- candidate ids
- candidate texts or references
- approximate retrieval scores
- exact reranking scores

The retrieval output should make it clear which numbers came from:

- approximate matching
- exact overlap scoring

## Design Notes

- Character-level and sequence-alignment metrics are better for quantifying reproduced spans.
- SimHash and LSH are better for scale and retrieval.
- Exact overlap metrics remain necessary even if fast approximate retrieval is present.

This distinction is operationally important and should remain explicit in both APIs and docs.

## Future Extensions

Possible future additions:

- MinHash over token shingles
- suffix-array or suffix-automaton based matching for long-span reuse
- span extraction showing copied regions
- chunked comparison for very long documents

These may become useful once the initial pairwise and retrieval utilities are stable.

## Non-Goals for V1

- legal-risk adjudication
- semantic paraphrase detection
- embedding-based plagiarism scoring
- OCR or multimodal copyright checks

The goal is a compact text-overlap suite, not a complete originality-detection platform.
