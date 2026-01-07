import random, math
from turtle import Turtle

def mark():
    """Create a random target dot and return its coordinates."""
    marker = Turtle()
    marker.hideturtle()
    marker.penup()
    x, y = random.randint(-200, 200), random.randint(-200, 200)
    marker.goto(x, y)
    marker.dot(15, "red")   # target
    return (x, y)

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

# --- Different movement models ---
def model1(t, target):
    """Random walk in 4 directions."""
    t.setheading(random.choice([0, 90, 180, 270]))
    t.forward(10)
    return math.dist(target, t.pos()) <= 10

def model2(t, target):
    """Chaotic: random turn in any direction."""
    t.left(random.randint(-180, 180))
    t.forward(10)
    return math.dist(target, t.pos()) <= 10

def model3(t, target):
    """Greedy: tries to move toward target with some randomness."""
    angle = t.towards(target)
    t.setheading(angle + random.randint(-100, 190))  #
    t.forward(10)
    return math.dist(target, t.pos()) <= 10

# Test run only if this file is executed directly
if __name__ == "__main__":
    from turtle import Screen
    screen = Screen()
    target = mark()
    t = create_turtle("turtle", "blue", (-250, 0))
    while not model3(t, target):
        pass
    screen.mainloop()
