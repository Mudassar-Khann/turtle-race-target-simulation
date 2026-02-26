from __future__ import annotations

import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from adaptive_nav.environment import (
    MODEL_NAMES,
    ScenarioConfig,
    observe_target,
    sample_target,
)
from adaptive_nav.models import step_model1, step_model2, step_model3, step_model4
from adaptive_nav.rl import QLearningConfig, QLearningNavigator


MODEL_ORDER = ("model1", "model2", "model3", "model4")
START_POSITIONS = {
    "model1": (0.0, 0.0),
    "model2": (-250.0, 0.0),
    "model3": (250.0, 0.0),
    "model4": (0.0, -200.0),
}


@dataclass
class RaceResult:
    run_id: str
    seed: int
    scenario: str
    winner: str
    steps: int
    model_steps: dict[str, int]
    epsilon_final: float
    finished: bool


class SimTurtle:
    """Minimal turtle-compatible object for fast benchmark simulation."""

    def __init__(self, start_pos: tuple[float, float]):
        self._x, self._y = start_pos
        self._heading = 0.0

    def pos(self) -> tuple[float, float]:
        return self._x, self._y

    def goto(self, x: float, y: float | None = None) -> None:
        if y is None:
            x, y = x  # type: ignore[misc]
        self._x = float(x)
        self._y = float(y)

    def heading(self) -> float:
        return self._heading

    def setheading(self, angle: float) -> None:
        self._heading = float(angle) % 360

    def left(self, angle: float) -> None:
        self._heading = (self._heading + float(angle)) % 360

    def forward(self, distance: float) -> None:
        radians = math.radians(self._heading)
        self._x += float(distance) * math.cos(radians)
        self._y += float(distance) * math.sin(radians)

    def towards(self, target: tuple[float, float]) -> float:
        tx, ty = target
        return math.degrees(math.atan2(ty - self._y, tx - self._x)) % 360


class RaceSimulator:
    def __init__(
        self,
        scenarios: dict[str, ScenarioConfig],
        seed: int,
        epsilon: float | None = None,
        alpha: float | None = None,
        gamma: float | None = None,
        learning_enabled: bool = True,
    ):
        self.scenarios = scenarios
        self.seed = seed
        self.rng = random.Random(seed)
        self.override_epsilon = epsilon
        self.override_alpha = alpha
        self.override_gamma = gamma
        self.learning_enabled = learning_enabled
        self.rl_policies: dict[str, QLearningNavigator] = {}

    def scenario_cycle(self, mode: str) -> Iterable[str]:
        if mode == "mixed":
            return tuple(self.scenarios.keys())
        if mode not in self.scenarios:
            raise ValueError(f"Unknown scenario '{mode}'")
        return (mode,)

    def _init_rl(self, scenario: ScenarioConfig) -> QLearningNavigator:
        model_cfg = scenario.model_configs["model4"]
        config = QLearningConfig(
            action_offsets=model_cfg.action_offsets,
            alpha=self.override_alpha if self.override_alpha is not None else 0.2,
            gamma=self.override_gamma if self.override_gamma is not None else 0.95,
            epsilon=self.override_epsilon if self.override_epsilon is not None else model_cfg.epsilon,
            min_epsilon=model_cfg.min_epsilon,
            epsilon_decay=model_cfg.epsilon_decay,
            learning_enabled=self.learning_enabled,
        )
        return QLearningNavigator(config)

    def _get_rl_policy(self, scenario_name: str, scenario: ScenarioConfig) -> QLearningNavigator:
        policy = self.rl_policies.get(scenario_name)
        if policy is None:
            policy = self._init_rl(scenario)
            self.rl_policies[scenario_name] = policy
        policy.set_learning_mode(self.learning_enabled)
        return policy

    def save_q_tables(self, directory: str | Path) -> None:
        output_dir = Path(directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        for scenario_name, policy in self.rl_policies.items():
            policy.save_q_table(output_dir / f"{scenario_name}.pkl")

    def load_q_tables(self, directory: str | Path) -> None:
        input_dir = Path(directory)
        if not input_dir.exists():
            return
        for scenario_name, scenario in self.scenarios.items():
            policy = self._get_rl_policy(scenario_name, scenario)
            policy.load_q_table(input_dir / f"{scenario_name}.pkl")

    def run_race(self, run_id: str, scenario_name: str) -> RaceResult:
        if scenario_name not in self.scenarios:
            raise ValueError(f"Unknown scenario '{scenario_name}'")

        scenario = self.scenarios[scenario_name]
        target = sample_target(scenario, self.rng)
        rl_nav = self._get_rl_policy(scenario_name, scenario)
        model_steps = {name: 0 for name in MODEL_NAMES}
        agents = {
            model_name: SimTurtle(START_POSITIONS[model_name]) for model_name in MODEL_ORDER
        }

        for step in range(1, scenario.max_steps + 1):
            for model_name in MODEL_ORDER:
                model_steps[model_name] += 1
                cfg = scenario.model_configs[model_name]
                perceived_target = observe_target(
                    target,
                    noise_level=cfg.sensor_noise,
                    bounds=scenario.bounds,
                    rng=self.rng,
                )

                if model_name == "model1":
                    outcome = step_model1(
                        agents[model_name],
                        target,
                        self.rng,
                        step_size=cfg.step_size,
                        hit_radius=cfg.hit_radius,
                        bounds=scenario.bounds,
                        boundary_mode=scenario.boundary_mode,
                    )
                elif model_name == "model2":
                    outcome = step_model2(
                        agents[model_name],
                        target,
                        self.rng,
                        step_size=cfg.step_size,
                        hit_radius=cfg.hit_radius,
                        bounds=scenario.bounds,
                        boundary_mode=scenario.boundary_mode,
                    )
                elif model_name == "model3":
                    outcome = step_model3(
                        agents[model_name],
                        perceived_target,
                        self.rng,
                        step_size=cfg.step_size,
                        hit_radius=cfg.hit_radius,
                        jitter_degrees=cfg.jitter_degrees,
                        bounds=scenario.bounds,
                        boundary_mode=scenario.boundary_mode,
                        goal_target=target,
                    )
                else:
                    outcome = step_model4(
                        agents[model_name],
                        target_true=target,
                        target_observed=perceived_target,
                        rng=self.rng,
                        step_size=cfg.step_size,
                        hit_radius=cfg.hit_radius,
                        bounds=scenario.bounds,
                        boundary_mode=scenario.boundary_mode,
                        rl_nav=rl_nav,
                    )

                if outcome.hit:
                    return RaceResult(
                        run_id=run_id,
                        seed=self.seed,
                        scenario=scenario_name,
                        winner=model_name,
                        steps=step,
                        model_steps=model_steps,
                        epsilon_final=rl_nav.epsilon,
                        finished=True,
                    )

        return RaceResult(
            run_id=run_id,
            seed=self.seed,
            scenario=scenario_name,
            winner="unfinished",
            steps=scenario.max_steps,
            model_steps=model_steps,
            epsilon_final=rl_nav.epsilon,
            finished=False,
        )
