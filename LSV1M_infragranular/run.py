# -*- coding: utf-8 -*-
"""
This is implementation of model of corresponding to the pre-print `Large scale model of cat primary visual cortex`
Antolík, J., Cagnol, R., Rózsa, T., Monier, C., Frégnac, Y., & Davison, A. P. (2018).
https://www.biorxiv.org/content/10.1101/416156v5.abstract
"""
import matplotlib
matplotlib.use('Agg')

from mpi4py import MPI
from mozaik.storage.datastore import Hdf5DataStore, PickledDataStore
from parameters import ParameterSet
from analysis_and_visualization import perform_analysis_and_visualization
from model import SelfSustainedPushPull
from experiments import create_experiments
import mozaik
from mozaik.controller import run_workflow, setup_logging
import mozaik.controller
import sys
from pyNN import nest

from mpi4py import MPI

mpi_comm = MPI.COMM_WORLD

import nest
nest.Install("stepcurrentmodule")

if True:
    data_store, model = run_workflow(
        'SelfSustainedPushPull', SelfSustainedPushPull, create_experiments)

    model.connectors['V1L23ExcL5ExaConnection'].store_connections(data_store)
    model.connectors['V1L23ExcL5ExbConnection'].store_connections(data_store)
    model.connectors['V1L23ExcL5InhConnection'].store_connections(data_store)

    if False:
        model.connectors['V1AffConnectionOn'].store_connections(data_store)
        model.connectors['V1AffConnectionOff'].store_connections(data_store)
        model.connectors['V1AffInhConnectionOn'].store_connections(data_store)
        model.connectors['V1AffInhConnectionOff'].store_connections(data_store)
        model.connectors['V1L4ExcL4ExcConnection'].store_connections(
            data_store)
        model.connectors['V1L4ExcL4InhConnection'].store_connections(
            data_store)
        model.connectors['V1L4InhL4ExcConnection'].store_connections(
            data_store)
        model.connectors['V1L4InhL4InhConnection'].store_connections(
            data_store)
        model.connectors['V1L23ExcL23ExcConnection'].store_connections(
            data_store)
        model.connectors['V1L23ExcL23InhConnection'].store_connections(
            data_store)
        model.connectors['V1L23InhL23ExcConnection'].store_connections(
            data_store)
        model.connectors['V1L23InhL23InhConnection'].store_connections(
            data_store)
        model.connectors['V1L4ExcL23ExcConnection'].store_connections(data_store)
        model.connectors['V1L4ExcL23InhConnection'].store_connections(data_store)
    data_store.save()
else:
    setup_logging()
    data_store = PickledDataStore(load=True, parameters=ParameterSet(
        {'root_directory': 'SelfSustainedPushPull_test____', 'store_stimuli': False}), replace=True)

if mpi_comm.rank == 0 and not data_store.block.annotations["simulation_log"]["explosion_detected"]:
    print("Starting visualization")
    perform_analysis_and_visualization(data_store)
    print("Finished")

