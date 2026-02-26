from turtle import Screen

from model_working import (
    DEFAULT_HIT_RADIUS,
    DEFAULT_STEP_SIZE,
    DEFAULT_TARGET_X_RANGE,
    DEFAULT_TARGET_Y_RANGE,
    create_turtle,
    mark,
    model1,
    model2,
    model3,
)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BOUNDARY_MODE = "wrap"
MODEL3_JITTER_DEGREES = 60
MAX_STEPS = 10_000
BOUNDS = (
    -(SCREEN_WIDTH // 2) + 5,
    (SCREEN_WIDTH // 2) - 5,
    -(SCREEN_HEIGHT // 2) + 5,
    (SCREEN_HEIGHT // 2) - 5,
)


screen = Screen()
screen.title("Turtle Race to the Target")
screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
screen.tracer(0)

target = mark(x_range=DEFAULT_TARGET_X_RANGE, y_range=DEFAULT_TARGET_Y_RANGE)

participants = [
    ("model1", create_turtle("turtle", "black", (0, 0)), model1),
    ("model2", create_turtle("arrow", "red", (-250, 0)), model2),
    ("model3", create_turtle("circle", "green", (250, 0)), model3),
]

running = True
winner_name = None
step_count = 0


def stop_race():
    global running
    running = False


screen.listen()
screen.onkey(stop_race, "Escape")

while running and winner_name is None and step_count < MAX_STEPS:
    step_count += 1
    for name, turtle_agent, model_fn in participants:
        kwargs = {
            "step_size": DEFAULT_STEP_SIZE,
            "hit_radius": DEFAULT_HIT_RADIUS,
            "bounds": BOUNDS,
            "boundary_mode": BOUNDARY_MODE,
        }
        if model_fn is model3:
            kwargs["jitter_degrees"] = MODEL3_JITTER_DEGREES

        if model_fn(turtle_agent, target, **kwargs):
            winner_name = name
            break

    screen.update()

if winner_name is not None:
    message = f"Winner: {winner_name} in {step_count} steps."
elif not running:
    message = f"Race stopped after {step_count} steps."
else:
    message = f"No winner after {MAX_STEPS} steps."

print(message)
screen.title(f"Turtle Race to the Target | {message}")
screen.mainloop()
