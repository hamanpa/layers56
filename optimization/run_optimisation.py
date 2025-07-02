import multiprocessing as mp
from bluepyopt.deapext.optimisationsCMA import DEAPOptimisationCMA
from evaluator import define_evaluator


offspring_size = 2                 # Size of the population used by the optimizer
timeout = 72000                      # Hard cut-off for the evaluation of an individual (in seconds)
optimiser_seed = 7                  # random seed for the optimiser
optimiser_sigma = 0.3               # width of the search at the first generation of the optimisation, default: 0.4
max_ngen = 200                      # Maximum number of generation of the optimiser
# run_script = "run_experiment.py"    # Path to the Mozaik run script to use for evaluation
model = 'LSV1M_split_ee'  

import os
os.chdir('/home/haman/layers56/' + model + '/')

run_script = 'run_optimization_experiment.py'
parameters_url = 'param_optim/defaults'
config_optimisation = './param_optim/config_optimisation'

MODELS = {
    'LSV1M_split_ee': {
        'parameters_url' : "LSV1M_split_ee/param-optim/defaults",                              # Path the Mozaik parameters
        'config_optimisation' : "./param-optim/config_optimisation",            # path to the optimisation parameters and targets
        'optimiser_centroid' : []
    },

    'full-split': {
        'parameters_url' : "param-split/defaults",                              # Path the Mozaik parameters
        'config_optimisation' : "./param-split/config_optimisation",            # path to the optimisation parameters and targets
        'optimiser_centroid' : [
            0.05838074015746973,                                                # density_frac

            2.118356202491846,                                                  # sheets.l4_cortex_exc.params.cell.params.tau_syn_E
            7.714636035653577,                                                  # sheets.l4_cortex_exc.params.cell.params.tau_syn_I
            8.219650587987363,                                                  # sheets.l4_cortex_exc.params.cell.params.tau_m
            0.03372765761768889,                                                # sheets.l4_cortex_exc.params.cell.params.cm
            -78.85422944055654,                                                 # sheets.l4_cortex_exc.params.cell.params.v_rest
            -55.85177146816158,                                                 # sheets.l4_cortex_exc.params.cell.params.v_thresh
            0.03126047748510413,                                                # sheets.l4_cortex_inh.params.cell.params.cm
            8.151771318660863,                                                  # sheets.l4_cortex_inh.params.cell.params.tau_m
            -74.06216071007701,                                                 # sheets.l4_cortex_inh.params.cell.params.v_rest
            -56.35738453193072,                                                 # sheets.l4_cortex_inh.params.cell.params.v_thresh

            1095.0682791181828,                                                 # sheets.l4_cortex_exc.K
            2220.7710506710987,                                                 # sheets.l23_cortex_exc.K
            0.11712571655620121,                                                # sheets.l4_cortex_exc.feedback_conn_ratio
            0.5546389541284226,                                                 # sheets.l4_cortex_exc.inhibitory_connection_ratio
            0.26484716139843406,                                                # sheets.l23_cortex_exc.layer23_aff_ratio

            188.93776858990196,                                                 # sheets.l23_cortex_exc.L23ExcL4ExcConnection.weight_functions.f1.params.arborization_constant

            0.8673651121010519,                                                 # sheets.l4_cortex_exc.L4ExcL4ExcConnection.short_term_plasticity.U
            33.92257613712719,                                                  # sheets.l4_cortex_exc.L4ExcL4ExcConnection.short_term_plasticity.tau_rec
            54.67942337721925,                                                  # sheets.l4_cortex_inh.L4InhL4ExcConnection.short_term_plasticity.tau_rec
            141.75322258139843,                                                 # sheets.l4_cortex_exc.AfferentConnection.short_term_plasticity.tau_rec

            0.00018833858091460187,                                             # sheets.l4_cortex_exc.L4ExcL4ExcConnection.base_weight
            0.0002569499417549022,                                              # sheets.l4_cortex_exc.L4ExcL4InhConnection.base_weight
            0.0008781289547551183,                                              # sheets.l23_cortex_exc.L4ExcL23ExcConnection.base_weight
            0.00018833858091460187,                                             # sheets.l23_cortex_exc.L23ExcL23ExcConnectionShort.base_weight
            0.00018833858091460187,                                             # sheets.l23_cortex_exc.L23ExcL23ExcConnectionLong.base_weight
            0.000672471570786831,                                               # sheets.l23_cortex_exc.L23ExcL23InhConnectionShort.base_weight
            0.000672471570786831,                                               # sheets.l23_cortex_exc.L23ExcL23InhConnectionLong.base_weight
            0.0006146969239380421,                                              # sheets.l4_cortex_inh.L4InhL4ExcConnection.base_weight
            0.0009296706810154975,                                              # sheets.l4_cortex_exc.AfferentConnection.base_weight

            1.267548593235346,                                                  # sheets.l23_cortex_exc.L23ExcL23ExcConnectionLong.weight_functions.f1.params.sigma

            84.61143364723677,                                                  # sheets.l4_cortex_exc.AfferentMean
            26.043109298883095,                                                 # sheets.l4_cortex_exc.AfferentVar
            0.18849539734518034,                                                # sheets.l4_cortex_exc.AfferentConnection.size
            0.0003201222939928967,                                              # sheets.l4_cortex_exc.AfferentConnection.rf_jitter
            1.0808622343161192,                                                 # sheets.l4_cortex_exc.AfferentConnection.off_bias
            19.048852261595727,                                                 # sheets.l4_cortex_inh.AfferentVar

        ],
    },
    'ee-split': {
        'parameters_url' : "param-ee-split/defaults",                              # Path the Mozaik parameters
        'config_optimisation' : "./param-ee-split/config_optimisation",            # path to the optimisation parameters and targets
        'optimiser_centroid' : [
            0.05838074015746973,                                                # density_frac

            2.118356202491846,                                                  # sheets.l4_cortex_exc.params.cell.params.tau_syn_E
            7.714636035653577,                                                  # sheets.l4_cortex_exc.params.cell.params.tau_syn_I
            8.219650587987363,                                                  # sheets.l4_cortex_exc.params.cell.params.tau_m
            0.03372765761768889,                                                # sheets.l4_cortex_exc.params.cell.params.cm
            -78.85422944055654,                                                 # sheets.l4_cortex_exc.params.cell.params.v_rest
            -55.85177146816158,                                                 # sheets.l4_cortex_exc.params.cell.params.v_thresh
            0.03126047748510413,                                                # sheets.l4_cortex_inh.params.cell.params.cm
            8.151771318660863,                                                  # sheets.l4_cortex_inh.params.cell.params.tau_m
            -74.06216071007701,                                                 # sheets.l4_cortex_inh.params.cell.params.v_rest
            -56.35738453193072,                                                 # sheets.l4_cortex_inh.params.cell.params.v_thresh

            1095.0682791181828,                                                 # sheets.l4_cortex_exc.K
            2220.7710506710987,                                                 # sheets.l23_cortex_exc.K
            0.11712571655620121,                                                # sheets.l4_cortex_exc.feedback_conn_ratio
            0.5546389541284226,                                                 # sheets.l4_cortex_exc.inhibitory_connection_ratio
            0.26484716139843406,                                                # sheets.l23_cortex_exc.layer23_aff_ratio

            188.93776858990196,                                                 # sheets.l23_cortex_exc.L23ExcL4ExcConnection.weight_functions.f1.params.arborization_constant

            0.8673651121010519,                                                 # sheets.l4_cortex_exc.L4ExcL4ExcConnection.short_term_plasticity.U
            33.92257613712719,                                                  # sheets.l4_cortex_exc.L4ExcL4ExcConnection.short_term_plasticity.tau_rec
            54.67942337721925,                                                  # sheets.l4_cortex_inh.L4InhL4ExcConnection.short_term_plasticity.tau_rec
            141.75322258139843,                                                 # sheets.l4_cortex_exc.AfferentConnection.short_term_plasticity.tau_rec

            0.00018833858091460187,                                             # sheets.l4_cortex_exc.L4ExcL4ExcConnection.base_weight
            0.0002569499417549022,                                              # sheets.l4_cortex_exc.L4ExcL4InhConnection.base_weight
            0.0008781289547551183,                                              # sheets.l23_cortex_exc.L4ExcL23ExcConnection.base_weight
            0.00018833858091460187,                                             # sheets.l23_cortex_exc.L23ExcL23ExcConnectionShort.base_weight
            0.00018833858091460187,                                             # sheets.l23_cortex_exc.L23ExcL23ExcConnectionLong.base_weight
            0.000672471570786831,                                               # sheets.l23_cortex_exc.L23ExcL23InhConnection.base_weight
            0.0006146969239380421,                                              # sheets.l4_cortex_inh.L4InhL4ExcConnection.base_weight
            0.0009296706810154975,                                              # sheets.l4_cortex_exc.AfferentConnection.base_weight

            1.267548593235346,                                                  # sheets.l23_cortex_exc.L23ExcL23ExcConnectionLong.weight_functions.f1.params.sigma

            84.61143364723677,                                                  # sheets.l4_cortex_exc.AfferentMean
            26.043109298883095,                                                 # sheets.l4_cortex_exc.AfferentVar
            0.18849539734518034,                                                # sheets.l4_cortex_exc.AfferentConnection.size
            0.0003201222939928967,                                              # sheets.l4_cortex_exc.AfferentConnection.rf_jitter
            1.0808622343161192,                                                 # sheets.l4_cortex_exc.AfferentConnection.off_bias
            19.048852261595727,                                                 # sheets.l4_cortex_inh.AfferentVar
        ]
    }
}



optimiser_centroid = [
    0.1,  # density_frac
    1.5,  # sheets.l4_cortex_exc.params.cell.params.tau_syn_E
    4.2,  # sheets.l4_cortex_exc.params.cell.params.tau_syn_I
    8.0,  # sheets.l4_cortex_exc.params.cell.params.tau_m
    0.032,  # sheets.l4_cortex_exc.params.cell.params.cm
    -80.0,  # sheets.l4_cortex_exc.params.cell.params.v_rest
    -57.0,  # sheets.l4_cortex_exc.params.cell.params.v_thresh
    0.03,  # sheets.l4_cortex_inh.params.cell.params.cm
    9.0,  # sheets.l4_cortex_inh.params.cell.params.tau_m
    -78.0,  # sheets.l4_cortex_inh.params.cell.params.v_rest
    -58.0,  # sheets.l4_cortex_inh.params.cell.params.v_thresh
    1000,  # sheets.l4_cortex_exc.K
    2300,  # sheets.l23_cortex_exc.K
    0.2,  # sheets.l4_cortex_exc.feedback_conn_ratio
    0.6,  # sheets.l4_cortex_exc.inhibitory_connection_ratio
    0.22,  # sheets.l23_cortex_exc.layer23_aff_ratio
    0.75,  # sheets.l4_cortex_exc.L4ExcL4ExcConnection.short_term_plasticity.U
    30,  # sheets.l4_cortex_exc.L4ExcL4ExcConnection.short_term_plasticity.tau_rec
    70,  # sheets.l4_cortex_inh.L4InhL4ExcConnection.short_term_plasticity.tau_rec
    1.3,  # sheets.l4_cortex_exc.L4ExcL4ExcConnection.weight_functions.f1.params.sigma
    0.00018,  # sheets.l4_cortex_exc.L4ExcL4ExcConnection.base_weight
    0.00022,  # sheets.l4_cortex_exc.L4ExcL4InhConnection.base_weight
    0.001,  # sheets.l23_cortex_exc.L4ExcL23ExcConnection.base_weight
    0.001,  # sheets.l23_cortex_exc.L23ExcL23InhConnection.base_weight
    0.00035,  # sheets.l4_cortex_inh.L4InhL4ExcConnection.base_weight
    100.0,  # sheets.l23_cortex_exc.L23ExcL4ExcConnection.weight_functions.f1.params.arborization_constant
    4.0,  # sheets.l23_cortex_exc.L23ExcL23ExcConnection.weight_functions.f3.params.arborization_scaler
    70,  # sheets.l4_cortex_exc.AfferentMean
    25,  # sheets.l4_cortex_exc.AfferentVar
    0.17,  # sheets.l4_cortex_exc.AfferentConnection.size
    0.,  # sheets.l4_cortex_exc.AfferentConnection.rf_jitter
    1.0,  # sheets.l4_cortex_exc.AfferentConnection.off_bias
    0.0012,  # sheets.l4_cortex_exc.AfferentConnection.base_weight
    125,  # sheets.l4_cortex_exc.AfferentConnection.short_term_plasticity.tau_rec
    14,  # sheets.l4_cortex_inh.AfferentVar
]




#######################
# Tanguy's parameters #
#######################

# parameters_url = "param/defaults"   # Path the Mozaik parameters
# config_optimisation = "./param/config_optimisation" # path to the optimisation parameters and targets

#####################
# Remy's parameters #
#####################

# parameters_url = "param/defaults"   # Path the Mozaik parameters
# config_optimisation = "./param/config_optimisation" # path to the optimisation parameters and targets

###################
# LSV1M with refs #
###################

# NOTE: parameters where all the possible references have been made

# parameters_url = "param-ref-orig/defaults"   # Path the Mozaik parameters
# config_optimisation = "./param-ref-orig/config_optimisation" # path to the optimisation parameters and targets

########################
# Optimizer parameters #
########################

# NOTE: these parameters are taking the LSV1M with refs and connects 
# following parameters: Short-term plasticity (U, tau_rec)

########################
# Connections split parameters #
########################

# parameters_url = MODELS[model]['parameters_url']   
# config_optimisation = MODELS[model]['config_optimisation'] 
optimiser_centroid = MODELS['ee-split']['optimiser_centroid'] 

##############
# Layers 5&6 #
##############

# parameters_url = "param/defaults"   # Path the Mozaik parameters
# config_optimisation = "./param/config_optimisation" # path to the optimisation parameters and targets



evaluator = define_evaluator(
    run_script=run_script,
    parameters_url=parameters_url,
    timeout = timeout,
    config_optimisation=config_optimisation
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
