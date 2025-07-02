# Run optimizations


run optimization
`sbatch optimisation.sbatch`

run optimization setup for specific set of params
- this will run optimization setup (`run_experiment.py`) for the best params found so far (set up optimization in `run_parameter_search.py`)
`python run_parameter_search.py run_experiment.py nest param-split/defaults`

run full experiment protocol
- TODO: use paper-like recorders





