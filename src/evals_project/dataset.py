from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from evals_project.schemas import GoldenCase


def load_golden_cases(path: str | Path) -> list[GoldenCase]:
    dataset_path = Path(path)
    cases: list[GoldenCase] = []
    with dataset_path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{dataset_path}:{line_number} contains invalid JSONL") from exc
            cases.append(GoldenCase.model_validate(payload))
    return cases


def write_golden_cases(path: str | Path, cases: Iterable[GoldenCase]) -> None:
    dataset_path = Path(path)
    dataset_path.parent.mkdir(parents=True, exist_ok=True)
    with dataset_path.open("w", encoding="utf-8") as handle:
        for case in cases:
            handle.write(case.model_dump_json() + "\n")
