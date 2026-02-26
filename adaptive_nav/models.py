from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Protocol

from adaptive_nav.environment import (
    apply_bounds,
    distance_to_target,
)
from adaptive_nav.rl import QLearningNavigator


class NavigatorLike(Protocol):
    def pos(self) -> tuple[float, float]:
        ...

    def heading(self) -> float:
        ...

    def setheading(self, angle: float) -> None:
        ...

    def left(self, angle: float) -> None:
        ...

    def forward(self, distance: float) -> None:
        ...

    def towards(self, target: tuple[float, float]) -> float:
        ...

    def goto(self, x: float, y: float | None = None) -> None:
        ...


@dataclass
class StepOutcome:
    hit: bool
    collided: bool
    before_distance: float
    after_distance: float


def _evaluate_step(
    agent: NavigatorLike,
    goal_target: tuple[float, float],
    bounds: tuple[float, float, float, float],
    boundary_mode: str,
    hit_radius: float,
    before_distance: float,
) -> StepOutcome:
    collided = apply_bounds(agent, bounds, boundary_mode)
    after_distance = distance_to_target(agent, goal_target)
    return StepOutcome(
        hit=after_distance <= hit_radius,
        collided=collided,
        before_distance=before_distance,
        after_distance=after_distance,
    )


def step_model1(
    agent: NavigatorLike,
    target: tuple[float, float],
    rng: random.Random,
    step_size: float,
    hit_radius: float,
    bounds: tuple[float, float, float, float],
    boundary_mode: str,
) -> StepOutcome:
    before_distance = distance_to_target(agent, target)
    agent.setheading(rng.choice((0, 90, 180, 270)))
    agent.forward(step_size)
    return _evaluate_step(agent, target, bounds, boundary_mode, hit_radius, before_distance)


def step_model2(
    agent: NavigatorLike,
    target: tuple[float, float],
    rng: random.Random,
    step_size: float,
    hit_radius: float,
    bounds: tuple[float, float, float, float],
    boundary_mode: str,
) -> StepOutcome:
    before_distance = distance_to_target(agent, target)
    agent.left(rng.randint(-180, 180))
    agent.forward(step_size)
    return _evaluate_step(agent, target, bounds, boundary_mode, hit_radius, before_distance)


def step_model3(
    agent: NavigatorLike,
    target: tuple[float, float],
    rng: random.Random,
    step_size: float,
    hit_radius: float,
    jitter_degrees: int,
    bounds: tuple[float, float, float, float],
    boundary_mode: str,
    goal_target: tuple[float, float] | None = None,
) -> StepOutcome:
    if goal_target is None:
        goal_target = target
    before_distance = distance_to_target(agent, goal_target)
    angle = agent.towards(target)
    agent.setheading(angle + rng.randint(-jitter_degrees, jitter_degrees))
    agent.forward(step_size)
    return _evaluate_step(agent, goal_target, bounds, boundary_mode, hit_radius, before_distance)


def step_model4(
    agent: NavigatorLike,
    target_true: tuple[float, float],
    target_observed: tuple[float, float],
    rng: random.Random,
    step_size: float,
    hit_radius: float,
    bounds: tuple[float, float, float, float],
    boundary_mode: str,
    rl_nav: QLearningNavigator,
) -> StepOutcome:
    state = rl_nav.discretize_state(agent, target_observed, bounds)
    action_idx, action_offset = rl_nav.select_action(state, rng)

    before_distance = distance_to_target(agent, target_true)
    base_angle = agent.towards(target_observed)
    agent.setheading(base_angle + action_offset)
    agent.forward(step_size)
    collided = apply_bounds(agent, bounds, boundary_mode)
    after_distance = distance_to_target(agent, target_true)
    hit = after_distance <= hit_radius

    reward = -1.0
    if collided:
        reward -= 5.0
    reward += 0.25 * (before_distance - after_distance)
    if hit:
        reward += 100.0

    next_state = rl_nav.discretize_state(agent, target_observed, bounds)
    rl_nav.update(state, action_idx, reward, next_state, done=hit)
    return StepOutcome(
        hit=hit,
        collided=collided,
        before_distance=before_distance,
        after_distance=after_distance,
    )
