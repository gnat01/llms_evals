"""Build a larger multilingual translation benchmark from sacrebleu test sets."""

from __future__ import annotations

import os
import random
import re
import string
from pathlib import Path

import pandas as pd
from sacrebleu.dataset import DATASETS


ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / ".sacrebleu_cache"
INPUT_DIR = ROOT / "inputs_translation"
OUTPUT_FILE = INPUT_DIR / "translation_benchmark.csv"

os.environ.setdefault("SACREBLEU", str(CACHE_DIR))

LANGUAGE_SPECS = [
    {"language": "Spanish", "langpair": "en-es", "dataset": "wmt13", "sample_size": 143},
    {"language": "Italian", "langpair": "en-it", "dataset": "wmt09", "sample_size": 143},
    {"language": "Japanese", "langpair": "en-ja", "dataset": "wmt24", "sample_size": 143},
    {"language": "Turkish", "langpair": "en-tr", "dataset": "wmt18", "sample_size": 143},
    {"language": "Hindi", "langpair": "en-hi", "dataset": "wmt24", "sample_size": 143},
    {"language": "Arabic", "langpair": "en-ar", "dataset": "iwslt17", "sample_size": 143},
    {"language": "Tamil", "langpair": "en-ta", "dataset": "wmt20", "sample_size": 142},
]

PUNCTUATION_PATTERN = re.compile(r"[{}]".format(re.escape(string.punctuation + "。、！？，؛،؟")))
WHITESPACE_PATTERN = re.compile(r"\s+")


def _read_lines(path: str) -> list[str]:
    return Path(path).read_text(encoding="utf-8").splitlines()


def _load_parallel_data(dataset_name: str, langpair: str) -> tuple[list[str], list[str]]:
    files = DATASETS[dataset_name].get_files(langpair)
    src_path = next(path for path in files if path.endswith(".src"))
    ref_candidates = [path for path in files if ".ref" in Path(path).name]
    ref_path = ref_candidates[0]
    return _read_lines(src_path), _read_lines(ref_path)


def _normalize_spaces(text: str) -> str:
    return WHITESPACE_PATTERN.sub(" ", text).strip()


def _drop_punctuation(text: str) -> str:
    cleaned = PUNCTUATION_PATTERN.sub("", text)
    return _normalize_spaces(cleaned) or text.strip()


def _truncate_text(text: str) -> str:
    tokens = text.split()
    if len(tokens) >= 4:
        keep = max(1, int(round(len(tokens) * 0.75)))
        return " ".join(tokens[:keep])
    if len(text) >= 8:
        keep = max(1, int(round(len(text) * 0.75)))
        return text[:keep].strip() or text
    return text


def _delete_middle_fragment(text: str) -> str:
    tokens = text.split()
    if len(tokens) >= 3:
        idx = len(tokens) // 2
        candidate = tokens[:idx] + tokens[idx + 1 :]
        return " ".join(candidate) or text
    if len(text) >= 4:
        idx = len(text) // 2
        candidate = (text[:idx] + text[idx + 1 :]).strip()
        return candidate or text
    return text


def _swap_middle_chunks(text: str) -> str:
    tokens = text.split()
    if len(tokens) >= 4:
        swapped = tokens[:]
        mid = len(swapped) // 2
        swapped[mid - 1], swapped[mid] = swapped[mid], swapped[mid - 1]
        return " ".join(swapped)
    if len(text) >= 6:
        chunk = max(1, len(text) // 3)
        parts = [text[:chunk], text[chunk : 2 * chunk], text[2 * chunk :]]
        parts[0], parts[1] = parts[1], parts[0]
        return "".join(parts).strip() or text
    return text


def _append_source_leakage(reference: str, source: str) -> str:
    source_tokens = source.split()
    if source_tokens:
        leak = " ".join(source_tokens[:2])
        return f"{reference.strip()} {leak}".strip()
    return reference


def _duplicate_fragment(text: str) -> str:
    tokens = text.split()
    if len(tokens) >= 2:
        idx = len(tokens) // 2
        tokens.insert(idx, tokens[idx])
        return " ".join(tokens)
    if len(text) >= 3:
        idx = len(text) // 2
        return f"{text[:idx]}{text[idx]}{text[idx:]}"
    return text


def _build_candidate(reference: str, source: str, mode: str) -> str:
    if mode == "exact_match":
        return reference.strip()
    if mode == "punctuation_drop":
        return _drop_punctuation(reference)
    if mode == "partial_truncation":
        return _truncate_text(reference)
    if mode == "middle_deletion":
        return _delete_middle_fragment(reference)
    if mode == "local_reordering":
        return _swap_middle_chunks(reference)
    if mode == "source_leakage":
        return _append_source_leakage(reference, source)
    if mode == "fragment_duplication":
        return _duplicate_fragment(reference)
    raise ValueError(f"Unknown mode: {mode}")


def build_benchmark(seed: int = 17) -> pd.DataFrame:
    random.seed(seed)
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    modes = [
        "exact_match",
        "punctuation_drop",
        "partial_truncation",
        "middle_deletion",
        "local_reordering",
        "source_leakage",
        "fragment_duplication",
    ]

    rows: list[dict[str, str | int]] = []
    global_index = 1

    for spec in LANGUAGE_SPECS:
        sources, references = _load_parallel_data(spec["dataset"], spec["langpair"])
        available_indices = list(range(len(sources)))
        sample_size = min(spec["sample_size"], len(available_indices))
        sampled_indices = sorted(random.sample(available_indices, sample_size))

        for local_position, sample_index in enumerate(sampled_indices):
            source = _normalize_spaces(sources[sample_index])
            reference = _normalize_spaces(references[sample_index])
            mode = modes[local_position % len(modes)]
            candidate = _build_candidate(reference, source, mode)
            rows.append(
                {
                    "id": f"mt{global_index:04d}",
                    "language": spec["language"],
                    "dataset": spec["dataset"],
                    "langpair": spec["langpair"],
                    "category": mode,
                    "source": source,
                    "reference": reference,
                    "candidate": candidate,
                    "notes": f"{spec['dataset']} sampled official pair with {mode}",
                }
            )
            global_index += 1

    frame = pd.DataFrame(rows)
    frame.to_csv(OUTPUT_FILE, index=False)
    return frame


if __name__ == "__main__":
    build_benchmark()
