from mpi4py import MPI
from pyNN import nest
import nest
import numpy

from mozaik.experiments import *
from mozaik.experiments.vision import *
from parameters import ParameterSet
from mozaik.controller import run_workflow

from model import SelfSustainedPushPull



class MeasureSizeTuningOneSize(VisualExperiment):

    required_parameters = ParameterSet({
            'size' : float,
            'orientations' : list,
            'positions' : list,
            'spatial_frequency' : float,
            'temporal_frequency' : float,
            'grating_duration' : float,
            'contrasts' : list,
            'num_trials' : int
    })

    def generate_stimuli(self):

        stimulus_parameters = []
        # stimuli creation        
        for c in self.parameters.contrasts:
            for o in self.parameters.orientations:
                for x, y in self.parameters.positions:
                    for k in range(0, self.parameters.num_trials):
                        self.stimuli.append(topo.DriftingSinusoidalGratingDisk(
                                frame_duration = self.frame_duration,
                                size_x=self.model.visual_field.size_x,
                                size_y=self.model.visual_field.size_y,
                                location_x=x,
                                location_y=y,
                                background_luminance=self.background_luminance,
                                contrast=c,
                                duration=self.parameters.grating_duration,
                                density=self.density,
                                trial=k,
                                orientation=o,
                                radius=self.parameters.size,
                                spatial_frequency=self.parameters.spatial_frequency,
                                temporal_frequency=self.parameters.temporal_frequency))

    def do_analysis(self, data_store):
        pass


def create_experiments(model):

    spont_short = NoStimulation(model, ParameterSet({"duration": 500}))

    spont = NoStimulation(model, ParameterSet({"duration": 5000}))

    orientation_tuning = MeasureOrientationTuningFullfield(model, ParameterSet(
    {
        'num_orientations': 2,
        'spatial_frequency': 0.8,
        'temporal_frequency': 2,
        'grating_duration': 2000,
        'contrasts': [10, 100],
        'num_trials': 1,
        'shuffle_stimuli': True
    }))

    size_tuning = MeasureSizeTuningOneSize(model, ParameterSet(
    {
        'size': 1.25,
        'orientations': [numpy.pi / 2.],
        'positions': [(0,0)],
        'spatial_frequency': 0.8,
        'temporal_frequency': 2,
        'grating_duration': 2000,
        'contrasts': [100],
        'num_trials': 1,
        'shuffle_stimuli': True
    }))

    return [spont_short, spont, orientation_tuning, size_tuning]


mpi_comm = MPI.COMM_WORLD

nest.Install("stepcurrentmodule")

data_store, model = run_workflow('SelfSustainedPushPull', SelfSustainedPushPull, create_experiments)
