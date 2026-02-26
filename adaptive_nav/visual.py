from __future__ import annotations

import argparse
import random
from pathlib import Path
from turtle import Screen, Turtle

from adaptive_nav.environment import (
    load_scenarios,
    observe_target,
    sample_target,
)
from adaptive_nav.models import step_model1, step_model2, step_model3, step_model4
from adaptive_nav.rl import QLearningConfig, QLearningNavigator
from adaptive_nav.simulator import MODEL_ORDER, START_POSITIONS


def _default_scenarios_path() -> Path:
    return Path(__file__).resolve().parents[1] / "configs" / "scenarios.yaml"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Adaptive navigation visual simulator.")
    parser.add_argument("--scenario", type=str, default="mixed", help="Scenario name or mixed.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument("--rounds", type=int, default=8, help="Number of rounds.")
    parser.add_argument("--frame-ms", type=int, default=80, help="Delay between animation frames.")
    parser.add_argument("--round-break-ms", type=int, default=900, help="Delay between rounds.")
    parser.add_argument("--no-learning", action="store_true", help="Disable RL updates.")
    parser.add_argument(
        "--config",
        type=str,
        default=str(_default_scenarios_path()),
        help="Path to YAML scenario config.",
    )
    return parser.parse_args()


class VisualTournament:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.scenarios = load_scenarios(args.config)
        self.rng = random.Random(args.seed)
        self.running = True
        self.finished = False
        self.round_index = 0
        self.round_step = 0
        self.round_winner: str | None = None
        self.current_target = (0.0, 0.0)
        self.current_scenario_name = ""
        self.current_scenario = None
        self.model4_rl: QLearningNavigator | None = None
        self.scores = {name: 0 for name in MODEL_ORDER}

        self.scenario_cycle = (
            tuple(self.scenarios.keys()) if args.scenario == "mixed" else (args.scenario,)
        )
        for name in self.scenario_cycle:
            if name not in self.scenarios:
                raise ValueError(f"Unknown scenario '{name}'")

        self.screen = Screen()
        self.screen.title("Adaptive Navigation Strategy Benchmark")
        self.screen.setup(width=900, height=650)
        self.screen.tracer(0)

        self.target_writer = Turtle(visible=False)
        self.target_writer.penup()

        self.status_writer = Turtle(visible=False)
        self.status_writer.penup()
        self.status_writer.goto(-430, 280)

        self.legend_writer = Turtle(visible=False)
        self.legend_writer.penup()
        self.legend_writer.goto(-430, -300)
        self.legend_writer.write(
            "black:model1 cardinal | red:model2 random-turn | green:model3 greedy | blue:model4 RL",
            font=("Arial", 10, "normal"),
        )

        self.agents = {
            "model1": self._create_agent("turtle", "black", START_POSITIONS["model1"]),
            "model2": self._create_agent("arrow", "red", START_POSITIONS["model2"]),
            "model3": self._create_agent("circle", "green", START_POSITIONS["model3"]),
            "model4": self._create_agent("square", "blue", START_POSITIONS["model4"]),
        }

    @staticmethod
    def _create_agent(shape: str, color: str, start: tuple[float, float]) -> Turtle:
        agent = Turtle(shape=shape)
        agent.pensize(2)
        agent.pencolor(color)
        agent.speed(0)
        agent.penup()
        agent.goto(start)
        agent.pendown()
        return agent

    def stop(self) -> None:
        self.running = False

    def reset_agents(self) -> None:
        for model_name, agent in self.agents.items():
            agent.clear()
            agent.penup()
            agent.goto(START_POSITIONS[model_name])
            agent.setheading(0)
            agent.pendown()

    def draw_target(self) -> None:
        self.target_writer.clear()
        self.target_writer.goto(self.current_target)
        self.target_writer.dot(16, "red")

    def draw_status(self, extra: str = "") -> None:
        self.status_writer.clear()
        epsilon_info = "n/a"
        if self.model4_rl is not None:
            epsilon_info = f"{self.model4_rl.epsilon:.4f}"
        lines = [
            f"Round {self.round_index + 1}/{self.args.rounds}",
            f"Scenario: {self.current_scenario_name}",
            f"Step: {self.round_step}",
            f"Score: {self.scores}",
            f"RL epsilon: {epsilon_info}",
            "Esc: stop",
        ]
        if extra:
            lines.append(extra)
        self.status_writer.write("\n".join(lines), font=("Arial", 11, "normal"))

    def _init_rl_for_round(self) -> None:
        assert self.current_scenario is not None
        cfg = self.current_scenario.model_configs["model4"]
        q_cfg = QLearningConfig(
            action_offsets=cfg.action_offsets,
            epsilon=cfg.epsilon,
            min_epsilon=cfg.min_epsilon,
            epsilon_decay=cfg.epsilon_decay,
            learning_enabled=not self.args.no_learning,
        )
        self.model4_rl = QLearningNavigator(q_cfg)

    def start_round(self) -> None:
        if self.finished:
            return
        if not self.running:
            self.finish_tournament("Tournament stopped by user.")
            return
        if self.round_index >= self.args.rounds:
            self.finish_tournament("Tournament complete.")
            return

        self.current_scenario_name = self.scenario_cycle[self.round_index % len(self.scenario_cycle)]
        self.current_scenario = self.scenarios[self.current_scenario_name]
        self.current_target = sample_target(self.current_scenario, self.rng)
        self._init_rl_for_round()
        self.round_step = 0
        self.round_winner = None

        self.reset_agents()
        self.draw_target()
        self.draw_status(self.current_scenario.description)
        self.screen.title(
            f"Adaptive Navigation Strategy Benchmark | {self.current_scenario_name} | Round {self.round_index + 1}"
        )
        self.screen.update()
        self.screen.ontimer(self.step_round, self.args.frame_ms)

    def finish_round(self) -> None:
        if self.round_winner is not None:
            self.scores[self.round_winner] += 1
            message = f"Winner: {self.round_winner} at step {self.round_step}."
        else:
            message = "No winner in this round."

        print(f"[Round {self.round_index + 1}] {message}")
        self.draw_status(message)
        self.screen.update()
        self.round_index += 1

        if self.running and self.round_index < self.args.rounds:
            self.screen.ontimer(self.start_round, self.args.round_break_ms)
        else:
            self.finish_tournament("Tournament complete." if self.running else "Tournament stopped by user.")

    def finish_tournament(self, message: str) -> None:
        if self.finished:
            return
        self.finished = True
        top_score = max(self.scores.values())
        champions = [model for model, score in self.scores.items() if score == top_score]
        summary = f"{message} Champion: {', '.join(champions)} ({top_score} wins)."
        print(summary)
        self.draw_status(summary)
        self.screen.title(summary)
        self.screen.update()

    def step_round(self) -> None:
        if self.finished:
            return
        if not self.running:
            self.finish_tournament("Tournament stopped by user.")
            return
        assert self.current_scenario is not None
        assert self.model4_rl is not None

        if self.round_winner is not None or self.round_step >= self.current_scenario.max_steps:
            self.finish_round()
            return

        self.round_step += 1
        for model_name in MODEL_ORDER:
            cfg = self.current_scenario.model_configs[model_name]
            perceived_target = observe_target(
                self.current_target,
                noise_level=cfg.sensor_noise,
                bounds=self.current_scenario.bounds,
                rng=self.rng,
            )

            if model_name == "model1":
                outcome = step_model1(
                    self.agents[model_name],
                    self.current_target,
                    self.rng,
                    cfg.step_size,
                    cfg.hit_radius,
                    self.current_scenario.bounds,
                    self.current_scenario.boundary_mode,
                )
            elif model_name == "model2":
                outcome = step_model2(
                    self.agents[model_name],
                    self.current_target,
                    self.rng,
                    cfg.step_size,
                    cfg.hit_radius,
                    self.current_scenario.bounds,
                    self.current_scenario.boundary_mode,
                )
            elif model_name == "model3":
                outcome = step_model3(
                    self.agents[model_name],
                    perceived_target,
                    self.rng,
                    cfg.step_size,
                    cfg.hit_radius,
                    cfg.jitter_degrees,
                    self.current_scenario.bounds,
                    self.current_scenario.boundary_mode,
                    goal_target=self.current_target,
                )
            else:
                outcome = step_model4(
                    self.agents[model_name],
                    target_true=self.current_target,
                    target_observed=perceived_target,
                    rng=self.rng,
                    step_size=cfg.step_size,
                    hit_radius=cfg.hit_radius,
                    bounds=self.current_scenario.bounds,
                    boundary_mode=self.current_scenario.boundary_mode,
                    rl_nav=self.model4_rl,
                )

            if outcome.hit:
                self.round_winner = model_name
                break

        self.draw_status()
        self.screen.update()
        self.screen.ontimer(self.step_round, self.args.frame_ms)

    def run(self) -> None:
        self.screen.listen()
        self.screen.onkey(self.stop, "Escape")
        self.start_round()
        self.screen.mainloop()


def run() -> None:
    args = parse_args()
    VisualTournament(args).run()


if __name__ == "__main__":
    run()
