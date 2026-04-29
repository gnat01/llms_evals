"""Sanity tests for the classification evaluator."""

from __future__ import annotations

import unittest

import numpy as np

from classification import evaluate_binary_classification


class ClassificationEvaluationTests(unittest.TestCase):
    def test_perfect_separation_has_near_perfect_metrics(self) -> None:
        y_true = np.array([0, 0, 0, 1, 1, 1])
        y_score = np.array([0.02, 0.08, 0.15, 0.82, 0.91, 0.99])

        evaluation = evaluate_binary_classification(y_true, y_score, num_bins=6)

        self.assertAlmostEqual(evaluation.summary["roc_auc"], 1.0)
        self.assertAlmostEqual(evaluation.summary["pr_auc"], 1.0)
        self.assertGreater(evaluation.summary["js_divergence"], 0.4)
        self.assertEqual(evaluation.confusion, {"tp": 3, "fp": 0, "tn": 3, "fn": 0})

    def test_cost_sensitive_threshold_prefers_recall_under_high_fn_cost(self) -> None:
        y_true = np.array([0, 0, 0, 0, 1, 1, 1, 1])
        y_score = np.array([0.05, 0.10, 0.20, 0.55, 0.35, 0.45, 0.60, 0.90])

        evaluation = evaluate_binary_classification(
            y_true,
            y_score,
            cost_fp=1.0,
            cost_fn=8.0,
            num_bins=8,
        )

        self.assertLessEqual(evaluation.summary["best_cost_threshold"], 0.45)
        self.assertLess(
            evaluation.summary["best_cost_per_example"],
            evaluation.summary["expected_cost_per_example"],
        )

    def test_flat_scores_produce_low_jsd(self) -> None:
        y_true = np.array([0, 0, 0, 1, 1, 1])
        y_score = np.array([0.50, 0.50, 0.50, 0.50, 0.50, 0.50])

        evaluation = evaluate_binary_classification(y_true, y_score, num_bins=5)

        self.assertAlmostEqual(evaluation.summary["roc_auc"], 0.5)
        self.assertAlmostEqual(evaluation.summary["js_divergence"], 0.0, places=4)


if __name__ == "__main__":
    unittest.main()
