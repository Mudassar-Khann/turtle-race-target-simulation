from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from adaptive_nav.simulator import RaceResult


RESULT_COLUMNS = [
    "run_id",
    "seed",
    "scenario",
    "winner",
    "steps",
    "model1_steps",
    "model2_steps",
    "model3_steps",
    "model4_steps",
    "epsilon_final",
]


def race_result_to_row(result: RaceResult) -> dict[str, object]:
    return {
        "run_id": result.run_id,
        "seed": result.seed,
        "scenario": result.scenario,
        "winner": result.winner,
        "steps": result.steps,
        "model1_steps": result.model_steps.get("model1", 0),
        "model2_steps": result.model_steps.get("model2", 0),
        "model3_steps": result.model_steps.get("model3", 0),
        "model4_steps": result.model_steps.get("model4", 0),
        "epsilon_final": f"{result.epsilon_final:.6f}",
    }


def append_results_csv(csv_path: str | Path, results: Iterable[RaceResult]) -> Path:
    path = Path(csv_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = path.exists()

    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_COLUMNS)
        if not file_exists:
            writer.writeheader()
        for result in results:
            writer.writerow(race_result_to_row(result))
    return path
