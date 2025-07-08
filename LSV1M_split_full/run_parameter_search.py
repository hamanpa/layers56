# -*- coding: utf-8 -*-
import sys
from mozaik.meta_workflow.parameter_search import CombinationParameterSearch, SlurmSequentialBackend
import numpy
import time

import json
import pickle

if False:
    optimization_folder = "20250617-145255_Optimization"
    checkpoint_path = f"./{optimization_folder}/opt_check.pkl"
    config_optimisation = "param_optim/config_optimisation"

    with open(config_optimisation) as f:
        opt_config = json.load(f)
    param_names = list(opt_config['parameters'].keys())

    with open(checkpoint_path, "rb") as fp:
        run = pickle.load(fp, encoding="latin1")

    best_pars = {x : [y] for x,y in zip(param_names,run['halloffame'][0])}
if False:
    best_pars = {
        "density_frac": [0.05248792352367391],
        "sheets.l4_cortex_exc.params.cell.params.tau_syn_E": [1.50000000175],
        "sheets.l4_cortex_exc.params.cell.params.tau_syn_I": [8.971428282343778],
        "sheets.l4_cortex_exc.params.cell.params.tau_m": [9.5506262163267],
        "sheets.l4_cortex_exc.params.cell.params.cm": [0.03501170412988251],
        "sheets.l4_cortex_exc.params.cell.params.v_rest": [-78.21654511158059],
        "sheets.l4_cortex_exc.params.cell.params.v_thresh": [-56.594939932098356],
        "sheets.l4_cortex_inh.params.cell.params.cm": [0.030370170618297446],
        "sheets.l4_cortex_inh.params.cell.params.tau_m": [8.296317041517392],
        "sheets.l4_cortex_inh.params.cell.params.v_rest": [-73.81728476565934],
        "sheets.l4_cortex_inh.params.cell.params.v_thresh": [-56.65324549713711],
        "sheets.l4_cortex_exc.K": [881.621301715468],
        "sheets.l23_cortex_exc.K": [2132.3411209720434],
        "sheets.l4_cortex_exc.feedback_conn_ratio": [0.1166407161705132],
        "sheets.l4_cortex_exc.inhibitory_connection_ratio": [0.5882265047584692],
        "sheets.l23_cortex_exc.layer23_aff_ratio": [0.3748403351830457],
        "sheets.l23_cortex_exc.L23ExcL4ExcConnection.weight_functions.f1.params.arborization_constant": [161.6038213918382],
        "sheets.l4_cortex_exc.L4ExcL4ExcConnection.short_term_plasticity.U": [0.9048541679002206],
        "sheets.l4_cortex_exc.L4ExcL4ExcConnection.short_term_plasticity.tau_rec": [28.154098013290373],
        "sheets.l4_cortex_inh.L4InhL4ExcConnection.short_term_plasticity.tau_rec": [68.92918590395277],
        "sheets.l4_cortex_exc.AfferentConnection.short_term_plasticity.tau_rec": [107.42657357553244],
        "sheets.l4_cortex_exc.L4ExcL4ExcConnection.base_weight": [0.00013386959673549007],
        "sheets.l4_cortex_exc.L4ExcL4InhConnection.base_weight": [0.00039131627516358447],
        "sheets.l23_cortex_exc.L4ExcL23ExcConnection.base_weight": [0.0007594606185067022],
        "sheets.l23_cortex_exc.L23ExcL23ExcConnectionShort.base_weight": [0.0001989402776580432],
        "sheets.l23_cortex_exc.L23ExcL23ExcConnectionLong.base_weight": [8.408060063706856e-05],
        "sheets.l23_cortex_exc.L23ExcL23InhConnectionShort.base_weight": [0.0007286429703506393],
        "sheets.l23_cortex_exc.L23ExcL23InhConnectionLong.base_weight": [0.0007552842305782526],
        "sheets.l4_cortex_inh.L4InhL4ExcConnection.base_weight": [0.0005533537195323776],
        "sheets.l4_cortex_exc.AfferentConnection.base_weight": [0.0007567584525506748],
        "sheets.l23_cortex_exc.L23ExcL23ExcConnectionLong.weight_functions.f1.params.sigma": [1.0440668988280315],
        "sheets.l4_cortex_exc.AfferentMean": [72.04257401080599],
        "sheets.l4_cortex_exc.AfferentVar": [27.71837268944862],
        "sheets.l4_cortex_exc.AfferentConnection.size": [0.1871597255704232],
        "sheets.l4_cortex_exc.AfferentConnection.rf_jitter": [0.0003383061499029833],
        "sheets.l4_cortex_exc.AfferentConnection.off_bias": [1.0999999999],
        "sheets.l4_cortex_inh.AfferentVar": [17.256562416185112],
    }

else:
    best_pars = {}

if True:
    CombinationParameterSearch(
        SlurmSequentialBackend(
            num_threads=1, 
            num_mpi=16,
            slurm_options=[
                '--hint=nomultithread',
                # '-x w[9,11,13-17]',  # Runs on all the small nodes
                '-x w[1,2,9,11,13-17]',  # Runs on the small nodes (except w1,w2)
                # '-x w[1-8,10,12]',  # Runs on the big nodes
                '-N 1-1',  # ensure minimum 1 node - maximum 1 node is used
            ],
            path_to_mozaik_env='/home/haman/virt_env/layers56new/bin/activate'), 
        {
            'trial' : [1],
            **best_pars
        }).run_parameter_search()



