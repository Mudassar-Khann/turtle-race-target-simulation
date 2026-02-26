from __future__ import annotations

import argparse
import statistics
from pathlib import Path

from adaptive_nav.environment import MODEL_NAMES, load_scenarios
from adaptive_nav.logging_utils import append_results_csv
from adaptive_nav.simulator import RaceResult, RaceSimulator


def _default_scenarios_path() -> Path:
    return Path(__file__).resolve().parents[1] / "configs" / "scenarios.yaml"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Adaptive navigation benchmark runner.")
    parser.add_argument("--races", type=int, default=300, help="Number of races to run.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument(
        "--scenario",
        type=str,
        default="mixed",
        help="Scenario name or 'mixed' to cycle all scenarios.",
    )
    parser.add_argument("--save-csv", action="store_true", help="Append per-race logs to data/results.csv.")
    parser.add_argument("--no-learning", action="store_true", help="Disable RL learning updates.")
    parser.add_argument("--epsilon", type=float, default=None, help="Override RL epsilon.")
    parser.add_argument("--alpha", type=float, default=None, help="Override RL alpha.")
    parser.add_argument("--gamma", type=float, default=None, help="Override RL gamma.")
    parser.add_argument("--qtable-in", type=str, default=None, help="Directory containing saved Q-tables.")
    parser.add_argument("--qtable-out", type=str, default=None, help="Directory to persist learned Q-tables.")
    parser.add_argument(
        "--config",
        type=str,
        default=str(_default_scenarios_path()),
        help="Path to YAML scenario config.",
    )
    return parser.parse_args()


def _win_rate(wins: int, total: int) -> float:
    return (wins / total) * 100 if total > 0 else 0.0


def _print_results(
    results: list[RaceResult],
    scenario_names: tuple[str, ...],
) -> None:
    total_races = len(results)
    finished = [result for result in results if result.finished]
    unfinished = total_races - len(finished)

    print("Global Results")
    print("Win Rate:")
    model_labels = {
        "model1": "Model1",
        "model2": "Model2",
        "model3": "Model3",
        "model4": "Model4 (RL)",
    }
    for model in MODEL_NAMES:
        wins = sum(1 for result in finished if result.winner == model)
        print(f"{model_labels[model]}: {_win_rate(wins, total_races):.1f}%")

    print("\nStatistical Insight")
    print(f"mean steps: {statistics.mean(result.steps for result in results):.2f}")
    print(f"unfinished %: {_win_rate(unfinished, total_races):.2f}%")
    if total_races > 1:
        print(f"variance of performance (steps): {statistics.pvariance(result.steps for result in results):.2f}")
    else:
        print("variance of performance (steps): n/a")

    print("\nPer Scenario")
    for scenario in scenario_names:
        scenario_results = [result for result in results if result.scenario == scenario and result.finished]
        print(f"{scenario} ->")
        if not scenario_results:
            print("  no finished races")
            continue
        wins_by_model = {}
        for model in MODEL_NAMES:
            wins = sum(1 for result in scenario_results if result.winner == model)
            wins_by_model[model] = wins
            print(f"  {model}: {_win_rate(wins, len(scenario_results)):.1f}%")
        dominant_model = max(wins_by_model, key=wins_by_model.get)
        print(f"  insight: {dominant_model} dominates")

    print("\nAverage steps per winner")
    for model in MODEL_NAMES:
        model_steps = [result.steps for result in finished if result.winner == model]
        if not model_steps:
            print(f"{model}: n/a")
            continue
        print(f"{model}: {statistics.mean(model_steps):.2f}")


def run() -> None:
    args = parse_args()
    scenarios = load_scenarios(args.config)
    simulator = RaceSimulator(
        scenarios=scenarios,
        seed=args.seed,
        epsilon=args.epsilon,
        alpha=args.alpha,
        gamma=args.gamma,
        learning_enabled=not args.no_learning,
    )
    if args.qtable_in:
        simulator.load_q_tables(args.qtable_in)
    scenario_cycle = tuple(simulator.scenario_cycle(args.scenario))

    results: list[RaceResult] = []
    for race_idx in range(args.races):
        scenario_name = scenario_cycle[race_idx % len(scenario_cycle)]
        run_id = f"{args.seed}-{race_idx + 1:06d}"
        result = simulator.run_race(run_id=run_id, scenario_name=scenario_name)
        results.append(result)

    _print_results(results, scenario_cycle)

    if args.save_csv:
        csv_path = Path("data") / "results.csv"
        append_results_csv(csv_path, results)
        print(f"\nSaved race logs -> {csv_path}")

    if args.qtable_out:
        simulator.save_q_tables(args.qtable_out)
        print(f"Saved Q-tables -> {args.qtable_out}")


if __name__ == "__main__":
    run()
