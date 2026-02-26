from turtle import Screen, Turtle

from model_working import (
    AIState,
    DEFAULT_HIT_RADIUS,
    DEFAULT_STEP_SIZE,
    DEFAULT_TARGET_X_RANGE,
    DEFAULT_TARGET_Y_RANGE,
    create_turtle,
    mark,
    model1,
    model2,
    model3,
    model4_ai,
)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BOUNDARY_MODE = "wrap"
MODEL3_JITTER_DEGREES = 60
FRAME_DELAY_MS = 80
STEPS_PER_FRAME = 1
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
ai_state = AIState()

participants = [
    {
        "name": "model1-random-grid",
        "agent": create_turtle("turtle", "black", (0, 0)),
        "model": model1,
        "kwargs": {},
    },
    {
        "name": "model2-random-turn",
        "agent": create_turtle("arrow", "red", (-250, 0)),
        "model": model2,
        "kwargs": {},
    },
    {
        "name": "model3-greedy",
        "agent": create_turtle("circle", "green", (250, 0)),
        "model": model3,
        "kwargs": {"jitter_degrees": MODEL3_JITTER_DEGREES},
    },
    {
        "name": "model4-ai",
        "agent": create_turtle("square", "blue", (0, -200)),
        "model": model4_ai,
        "kwargs": {"ai_state": ai_state},
    },
]

running = True
winner_name = None
step_count = 0
finished = False

status_writer = Turtle(visible=False)
status_writer.penup()
status_writer.color("black")
status_writer.goto(-(SCREEN_WIDTH // 2) + 10, (SCREEN_HEIGHT // 2) - 30)

legend_writer = Turtle(visible=False)
legend_writer.penup()
legend_writer.color("black")
legend_writer.goto(-(SCREEN_WIDTH // 2) + 10, -(SCREEN_HEIGHT // 2) + 20)
legend_writer.write(
    "black:model1 random-grid | red:model2 random-turn | green:model3 greedy | blue:model4 AI (epsilon-greedy)",
    font=("Arial", 10, "normal"),
)

def stop_race():
    global running
    running = False


def draw_status(message=None):
    status_writer.clear()
    ai_info = (
        f"AI epsilon={ai_state.epsilon:.3f} best_offset={ai_state.best_action():+d}deg "
        f"last_action={ai_state.last_action:+d}deg"
    )
    lines = [f"Step: {step_count}", ai_info, "Esc: stop race"]
    if message:
        lines.append(message)
    status_writer.write("\n".join(lines), font=("Arial", 11, "normal"))


def finish_race():
    global finished
    if finished:
        return

    finished = True
    if winner_name is not None:
        message = f"Winner: {winner_name} in {step_count} steps."
    elif not running:
        message = f"Race stopped after {step_count} steps."
    else:
        message = f"No winner after {MAX_STEPS} steps."

    draw_status(message)
    print(message)
    screen.title(f"Turtle Race to the Target | {message}")
    screen.update()


def step_race():
    global step_count, winner_name

    if finished:
        return

    if not running or winner_name is not None or step_count >= MAX_STEPS:
        finish_race()
        return

    for _ in range(STEPS_PER_FRAME):
        if not running or winner_name is not None or step_count >= MAX_STEPS:
            break
        step_count += 1

        for participant in participants:
            kwargs = {
                "step_size": DEFAULT_STEP_SIZE,
                "hit_radius": DEFAULT_HIT_RADIUS,
                "bounds": BOUNDS,
                "boundary_mode": BOUNDARY_MODE,
            }
            kwargs.update(participant["kwargs"])
            if participant["model"](participant["agent"], target, **kwargs):
                winner_name = participant["name"]
                break

    draw_status()
    screen.update()
    screen.ontimer(step_race, FRAME_DELAY_MS)


screen.listen()
screen.onkey(stop_race, "Escape")
draw_status()
screen.ontimer(step_race, FRAME_DELAY_MS)
screen.mainloop()
