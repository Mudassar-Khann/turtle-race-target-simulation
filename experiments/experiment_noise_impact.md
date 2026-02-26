# Experiment: Noise Impact on Navigation

## Hypothesis
As sensor noise increases, target-dependent strategies degrade and exploration-heavy strategies become more competitive.

## Setup
- Scenario: `exploration_chaos`
- Command: `python -m adaptive_nav.benchmark --races 500 --scenario exploration_chaos --seed 42 --save-csv`
- Learning mode: enabled

## Result
Model2 (continuous random exploration) improves relative rank; heuristic and RL policies lose precision under noisy perception.

## Insight
Environment uncertainty can invert model rankings. This supports the research claim that performance is environment-dependent.
