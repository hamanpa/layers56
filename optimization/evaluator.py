import os
import time
from datetime import datetime
import subprocess
import shutil
import psutil
import json
import sys

from parameters import ParameterSet
from mozaik.storage.datastore import PickledDataStore
from mozaik.meta_workflow.parameter_search import ParameterSearch

from targets import *


def get_data_store(path):

    parameters = ParameterSet(
            {'root_directory': path,
             'store_stimuli': False}
    )

    try:
        data_store = PickledDataStore(
                load=True,
                parameters=parameters,
                replace=True
            )
    except:
        print(f"[{time.strftime('%D-%H:%M:%S')}] Error while loading datastore at {path}.")
        return None

    return data_store


class FitnessCalculator():

    def __init__(self, objectives):
        self.objectives = objectives

    def calculate_scores(self, data_store):
        return {t.name: t.calculate_score(data_store) for t in self.objectives}

    def calculate_values(self, data_store):
        return {t.name: t.calculate_value(data_store) for t in self.objectives}


class SlurmSequentialBackend():

    def __init__(self, num_threads, num_mpi, path_to_mozaik_env, slurm_options=None):
        self.num_threads = num_threads
        self.num_mpi = num_mpi
        self.path_to_mozaik_env = path_to_mozaik_env
        if slurm_options == None:
           self.slurm_options = []
        else:
           self.slurm_options = slurm_options 

    def execute_job(self, run_script, simulator_name, parameters_url, parameters, simulation_run_name):

        modified_parameters = []
        for k in parameters.keys():
            modified_parameters.append(k)
            modified_parameters.append(str(parameters[k]))

        from subprocess import Popen, PIPE
        sbatch_cmd = ['sbatch'] + self.slurm_options + ['-o', parameters['results_dir'][2:-2] + "/slurm-%j.out"]
        p = Popen(
            sbatch_cmd,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            text=True
        )

        data = '\n'.join([
            '#!/bin/bash',
            '#SBATCH -n ' + str(self.num_mpi),
            '#SBATCH -c ' + str(self.num_threads),
            'source ' + str(self.path_to_mozaik_env),
            'cd ' + os.getcwd(),
            ' '.join(
                ["srun --mpi=pmix_v5 python", run_script, simulator_name, str(self.num_threads), parameters_url] + \
                modified_parameters + [simulation_run_name] + ['>'] + [parameters['results_dir'][1:-1] + '/OUTFILE' + str(time.time())]
            ),
        ])

        slurm_com = p.communicate(input=data)[0]
        p.stdin.close()

        return slurm_com


class Parameter():

    def __init__(self, name, lower_bound, upper_bound):
        self.name = name
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.bounds = [lower_bound, upper_bound]


class Evaluator(ParameterSearch):

    def __init__(self, fitness_calculator, params, run_script, simulator_name, parameters_url, backend, pynn_seed=0, timeout=3600):
        self.fitness_calculator = fitness_calculator
        self.objectives = self.fitness_calculator.objectives
        self.params = params
        self.param_names = [p.name for p in self.params]
        self.timeout = timeout
        self.run_script = run_script
        self.simulator_name = simulator_name
        self.parameters_url = parameters_url
        self.backend = backend
        self.pynn_seed = pynn_seed
        self.optimization_id = str(datetime.now().strftime('%Y%m%d-%H%M%S') + "_Optimization")
        os.mkdir(self.optimization_id)

    def check_evaluation_finished(self, slurm_id):
        try:
            slurm_status = str(subprocess.run(['squeue', '-j', slurm_id], stdout=subprocess.PIPE, timeout=20).stdout.decode('utf-8'))
        except subprocess.TimeoutExpired:
            print(f"[{time.strftime('%D-%H:%M:%S')}] The squeue command timed out for slurm job {slurm_id}.")
            return False
        if slurm_id in slurm_status:
            return False
        return True

        # Alternative way to check if job is finished
        # Maybe try it if the optimizer waits for the job to finish indefinitely
        try:
            slurm_status = str(subprocess.run(['sacct', '-j', slurm_id, '--format=State', '--noheader'],
                                              stdout=subprocess.PIPE, timeout=20).stdout.decode('utf-8'))
            # NOTE; slurm actually create multiple jobs with the same ID
            # for sbatch it will create subjobs batch and python
            # I want to check that status of all the subjobs is COMPLETED
            slurm_status = set(map(str.strip, a.split("\n")))
        except subprocess.TimeoutExpired:
            print(f"[{time.strftime('%D-%H:%M:%S')}] The sacct command timed out for slurm job {slurm_id}.")
            return False
        return slurm_status == {'COMPLETED'}

    def evaluate_data_store(self, data_store):
        return self.fitness_calculator.calculate_scores(data_store)

    def evaluate_parameters(self, parameters):

        process = psutil.Process()
        
        pid = os.getpid()

        # Create parameter set
        _params = {'pynn_seed': self.pynn_seed}
        _params.update(parameters)
        print(f"[{time.strftime('%D-%H:%M:%S')}] On pid {pid}. Launching job for parameters: ", _params)

        # Run the model
        _params['results_dir'] = '\"\'' + os.getcwd() + '/' + self.optimization_id + '/\'\"'
        slurm_com = self.backend.execute_job(self.run_script, self.simulator_name, self.parameters_url, _params, f'Opt_{pid}')
        slurm_id = slurm_com.replace("Submitted batch job ", "").rstrip()

        # Wait for run to finish
        print(f"[{time.strftime('%D-%H:%M:%S')}] On pid {pid}. Waiting for slurm job {slurm_id} to finish ...")
        t1 = time.time()
        while not self.check_evaluation_finished(slurm_id):
            time.sleep(20)
            if (time.time() - t1) > self.timeout:
                print(f"[{time.strftime('%D-%H:%M:%S')}] On pid {pid}. Slurm job timed out.")
                return {obj.name : obj.max_score for obj in self.objectives}
        print(f"[{time.strftime('%D-%H:%M:%S')}] On pid {pid}. Slurm job finished.")

        # Load data store
        for subf in glob.glob(f"./{self.optimization_id}/SelfSustainedPushPull_Opt_{pid}*"):
            data_store = get_data_store(subf)
            break

        print(f"[{time.strftime('%D-%H:%M:%S')}] On pid {pid}. Computing scores ...")
        score = self.evaluate_data_store(data_store)
        print(f"[{time.strftime('%D-%H:%M:%S')}] On pid {pid}. Done computing scores.")

        shutil.rmtree(subf) 

        print(f"[{time.strftime('%D-%H:%M:%S')}] On pid {pid}. Scores = {score}")
        return score

    def init_simulator_and_evaluate_with_lists(self, param_list=None, target='scores'):
        parameters_dict = {k.name: v for k, v in zip(self.params, param_list)}
        score_dict = self.evaluate_parameters(parameters_dict)
        print(f"[{time.strftime('%D-%H:%M:%S')}] Sum scores: ", numpy.sum([score_dict[t.name] for t in self.objectives]))
        return [score_dict[t.name] for t in self.objectives]


def define_targets(opt_config):

    targets = []
    for target_config in opt_config['targets']:

        target_name = target_config["class"] + "_" + target_config["sheet_name"]

        targets.append(
            getattr(sys.modules[__name__], target_config['class'])(
                name=target_name,
                target_value=target_config["target_value"],
                sheet_name=target_config["sheet_name"],
                norm=target_config["norm"],
                max_score=target_config["max_score"]
            )
        )

    return targets


def define_parameters(opt_config):

    parameters = []
    for k, v in opt_config['parameters'].items():
        parameters.append(Parameter(name=k, lower_bound=v[0], upper_bound=v[1]))

    return parameters


def define_fitness_calculator(opt_config):
    targets = define_targets(opt_config)
    return FitnessCalculator(targets)


def define_evaluator(run_script, parameters_url, timeout, config_optimisation):

    with open(config_optimisation) as f:
        opt_config = json.load(f)

    simulator_name = "nest"

    backend = SlurmSequentialBackend(
        num_threads=1,
        num_mpi=16,
        slurm_options=[
            '--hint=nomultithread', 
            '-N 1-1', 
            '-x w[9,11,13-17]',  # Runs on the small nodes
            # '-x w[1-8,10,12]',  # Runs on the big nodes
        ],
        path_to_mozaik_env='/home/haman/virt_env/layers56new/bin/activate'
    )
    params = define_parameters(opt_config)
    fitness_calculator = define_fitness_calculator(opt_config)

    return Evaluator(fitness_calculator, params, run_script, simulator_name, parameters_url, backend, pynn_seed=1, timeout=timeout)
