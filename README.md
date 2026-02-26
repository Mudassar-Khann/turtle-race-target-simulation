# Turtle Race Target Simulation

## Overview
This project is a Python simulation using the built-in `turtle` module.
Three agents race to reach a randomly placed target. Each agent uses a
different movement strategy so you can compare random and heuristic behavior.

## Movement Models
1. `model1`: random walk over cardinal directions (`0, 90, 180, 270`).
2. `model2`: random turn each step, then forward movement.
3. `model3`: target-seeking heading with symmetric random jitter.

## Recent Improvements
1. Added configurable constants for step size, hit radius, target range, and bounds.
2. Added boundary handling (`wrap` and `bounce` support).
3. Fixed heuristic bias by using symmetric randomness in `model3`.
4. Removed dead/unused control code in `main.py`.
5. Added race stop via keyboard (`Esc`).
6. Added benchmark mode (`benchmark.py`) for multi-race statistics.

## Project Files
1. `main.py`: visual turtle simulation.
2. `model_working.py`: target creation, turtle factory, and movement models.
3. `benchmark.py`: non-UI simulation for win-rate and average-step comparison.

## Run the Visual Simulation
```bash
python main.py
```

The race window opens immediately.
Press `Esc` to stop the race manually.

## Run the Benchmark
```bash
python benchmark.py
```

Optional arguments:
```bash
python benchmark.py --races 500 --max-steps 10000 --seed 42
```

Benchmark output includes:
1. Wins per model.
2. Win rate percentage.
3. Average steps for winning races.
4. Unfinished race count and percentage.

## Tuning
Adjust constants in `model_working.py`:
1. `DEFAULT_STEP_SIZE`
2. `DEFAULT_HIT_RADIUS`
3. `DEFAULT_TARGET_X_RANGE`, `DEFAULT_TARGET_Y_RANGE`
4. `DEFAULT_BOUNDS`

Adjust visual-run settings in `main.py`:
1. `BOUNDARY_MODE` (`wrap` or `bounce`)
2. `MODEL3_JITTER_DEGREES`
3. `MAX_STEPS`

## Author
Mudassar Khan
