# Turtle Race Target Simulation

## Overview
This project is a Python-based graphical simulation built using the Turtle
module. Multiple agents (turtles) attempt to reach a randomly placed target
on a two-dimensional plane. Each agent follows a different movement model,
allowing comparison between deterministic, stochastic, and heuristic-based
search behaviors.

The simulation runs until any one agent reaches the target.

## Conceptual Motivation
The project is inspired by classical ideas from probability theory, search
algorithms, and random processes. In particular, it explores the difference
between directed behavior and randomness, including the well-known intuition
that while a “lost bird” moving randomly may never find its home, a “drunk
person” performing a random walk will eventually reach any location given
enough time.

Each movement model reflects a different interpretation of these ideas.

## Movement Models and Theory

The first model represents a purely random walk constrained to fixed directions.
At each step, the agent randomly chooses one of the four cardinal directions.
This resembles a naive search strategy with no memory or awareness of the
target. While movement is unbiased, progress toward the target is slow and
unreliable.

The second model represents an unrestricted random walk, where the agent turns
by a random angle at each step. This aligns with the classical “drunkard’s walk”
model studied in probability theory. Although the movement appears chaotic and
unintelligent, such random motion has a surprising theoretical property: in a
bounded two-dimensional space, it will eventually reach any reachable point
with probability one.

The third model introduces heuristic behavior. Instead of moving blindly, the
agent continuously biases its direction toward the target while still retaining
some randomness. This simulates a simple greedy strategy, similar to how search
algorithms use heuristics to guide exploration. The result is faster convergence
at the cost of reduced randomness.

## Behavior Tuning
The behavior of each model can be adjusted by modifying internal parameters such
as step size, turning angle range, and randomness strength. Changing these values
directly impacts convergence speed, stability, and exploration patterns, making
the simulation useful for experimentation and comparison.

## File Structure
The main execution loop, screen setup, and simulation control logic are defined
in main.py.  
All movement models, turtle creation utilities, and target generation logic are
implemented in model_working.py.

## How to Run
Ensure Python is installed on your system, then run:

python main.py

A graphical window will open and the simulation will start automatically.

## Concepts Demonstrated
This project demonstrates random walk theory, heuristic-guided movement,
agent-based simulation, modular program design, and event-driven graphical
programming in Python.

## Author
Mudassar Khan
