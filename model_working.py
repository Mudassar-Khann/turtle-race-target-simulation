import math
import random
from turtle import Turtle

DEFAULT_STEP_SIZE = 10
DEFAULT_HIT_RADIUS = 10
DEFAULT_TARGET_X_RANGE = (-300, 300)
DEFAULT_TARGET_Y_RANGE = (-220, 220)
DEFAULT_BOUNDS = (-390, 390, -290, 290)


class AIState:
    """Simple reinforcement-style controller state for model4_ai."""

    def __init__(
        self,
        action_offsets=(-90, -45, 0, 45, 90),
        alpha=0.25,
        epsilon=0.35,
        epsilon_decay=0.995,
        min_epsilon=0.05,
    ):
        if not action_offsets:
            raise ValueError("action_offsets must not be empty")
        self.action_offsets = tuple(action_offsets)
        self.alpha = alpha
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        self.q_values = {offset: 0.0 for offset in self.action_offsets}
        self.last_action = 0

    def choose_action(self, rng):
        if rng.random() < self.epsilon:
            action = rng.choice(self.action_offsets)
        else:
            best_q = max(self.q_values.values())
            best_actions = [
                action for action, q_value in self.q_values.items() if q_value == best_q
            ]
            action = rng.choice(best_actions)

        self.last_action = action
        return action

    def update(self, action, reward):
        old_q = self.q_values[action]
        self.q_values[action] = old_q + self.alpha * (reward - old_q)
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

    def best_action(self):
        return max(self.q_values, key=self.q_values.get)


def _resolve_rng(rng=None):
    return rng if rng is not None else random


def choose_target(
    rng=None,
    x_range=DEFAULT_TARGET_X_RANGE,
    y_range=DEFAULT_TARGET_Y_RANGE,
):
    """Return random target coordinates."""
    rnd = _resolve_rng(rng)
    return (rnd.randint(*x_range), rnd.randint(*y_range))


def mark(rng=None, x_range=DEFAULT_TARGET_X_RANGE, y_range=DEFAULT_TARGET_Y_RANGE):
    """Create a random target dot and return its coordinates."""
    marker = Turtle()
    marker.hideturtle()
    marker.penup()
    target = choose_target(rng=rng, x_range=x_range, y_range=y_range)
    marker.goto(target)
    marker.dot(15, "red")
    return target


def create_turtle(shape, color, start_pos):
    """Factory for clean turtle creation."""
    t = Turtle(shape=shape)
    t.pensize(3)
    t.pencolor(color)
    t.speed(0)
    t.penup()
    t.goto(start_pos)
    t.pendown()
    return t


def _distance_to_target(agent, target):
    return math.dist(target, agent.pos())


def _apply_bounds(agent, bounds, mode):
    if bounds is None:
        return

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
        return

    if mode == "bounce":
        heading = agent.heading()
        bounced = False

        if x < xmin or x > xmax:
            heading = (180 - heading) % 360
            x = max(xmin, min(x, xmax))
            bounced = True

        if y < ymin or y > ymax:
            heading = (-heading) % 360
            y = max(ymin, min(y, ymax))
            bounced = True

        if bounced:
            agent.goto(x, y)
            agent.setheading(heading)
        return

    raise ValueError(f"Unsupported boundary mode: {mode}")


def model1(
    t,
    target,
    step_size=DEFAULT_STEP_SIZE,
    hit_radius=DEFAULT_HIT_RADIUS,
    bounds=DEFAULT_BOUNDS,
    boundary_mode="wrap",
    rng=None,
):
    """Random walk in 4 cardinal directions."""
    rnd = _resolve_rng(rng)
    t.setheading(rnd.choice((0, 90, 180, 270)))
    t.forward(step_size)
    _apply_bounds(t, bounds, boundary_mode)
    return _distance_to_target(t, target) <= hit_radius


def model2(
    t,
    target,
    step_size=DEFAULT_STEP_SIZE,
    hit_radius=DEFAULT_HIT_RADIUS,
    bounds=DEFAULT_BOUNDS,
    boundary_mode="wrap",
    rng=None,
):
    """Chaotic walk with random rotation each step."""
    rnd = _resolve_rng(rng)
    t.left(rnd.randint(-180, 180))
    t.forward(step_size)
    _apply_bounds(t, bounds, boundary_mode)
    return _distance_to_target(t, target) <= hit_radius


def model3(
    t,
    target,
    step_size=DEFAULT_STEP_SIZE,
    hit_radius=DEFAULT_HIT_RADIUS,
    jitter_degrees=60,
    bounds=DEFAULT_BOUNDS,
    boundary_mode="wrap",
    rng=None,
):
    """Greedy walk toward target with symmetric random jitter."""
    if jitter_degrees < 0:
        raise ValueError("jitter_degrees must be >= 0")

    rnd = _resolve_rng(rng)
    angle = t.towards(target)
    t.setheading(angle + rnd.randint(-jitter_degrees, jitter_degrees))
    t.forward(step_size)
    _apply_bounds(t, bounds, boundary_mode)
    return _distance_to_target(t, target) <= hit_radius


def model4_ai(
    t,
    target,
    ai_state,
    step_size=DEFAULT_STEP_SIZE,
    hit_radius=DEFAULT_HIT_RADIUS,
    bounds=DEFAULT_BOUNDS,
    boundary_mode="wrap",
    rng=None,
):
    """
    Reinforcement-style policy:
    choose a heading offset using epsilon-greedy action values,
    then update action value from immediate distance-improvement reward.
    """
    rnd = _resolve_rng(rng)
    before = _distance_to_target(t, target)

    action_offset = ai_state.choose_action(rnd)
    base_angle = t.towards(target)
    t.setheading(base_angle + action_offset)
    t.forward(step_size)
    _apply_bounds(t, bounds, boundary_mode)

    after = _distance_to_target(t, target)
    reward = before - after
    ai_state.update(action_offset, reward)

    return after <= hit_radius
