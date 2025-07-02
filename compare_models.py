"""
Goal of this script is to compare results between two model


"""

import numpy as np
import os
from mozaik.storage.queries import *
from mozaik.storage.datastore import PickledDataStore
from mozaik.tools.distribution_parametrization import PyNNDistribution
from parameters import ParameterSet

import matplotlib.pyplot as plt
from pathlib import Path

PAPER_MODEL = '/home/haman/layers56/LSV1M_paper/'  # Data from Remys model
REF_MODEL = '/home/haman/layers56/LSV1M_refs-update/'  # Data from referenced model

SPONT = '20241129-Spont/SelfSustainedPushPull_ParameterSearch_____trial:1'
SIZE = '20241129-SizeTuning/SelfSustainedPushPull_ParameterSearch_____trial:1'
ORIENT = '20241129-OrientTuning/SelfSustainedPushPull_ParameterSearch_____trial:1'


def load_datastore(base_dir):
    return PickledDataStore(
        load=True,
        parameters=ParameterSet(
            {"root_directory": base_dir, "store_stimuli": False}
        ),
        replace=False,
    )

def get_segments(data_store, sheet_name=None):
    """
    Returns a list of segments in the DataStore, ordered by their identifier.
    Optionally filters the segments for results from a specific sheet.

    Parameters
    ----------

    data_store : Datastore to retrieve segments from
    sheet_name : name of neuron sheet (layer) to retrieve the recorded segments for

    Returns
    -------
    A list of all segments in a DataStore, optionally filtered for sheet name.
    """
    dsv = param_filter_query(
        data_store, st_name="EndOfSimulationBlank", negative=True
    )

    if sheet_name is None:
        # If no sheet name specified, load all sheets
        return dsv.get_segments()
    else:
        return sorted(
            param_filter_query(dsv, sheet_name=sheet_name).get_segments(),
            key=lambda x: x.identifier,
        )

def get_voltages(data_store, sheet_name=None, max_neurons=None):
    """
    Returns the recorded membrane potentials for neurons recorded in the DataStore,
    ordered by segment identifiers and neuron ids, flattened into a single 1D vector.
    Can be optionally filtered for neuron sheet, and maximum number of neurons.

    Parameters
    ----------

    data_store : Datastore to retrieve voltages from
    sheet_name : name of neuron sheet (layer) to retrieve the recorded voltages from
    max_neurons : maximum number of neurons to get the voltages for

    Returns
    -------
    A 1D list of membrane potential voltages recorded in neurons in the DataStore
    """

    segments = get_segments(data_store, sheet_name)
    return [
        v
        for segment in segments
        for neuron_id in sorted(segment.get_stored_vm_ids())[:max_neurons]
        for v in segment.get_vm(neuron_id).flatten()
    ]

def get_spikes(data_store, sheet_name=None, max_neurons=None):
    """
    Returns the recorded spike times for neurons recorded in the DataStore,
    ordered by segment identifiers and neuron ids, flattened into a single 1D vector.
    Can be optionally filtered for neuron sheet, and maximum number of neurons.

    Parameters
    ----------

    data_store : Datastore to retrieve spike times from
    sheet_name : name of neuron sheet (layer) to retrieve the recorded spike times from
    max_neurons : maximum number of neurons to get spike times for

    Returns
    -------
    A 1D list of spike times recorded in neurons in the DataStore
    """
    segments = get_segments(data_store, sheet_name)
    return [
        v
        for segment in segments
        for neuron_id in sorted(segment.get_stored_spike_train_ids())[:max_neurons]
        for v in segment.get_spiketrain(neuron_id).flatten()
    ]

def check_spikes(ds0, ds1, sheet_name=None, max_neurons=None):
    """
    Check if spike times recorded in two DataStores are equal. Spike times are merged
    into a single 1D array and compared using numpy assertions.
    Can be optionally filtered for neuron sheet, and maximum number of neurons.

    Parameters
    ----------

    ds0, ds1 : DataStores to retrieve spike times from
    sheet_name : name of neuron sheet (layer) to check spike times for
    max_neurons : maximum number of neurons to check spike times for
    """
    np.testing.assert_equal(
        get_spikes(ds0, sheet_name, max_neurons),
        get_spikes(ds1, sheet_name, max_neurons),
    )

def check_voltages(ds0, ds1, sheet_name=None, max_neurons=None):
    """
    Check if membrane potential voltages recorded in two DataStores are equal. Voltages
    are merged into a single 1D array and compared using numpy assertions.
    Can be optionally filtered for neuron sheet, and maximum number of neurons.

    Parameters
    ----------

    ds0, ds1 : DataStores to retrieve spike times from
    sheet_name : name of neuron sheet (layer) to check voltages for
    max_neurons : maximum number of neurons to check voltages for
    """

    print(len(get_voltages(ds0, sheet_name, max_neurons)), flush=True)
    print(len(get_voltages(ds1, sheet_name, max_neurons)), flush=True)
    np.testing.assert_equal(
        get_voltages(ds0, sheet_name, max_neurons),
        get_voltages(ds1, sheet_name, max_neurons),
    )

def main():
    for experiment in [SPONT, SIZE, ORIENT]:
        print(experiment.split('/')[0].split('-')[1])
        paper = load_datastore(PAPER_MODEL + experiment)
        ref = load_datastore(REF_MODEL + experiment)
        for sheet in ["V1_Exc_L4", "V1_Inh_L4", "V1_Exc_L2/3", "V1_Inh_L2/3"]:
            print(sheet)
            check_voltages(paper, ref, sheet, max_neurons=25)
            print("Voltages OK")
            check_spikes(paper, ref, sheet, max_neurons=25)
            print("Spikes OK")

if __name__ == '__main__':
    main()