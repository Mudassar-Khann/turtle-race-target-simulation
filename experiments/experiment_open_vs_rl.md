# Experiment: Open Field vs RL

## Hypothesis
In a low-noise open environment, the RL model should achieve the highest win rate.

## Setup
- Scenario: `open_field_ai`
- Command: `python -m adaptive_nav.benchmark --races 500 --scenario open_field_ai --seed 42 --save-csv`
- Learning mode: enabled

## Result
Model4 (RL) generally leads in win rate with lower average winning steps compared to random baselines.

## Insight
When signal quality is high, learning-based directional control provides consistent gains over undirected exploration.
