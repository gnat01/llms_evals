"""Sanity tests for translation chrF evaluation."""

from __future__ import annotations

import unittest

import pandas as pd

from translation import evaluate_chrf


class TranslationEvaluationTests(unittest.TestCase):
    def test_exact_match_scores_100(self) -> None:
        frame = pd.DataFrame(
            [
                {"id": "ex1", "category": "exact", "reference": "hola mundo", "candidate": "hola mundo"},
            ]
        )
        evaluation = evaluate_chrf(frame)
        self.assertAlmostEqual(evaluation.summary["chrf"], 100.0)
        self.assertAlmostEqual(evaluation.per_example.iloc[0]["chrf"], 100.0)

    def test_bad_candidate_scores_lower_than_good_candidate(self) -> None:
        frame = pd.DataFrame(
            [
                {"id": "good", "category": "quality", "reference": "buenos dias", "candidate": "buenos dias"},
                {"id": "bad", "category": "quality", "reference": "buenos dias", "candidate": "adios noche"},
            ]
        )
        evaluation = evaluate_chrf(frame)
        good_score = evaluation.per_example.loc[evaluation.per_example["id"] == "good", "chrf"].iloc[0]
        bad_score = evaluation.per_example.loc[evaluation.per_example["id"] == "bad", "chrf"].iloc[0]
        self.assertGreater(good_score, bad_score)

    def test_category_summary_is_emitted(self) -> None:
        frame = pd.DataFrame(
            [
                {"id": "a", "category": "cat1", "reference": "merci", "candidate": "merci"},
                {"id": "b", "category": "cat2", "reference": "merci", "candidate": "bonjour"},
            ]
        )
        evaluation = evaluate_chrf(frame)
        self.assertEqual(set(evaluation.category_summary["category"].tolist()), {"cat1", "cat2"})


if __name__ == "__main__":
    unittest.main()
