from __future__ import annotations

import math
import pickle
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class RLNavigatorLike(Protocol):
    def pos(self) -> tuple[float, float]:
        ...

    def heading(self) -> float:
        ...

    def setheading(self, angle: float) -> None:
        ...

    def forward(self, distance: float) -> None:
        ...

    def towards(self, target: tuple[float, float]) -> float:
        ...


State = tuple[int, int]


@dataclass
class QLearningConfig:
    action_offsets: tuple[int, ...] = (-30, -15, 0, 15, 30)
    alpha: float = 0.2
    gamma: float = 0.95
    epsilon: float = 0.2
    min_epsilon: float = 0.05
    epsilon_decay: float = 0.99
    learning_enabled: bool = True


class QLearningNavigator:
    def __init__(self, config: QLearningConfig):
        if not config.action_offsets:
            raise ValueError("action_offsets cannot be empty")
        self.config = config
        self.q_table: dict[State, list[float]] = {}

    @property
    def epsilon(self) -> float:
        return self.config.epsilon

    def set_learning_mode(self, enabled: bool) -> None:
        self.config.learning_enabled = enabled

    def _ensure_state(self, state: State) -> None:
        if state not in self.q_table:
            self.q_table[state] = [0.0 for _ in self.config.action_offsets]

    def discretize_state(
        self,
        agent: RLNavigatorLike,
        target: tuple[float, float],
        bounds: tuple[float, float, float, float],
    ) -> State:
        angle_to_target = agent.towards(target)
        relative_angle = ((angle_to_target - agent.heading() + 180) % 360) - 180
        angle_bucket = int((relative_angle + 180) // 45) % 8

        x_min, x_max, y_min, y_max = bounds
        max_distance = math.dist((x_min, y_min), (x_max, y_max))
        distance = math.dist(agent.pos(), target)
        normalized_distance = distance / max_distance if max_distance > 0 else 0.0
        distance_bucket = min(4, int(normalized_distance * 5))
        return angle_bucket, distance_bucket

    def select_action(self, state: State, rng: random.Random) -> tuple[int, int]:
        self._ensure_state(state)
        if self.config.learning_enabled and rng.random() < self.config.epsilon:
            action_idx = rng.randrange(len(self.config.action_offsets))
            return action_idx, self.config.action_offsets[action_idx]

        values = self.q_table[state]
        best_value = max(values)
        best_indexes = [idx for idx, value in enumerate(values) if value == best_value]
        action_idx = rng.choice(best_indexes)
        return action_idx, self.config.action_offsets[action_idx]

    def update(
        self,
        state: State,
        action_idx: int,
        reward: float,
        next_state: State,
        done: bool,
    ) -> None:
        if not self.config.learning_enabled:
            return

        self._ensure_state(state)
        self._ensure_state(next_state)
        old_q = self.q_table[state][action_idx]
        next_max = 0.0 if done else max(self.q_table[next_state])
        target = reward + self.config.gamma * next_max
        self.q_table[state][action_idx] = old_q + self.config.alpha * (target - old_q)
        self.config.epsilon = max(
            self.config.min_epsilon,
            self.config.epsilon * self.config.epsilon_decay,
        )

    def save_q_table(self, path: str | Path) -> None:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("wb") as handle:
            pickle.dump(self.q_table, handle)

    def load_q_table(self, path: str | Path) -> bool:
        file_path = Path(path)
        if not file_path.exists():
            return False
        with file_path.open("rb") as handle:
            self.q_table = pickle.load(handle)
        return True
