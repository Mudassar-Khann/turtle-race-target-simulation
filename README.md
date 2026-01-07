# Turtle Race Target Simulation

## Overview
This project is a Python-based graphical simulation developed using the Turtle
module. The program simulates multiple agents competing to reach a randomly
generated target on the screen. Each agent follows a different movement strategy,
resulting in varied behavior during the race.

The simulation continues until one of the agents successfully reaches the
target location.

## Simulation Logic
Each turtle represents an independent agent controlled by a movement model.
The models define how an agent turns, moves, and reacts relative to the target.
Although all agents share the same environment, their decision logic differs,
which leads to noticeably different movement patterns and outcomes.

The behavior of each model can be modified by changing internal parameters such
as turning angles, randomness ranges, and step size. Adjusting these values
directly affects how aggressively, randomly, or accurately a turtle moves
toward the target.

## File Structure
The main program logic, screen setup, and execution loop are handled in
main.py.  
All movement models, turtle creation logic, and target generation are defined
in model_working.py.

## How to Run
Ensure that Python is installed on your system.  
Run the simulation using the following command:

python main.py

A graphical window will open automatically and start the simulation.

## Customization
Movement behavior can be changed by modifying the numerical values used inside
the model functions. For example, changing the angle variation or movement
distance will result in more controlled or more chaotic motion. This allows
experimentation with different strategies without altering the overall program
structure.

## Concepts Demonstrated
This project demonstrates agent-based simulation, modular program design, basic
heuristic behavior, randomized movement strategies, and graphical programming
using event-driven logic.

## Author
Mudassar khan
