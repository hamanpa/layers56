# -*- coding: utf-8 -*-
import sys
from mozaik.meta_workflow.parameter_search import CombinationParameterSearch, SlurmSequentialBackend
import numpy
import time

test_pars = {
    'pynn_seed': [1],
    'density_frac': [0.07097590559911304],
    'sheets.l4_cortex_exc.params.cell.params.tau_syn_E': [1.50000000175],
    'sheets.l4_cortex_exc.params.cell.params.tau_syn_I': [8.26620773143669],
    'sheets.l4_cortex_exc.params.cell.params.tau_m': [8.987131294895978],
    'sheets.l4_cortex_exc.params.cell.params.cm': [0.028395074490369182],
    'sheets.l4_cortex_exc.params.cell.params.v_rest': [-73.55848017688666],
    'sheets.l4_cortex_exc.params.cell.params.v_thresh': [-56.37783332931715],
    'sheets.l4_cortex_inh.params.cell.params.cm': [0.02422793561112068],
    'sheets.l4_cortex_inh.params.cell.params.tau_m': [7.493278497363723],
    'sheets.l4_cortex_inh.params.cell.params.v_rest': [-77.91607230035372],
    'sheets.l4_cortex_inh.params.cell.params.v_thresh': [-56.69366306126536],
    'sheets.l4_cortex_exc.K': [1164.4052484690596],
    'sheets.l23_cortex_exc.K': [2152.00831905776],
    'sheets.l4_cortex_exc.feedback_conn_ratio': [0.14143071280352332],
    'sheets.l4_cortex_exc.inhibitory_connection_ratio': [0.50000000015],
    'sheets.l23_cortex_exc.layer23_aff_ratio': [0.28027063152221665],
    'sheets.l23_cortex_exc.L23ExcL4ExcConnection.weight_functions.f1.params.arborization_constant': [245.8512180374346],
    'sheets.l4_cortex_exc.L4ExcL4ExcConnection.short_term_plasticity.U': [0.7806513058184916],
    'sheets.l4_cortex_exc.L4ExcL4ExcConnection.short_term_plasticity.tau_rec': [31.82601806718693],
    'sheets.l4_cortex_inh.L4InhL4ExcConnection.short_term_plasticity.tau_rec': [23.425825902210626],
    'sheets.l4_cortex_exc.AfferentConnection.short_term_plasticity.tau_rec': [115.68385101358946],
    'sheets.l4_cortex_exc.L4ExcL4ExcConnection.base_weight': [0.0001536014475263858],
    'sheets.l4_cortex_exc.L4ExcL4InhConnection.base_weight': [0.00027569469045778057],
    'sheets.l23_cortex_exc.L4ExcL23ExcConnection.base_weight': [0.0009852913353158685],
    'sheets.l23_cortex_exc.L23ExcL23ExcConnectionShort.base_weight': [0.00025605154547189143],
    'sheets.l23_cortex_exc.L23ExcL23ExcConnectionLong.base_weight': [0.0003487719497965897],
    'sheets.l23_cortex_exc.L23ExcL23InhConnection.base_weight': [0.0006940442649024069],
    'sheets.l4_cortex_inh.L4InhL4ExcConnection.base_weight': [0.00023524438212862455],
    'sheets.l4_cortex_exc.AfferentConnection.base_weight': [0.0010463849887015386],
    'sheets.l23_cortex_exc.L23ExcL23ExcConnectionLong.weight_functions.f1.params.sigma': [1.0594535406891785],
    'sheets.l4_cortex_exc.AfferentMean': [78.03342055810427],
    'sheets.l4_cortex_exc.AfferentVar': [24.491391081689887],
    'sheets.l4_cortex_exc.AfferentConnection.size': [0.17880144999979594],
    'sheets.l4_cortex_exc.AfferentConnection.rf_jitter': [0.0003243466688827848],
    'sheets.l4_cortex_exc.AfferentConnection.off_bias': [1.0431210708341525],
    'sheets.l4_cortex_inh.AfferentVar': [18.868284915002683]
}


if True:
    CombinationParameterSearch(SlurmSequentialBackend(
        num_threads=1, 
        num_mpi=16,
        slurm_options=[
            '--hint=nomultithread',
            # '-w w5',
            '-x w[1,2,9,11,13-17]',  # Runs on the small nodes
            # '-x w[1-8,10,12]',  # Runs on the big nodes
            '-N 1-1',  # ensure minimum 1 node - maximum 1 node is used
        ],
        path_to_mozaik_env='/home/haman/virt_env/layers56new/bin/activate'),
        {
            'trial' : [1],
            **test_pars,
        }).run_parameter_search()



