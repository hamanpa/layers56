import gc
import numpy
import glob
import pickle
import time
import matplotlib.pyplot as plt
from pathlib import Path
import ast

from parameters import ParameterSet
from mozaik.storage.datastore import PickledDataStore
from mozaik.storage.queries import *
from mozaik.analysis.technical import NeuronAnnotationsToPerNeuronValues
from mozaik.tools.distribution_parametrization import MozaikExtendedParameterSet


class PickledSegment():

    def __init__(self, segment, sheet):

        self.spiketrains = [numpy.array(s) for s in segment.spiketrains]
        self.sheet = sheet
        self.annotation = eval(segment.annotations['stimulus'])

        self.t_start = segment.spiketrains[0].t_start
        self.t_stop = segment.spiketrains[0].t_stop
        self.duration = segment.spiketrains[0].t_stop - segment.spiketrains[0].t_start

        self.mean_rate = 1000. *  numpy.mean([len(s) for s in self.spiketrains]) / self.duration


def datastore_to_pickle(run_id, sheet_name, export_folder='./pickled_datastore'):

    Path(f'./{export_folder}').mkdir(parents=True, exist_ok=True)
    export_path = f"./{export_folder}/{run_id}_{sheet_name.replace('/', '')}.pkl"

    if Path(export_path).is_file():
        print(f"Did not pickle {run_id} because it has already been pickled")
        return 

    data_stores = get_data_stores(run_id)

    if not data_stores:
        print(f"Did not pickle {run_id} because the datastore does not exist")
        return

    data_store = data_stores[0]

    print(f"Pickling {run_id}, sheet {sheet_name}")
    export_data = []

    t1 = time.time()
    data_view = param_filter_query(data_store, sheet_name=sheet_name)
    segments = data_view.get_segments()

    for idx_seg, segment in enumerate(segments):
        print(idx_seg, '/', len(segments), end =" , ")
        export_data.append(PickledSegment(segment, sheet_name))
    print()

    print(f"Took {time.time() - t1}s for {len(export_data)} segments")

    with open(export_path, 'wb') as file:
        pickle.dump(export_data, file)

    gc.collect()


def read_pickled_datastore(run_id, sheet_name):
    with open(f"./pickled_datastore/{run_id}_{sheet_name.replace('/', '')}.pkl", 'rb') as file:
        pickled_datastore = pickle.load(file)
    return pickled_datastore


def get_data_store(path):

    parameters = ParameterSet(
            {'root_directory': path,
             'store_stimuli': False}
    )

    print(f"Reading folder {path}")
    try:
        data_store = PickledDataStore(
                load=True,
                parameters=parameters,
                replace=True
            )
    except:
        return None

    return data_store


def get_data_stores(run_id, absolute_path=False):

    data_stores = []
    if absolute_path:
        _folders = glob.glob(f"{run_id}*")
    else:
        _folders = glob.glob(f"./{run_id}*")
    if _folders is None or len(_folders) == 0:
        print(f"FOLDER {run_id} NOT FOUND")
        return data_stores

    sub_folders = glob.glob(glob.escape(_folders[0]) + "/SelfSustainedPushPull*")

    for subf in sub_folders:
        ds = get_data_store(subf)
        if ds is not None:
            data_stores.append(ds)

    return data_stores


def get_annotation(segment, key):
    return eval(segment.annotations['stimulus'])[key]


def get_spiketrains_duration(spiketrains):
    t_start = spiketrains[0].t_start
    t_stop = spiketrains[0].t_stop
    return t_stop - t_start


def get_mean_rate(spiketrains, filter_idx=None):
    if filter_idx is not None:
        spike_count = numpy.mean([len(spiketrains[idx]) for idx in filter_idx]) 
    else:
        spike_count = numpy.mean([len(spiketrains[idx]) for idx in filter_idx]) 
    return 1000. * spike_count / get_spiketrains_duration(spiketrains)


def get_ICMS_analysis_results(population_name, data_store):
    data_view_ICMS = param_filter_query(data_store, sheet_name=population_name)
    return data_view_ICMS.get_analysis_result()


def get_ICMS_position_data(sheet_name, data_store, amplitude=None, frequency=None, active_electrodes=None):
    analysis_results = get_ICMS_analysis_results(sheet_name, data_store)

    cells_positions = data_store.get_neuron_positions()[sheet_name]
    cells_positions = numpy.array([cells_positions[0] * 1000, cells_positions[1] * 1000, cells_positions[2]])

    _act_elec = '_'.join(str(e) for e in active_electrodes)
    if (frequency).is_integer():
        metadata = f"__{amplitude}__{int(frequency)}__{_act_elec}"
    else:
        metadata = f"__{amplitude}__{frequency}__{_act_elec}"
    probe_positions = next((data for data in analysis_results if 'probe_electrode_positions' + metadata in data.value_name), None)
    if probe_positions is None:
        raise Exception("The metadata was not found in the data store analysis results")
    
    electrode_active_per_cell = next(data for data in analysis_results if 'electrode_active_per_cell' + metadata == data.value_name)

    return probe_positions, cells_positions.T, electrode_active_per_cell


def get_orientation_preference(data_store, sheet_name):
    try:
        orientations = data_store.get_analysis_result(
            identifier='PerNeuronValue',
            value_name=['LGNAfferentOrientation', 'ORMapOrientation'],
            sheet_name=sheet_name
        )[0]
    except:
        NeuronAnnotationsToPerNeuronValues(data_store, ParameterSet({})).analyse()
        orientations = data_store.get_analysis_result(
            identifier='PerNeuronValue',
            value_name=['LGNAfferentOrientation', 'ORMapOrientation'],
            sheet_name=sheet_name
        )[0]

    return orientations


def make_dir(path_dir):
    """Creates directory if it does not exist"""
    p = Path(path_dir)
    if not (p.is_dir()):
        p.mkdir(parents=True, exist_ok=True)
