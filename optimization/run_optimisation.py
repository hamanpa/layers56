import multiprocessing as mp
from bluepyopt.deapext.optimisationsCMA import DEAPOptimisationCMA
from evaluator import define_evaluator
import json
import os

offspring_size = 12                 # Size of the population used by the optimizer
timeout = 72000                      # Hard cut-off for the evaluation of an individual (in seconds)
optimiser_seed = 7                  # random seed for the optimiser
optimiser_sigma = 0.3               # width of the search at the first generation of the optimisation, default: 0.4
max_ngen = 200                      # Maximum number of generation of the optimiser

# model = 'LSV1M_split_full'
model = 'LSV1M_split_ee'



os.chdir(f'/home/haman/layers56/{model}/')

run_script = 'run_optimization_experiment.py'
parameters_url = 'param_optim/defaults'
config_optimisation = './param_optim/config_optimisation'

# NOTE: centroid has to have the values in the same order as the parameters in the config_optimisation file!
with open(config_optimisation) as f:
    opt_config = json.load(f)

with open(config_optimisation) as f:
    opt_config = json.load(f)
optimiser_centroid = []
for key in opt_config["parameters"].keys():
    if key in opt_config["optimiser_centroid"]:
        optimiser_centroid.append(opt_config["optimiser_centroid"][key])
    else:
        raise KeyError(f"Key {key} not found in optimiser_centroid in config_optimisation file {config_optimisation}")

evaluator = define_evaluator(
    run_script=run_script,
    parameters_url=parameters_url,
    timeout = timeout,
    config_optimisation=config_optimisation,
)



continue_cp = False                 # Should the optimisation resume from the informed checkpoint file
if not continue_cp:
    cp_filename = f"./{evaluator.optimization_id}/opt_check.pkl"       # Path to the checkpoint file of the optimisation
else:
    # raise Exception("Please inform the path to the last chckpointfile here !")
    # cp_filename = None # <------
    cp_filename = './20250328-192103_Optimization/opt_check.pkl'

map_function = mp.Pool(processes=offspring_size).map

# NOTE: this was just an attempt to test the evaluator whether it will crash or not
# import glob
# from evaluator import get_data_store
# map_function = mp.Pool(processes=2).map
# data_stores = list(map(get_data_store, glob.glob("./20250113-102906_Optimization/SelfSustainedPushPull_Opt*")))
# map_function(evaluator.evaluate_data_store, data_stores)

optimizer = DEAPOptimisationCMA(
    evaluator=evaluator,
    use_scoop=False,
    seed=optimiser_seed,
    offspring_size=offspring_size,
    map_function=map_function,
    selector_name="single_objective",
    use_stagnation_criterion=False,
    sigma=optimiser_sigma,
    centroids=[optimiser_centroid]
)

optimizer.run(
    max_ngen=max_ngen,
    cp_filename=cp_filename,
    cp_frequency=1,
    continue_cp=continue_cp,
)
