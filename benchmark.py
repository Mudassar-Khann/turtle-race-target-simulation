import argparse
import math
import random
import statistics

from model_working import (
    AIState,
    DEFAULT_BOUNDS,
    DEFAULT_HIT_RADIUS,
    DEFAULT_STEP_SIZE,
    DEFAULT_TARGET_X_RANGE,
    DEFAULT_TARGET_Y_RANGE,
    choose_target,
    model1,
    model2,
    model3,
    model4_ai,
)


class SimTurtle:
    """Lightweight turtle-compatible agent for fast, non-UI benchmarking."""

    def __init__(self, start_pos):
        self._x, self._y = start_pos
        self._heading = 0.0

    def pos(self):
        return (self._x, self._y)

    def goto(self, x, y=None):
        if y is None:
            x, y = x
        self._x = float(x)
        self._y = float(y)

    def heading(self):
        return self._heading

    def setheading(self, angle):
        self._heading = float(angle) % 360

    def left(self, angle):
        self._heading = (self._heading + float(angle)) % 360

    def forward(self, distance):
        radians = math.radians(self._heading)
        self._x += float(distance) * math.cos(radians)
        self._y += float(distance) * math.sin(radians)

    def towards(self, target):
        tx, ty = target
        angle = math.degrees(math.atan2(ty - self._y, tx - self._x))
        return angle % 360


def run_single_race(rng, max_steps):
    target = choose_target(
        rng=rng,
        x_range=DEFAULT_TARGET_X_RANGE,
        y_range=DEFAULT_TARGET_Y_RANGE,
    )
    ai_state = AIState()
    participants = [
        ("model1", SimTurtle((0, 0)), model1),
        ("model2", SimTurtle((-250, 0)), model2),
        ("model3", SimTurtle((250, 0)), model3),
        ("model4", SimTurtle((0, -200)), model4_ai),
    ]

    for step in range(1, max_steps + 1):
        for name, turtle_agent, model_fn in participants:
            kwargs = {
                "step_size": DEFAULT_STEP_SIZE,
                "hit_radius": DEFAULT_HIT_RADIUS,
                "bounds": DEFAULT_BOUNDS,
                "boundary_mode": "wrap",
                "rng": rng,
            }
            if model_fn is model3:
                kwargs["jitter_degrees"] = 60
            if model_fn is model4_ai:
                kwargs["ai_state"] = ai_state

            if model_fn(turtle_agent, target, **kwargs):
                return name, step

    return None, max_steps


def run_benchmark(races, max_steps, seed):
    rng = random.Random(seed)
    wins = {"model1": 0, "model2": 0, "model3": 0, "model4": 0}
    winning_steps = {"model1": [], "model2": [], "model3": [], "model4": []}
    unfinished = 0

    for _ in range(races):
        winner, steps = run_single_race(rng=rng, max_steps=max_steps)
        if winner is None:
            unfinished += 1
            continue
        wins[winner] += 1
        winning_steps[winner].append(steps)

    print(f"Races: {races} | Seed: {seed} | Max steps per race: {max_steps}")
    for name in ("model1", "model2", "model3", "model4"):
        rate = (wins[name] / races) * 100
        avg_steps = (
            f"{statistics.mean(winning_steps[name]):.1f}"
            if winning_steps[name]
            else "n/a"
        )
        print(f"{name:7} wins={wins[name]:4} ({rate:6.2f}%) avg_win_steps={avg_steps}")

    unfinished_rate = (unfinished / races) * 100
    print(f"unfinished races={unfinished} ({unfinished_rate:.2f}%)")


def parse_args():
    parser = argparse.ArgumentParser(description="Benchmark turtle race models.")
    parser.add_argument("--races", type=int, default=300, help="Number of races to run.")
    parser.add_argument(
        "--max-steps",
        type=int,
        default=10_000,
        help="Step limit per race before counting as unfinished.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_benchmark(races=args.races, max_steps=args.max_steps, seed=args.seed)
