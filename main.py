from turtle import Screen, Turtle
from model_working import mark, create_turtle, model1, model2, model3

# Setup screen
screen = Screen()
screen.title("Turtle Race to the Target")
screen.setup(width=800, height=600)
screen.tracer(1)

# Create target
target = mark()

# Create turtles with different models
t1 = create_turtle("turtle", "black", (0, 0))
t2 = create_turtle("arrow", "red", (-250, 0))
t3 = create_turtle("circle", "green", (250, 0))
def stop(x=None,y=None):
    global reached
    reached = True



# Race loop
reached = False

try:
    while not reached:

        r1 = model1(t1, target)
        r2 = model2(t2, target)
        r3 = model3(t3, target)
        if r1 or r2 or r3:
            reached = True

except Exception as e:
    print("program closed ")

screen.mainloop()
