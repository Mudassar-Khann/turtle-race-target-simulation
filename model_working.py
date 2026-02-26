import math
import random
from turtle import Turtle

DEFAULT_STEP_SIZE = 10
DEFAULT_HIT_RADIUS = 10
DEFAULT_TARGET_X_RANGE = (-300, 300)
DEFAULT_TARGET_Y_RANGE = (-220, 220)
DEFAULT_BOUNDS = (-390, 390, -290, 290)


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
