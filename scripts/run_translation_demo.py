"""Run the handcrafted translation benchmark with sacrebleu chrF."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MPL_DIR = ROOT / ".mplconfig"
MPL_DIR.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_DIR))
os.environ.setdefault("MPLBACKEND", "Agg")

from translation import evaluate_chrf, plot_translation_report


INPUT_DIR = ROOT / "inputs_translation"
OUTPUT_DIR = ROOT / "outputs_translation"
INPUT_FILE = INPUT_DIR / "translation_benchmark.csv"


def _markdown_table(frame: pd.DataFrame, digits: int = 2) -> str:
    formatted = frame.copy()
    for column in formatted.columns:
        if pd.api.types.is_float_dtype(formatted[column]):
            formatted[column] = formatted[column].map(lambda value: f"{value:.{digits}f}")
    return formatted.to_html(index=False, escape=False, border=0)


def run_demo() -> None:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    benchmark = pd.read_csv(INPUT_FILE)
    evaluation = evaluate_chrf(benchmark)

    evaluation.per_example.to_csv(OUTPUT_DIR / "translation_per_example_scores.csv", index=False)
    evaluation.category_summary.to_csv(OUTPUT_DIR / "translation_category_summary.csv", index=False)
    pd.DataFrame([evaluation.summary | {"signature": evaluation.signature}]).to_csv(
        OUTPUT_DIR / "translation_summary.csv",
        index=False,
    )
    evaluation.best_examples(10).to_csv(OUTPUT_DIR / "translation_best_examples.csv", index=False)
    evaluation.worst_examples(10).to_csv(OUTPUT_DIR / "translation_worst_examples.csv", index=False)

    plot_translation_report(
        evaluation,
        title="Translation chrF Demo",
        output_path=OUTPUT_DIR / "translation_chrf_report.png",
    )

    report = "\n".join(
        [
            "# Translation Demo Report",
            "",
            "This report uses `sacrebleu` as the scoring engine for `chrF`.",
            "",
            f"Input benchmark: [`translation_benchmark.csv`](../inputs_translation/{INPUT_FILE.name})",
            "",
            "## Summary",
            "",
            _markdown_table(pd.DataFrame([evaluation.summary | {"signature": evaluation.signature}])),
            "",
            "## Category Summary",
            "",
            _markdown_table(evaluation.category_summary),
            "",
            "## Best Examples",
            "",
            _markdown_table(
                evaluation.best_examples(10)[
                    ["id", "category", "source", "reference", "candidate", "chrf"]
                ]
            ),
            "",
            "## Worst Examples",
            "",
            _markdown_table(
                evaluation.worst_examples(10)[
                    ["id", "category", "source", "reference", "candidate", "chrf"]
                ]
            ),
            "",
            "## Plot",
            "",
            "![translation chrF report](../outputs_translation/translation_chrf_report.png)",
            "",
        ]
    )
    (OUTPUT_DIR / "translation_demo_report.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    run_demo()
