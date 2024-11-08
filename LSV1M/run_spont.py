# -*- coding: utf-8 -*-
"""
This is implementation of model of self-sustained activitity in balanced networks from: 
Vogels, T. P., & Abbott, L. F. (2005). 
Signal propagation and logic gating in networks of integrate-and-fire neurons. 
The Journal of neuroscience : the official journal of the Society for Neuroscience, 25(46), 10786–95. 
"""
import matplotlib
matplotlib.use('Agg')

from mpi4py import MPI
from mozaik.storage.datastore import Hdf5DataStore, PickledDataStore
from parameters import ParameterSet
from analysis_and_visualization import perform_analysis_and_visualization_spont
from model import SelfSustainedPushPull
from experiments import create_experiments_spont
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
        'SelfSustainedPushPull', SelfSustainedPushPull, create_experiments_spont)

    # model.connectors['V1L23ExcL23ExcConnection'].store_connections(data_store)
    # model.connectors['V1L23ExcL23InhConnection'].store_connections(data_store)
    # model.connectors['V1L23InhL23ExcConnection'].store_connections(data_store)
    # model.connectors['V1L23InhL23InhConnection'].store_connections(data_store)

    # model.connectors['V1L23ExcL5InhConnection'].store_connections(data_store)

    # # L5a
    # model.connectors['V1L23ExcL5ExaConnection'].store_connections(data_store)
    # model.connectors['V1L5ExaL5ExaConnection'].store_connections(data_store)
    # model.connectors['V1L5ExaL5InhConnection'].store_connections(data_store)
    # model.connectors['V1L5InhL5ExaConnection'].store_connections(data_store)

    # L5b
    # model.connectors['V1L23ExcL5ExbConnection'].store_connections(data_store)
    # model.connectors['V1L5ExbL5ExbConnection'].store_connections(data_store)
    # model.connectors['V1L5ExbL5InhConnection'].store_connections(data_store)
    # model.connectors['V1L5InhL5ExbConnection'].store_connections(data_store)



    # model.connectors['V1L5InhL5InhConnection'].store_connections(data_store)

    # model.connectors['V1L4ExcL4ExcConnection'].store_connections(data_store)
    # # model.connectors['V1L23ExcL5ExbConnection'].store_connections(data_store)

 
    if False:
        # These Aff Conns should be changed 
        # V1AffL4ExcConnection, V1AffL4InhConnection, V1AffL6ExaConnection,V1AffL6InhConnection
        # not sure how the On, Off is added...

        # model.connectors['V1AffConnectionOn'].store_connections(data_store)
        # model.connectors['V1AffConnectionOff'].store_connections(data_store)
        # model.connectors['V1AffInhConnectionOn'].store_connections(data_store)
        # model.connectors['V1AffInhConnectionOff'].store_connections(data_store)


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

        model.connectors['V1L23ExcL5ExaConnection'].store_connections(data_store)
        # model.connectors['V1L23ExcL5ExbConnection'].store_connections(data_store)
        model.connectors['V1L23ExcL5InhConnection'].store_connections(data_store)

        model.connectors['V1L5ExaL5ExaConnection'].store_connections(data_store)
        model.connectors['V1L5ExaL5InhConnection'].store_connections(data_store)
        model.connectors['V1L5InhL5ExaConnection'].store_connections(data_store)


    data_store.save()
else:
    setup_logging()
    data_store = PickledDataStore(load=True, parameters=ParameterSet(
        {'root_directory': 'SelfSustainedPushPull_test____', 'store_stimuli': False}), replace=True)

if mpi_comm.rank == 0:
    print("Starting visualization")
    perform_analysis_and_visualization_spont(data_store)
