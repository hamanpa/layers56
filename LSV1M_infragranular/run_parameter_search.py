# -*- coding: utf-8 -*-
import sys
from mozaik.meta_workflow.parameter_search import CombinationParameterSearch, SlurmSequentialBackend
import numpy
import time

SIMULATION_NAME = 'L5b-lgnl5_projection'

if True:
    CombinationParameterSearch(
        SlurmSequentialBackend(
            num_threads = 1, 
            num_mpi = 32,
            slurm_options = [
                '--hint=nomultithread',
                '-w w15',
                # '-x w[1-14,16-17]',  # exclude nodes
                '-N 1-1',  # ensure minimum 1 node - maximum 1 node is used
                f'--job-name={SIMULATION_NAME}'
            ],
            path_to_mozaik_env = '/home/haman/virt_env/layers56/bin/activate'),
        {
            'l5a' : [False],
            'l5b' : [True],
            'l5_conn_ratio' : [0.], # 0 means only l5b

            # 'l4l5_projection' : [True],
            'sheets.l5_cortex_exb.l23_aff_ratio' : [0.3], 
            'sheets.l5_cortex_exb.l4_aff_ratio' : [0.0],

            # No L5 self cons 
            'sheets.l5_cortex_exb.L5ExbL5ExbConnection.num_samples' : [0],
            'sheets.l5_cortex_exb.L5ExbL5InhConnection.num_samples' : [0],
            'sheets.l5_cortex_inh.L5InhL5InhConnection.num_samples' : [0],
            'sheets.l5_cortex_inh.L5InhL5ExbConnection.num_samples' : [0],
            
            # 'lgnl23_projection' : [False],

            'lgnl5_projection' : [True],
            'sheets.l5_cortex_exb.AfferentMean' : [0, 20],
            # 'sheets.l5_cortex_inh.AfferentMean' : [0],

            # 'sheets.l23_cortex_exc.L23ExcL23ExcConnection.num_samples' : [0],
            # 'sheets.l23_cortex_exc.L23ExcL23InhConnection.num_samples' : [0],
            # 'sheets.l23_cortex_inh.L23InhL23ExcConnection.num_samples' : [0],
            # 'sheets.l23_cortex_inh.L23InhL23InhConnection.num_samples' : [0],

            # 'sheets.l23_cortex_exc.L23ExcL5ExaConnection.short_term_plasticity.tau_rec' : [0.1, 5., 15., 30.0, 100.],
            # 'sheets.l23_cortex_exc.L23ExcL5InhConnection.short_term_plasticity.tau_rec' : [0.1, 5., 15., 30.0],


            ########################
            #       L5a ONLY       #
            ########################

            # 'l5a_density' : [19300],
            # 'sheets.l5_cortex_inh.params.density' : [19300/4.*0.1],
            # 'l5_conn_ratio' : [1],
            # 'sheets.l5_cortex_exb.K' : [0],
            # 'sheets.l5_cortex_exa.l23_aff_ratio' : [0.3],
            # 'sheets.l5_cortex_exa.l5b_aff_ratio' : [0.0],

            ########################
            #       L5b ONLY       #
            ########################

            # 'l5a_density' : [19300],
            # 'sheets.l5_cortex_inh.params.density' : [19300/4.*0.1],
            # 'l5_conn_ratio' : [0],
            # 'sheets.l5_cortex_exa.K' : [0],
            # 'sheets.l5_cortex_exb.K' : [1],
            # 'sheets.l5_cortex_exb.l23_aff_ratio' : [0.3],
            # 'sheets.l5_cortex_exb.l5a_aff_ratio' : [0.0],

            # connectios directly
            # 'sheets.l23_cortex_exc.L23ExcL5ExbConnection.num_samples' : [240],
            # 'sheets.l23_cortex_exc.L23ExcL5ExbConnection.base_weight' : [0.001],

            # 'sheets.l23_cortex_exc.L23ExcL5InhConnection.num_samples' : [144],
            # 'sheets.l23_cortex_exc.L23ExcL5InhConnection.base_weight' : [0.001],

            # 'sheets.l5_cortex_exb.L5ExbL5ExbConnection.num_samples' : [560],
            # 'sheets.l5_cortex_exb.L5ExbL5ExbConnection.num_samples' : [0],
            # 'sheets.l5_cortex_exb.L5ExbL5ExbConnection.num_samples' : [460, 510, 560, 610, 660],
            # 'sheets.l5_cortex_exb.L5ExbLL5ExbConnection.base_weight' : [0.001],

            # 'sheets.l5_cortex_exb.L5ExbL5InhConnection.num_samples' : [336],
            # 'sheets.l5_cortex_exb.L5ExbL5InhConnection.num_samples' : [0],
            # 'sheets.l5_cortex_exb.L5ExbL5InhConnection.num_samples' : [276, 306, 336, 366, 396],
            # 'sheets.l5_cortex_exb.L5ExbL5InhConnection.base_weight' : [0.001],
            
            # 'sheets.l5_cortex_inh.L5InhL5InhConnection.num_samples' : [120],
            # 'sheets.l5_cortex_inh.L5InhL5InhConnection.num_samples' : [0],
            # 'sheets.l5_cortex_inh.L5InhL5InhConnection.num_samples' : [80, 100, 120, 140, 160],
            # 'sheets.l5_cortex_exb.L5InhL5InhConnection.base_weight' : [0.001],

            # 'sheets.l5_cortex_inh.L5InhL5ExbConnection.num_samples' : [200],
            # 'sheets.l5_cortex_inh.L5InhL5ExbConnection.num_samples' : [0],
            # 'sheets.l5_cortex_inh.L5InhL5ExbConnection.num_samples' : [140, 170, 200, 230, 260],
            # 'sheets.l5_cortex_exb.L5InhL5ExbConnection.base_weight' : [0.001],

            ########################
            #       L5ab MIX       #
            ########################

            # 'l5a_density' : [9650],
            # 'sheets.l5_cortex_inh.params.density' : [19300/4.*0.1],
            # 'l5_conn_ratio' : [0.5],
            # 'sheets.l5_cortex_exa.l23_aff_ratio' : [0.3],
            # 'sheets.l5_cortex_exb.l23_aff_ratio' : [0.3],
            # 'sheets.l5_cortex_exa.l5b_aff_ratio' : [0.35],
            # 'sheets.l5_cortex_exb.l5a_aff_ratio' : [0.35],

            ########################
            #        PARAMS        #
            ########################

            # 'sheets.l23_cortex_exc.l4_aff_ratio' : [0., 0.1, 0.2, 0.22, 0.3, 0.4, 0.5],


            # 'sheets.l23_cortex_exc.L23ExcL23ExcConnection.num_samples' : [0],
            # 'sheets.l23_cortex_exc.L23ExcL23InhConnection.num_samples' : [0],
            # 'sheets.l23_cortex_inh.L23InhL23ExcConnection.num_samples' : [0],
            # 'sheets.l23_cortex_inh.L23InhL23InhConnection.num_samples' : [0],


            # 'sheets.l5_cortex_exb.L5ExbL5InhConnection.base_weight' : [0.00035],

            # 'sheets.l23_cortex_exc.L23ExcL5ExaConnection.base_weight' : [0.0008, 0.0009, 0.001, 0.0011, 0.0012],
            # 'sheets.l23_cortex_exc.L23ExcL5ExbConnection.base_weight' : [0.0008, 0.0009, 0.001, 0.0011, 0.0012],
            # 'sheets.l23_cortex_exc.L23ExcL5InhConnection.base_weight' : [0.0008, 0.001, 0.0012],

            # 1) L23 AFFERENT RATIO
            # 'sheets.l5_cortex_exa.l23_aff_ratio' : [0.3],
            # 'sheets.l5_cortex_exb.l23_aff_ratio' : [0.4],

            # 2) HORIZONTAL CONNECTIONS
            # 'sheets.l5_cortex_exa.L5ExaL5ExaConnection.weight_functions.f3.params.arborization_constant' : [250, 750, 1500],
            # 'sheets.l5_cortex_exa.L5ExaL5ExaConnection.weight_functions.f3.params.arborization_scaler' : [0, 2, 4],
            # 'sheets.l5_cortex_exb.L5ExbL5ExaConnection.weight_functions.f3.arborization_constant' : [200, 400, 600, 800, 1000, 1200, 1400, 1600],
            # 'sheets.l5_cortex_exb.L5ExbL5ExaConnection.weight_functions.f3.arborization_scaler' : [1, 3, 5],

            # TURNS ON ADPATATION
            # 'sheets.l4_cortex_exc.params.cell.params.b' : [80.0],
            # 'sheets.l4_cortex_exc.params.cell.params.tau_w' : [144.0],

            # BASE_WEIGHT L23 --> L5
            # 'sheets.l23_cortex_exc.L23ExcL5ExaConnection.base_weight' : [0.001],
            # 'sheets.l23_cortex_exc.L23ExcL5ExbConnection.base_weight' : [0.001],
            # 'sheets.l23_cortex_exc.L23ExcL5InhConnection.base_weight' : [0.001],

            # L5 INTRALAMINAR CONNECTIONS
            # 'sheets.l5_cortex_exa.l5b_aff_ratio' : [0.05*x for x in range(15)],
            # 'sheets.l5_cortex_exb.l5a_aff_ratio' : [0.05*x for x in range(13)],

            # 'sheets.l5_cortex_exa.K' : [800+100*x for x in range(8)],
            # 'sheets.l5_cortex_exb.K' : [800+100*x for x in range(8)],

            # 'sheets.l5_cortex_inh.inhibitory_connection_ratio' : [0.5 + 0.05*x for x in range(5)],

            # 'sheets.l5_cortex_exa.L5ExaL5ExaConnection.base_weight' : [0.0001, 0.0002],
            # 'sheets.l5_cortex_inh.L5InhL5ExaConnection.num_samples' : [200],
            # 'sheets.l5_cortex_inh.L5InhL5ExaConnection.num_samples' : [200],
            # [180 + 10*x for x in range(10)],
            # 'sheets.l5_cortex_inh.L5InhL5ExaConnection.num_samples' : [2*x for x in range(1,26)],


            # 'sheets.l6_cortex_exa.AfferentMean' : [20, 30, 40],
            # Connectivity setup
            # 'l23' : [True],
            # 'l5' : [True],
            # 'l6' : [False],
            # 'feedback_l5' : [False],  # l5_exa are sending feedback to L23
            # 'feedback_l6a' : [False],  # cells sending to L4 
            # 'feedback_l6b' : [False],  # cells sending to L5/6 (horizontal feedback to L5)
        },
        simulation_run_name=SIMULATION_NAME,
    ).run_parameter_search()


# TODO:
# base_weight of incoming connections from L23
