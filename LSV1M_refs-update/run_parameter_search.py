# -*- coding: utf-8 -*-
import sys
from mozaik.meta_workflow.parameter_search import CombinationParameterSearch, SlurmSequentialBackend
import numpy
import time


if True:
    CombinationParameterSearch(
        SlurmSequentialBackend(
            num_threads=1, 
            num_mpi=16,
            slurm_options=[
                '--hint=nomultithread',
                # '-w w15',
                '-x w[12-17]',  # exclude nodes
                '-N 1-1',  # ensure minimum 1 node - maximum 1 node is used
            ],
            path_to_mozaik_env='/home/haman/virt_env/layers56new/bin/activate'), 
        {
            'trial' : [1],
        }).run_parameter_search()



