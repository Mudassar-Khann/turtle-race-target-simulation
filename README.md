# Adaptive Navigation Strategy Benchmark

## Research Question
How do navigation strategies perform under varying environmental constraints?

## Models Compared
1. Random Cardinal (`model1`)
2. Continuous Random (`model2`)
3. Greedy Heuristic (`model3`)
4. Epsilon-Greedy RL with Q-Learning (`model4`)

## Experiment Design
1. Multiple environments are defined in `configs/scenarios.yaml`.
2. Sensor noise is injected through noisy target observation.
3. Boundary physics (`wrap` or `bounce`) are scenario-controlled.
4. Reproducible seeds are used across benchmark and visualization.
5. Benchmark supports learning and evaluation-only modes.

## Key Findings
1. Performance is environment dependent.
2. RL dominates in open, low-noise environments.
3. Greedy heuristic excels in moderate-signal constrained lanes.
4. Random cardinal can dominate axis-aligned grid worlds.
5. Continuous random exploration wins highly chaotic noisy maps.

## Repository Structure
```text
adaptive_nav/
+-- adaptive_nav/
¦   +-- __init__.py
¦   +-- models.py
¦   +-- environment.py
¦   +-- simulator.py
¦   +-- benchmark.py
¦   +-- visual.py
¦   +-- logging_utils.py
¦   +-- rl.py
+-- configs/
¦   +-- scenarios.yaml
+-- data/
+-- experiments/
¦   +-- plot_results.py
¦   +-- experiment_open_vs_rl.md
¦   +-- experiment_noise_impact.md
¦   +-- media/
¦   +-- plots/
+-- README.md
+-- requirements.txt
+-- setup.py
```

## Reproducibility
1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Run benchmark with fixed seed:
```bash
python -m adaptive_nav.benchmark --races 1000 --scenario mixed --seed 42 --save-csv
```
3. Generate plots:
```bash
python experiments/plot_results.py --csv data/results.csv
```

## Benchmark CLI
Supported options:
- `--races`
- `--seed`
- `--scenario`
- `--save-csv`
- `--no-learning`
- `--epsilon`
- `--alpha`
- `--gamma`
- `--config`

## Visual Simulation
```bash
python -m adaptive_nav.visual --scenario mixed --rounds 8 --seed 42
```

Press `Esc` to stop the tournament.

## Experiment Notes
1. `experiments/experiment_open_vs_rl.md`
2. `experiments/experiment_noise_impact.md`

## Author
Mudassar Khan
