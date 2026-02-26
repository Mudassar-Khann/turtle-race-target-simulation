from __future__ import annotations

import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import yaml


MODEL_NAMES = ("model1", "model2", "model3", "model4")


class AgentLike(Protocol):
    def pos(self) -> tuple[float, float]:
        ...

    def goto(self, x: float, y: float | None = None) -> None:
        ...

    def heading(self) -> float:
        ...

    def setheading(self, angle: float) -> None:
        ...


@dataclass(frozen=True)
class ModelConfig:
    step_size: float
    hit_radius: float
    sensor_noise: float
    jitter_degrees: int = 60
    action_offsets: tuple[int, ...] = (-30, -15, 0, 15, 30)
    epsilon: float = 0.2
    min_epsilon: float = 0.05
    epsilon_decay: float = 0.99


@dataclass(frozen=True)
class ScenarioConfig:
    name: str
    description: str
    boundary_mode: str
    bounds: tuple[float, float, float, float]
    target_mode: str
    target_x_range: tuple[int, int]
    target_y_range: tuple[int, int]
    target_grid_step: int
    max_steps: int
    model_configs: dict[str, ModelConfig]


def _merge_dict(base: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_dict(merged[key], value)
        else:
            merged[key] = value
    return merged


def _tuple2(values: Any) -> tuple[int, int]:
    return int(values[0]), int(values[1])


def _tuple4(values: Any) -> tuple[float, float, float, float]:
    return float(values[0]), float(values[1]), float(values[2]), float(values[3])


def _parse_model_config(data: dict[str, Any]) -> ModelConfig:
    action_offsets = tuple(int(v) for v in data.get("action_offsets", (-30, -15, 0, 15, 30)))
    return ModelConfig(
        step_size=float(data["step_size"]),
        hit_radius=float(data["hit_radius"]),
        sensor_noise=float(data["sensor_noise"]),
        jitter_degrees=int(data.get("jitter_degrees", 60)),
        action_offsets=action_offsets,
        epsilon=float(data.get("epsilon", 0.2)),
        min_epsilon=float(data.get("min_epsilon", 0.05)),
        epsilon_decay=float(data.get("epsilon_decay", 0.99)),
    )


def load_scenarios(config_path: str | Path) -> dict[str, ScenarioConfig]:
    path = Path(config_path)
    with path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    defaults = raw.get("defaults", {})
    raw_scenarios = raw.get("scenarios")
    if raw_scenarios is None:
        raw_scenarios = {k: v for k, v in raw.items() if k != "defaults"}

    scenarios: dict[str, ScenarioConfig] = {}
    for name, scenario_data in raw_scenarios.items():
        merged = _merge_dict(defaults, scenario_data or {})
        models = merged.get("models", {})
        if not models:
            raise ValueError(f"Scenario '{name}' has no model configuration")

        model_configs: dict[str, ModelConfig] = {}
        for model_name in MODEL_NAMES:
            if model_name not in models:
                raise ValueError(f"Scenario '{name}' missing configuration for {model_name}")
            model_configs[model_name] = _parse_model_config(models[model_name])

        target = merged.get("target", {})
        scenarios[name] = ScenarioConfig(
            name=name,
            description=str(merged.get("description", "")),
            boundary_mode=str(merged["boundary_mode"]),
            bounds=_tuple4(merged["bounds"]),
            target_mode=str(target.get("mode", "random")),
            target_x_range=_tuple2(target["x_range"]),
            target_y_range=_tuple2(target["y_range"]),
            target_grid_step=int(target.get("grid_step", 40)),
            max_steps=int(merged["max_steps"]),
            model_configs=model_configs,
        )
    return scenarios


def choose_target(rng: random.Random, x_range: tuple[int, int], y_range: tuple[int, int]) -> tuple[int, int]:
    return (rng.randint(*x_range), rng.randint(*y_range))


def sample_target(scenario: ScenarioConfig, rng: random.Random) -> tuple[int, int]:
    if scenario.target_mode == "axis":
        step = max(1, scenario.target_grid_step)
        values = list(range(scenario.target_x_range[0], scenario.target_x_range[1] + 1, step))
        axis_value = rng.choice(values)
        if rng.random() < 0.5:
            return axis_value, 0
        return 0, axis_value

    return choose_target(rng, scenario.target_x_range, scenario.target_y_range)


def noise_to_radius(noise_level: float, bounds: tuple[float, float, float, float]) -> int:
    if noise_level <= 0:
        return 0
    if noise_level <= 1:
        xmin, xmax, ymin, ymax = bounds
        scale = min(abs(xmax - xmin), abs(ymax - ymin))
        return int(noise_level * scale)
    return int(noise_level)


def observe_target(
    target: tuple[float, float],
    noise_level: float,
    bounds: tuple[float, float, float, float],
    rng: random.Random,
) -> tuple[float, float]:
    radius = noise_to_radius(noise_level, bounds)
    if radius <= 0:
        return target
    return (
        target[0] + rng.randint(-radius, radius),
        target[1] + rng.randint(-radius, radius),
    )


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.dist(a, b)


def distance_to_target(agent: AgentLike, target: tuple[float, float]) -> float:
    return distance(agent.pos(), target)


def apply_bounds(
    agent: AgentLike,
    bounds: tuple[float, float, float, float],
    mode: str,
) -> bool:
    xmin, xmax, ymin, ymax = bounds
    x, y = agent.pos()

    if mode == "wrap":
        wrapped = False
        if x < xmin:
            x = xmax
            wrapped = True
        elif x > xmax:
            x = xmin
            wrapped = True
        if y < ymin:
            y = ymax
            wrapped = True
        elif y > ymax:
            y = ymin
            wrapped = True
        if wrapped:
            agent.goto(x, y)
        return False

    if mode == "bounce":
        collided = False
        heading = agent.heading()
        if x < xmin or x > xmax:
            heading = (180 - heading) % 360
            x = max(xmin, min(x, xmax))
            collided = True
        if y < ymin or y > ymax:
            heading = (-heading) % 360
            y = max(ymin, min(y, ymax))
            collided = True
        if collided:
            agent.goto(x, y)
            agent.setheading(heading)
        return collided

    raise ValueError(f"Unsupported boundary mode: {mode}")
