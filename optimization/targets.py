import numpy
import gc

from mozaik.storage.queries import param_filter_query
from utils import *
from math import isclose
from scipy.spatial.distance import cdist
import time

class TargetValue():

    def __init__(self, name, target_value, sheet_name=None, norm=None, max_score=10):
        self.name  = name
        self.target_value = target_value
        self.norm = norm
        self.max_score = max_score
        self.sheet_name = sheet_name
        assert self.norm != 0

    @staticmethod
    def print_feature_results(name, value, score, slurm_id=None, pid=None):
        """Prints the results in formatted way while handling value None"""


        msg = f"[{time.strftime('%D-%H:%M:%S')}] "
        if pid:
            msg += f"PID: {pid}. "
        if slurm_id:
            msg += f"Slurm job: {slurm_id}. "
        if value is None:
            print(msg + f"For feature {name}, for value {value} computed score {score:.2f}")
        else:
            print(msg + f"For feature {name}, for value {value:.4f} computed score {score:.2f}")

    @staticmethod
    def get_orient_cell_idx(orientation, data_store, sheet_name) -> list:
        """Returns the indices of the cells that respond to the given orientation
        
        This function works also for the case when not all neurons are recorded from.
        """
        try:
            seg = TargetValue.filter_spont_stimulus(data_store, sheet_name)[0]
        except IndexError:
            return []
        orientations_cells = get_orientation_preference(data_store, sheet_name).values
        idxs = data_store.get_sheet_indexes(sheet_name, seg.get_stored_spike_train_ids())
        idx_cells = [n for n, idx in enumerate(idxs) if isclose(orientation, orientations_cells[idx], abs_tol=0.1)]
        return idx_cells

    @staticmethod
    def get_spont_rate(data_store, idx_cells, sheet_name):
        try:
            seg = TargetValue.filter_spont_stimulus(data_store, sheet_name)[0]
        except IndexError:
            return None
        return get_mean_rate(seg.spiketrains, idx_cells)
    
    @staticmethod
    def filter_spont_stimulus(data_store, sheet_name):
        seg = param_filter_query(data_store, sheet_name=sheet_name, st_name='InternalStimulus', st_duration=5000).get_segments()
        if len(seg) > 1:
            raise ValueError(f"More than one segment found for spontaneous activity in sheet {sheet_name}.")
        return seg

    def calculate_value(self, data_store, **kwargs):
        raise NotImplementedError

    def calculate_score(self, data_store, slurm_id=None, pid=None, **kwargs):
        if data_store is None:
            return self.max_score
        value = self.calculate_value(data_store)
        if value is None or numpy.isnan(value):
            score = self.max_score
        elif self.norm is not None:
            score = abs(self.target_value - value) / self.norm
        else:
            score = abs(self.target_value - value)
        threshold_score = min(score, self.max_score)
        if numpy.isnan(threshold_score):
            threshold_score = self.max_score
        self.print_feature_results(self.name, value, threshold_score, slurm_id=slurm_id, pid=pid)
        return threshold_score


class OneBoundUpperTarget(TargetValue):
    def calculate_score(self, data_store, slurm_id=None, pid=None, **kwargs):
        if data_store is None:
            return self.max_score
        value = self.calculate_value(data_store)
        if value is None or numpy.isnan(value):
            score = self.max_score
        elif self.norm is not None:
            if value < self.target_value:
                score = abs(self.target_value - value) / self.norm
            else:
                score = 0.
        else:
            if value < self.target_value:
                score = abs(self.target_value - value)
            else:
                score = 0.
        threshold_score = min(score, self.max_score)
        if numpy.isnan(threshold_score):
            threshold_score = self.max_score
        self.print_feature_results(self.name, value, threshold_score, slurm_id=slurm_id, pid=pid)
        return threshold_score


class OneBoundLowerTarget(TargetValue):
    def calculate_score(self, data_store, slurm_id=None, pid=None, **kwargs):
        if data_store is None:
            return self.max_score
        value = self.calculate_value(data_store)
        if value is None or numpy.isnan(value):
            score = self.max_score
        elif self.norm is not None:
            if value > self.target_value:
                score = abs(self.target_value - value) / self.norm
            else:
                score = 0.
        else:
            if value > self.target_value:
                score = abs(self.target_value - value)
            else:
                score = 0.
        threshold_score = min(score, self.max_score)
        if numpy.isnan(threshold_score):
            threshold_score = self.max_score
        self.print_feature_results(self.name, value, threshold_score, slurm_id=slurm_id, pid=pid)
        return threshold_score


class RangeTarget(TargetValue):
    
    def __init__(self, name, target_value, sheet_name=None, norm=None, max_score=10):
        self.name  = name
        self.target_value = target_value
        self.norm = norm
        self.max_score = max_score
        self.sheet_name = sheet_name
        assert self.norm != 0

    def calculate_score(self, data_store, slurm_id=None, pid=None, **kwargs):
        if data_store is None:
            return self.max_score
        value = self.calculate_value(data_store)
        if value is None or numpy.isnan(value):
            score = self.max_score
        elif self.norm is not None:
            if self.target_value[0] < value < self.target_value[1]:
                score = 0
            else:
                low = abs(self.target_value[0] - value) / self.norm
                high = abs(self.target_value[1] - value) / self.norm
                score = numpy.min([low, high])
        else:
            low = abs(self.target_value[0] - value)
            high = abs(self.target_value[1] - value)
            score = numpy.min([low, high])
        threshold_score = min(score, self.max_score)
        if numpy.isnan(threshold_score):
            threshold_score = self.max_score
        self.print_feature_results(self.name, value, threshold_score, slurm_id=slurm_id, pid=pid)
        return threshold_score


class SpontActivityTarget(RangeTarget):
    def calculate_value(self, data_store):

        segments = self.filter_spont_stimulus(data_store, self.sheet_name)
        if not len(segments):
            return None

        spiketrains = segments[0].spiketrains
        return 1000 * numpy.mean([float(len(s) / (s.t_stop - s.t_start)) for s in spiketrains])


class IrregularityTarget(OneBoundUpperTarget):
    def calculate_value(self, data_store):
        
        segments = self.filter_spont_stimulus(data_store, self.sheet_name)
        if not len(segments):
            return None

        spiketrains = segments[0].spiketrains
        isis = [numpy.diff(st.magnitude) for st in spiketrains]
        idxs = numpy.array([len(isi) for isi in isis]) > 5
        value = numpy.mean(numpy.array([numpy.std(isi) / numpy.mean(isi) for isi in isis])[idxs])
        return value


class SynchronyTarget(TargetValue):
    def calculate_value(self, data_store):
        gc.collect()

        segments = self.filter_spont_stimulus(data_store, self.sheet_name)
        if not len(segments):
            return None

        spiketrains = segments[0].spiketrains

        idxs = data_store.get_sheet_indexes(self.sheet_name, segments[0].get_stored_spike_train_ids())
        idx_cells = [n for n, idx in enumerate(idxs)]

        x_pos = data_store.get_neuron_positions()[self.sheet_name][0]
        y_pos = data_store.get_neuron_positions()[self.sheet_name][1]
        radius = 1.5

        # circle
        # spiketrains = [spiketrains[idx] for idx in idx_cells if x_pos[idx]**2 + y_pos[idx]**2 < radius**2]

        # square
        in_square = numpy.maximum(numpy.abs(x_pos), numpy.abs(y_pos)) <= radius
        spiketrains = [spiketrains[idx] for idx in idx_cells if in_square[idx]]


        # spiketrains = segments[0].spiketrains[:2000]
        isis = [numpy.diff(st.magnitude) for st in spiketrains]
        idxs = numpy.array([len(isi) for isi in isis]) > 5
        t_start = round(spiketrains[0].t_start, 5)
        t_stop = round(spiketrains[0].t_stop, 5)
        num_bins = int(round((t_stop - t_start) / 10.))
        r = (float(t_start), float(t_stop))
        psths = [numpy.histogram(x, bins=num_bins, range=r)[0] for x in spiketrains]

        corrs = numpy.nan_to_num(numpy.corrcoef(numpy.squeeze(psths)))
        value = numpy.mean(corrs[idxs, :][:, idxs][numpy.triu_indices(sum(idxs == True), 1)])

        gc.collect()

        return value


class OrientationTuningPreferenceTarget(OneBoundUpperTarget):
    def calculate_value(self, data_store):
        gc.collect()
        # Choose the O to consider
        target_O = numpy.pi / 2
        orthogonal_O = target_O - (numpy.pi / 2)

        # Get the id of the neurons that respond to that orientation target_0
        idx_cells = self.get_orient_cell_idx(target_O, data_store, self.sheet_name)
        if not idx_cells:
            return None

        # Get the rates for the O and the orthogonal
        segments = param_filter_query(data_store, st_name='FullfieldDriftingSinusoidalGrating', sheet_name=self.sheet_name, st_contrast=[100]).get_segments()
        if not len(segments):
            return None

        for seg in segments:
            orientation = get_annotation(seg, "orientation")
            if isclose(orientation, target_O, abs_tol=0.1):
                spike_rate_high = get_mean_rate(seg.spiketrains, idx_cells)
            elif isclose(orientation, orthogonal_O, abs_tol=0.1):
                spike_rate_ortho_high = get_mean_rate(seg.spiketrains, idx_cells)

        gc.collect()

        try:
            return spike_rate_high / spike_rate_ortho_high
        except UnboundLocalError:
            # Variable is not defined - some data is missing 
            # (probably due to explosion)
            return None


class OrientationTuningOrthoHighTarget(TargetValue):
    def calculate_value(self, data_store):
        gc.collect()

        # Choose the O to consider
        target_O = numpy.pi / 2
        orthogonal_O = target_O - (numpy.pi / 2)

        # Get the id of the neurons that respond to that orientation target_0
        idx_cells = self.get_orient_cell_idx(target_O, data_store, self.sheet_name)
        if not idx_cells:
            return None

        # Get the spontaneous rate
        spont_rate = self.get_spont_rate(data_store, idx_cells, self.sheet_name)
        if spont_rate is None:
            return None

        # Get the rates for the O and the orthogonal O high contrast
        segments = param_filter_query(data_store, st_name='FullfieldDriftingSinusoidalGrating', sheet_name=self.sheet_name, st_contrast=[100]).get_segments()
        if not len(segments):
            return None
        for seg in segments:
            orientation = get_annotation(seg, "orientation")
            if isclose(orientation, orthogonal_O, abs_tol=0.1):
                spike_rate_ortho_high = get_mean_rate(seg.spiketrains, idx_cells)
                break

        gc.collect()

        try:
            return numpy.abs(spont_rate - spike_rate_ortho_high)  / spont_rate
        except UnboundLocalError:
            # Variable is not defined - some data is missing 
            # (probably due to explosion)
            return None


class OrientationTuningOrthoLowTarget(TargetValue):
    def calculate_value(self, data_store):
        gc.collect()
    
        # Choose the O to consider
        target_O = numpy.pi / 2
        orthogonal_O = target_O - (numpy.pi / 2)
        
        # Get the id of the neurons that respond to that orientation target_0
        idx_cells = self.get_orient_cell_idx(target_O, data_store, self.sheet_name)
        if not idx_cells:
            return None

        # Get the spontaneous rate
        spont_rate = self.get_spont_rate(data_store, idx_cells, self.sheet_name)
        if spont_rate is None:
            return None

        # Get the rates for the orthogonal O low contrast
        segments = param_filter_query(data_store, st_name='FullfieldDriftingSinusoidalGrating', sheet_name=self.sheet_name, st_contrast=[10]).get_segments()
        if not len(segments):
            return None
        for seg in segments:
            orientation = get_annotation(seg, "orientation")
            if isclose(orientation, orthogonal_O, abs_tol=0.1):
                spike_rate_ortho_low = get_mean_rate(seg.spiketrains, idx_cells)
                break

        gc.collect()

        try:
            return numpy.abs(spont_rate - spike_rate_ortho_low) / spont_rate
        except UnboundLocalError:
            # Variable is not defined - some data is missing 
            # (probably due to explosion)
            return None


class SizeTuning(OneBoundUpperTarget):
    def calculate_value(self, data_store):
        """Compute the percentage of cells that show a suppression above +20%"""

        gc.collect()

        # Choose the O to consider
        target_O = numpy.pi / 2

        # Get the id of the neurons that respond to that orientation target_0
        idx_cells = self.get_orient_cell_idx(target_O, data_store, self.sheet_name)
        if not idx_cells:
            return None

        x_pos = data_store.get_neuron_positions()[self.sheet_name][0]
        y_pos = data_store.get_neuron_positions()[self.sheet_name][1]
        radius = 1

        idx_cells = [idx for idx in idx_cells if x_pos[idx]**2 + y_pos[idx]**2 < radius**2]

        # Get the firing rates for the full field gratings at high contrast
        segments = param_filter_query(
            data_store, st_name='FullfieldDriftingSinusoidalGrating', sheet_name=self.sheet_name, st_contrast=[100]
        ).get_segments()
        if not len(segments):
            return None
        for seg in segments:
            orientation = get_annotation(seg, "orientation")
            if isclose(orientation, target_O, abs_tol=0.1):
                full_field_rates = [len(seg.spiketrains[idx]) for idx in idx_cells]
                break

        # Get the firing rates for the small grating disk at high contrast
        segments = param_filter_query(
            data_store, st_name='DriftingSinusoidalGratingDisk', sheet_name=self.sheet_name, st_contrast=[100]
        ).get_segments()
        if not len(segments):
            return None
        for seg in segments:
            orientation = get_annotation(seg, "orientation")
            if isclose(orientation, target_O, abs_tol=0.1):
                small_disk_rates = [len(seg.spiketrains[idx]) for idx in idx_cells]
                break

        gc.collect()

        suppression_index = []
        for small_rate, full_rate in zip(small_disk_rates, full_field_rates):
            if small_rate > 2. and full_rate > 0.:
                _suppression = small_rate / full_rate
                if _suppression > 1.1:
                    suppression_index.append(_suppression)

        return len(suppression_index) / len(idx_cells)
