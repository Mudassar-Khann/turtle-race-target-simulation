from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

MODEL_ORDER = ("model1", "model2", "model3", "model4")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot adaptive navigation experiment results.")
    parser.add_argument("--csv", type=str, default="data/results.csv", help="Path to benchmark CSV output.")
    parser.add_argument("--out-dir", type=str, default="experiments/plots", help="Directory for plot images.")
    return parser.parse_args()


def load_rows(csv_path: Path) -> list[dict[str, str]]:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def plot_win_rate_per_model(rows: list[dict[str, str]], out_dir: Path) -> None:
    finished = [row for row in rows if row["winner"] != "unfinished"]
    wins = Counter(row["winner"] for row in finished)
    total = len(rows)
    rates = [100.0 * wins.get(model, 0) / total if total else 0.0 for model in MODEL_ORDER]

    plt.figure(figsize=(8, 4.5))
    plt.bar(MODEL_ORDER, rates, color=["black", "red", "green", "blue"])
    plt.ylabel("Win Rate (%)")
    plt.title("Win Rate per Model")
    plt.ylim(0, max(rates + [5]) * 1.2)
    plt.tight_layout()
    plt.savefig(out_dir / "win_rate_per_model.png", dpi=150)
    plt.close()


def plot_win_rate_per_scenario(rows: list[dict[str, str]], out_dir: Path) -> None:
    scenario_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        scenario_rows[row["scenario"]].append(row)

    scenarios = sorted(scenario_rows.keys())
    if not scenarios:
        return

    bar_width = 0.2
    x = list(range(len(scenarios)))
    colors = ["black", "red", "green", "blue"]

    plt.figure(figsize=(10, 5))
    for model_idx, model in enumerate(MODEL_ORDER):
        rates = []
        for scenario in scenarios:
            rows_for_scenario = scenario_rows[scenario]
            finished = [row for row in rows_for_scenario if row["winner"] != "unfinished"]
            if not finished:
                rates.append(0.0)
                continue
            wins = sum(1 for row in finished if row["winner"] == model)
            rates.append(100.0 * wins / len(finished))
        offsets = [value + (model_idx - 1.5) * bar_width for value in x]
        plt.bar(offsets, rates, width=bar_width, label=model, color=colors[model_idx])

    plt.xticks(x, scenarios, rotation=15)
    plt.ylabel("Win Rate (%)")
    plt.title("Win Rate per Scenario")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "win_rate_per_scenario.png", dpi=150)
    plt.close()


def plot_average_steps_per_winner(rows: list[dict[str, str]], out_dir: Path) -> None:
    winner_steps: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        winner = row["winner"]
        if winner == "unfinished":
            continue
        winner_steps[winner].append(int(row["steps"]))

    averages = [
        (sum(winner_steps.get(model, [])) / len(winner_steps[model])) if winner_steps.get(model) else 0.0
        for model in MODEL_ORDER
    ]
    plt.figure(figsize=(8, 4.5))
    plt.bar(MODEL_ORDER, averages, color=["black", "red", "green", "blue"])
    plt.ylabel("Average Winning Steps")
    plt.title("Average Steps per Winner")
    plt.tight_layout()
    plt.savefig(out_dir / "average_steps_per_winner.png", dpi=150)
    plt.close()


def plot_epsilon_decay(rows: list[dict[str, str]], out_dir: Path) -> None:
    epsilon_points = [float(row["epsilon_final"]) for row in rows if row.get("epsilon_final") not in (None, "")]

    plt.figure(figsize=(8, 4.5))
    if epsilon_points:
        plt.plot(range(1, len(epsilon_points) + 1), epsilon_points, color="blue")
    else:
        plt.plot([], [])
    plt.xlabel("Race Index")
    plt.ylabel("Epsilon Final")
    plt.title("RL Epsilon Decay Curve")
    plt.tight_layout()
    plt.savefig(out_dir / "epsilon_decay_curve.png", dpi=150)
    plt.close()


def main() -> None:
    args = parse_args()
    csv_path = Path(args.csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = load_rows(csv_path)
    plot_win_rate_per_model(rows, out_dir)
    plot_win_rate_per_scenario(rows, out_dir)
    plot_average_steps_per_winner(rows, out_dir)
    plot_epsilon_decay(rows, out_dir)

    print(f"Saved plots to {out_dir}")


if __name__ == "__main__":
    main()
