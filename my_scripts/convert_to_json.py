"""
Script to convert output files loaded by Arkheia to a newly used JSON format.
It requiers a new version of Mozaik to be installed, which includes the save_json function.
"""

import glob
from pathlib import Path
import os
import re
import pickle

import json
from numpyencoder import NumpyEncoder
from mozaik.tools.json_export import save_json, get_experimental_protocols, get_recorders, get_stimuli
from mozaik.tools.distribution_parametrization import MozaikExtendedParameterSet
from mozaik.storage.datastore import PickledDataStore
from parameters import ParameterSet


# Change this to the directory where the model ParameterSearch folders are located
MODEL_DIR = Path('/home/haman/layers56/LSV1M')

def main():
    for param_search in MODEL_DIR.glob("[0-9]*"):
        print(param_search.name)

        # parameter_combinations --> parameter_combinations.json
        try:
            with open(param_search / 'parameter_combinations', 'rb') as f:
                par_combs = pickle.load(f)
            save_json(par_combs, param_search / 'parameter_combinations.json')
        except FileNotFoundError:
            print(f"file 'parameter_combinations' not found in {param_search}")
            print('Skipping...')
            continue

        for sim_run in param_search.glob("*ParameterSearch*"):

            # results --> results.json
            try:
                with open(sim_run / 'results', 'r') as f:
                    results = f.read()
                new_results = []
                for res in results.strip("\n").split("\n"):
                    res = eval(res)
                    entry = {'code': res['class_name'].split("'")[1]}
                    entry['name'] = entry['code'].split('.')[-1]
                    entry['caption'] = 'Caption not specified.'
                    entry['parameters'] = res['parameters']
                    entry['figure'] = res['file_name']
                    new_results.append(entry)
                save_json(new_results, sim_run / 'results.json')
            except FileNotFoundError:
                print(f"file 'results' not found in {sim_run}")

            # modified_parameters --> modified_parameters.json
            try:
                with open (sim_run / "modified_parameters", "rb") as f:
                    mod_pars = pickle.load(f)
                mod_pars = eval(mod_pars)
                save_json(mod_pars, sim_run / "modified_parameters.json")
            except FileNotFoundError:
                print(f"file 'modified_parameters' not found in {sim_run}")

            # info --> sim_info.json
            try:
                with open (sim_run / "info", "rb") as f:
                    info = f.read()
                info = eval(info)
                sim_info = {}
                sim_info['submission_date'] = None
                sim_info['run_date'] = info['creation_data']

                # sim_info['simulation_run_name'] = info['simulation_run_name']
                # By default, the simulation_run_name is 'ParameterSearch'
                sim_info['simulation_run_name'] = param_search.name

                sim_info['model_name'] = info['model_name']
                if info['model_docstring']:
                    sim_info["model_description"] = info['model_docstring']
                else:
                    sim_info["model_description"] = "\n    Model description placeholder.\n    "
                sim_info['results'] = {"$ref": "results.json"}
                sim_info['stimuli'] = {"$ref": "stimuli.json"},
                sim_info['recorders'] = {"$ref": "recorders.json"},
                sim_info['experimental_protocols'] = {"$ref": "experimental_protocols.json"},
                sim_info['parameters'] = {"$ref": "parameters.json"},
                save_json(sim_info, sim_run / 'sim_info.json')
            except FileNotFoundError:
                print(f"file 'info' not found in {sim_run}")

            # parameters --> parameters.json
            try:
                with open (sim_run / "parameters", "rb") as f:
                    pars = f.read()
                pars = MozaikExtendedParameterSet(pars)
                save_json(pars.to_dict(), sim_run / "parameters.json")

                # recorders --> recorders.json
                recorders = get_recorders(pars.to_dict())
                save_json(recorders, sim_run / 'recorders.json')

                # data_store = PickledDataStore(load=True, 
                #     parameters=ParameterSet({
                #         'root_directory': str(Path(sim_run).resolve()),
                #         'store_stimuli': False
                #     }),
                #     replace=True
                # )

                # # experimental_protocols --> experimental_protocols.json
                # experimental_protocols = get_experimental_protocols(data_store)
                # save_json(experimental_protocols, sim_run / 'experimental_protocols.json')

                # # stimuli --> stimuli.json
                # stimuli = get_stimuli(data_store, pars.store_stimuli, pars.input_space)
                # save_json(stimuli, sim_run / 'stimuli.json')


            except FileNotFoundError:
                print(f"file 'parameters' not found in {sim_run}")

if __name__ == "__main__":
    main()
