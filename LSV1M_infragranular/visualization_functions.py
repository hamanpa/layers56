import pylab
import numpy

import mozaik.storage.queries as queries
import matplotlib.gridspec as gridspec
from mozaik.visualization.plotting import Plotting
from mozaik.visualization.helper_functions import *
from parameters import ParameterSet
from mozaik.storage.queries import *
from mozaik.analysis.analysis import *
from mozaik.controller import Global
from mozaik.visualization.plotting import (Plotting, GSynPlot, RasterPlot, PerNeuronAnalogSignalScatterPlot,
                                           VmPlot, ConductanceSignalListPlot, ScatterPlot,
                                           AnalogSignalListPlot, OverviewPlot, PerNeuronValueScatterPlot, PlotTuningCurve, PerNeuronValuePlot, CorticalColumnRasterPlot)
from mozaik.visualization.simple_plot import *

from mozaik.tools.circ_stat import circular_dist
import mozaik.visualization.helper_functions as phf

import mozaik
logger = mozaik.getMozaikLogger()

low_contrast=10
ttcc_contrast=30
high_contrast=100

class SpontActOverviewAllLayers(Plotting):

    """
    This figure shows example of spontaneous activity in the model. 
      
    Parameters
    ----------
    l4_exc_neuron : str
               The name of the sheet corresponding to layer 4 excitatory neurons.
              
    l23_exc_neuron : str
          The name of the sheet corresponding to layer 2/3 excitatory neurons.


    l4_inh_neuron : str
               The name of the sheet corresponding to layer 4 inhibitory neurons.
              
    l23_inh_neuron : str
          The name of the sheet corresponding to layer 2/3 inhibitory neurons.

    """

    required_parameters = ParameterSet({
        'l4_exc_neuron' : int,
        'l4_inh_neuron' : int,
        'l23_exc_neuron' : int,
        'l23_inh_neuron' : int,
        'l5_exa_neuron' : int,
        'l5_exb_neuron' : int,
        'l5_inh_neuron' : int,
        'l6_exa_neuron' : int,
        'l6_exb_neuron' : int,
        'l6_inh_neuron' : int,
    })

    def subplot(self, subplotspec):
        # May not work if there are sheets for which no spikes are recorded!!!

        sheets = [x for x in self.datastore.sheets() if 'V1' in x]
        sheets = sorted(sheets,key=lambda x: x.split("_")[2] + x.split("_")[1])
        # sheets = []
        # if self.parameters.l23_exc_neuron != -1:
        #     sheets.append('V1_Exc_L2/3')
        #     sheets.append('V1_Inh_L2/3')
        # if self.parameters.l4_exc_neuron != -1:
        #     sheets.append('V1_Exc_L4')
        #     sheets.append('V1_Inh_L4')
        # if self.parameters.l5_exa_neuron != -1:
        #     sheets.append('V1_Exa_L5')
        #     sheets.append('V1_Exb_L5')
        #     sheets.append('V1_Inh_L5')
        # if self.parameters.l6_exa_neuron != -1:
        #     sheets.append('V1_Exa_L6')
        #     sheets.append('V1_Exb_L6')
        #     sheets.append('V1_Inh_L6')
        
        analog_ids1 = sorted(numpy.random.permutation(queries.param_filter_query(self.datastore,sheet_name=sheets[0]).get_segments()[0].get_stored_esyn_ids()))
        tstop = queries.param_filter_query(self.datastore,st_direct_stimulation_name=None,st_name="InternalStimulus",sheet_name = sheets[0]).get_segments()[0].get_vm(analog_ids1[0]).t_stop.magnitude
        tstop = min(5000,tstop)

        spike_ids = dict()
        for sheet in sheets:
            spike_ids[sheet] = param_filter_query(self.datastore,sheet_name=sheet).get_segments()[0].get_stored_spike_train_ids()

        def parse_densities(param_str, relative_sheet='V1_Inh_L4'):
            """
            density_fractions = {
                'V1_Exc_L2/3' : 3.86,
                'V1_Inh_L2/3' : 0.965,
                'V1_Exc_L4' : 4,
                'V1_Inh_L4' : 1,
                'V1_Exa_L5' : 0.164,
                'V1_Exb_L5' : 0.656,
                'V1_Inh_L5' : 0.205,
                'V1_Exa_L6' : 1.18,
                'V1_Exb_L6' : 1.18,
                'V1_Inh_L6' : 0.59,
            }
            """
            import re

            pattern = r'"name"\s*:\s*"(V1_\w*_L[\w/]*)"[\w\W]*?"density"\s*:\s*([\d.]+)'
            matches = re.findall(pattern, param_str)
            density_fracs = {}
            for key, val in matches:
                density_fracs[key] = float(val)
            weight = density_fracs[relative_sheet]
            for key in density_fracs:
                density_fracs[key] = density_fracs[key] / weight

            return density_fracs


        density_fractions = parse_densities(self.datastore.get_model_parameters())
        max_number_of_spikes = 100

        spikes = [max_number_of_spikes]
        for sheet in sheets:
            spikes.append(numpy.floor(len(spike_ids[sheet])/density_fractions[sheet]))
        d = int(numpy.min(spikes))
        neuron_ids = []
        for sheet in sheets:
                num_spikes = int(d*density_fractions[sheet])
                neuron_ids.append(spike_ids[sheet][:num_spikes])

        colors = []
        labels = []
        for sheet in sheets:
            label = sheet.split('_')[2] + sheet.split('_')[1]
            labels.append(label)
            if 'Inh' in sheet:
                colors.append('#0000FF')
            elif 'Exb' in sheet:
                colors.append('#FF7777')
            else:
                colors.append('#FF0000')
            
        plots = {}
        height = len(sheets)*3
        gs = gridspec.GridSpecFromSubplotSpec(height,3, subplot_spec=subplotspec,hspace=0.3, wspace=0.45)
        fontsize=14

        dsv = param_filter_query(self.datastore,st_direct_stimulation_name=None,st_name=['InternalStimulus'])

        plots['SpikingOverview'] = (CorticalColumnRasterPlot(dsv,ParameterSet({'spontaneous' : False, 'sheet_names' : sheets[::-1], 'neurons' : neuron_ids[::-1], 'colors' : colors[::-1], 'labels' : labels[::-1]})),gs[:,0],{'fontsize' : fontsize,'x_lim' : (0,tstop/1000)})
        max_i = len(sheets) -1
        for i, sheet in enumerate(sheets):
            neuron_name = sheet.lower().replace('/','')
            neuron_name = neuron_name.split('_')[2] + '_' + neuron_name.split('_')[1]
            neuron = eval('self.parameters.' + neuron_name + '_neuron')
            if i < max_i:
                # 'separated' : False merges the two plots in one
                plots[sheet + 'Cond'] = (GSynPlot(dsv, ParameterSet({'sheet_name' : sheet, 'neuron' : neuron, 'separated' : True, 'spontaneous' : False})),gs[i*3:i*3+2,1:],{'x_label': None,'fontsize' : fontsize, 'x_ticks' : [],'title' : None,'x_lim' : (0,tstop),'y_lim' : (0,15),'y_axis' : None})
                plots[sheet + 'Vm'] = (VmPlot(dsv, ParameterSet({'sheet_name' : sheet, 'neuron' : neuron, 'spontaneous' : False})),gs[i*3+2,1:],{'x_label': None,'fontsize' : fontsize, 'x_ticks' : [],'title' : None,'x_lim' : (0,tstop), 'y_ticks' : [], 'y_label' : labels[i]}) 
            else:
                plots[sheet + 'Cond'] = (GSynPlot(dsv, ParameterSet({'sheet_name' : sheet, 'neuron' : neuron, 'separated' : True, 'spontaneous' : False})),gs[i*3:i*3+2,1:],{'x_label': None,'fontsize' : fontsize, 'x_ticks' : [],'title' : None,'x_lim' : (0,tstop),'y_lim' : (0,15)})
                plots[sheet + 'Vm'] = (VmPlot(dsv, ParameterSet({'sheet_name' : sheet, 'neuron' : neuron, 'spontaneous' : False})),gs[i*3+2,1:],{'fontsize' : fontsize, 'title' : None,'x_lim' : (0,tstop)})
                
        return plots

class SpontStatisticsOverviewAllLayers(Plotting):
    """This class is similar to SpontStatisticsOverview but plots all layers.
    
    """
    required_parameters = ParameterSet({

    })

    def subplot(self, subplotspec):

        dsv = param_filter_query(self.datastore,st_direct_stimulation_name=None,st_name=['InternalStimulus'])    
        
        all_sheets = [
            'V1_Exc_L2/3', 
            'V1_Inh_L2/3', 
            'V1_Exc_L4', 
            'V1_Inh_L4', 
            'V1_Exa_L5', 
            'V1_Exb_L5', 
            'V1_Inh_L5', 
            'V1_Exa_L6', 
            'V1_Exb_L6', 
            'V1_Inh_L6'
        ]

        sheets = []
        for result in param_filter_query(self.datastore,st_direct_stimulation_name=None,st_name='InternalStimulus',analysis_algorithm='PopulationMeanAndVar',identifier='SingleValue',value_name='Mean(Firing rate)').get_analysis_result():
            sheets.append(result.sheet_name)



        spike_ids = dict()
        idx = dict()
        for sheet in sheets:
            spike_ids[sheet] = numpy.array(param_filter_query(self.datastore,sheet_name=sheet).get_segments()[0].get_stored_spike_train_ids())
            idx[sheet] = self.datastore.get_sheet_indexes(sheet_name=sheet,neuron_ids=spike_ids[sheet])            

        # center neurons
        x = dict()
        y = dict()
        center = dict()
        for sheet in sheets:
            x[sheet] = self.datastore.get_neuron_positions()[sheet][0][idx[sheet]]
            y[sheet] = self.datastore.get_neuron_positions()[sheet][1][idx[sheet]]
            center[sheet] = spike_ids[sheet][numpy.nonzero(numpy.sqrt(numpy.multiply(x[sheet],x[sheet])+numpy.multiply(y[sheet],y[sheet])) < 0.5)[0]]

        mean_and_std = lambda x : (numpy.mean(x), numpy.std(x))

        mean_firing_rate = dict()
        std_firing_rate = dict()
        
        mean_cv = dict()
        std_cv = dict()
        
        mean_cc = dict()
        std_cc = dict()

        mean_vm = dict()
        std_vm = dict()

        mean_cond_e = dict()
        std_cond_e = dict()

        mean_cond_i = dict()
        std_cond_i = dict()

        for sheet in sheets:
            mean_firing_rate[sheet] = param_filter_query(self.datastore, st_direct_stimulation_name=None, st_name='InternalStimulus', analysis_algorithm='PopulationMeanAndVar', sheet_name=sheet, identifier='SingleValue', value_name='Mean(Firing rate)', ads_unique=True).get_analysis_result()[0].value
            std_firing_rate[sheet] = numpy.sqrt(param_filter_query(self.datastore, st_direct_stimulation_name=None, st_name='InternalStimulus', analysis_algorithm='PopulationMeanAndVar',sheet_name=sheet ,identifier='SingleValue',value_name='Var(Firing rate)',ads_unique=True).get_analysis_result()[0].value)

            s = queries.param_filter_query(self.datastore, st_name='InternalStimulus', sheet_name=sheet).get_segments()[0]
            isis = [numpy.diff(st.magnitude) for st in s.spiketrains]  # InterSpike Intervals
            idxs = numpy.array([len(isi) for isi in isis]) > 5
            mean_cv[sheet], std_cv[sheet] = mean_and_std(numpy.array([numpy.std(isi)/numpy.mean(isi) for isi in isis])[idxs])

            s = queries.param_filter_query(self.datastore, st_name='InternalStimulus', sheet_name=sheet, value_name='Correlation coefficient(psth (bin=10.0))', ads_unique=True).get_analysis_result()[0]
            mean_cc[sheet], std_cc[sheet] = mean_and_std(numpy.array(s.values)[idxs, :][:, idxs][numpy.triu_indices(sum(idxs == True), 1)])

            mean_vm[sheet], std_vm[sheet] = mean_and_std(param_filter_query(self.datastore, sheet_name=sheet, st_direct_stimulation_name=None, st_name=['InternalStimulus'], analysis_algorithm='Analog_MeanSTDAndFanoFactor', value_name='Mean(VM)', ads_unique=True).get_analysis_result()[0].values)

            mean_cond_e[sheet], std_cond_e[sheet] = mean_and_std(param_filter_query(self.datastore,sheet_name=sheet,st_direct_stimulation_name=None,st_name=['InternalStimulus'],analysis_algorithm='Analog_MeanSTDAndFanoFactor',value_name='Mean(ECond)',ads_unique=True).get_analysis_result()[0].values)
            mean_cond_e[sheet], std_cond_e[sheet] = mean_cond_e[sheet] * 1000, std_cond_e[sheet] * 1000
            mean_cond_i[sheet], std_cond_i[sheet] = mean_and_std(param_filter_query(self.datastore,sheet_name=sheet,st_direct_stimulation_name=None,st_name=['InternalStimulus'],analysis_algorithm='Analog_MeanSTDAndFanoFactor',value_name='Mean(ICond)',ads_unique=True).get_analysis_result()[0].values)
            mean_cond_i[sheet], std_cond_i[sheet] = mean_cond_i[sheet] * 1000, std_cond_i[sheet] * 1000
        for name, variable in zip(
            ['Mean firing rate', 'Mean CC', 'Mean CV', 'Mean Vm', 'Mean excitatory conductance', 'Mean inhibitory conductance'],
            [mean_firing_rate, mean_cc, mean_cv, mean_vm, mean_cond_e, mean_cond_i]):
            for sheet in sheets:
                logger.info(f'{name} of {sheet} : {mean_firing_rate[sheet]}')

        # Not sure why the weights are 0.25 for inhibitory layers
        mean_ECond = 0
        mean_ICond = 0
        total_weight = 0
        for sheet in sheets:
            if 'Inh' in sheet:
                weight = 0.25
            else:
                weight = 1
            mean_ECond += mean_cond_e[sheet] * weight
            mean_ICond += mean_cond_i[sheet] * weight
            total_weight += weight 
        mean_ECond = mean_ECond / total_weight
        mean_ICond = mean_ECond / total_weight

        logger.info(f'mean_ECond : {mean_ECond}')
        logger.info(f'mean_ICond : {mean_ICond}')

        def autolabel(rects,offset=0.35):
            # attach some text labels
            for rect in rects:
                height = rect.get_width()
                pylab.gca().text(rect.get_x() + rect.get_width() + abs(pylab.gca().get_xlim()[0] - pylab.gca().get_xlim()[1])*offset, rect.get_y()+0.012,
                        '%.2g' % float(height),
                        ha='center', va='bottom',fontsize=17)

        def barh_plot(gs, mean_data, std_data, label, fontsize, xmax=None, xmin=0, offset=0.35):
            width = 0.12
            bar_gap = 0.16  # width*4/3
            layer_gap = 0.34

            sheets = [
                'V1_Exc_L2/3', 
                'V1_Inh_L2/3', 
                'V1_Exc_L4', 
                'V1_Inh_L4', 
                'V1_Exa_L5', 
                'V1_Exb_L5', 
                'V1_Inh_L5', 
                'V1_Exa_L6', 
                'V1_Exb_L6', 
                'V1_Inh_L6'
            ]

            sheet_vals = numpy.zeros(len(sheets))
            sheet_val = 0
            for i, sheet in enumerate(sheets):
                sheet_vals[i] = sheet_val
                if 'Inh' in sheet:
                    sheet_val -= layer_gap
                else:
                    sheet_val -= bar_gap    
            sheet_vals = sheet_vals - sheet_vals[-1] + 0.17
            sheet_vals = dict(zip(sheets, numpy.round(sheet_vals, 2)))

            sheet_ticks = [0.33, 0.99, 1.57, 2.07]

            pylab.subplot(gs)
            plts = []
            for sheet in mean_data.keys():
                if 'Inh' in sheet:
                    color = '#FFFFFF'
                else:
                    color = '#000000'
                plts.append(pylab.barh(sheet_vals[sheet], numpy.abs(mean_data[sheet]), height=width, color=color, edgecolor='#000000', xerr=std_data[sheet], error_kw=dict(ecolor='gray', lw=2, capsize=5, capthick=2)))

            pylab.ylim(0,2.3) 
            if xmax:
                pylab.xlim(xmin, xmax)
            else:
                xmax = 0
                for value in mean_data.values():
                    if numpy.abs(value).max() > xmax:
                        xmax = numpy.abs(value).max()
                pylab.xlim(xmin, xmax*1.3)

            pylab.yticks(sheet_ticks, ['L6', 'L5', 'L4', 'L2/3'])
            pylab.xlabel(label, fontsize=fontsize)
            
            phf.three_tick_axis(pylab.gca().xaxis)
            for label in pylab.gca().get_xticklabels() + pylab.gca().get_yticklabels():
                label.set_fontsize(fontsize)
            phf.disable_top_right_axis(pylab.gca())

            for plot in plts:
                autolabel(plot, offset=offset)

        def plot_with_log_normal_fit(values,gs1,gs2,x_label=False,y_label=""):
            valuesnz = values[numpy.nonzero(values)[0]]
            h,bin_edges = numpy.histogram(numpy.log10(valuesnz),range=(-2,2),bins=20,density=True)
            bin_centers = bin_edges[:-1] + (bin_edges[1:] - bin_edges[:-1])/2.0
            
            m = numpy.mean(numpy.log10(valuesnz))
            nm = numpy.mean(valuesnz)
            s = numpy.std(numpy.log10(valuesnz))
            if s == 0: 
               s=1.0

            pylab.subplot(gs1)
            pylab.plot(numpy.logspace(-2,2,100),numpy.exp(-((numpy.log10(numpy.logspace(-2,2,100))-m)**2)/(2*s*s))/(s*numpy.sqrt(2*numpy.pi)),linewidth=4,color="#666666")
            pylab.plot(numpy.power(10,bin_centers),h,'ko',mec=None,mew=3)
            pylab.xlim(10**-2,10**2)
            pylab.gca().set_xscale("log")
            if x_label:
                pylab.xlabel('firing rate [sp/s]',fontsize=fontsize)
                pylab.xticks([0.01,0.1,1.0,10,100])
            else:
                pylab.xticks([])
            pylab.ylabel(y_label,fontsize=fontsize)                
            #pylab.yticks([0.0,0.5,1.0])
            for label in pylab.gca().get_xticklabels() + pylab.gca().get_yticklabels():
                label.set_fontsize(fontsize)
            phf.disable_top_right_axis(pylab.gca())
            
            pylab.subplot(gs2)
            pylab.plot(numpy.logspace(-1,2,100),numpy.exp(-((numpy.log10(numpy.logspace(-1,2,100))-m)**2)/(2*s*s))/(s*numpy.sqrt(2*numpy.pi)),linewidth=4,color="#666666")
            pylab.plot(numpy.logspace(-1,2,100),numpy.exp(-numpy.logspace(-1,2,100)/nm)/nm,'k--',linewidth=4)
            pylab.plot(numpy.power(10,bin_centers),h,'ko',mec=None,mew=3)
            pylab.xlim(10**-1,10**2)
            pylab.ylim(0.00001,5.0)
            pylab.gca().set_xscale("log")
            pylab.gca().set_yscale("log")
            if x_label:
                pylab.xlabel('firing rate [sp/s]',fontsize=fontsize)
                pylab.xticks([0.1,1.0,10,100])
            else:
                pylab.xticks([])
            pylab.yticks([0.0001,0.01,1.0])
            for label in pylab.gca().get_xticklabels() + pylab.gca().get_yticklabels():
                label.set_fontsize(fontsize)
            phf.disable_top_right_axis(pylab.gca())
        

        plots = {}
        fontsize = 20
        pylab.rc('axes', linewidth=1)

        if True:
            gs = gridspec.GridSpecFromSubplotSpec(60,4, subplot_spec=subplotspec,hspace=10, wspace=0.8)

            barh_plot(gs[0:18,0], mean_firing_rate, std_firing_rate, 'firing rate (sp/s)', fontsize)
            # xmax=10.0, xmin=0.0
            barh_plot(gs[20:38,0], mean_cv, std_cv, 'irregularity', fontsize, xmax=2.0, xmin=0.0, offset=0.37)
            barh_plot(gs[40:58,0], mean_cc, std_cc, 'synchrony', fontsize, offset=0.4)
            # xmax=0.15, xmin=0.0
            barh_plot(gs[0:18,1], mean_vm, std_vm, 'membrane potential (mV)', fontsize, xmax=80.0, xmin=40.0)
            barh_plot(gs[20:38,1], mean_cond_e, std_cond_e, 'excitatory conductance (nS)', fontsize, xmax=2.0, xmin=0.0) 
            barh_plot(gs[40:58,1], mean_cond_i, std_cond_i, 'inhibitory conductance (nS)', fontsize, xmax=10.0, xmin=0.0)

            valid_sheets = len(mean_firing_rate.keys())
            plotted = 0
            for i, sheet in enumerate(all_sheets):
                if sheet in mean_firing_rate:
                    label = sheet.split('_')[2] + sheet.split('_')[1][0]
                    if plotted < valid_sheets-1:
                        plot_with_log_normal_fit(param_filter_query(self.datastore,value_name=['Firing rate'],sheet_name=sheet,st_direct_stimulation_name=None,st_name=['InternalStimulus'],ads_unique=True).get_analysis_result()[0].values,gs[i*6:(i+1)*6,2],gs[i*6:(i+1)*6,3],y_label=label)
                        plotted += 1
                    else:
                        plot_with_log_normal_fit(param_filter_query(self.datastore,value_name=['Firing rate'],sheet_name=sheet,st_direct_stimulation_name=None,st_name=['InternalStimulus'],ads_unique=True).get_analysis_result()[0].values,gs[i*6:(i+1)*6,2],gs[i*6:(i+1)*6,3],x_label=True,y_label=label)

        return plots

class OrientationTuningSummaryAnalogSignalsAllLayers(Plotting):

    required_parameters = ParameterSet({
        'sheet_names': list,
    })

    def subplot(self, subplotspec):
        sheets_num = len(self.parameters.sheet_names)
        analog_ids = dict()
        or_tuning = dict()
        for sheet in self.parameters.sheet_names:
            analog_ids[sheet] = sorted(numpy.random.permutation(queries.param_filter_query(self.datastore, sheet_name=sheet).get_segments()[0].get_stored_esyn_ids()))
            or_tuning[sheet] = self.datastore.get_analysis_result(identifier='PerNeuronValue', value_name='LGNAfferentOrientation', sheet_name=sheet)[0]
            or_tuning[sheet] = None
        # TODO: test or_tuning

        plots = {}
        gs = gridspec.GridSpecFromSubplotSpec(6*sheets_num, 35, subplot_spec=subplotspec, hspace=10.0, wspace=0.6)

        for i, sheet in enumerate(self.parameters.sheet_names):
            key_label = sheet.split('_')[2].replace("/","") + sheet.split('_')[1]
            label = sheet.split('_')[2] + sheet.split('_')[1]
            if i==0:
                titles = ['F0 of Vm (mV)', 'F1 of Vm (mV)', 'F0 of gE (nS)', 'F1 of gE (nS)', 'F0 of gI (nS)', 'F1 of gI (nS)']
            else:
                titles = [None, None, None, None, None, None]

            if i < sheets_num-1:
                x_labels = {'x_axis': False, 'x_ticks': False}
            else:
                x_labels = {}

            dsv = queries.param_filter_query(self.datastore, value_name=['-(x+y)(F0_Vm,Mean(VM))'],st_contrast=[low_contrast,high_contrast])
            plots[key_label + '_F0_Vm'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids[sheet]), 'sheet_name': sheet, 'centered': True, 'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning[sheet]), gs[i*6:(i+1)*6, :5], {'title': titles[0], 'x_label': None, 'y_label': label, 'y_tick_precision': 2, **x_labels})
            dsv = queries.param_filter_query(self.datastore, value_name=['F1_Vm'],st_contrast=[low_contrast,high_contrast])
            plots[key_label + '_F1_Vm'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids[sheet]), 'sheet_name': sheet, 'centered': True, 'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning[sheet]), gs[i*6:(i+1)*6, 6:11], {'title': titles[1], 'x_label': None, 'y_label': None, 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2})
            dsv = queries.param_filter_query(self.datastore, value_name=['F0_Exc_Cond-Mean(ECond)'],st_contrast=[low_contrast,high_contrast])
            plots[key_label + '_F0_CondExc'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids[sheet]), 'sheet_name': sheet, 'centered': True, 'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning[sheet]), gs[i*6:(i+1)*6, 12:17], {'title': titles[2], 'x_label': None, 'y_label': None, 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2})
            dsv = queries.param_filter_query(self.datastore, value_name=['F1_Exc_Cond'],st_contrast=[low_contrast,high_contrast])
            plots[key_label + '_F1_CondExc'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids[sheet]), 'sheet_name': sheet, 'centered': True, 'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning[sheet]), gs[i*6:(i+1)*6, 18:23], {'title': titles[3], 'x_label': None, 'y_label': None, 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2})
            dsv = queries.param_filter_query(self.datastore, value_name=['F0_Inh_Cond-Mean(ICond)'],st_contrast=[low_contrast,high_contrast])
            plots[key_label + '_F0_CondInh'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids[sheet]), 'sheet_name': sheet, 'centered': True, 'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning[sheet]), gs[i*6:(i+1)*6, 24:29], {'title': titles[4], 'x_label': None, 'y_label': None, 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2})
            dsv = queries.param_filter_query(self.datastore, value_name=['F1_Inh_Cond'],st_contrast=[low_contrast,high_contrast])
            plots[key_label + '_F1_CondInh'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids[sheet]), 'sheet_name': sheet, 'centered': True, 'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning[sheet]), gs[i*6:(i+1)*6, 30:35], {'title': titles[5], 'x_label': None, 'y_label': None, 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2})

        return plots

class OrientationTuningSummaryFiringRatesAllLayers(Plotting):

    """
    This figure plots summary of orientation tuning analysis in the model. 
      
    Parameters
    ----------
    exc_sheet_name1 : str
               The name of the sheet corresponding to layer 4 excitatory neurons.
              
    exc_sheet_name2 : str
          The name of the sheet corresponding to layer 2/3 excitatory neurons.


    inh_sheet_name1 : str
               The name of the sheet corresponding to layer 4 inhibitory neurons.
              
    inh_sheet_name2 : str
          The name of the sheet corresponding to layer 2/3 inhibitory neurons.

    """

    # required_parameters = ParameterSet({
    #     'exc_sheet_name1': str,  # the name of the sheet for which to plot
    #     'inh_sheet_name1': str,  # the name of the sheet for which to plot
    #     'exc_sheet_name2': str,  # the name of the sheet for which to plot
    #     'inh_sheet_name2': str,  # the name of the sheet for which to plot
    # })
    required_parameters = ParameterSet({
        'sheet_names': list,
    })


    def subplot(self, subplotspec):
        plots = {}
        sheets_num = len(self.parameters.sheet_names)
        gs = gridspec.GridSpecFromSubplotSpec(7*sheets_num-1, 39, subplot_spec=subplotspec, hspace=1.0, wspace=5.0)
        
        mean_and_sem = lambda x : (numpy.mean(x), numpy.std(x)/numpy.sqrt(len(x)))

        spike_ids = dict()
        idxs = dict()
        for sheet in self.parameters.sheet_names:
            spike_ids[sheet] = numpy.array(sorted(numpy.random.permutation(queries.param_filter_query(self.datastore, sheet_name=sheet).get_segments()[0].get_stored_spike_train_ids())))
            idxs[sheet] = self.datastore.get_sheet_indexes(sheet_name=sheet, neuron_ids=spike_ids[sheet])
            x = self.datastore.get_neuron_positions()[sheet][0][idxs[sheet]]
            y = self.datastore.get_neuron_positions()[sheet][1][idxs[sheet]]
            spike_ids[sheet] = spike_ids[sheet][numpy.nonzero(numpy.sqrt(numpy.multiply(x,x)+numpy.multiply(y,y)) < 0.9)[0]]

        spont_pnv = dict()
        for sheet in self.parameters.sheet_names:
            spont_pnv[sheet] = param_filter_query(self.datastore,st_name='InternalStimulus',analysis_algorithm=['TrialAveragedFiringRate'],value_name='Firing rate',sheet_name=sheet,ads_unique=True).get_analysis_result()[0]

        r = 1.0
        responsive_spike_ids = dict()
        sheets_base = dict()
        sheets_mmax = dict()
        sheets_rura = dict()
        for sheet in self.parameters.sheet_names:
            base = queries.param_filter_query(self.datastore, sheet_name=sheet, st_name=['FullfieldDriftingSinusoidalGrating'], st_contrast=low_contrast, value_name=['orientation baseline of Firing rate'], ads_unique=True).get_analysis_result()[0].get_value_by_id(spike_ids[sheet])
            mmax = queries.param_filter_query(self.datastore, sheet_name=sheet, st_name=['FullfieldDriftingSinusoidalGrating'], st_contrast=low_contrast, value_name=['orientation max of Firing rate'], ads_unique=True).get_analysis_result()[0].get_value_by_id(spike_ids[sheet])
            err = queries.param_filter_query(self.datastore, sheet_name=sheet, st_name=['FullfieldDriftingSinusoidalGrating'], st_contrast=high_contrast, value_name=['orientation fitting error of Firing rate'], ads_unique=True).get_analysis_result()[0].get_value_by_id(spike_ids[sheet])
            err_lc = queries.param_filter_query(self.datastore, sheet_name=sheet, st_name=['FullfieldDriftingSinusoidalGrating'], st_contrast=low_contrast, value_name=['orientation fitting error of Firing rate'], ads_unique=True).get_analysis_result()[0].get_value_by_id(spike_ids[sheet])
            responsive_spike_ids[sheet] = numpy.array(spike_ids[sheet])[numpy.logical_and(numpy.logical_and(numpy.array(base)+numpy.array(mmax) > r, numpy.array(err) <= 0.3), numpy.array(err_lc) <= 0.3)]
            base = numpy.array(queries.param_filter_query(self.datastore, sheet_name=sheet, st_name=['FullfieldDriftingSinusoidalGrating'], st_contrast=high_contrast, value_name=['orientation baseline of Firing rate'], ads_unique=True).get_analysis_result()[0].get_value_by_id(responsive_spike_ids[sheet]))
            mmax = numpy.array(queries.param_filter_query(self.datastore, sheet_name=sheet, st_name=['FullfieldDriftingSinusoidalGrating'], st_contrast=high_contrast, value_name=['orientation max of Firing rate'], ads_unique=True).get_analysis_result()[0].get_value_by_id(responsive_spike_ids[sheet]))
            idx = numpy.logical_and(base>=0,mmax>=0)
            base = base[idx]
            mmax = mmax[idx]
            sp = numpy.array(spont_pnv[sheet].get_value_by_id(responsive_spike_ids[sheet]))[idx]
            sheets_base[sheet] = base
            sheets_mmax[sheet] = mmax
            sheets_rura[sheet] = ((numpy.array(base)-numpy.array(sp))/(numpy.array(base)+numpy.array(mmax)-numpy.array(sp)))[numpy.array(base)+numpy.array(mmax) > r]
            print('Removed \% of neurons:' + str(float(len(spike_ids[sheet])-len(responsive_spike_ids[sheet]))/len(spike_ids[sheet])))

        dsv = queries.param_filter_query(self.datastore, st_name='FullfieldDriftingSinusoidalGrating', analysis_algorithm=['TrialAveragedFiringRate'], st_contrast=[low_contrast, high_contrast], value_name='Firing rate')
        for i, sheet in enumerate(self.parameters.sheet_names):
            # expected name of sheet is eg. "V1_Exc_L4"
            pop_type = sheet.split('_')[1]
            layer = sheet.split('_')[2].replace("/","")
            y_label = f"Layer {layer} ({pop_type.upper()})\n\nfiring rate (sp/s)"
            if i == sheets_num-1:
                x_labels = {}
            else:
                x_labels = {'x_label': None, 'x_ticks': None}

            plots[f'{pop_type}ORTCMean{layer}'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name' : 'orientation', 'neurons': list(spike_ids[sheet]), 'sheet_name' : sheet,'centered'  : True,'mean' : True,'pool' : False,'polar' : False}), spont_level_pnv=spont_pnv[sheet]),gs[i*7:i*7+6, :6],{'y_lim' : (0,None),'title' : None, 'y_label' : y_label, 'linestyles' : ['--','-','-'], **x_labels})
            if len(responsive_spike_ids[sheet]) > 0:
                plots[f'{pop_type}ORTC1{layer}'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name' : 'orientation', 'neurons': list(responsive_spike_ids[sheet][0:3]), 'sheet_name' : sheet,'centered'  : True,'mean' : False,'pool' : False,'polar' : False}), spont_level_pnv=spont_pnv[sheet]),gs[i*7:i*7+3, 6:15],{'y_lim' : (0,None),'title' : None,'left_border' : None, 'x_label' : None,'y_axis' : False,'x_axis' : False, 'x_ticks' : False, 'linestyles' : ['--','-','-']})
            if len(responsive_spike_ids[sheet]) > 3:
                plots[f'{pop_type}ORTC2{layer}'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name' : 'orientation', 'neurons': list(responsive_spike_ids[sheet][3:6]), 'sheet_name' : sheet,'centered'  : True,'mean' : False,'pool' : False,'polar': False}), spont_level_pnv=spont_pnv[sheet]),gs[i*7+3:i*7+6, 6:15],{'y_lim' : (0,None),'title' : None,'left_border' : None, 'x_label' : None,'y_axis' : False,'x_axis' : False, 'linestyles' : ['--','-','-']})


        sheets_hc = dict()
        for i, sheet in enumerate(self.parameters.sheet_names):
            # expected name of sheet is eg. "V1_Exc_L4"
            pop_type = sheet.split('_')[1]
            layer = sheet.split('_')[2].replace("/","")
            if i == sheets_num-1:
                x_labels = {'x_label' : f'HWHH Cont. {high_contrast}%'}
            else:
                x_labels = {'x_label': None}

            dsv1 = queries.param_filter_query(self.datastore,value_name=['orientation HWHH of Firing rate'],sheet_name=[sheet], st_contrast =[low_contrast,high_contrast])
            dsv = queries.param_filter_query(dsv1,st_contrast=low_contrast)
            b = numpy.array(dsv.get_analysis_result()[0].get_value_by_id(responsive_spike_ids[sheet]))
            dsv = queries.param_filter_query(dsv1,st_contrast=high_contrast)
            a = numpy.array(dsv.get_analysis_result()[0].get_value_by_id(responsive_spike_ids[sheet]))
            lc = b[numpy.logical_and(numpy.logical_and(a>0,b>0),numpy.logical_and(a<200,b<200))]
            hc = a[numpy.logical_and(numpy.logical_and(a>0,b>0),numpy.logical_and(a<200,b<200))]
            print('Removed \% of neurons:' + str(float(len(spike_ids[sheet])-len(hc))/len(spike_ids[sheet])))
            print(f"{layer}{pop_type} Mean HWHH: {mean_and_sem(hc)}")
            print("LC_HC diff: "+  str(mean_and_sem((hc-lc)[abs(hc-lc)< 50])) + ' p=' + str( scipy.stats.ttest_rel(hc[abs(hc-lc)< 50],lc[abs(hc-lc)< 50])))
            mean_hwhh = round(mean_and_sem(hc)[0],2)
            diff_hwhh = str(round(mean_and_sem((hc-lc)[abs(hc-lc)< 50])[0],2))
            dsv1.sort_analysis_results('st_contrast', reverse=True)

            plots[f'HWHH{pop_type}{layer}'] = (PerNeuronValueScatterPlot(dsv1, ParameterSet({'only_matching_units' : True, 'ignore_nan' : True, 'lexicographic_order': True, 'neuron_ids': list(responsive_spike_ids[sheet])})),gs[i*7:i*7+6,17:23],{'x_lim': (0,50),'y_lim' : (0,50),'identity_line' : True, 'y_label' : 'HWHH cont. '+str(low_contrast)+'%', 'cmp' : None,'title' : None, 'dot_size' : 10, **x_labels})
            sheets_hc[sheet] = hc

        hc_exc = []
        hc_inh = []
        for sheet in sheets_hc:
            if 'ex' in sheet.lower():
                hc_exc += sheets_hc[sheet].tolist()
            else:
                hc_inh += sheets_hc[sheet].tolist()
        print("HWHH Exc: " +str( mean_and_sem(hc_exc)))
        print("HWHH Inh: " +str( mean_and_sem(hc_inh)))

        for i, sheet in enumerate(self.parameters.sheet_names):
            # expected name of sheet is eg. "V1_Exc_L4"
            pop_type = sheet.split('_')[1]
            layer = sheet.split('_')[2].replace("/","")

            if i == sheets_num-1:
                x_labels = {'x_label' : f'HWHH ({high_contrast}% cont.)'}
            else:
                x_labels = {'x_label': None}

            dsv = queries.param_filter_query(self.datastore,value_name=['orientation HWHH of Firing rate'],sheet_name=[sheet], st_contrast=[high_contrast])
            plots[f'HWHHHistogram{pop_type}{layer}'] = (PerNeuronValuePlot(dsv, ParameterSet({'cortical_view' : False, 'neuron_ids':list(responsive_spike_ids[sheet])})),gs[i*7:i*7+6,26:32],{ 'x_lim' : (0.0,50.0), 'title' : None,'y_label' : '# neurons', **x_labels})

        for i, sheet in enumerate(self.parameters.sheet_names):
            # expected name of sheet is eg. "V1_Exc_L4"
            pop_type = sheet.split('_')[1]
            layer = sheet.split('_')[2].replace("/","")

            axis = pylab.subplot(gs[i*7:i*7+6,33:39])
            pylab.hist(sheets_rura[sheet]*100, color='k', bins=numpy.arange(-20,40,3))
            pylab.xlim(-20,40)
            pylab.xticks([-20,10,40])
            pylab.ylabel('# neurons',fontsize=19)
            for label in axis.get_xticklabels() + axis.get_yticklabels():
                label.set_fontsize(19)
            phf.disable_top_right_axis(pylab.gca())
            phf.three_tick_axis(axis.yaxis ,log=False, precision = 3)
            xtls = axis.get_xticklabels()
            for xtl in xtls:
                x,y = xtl.get_position()
                xtl.set_position((x,y-0.032))
            #phf.disable_left_axis(pylab.gca())
            if i == sheets_num-1:
                pylab.xlabel('RURA',fontsize=19)
            print(f"{layer}{pop_type} Mean/SEM RURA:" + str( mean_and_sem(sheets_rura[sheet][numpy.abs(sheets_rura[sheet])<0.5]*100)))

        rura_exc = []
        rura_inh = []
        for sheet in sheets_rura:
            if 'ex' in sheet.lower():
                hc_exc += list(sheets_rura[sheet][numpy.abs(sheets_rura[sheet])<0.5]*100)
            else:
                hc_inh += list(sheets_rura[sheet][numpy.abs(sheets_rura[sheet])<0.5]*100)
        print(f"Exc RURA: {mean_and_sem(rura_exc)}")
        print(f"Inh RURA: {mean_and_sem(rura_inh)}")

        return plots

class MRfigRealAllLayers(Plotting):
    required_parameters = ParameterSet({
        'SimpleSheetName': str,  # the name of the sheet for which to plot
        'ComplexSheetName': str,  # which neuron to show
    })

    def plot(self):
        sheets = self.parametes.sheet_names
        sheets_num = len(self.parameters.sheet_names)

        self.fig = pylab.figure(facecolor='w', **self.fig_param)
        gs = gridspec.GridSpec(1, 1)
        gs.update(left=0.07, right=0.97, top=0.9, bottom=0.1)
        gs = gs[0, 0]


        # modulation ration only for excitatory neurons
        # ModulationRatio(param_filter_query(data_store, sheet_name=exc_sheets, st_contrast=[high_contrast]), ParameterSet({})).analyse()
        dsv_l4 = self.datastore.get_analysis_result(identifier='PerNeuronValue', sheet_name=self.parameters.SimpleSheetName, analysis_algorithm='ModulationRatio', value_name='Modulation ratio(time)')
        dsv_l23 = self.datastore.get_analysis_result(identifier='PerNeuronValue', sheet_name=self.parameters.ComplexSheetName, analysis_algorithm='ModulationRatio', value_name='Modulation ratio(time)')


        dsv = queries.param_filter_query(self.datastore, st_name='FullfieldDriftingSinusoidalGrating', st_orientation=0)
        dsv_l4_v_F0 = dsv.get_analysis_result(identifier='PerNeuronValue', sheet_name=self.parameters.SimpleSheetName, value_name='-(x+y)(F0_Vm,Mean(VM))')
        dsv_l23_v_F0 = dsv.get_analysis_result(identifier='PerNeuronValue', sheet_name=self.parameters.ComplexSheetName, value_name='-(x+y)(F0_Vm,Mean(VM))')
        dsv_l4_v_F1 = dsv.get_analysis_result(identifier='PerNeuronValue', sheet_name=self.parameters.SimpleSheetName, value_name='F1_Vm')
        dsv_l23_v_F1 = dsv.get_analysis_result(identifier='PerNeuronValue', sheet_name=self.parameters.ComplexSheetName, value_name='F1_Vm')

        dsv_l4_v_F0_inh = dsv.get_analysis_result(identifier='PerNeuronValue', sheet_name='V1_Inh_L4', value_name='-(x+y)(F0_Vm,Mean(VM))')
        dsv_l23_v_F0_inh = dsv.get_analysis_result(identifier='PerNeuronValue', sheet_name='V1_Inh_L2/3', value_name='-(x+y)(F0_Vm,Mean(VM))')
        dsv_l4_v_F1_inh = dsv.get_analysis_result(identifier='PerNeuronValue', sheet_name='V1_Inh_L4', value_name='F1_Vm')
        dsv_l23_v_F1_inh = dsv.get_analysis_result(identifier='PerNeuronValue', sheet_name='V1_Inh_L2/3', value_name='F1_Vm')

        assert len(dsv_l4) == 1,  str(len(dsv_l4))
        assert len(dsv_l4_v_F0) == 1
        assert len(dsv_l4_v_F1) == 1
        if self.parameters.ComplexSheetName != 'None':
            assert len(dsv_l23) == 1
            assert len(dsv_l23_v_F0) == 1
            assert len(dsv_l23_v_F1) == 1

        l4_ids = dsv_l4_v_F0[0].ids
        l4_ids_inh = dsv_l4_v_F0_inh[0].ids
        if self.parameters.ComplexSheetName != 'None':
            l23_ids = dsv_l23_v_F0[0].ids
            l23_ids_inh = dsv_l23_v_F0_inh[0].ids

        l4_exc_or = self.datastore.full_datastore.get_analysis_result(identifier='PerNeuronValue', value_name=['LGNAfferentOrientation', 'ORMapOrientation'], sheet_name='V1_Exc_L4')[0]
        l4_ids = numpy.array(l4_ids)[numpy.nonzero(numpy.array([circular_dist(l4_exc_or.get_value_by_id(i), 0, numpy.pi) for i in l4_ids]) < 0.4)[0]]

        l4_exc_or_inh = self.datastore.full_datastore.get_analysis_result(identifier='PerNeuronValue', value_name=['LGNAfferentOrientation', 'ORMapOrientation'], sheet_name='V1_Inh_L4')[0]
        l4_ids_inh = numpy.array(l4_ids_inh)[numpy.nonzero(numpy.array([circular_dist(l4_exc_or_inh.get_value_by_id(i), 0, numpy.pi) for i in l4_ids_inh]) < 0.4)[0]]

        if self.parameters.ComplexSheetName != 'None':
            l23_exc_or = self.datastore.full_datastore.get_analysis_result(identifier='PerNeuronValue', value_name=['LGNAfferentOrientation', 'ORMapOrientation'], sheet_name='V1_Exc_L2/3')[0]
            l23_ids = numpy.array(l23_ids)[numpy.nonzero(numpy.array([circular_dist(l23_exc_or.get_value_by_id(i), 0, numpy.pi) for i in l23_ids]) < 0.4)[0]]

            l23_exc_or_inh = self.datastore.full_datastore.get_analysis_result(identifier='PerNeuronValue', value_name=['LGNAfferentOrientation', 'ORMapOrientation'], sheet_name='V1_Inh_L2/3')[0]
            l23_ids_inh = numpy.array(l23_ids_inh)[numpy.nonzero(numpy.array([circular_dist(l23_exc_or_inh.get_value_by_id(i), 0, numpy.pi) for i in l23_ids_inh]) < 0.4)[0]]

        l4_v_mr = numpy.array(dsv_l4_v_F1[0].get_value_by_id(l4_ids))/numpy.array(dsv_l4_v_F0[0].get_value_by_id(l4_ids))
        l4_v_mr_inh = numpy.array(dsv_l4_v_F1_inh[0].get_value_by_id(l4_ids_inh))/numpy.array(dsv_l4_v_F0_inh[0].get_value_by_id(l4_ids_inh))
        dsv_l4 = dsv_l4[0]
        if self.parameters.ComplexSheetName != 'None':
            l23_v_mr = numpy.array(dsv_l23_v_F1[0].get_value_by_id(l23_ids))/numpy.array(dsv_l23_v_F0[0].get_value_by_id(l23_ids))
            l23_v_mr_inh = numpy.array(dsv_l23_v_F1_inh[0].get_value_by_id(l23_ids_inh))/numpy.array(dsv_l23_v_F0_inh[0].get_value_by_id(l23_ids_inh))
            dsv_l23 = dsv_l23[0]

        if self.parameters.ComplexSheetName != 'None':
            dsv_simple = numpy.append(dsv_l4.values[dsv_l4.values < 1.0], dsv_l23.values[dsv_l23.values < 1.0])
            dsv_complex = numpy.append(dsv_l4.values[dsv_l4.values > 1.0], dsv_l23.values[dsv_l23.values > 1.0])

            simple_mr = numpy.append(numpy.array(dsv_l4.get_value_by_id(l4_ids))[numpy.array(dsv_l4.get_value_by_id(l4_ids)) < 1.0], numpy.array(dsv_l23.get_value_by_id(l23_ids))[numpy.array(dsv_l23.get_value_by_id(l23_ids)) < 1.0])
            complex_mr = numpy.append(numpy.array(dsv_l4.get_value_by_id(l4_ids))[numpy.array(dsv_l4.get_value_by_id(l4_ids)) > 1.0], numpy.array(dsv_l23.get_value_by_id(l23_ids))[numpy.array(dsv_l23.get_value_by_id(l23_ids)) > 1.0])

            simple_v_mr = numpy.append(l4_v_mr[numpy.array(dsv_l4.get_value_by_id(l4_ids)) < 1.0], l23_v_mr[numpy.array(dsv_l23.get_value_by_id(l23_ids)) < 1.0])
            complex_v_mr = numpy.append(l4_v_mr[numpy.array(dsv_l4.get_value_by_id(l4_ids)) > 1.0], l23_v_mr[numpy.array(dsv_l23.get_value_by_id(l23_ids)) > 1.0])

            dsv_simple_v_F0 = numpy.append(numpy.array(dsv_l4_v_F0[0].get_value_by_id(l4_ids))[numpy.array(dsv_l4.get_value_by_id(l4_ids)) < 1.0], numpy.array(dsv_l23_v_F0[0].get_value_by_id(l23_ids))[numpy.array(dsv_l23.get_value_by_id(l23_ids)) < 1.0])
            dsv_complex_v_F0 = numpy.append(numpy.array(dsv_l4_v_F0[0].get_value_by_id(l4_ids))[numpy.array(dsv_l4.get_value_by_id(l4_ids)) > 1.0], numpy.array(dsv_l23_v_F0[0].get_value_by_id(l23_ids))[numpy.array(dsv_l23.get_value_by_id(l23_ids)) > 1.0])

            dsv_simple_v_F1 = numpy.append(numpy.array(dsv_l4_v_F1[0].get_value_by_id(l4_ids))[numpy.array(dsv_l4.get_value_by_id(l4_ids)) < 1.0], numpy.array(dsv_l23_v_F1[0].get_value_by_id(l23_ids))[numpy.array(dsv_l23.get_value_by_id(l23_ids)) < 1.0])
            dsv_complex_v_F1 = numpy.append(numpy.array(dsv_l4_v_F1[0].get_value_by_id(l4_ids))[numpy.array(dsv_l4.get_value_by_id(l4_ids)) > 1.0], numpy.array(dsv_l23_v_F1[0].get_value_by_id(l23_ids))[numpy.array(dsv_l23.get_value_by_id(l23_ids)) > 1.0])
        else:
            dsv_simple = dsv_l4.values[dsv_l4.values < 1.0]
            dsv_complex = dsv_l4.values[dsv_l4.values > 1.0]

            simple_mr = numpy.array(dsv_l4.get_value_by_id(l4_ids))[numpy.array(dsv_l4.get_value_by_id(l4_ids)) < 1.0]
            complex_mr = numpy.array(dsv_l4.get_value_by_id(l4_ids))[numpy.array(dsv_l4.get_value_by_id(l4_ids)) > 1.0]
            simple_v_mr = l4_v_mr[numpy.array(dsv_l4.get_value_by_id(l4_ids)) < 1.0]
            complex_v_mr = l4_v_mr[numpy.array(dsv_l4.get_value_by_id(l4_ids)) > 1.0]

            dsv_simple_v_F0 = numpy.array(dsv_l4_v_F0[0].get_value_by_id(l4_ids))[numpy.array(dsv_l4.get_value_by_id(l4_ids)) < 1.0]
            dsv_complex_v_F0 = numpy.array(dsv_l4_v_F0[0].get_value_by_id(l4_ids))[numpy.array(dsv_l4.get_value_by_id(l4_ids)) > 1.0]

            dsv_simple_v_F1 = numpy.array(dsv_l4_v_F1[0].get_value_by_id(l4_ids))[numpy.array(dsv_l4.get_value_by_id(l4_ids)) < 1.0]
            dsv_complex_v_F1 = numpy.array(dsv_l4_v_F1[0].get_value_by_id(l4_ids))[numpy.array(dsv_l4.get_value_by_id(l4_ids)) > 1.0]

        gs = gridspec.GridSpecFromSubplotSpec(3, 7, subplot_spec=gs, wspace=0.3)
        ax = pylab.subplot(gs[0, 0])
        ax.hist(dsv_l4.values, bins=numpy.arange(0, 2.01, 0.2), color='gray', rwidth=0.8)
        disable_top_right_axis(ax)
        disable_left_axis(ax)
        pylab.ylim(0, 540)
        disable_xticks(ax)
        remove_x_tick_labels()
        remove_y_tick_labels()
        pylab.ylabel('Layer 4', fontsize=19)
        ax = pylab.subplot(gs[1, 0])
        if self.parameters.ComplexSheetName != 'None':
            ax.hist(dsv_l23.values, bins=numpy.arange(0, 2.01, 0.2), color='gray', rwidth=0.8)
            disable_top_right_axis(ax)
            disable_left_axis(ax)
            pylab.ylim(0, 540)
            disable_xticks(ax)
            remove_x_tick_labels()
            remove_y_tick_labels()
            pylab.ylabel('Layer 2/3', fontsize=19)

            ax = pylab.subplot(gs[2, 0])
            ax.hist([dsv_complex, dsv_simple], bins=numpy.arange(0, 2.01, 0.2), histtype='barstacked', color=['w', 'k'], rwidth=0.8, ec='black')
            disable_top_right_axis(ax)
            disable_left_axis(ax)
            pylab.ylim(0, 540)
            pylab.ylabel('Pooled', fontsize=19)
            ax.set_xticks([0,1,2])
            remove_y_tick_labels()
            pylab.xlabel('F1/F0 spikes', fontsize=19)
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontsize(19)
            disable_top_right_axis(ax)
            disable_left_axis(ax)

        ax = pylab.subplot(gs[0, 1])
        ax.hist(l4_v_mr, bins=numpy.arange(
            0, 5.01, 0.5), color='gray', rwidth=0.8)
        disable_top_right_axis(ax)
        disable_left_axis(ax)
        disable_xticks(ax)
        remove_x_tick_labels()
        remove_y_tick_labels()
        pylab.xlim(0, 5.0)

        if self.parameters.ComplexSheetName != 'None':
            ax = pylab.subplot(gs[1, 1])
            ax.hist(l23_v_mr, bins=numpy.arange(0, 5.01, 0.5), color='gray', rwidth=0.8)
            disable_top_right_axis(ax)
            disable_left_axis(ax)
            disable_xticks(ax)
            remove_x_tick_labels()
            remove_y_tick_labels()
            pylab.xlim(0, 5.0)
            ax = pylab.subplot(gs[2, 1])
            ax.hist([complex_v_mr, simple_v_mr], bins=numpy.arange(0, 5.01, 0.5), histtype='barstacked', color=['w', 'k'], rwidth=0.8, ec='black')
            three_tick_axis(ax.xaxis)
            remove_y_tick_labels()
            pylab.xlabel('F1/F0 Vm', fontsize=19)
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontsize(19)
            disable_top_right_axis(ax)
            disable_left_axis(ax)
            pylab.xlim(0, 5.0)

        ax = pylab.subplot(gs[0, 2])
        ax.hist(numpy.abs(dsv_l4_v_F0[0].get_value_by_id(l4_ids)), bins=numpy.arange(0, 3.01, 0.3), color='gray', rwidth=0.8)
        disable_top_right_axis(ax)
        disable_left_axis(ax)
        disable_left_axis(ax)
        disable_xticks(ax)
        remove_x_tick_labels()
        remove_y_tick_labels()
        pylab.xlim(0, 3.0)

        if self.parameters.ComplexSheetName != 'None':
            ax = pylab.subplot(gs[1, 2])
            ax.hist(numpy.abs(dsv_l23_v_F0[0].get_value_by_id(l23_ids)), bins=numpy.arange(0, 3.01, 0.3), color='gray', rwidth=0.8)
            disable_top_right_axis(ax)
            disable_left_axis(ax)
            disable_xticks(ax)
            remove_x_tick_labels()
            remove_y_tick_labels()
            pylab.xlim(0, 3.0)
            ax = pylab.subplot(gs[2, 2])
            ax.hist([numpy.abs(dsv_complex_v_F0), numpy.abs(dsv_simple_v_F0)], bins=numpy.arange(0, 3.01, 0.3), histtype='barstacked', color=['w', 'k'], rwidth=0.8, ec='black')
            three_tick_axis(ax.xaxis)
            remove_y_tick_labels()
            pylab.xlabel('F0 Vm (mV)', fontsize=19)
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontsize(19)
            disable_top_right_axis(ax)
            disable_left_axis(ax)
            pylab.xlim(0, 3.0)

        ax = pylab.subplot(gs[0, 3])
        ax.hist(numpy.abs(dsv_l4_v_F1[0].get_value_by_id(l4_ids)), bins=numpy.arange(0, 10.01, 1), color='gray', rwidth=0.8)
        disable_top_right_axis(ax)
        disable_left_axis(ax)
        disable_xticks(ax)
        remove_x_tick_labels()
        remove_y_tick_labels()
        pylab.xlim(0, 10.0)

        if self.parameters.ComplexSheetName != 'None':
            ax = pylab.subplot(gs[1, 3])
            ax.hist(numpy.abs(dsv_l23_v_F1[0].get_value_by_id(l23_ids)), bins=numpy.arange(0, 10.01, 1), color='gray', rwidth=0.8)
            disable_top_right_axis(ax)
            disable_left_axis(ax)
            disable_xticks(ax)
            remove_x_tick_labels()
            remove_y_tick_labels()
            pylab.xlim(0, 10.0)
            ax = pylab.subplot(gs[2, 3])
            ax.hist([numpy.abs(dsv_complex_v_F1), numpy.abs(dsv_simple_v_F1)], bins=numpy.arange(0, 10.01, 1), histtype='barstacked', color=['w', 'k'], rwidth=0.8, ec='black')
            three_tick_axis(ax.xaxis)
            remove_y_tick_labels()
            pylab.xlabel('F1 Vm (mV)', fontsize=19)
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontsize(19)
            disable_top_right_axis(ax)
            disable_left_axis(ax)
            pylab.xlim(0, 10.0)

        logger.info(len(simple_v_mr))
        logger.info(len(dsv_simple))
        if self.parameters.ComplexSheetName != 'None':
            ggs = gridspec.GridSpecFromSubplotSpec(20, 20, gs[:, 4:7])
            ax = pylab.subplot(ggs[3:18, 3:18])
            ax.plot(complex_v_mr, complex_mr, 'ok', label='layer 2/3')
            ax.plot(simple_v_mr, simple_mr, 'ok', label='layer 4')
            pylab.xlabel('F1/F0 Vm', fontsize=19)
            pylab.ylabel('F1/F0 Spikes', fontsize=19)
            pylab.xlim(0, 5.0)
            pylab.ylim(0, 2.0)
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontsize(19)

        if self.plot_file_name:
            pylab.savefig(Global.root_directory+self.plot_file_name)

class LSV1MReponseOverviewAllLayers(Plotting):
    required_parameters = ParameterSet({
        'or_many_analog' : dict,
        'exc_sheet_names' : list, # which keys in or_many_analog will be plotted on the left
    })

    def subplot(self, subplotspec):
        plots = {}

        sheets = list(self.parameters.or_many_analog)
        exc_sheets = self.parameters.exc_sheet_names
        inh_sheets = sorted(set(sheets) - set(exc_sheets), key=lambda x: sheets.index(x))

        layers_pops = dict()
        for sheet in sheets:
            pop_type = sheet.split('_')[1][0].lower()
            layer = sheet.split('_')[2].replace("/","")
            if layer not in layers_pops:
                layers_pops[layer] = {'exc':[], 'inh':[]}
            if pop_type == 'e':
                layers_pops[layer]['exc'].append(sheet)
            else:
                layers_pops[layer]['inh'].append(sheet)
        exc_rows = []
        inh_rows = []
        for layer in layers_pops:
            exc_rows.extend(layers_pops[layer]['exc'])
            inh_rows.extend(layers_pops[layer]['inh'])
            diff = len(exc_rows) - len(inh_rows) 
            exc_rows.extend(['']*-diff)
            inh_rows.extend(['']*diff)            


        rows_num = len(exc_sheets)

        gs = gridspec.GridSpecFromSubplotSpec(10*rows_num-1, 68, subplot_spec=subplotspec,hspace=1.0, wspace=100.0)

        for i, rows in enumerate((exc_rows, inh_rows)):
            for j, sheet in enumerate(rows):
                if sheet == '':
                    continue
                pop_type = sheet.split('_')[1]
                layer = sheet.split('_')[2].replace("/","")
                if i == 0:  # set up y axis
                    y_labels = {}
                else:
                    y_labels = {'y_label': None,'y_axis' : False, 'y_ticks' : False}

                if j == 0:
                    title = {}
                else:
                    title = {'title' : None}
                if j == rows_num-1:  # set up x axis
                    x_labels = {}
                else:
                    x_labels = {'x_label': None,'x_axis' : False, 'x_ticks' : False}
                dsv = param_filter_query(self.datastore,st_name='FullfieldDriftingSinusoidalGrating',st_orientation=[0],st_contrast=[100])
                plots[f'{pop_type}Or0{layer}'] = (OverviewPlot(dsv, ParameterSet({'sheet_name' : sheet, 'neuron' : self.parameters.or_many_analog[sheet], 'sheet_activity' : {}, 'spontaneous' : False})),gs[j*10:j*10+9,35*i:35*i+16], {**x_labels, **y_labels, **title})
                dsv = param_filter_query(self.datastore,st_name='FullfieldDriftingSinusoidalGrating',st_orientation=[numpy.pi/2],st_contrast=[100])
                plots[f'{pop_type}OrPiH{layer}'] = (OverviewPlot(dsv, ParameterSet({'sheet_name' : sheet, 'neuron' : self.parameters.or_many_analog[sheet], 'sheet_activity' : {}, 'spontaneous' : False})),gs[j*10:j*10+9,35*i+17:35*i+33], {'y_label': None,'y_axis' : False, 'y_ticks' : False, **x_labels, **title})

        def stim_plot(phase):
            x = numpy.arange(0,2,0.01)
            pylab.plot(x,numpy.sin(x*numpy.pi*4+phase),'g',linewidth=3)
            phf.disable_top_right_axis(self.axis)
            phf.disable_xticks(self.axis)
            phf.disable_yticks(self.axis)
            phf.remove_x_tick_labels()
            phf.remove_y_tick_labels()
            self.axis.set_ylim(-1.3,1.3)
            self.axis.set_xlim(0,2)

        self.axis = pylab.subplot(gs[9:10,0:16])
        stim_plot(8*numpy.pi/16)
        self.axis = pylab.subplot(gs[9:10,35:51])
        stim_plot(7*numpy.pi/16)

        return plots


### Follows old code ###


class MRfigReal(Plotting):
    required_parameters = ParameterSet({
        'SimpleSheetName': str,  # the name of the sheet for which to plot
        'ComplexSheetName': str,  # which neuron to show
    })

    def plot(self):
        self.fig = pylab.figure(facecolor='w', **self.fig_param)
        gs = gridspec.GridSpec(1, 1)
        gs.update(left=0.07, right=0.97, top=0.9, bottom=0.1)
        gs = gs[0, 0]

        dsv_l4 = self.datastore.get_analysis_result(identifier='PerNeuronValue', sheet_name=self.parameters.SimpleSheetName,
                                                    analysis_algorithm='ModulationRatio', value_name='Modulation ratio(time)')
        dsv_l23 = self.datastore.get_analysis_result(
            identifier='PerNeuronValue', sheet_name=self.parameters.ComplexSheetName, analysis_algorithm='ModulationRatio', value_name='Modulation ratio(time)')

        dsv = queries.param_filter_query(
            self.datastore, st_name='FullfieldDriftingSinusoidalGrating', st_orientation=0)
        dsv_l4_v_F0 = dsv.get_analysis_result(
            identifier='PerNeuronValue', sheet_name=self.parameters.SimpleSheetName, value_name='-(x+y)(F0_Vm,Mean(VM))')
        dsv_l23_v_F0 = dsv.get_analysis_result(
            identifier='PerNeuronValue', sheet_name=self.parameters.ComplexSheetName, value_name='-(x+y)(F0_Vm,Mean(VM))')
        dsv_l4_v_F1 = dsv.get_analysis_result(
            identifier='PerNeuronValue', sheet_name=self.parameters.SimpleSheetName, value_name='F1_Vm')
        dsv_l23_v_F1 = dsv.get_analysis_result(
            identifier='PerNeuronValue', sheet_name=self.parameters.ComplexSheetName, value_name='F1_Vm')

        dsv_l4_v_F0_inh = dsv.get_analysis_result(
            identifier='PerNeuronValue', sheet_name='V1_Inh_L4', value_name='-(x+y)(F0_Vm,Mean(VM))')
        dsv_l23_v_F0_inh = dsv.get_analysis_result(
            identifier='PerNeuronValue', sheet_name='V1_Inh_L2/3', value_name='-(x+y)(F0_Vm,Mean(VM))')
        dsv_l4_v_F1_inh = dsv.get_analysis_result(
            identifier='PerNeuronValue', sheet_name='V1_Inh_L4', value_name='F1_Vm')
        dsv_l23_v_F1_inh = dsv.get_analysis_result(
            identifier='PerNeuronValue', sheet_name='V1_Inh_L2/3', value_name='F1_Vm')

        assert len(dsv_l4) == 1,  str(len(dsv_l4))
        assert len(dsv_l4_v_F0) == 1
        assert len(dsv_l4_v_F1) == 1
        if self.parameters.ComplexSheetName != 'None':
            assert len(dsv_l23) == 1
            assert len(dsv_l23_v_F0) == 1
            assert len(dsv_l23_v_F1) == 1

        l4_ids = dsv_l4_v_F0[0].ids
        l4_ids_inh = dsv_l4_v_F0_inh[0].ids
        if self.parameters.ComplexSheetName != 'None':
            l23_ids = dsv_l23_v_F0[0].ids
            l23_ids_inh = dsv_l23_v_F0_inh[0].ids

        l4_exc_or = self.datastore.full_datastore.get_analysis_result(identifier='PerNeuronValue', value_name=[
                                                                      'LGNAfferentOrientation', 'ORMapOrientation'], sheet_name='V1_Exc_L4')[0]
        l4_ids = numpy.array(l4_ids)[numpy.nonzero(numpy.array([circular_dist(
            l4_exc_or.get_value_by_id(i), 0, numpy.pi) for i in l4_ids]) < 0.4)[0]]

        l4_exc_or_inh = self.datastore.full_datastore.get_analysis_result(identifier='PerNeuronValue', value_name=[
                                                                          'LGNAfferentOrientation', 'ORMapOrientation'], sheet_name='V1_Inh_L4')[0]
        l4_ids_inh = numpy.array(l4_ids_inh)[numpy.nonzero(numpy.array([circular_dist(
            l4_exc_or_inh.get_value_by_id(i), 0, numpy.pi) for i in l4_ids_inh]) < 0.4)[0]]

        if self.parameters.ComplexSheetName != 'None':
            l23_exc_or = self.datastore.full_datastore.get_analysis_result(identifier='PerNeuronValue', value_name=[
                                                                           'LGNAfferentOrientation', 'ORMapOrientation'], sheet_name='V1_Exc_L2/3')[0]
            l23_ids = numpy.array(l23_ids)[numpy.nonzero(numpy.array([circular_dist(
                l23_exc_or.get_value_by_id(i), 0, numpy.pi) for i in l23_ids]) < 0.4)[0]]

            l23_exc_or_inh = self.datastore.full_datastore.get_analysis_result(identifier='PerNeuronValue', value_name=[
                                                                               'LGNAfferentOrientation', 'ORMapOrientation'], sheet_name='V1_Inh_L2/3')[0]
            l23_ids_inh = numpy.array(l23_ids_inh)[numpy.nonzero(numpy.array([circular_dist(
                l23_exc_or_inh.get_value_by_id(i), 0, numpy.pi) for i in l23_ids_inh]) < 0.4)[0]]

        l4_v_mr = numpy.array(dsv_l4_v_F1[0].get_value_by_id(
            l4_ids))/numpy.array(dsv_l4_v_F0[0].get_value_by_id(l4_ids))
        l4_v_mr_inh = numpy.array(dsv_l4_v_F1_inh[0].get_value_by_id(
            l4_ids_inh))/numpy.array(dsv_l4_v_F0_inh[0].get_value_by_id(l4_ids_inh))
        dsv_l4 = dsv_l4[0]
        if self.parameters.ComplexSheetName != 'None':
            l23_v_mr = numpy.array(dsv_l23_v_F1[0].get_value_by_id(
                l23_ids))/numpy.array(dsv_l23_v_F0[0].get_value_by_id(l23_ids))
            l23_v_mr_inh = numpy.array(dsv_l23_v_F1_inh[0].get_value_by_id(
                l23_ids_inh))/numpy.array(dsv_l23_v_F0_inh[0].get_value_by_id(l23_ids_inh))
            dsv_l23 = dsv_l23[0]

        if self.parameters.ComplexSheetName != 'None':
            dsv_simple = numpy.append(
                dsv_l4.values[dsv_l4.values < 1.0], dsv_l23.values[dsv_l23.values < 1.0])
            dsv_complex = numpy.append(
                dsv_l4.values[dsv_l4.values > 1.0], dsv_l23.values[dsv_l23.values > 1.0])

            simple_mr = numpy.append(numpy.array(dsv_l4.get_value_by_id(l4_ids))[numpy.array(dsv_l4.get_value_by_id(
                l4_ids)) < 1.0], numpy.array(dsv_l23.get_value_by_id(l23_ids))[numpy.array(dsv_l23.get_value_by_id(l23_ids)) < 1.0])
            complex_mr = numpy.append(numpy.array(dsv_l4.get_value_by_id(l4_ids))[numpy.array(dsv_l4.get_value_by_id(
                l4_ids)) > 1.0], numpy.array(dsv_l23.get_value_by_id(l23_ids))[numpy.array(dsv_l23.get_value_by_id(l23_ids)) > 1.0])

            simple_v_mr = numpy.append(l4_v_mr[numpy.array(dsv_l4.get_value_by_id(
                l4_ids)) < 1.0], l23_v_mr[numpy.array(dsv_l23.get_value_by_id(l23_ids)) < 1.0])
            complex_v_mr = numpy.append(l4_v_mr[numpy.array(dsv_l4.get_value_by_id(
                l4_ids)) > 1.0], l23_v_mr[numpy.array(dsv_l23.get_value_by_id(l23_ids)) > 1.0])

            dsv_simple_v_F0 = numpy.append(numpy.array(dsv_l4_v_F0[0].get_value_by_id(l4_ids))[numpy.array(dsv_l4.get_value_by_id(
                l4_ids)) < 1.0], numpy.array(dsv_l23_v_F0[0].get_value_by_id(l23_ids))[numpy.array(dsv_l23.get_value_by_id(l23_ids)) < 1.0])
            dsv_complex_v_F0 = numpy.append(numpy.array(dsv_l4_v_F0[0].get_value_by_id(l4_ids))[numpy.array(dsv_l4.get_value_by_id(
                l4_ids)) > 1.0], numpy.array(dsv_l23_v_F0[0].get_value_by_id(l23_ids))[numpy.array(dsv_l23.get_value_by_id(l23_ids)) > 1.0])

            dsv_simple_v_F1 = numpy.append(numpy.array(dsv_l4_v_F1[0].get_value_by_id(l4_ids))[numpy.array(dsv_l4.get_value_by_id(
                l4_ids)) < 1.0], numpy.array(dsv_l23_v_F1[0].get_value_by_id(l23_ids))[numpy.array(dsv_l23.get_value_by_id(l23_ids)) < 1.0])
            dsv_complex_v_F1 = numpy.append(numpy.array(dsv_l4_v_F1[0].get_value_by_id(l4_ids))[numpy.array(dsv_l4.get_value_by_id(
                l4_ids)) > 1.0], numpy.array(dsv_l23_v_F1[0].get_value_by_id(l23_ids))[numpy.array(dsv_l23.get_value_by_id(l23_ids)) > 1.0])
        else:
            dsv_simple = dsv_l4.values[dsv_l4.values < 1.0]
            dsv_complex = dsv_l4.values[dsv_l4.values > 1.0]

            simple_mr = numpy.array(dsv_l4.get_value_by_id(l4_ids))[numpy.array(dsv_l4.get_value_by_id(l4_ids)) < 1.0]
            complex_mr = numpy.array(dsv_l4.get_value_by_id(l4_ids))[numpy.array(dsv_l4.get_value_by_id(l4_ids)) > 1.0]
            simple_v_mr = l4_v_mr[numpy.array(dsv_l4.get_value_by_id(l4_ids)) < 1.0]
            complex_v_mr = l4_v_mr[numpy.array(dsv_l4.get_value_by_id(l4_ids)) > 1.0]

            dsv_simple_v_F0 = numpy.array(dsv_l4_v_F0[0].get_value_by_id(l4_ids))[numpy.array(dsv_l4.get_value_by_id(l4_ids)) < 1.0]
            dsv_complex_v_F0 = numpy.array(dsv_l4_v_F0[0].get_value_by_id(l4_ids))[numpy.array(dsv_l4.get_value_by_id(l4_ids)) > 1.0]

            dsv_simple_v_F1 = numpy.array(dsv_l4_v_F1[0].get_value_by_id(l4_ids))[numpy.array(dsv_l4.get_value_by_id(l4_ids)) < 1.0]
            dsv_complex_v_F1 = numpy.array(dsv_l4_v_F1[0].get_value_by_id(l4_ids))[numpy.array(dsv_l4.get_value_by_id(l4_ids)) > 1.0]

        gs = gridspec.GridSpecFromSubplotSpec(
            3, 7, subplot_spec=gs, wspace=0.3)
        ax = pylab.subplot(gs[0, 0])
        ax.hist(dsv_l4.values, bins=numpy.arange(
            0, 2.01, 0.2), color='gray', rwidth=0.8)
        disable_top_right_axis(ax)
        disable_left_axis(ax)
        pylab.ylim(0, 540)
        disable_xticks(ax)
        remove_x_tick_labels()
        remove_y_tick_labels()
        pylab.ylabel('Layer 4', fontsize=19)
        ax = pylab.subplot(gs[1, 0])
        if self.parameters.ComplexSheetName != 'None':
            ax.hist(dsv_l23.values, bins=numpy.arange(
                0, 2.01, 0.2), color='gray', rwidth=0.8)
            disable_top_right_axis(ax)
            disable_left_axis(ax)
            pylab.ylim(0, 540)
            disable_xticks(ax)
            remove_x_tick_labels()
            remove_y_tick_labels()
            pylab.ylabel('Layer 2/3', fontsize=19)

            ax = pylab.subplot(gs[2, 0])
            ax.hist([dsv_complex, dsv_simple], bins=numpy.arange(
                0, 2.01, 0.2), histtype='barstacked', color=['w', 'k'], rwidth=0.8, ec='black')
            disable_top_right_axis(ax)
            disable_left_axis(ax)
            pylab.ylim(0, 540)
            pylab.ylabel('Pooled', fontsize=19)
            ax.set_xticks([0,1,2])
            remove_y_tick_labels()
            pylab.xlabel('F1/F0 spikes', fontsize=19)
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontsize(19)
            disable_top_right_axis(ax)
            disable_left_axis(ax)

        ax = pylab.subplot(gs[0, 1])
        ax.hist(l4_v_mr, bins=numpy.arange(
            0, 5.01, 0.5), color='gray', rwidth=0.8)
        disable_top_right_axis(ax)
        disable_left_axis(ax)
        disable_xticks(ax)
        remove_x_tick_labels()
        remove_y_tick_labels()
        pylab.xlim(0, 5.0)

        if self.parameters.ComplexSheetName != 'None':
            ax = pylab.subplot(gs[1, 1])
            ax.hist(l23_v_mr, bins=numpy.arange(
                0, 5.01, 0.5), color='gray', rwidth=0.8)
            disable_top_right_axis(ax)
            disable_left_axis(ax)
            disable_xticks(ax)
            remove_x_tick_labels()
            remove_y_tick_labels()
            pylab.xlim(0, 5.0)
            ax = pylab.subplot(gs[2, 1])
            ax.hist([complex_v_mr, simple_v_mr], bins=numpy.arange(
                0, 5.01, 0.5), histtype='barstacked', color=['w', 'k'], rwidth=0.8, ec='black')
            three_tick_axis(ax.xaxis)
            remove_y_tick_labels()
            pylab.xlabel('F1/F0 Vm', fontsize=19)
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontsize(19)
            disable_top_right_axis(ax)
            disable_left_axis(ax)
            pylab.xlim(0, 5.0)

        ax = pylab.subplot(gs[0, 2])
        ax.hist(numpy.abs(dsv_l4_v_F0[0].get_value_by_id(l4_ids)), bins=numpy.arange(
            0, 3.01, 0.3), color='gray', rwidth=0.8)
        disable_top_right_axis(ax)
        disable_left_axis(ax)
        disable_left_axis(ax)
        disable_xticks(ax)
        remove_x_tick_labels()
        remove_y_tick_labels()
        pylab.xlim(0, 3.0)

        if self.parameters.ComplexSheetName != 'None':
            ax = pylab.subplot(gs[1, 2])
            ax.hist(numpy.abs(dsv_l23_v_F0[0].get_value_by_id(l23_ids)), bins=numpy.arange(
                0, 3.01, 0.3), color='gray', rwidth=0.8)
            disable_top_right_axis(ax)
            disable_left_axis(ax)
            disable_xticks(ax)
            remove_x_tick_labels()
            remove_y_tick_labels()
            pylab.xlim(0, 3.0)
            ax = pylab.subplot(gs[2, 2])
            ax.hist([numpy.abs(dsv_complex_v_F0), numpy.abs(dsv_simple_v_F0)], bins=numpy.arange(
                0, 3.01, 0.3), histtype='barstacked', color=['w', 'k'], rwidth=0.8, ec='black')
            three_tick_axis(ax.xaxis)
            remove_y_tick_labels()
            pylab.xlabel('F0 Vm (mV)', fontsize=19)
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontsize(19)
            disable_top_right_axis(ax)
            disable_left_axis(ax)
            pylab.xlim(0, 3.0)

        ax = pylab.subplot(gs[0, 3])
        ax.hist(numpy.abs(dsv_l4_v_F1[0].get_value_by_id(l4_ids)), bins=numpy.arange(
            0, 10.01, 1), color='gray', rwidth=0.8)
        disable_top_right_axis(ax)
        disable_left_axis(ax)
        disable_xticks(ax)
        remove_x_tick_labels()
        remove_y_tick_labels()
        pylab.xlim(0, 10.0)

        if self.parameters.ComplexSheetName != 'None':
            ax = pylab.subplot(gs[1, 3])
            ax.hist(numpy.abs(dsv_l23_v_F1[0].get_value_by_id(l23_ids)), bins=numpy.arange(
                0, 10.01, 1), color='gray', rwidth=0.8)
            disable_top_right_axis(ax)
            disable_left_axis(ax)
            disable_xticks(ax)
            remove_x_tick_labels()
            remove_y_tick_labels()
            pylab.xlim(0, 10.0)
            ax = pylab.subplot(gs[2, 3])
            ax.hist([numpy.abs(dsv_complex_v_F1), numpy.abs(dsv_simple_v_F1)], bins=numpy.arange(
                0, 10.01, 1), histtype='barstacked', color=['w', 'k'], rwidth=0.8, ec='black')
            three_tick_axis(ax.xaxis)
            remove_y_tick_labels()
            pylab.xlabel('F1 Vm (mV)', fontsize=19)
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontsize(19)
            disable_top_right_axis(ax)
            disable_left_axis(ax)
            pylab.xlim(0, 10.0)

        logger.info(len(simple_v_mr))
        logger.info(len(dsv_simple))
        if self.parameters.ComplexSheetName != 'None':
            ggs = gridspec.GridSpecFromSubplotSpec(20, 20, gs[:, 4:7])
            ax = pylab.subplot(ggs[3:18, 3:18])
            ax.plot(complex_v_mr, complex_mr, 'ok', label='layer 2/3')
            ax.plot(simple_v_mr, simple_mr, 'ok', label='layer 4')
            pylab.xlabel('F1/F0 Vm', fontsize=19)
            pylab.ylabel('F1/F0 Spikes', fontsize=19)
            pylab.xlim(0, 5.0)
            pylab.ylim(0, 2.0)
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontsize(19)

        if self.plot_file_name:
            pylab.savefig(Global.root_directory+self.plot_file_name)

class LSV1MReponseOverview(Plotting):
    required_parameters = ParameterSet({
        'l4_exc_neuron' : int,
        'l4_inh_neuron' : int,
        'l23_exc_neuron' : int,
        'l23_inh_neuron' : int,
    })

    def subplot(self, subplotspec):
        plots = {}
        gs = gridspec.GridSpecFromSubplotSpec(19, 68, subplot_spec=subplotspec,hspace=1.0, wspace=100.0)



        dsv = param_filter_query(self.datastore,st_name='FullfieldDriftingSinusoidalGrating',st_orientation=[0],st_contrast=[100])
        plots['ExcOr0L4'] = (OverviewPlot(dsv, ParameterSet({'sheet_name' : 'V1_Exc_L4', 'neuron' : self.parameters.l4_exc_neuron, 'sheet_activity' : {}, 'spontaneous' : False})),gs[0:9,0:16],{'x_label': None,'x_axis' : False, 'x_ticks' : False })

        dsv = param_filter_query(self.datastore,st_name='FullfieldDriftingSinusoidalGrating',st_orientation=[numpy.pi/2],st_contrast=[100])
        plots['ExcOrPiHL4'] = (OverviewPlot(dsv, ParameterSet({'sheet_name' : 'V1_Exc_L4', 'neuron' : self.parameters.l4_exc_neuron, 'sheet_activity' : {}, 'spontaneous' : False})),gs[0:9,17:33],{'x_label': None,'y_label': None,'x_axis' : False, 'x_ticks' : False,'y_axis' : False, 'y_ticks' : False})

        dsv = param_filter_query(self.datastore,st_name='FullfieldDriftingSinusoidalGrating',st_orientation=[0],st_contrast=[100])
        plots['InhOr0L4'] = (OverviewPlot(dsv, ParameterSet({'sheet_name' : 'V1_Inh_L4', 'neuron' : self.parameters.l4_inh_neuron, 'sheet_activity' : {}, 'spontaneous' : False})),gs[0:9,35:51],{'x_label': None,'y_label': None, 'title' : None,'y_axis' : False, 'y_ticks' : False,'x_axis' : False, 'x_ticks' : False})

        dsv = param_filter_query(self.datastore,st_name='FullfieldDriftingSinusoidalGrating',st_orientation=[numpy.pi/2],st_contrast=[100])
        plots['ExcOrPiHL4'] = (OverviewPlot(dsv, ParameterSet({'sheet_name' : 'V1_Exc_L4', 'neuron' : self.parameters.l4_exc_neuron, 'sheet_activity' : {}, 'spontaneous' : False})),gs[0:9,17:33],{'x_label': None,'y_label': None,'x_axis' : False, 'x_ticks' : False,'y_axis' : False, 'y_ticks' : False})

        dsv = param_filter_query(self.datastore,st_name='FullfieldDriftingSinusoidalGrating',st_orientation=[0],st_contrast=[100])
        plots['InhOr0L4'] = (OverviewPlot(dsv, ParameterSet({'sheet_name' : 'V1_Inh_L4', 'neuron' : self.parameters.l4_inh_neuron, 'sheet_activity' : {}, 'spontaneous' : False})),gs[0:9,35:51],{'x_label': None,'y_label': None, 'title' : None,'y_axis' : False, 'y_ticks' : False,'x_axis' : False, 'x_ticks' : False})

        dsv = param_filter_query(self.datastore,st_name='FullfieldDriftingSinusoidalGrating',st_orientation=[numpy.pi/2],st_contrast=[100])
        plots['InhOrPiHL4'] = (OverviewPlot(dsv, ParameterSet({'sheet_name' : 'V1_Inh_L4', 'neuron' : self.parameters.l4_inh_neuron, 'sheet_activity' : {}, 'spontaneous' : False})),gs[0:9,52:68],{'x_label': None,'y_label': None, 'title' : None,'y_axis' : False, 'y_ticks' : False,'x_axis' : False, 'x_ticks' : False})


        def stim_plot(phase):
            x = numpy.arange(0,2,0.01)
            pylab.plot(x,numpy.sin(x*numpy.pi*4+phase),'g',linewidth=3)
            phf.disable_top_right_axis(self.axis)
            phf.disable_xticks(self.axis)
            phf.disable_yticks(self.axis)
            phf.remove_x_tick_labels()
            phf.remove_y_tick_labels()
            self.axis.set_ylim(-1.3,1.3)
            self.axis.set_xlim(0,2)

        self.axis = pylab.subplot(gs[9:10,0:16])
        stim_plot(8*numpy.pi/16)
        self.axis = pylab.subplot(gs[9:10,35:51])
        stim_plot(7*numpy.pi/16)

        dsv = param_filter_query(self.datastore,st_name='FullfieldDriftingSinusoidalGrating',st_orientation=[0],st_contrast=[100])
        plots['ExcOr0L23'] = (OverviewPlot(dsv, ParameterSet({'sheet_name' : 'V1_Exc_L2/3', 'neuron' : self.parameters.l23_exc_neuron, 'sheet_activity' : {}, 'spontaneous' : False})),gs[10:,0:16],{'title' : None})

        dsv = param_filter_query(self.datastore,st_name='FullfieldDriftingSinusoidalGrating',st_orientation=[numpy.pi/2],st_contrast=[100])
        plots['ExcOrPiHL23'] = (OverviewPlot(dsv, ParameterSet({'sheet_name' : 'V1_Exc_L2/3', 'neuron' : self.parameters.l23_exc_neuron, 'sheet_activity' : {}, 'spontaneous' : False})),gs[10:,17:33],{'y_label': None, 'title' : None,'y_axis' : False, 'y_ticks' : False})

        dsv = param_filter_query(self.datastore,st_name='FullfieldDriftingSinusoidalGrating',st_orientation=[0],st_contrast=[100])
        plots['InhOr0L23'] = (OverviewPlot(dsv, ParameterSet({'sheet_name' : 'V1_Inh_L2/3', 'neuron' : self.parameters.l23_inh_neuron, 'sheet_activity' : {}, 'spontaneous' : False})),gs[10:,35:51],{'y_label': None, 'title' : None,'y_axis' : False, 'y_ticks' : False})

        dsv = param_filter_query(self.datastore,st_name='FullfieldDriftingSinusoidalGrating',st_orientation=[numpy.pi/2],st_contrast=[100])
        plots['InhOrPiHL23'] = (OverviewPlot(dsv, ParameterSet({'sheet_name' : 'V1_Inh_L2/3', 'neuron' : self.parameters.l23_inh_neuron, 'sheet_activity' : {}, 'spontaneous' : False})),gs[10:,52:68],{'y_label': None, 'title' : None,'y_axis' : False, 'y_ticks' : False})

        return plots

class SpontActOverview(Plotting):

    """
    This figure shows example of spontaneous activity in the model. 
      
    Parameters
    ----------
    l4_exc_neuron : str
               The name of the sheet corresponding to layer 4 excitatory neurons.
              
    l23_exc_neuron : str
          The name of the sheet corresponding to layer 2/3 excitatory neurons.


    l4_inh_neuron : str
               The name of the sheet corresponding to layer 4 inhibitory neurons.
              
    l23_inh_neuron : str
          The name of the sheet corresponding to layer 2/3 inhibitory neurons.

    """

    required_parameters = ParameterSet({
        'l4_exc_neuron' : int,
        'l4_inh_neuron' : int,
        'l23_exc_neuron' : int,
        'l23_inh_neuron' : int,
    })

    def subplot(self, subplotspec):
        plots = {}
        gs = gridspec.GridSpecFromSubplotSpec(12,3, subplot_spec=subplotspec,hspace=0.3, wspace=0.45)
        dsv = param_filter_query(self.datastore,st_direct_stimulation_name=None,st_name=['InternalStimulus'])

        fontsize=14
        
        analog_ids1 = sorted(numpy.random.permutation(queries.param_filter_query(self.datastore,sheet_name='V1_Exc_L4').get_segments()[0].get_stored_esyn_ids()))
        
        tstop = queries.param_filter_query(self.datastore,st_direct_stimulation_name=None,st_name="InternalStimulus",sheet_name = 'V1_Exc_L4').get_segments()[0].get_vm(analog_ids1[0]).t_stop.magnitude
        tstop = min(min(tstop,5000),tstop)
        
        spike_ids = param_filter_query(self.datastore,sheet_name="V1_Exc_L4").get_segments()[0].get_stored_spike_train_ids()
        spike_ids_inh = param_filter_query(self.datastore,sheet_name="V1_Inh_L4").get_segments()[0].get_stored_spike_train_ids()
        if self.parameters.l23_exc_neuron != -1:
            spike_ids23 = param_filter_query(self.datastore,sheet_name="V1_Exc_L2/3").get_segments()[0].get_stored_spike_train_ids()
            spike_ids_inh23 = param_filter_query(self.datastore,sheet_name="V1_Inh_L2/3").get_segments()[0].get_stored_spike_train_ids()
        
        if self.parameters.l23_exc_neuron != -1:
            d = int(numpy.min([numpy.floor(len(spike_ids)/4.0),len(spike_ids_inh),numpy.floor(len(spike_ids23)/4.0),len(spike_ids_inh23)]))
            d = min([100,d])
            neuron_ids = [spike_ids_inh23[:d],spike_ids23[:d*4],spike_ids_inh[:d],spike_ids[:d*4]]
        else:
            d = int(numpy.min([numpy.floor(len(spike_ids)/4.0),len(spike_ids_inh)]))
            d = min([100,d])
            neuron_ids = [spike_ids_inh[:d],spike_ids[:d*4]]
    
    
        if self.parameters.l23_exc_neuron != -1:
            plots['SpikingOverview'] = (CorticalColumnRasterPlot(dsv,ParameterSet({'spontaneous' : False, 'sheet_names' : ['V1_Inh_L2/3','V1_Exc_L2/3','V1_Inh_L4','V1_Exc_L4'], 'neurons' : neuron_ids, 'colors' : ['#0000FF', '#FF0000' , '#0000FF', '#FF0000'], 'labels' : ["L2/3i","L2/3e" , "L4i", "L4e"]})),gs[:,0],{'fontsize' : fontsize,'x_lim' : (0,tstop/1000)})
            plots['ExcL2/3Cond'] = (GSynPlot(dsv, ParameterSet({'sheet_name' : 'V1_Exc_L2/3', 'neuron' : self.parameters.l23_exc_neuron, 'separated' : True, 'spontaneous' : False})),gs[6:8,1:],{'x_label': None,'fontsize' : fontsize, 'x_ticks' : [],'title' : None,'x_lim' : (0,tstop),'y_lim' : (0,15),'y_axis' : None})
            plots['ExcL2/3Vm'] = (VmPlot(dsv, ParameterSet({'sheet_name' : 'V1_Exc_L2/3', 'neuron' : self.parameters.l23_exc_neuron, 'spontaneous' : False})),gs[8,1:],{'x_label': None,'fontsize' : fontsize, 'x_ticks' : [],'title' : None,'x_lim' : (0,tstop),'y_axis' : None})
            plots['InhL2/3Cond'] = (GSynPlot(dsv, ParameterSet({'sheet_name' : 'V1_Inh_L2/3', 'neuron' : self.parameters.l23_inh_neuron, 'separated' : True, 'spontaneous' : False})),gs[9:11,1:],{'x_label': None,'fontsize' : fontsize, 'x_ticks' : [],'title' : None,'x_lim' : (0,tstop),'y_lim' : (0,15)})
            plots['InhL2/3Vm'] = (VmPlot(dsv, ParameterSet({'sheet_name' : 'V1_Inh_L2/3', 'neuron' : self.parameters.l23_inh_neuron, 'spontaneous' : False})),gs[11,1:],{'fontsize' : fontsize, 'x_ticks' : None,'title' : None,'x_lim' : (0,tstop)})
        else:
            plots['SpikingOverview'] = (CorticalColumnRasterPlot(dsv,ParameterSet({'spontaneous' : False, 'sheet_names' : ['V1_Inh_L4','V1_Exc_L4'], 'neurons' : neuron_ids, 'colors' : ['#666666', '#000000'], 'labels' : ["L4i","L4e" ]})),gs[:,0],{'fontsize' : fontsize,'x_lim' : (0,tstop/1000)})
            
        plots['ExcL4Cond'] = (GSynPlot(dsv, ParameterSet({'sheet_name' : 'V1_Exc_L4', 'neuron' : self.parameters.l4_exc_neuron, 'separated' : True, 'spontaneous' : False})),gs[0:2,1:],{'x_label': None,'fontsize' : fontsize, 'x_ticks' : [],'title' : None,'x_lim' : (0,tstop),'y_lim' : (0,15),'y_axis' : None})
        plots['ExcL4Vm'] = (VmPlot(dsv, ParameterSet({'sheet_name' : 'V1_Exc_L4', 'neuron' : self.parameters.l4_exc_neuron, 'spontaneous' : False})),gs[2,1:],{'x_label': None,'fontsize' : fontsize, 'x_ticks' : [],'title' : None,'x_lim' : (0,tstop),'y_axis' : None})
        plots['InhL4Cond'] = (GSynPlot(dsv, ParameterSet({'sheet_name' : 'V1_Inh_L4', 'neuron' : self.parameters.l4_inh_neuron, 'separated' : True, 'spontaneous' : False})),gs[3:5,1:],{'x_label': None,'fontsize' : fontsize, 'x_ticks' : [],'title' : None,'x_lim' : (0,tstop),'y_lim' : (0,15),'y_axis' : None})
        plots['InhL4Vm'] = (VmPlot(dsv, ParameterSet({'sheet_name' : 'V1_Inh_L4', 'neuron' : self.parameters.l4_inh_neuron, 'spontaneous' : False})),gs[5,1:],{'x_label': None,'fontsize' : fontsize,'title' : None,'x_ticks' : [],'x_lim' : (0,tstop),'y_axis' : None})
                
        return plots


class SpontStatisticsOverview(Plotting):
    required_parameters = ParameterSet({

    })

    def subplot(self, subplotspec):
        plots = {}
        gs = gridspec.GridSpecFromSubplotSpec(12,4, subplot_spec=subplotspec,hspace=10.0, wspace=0.5)
        dsv = param_filter_query(self.datastore,st_direct_stimulation_name=None,st_name=['InternalStimulus'])    
        
        l23_flag = len(param_filter_query(self.datastore,st_direct_stimulation_name=None,st_name='InternalStimulus',analysis_algorithm='PopulationMeanAndVar',sheet_name='V1_Exc_L2/3',identifier='SingleValue',value_name='Mean(Firing rate)').get_analysis_result()) != 0
        
        fontsize=15

        spike_ids = numpy.array(param_filter_query(self.datastore,sheet_name="V1_Exc_L4").get_segments()[0].get_stored_spike_train_ids())
        spike_ids_inh = numpy.array(param_filter_query(self.datastore,sheet_name="V1_Inh_L4").get_segments()[0].get_stored_spike_train_ids())
        idx4_inh = self.datastore.get_sheet_indexes(sheet_name='V1_Inh_L4',neuron_ids=spike_ids_inh)
        idx4 = self.datastore.get_sheet_indexes(sheet_name='V1_Exc_L4',neuron_ids=spike_ids)

        if l23_flag:
           spike_ids23 = numpy.array(param_filter_query(self.datastore,sheet_name="V1_Exc_L2/3").get_segments()[0].get_stored_spike_train_ids())
           spike_ids_inh23 = numpy.array(param_filter_query(self.datastore,sheet_name="V1_Inh_L2/3").get_segments()[0].get_stored_spike_train_ids())
           idx23 = self.datastore.get_sheet_indexes(sheet_name='V1_Exc_L2/3',neuron_ids=spike_ids23)
           idx23_inh = self.datastore.get_sheet_indexes(sheet_name='V1_Inh_L2/3',neuron_ids=spike_ids_inh23)

        # center neurons
        x = self.datastore.get_neuron_positions()['V1_Exc_L4'][0][idx4]
        y = self.datastore.get_neuron_positions()['V1_Exc_L4'][1][idx4]
        center4 = spike_ids[numpy.nonzero(numpy.sqrt(numpy.multiply(x,x)+numpy.multiply(y,y)) < 0.5)[0]]

        x = self.datastore.get_neuron_positions()['V1_Inh_L4'][0][idx4_inh]
        y = self.datastore.get_neuron_positions()['V1_Inh_L4'][1][idx4_inh]
        center4_inh = spike_ids_inh[numpy.nonzero(numpy.sqrt(numpy.multiply(x,x)+numpy.multiply(y,y)) < 0.5)[0]]

        if l23_flag:
           x = self.datastore.get_neuron_positions()['V1_Exc_L2/3'][0][idx23]
           y = self.datastore.get_neuron_positions()['V1_Exc_L2/3'][1][idx23]
           center23 = spike_ids23[numpy.nonzero(numpy.sqrt(numpy.multiply(x,x)+numpy.multiply(y,y)) < 0.5)[0]]

           x = self.datastore.get_neuron_positions()['V1_Inh_L2/3'][0][idx23_inh]
           y = self.datastore.get_neuron_positions()['V1_Inh_L2/3'][1][idx23_inh]
           center23_inh = spike_ids_inh23[numpy.nonzero(numpy.sqrt(numpy.multiply(x,x)+numpy.multiply(y,y)) < 0.5)[0]]

        
        mean_firing_rate_L4E = param_filter_query(self.datastore,st_direct_stimulation_name=None,st_name='InternalStimulus',analysis_algorithm='PopulationMeanAndVar',sheet_name='V1_Exc_L4',identifier='SingleValue',value_name='Mean(Firing rate)',ads_unique=True).get_analysis_result()[0].value
        mean_firing_rate_L4I = param_filter_query(self.datastore,st_direct_stimulation_name=None,st_name='InternalStimulus',analysis_algorithm='PopulationMeanAndVar',sheet_name='V1_Inh_L4',identifier='SingleValue',value_name='Mean(Firing rate)',ads_unique=True).get_analysis_result()[0].value
        std_firing_rate_L4E = numpy.sqrt(param_filter_query(self.datastore,st_direct_stimulation_name=None,st_name='InternalStimulus',analysis_algorithm='PopulationMeanAndVar',sheet_name='V1_Exc_L4',identifier='SingleValue',value_name='Var(Firing rate)',ads_unique=True).get_analysis_result()[0].value)
        std_firing_rate_L4I = numpy.sqrt(param_filter_query(self.datastore,st_direct_stimulation_name=None,st_name='InternalStimulus',analysis_algorithm='PopulationMeanAndVar',sheet_name='V1_Inh_L4',identifier='SingleValue',value_name='Var(Firing rate)',ads_unique=True).get_analysis_result()[0].value)
        
        if l23_flag:
            mean_firing_rate_L23E = param_filter_query(self.datastore,st_direct_stimulation_name=None,st_name='InternalStimulus',analysis_algorithm='PopulationMeanAndVar',sheet_name='V1_Exc_L2/3',identifier='SingleValue',value_name='Mean(Firing rate)',ads_unique=True).get_analysis_result()[0].value
            mean_firing_rate_L23I = param_filter_query(self.datastore,st_direct_stimulation_name=None,st_name='InternalStimulus',analysis_algorithm='PopulationMeanAndVar',sheet_name='V1_Inh_L2/3',identifier='SingleValue',value_name='Mean(Firing rate)',ads_unique=True).get_analysis_result()[0].value
            std_firing_rate_L23E = numpy.sqrt(param_filter_query(self.datastore,st_direct_stimulation_name=None,st_name='InternalStimulus',analysis_algorithm='PopulationMeanAndVar',sheet_name='V1_Exc_L2/3',identifier='SingleValue',value_name='Var(Firing rate)',ads_unique=True).get_analysis_result()[0].value)
            std_firing_rate_L23I = numpy.sqrt(param_filter_query(self.datastore,st_direct_stimulation_name=None,st_name='InternalStimulus',analysis_algorithm='PopulationMeanAndVar',sheet_name='V1_Inh_L2/3',identifier='SingleValue',value_name='Var(Firing rate)',ads_unique=True).get_analysis_result()[0].value)
        else:
            mean_firing_rate_L23E = 0
            mean_firing_rate_L23I = 0
            std_firing_rate_L23E = 0
            std_firing_rate_L23I = 0
            


        logger.info('mean_firing_rate_L4E :' + str(mean_firing_rate_L4E))
        logger.info('mean_firing_rate_L4I :' + str(mean_firing_rate_L4I))
        logger.info('mean_firing_rate_L23E :' + str(mean_firing_rate_L23E))
        logger.info('mean_firing_rate_L23I :' + str(mean_firing_rate_L23I))
                
        mean_and_std = lambda x : (numpy.mean(x),numpy.std(x))
        s = queries.param_filter_query(
            self.datastore, st_name='InternalStimulus', sheet_name='V1_Exc_L4').get_segments()[0]
        isis = [numpy.diff(st.magnitude) for st in s.spiketrains]
        idxs = numpy.array([len(isi) for isi in isis]) > 5
        mean_CV_L4E, std_CV_L4E = mean_and_std(numpy.array(
            [numpy.std(isi)/numpy.mean(isi) for isi in isis])[idxs])
        s = queries.param_filter_query(self.datastore, st_name='InternalStimulus', sheet_name='V1_Exc_L4',
                                       value_name='Correlation coefficient(psth (bin=10.0))', ads_unique=True).get_analysis_result()[0]
        mean_CC_L4E, std_CC_L4E = mean_and_std(numpy.array(
            s.values)[idxs, :][:, idxs][numpy.triu_indices(sum(idxs == True), 1)])

        s = queries.param_filter_query(
            self.datastore, st_name='InternalStimulus', sheet_name='V1_Inh_L4').get_segments()[0]
        isis = [numpy.diff(st.magnitude) for st in s.spiketrains]
        idxs = numpy.array([len(isi) for isi in isis]) > 5
        mean_CV_L4I, std_CV_L4I = mean_and_std(numpy.array(
            [numpy.std(isi)/numpy.mean(isi) for isi in isis])[idxs])
        s = queries.param_filter_query(self.datastore, st_name='InternalStimulus', sheet_name='V1_Inh_L4',
                                       value_name='Correlation coefficient(psth (bin=10.0))', ads_unique=True).get_analysis_result()[0]
        mean_CC_L4I, std_CC_L4I = mean_and_std(numpy.array(
            s.values)[idxs, :][:, idxs][numpy.triu_indices(sum(idxs == True), 1)])

        if l23_flag:
          s = queries.param_filter_query(
              self.datastore, st_name='InternalStimulus', sheet_name='V1_Exc_L2/3').get_segments()[0]
          isis = [numpy.diff(st.magnitude) for st in s.spiketrains]
          idxs = numpy.array([len(isi) for isi in isis]) > 5
          mean_CV_L23E, std_CV_L23E = mean_and_std(numpy.array(
              [numpy.std(isi)/numpy.mean(isi) for isi in isis])[idxs])
          s = queries.param_filter_query(self.datastore, st_name='InternalStimulus', sheet_name='V1_Exc_L2/3',
                                         value_name='Correlation coefficient(psth (bin=10.0))', ads_unique=True).get_analysis_result()[0]
          mean_CC_L23E, std_CC_L23E = mean_and_std(numpy.array(
              s.values)[idxs, :][:, idxs][numpy.triu_indices(sum(idxs == True), 1)])

          s = queries.param_filter_query(
            self.datastore, st_name='InternalStimulus', sheet_name='V1_Inh_L2/3').get_segments()[0]
          isis = [numpy.diff(st.magnitude) for st in s.spiketrains]
          idxs = numpy.array([len(isi) for isi in isis]) > 5
          mean_CV_L23I, std_CV_L23I = mean_and_std(numpy.array(
              [numpy.std(isi)/numpy.mean(isi) for isi in isis])[idxs])
          s = queries.param_filter_query(self.datastore, st_name='InternalStimulus', sheet_name='V1_Inh_L2/3',
                                       value_name='Correlation coefficient(psth (bin=10.0))', ads_unique=True).get_analysis_result()[0]
          mean_CC_L23I, std_CC_L23I = mean_and_std(numpy.array(
              s.values)[idxs, :][:, idxs][numpy.triu_indices(sum(idxs == True), 1)])
        else:
          mean_CV_L23E=0
          mean_CV_L23I=0
          mean_CC_L23E=0
          mean_CC_L23I=0
          std_CV_L23E=0
          std_CV_L23I=0
          std_CC_L23E=0
          std_CC_L23I=0

        
        logger.info('mean_CV_L4E :' + str(mean_CV_L4E))        
        logger.info('mean_CV_L4I :' + str(mean_CV_L4I))        
        logger.info('mean_CV_L23E :' + str(mean_CV_L23E))
        logger.info('mean_CV_L23I :' + str(mean_CV_L23I))        
            
        logger.info('mean_CC_L4E :' + str(mean_CC_L4E))        
        logger.info('mean_CC_L4I :' + str(mean_CC_L4I))        
        logger.info('mean_CC_L23E :' + str(mean_CC_L23E))
        logger.info('mean_CC_L23I :' + str(mean_CC_L23I))        
                
        
        ms = lambda a: (numpy.mean(a),numpy.std(a))
        mean_VM_L4E, std_VM_L4E = ms(param_filter_query(self.datastore,sheet_name='V1_Exc_L4',st_direct_stimulation_name=None,st_name=['InternalStimulus'],analysis_algorithm='Analog_MeanSTDAndFanoFactor',value_name='Mean(VM)',ads_unique=True).get_analysis_result()[0].values)
        mean_VM_L4I, std_VM_L4I= ms(param_filter_query(self.datastore,sheet_name='V1_Inh_L4',st_direct_stimulation_name=None,st_name=['InternalStimulus'],analysis_algorithm='Analog_MeanSTDAndFanoFactor',value_name='Mean(VM)',ads_unique=True).get_analysis_result()[0].values)
        if l23_flag:
            mean_VM_L23E, std_VM_L23E = ms(param_filter_query(self.datastore,sheet_name='V1_Exc_L2/3',st_direct_stimulation_name=None,st_name=['InternalStimulus'],analysis_algorithm='Analog_MeanSTDAndFanoFactor',value_name='Mean(VM)',ads_unique=True).get_analysis_result()[0].values)
            mean_VM_L23I, std_VM_L23I = ms(param_filter_query(self.datastore,sheet_name='V1_Inh_L2/3',st_direct_stimulation_name=None,st_name=['InternalStimulus'],analysis_algorithm='Analog_MeanSTDAndFanoFactor',value_name='Mean(VM)',ads_unique=True).get_analysis_result()[0].values)
        else:
            mean_VM_L23E, std_VM_L23E = 0,0
            mean_VM_L23I, std_VM_L23I = 0,0
        logger.info('mean_VM_L4E :' + str(mean_VM_L4E))        
        logger.info('mean_VM_L4I :' + str(mean_VM_L4I))        
        logger.info('mean_VM_L23E :' + str(mean_VM_L23E))
        logger.info('mean_VM_L23I :' + str(mean_VM_L23I))        
        
        
       
        mean_CondE_L4E, std_CondE_L4E = ms(param_filter_query(self.datastore,sheet_name='V1_Exc_L4',st_direct_stimulation_name=None,st_name=['InternalStimulus'],analysis_algorithm='Analog_MeanSTDAndFanoFactor',value_name='Mean(ECond)',ads_unique=True).get_analysis_result()[0].values)
        mean_CondE_L4I, std_CondE_L4I = ms(param_filter_query(self.datastore,sheet_name='V1_Inh_L4',st_direct_stimulation_name=None,st_name=['InternalStimulus'],analysis_algorithm='Analog_MeanSTDAndFanoFactor',value_name='Mean(ECond)',ads_unique=True).get_analysis_result()[0].values)
        if l23_flag:
            mean_CondE_L23E, std_CondE_L23E = ms(param_filter_query(self.datastore,sheet_name='V1_Exc_L2/3',st_direct_stimulation_name=None,st_name=['InternalStimulus'],analysis_algorithm='Analog_MeanSTDAndFanoFactor',value_name='Mean(ECond)',ads_unique=True).get_analysis_result()[0].values)
            mean_CondE_L23I, std_CondE_L23I = ms(param_filter_query(self.datastore,sheet_name='V1_Inh_L2/3',st_direct_stimulation_name=None,st_name=['InternalStimulus'],analysis_algorithm='Analog_MeanSTDAndFanoFactor',value_name='Mean(ECond)',ads_unique=True).get_analysis_result()[0].values)
        else:
            mean_CondE_L23E, std_CondE_L23E = 0,0
            mean_CondE_L23I, std_CondE_L23I = 0,0
        
        logger.info('mean_ECond :' + str((mean_CondE_L4E+0.25*mean_CondE_L4I+mean_CondE_L23E+0.25*mean_CondE_L23I)/2.5))
        
        mean_CondI_L4E, std_CondI_L4E = ms(param_filter_query(self.datastore,sheet_name='V1_Exc_L4',st_direct_stimulation_name=None,st_name=['InternalStimulus'],analysis_algorithm='Analog_MeanSTDAndFanoFactor',value_name='Mean(ICond)',ads_unique=True).get_analysis_result()[0].values)
        mean_CondI_L4I, std_CondI_L4I = ms(param_filter_query(self.datastore,sheet_name='V1_Inh_L4',st_direct_stimulation_name=None,st_name=['InternalStimulus'],analysis_algorithm='Analog_MeanSTDAndFanoFactor',value_name='Mean(ICond)',ads_unique=True).get_analysis_result()[0].values)
        if l23_flag:
            mean_CondI_L23E, std_CondI_L23E = ms(param_filter_query(self.datastore,sheet_name='V1_Exc_L2/3',st_direct_stimulation_name=None,st_name=['InternalStimulus'],analysis_algorithm='Analog_MeanSTDAndFanoFactor',value_name='Mean(ICond)',ads_unique=True).get_analysis_result()[0].values)
            mean_CondI_L23I, std_CondI_L23I = ms(param_filter_query(self.datastore,sheet_name='V1_Inh_L2/3',st_direct_stimulation_name=None,st_name=['InternalStimulus'],analysis_algorithm='Analog_MeanSTDAndFanoFactor',value_name='Mean(ICond)',ads_unique=True).get_analysis_result()[0].values)
        else:
            mean_CondI_L23E, std_CondI_L23E = 0,0
            mean_CondI_L23I, std_CondI_L23I = 0,0

        logger.info('mean_ICond :' + str((mean_CondI_L4E+0.25*mean_CondI_L4I+mean_CondI_L23E+0.25*mean_CondI_L23I)/2.5))
        
        
        pylab.rc('axes', linewidth=1)
        
        def plot_with_log_normal_fit(values,gs1,gs2,x_label=False,y_label=""):
            valuesnz = values[numpy.nonzero(values)[0]]
            h,bin_edges = numpy.histogram(numpy.log10(valuesnz),range=(-2,2),bins=20,density=True)
            bin_centers = bin_edges[:-1] + (bin_edges[1:] - bin_edges[:-1])/2.0
            
            m = numpy.mean(numpy.log10(valuesnz))
            nm = numpy.mean(valuesnz)
            s = numpy.std(numpy.log10(valuesnz))
            if s == 0: 
               s=1.0

            pylab.subplot(gs1)
            pylab.plot(numpy.logspace(-2,2,100),numpy.exp(-((numpy.log10(numpy.logspace(-2,2,100))-m)**2)/(2*s*s))/(s*numpy.sqrt(2*numpy.pi)),linewidth=4,color="#666666")
            pylab.plot(numpy.power(10,bin_centers),h,'ko',mec=None,mew=3)
            pylab.xlim(10**-2,10**2)
            pylab.gca().set_xscale("log")
            if x_label:
                pylab.xlabel('firing rate [sp/s]',fontsize=fontsize)
                pylab.xticks([0.01,0.1,1.0,10,100])
            else:
                pylab.xticks([])
            pylab.ylabel(y_label,fontsize=fontsize)                
            #pylab.yticks([0.0,0.5,1.0])
            for label in pylab.gca().get_xticklabels() + pylab.gca().get_yticklabels():
                label.set_fontsize(fontsize)
            phf.disable_top_right_axis(pylab.gca())
            
            pylab.subplot(gs2)
            pylab.plot(numpy.logspace(-1,2,100),numpy.exp(-((numpy.log10(numpy.logspace(-1,2,100))-m)**2)/(2*s*s))/(s*numpy.sqrt(2*numpy.pi)),linewidth=4,color="#666666")
            pylab.plot(numpy.logspace(-1,2,100),numpy.exp(-numpy.logspace(-1,2,100)/nm)/nm,'k--',linewidth=4)
            pylab.plot(numpy.power(10,bin_centers),h,'ko',mec=None,mew=3)
            pylab.xlim(10**-1,10**2)
            pylab.ylim(0.00001,5.0)
            pylab.gca().set_xscale("log")
            pylab.gca().set_yscale("log")
            if x_label:
                pylab.xlabel('firing rate [sp/s]',fontsize=fontsize)
                pylab.xticks([0.1,1.0,10,100])
            else:
                pylab.xticks([])
            pylab.yticks([0.0001,0.01,1.0])
            for label in pylab.gca().get_xticklabels() + pylab.gca().get_yticklabels():
                label.set_fontsize(fontsize)
            phf.disable_top_right_axis(pylab.gca())
        
        
        plot_with_log_normal_fit(param_filter_query(self.datastore,value_name=['Firing rate'],sheet_name=["V1_Exc_L4"],st_direct_stimulation_name=None,st_name=['InternalStimulus'],ads_unique=True).get_analysis_result()[0].values,gs[0:3,2],gs[0:3,3],y_label='L4e')
        plot_with_log_normal_fit(param_filter_query(self.datastore,value_name=['Firing rate'],sheet_name=["V1_Inh_L4"],st_direct_stimulation_name=None,st_name=['InternalStimulus'],ads_unique=True).get_analysis_result()[0].values,gs[3:6,2],gs[3:6,3],y_label='L4i')
        if l23_flag:
            plot_with_log_normal_fit(param_filter_query(self.datastore,value_name=['Firing rate'],sheet_name=["V1_Exc_L2/3"],st_direct_stimulation_name=None,st_name=['InternalStimulus'],ads_unique=True).get_analysis_result()[0].values,gs[6:9,2],gs[6:9,3],y_label='L2/3e')
            plot_with_log_normal_fit(param_filter_query(self.datastore,value_name=['Firing rate'],sheet_name=["V1_Inh_L2/3"],st_direct_stimulation_name=None,st_name=['InternalStimulus'],ads_unique=True).get_analysis_result()[0].values,gs[9:12,2],gs[9:12,3],x_label=True,y_label='L2/3i')

        def autolabel(rects,offset=0.35):
            # attach some text labels
            for rect in rects:
                height = rect.get_width()
                pylab.gca().text(rect.get_x() + rect.get_width() + abs(pylab.gca().get_xlim()[0] - pylab.gca().get_xlim()[1])*offset, rect.get_y()+0.012,
                        '%.2g' % float(height),
                        ha='center', va='bottom',fontsize=17)
        
        if True:
            pylab.subplot(gs[0:4,0])
            r1 = pylab.barh(numpy.array([0.17,0.67]),[mean_firing_rate_L23E,mean_firing_rate_L4E],height = 0.12,color='#000000',edgecolor='#000000',xerr=[std_firing_rate_L23E,std_firing_rate_L4E],error_kw=dict(ecolor='gray', lw=2, capsize=5, capthick=2))
            r2 = pylab.barh(numpy.array([0.33,0.83]),[mean_firing_rate_L23I,mean_firing_rate_L4I],height = 0.12,color='#FFFFFF',edgecolor='#000000',xerr=[std_firing_rate_L23I,std_firing_rate_L4I],error_kw=dict(ecolor='gray', lw=2, capsize=5, capthick=2))
            pylab.ylim(0,1.0)
            pylab.xlim(0,10.0)
            pylab.yticks([0.25,0.75],['L2/3','L4'])
            pylab.xlabel('firing rate (sp/s)',fontsize=fontsize)
            phf.three_tick_axis(pylab.gca().xaxis)
            for label in pylab.gca().get_xticklabels() + pylab.gca().get_yticklabels():
                label.set_fontsize(fontsize)
            phf.disable_top_right_axis(pylab.gca())
            autolabel(r1)
            autolabel(r2)

            
            pylab.subplot(gs[4:8,0])
            r1 = pylab.barh(numpy.array([0.17,0.67]),[mean_CV_L23E,mean_CV_L4E],height = 0.12,color='#000000',edgecolor='#000000',xerr=[std_CV_L23E,std_CV_L4E],error_kw=dict(ecolor='gray', lw=2, capsize=5, capthick=2))
            r2 = pylab.barh(numpy.array([0.33,0.83]),[mean_CV_L23I,mean_CV_L4I],height = 0.12,color='#FFFFFF',edgecolor='#000000',xerr=[std_CV_L23I,std_CV_L4I],error_kw=dict(ecolor='gray', lw=2, capsize=5, capthick=2))
            pylab.ylim(0,1.0)
            pylab.xlim(0,2.0)
            pylab.yticks([0.25,0.75],['L2/3','L4'])
            pylab.xlabel('irregularity',fontsize=fontsize)
            phf.three_tick_axis(pylab.gca().xaxis)
            for label in pylab.gca().get_xticklabels() + pylab.gca().get_yticklabels():
                label.set_fontsize(fontsize)
            phf.disable_top_right_axis(pylab.gca())     
            autolabel(r1,offset=0.37)
            autolabel(r2,offset=0.37)
       

            pylab.subplot(gs[8:12,0])
            r1 = pylab.barh(numpy.array([0.17,0.67]),[mean_CC_L23E,mean_CC_L4E],height = 0.12,color='#000000',edgecolor='#000000',xerr=[std_CC_L23E,std_CC_L4E],error_kw=dict(ecolor='gray', lw=2, capsize=5, capthick=2))
            r2 = pylab.barh(numpy.array([0.33,0.83]),[mean_CC_L23I,mean_CC_L4I],height = 0.12,color='#FFFFFF',edgecolor='#000000',xerr=[std_CC_L23I,std_CC_L4I],error_kw=dict(ecolor='gray', lw=2, capsize=5, capthick=2))
            pylab.ylim(0,1.0)
            pylab.xlim(0,0.15)
            pylab.yticks([0.25,0.75],['L2/3','L4'])
            pylab.xlabel('synchrony',fontsize=fontsize)
            phf.three_tick_axis(pylab.gca().xaxis)
            for label in pylab.gca().get_xticklabels() + pylab.gca().get_yticklabels():
                label.set_fontsize(fontsize)
            phf.disable_top_right_axis(pylab.gca())
            autolabel(r1,offset=0.6)
            autolabel(r2,offset=0.6)
            
            pylab.subplot(gs[0:4,1])
            r1 = pylab.barh(numpy.array([0.17,0.67]),[abs(mean_VM_L23E),numpy.abs(mean_VM_L4E)],height = 0.12,color='#000000',edgecolor='#000000',xerr=[std_VM_L23E,std_VM_L4E],error_kw=dict(ecolor='gray', lw=2, capsize=5, capthick=2))
            r2 = pylab.barh(numpy.array([0.33,0.83]),[abs(mean_VM_L23I),numpy.abs(mean_VM_L4I)],height = 0.12,color='#FFFFFF',edgecolor='#000000',xerr=[std_VM_L23I,std_VM_L4I],error_kw=dict(ecolor='gray', lw=2, capsize=5, capthick=2))
            pylab.ylim(0,1.0)
            pylab.xlim(40,80)
            pylab.xticks([40,60,80],[-40,-60,-80])
            pylab.yticks([0.25,0.75],['L2/3','L4'])
            pylab.xlabel('membrane potential (mV)',fontsize=fontsize)
            phf.three_tick_axis(pylab.gca().xaxis)
            for label in pylab.gca().get_xticklabels() + pylab.gca().get_yticklabels():
                label.set_fontsize(fontsize)
            phf.disable_top_right_axis(pylab.gca())
            autolabel(r1)
            autolabel(r2)

            pylab.subplot(gs[4:8,1])
            r1 = pylab.barh(numpy.array([0.17,0.67]),[mean_CondE_L23E*1000,mean_CondE_L4E*1000],height = 0.12,color='#000000',edgecolor='#000000',xerr=[std_CondE_L23E*1000,std_CondE_L4E*1000],error_kw=dict(ecolor='gray', lw=2, capsize=5, capthick=2))
            r2 = pylab.barh(numpy.array([0.33,0.83]),[mean_CondE_L23I*1000,mean_CondE_L4I*1000],height = 0.12,color='#FFFFFF',edgecolor='#000000',xerr=[std_CondE_L23I*1000,std_CondE_L4I*1000],error_kw=dict(ecolor='gray', lw=2, capsize=5, capthick=2))
            pylab.ylim(0,1.0)
            pylab.xlim(0,2.0)
            pylab.yticks([0.25,0.75],['L2/3','L4'])
            pylab.xlabel('excitatory conductance (nS)',fontsize=fontsize)
            phf.three_tick_axis(pylab.gca().xaxis)
            for label in pylab.gca().get_xticklabels() + pylab.gca().get_yticklabels():
                label.set_fontsize(fontsize)
            phf.disable_top_right_axis(pylab.gca())            
            autolabel(r1)
            autolabel(r2)

            pylab.subplot(gs[8:12,1])
            r1 = pylab.barh(numpy.array([0.17,0.67]),[mean_CondI_L23E*1000,mean_CondI_L4E*1000],height = 0.12,color='#000000',edgecolor='#000000',xerr=[std_CondI_L23E*1000,std_CondI_L4E*1000],error_kw=dict(ecolor='gray', lw=2, capsize=5, capthick=2))
            r2 = pylab.barh(numpy.array([0.33,0.83]),[mean_CondI_L23I*1000,mean_CondI_L4I*1000],height = 0.12,color='#FFFFFF',edgecolor='#000000',xerr=[std_CondI_L23I*1000,std_CondI_L4I*1000],error_kw=dict(ecolor='gray', lw=2, capsize=5, capthick=2))
            pylab.ylim(0,1.0)
            pylab.xlim(0,10)
            pylab.yticks([0.25,0.75],['L2/3','L4'])
            pylab.xlabel('inhibitory conductance (nS)',fontsize=fontsize)
            phf.three_tick_axis(pylab.gca().xaxis)
            for label in pylab.gca().get_xticklabels() + pylab.gca().get_yticklabels():
                label.set_fontsize(fontsize)
            phf.disable_top_right_axis(pylab.gca())
            autolabel(r1)
            autolabel(r2)
            
            pylab.rc('axes', linewidth=1)
        
        return plots


class OrientationTuningSummaryFiringRates(Plotting):

    """
    This figure plots summary of orientation tuning analysis in the model. 
      
    Parameters
    ----------
    exc_sheet_name1 : str
               The name of the sheet corresponding to layer 4 excitatory neurons.
              
    exc_sheet_name2 : str
          The name of the sheet corresponding to layer 2/3 excitatory neurons.


    inh_sheet_name1 : str
               The name of the sheet corresponding to layer 4 inhibitory neurons.
              
    inh_sheet_name2 : str
          The name of the sheet corresponding to layer 2/3 inhibitory neurons.

    """

    required_parameters = ParameterSet({
        'exc_sheet_name1': str,  # the name of the sheet for which to plot
        'inh_sheet_name1': str,  # the name of the sheet for which to plot
        'exc_sheet_name2': str,  # the name of the sheet for which to plot
        'inh_sheet_name2': str,  # the name of the sheet for which to plot
    })


    def subplot(self, subplotspec):
        plots = {}
        gs = gridspec.GridSpecFromSubplotSpec(27, 39, subplot_spec=subplotspec,
                                              hspace=1.0, wspace=5.0)
        
        mean_and_sem = lambda x : (numpy.mean(x),numpy.std(x)/numpy.sqrt(len(x)))

        spike_ids1 = numpy.array(sorted(numpy.random.permutation(queries.param_filter_query(self.datastore,sheet_name=self.parameters.exc_sheet_name1).get_segments()[0].get_stored_spike_train_ids())))
        spike_ids_inh1 = numpy.array(sorted(numpy.random.permutation(queries.param_filter_query(self.datastore,sheet_name=self.parameters.inh_sheet_name1).get_segments()[0].get_stored_spike_train_ids())))

        idxs = self.datastore.get_sheet_indexes(sheet_name=self.parameters.exc_sheet_name1,neuron_ids=spike_ids1)
        x = self.datastore.get_neuron_positions()[self.parameters.exc_sheet_name1][0][idxs]
        y = self.datastore.get_neuron_positions()[self.parameters.exc_sheet_name1][1][idxs]
        spike_ids1 = spike_ids1[numpy.nonzero(numpy.sqrt(numpy.multiply(x,x)+numpy.multiply(y,y)) < 0.9)[0]]

        idxs = self.datastore.get_sheet_indexes(sheet_name=self.parameters.inh_sheet_name1,neuron_ids=spike_ids_inh1)
        x = self.datastore.get_neuron_positions()[self.parameters.inh_sheet_name1][0][idxs]
        y = self.datastore.get_neuron_positions()[self.parameters.inh_sheet_name1][1][idxs]
        spike_ids_inh1 = spike_ids_inh1[numpy.nonzero(numpy.sqrt(numpy.multiply(x,x)+numpy.multiply(y,y)) < 0.9)[0]]

        if self.parameters.exc_sheet_name2 != 'None':
            spike_ids2 = numpy.array(sorted(numpy.random.permutation(queries.param_filter_query(self.datastore,sheet_name=self.parameters.exc_sheet_name2).get_segments()[0].get_stored_spike_train_ids())))
            spike_ids_inh2 = numpy.array(sorted(numpy.random.permutation(queries.param_filter_query(self.datastore,sheet_name=self.parameters.inh_sheet_name2).get_segments()[0].get_stored_spike_train_ids())))

            idxs = self.datastore.get_sheet_indexes(sheet_name=self.parameters.exc_sheet_name2,neuron_ids=spike_ids2)
            x = self.datastore.get_neuron_positions()[self.parameters.exc_sheet_name2][0][idxs]
            y = self.datastore.get_neuron_positions()[self.parameters.exc_sheet_name2][1][idxs]
            spike_ids2 = spike_ids2[numpy.nonzero(numpy.sqrt(numpy.multiply(x,x)+numpy.multiply(y,y)) < 0.9)[0]]

            idxs = self.datastore.get_sheet_indexes(sheet_name=self.parameters.inh_sheet_name2,neuron_ids=spike_ids_inh2)
            x = self.datastore.get_neuron_positions()[self.parameters.inh_sheet_name2][0][idxs]
            y = self.datastore.get_neuron_positions()[self.parameters.inh_sheet_name2][1][idxs]
            spike_ids_inh2 = spike_ids_inh2[numpy.nonzero(numpy.sqrt(numpy.multiply(x,x)+numpy.multiply(y,y)) < 0.9)[0]]

        spont_l4exc_pnv = param_filter_query(self.datastore,st_name='InternalStimulus',analysis_algorithm=['TrialAveragedFiringRate'],value_name='Firing rate',sheet_name="V1_Exc_L4",ads_unique=True).get_analysis_result()[0]
        spont_l4inh_pnv = param_filter_query(self.datastore,st_name='InternalStimulus',analysis_algorithm=['TrialAveragedFiringRate'],value_name='Firing rate',sheet_name="V1_Inh_L4",ads_unique=True).get_analysis_result()[0]

        if self.parameters.exc_sheet_name2 != 'None':
            spont_l23exc_pnv = param_filter_query(self.datastore,st_name='InternalStimulus',analysis_algorithm=['TrialAveragedFiringRate'],value_name='Firing rate',sheet_name=self.parameters.exc_sheet_name2,ads_unique=True).get_analysis_result()[0]
            spont_l23inh_pnv = param_filter_query(self.datastore,st_name='InternalStimulus',analysis_algorithm=['TrialAveragedFiringRate'],value_name='Firing rate',sheet_name=self.parameters.inh_sheet_name2,ads_unique=True).get_analysis_result()[0]

        r = 1.0
        base = queries.param_filter_query(self.datastore,sheet_name=self.parameters.exc_sheet_name1,st_name=['FullfieldDriftingSinusoidalGrating'],st_contrast=low_contrast,value_name=['orientation baseline of Firing rate'],ads_unique=True).get_analysis_result()[0].get_value_by_id(spike_ids1)
        mmax = queries.param_filter_query(self.datastore,sheet_name=self.parameters.exc_sheet_name1,st_name=['FullfieldDriftingSinusoidalGrating'],st_contrast=low_contrast,value_name=['orientation max of Firing rate'],ads_unique=True).get_analysis_result()[0].get_value_by_id(spike_ids1)
        err =queries.param_filter_query(self.datastore,sheet_name=self.parameters.exc_sheet_name1,st_name=['FullfieldDriftingSinusoidalGrating'],st_contrast=high_contrast,value_name=['orientation fitting error of Firing rate'],ads_unique=True).get_analysis_result()[0].get_value_by_id(spike_ids1)
        err_lc =queries.param_filter_query(self.datastore,sheet_name=self.parameters.exc_sheet_name1,st_name=['FullfieldDriftingSinusoidalGrating'],st_contrast=low_contrast,value_name=['orientation fitting error of Firing rate'],ads_unique=True).get_analysis_result()[0].get_value_by_id(spike_ids1)
        responsive_spike_ids1 = numpy.array(spike_ids1)[numpy.logical_and(numpy.logical_and(numpy.array(base)+numpy.array(mmax) > r, numpy.array(err) <= 0.3), numpy.array(err_lc) <= 0.3)]
        base = numpy.array(queries.param_filter_query(self.datastore,sheet_name=self.parameters.exc_sheet_name1,st_name=['FullfieldDriftingSinusoidalGrating'],st_contrast=high_contrast,value_name=['orientation baseline of Firing rate'],ads_unique=True).get_analysis_result()[0].get_value_by_id(responsive_spike_ids1))
        mmax = numpy.array(queries.param_filter_query(self.datastore,sheet_name=self.parameters.exc_sheet_name1,st_name=['FullfieldDriftingSinusoidalGrating'],st_contrast=high_contrast,value_name=['orientation max of Firing rate'],ads_unique=True).get_analysis_result()[0].get_value_by_id(responsive_spike_ids1))
        idx = numpy.logical_and(base>=0,mmax>=0)
        base = base[idx]
        mmax = mmax[idx]
        sp = numpy.array(spont_l4exc_pnv.get_value_by_id(responsive_spike_ids1))[idx]
        base_l4E = base
        mmax_l4E = mmax
        rura_l4E = ((numpy.array(base)-numpy.array(sp))/(numpy.array(base)+numpy.array(mmax)-numpy.array(sp)))[numpy.array(base)+numpy.array(mmax) > r]
        print('Removed \% of neurons:' + str(float(len(spike_ids1)-len(responsive_spike_ids1))/len(spike_ids1)))

        base = queries.param_filter_query(self.datastore,sheet_name=self.parameters.inh_sheet_name1,st_name=['FullfieldDriftingSinusoidalGrating'],st_contrast=low_contrast,value_name=['orientation baseline of Firing rate'],ads_unique=True).get_analysis_result()[0].get_value_by_id(spike_ids_inh1)
        mmax = queries.param_filter_query(self.datastore,sheet_name=self.parameters.inh_sheet_name1,st_name=['FullfieldDriftingSinusoidalGrating'],st_contrast=low_contrast,value_name=['orientation max of Firing rate'],ads_unique=True).get_analysis_result()[0].get_value_by_id(spike_ids_inh1)
        err =queries.param_filter_query(self.datastore,sheet_name=self.parameters.inh_sheet_name1,st_name=['FullfieldDriftingSinusoidalGrating'],st_contrast=high_contrast,value_name=['orientation fitting error of Firing rate'],ads_unique=True).get_analysis_result()[0].get_value_by_id(spike_ids_inh1)
        err_lc =queries.param_filter_query(self.datastore,sheet_name=self.parameters.inh_sheet_name1,st_name=['FullfieldDriftingSinusoidalGrating'],st_contrast=low_contrast,value_name=['orientation fitting error of Firing rate'],ads_unique=True).get_analysis_result()[0].get_value_by_id(spike_ids_inh1)
        responsive_spike_ids_inh1 = numpy.array(spike_ids_inh1)[numpy.logical_and(numpy.logical_and(numpy.array(base)+numpy.array(mmax) > r, numpy.array(err) <= 0.3), numpy.array(err_lc) <= 0.3)]
        base = numpy.array(queries.param_filter_query(self.datastore,sheet_name=self.parameters.inh_sheet_name1,st_name=['FullfieldDriftingSinusoidalGrating'],st_contrast=high_contrast,value_name=['orientation baseline of Firing rate'],ads_unique=True).get_analysis_result()[0].get_value_by_id(responsive_spike_ids_inh1))
        mmax = numpy.array(queries.param_filter_query(self.datastore,sheet_name=self.parameters.inh_sheet_name1,st_name=['FullfieldDriftingSinusoidalGrating'],st_contrast=high_contrast,value_name=['orientation max of Firing rate'],ads_unique=True).get_analysis_result()[0].get_value_by_id(responsive_spike_ids_inh1))
        idx = numpy.logical_and(base>=0,mmax>=0)
        base = base[idx]
        mmax = mmax[idx]
        base_l4I = base
        mmax_l4I = mmax
        sp = numpy.array(spont_l4inh_pnv.get_value_by_id(responsive_spike_ids_inh1))[idx]
        rura_l4I = ((numpy.array(base)-numpy.array(sp))/(numpy.array(base)+numpy.array(mmax)-numpy.array(sp)))[numpy.array(base)+numpy.array(mmax) > r]
        print('Removed \% of neurons:' + str(float(len(spike_ids_inh1)-len(responsive_spike_ids_inh1))/len(spike_ids_inh1)))

        if self.parameters.exc_sheet_name2 != 'None':
            base = queries.param_filter_query(self.datastore,sheet_name=self.parameters.exc_sheet_name2,st_name=['FullfieldDriftingSinusoidalGrating'],st_contrast=low_contrast,value_name=['orientation baseline of Firing rate'],ads_unique=True).get_analysis_result()[0].get_value_by_id(spike_ids2)
            mmax = queries.param_filter_query(self.datastore,sheet_name=self.parameters.exc_sheet_name2,st_name=['FullfieldDriftingSinusoidalGrating'],st_contrast=low_contrast,value_name=['orientation max of Firing rate'],ads_unique=True).get_analysis_result()[0].get_value_by_id(spike_ids2)
            err =queries.param_filter_query(self.datastore,sheet_name=self.parameters.exc_sheet_name2,st_name=['FullfieldDriftingSinusoidalGrating'],st_contrast=high_contrast,value_name=['orientation fitting error of Firing rate'],ads_unique=True).get_analysis_result()[0].get_value_by_id(spike_ids2)
            err_lc =queries.param_filter_query(self.datastore,sheet_name=self.parameters.exc_sheet_name2,st_name=['FullfieldDriftingSinusoidalGrating'],st_contrast=low_contrast,value_name=['orientation fitting error of Firing rate'],ads_unique=True).get_analysis_result()[0].get_value_by_id(spike_ids2)
            responsive_spike_ids2 = numpy.array(spike_ids2)[numpy.logical_and(numpy.logical_and(numpy.array(base)+numpy.array(mmax) > r, numpy.array(err) <= 0.3), numpy.array(err_lc) <= 0.3)]
            base = numpy.array(queries.param_filter_query(self.datastore,sheet_name=self.parameters.exc_sheet_name2,st_name=['FullfieldDriftingSinusoidalGrating'],st_contrast=high_contrast,value_name=['orientation baseline of Firing rate'],ads_unique=True).get_analysis_result()[0].get_value_by_id(responsive_spike_ids2))
            mmax = numpy.array(queries.param_filter_query(self.datastore,sheet_name=self.parameters.exc_sheet_name2,st_name=['FullfieldDriftingSinusoidalGrating'],st_contrast=high_contrast,value_name=['orientation max of Firing rate'],ads_unique=True).get_analysis_result()[0].get_value_by_id(responsive_spike_ids2))
            idx = numpy.logical_and(base>=0,mmax>=0)
            base = base[idx]
            mmax = mmax[idx]
            sp = numpy.array(spont_l23exc_pnv.get_value_by_id(responsive_spike_ids2))[idx]
            rura_l23E = ((numpy.array(base)-numpy.array(sp))/(numpy.array(base)+numpy.array(mmax)-numpy.array(sp)))[numpy.array(base)+numpy.array(mmax) > r]
            print('Removed \% of neurons:' + str(float(len(spike_ids2)-len(responsive_spike_ids2))/len(spike_ids2)))

            base = queries.param_filter_query(self.datastore,sheet_name=self.parameters.inh_sheet_name2,st_name=['FullfieldDriftingSinusoidalGrating'],st_contrast=low_contrast,value_name=['orientation baseline of Firing rate'],ads_unique=True).get_analysis_result()[0].get_value_by_id(spike_ids_inh2)
            mmax = queries.param_filter_query(self.datastore,sheet_name=self.parameters.inh_sheet_name2,st_name=['FullfieldDriftingSinusoidalGrating'],st_contrast=low_contrast,value_name=['orientation max of Firing rate'],ads_unique=True).get_analysis_result()[0].get_value_by_id(spike_ids_inh2)
            err =queries.param_filter_query(self.datastore,sheet_name=self.parameters.inh_sheet_name2,st_name=['FullfieldDriftingSinusoidalGrating'],st_contrast=high_contrast,value_name=['orientation fitting error of Firing rate'],ads_unique=True).get_analysis_result()[0].get_value_by_id(spike_ids_inh2)
            err_lc =queries.param_filter_query(self.datastore,sheet_name=self.parameters.inh_sheet_name2,st_name=['FullfieldDriftingSinusoidalGrating'],st_contrast=low_contrast,value_name=['orientation fitting error of Firing rate'],ads_unique=True).get_analysis_result()[0].get_value_by_id(spike_ids_inh2)
            responsive_spike_ids_inh2 = numpy.array(spike_ids_inh2)[numpy.logical_and(numpy.logical_and(numpy.array(base)+numpy.array(mmax) > r, numpy.array(err) <= 0.3), numpy.array(err_lc) <= 0.3)]
            base = numpy.array(queries.param_filter_query(self.datastore,sheet_name=self.parameters.inh_sheet_name2,st_name=['FullfieldDriftingSinusoidalGrating'],st_contrast=high_contrast,value_name=['orientation baseline of Firing rate'],ads_unique=True).get_analysis_result()[0].get_value_by_id(responsive_spike_ids_inh2))
            mmax = numpy.array(queries.param_filter_query(self.datastore,sheet_name=self.parameters.inh_sheet_name2,st_name=['FullfieldDriftingSinusoidalGrating'],st_contrast=high_contrast,value_name=['orientation max of Firing rate'],ads_unique=True).get_analysis_result()[0].get_value_by_id(responsive_spike_ids_inh2))
            idx = numpy.logical_and(base>=0,mmax>=0)
            base = base[idx]
            mmax = mmax[idx]
            sp = numpy.array(spont_l23inh_pnv.get_value_by_id(responsive_spike_ids_inh2))[idx]
            rura_l23I = ((numpy.array(base)-numpy.array(sp))/(numpy.array(base)+numpy.array(mmax)-numpy.array(sp)))[numpy.array(base)+numpy.array(mmax) > r]
            print('Removed \% of neurons:' + str(float(len(spike_ids_inh2)-len(responsive_spike_ids_inh2))/len(spike_ids_inh2)))
        else:
            rura_l23E = 0
            rura_l23I = 0
                
        dsv = queries.param_filter_query(self.datastore,st_name='FullfieldDriftingSinusoidalGrating',analysis_algorithm=['TrialAveragedFiringRate'],st_contrast=[low_contrast,high_contrast], value_name='Firing rate')
        plots['ExcORTCMeanL4'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name' : 'orientation', 'neurons': list(spike_ids1), 'sheet_name' : self.parameters.exc_sheet_name1,'centered'  : True,'mean' : True,'pool' : False,'polar' : False}),spont_level_pnv=spont_l4exc_pnv),gs[0:6,:6],{'y_lim' : (0,None),'title' : None,'x_label' : None , 'y_label' : 'Layer 4 (EXC)\n\nfiring rate (sp/s)', 'x_ticks' : None, 'linestyles' : ['--','-','-']})
        if len(responsive_spike_ids1) > 0:
            plots['ExcORTC1L4'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name' : 'orientation', 'neurons': list(responsive_spike_ids1[0:3]), 'sheet_name' : self.parameters.exc_sheet_name1,'centered'  : True,'mean' : False,'pool' : False,'polar' : False}),spont_level_pnv=spont_l4exc_pnv),gs[0:3,6:15],{'y_lim' : (0,None),'title' : None,'left_border' : None, 'x_label' : None,'y_axis' : False,'x_axis' : False, 'x_ticks' : False, 'linestyles' : ['--','-','-']})
        if len(responsive_spike_ids1) > 3:
            plots['ExcORTC2L4'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name' : 'orientation', 'neurons': list(responsive_spike_ids1[3:6]), 'sheet_name' : self.parameters.exc_sheet_name1,'centered'  : True,'mean' : False,'pool' : False,'polar': False}),spont_level_pnv=spont_l4exc_pnv),gs[3:6,6:15],{'y_lim' : (0,None),'title' : None,'left_border' : None, 'x_label' : None,'y_axis' : False,'x_axis' : False, 'linestyles' : ['--','-','-']})

        plots['InhORTCMeanL4'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name' : 'orientation', 'neurons': list(spike_ids_inh1), 'sheet_name' : self.parameters.inh_sheet_name1,'centered'  : True,'mean' : True,'pool' : False,'polar' : False}),spont_level_pnv=spont_l4inh_pnv),gs[7:13,:6],{'y_lim' : (0,None),'title' : None, 'x_label' : None ,'y_label' : 'Layer 4 (INH)\n\nfiring rate (sp/s)', 'x_ticks' : None, 'linestyles' : ['--','-','-']})
        if len(responsive_spike_ids_inh1) > 0:
            plots['InhORTC1L4'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name' : 'orientation', 'neurons': list(responsive_spike_ids_inh1[0:3]), 'sheet_name' : self.parameters.inh_sheet_name1,'centered'  : True,'mean' : False,'pool' : False,'polar' : False}),spont_level_pnv=spont_l4inh_pnv),gs[7:10,6:15],{'y_lim' : (0,None),'title' : None,'left_border' : None, 'x_label' : None,'y_axis' : False,'x_axis' : False, 'linestyles' : ['--','-','-']})
        if len(responsive_spike_ids_inh1) > 3:
            plots['InhORTC2L4'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name' : 'orientation', 'neurons': list(responsive_spike_ids_inh1[3:6]), 'sheet_name' : self.parameters.inh_sheet_name1,'centered'  : True,'mean' : False,'pool' : False,'polar' : False}),spont_level_pnv=spont_l4inh_pnv),gs[10:13,6:15],{'y_lim' : (0,None),'title' : None,'left_border' : None, 'x_label' : None ,'y_axis' : None,'x_axis' : False, 'x_ticks' : False, 'linestyles' : ['--','-','-']})

        if self.parameters.exc_sheet_name2 != 'None':
            plots['ExcORTCMeanL23'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name' : 'orientation', 'neurons': list(spike_ids2), 'sheet_name' : self.parameters.exc_sheet_name2,'centered'  : True,'mean' : True,'pool' : False,'polar' : False}),spont_level_pnv=spont_l23exc_pnv),gs[14:20,:6],{'y_lim' : (0,None),'title' : None,'x_label' : None , 'y_label' : 'Layer 2/3 (EXC)\n\nfiring rate (sp/s)', 'x_ticks' : None, 'linestyles' : ['--','-','-']})
            if len(responsive_spike_ids2) > 0:
                plots['ExcORTC1L23'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name' : 'orientation', 'neurons': list(responsive_spike_ids2[0:3]), 'sheet_name' : self.parameters.exc_sheet_name2,'centered'  : True,'mean' : False,'pool' : False,'polar' : False}),spont_level_pnv=spont_l23exc_pnv),gs[14:17,6:15],{'y_lim' : (0,None),'title' : None,'left_border' : None, 'x_label' : None,'y_axis' : False,'x_axis' : False, 'x_ticks' : False, 'linestyles' : ['--','-','-']})
            logger.info(len(responsive_spike_ids2))
            if len(responsive_spike_ids2) > 3:
                plots['ExcORTC2L23'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name' : 'orientation', 'neurons': list(responsive_spike_ids2[3:6]), 'sheet_name' : self.parameters.exc_sheet_name2,'centered'  : True,'mean' : False,'pool' : False,'polar': False}),spont_level_pnv=spont_l23exc_pnv),gs[17:20,6:15],{'y_lim' : (0,None),'title' : None,'left_border' : None, 'x_label' : None,'y_axis' : False,'x_axis' : False, 'linestyles' : ['--','-','-']})

            plots['InhORTCMeanL23'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name' : 'orientation', 'neurons': list(spike_ids_inh2), 'sheet_name' : self.parameters.inh_sheet_name2,'centered'  : True,'mean' : True,'pool' : False,'polar' : False}),spont_level_pnv=spont_l23inh_pnv),gs[21:27,:6],{'y_lim' : (0,None),'title' : None, 'y_label' : 'Layer 2/3 (INH)\n\nfiring rate (sp/s)', 'linestyles' : ['--','-','-']})
            if len(responsive_spike_ids_inh2) > 0:
                plots['InhORTC1L23'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name' : 'orientation', 'neurons': list(responsive_spike_ids_inh2[0:3]), 'sheet_name' : self.parameters.inh_sheet_name2,'centered'  : True,'mean' : False,'pool' : False,'polar' : False}),spont_level_pnv=spont_l23inh_pnv),gs[21:24,6:15],{'y_lim' : (0,None),'title' : None,'left_border' : None, 'x_label' : None,'y_axis' : False,'x_axis' : False, 'linestyles' : ['--','-','-']})
            if len(responsive_spike_ids_inh2) > 3:
                plots['InhORTC2L23'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name' : 'orientation', 'neurons': list(responsive_spike_ids_inh2[3:6]), 'sheet_name' : self.parameters.inh_sheet_name2,'centered'  : True,'mean' : False,'pool' : False,'polar' : False}),spont_level_pnv=spont_l23inh_pnv),gs[24:27,6:15],{'y_lim' : (0,None),'title' : None,'left_border' : None, 'y_axis' : None,'x_axis' : False, 'linestyles' : ['--','-','-']})

        
        dsv1 = queries.param_filter_query(self.datastore,value_name=['orientation HWHH of Firing rate'],sheet_name=[self.parameters.exc_sheet_name1], st_contrast =[low_contrast,high_contrast])
        dsv = queries.param_filter_query(dsv1,st_contrast=low_contrast)
        b = numpy.array(dsv.get_analysis_result()[0].get_value_by_id(responsive_spike_ids1))
        dsv = queries.param_filter_query(dsv1,st_contrast=high_contrast)
        a = numpy.array(dsv.get_analysis_result()[0].get_value_by_id(responsive_spike_ids1))
        lc = b[numpy.logical_and(numpy.logical_and(a>0,b>0),numpy.logical_and(a<200,b<200))]
        hc = a[numpy.logical_and(numpy.logical_and(a>0,b>0),numpy.logical_and(a<200,b<200))]
        print('Removed \% of neurons:' + str(float(len(spike_ids1)-len(hc))/len(spike_ids1)))
        print("L4Exc Mean HWHH:"+str( mean_and_sem(hc)))
        print("LC_HC diff: "+  str(mean_and_sem((hc-lc)[abs(hc-lc)< 50])) + ' p=' + str( scipy.stats.ttest_rel(hc[abs(hc-lc)< 50],lc[abs(hc-lc)< 50])))
        mean_hwhh = round(mean_and_sem(hc)[0],2)
        diff_hwhh = str(round(mean_and_sem((hc-lc)[abs(hc-lc)< 50])[0],2))
        dsv1.sort_analysis_results('st_contrast', reverse=True)
        plots['HWHHExcL4'] = (PerNeuronValueScatterPlot(dsv1, ParameterSet({'only_matching_units' : True, 'ignore_nan' : True, 'lexicographic_order': True, 'neuron_ids': list(responsive_spike_ids1)})),gs[0:6,17:23],{'x_lim': (0,50),'y_lim' : (0,50),'identity_line' : True, 'x_label' : None,'y_label' : 'HWHH cont. '+str(low_contrast)+'%', 'cmp' : None,'title' : None, 'dot_size' : 10})
        hc_l4e = hc


        dsv1 = queries.param_filter_query(self.datastore,value_name=['orientation HWHH of Firing rate'],sheet_name=[self.parameters.inh_sheet_name1], st_contrast =[low_contrast,high_contrast])
        dsv = queries.param_filter_query(dsv1,st_contrast=low_contrast)
        b = numpy.array(dsv.get_analysis_result()[0].get_value_by_id(responsive_spike_ids_inh1))
        dsv = queries.param_filter_query(dsv1,st_contrast=high_contrast)
        a = numpy.array(dsv.get_analysis_result()[0].get_value_by_id(responsive_spike_ids_inh1))
        lc = b[numpy.logical_and(numpy.logical_and(a>0,b>0),numpy.logical_and(a<200,b<200))]
        hc = a[numpy.logical_and(numpy.logical_and(a>0,b>0),numpy.logical_and(a<200,b<200))]
        print('Removed \% of neurons:' + str(float(len(spike_ids_inh1)-len(hc))/len(spike_ids_inh1)))
        print("L4Inh Mean HWHH:" +str( mean_and_sem(hc)))
        print("LC_HC diff: " + str( mean_and_sem((hc-lc)[abs(hc-lc)< 50])) + ' p=' + str(scipy.stats.ttest_rel(hc[abs(hc-lc)< 50],lc[abs(hc-lc)< 50])))
        mean_hwhh = round(mean_and_sem(hc)[0],2)
        diff_hwhh = str(round(mean_and_sem((hc-lc)[abs(hc-lc)< 50])[0],2))
        dsv1.sort_analysis_results('st_contrast', reverse=True)
        plots['HWHHInhL4'] = (PerNeuronValueScatterPlot(dsv1, ParameterSet({'only_matching_units' : True, 'ignore_nan' : True, 'lexicographic_order': True, 'neuron_ids': list(responsive_spike_ids_inh1)})),gs[7:13,17:23],{'x_lim': (0,50),'y_lim' : (0,50),'identity_line' : True, 'x_label' : None,'y_label' : 'HWHH cont. '+str(low_contrast)+'%', 'cmp' : None,'title' : None, 'dot_size' : 10})
        hc_l4i = hc

        if self.parameters.exc_sheet_name2 != 'None':
            dsv1 = queries.param_filter_query(self.datastore,value_name=['orientation HWHH of Firing rate'],sheet_name=[self.parameters.exc_sheet_name2], st_contrast =[low_contrast,high_contrast])
            dsv = queries.param_filter_query(dsv1,st_contrast=low_contrast)
            b = numpy.array(dsv.get_analysis_result()[0].get_value_by_id(responsive_spike_ids2))
            dsv = queries.param_filter_query(dsv1,st_contrast=high_contrast)
            a = numpy.array(dsv.get_analysis_result()[0].get_value_by_id(responsive_spike_ids2))
            lc = b[numpy.logical_and(numpy.logical_and(a>0,b>0),numpy.logical_and(a<200,b<200))]
            hc = a[numpy.logical_and(numpy.logical_and(a>0,b>0),numpy.logical_and(a<200,b<200))]
            print('Removed \% of neurons:' + str(float(len(spike_ids2)-len(hc))/len(spike_ids2)))
            print("L23Exc Mean HWHH:" + str( mean_and_sem(hc)))
            print("LC_HC diff: "  + str( mean_and_sem((hc-lc)[abs(hc-lc)< 50])) + ' p=' + str(scipy.stats.ttest_rel(hc[abs(hc-lc)< 50],lc[abs(hc-lc)< 50])))
            mean_hwhh = round(mean_and_sem(hc)[0],2)
            diff_hwhh = str(round(mean_and_sem((hc-lc)[abs(hc-lc)< 50])[0],2))
            dsv1.sort_analysis_results('st_contrast', reverse=True)
            plots['HWHHExcL23'] = (PerNeuronValueScatterPlot(dsv1, ParameterSet({'only_matching_units' : True, 'ignore_nan' : True, 'lexicographic_order': True, 'neuron_ids': list(responsive_spike_ids2)})),gs[14:20,17:23],{'x_lim': (0,50),'y_lim' : (0,50),'identity_line' : True, 'x_label' : None,'y_label' : 'HWHH cont. '+str(low_contrast)+'%', 'cmp' : None,'title' : None, 'dot_size' : 10})
            hc_l23e = hc

            dsv1 = queries.param_filter_query(self.datastore,value_name=['orientation HWHH of Firing rate'],sheet_name=[self.parameters.inh_sheet_name2], st_contrast =[low_contrast,high_contrast])
            dsv = queries.param_filter_query(dsv1,st_contrast=low_contrast)
            b = numpy.array(dsv.get_analysis_result()[0].get_value_by_id(responsive_spike_ids_inh2))
            dsv = queries.param_filter_query(dsv1,st_contrast=high_contrast)
            a = numpy.array(dsv.get_analysis_result()[0].get_value_by_id(responsive_spike_ids_inh2))
            lc = b[numpy.logical_and(numpy.logical_and(a>0,b>0),numpy.logical_and(a<200,b<200))]
            hc = a[numpy.logical_and(numpy.logical_and(a>0,b>0),numpy.logical_and(a<200,b<200))]
            dsv1.sort_analysis_results('st_contrast', reverse=True)
            print('Removed \% of neurons:'+  str(float(len(spike_ids_inh2)-len(hc))/len(spike_ids_inh2)))
            print("L23Inh Mean HWHH:" + str ( mean_and_sem(hc)))
            print("LC_HC diff: " +str( mean_and_sem((hc-lc)[abs(hc-lc)< 50])) + ' p=' + str( scipy.stats.ttest_rel(hc[abs(hc-lc)< 50],lc[abs(hc-lc)< 50])))
            mean_hwhh = round(mean_and_sem(hc)[0],2)
            diff_hwhh = str(round(mean_and_sem((hc-lc)[abs(hc-lc)< 50])[0],2))
            hc_l23i = hc
            plots['HWHHInhL23'] = (PerNeuronValueScatterPlot(dsv1, ParameterSet({'only_matching_units' : True, 'ignore_nan' : True, 'lexicographic_order': True, 'neuron_ids': list(responsive_spike_ids_inh2)})),gs[21:27,17:23],{'x_lim': (0,50),'y_lim' : (0,50),'identity_line' : True, 'x_label' : 'HWHH Cont. '+str(high_contrast)+'%','y_label' : 'HWHH cont. '+str(low_contrast)+'%', 'cmp' : None,'title' : None, 'dot_size' : 10})

        else:
            hc_l23e = 0
            hc_l23i = 0

        if self.parameters.exc_sheet_name2 != 'None':
            print("HWHH Exc: " +str( mean_and_sem(hc_l4e.tolist()+hc_l23e.tolist())))
            print("HWHH Inh: " +str( mean_and_sem(hc_l4i.tolist()+hc_l23i.tolist())))

        else:
            print("HWHH Exc: " +str( mean_and_sem(hc_l4e.tolist())))
            print("HWHH Inh: " +str( mean_and_sem(hc_l4i.tolist())))


        dsv = queries.param_filter_query(self.datastore,value_name=['orientation HWHH of Firing rate'],sheet_name=[self.parameters.exc_sheet_name1],st_contrast=[high_contrast])
        plots['HWHHHistogramExcL4'] = (PerNeuronValuePlot(dsv, ParameterSet({'cortical_view' : False,'neuron_ids':list(responsive_spike_ids1)})),gs[0:6,26:32],{ 'x_lim' : (0.0,50.0), 'x_label' : None,'title' : None,'y_label' : '# neurons'})

        dsv = queries.param_filter_query(self.datastore,value_name=['orientation HWHH of Firing rate'],sheet_name=[self.parameters.inh_sheet_name1],st_contrast=[high_contrast])
        plots['HWHHHistogramInhL4'] = (PerNeuronValuePlot(dsv, ParameterSet({'cortical_view' : False,'neuron_ids':list(responsive_spike_ids_inh1)})),gs[7:13,26:32],{ 'x_lim' : (0.0,50.0), 'x_label' : None,'title' : None,'y_label' : '# neurons'})

        if self.parameters.exc_sheet_name2 != 'None':
            dsv = queries.param_filter_query(self.datastore,value_name=['orientation HWHH of Firing rate'],sheet_name=[self.parameters.exc_sheet_name2],st_contrast=[high_contrast])
            plots['HWHHHistogramExcL23'] = (PerNeuronValuePlot(dsv, ParameterSet({'cortical_view' : False,'neuron_ids':list(responsive_spike_ids2)})),gs[14:20,26:32],{ 'x_lim' : (0.0,50.0), 'x_label' : None,'title' : None,'y_label' : '# neurons'})

            dsv = queries.param_filter_query(self.datastore,value_name=['orientation HWHH of Firing rate'],sheet_name=[self.parameters.inh_sheet_name2],st_contrast=[high_contrast])
            plots['HWHHHistogramInhL23'] = (PerNeuronValuePlot(dsv, ParameterSet({'cortical_view' : False,'neuron_ids':list(responsive_spike_ids_inh2)})),gs[21:27,26:32],{ 'x_lim' : (0.0,50.0), 'x_label' : 'HWHH ('+str(high_contrast)+'% cont.)','title' : None,'y_label' : '# neurons'})

        axis = pylab.subplot(gs[0:6,33:39])
        pylab.hist(rura_l4E*100,color='k',bins=numpy.arange(-20,40,3))
        pylab.xlim(-20,40)
        pylab.xticks([-20,10,40])
        pylab.ylabel('# neurons',fontsize=19)
        for label in axis.get_xticklabels() + axis.get_yticklabels():
            label.set_fontsize(19)
        phf.disable_top_right_axis(pylab.gca())
        phf.three_tick_axis(axis.yaxis ,log=False, precision = 3)
        xtls = axis.get_xticklabels()
        for xtl in xtls:
            x,y = xtl.get_position()
            xtl.set_position((x,y-0.032))
        print("L4Exc Mean/SEM RURA:" + str( mean_and_sem(rura_l4E[numpy.abs(rura_l4E)<0.5]*100)))

        axis = pylab.subplot(gs[7:13,33:39])
        pylab.hist(rura_l4I*100,color='k',bins=numpy.arange(-20,40,3))
        pylab.xlim(-20,40)
        pylab.xticks([-20,10,40])
        pylab.ylabel('# neurons',fontsize=19)
        for label in axis.get_xticklabels() + axis.get_yticklabels():
            label.set_fontsize(19)
        phf.disable_top_right_axis(pylab.gca())
        phf.three_tick_axis(axis.yaxis ,log=False, precision = 3)
        xtls = axis.get_xticklabels()
        for xtl in xtls:
            x,y = xtl.get_position()
            xtl.set_position((x,y-0.032))
        print("L4Inh Mean/SE RURA:" + str( mean_and_sem(rura_l4I[numpy.abs(rura_l4I)<0.5]*100)))

        if self.parameters.exc_sheet_name2 != 'None':
            axis = pylab.subplot(gs[14:20,33:39])
            pylab.hist(rura_l23E*100,color='k',bins=numpy.arange(-20,40,3))
            pylab.xlim(-20,40)
            pylab.xticks([-20,10,40])
            pylab.ylabel('# neurons',fontsize=19)
            for label in axis.get_xticklabels() + axis.get_yticklabels():
                label.set_fontsize(19)
            phf.disable_top_right_axis(pylab.gca())
            phf.three_tick_axis(axis.yaxis ,log=False, precision = 3)
            xtls = axis.get_xticklabels()
            for xtl in xtls:
                x,y = xtl.get_position()
                xtl.set_position((x,y-0.032))
            print("L23Exc Mean/SE RURA:" + str( mean_and_sem(rura_l23E[numpy.abs(rura_l23E)<0.5]*100)))

            axis = pylab.subplot(gs[21:27,33:39])
            pylab.hist(rura_l23I*100,color='k',bins=numpy.arange(-20,40,3))
            pylab.xlim(-20,40)
            pylab.xticks([-20,10,40])
            pylab.ylabel('# neurons',fontsize=19)
            for label in axis.get_xticklabels() + axis.get_yticklabels():
                label.set_fontsize(19)
            phf.disable_top_right_axis(pylab.gca())
            phf.three_tick_axis(axis.yaxis ,log=False, precision = 3)
            xtls = axis.get_xticklabels()
            for xtl in xtls:
                x,y = xtl.get_position()
                xtl.set_position((x,y-0.032))
            #phf.disable_left_axis(pylab.gca())
            pylab.xlabel('RURA',fontsize=19)
            print("L23Inh Mean/SE RURA:" + str( mean_and_sem(rura_l23I[numpy.abs(rura_l23I)<0.5]*100)))

        if self.parameters.exc_sheet_name2 != 'None':
            print("Exc RURA:" +str( mean_and_sem(list(rura_l23E[numpy.abs(rura_l23E)<0.5]*100) + list(rura_l4E[numpy.abs(rura_l4E)<0.5]*100))))
            print("Inh RURA:" +str( mean_and_sem(list(rura_l23I[numpy.abs(rura_l23I)<0.5]*100) + list(rura_l4I[numpy.abs(rura_l4I)<0.5]*100))))
        else:
            print("Exc RURA:" +str( mean_and_sem(list(rura_l4E[numpy.abs(rura_l4E)<0.5]*100))))
            print("Inh RURA:" +str( mean_and_sem(list(rura_l4I[numpy.abs(rura_l4I)<0.5]*100))))

        return plots


class OrientationTuningSummaryAnalogSignals(Plotting):

    required_parameters = ParameterSet({
        'exc_sheet_name1': str,  # the name of the sheet for which to plot
        'inh_sheet_name1': str,  # the name of the sheet for which to plot
        'exc_sheet_name2': str,  # the name of the sheet for which to plot
        'inh_sheet_name2': str,  # the name of the sheet for which to plot
    })

    def subplot(self, subplotspec):
        plots = {}
        gs = gridspec.GridSpecFromSubplotSpec(24, 35, subplot_spec=subplotspec,
                                              hspace=10.0, wspace=0.6)

        analog_ids1 = sorted(numpy.random.permutation(queries.param_filter_query(
            self.datastore, sheet_name=self.parameters.exc_sheet_name1).get_segments()[0].get_stored_esyn_ids()))
        analog_ids_inh1 = sorted(numpy.random.permutation(queries.param_filter_query(
            self.datastore, sheet_name=self.parameters.inh_sheet_name1).get_segments()[0].get_stored_esyn_ids()))
        or_tuning_exc1 = self.datastore.get_analysis_result(
            identifier='PerNeuronValue', value_name='LGNAfferentOrientation', sheet_name=self.parameters.exc_sheet_name1)[0]
        or_tuning_inh1 = self.datastore.get_analysis_result(
            identifier='PerNeuronValue', value_name='LGNAfferentOrientation', sheet_name=self.parameters.inh_sheet_name1)[0]

        if self.parameters.exc_sheet_name2 != 'None':
            analog_ids2 = sorted(numpy.random.permutation(queries.param_filter_query(
                self.datastore, sheet_name=self.parameters.exc_sheet_name2).get_segments()[0].get_stored_esyn_ids()))
            analog_ids_inh2 = sorted(numpy.random.permutation(queries.param_filter_query(
                self.datastore, sheet_name=self.parameters.inh_sheet_name2).get_segments()[0].get_stored_esyn_ids()))
            or_tuning_exc2 = self.datastore.get_analysis_result(
                identifier='PerNeuronValue', value_name='LGNAfferentOrientation', sheet_name=self.parameters.exc_sheet_name2)[0]
            or_tuning_inh2 = self.datastore.get_analysis_result(
                identifier='PerNeuronValue', value_name='LGNAfferentOrientation', sheet_name=self.parameters.inh_sheet_name2)[0]

        or_tuning_exc1 = None
        or_tuning_inh1 = None
        or_tuning_exc2 = None
        or_tuning_inh2 = None

        # L4 EXC
        dsv = queries.param_filter_query(self.datastore, value_name=[
                                         '-(x+y)(F0_Vm,Mean(VM))'],st_contrast=[low_contrast,high_contrast])
        plots['L4E_F0_Vm'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids1), 'sheet_name': self.parameters.exc_sheet_name1, 'centered': True, 'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning_exc1), gs[0:6, :5], {'x_label': None, 'y_label': 'Layer 4 (EXC)', 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2, 'title': 'F0 of Vm (mV)'})
        dsv = queries.param_filter_query(self.datastore, value_name=['F1_Vm'],st_contrast=[low_contrast,high_contrast])
        plots['L4E_F1_Vm'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids1), 'sheet_name': self.parameters.exc_sheet_name1, 'centered': True, 'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning_exc1), gs[0:6, 6:11], {'x_label': None, 'y_label': None, 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2, 'title': 'F1 of Vm (mV)'})
        dsv = queries.param_filter_query(self.datastore, value_name=[
                                         'F0_Exc_Cond-Mean(ECond)'],st_contrast=[low_contrast,high_contrast])
        plots['L4E_F0_CondExc'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids1), 'sheet_name': self.parameters.exc_sheet_name1, 'centered': True, 'mean': True,
                                                                      'pool': False, 'polar': False}), centering_pnv=or_tuning_exc1), gs[0:6, 12:17], {'x_label': None, 'y_label': None, 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2, 'title': 'F0 of gE (nS)'})
        dsv = queries.param_filter_query(
            self.datastore, value_name=['F1_Exc_Cond'],st_contrast=[low_contrast,high_contrast])
        plots['L4E_F1_CondExc'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids1), 'sheet_name': self.parameters.exc_sheet_name1, 'centered': True, 'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning_exc1), gs[0:6, 18:23], {'x_label': None, 'y_label': None, 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2, 'title': 'F1 of gE (nS)'})
        dsv = queries.param_filter_query(self.datastore, value_name=[
                                         'F0_Inh_Cond-Mean(ICond)'],st_contrast=[low_contrast,high_contrast])
        plots['L4E_F0_CondInh'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids1), 'sheet_name': self.parameters.exc_sheet_name1, 'centered': True, 'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning_exc1), gs[0:6, 24:29], {'x_label': None, 'y_label': None, 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2, 'title': 'F0 of gI (nS)'})
        dsv = queries.param_filter_query(
            self.datastore, value_name=['F1_Inh_Cond'],st_contrast=[low_contrast,high_contrast])
        plots['L4E_F1_CondInh'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids1), 'sheet_name': self.parameters.exc_sheet_name1, 'centered': True, 'mean': True,
                                                                      'pool': False, 'polar': False}), centering_pnv=or_tuning_exc1), gs[0:6, 30:35], {'x_label': None, 'y_label': None, 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2, 'title': 'F1 of gI (nS)'})

        # L4 INH
        dsv = queries.param_filter_query(self.datastore, value_name=[
                                         '-(x+y)(F0_Vm,Mean(VM))'],st_contrast=[low_contrast,high_contrast])
        plots['L4I_F0_Vm'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids_inh1), 'sheet_name': self.parameters.inh_sheet_name1, 'centered': True,
                                                                 'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning_inh1), gs[6:12, :5], {'title': None, 'x_label': None, 'y_label': 'Layer 4 (INH)', 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2})
        dsv = queries.param_filter_query(self.datastore, value_name=['F1_Vm'],st_contrast=[low_contrast,high_contrast])
        plots['L4I_F1_Vm'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids_inh1), 'sheet_name': self.parameters.inh_sheet_name1, 'centered': True,
                                                                 'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning_inh1), gs[6:12, 6:11], {'title': None, 'x_label': None, 'y_label': None, 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2})
        dsv = queries.param_filter_query(self.datastore, value_name=[
                                         'F0_Exc_Cond-Mean(ECond)'],st_contrast=[low_contrast,high_contrast])
        plots['L4I_F0_CondExc'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids_inh1), 'sheet_name': self.parameters.inh_sheet_name1, 'centered': True,
                                                                      'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning_inh1), gs[6:12, 12:17], {'title': None, 'x_label': None, 'y_label': None, 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2})
        dsv = queries.param_filter_query(
            self.datastore, value_name=['F1_Exc_Cond'],st_contrast=[low_contrast,high_contrast])
        plots['L4I_F1_CondExc'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids_inh1), 'sheet_name': self.parameters.inh_sheet_name1, 'centered': True,
                                                                      'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning_inh1), gs[6:12, 18:23], {'title': None, 'x_label': None, 'y_label': None, 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2})
        dsv = queries.param_filter_query(self.datastore, value_name=[
                                         'F0_Inh_Cond-Mean(ICond)'],st_contrast=[low_contrast,high_contrast])
        plots['L4I_F0_CondInh'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids_inh1), 'sheet_name': self.parameters.inh_sheet_name1, 'centered': True,
                                                                      'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning_inh1), gs[6:12, 24:29], {'title': None, 'x_label': None, 'y_label': None, 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2})
        dsv = queries.param_filter_query(
            self.datastore, value_name=['F1_Inh_Cond'],st_contrast=[low_contrast,high_contrast])
        plots['L4I_F1_CondInh'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids_inh1), 'sheet_name': self.parameters.inh_sheet_name1, 'centered': True,
                                                                      'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning_inh1), gs[6:12, 30:35], {'title': None, 'x_label': None, 'y_label': None, 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2})

        if self.parameters.exc_sheet_name2 != 'None':
            # L2/3 EXC
            dsv = queries.param_filter_query(self.datastore, value_name=[
                                             '-(x+y)(F0_Vm,Mean(VM))'],st_contrast=[low_contrast,high_contrast])
            plots['L23E_F0_Vm'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids2), 'sheet_name': self.parameters.exc_sheet_name2, 'centered': True,
                                                                      'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning_exc2), gs[12:18, :5], {'title': None, 'x_label': None, 'y_label': 'Layer 2/3 (EXC)', 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2})
            dsv = queries.param_filter_query(
                self.datastore, value_name=['F1_Vm'],st_contrast=[low_contrast,high_contrast])
            plots['L23E_F1_Vm'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids2), 'sheet_name': self.parameters.exc_sheet_name2, 'centered': True,
                                                                      'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning_exc2), gs[12:18, 6:11], {'title': None, 'x_label': None, 'y_label': None, 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2})
            dsv = queries.param_filter_query(self.datastore, value_name=[
                                             'F0_Exc_Cond-Mean(ECond)'],st_contrast=[low_contrast,high_contrast])
            plots['L23E_F0_CondExc'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids2), 'sheet_name': self.parameters.exc_sheet_name2, 'centered': True,
                                                                           'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning_exc2), gs[12:18, 12:17], {'title': None, 'x_label': None, 'y_label': None, 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2})
            dsv = queries.param_filter_query(
                self.datastore, value_name=['F1_Exc_Cond'],st_contrast=[low_contrast,high_contrast])
            plots['L23E_F1_CondExc'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids2), 'sheet_name': self.parameters.exc_sheet_name2, 'centered': True,
                                                                           'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning_exc2), gs[12:18, 18:23], {'title': None, 'x_label': None, 'y_label': None, 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2})
            dsv = queries.param_filter_query(self.datastore, value_name=[
                                             'F0_Inh_Cond-Mean(ICond)'],st_contrast=[low_contrast,high_contrast])
            plots['L23E_F0_CondInh'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids2), 'sheet_name': self.parameters.exc_sheet_name2, 'centered': True,
                                                                           'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning_exc2), gs[12:18, 24:29], {'title': None, 'x_label': None, 'y_label': None, 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2})
            dsv = queries.param_filter_query(
                self.datastore, value_name=['F1_Inh_Cond'],st_contrast=[low_contrast,high_contrast])
            plots['L23E_F1_CondInh'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids2), 'sheet_name': self.parameters.exc_sheet_name2, 'centered': True,
                                                                           'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning_exc2), gs[12:18, 30:35], {'title': None, 'x_label': None, 'y_label': None, 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2})

            # L2/3 INH
            dsv = queries.param_filter_query(self.datastore, value_name=[
                                             '-(x+y)(F0_Vm,Mean(VM))'],st_contrast=[low_contrast,high_contrast])
            plots['L23I_F0_Vm'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids_inh2), 'sheet_name': self.parameters.inh_sheet_name2,
                                                                      'centered': True, 'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning_inh2), gs[18:24, :5], {'title': None, 'x_label': None, 'y_label': 'Layer 2/3 (INH)', 'y_tick_precision': 2})
            dsv = queries.param_filter_query(
                self.datastore, value_name=['F1_Vm'],st_contrast=[low_contrast,high_contrast])
            plots['L23I_F1_Vm'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids_inh2), 'sheet_name': self.parameters.inh_sheet_name2, 'centered': True,
                                                                      'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning_inh2), gs[18:24, 6:11], {'title': None, 'x_label': None, 'y_label': None, 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2})
            dsv = queries.param_filter_query(self.datastore, value_name=[
                                             'F0_Exc_Cond-Mean(ECond)'],st_contrast=[low_contrast,high_contrast])
            plots['L23I_F0_CondExc'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids_inh2), 'sheet_name': self.parameters.inh_sheet_name2, 'centered': True, 'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning_inh2), gs[18:24, 12:17], {'title': None, 'x_label': None, 'y_label': None, 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2})
            dsv = queries.param_filter_query(
                self.datastore, value_name=['F1_Exc_Cond'],st_contrast=[low_contrast,high_contrast])
            plots['L23I_F1_CondExc'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids_inh2), 'sheet_name': self.parameters.inh_sheet_name2, 'centered': True, 'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning_inh2), gs[18:24, 18:23], {'title': None, 'x_label': None, 'y_label': None, 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2})
            dsv = queries.param_filter_query(self.datastore, value_name=[
                                             'F0_Inh_Cond-Mean(ICond)'],st_contrast=[low_contrast,high_contrast])
            plots['L23I_F0_CondInh'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids_inh2), 'sheet_name': self.parameters.inh_sheet_name2, 'centered': True, 'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning_inh2), gs[18:24, 24:29], {'title': None, 'x_label': None, 'y_label': None, 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2})
            dsv = queries.param_filter_query(
                self.datastore, value_name=['F1_Inh_Cond'],st_contrast=[low_contrast,high_contrast])
            plots['L23I_F1_CondInh'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'orientation', 'neurons': list(analog_ids_inh2), 'sheet_name': self.parameters.inh_sheet_name2, 'centered': True, 'mean': True, 'pool': False, 'polar': False}), centering_pnv=or_tuning_inh2), gs[18:24, 30:35], {'title': None, 'x_label': None, 'y_label': None, 'x_axis': False, 'x_ticks': False, 'y_tick_precision': 2})

        return plots

class TrialCrossCorrelationAnalysis(Plotting):
        """
        Trial-to-trial crosscorrelation analysis replicated from figure 4D:
        Baudot, P., Levy, M., Marre, O., Monier, C., Pananceau, M., & Frgnac, Y. (2013). Animation of natural scene by virtual eye-movements evokes high precision and low noise in V1 neurons. Frontiers in neural circuits, 7(December), 206. doi:10.3389/fncir.2013.00206
        
        Differences:
        
        Notes:
        It assumes that the TrialToTrialCrossCorrelationOfPSTHandVM analysis was run on natural images, and that it was run with the 10.0 ms  bin lentgth for calculating of PSTH
        and that the optimal preferred orientation for all the neurons was selected for analysis.


        Parameters
        ----------
        neurons1 : list
               The list of layer 4 neurons to include in the analysis.

        neurons2 : list
               The list of layer 2/3 neurons to include in the analysis.

        sheet_name1 : str
               The name of the sheet corresponding to layer 4 excitatory neurons.
              
        sheet_name2 : str
          The name of the sheet corresponding to layer 2/3 excitatory neurons.
        
        window_length : int
          The length of the window which to plot.

        """
        
        required_parameters = ParameterSet({
            'neurons1': list,  # The list of neurons to include in the analysis
            'neurons2': list,  # The list of neurons to include in the analysis
            'sheet_name1' : str,
            'sheet_name2' : str,
            'window_length' : int, #ms
            
        })

        def __init__(self, datastore, parameters, plot_file_name=None,fig_param=None,frame_duration=0):
                Plotting.__init__(self, datastore, parameters, plot_file_name, fig_param,frame_duration)

        def calculate_cc(self,sheet_name,neurons):
                orr = list(set([MozaikParametrized.idd(s).orientation for s in queries.param_filter_query(self.datastore,st_name='FullfieldDriftingSinusoidalGrating',st_contrast=ttcc_contrast).get_stimuli()]))
                oor = self.datastore.get_analysis_result(identifier='PerNeuronValue',value_name = 'orientation preference', sheet_name = sheet_name)
                
                vm_gr_asls = []
                psth_gr_asls = []
                
                dsv1 =  queries.param_filter_query(self.datastore,st_name='FullfieldDriftingSinusoidalGrating',st_contrast=ttcc_contrast,sheet_name=sheet_name,analysis_algorithm='TrialToTrialCrossCorrelationOfAnalogSignalList')
                
                if True:
                    for neuron_idd in neurons:
                        col = orr[numpy.argmin([circular_dist(o,oor[0].get_value_by_id(neuron_idd),numpy.pi)  for o in orr])]
                        dsv =  queries.param_filter_query(dsv1,y_axis_name='trial-trial cross-correlation of Vm (no AP)',st_orientation=col,ads_unique=True)
                        vm_gr_asls.append(dsv.get_analysis_result()[0].get_asl_by_id(neuron_idd))
                        dsv =  queries.param_filter_query(dsv1,y_axis_name='trial-trial cross-correlation of psth (bin=10.0)',st_orientation=col,ads_unique=True)
                        psth_gr_asls.append(dsv.get_analysis_result()[0].get_asl_by_id(neuron_idd))

                vm_cc_gr = numpy.mean(numpy.array(vm_gr_asls),axis=0)
                psth_cc_gr = numpy.mean(numpy.array(psth_gr_asls),axis=0)

                dsv =  queries.param_filter_query(self.datastore,y_axis_name='trial-trial cross-correlation of Vm (no AP)',st_name="NaturalImageWithEyeMovement",sheet_name=sheet_name,ads_unique=True)
                vm_cc_ni = numpy.mean(numpy.array(dsv.get_analysis_result()[0].asl),axis=0)
                dsv =  queries.param_filter_query(self.datastore,y_axis_name='trial-trial cross-correlation of psth (bin=10.0)',st_name="NaturalImageWithEyeMovement",sheet_name=sheet_name,ads_unique=True)
                psth_cc_ni = numpy.mean(numpy.array(dsv.get_analysis_result()[0].asl),axis=0)
                
                return numpy.squeeze(vm_cc_gr),numpy.squeeze(psth_cc_gr),numpy.squeeze(vm_cc_ni),numpy.squeeze(psth_cc_ni)

        def _fitgaussian(self,X,Y):

          fitfunc = lambda p,x:  p[0] + p[1]*numpy.exp(-numpy.abs(0-x)**2/(2*p[2]**2))  

          errfunc = lambda p, x, y: fitfunc(p,x) - y # Distance to the target function
          
          p0 = [0, 1.0, 30] # Initial guess for the parameters
          p0[0] = numpy.min(Y)
          p0[1] = numpy.max(Y)-p0[0]
          
          p1, success = scipy.optimize.leastsq(errfunc,numpy.array(p0[:]), args=(numpy.array(X),numpy.array(Y)))      
          p1[2]  = abs(p1[2])
          
          if success:
            return p1
          else :
            return [0,0,0]        
        
        def subplot(self,subplotspec):
            plots = {}
            gs = gridspec.GridSpecFromSubplotSpec(2, 3, subplot_spec=subplotspec)
            
            vm_cc_gr_s1,psth_cc_gr_s1,vm_cc_ni_s1,psth_cc_ni_s1 = self.calculate_cc(self.parameters.sheet_name1,self.parameters.neurons1)
            vm_cc_gr_s2,psth_cc_gr_s2,vm_cc_ni_s2,psth_cc_ni_s2 = self.calculate_cc(self.parameters.sheet_name2,self.parameters.neurons2)
            
            vm_cc_gr_pool,psth_cc_gr_pool,vm_cc_ni_pool,psth_cc_ni_pool = (vm_cc_gr_s1+vm_cc_gr_s2)/2,(psth_cc_gr_s1+psth_cc_gr_s2)/2,(vm_cc_ni_s1+vm_cc_ni_s2)/2,(psth_cc_ni_s1+psth_cc_ni_s2)/2
            

            z = int(min(self.parameters.window_length,(len(vm_cc_gr_s1)-1)/2,(len(vm_cc_gr_s2)-1)/2)/2)*2

            bin_size=10
            a=0.8
            
            p0,p1,p2 = self._fitgaussian(numpy.linspace(-z,z,2*int(z/bin_size)+1),psth_cc_gr_s1[int(len(psth_cc_gr_s1)/2)-int(z/bin_size):int(len(psth_cc_gr_s1)/2)+int(z/bin_size)+1])
            print("GR_SP_L4: " + str(p1+p0)+ ' ' +str(p2))
            p0,p1,p2 = self._fitgaussian(numpy.linspace(-z,z,2*int(z/bin_size)+1),psth_cc_ni_s1[int(len(psth_cc_ni_s1)/2)-int(z/bin_size):int(len(psth_cc_ni_s1)/2)+int(z/bin_size)+1])
            print("NI_SP_L4: "+ str( p1+p0)+ ' ' +str(p2))
            p0,p1,p2 = self._fitgaussian(numpy.linspace(-z,z,2*int(z/bin_size)+1),psth_cc_gr_s2[int(len(psth_cc_gr_s2)/2)-int(z/bin_size):int(len(psth_cc_gr_s2)/2)+int(z/bin_size)+1])
            print("GR_SP_L23: "+ str( p1+p0)+ ' ' +str(p2))
            p0,p1,p2 = self._fitgaussian(numpy.linspace(-z,z,2*int(z/bin_size)+1),psth_cc_ni_s2[int(len(psth_cc_ni_s2)/2)-int(z/bin_size):int(len(psth_cc_ni_s2)/2)+int(z/bin_size)+1])
            print("NI_SP_L23: "+ str( p1+p0)+ ' '+str(p2))
            p0,p1,p2 = self._fitgaussian(numpy.linspace(-z,z,2*int(z/bin_size)+1),psth_cc_gr_pool[int(len(psth_cc_gr_pool)/2)-int(z/bin_size):int(len(psth_cc_gr_pool)/2)+int(z/bin_size)+1])
            print("GR_SP_POOLED: "+ str( p1+p0)+ ' ' +str(p2))
            p0,p1,p2 = self._fitgaussian(numpy.linspace(-z,z,2*int(z/bin_size)+1),psth_cc_ni_pool[int(len(psth_cc_ni_pool)/2)-int(z/bin_size):int(len(psth_cc_ni_pool)/2)+int(z/bin_size)+1])
            print("NI_SP_POOLED: "+ str( p1+p0)+ ' '+str(p2))

            p0,p1,p2 = self._fitgaussian(numpy.linspace(-z,z,2*z+1),vm_cc_gr_s1[int(len(vm_cc_gr_s1)/2)-z:int(len(vm_cc_gr_s1)/2)+z+1])
            print("GR_VM_L4: "+ str( p1+p0)+' '+ str(p2))
            p0,p1,p2 = self._fitgaussian(numpy.linspace(-z,z,2*z+1),vm_cc_ni_s1[int(len(vm_cc_ni_s1)/2)-z:int(len(vm_cc_ni_s1)/2)+z+1])
            print("NI_VM_L4: "+ str( p1+p0)+' '+ str(p2))
            p0,p1,p2 = self._fitgaussian(numpy.linspace(-z,z,2*z+1),vm_cc_gr_s2[int(len(vm_cc_gr_s2)/2)-z:int(len(vm_cc_gr_s2)/2)+z+1])
            print("GR_VM_L23: "+ str( p1+p0)+' '+ str(p2))
            p0,p1,p2 = self._fitgaussian(numpy.linspace(-z,z,2*z+1),vm_cc_ni_s2[int(len(vm_cc_ni_s2)/2)-z:int(len(vm_cc_ni_s2)/2)+z+1])
            print("NI_VM_L23: "+ str( p1+p0)+' '+ str(p2))
            p0,p1,p2 = self._fitgaussian(numpy.linspace(-z,z,2*z+1),vm_cc_gr_pool[int(len(vm_cc_gr_pool)/2)-z:int(len(vm_cc_gr_pool)/2)+z+1])
            print("GR_VM_POOLED: "+ str( p1+p0)+' '+ str(p2))
            p0,p1,p2 = self._fitgaussian(numpy.linspace(-z,z,2*z+1),vm_cc_ni_pool[int(len(vm_cc_ni_pool)/2)-z:int(len(vm_cc_ni_pool)/2)+z+1])
            print("NI_VM_POOLED: "+ str( p1+p0)+' '+ str(p2))
                        
            plots["Spike_sheet_1"] = (StandardStyleLinePlot([numpy.linspace(-z,z,2*int(z/bin_size)+1),numpy.linspace(-z,z,2*int(z/bin_size)+1)], [psth_cc_gr_s1[int(len(psth_cc_gr_s1)/2)-int(z/bin_size):int(len(psth_cc_gr_s1)/2)+int(z/bin_size)+1],psth_cc_ni_s1[int(len(psth_cc_ni_s1)/2)-int(z/bin_size):int(len(psth_cc_ni_s1)/2)+int(z/bin_size)+1]]),gs[0,0],{'colors':['r','k'], 'x_tick_style' : 'Custom', 'x_ticks' : [],'y_tick_style' : 'Custom', 'y_ticks' : [0,0.25], 'y_tick_labels' : [0.0,0.25], 'linewidth' : 2.0, 'y_lim' : (-0.02,0.25),'y_label' : 'spikes'})
            plots["Spike_sheet_2"] = (StandardStyleLinePlot([numpy.linspace(-z,z,2*int(z/bin_size)+1),numpy.linspace(-z,z,2*int(z/bin_size)+1)], [psth_cc_gr_s2[int(len(psth_cc_gr_s2)/2)-int(z/bin_size):int(len(psth_cc_gr_s2)/2)+int(z/bin_size)+1],psth_cc_ni_s2[int(len(psth_cc_ni_s2)/2)-int(z/bin_size):int(len(psth_cc_ni_s2)/2)+int(z/bin_size)+1]]),gs[0,1],{'colors':['r','k'], 'x_tick_style' : 'Custom', 'x_ticks' : [],'y_tick_style' : 'Custom', 'y_ticks' : [0,0.25], 'y_tick_labels' : [0.0,0.25], 'linewidth' : 2.0, 'y_lim' : (-0.02,0.25),'y_label' : 'spikes','y_ticks' : None,'y_label' : None})
            plots["Spike_sheet_pool"] = (StandardStyleLinePlot([numpy.linspace(-z,z,2*int(z/bin_size)+1),numpy.linspace(-z,z,2*int(z/bin_size)+1)], [psth_cc_gr_pool[int(len(psth_cc_gr_pool)/2)-int(z/bin_size):int(len(psth_cc_gr_pool)/2)+int(z/bin_size)+1],psth_cc_ni_pool[int(len(psth_cc_ni_pool)/2)-int(z/bin_size):int(len(psth_cc_ni_pool)/2)+int(z/bin_size)+1]]),gs[0,2],{'colors':['r','k'], 'x_tick_style' : 'Custom', 'x_ticks' : [],'y_tick_style' : 'Custom', 'y_ticks' : [0.0,0.25], 'y_tick_labels' : [0.0,0.25], 'linewidth' : 2.0, 'y_lim' : (-0.02,0.25),'y_label' : 'spikes','y_ticks' : None,'y_label' : None})

            plots["Vm_sheet_1"] = (StandardStyleLinePlot([numpy.linspace(-z,z,2*z+1),numpy.linspace(-z,z,2*z+1)], [vm_cc_gr_s1[int(len(vm_cc_gr_s1)/2)-z:int(len(vm_cc_gr_s1)/2)+z+1],vm_cc_ni_s1[int(len(vm_cc_ni_s1)/2)-z:int(len(vm_cc_ni_s1)/2)+z+1]]),gs[1,0],{'x_label' : 'time(ms)', 'colors':['r','k'], 'x_tick_style' : 'Custom', 'x_ticks' : [-z,0,z], 'x_tick_labels' : [-self.parameters.window_length,0,self.parameters.window_length],'y_tick_style' : 'Custom', 'y_ticks' : [-a,0,a], 'y_tick_labels' : [-a,0.0,a], 'linewidth' : 2.0, 'y_lim' : (-a,a),'y_label' : 'Vm'})
            plots["Vm_sheet_2"] = (StandardStyleLinePlot([numpy.linspace(-z,z,2*z+1),numpy.linspace(-z,z,2*z+1)], [vm_cc_gr_s2[int(len(vm_cc_gr_s2)/2)-z:int(len(vm_cc_gr_s2)/2)+z+1],vm_cc_ni_s2[int(len(vm_cc_ni_s2)/2)-z:int(len(vm_cc_ni_s2)/2)+z+1]]),gs[1,1],{'x_label' : 'time(ms)', 'colors':['r','k'], 'x_tick_style' : 'Custom', 'x_ticks' : [-z,0,z], 'x_tick_labels' : [-self.parameters.window_length,0,self.parameters.window_length],'y_tick_style' : 'Custom', 'y_ticks' : [-a,0,a], 'y_tick_labels' : [-a,0.0,a], 'linewidth' : 2.0, 'y_lim' : (-a,a),'y_label' : 'Vm','y_ticks' : None,'y_label' : None})
            plots["Vm_sheet_pool"] = (StandardStyleLinePlot([numpy.linspace(-z,z,2*z+1),numpy.linspace(-z,z,2*z+1)], [vm_cc_gr_pool[int(len(vm_cc_gr_pool)/2)-z:int(len(vm_cc_gr_pool)/2)+z+1],vm_cc_ni_pool[int(len(vm_cc_ni_pool)/2)-z:int(len(vm_cc_ni_pool)/2)+z+1]]),gs[1,2],{'x_label' : 'time(ms)', 'colors':['r','k'], 'x_tick_style' : 'Custom', 'x_ticks' : [-z,0,z], 'x_tick_labels' : [-self.parameters.window_length,0,self.parameters.window_length],'y_tick_style' : 'Custom', 'y_ticks' : [-a,0,a], 'y_tick_labels' : [-a,0.0,a], 'linewidth' : 2.0, 'y_lim' : (-a,a),'y_label' : 'Vm','y_ticks' : None,'y_label' : None})
                                    
                
            return plots


class SizeTuningOverview(Plotting):
    """
    The analysis of size tuning in the model.


    Parameters
    ----------
    l4_neurons : list
           The list of layer 4 neurons to include in the analysis.

    l23_neurons : list
           The list of layer 23 neurons to include in the analysis.

    l4_neurons_analog : list
           The list of layer 4 neurons for which sub-threshold signals were recorded to include in the analysis.

    l23_neurons_analog : list
           The list of layer 23 neurons for which sub-threshold signals were recorded to include in the analysis.
    """

    required_parameters = ParameterSet({
        'l4_neurons' : list,
        'l23_neurons' : list,
        'l4_neurons_analog' : list,
        'l23_neurons_analog' : list,
    })

    def subplot(self, subplotspec):
        plots = {}
        gs = gridspec.GridSpecFromSubplotSpec(8,24, subplot_spec=subplotspec,hspace=1.0, wspace=0.3)
        fontsize = 20
        
        lc = str(low_contrast)
        hc= str(high_contrast)
        
        dsv = param_filter_query(self.datastore,st_name='DriftingSinusoidalGratingDisk',value_name=['Firing rate'])
        plots['L4ExcFR'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name' : 'radius', 'neurons': self.parameters.l4_neurons, 'sheet_name' : 'V1_Exc_L4','centered'  : False,'mean' : True, 'polar' : False, 'pool'  : False})),gs[0:4,0:4],{'fontsize' : fontsize,'title' : None,'x_label' : None , 'y_label' : r'Firing rate ($\frac{sp}{s}$)', 'y_lim' : (0,8), 'x_axis' : False, 'x_ticks' : False,'colors' : {'contrast : ' + hc : '#000000' , 'contrast : ' + lc : '#0073B3'}})
        if self.parameters.l23_neurons != []:
            plots['L23ExcFR'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name' : 'radius', 'neurons': self.parameters.l23_neurons, 'sheet_name' : 'V1_Exc_L2/3','centered'  : False,'mean' : True, 'polar' : False, 'pool'  : False})),gs[4:8,0:4],{'fontsize' : fontsize,'title' : None,'y_label' : r'Firing rate ($\frac{sp}{s}$)', 'y_lim' : (0,8),'colors' : {'contrast : ' + hc : '#000000' , 'contrast : ' + lc : '#0073B3'}})
        #(x+y)(F1_Vm,-(x+y)(F0_Vm,Mean(VM)))
        dsv = param_filter_query(self.datastore,st_name='DriftingSinusoidalGratingDisk',value_name=['F1_Vm'])
        plots['L4ExcVm'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name' : 'radius', 'neurons': self.parameters.l4_neurons_analog, 'sheet_name' : 'V1_Exc_L4','centered'  : False,'mean' : True, 'polar' : False, 'pool'  : False})),gs[0:4,5:9],{'fontsize' : fontsize,'title' : None,'x_label' : None , 'y_label' : r'Vm (mV)','x_axis' : False, 'x_ticks' : False,'colors' : {'contrast : ' + hc : '#000000' , 'contrast : ' + lc : '#0073B3'}})
        if self.parameters.l23_neurons != []:
            dsv = param_filter_query(self.datastore,st_name='DriftingSinusoidalGratingDisk',value_name=['-(x+y)(F0_Vm,Mean(VM))'])
            plots['L23ExcVm'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name' : 'radius', 'neurons': self.parameters.l23_neurons_analog, 'sheet_name' : 'V1_Exc_L2/3','centered'  : False,'mean' : True, 'polar' : False, 'pool'  : False})),gs[4:8,5:9],{'fontsize' : fontsize,'title' : None,'y_label' : r'Vm (mV)','colors' : {'contrast : ' + hc : '#000000' , 'contrast : ' + lc : '#0073B3'}})

        dsv = param_filter_query(self.datastore,value_name=['Suppression index of Firing rate'],sheet_name='V1_Exc_L4')
        plots['L4ExcSI'] = (PerNeuronValuePlot(dsv, ParameterSet({'cortical_view' : False,'neuron_ids':self.parameters.l4_neurons})),gs[0:4,10:14],{'fontsize' : fontsize,'title' : None,'x_label' : None , 'y_label' : '# neurons', 'x_axis' : False, 'x_ticks' : False,'num_bins': 10,'mark_mean' : True,'x_lim' : (0,1.0), 'y_lim' : (0,20),'colors' : {'contrast : ' + hc : '#000000' , 'contrast : ' + lc : '#0073B3'}})
        if self.parameters.l23_neurons != []:
            dsv = param_filter_query(self.datastore,value_name=['Suppression index of Firing rate'],sheet_name='V1_Exc_L2/3')
            plots['L2/3ExcSI'] = (PerNeuronValuePlot(dsv, ParameterSet({'cortical_view' : False,'neuron_ids':self.parameters.l23_neurons})),gs[4:8,10:14],{'fontsize' : fontsize,'title' : None,'x_label' : None , 'y_label' : '# neurons', 'x_label' : 'Suppression index' ,'num_bins': 10,'mark_mean' : True,'x_lim' : (0,1.0), 'y_lim' : (0,20),'colors' : {'contrast : ' + hc : '#000000' , 'contrast : ' + lc : '#0073B3'}})

        dsv = param_filter_query(self.datastore,value_name=['Max. facilitation radius of Firing rate'],sheet_name='V1_Exc_L4')
        plots['L4ExcMaxFacilitationRadius'] = (PerNeuronValuePlot(dsv, ParameterSet({'cortical_view' : False,'neuron_ids':self.parameters.l4_neurons})),gs[0:4,15:19],{'fontsize' : fontsize,'title' : None,'x_label' : None , 'y_label' : '# neurons', 'x_axis' : False, 'x_ticks' : False,'num_bins': 8,'mark_mean' : True,'x_lim' : (0,4.0), 'y_lim' : (0,20),'colors' : {'contrast : ' + hc : '#000000' , 'contrast : ' + lc : '#0073B3'}})
        if self.parameters.l23_neurons != []:
            dsv = param_filter_query(self.datastore,value_name=['Max. facilitation radius of Firing rate'],sheet_name='V1_Exc_L2/3')
            plots['L2/3ExcMaxFacilitationRadius'] = (PerNeuronValuePlot(dsv, ParameterSet({'cortical_view' : False,'neuron_ids':self.parameters.l23_neurons})),gs[4:8,15:19],{'fontsize' : fontsize,'title' : None,'x_label' : None , 'y_label' : '# neurons', 'x_label' : 'Maximum facillitation radius' ,'num_bins': 8,'mark_mean' : True,'x_lim' : (0,4.0), 'y_lim' : (0,20),'colors' : {'contrast : ' + hc : '#000000' , 'contrast : ' + lc : '#0073B3'}})

        dsv = param_filter_query(self.datastore,st_name='DriftingSinusoidalGratingDisk',value_name=['F0_Exc_Cond','F0_Inh_Cond'])
        #dsv = param_filter_query(self.datastore,st_name='DriftingSinusoidalGratingDisk',value_name=['(x+y)(F0_Exc_Cond,F1_Exc_Cond)','(x+y)(F0_Inh_Cond,F1_Inh_Cond)'])    
        plots['L4ExcCond,'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name' : 'radius', 'neurons': self.parameters.l4_neurons_analog, 'sheet_name' : 'V1_Exc_L4','centered'  : False,'mean' : True, 'polar' : False, 'pool'  : True})),gs[0:4,20:24],{'fontsize' : fontsize,'title' : None,'x_label' : None , 'x_axis' : False, 'x_ticks' : False, 'colors' : {'F0_Exc_Cond contrast : ' + hc : '#FF0000' , 'F0_Exc_Cond contrast : ' + lc : '#FFACAC','F0_Inh_Cond contrast : ' + hc : '#0000FF' , 'F0_Inh_Cond contrast : ' + lc : '#ACACFF'},'y_label' : 'Conductance (nS)'})
        if self.parameters.l23_neurons != []:
            dsv = param_filter_query(self.datastore,st_name='DriftingSinusoidalGratingDisk',value_name=['F0_Exc_Cond','F0_Inh_Cond'])
            #dsv = param_filter_query(self.datastore,st_name='DriftingSinusoidalGratingDisk',value_name=['(x+y)(F0_Exc_Cond,F1_Exc_Cond)','(x+y)(F0_Inh_Cond,F1_Inh_Cond)'])  
            plots['L23ExcCond'] = (PlotTuningCurve(dsv, ParameterSet({'parameter_name' : 'radius', 'neurons': self.parameters.l23_neurons_analog, 'sheet_name' : 'V1_Exc_L2/3','centered'  : False,'mean' : True, 'polar' : False, 'pool'  : True})),gs[4:8,20:24],{'fontsize' : fontsize,'title' : None,'colors' : {'F0_Exc_Cond contrast : ' + hc : '#FF0000' , 'F0_Exc_Cond contrast : ' + lc : '#FFACAC','F0_Inh_Cond contrast : ' + hc: '#0000FF' , 'F0_Inh_Cond contrast : ' + lc : '#ACACFF'},'y_label' : 'Conductance (nS)'})

        return plots


class SizeTuningOverviewNew(Plotting):
    """
    The analysis of size tuning in the model.


    Parameters
    ----------
    l4_neurons : list
           The list of layer 4 neurons to include in the analysis.

    l23_neurons : list
           The list of layer 23 neurons to include in the analysis.

    l4_neurons_analog : list
           The list of layer 4 neurons for which sub-threshold signals were recorded to include in the analysis.

    l23_neurons_analog : list
           The list of layer 23 neurons for which sub-threshold signals were recorded to include in the analysis.
    """

    required_parameters = ParameterSet({
        'l4_neurons' : list,
        'l23_neurons' : list,
        'l4_neurons_analog' : list,
        'l23_neurons_analog' : list,
    })

    err = 0

    def _fitgaussian(self,X,Y):
          from scipy.special import erf

          fitfunc = lambda p,x:  p[0]*erf(x/p[1])**2 - p[2] *erf(x/(p[1] + p[3]))**2 + p[4] *erf(x/(p[1]+ p[3]+p[5]))**2 + p[6]
          fitfunc_st = lambda p,x:  p[0]*erf(x/p[1])**2 - p[2] *erf(x/(p[1] + p[3]))**2 + p[4]
          errfunc = lambda p, x, y: numpy.linalg.norm(fitfunc(p,x) - y) # Distance to the target function
          errfunc_st = lambda p, x, y: numpy.linalg.norm(fitfunc_st(p,x) - y) # Distance to the target function

          err = []
          res = []
          p0 = [8.0, 0.43, 8.0, 0.18, 3.0 ,1.4,numpy.min(Y)] # Initial guess for the parameters

          err_st = []
          res_st = []
          p0_st = [8.0, 0.43, 8.0, 0.18,numpy.min(Y)] # Initial guess for the parameters

          for i in range(2,30):
           for j in range(5,22):
              p0_st[1] = i/30.0
              p0_st[3] = j/20.0
              r = scipy.optimize.fmin_tnc(errfunc_st, numpy.array(p0_st), args=(numpy.array(X),numpy.array(Y)),disp=0,bounds=[(0,None),(0,None),(0,None),(0,None),(0,None)],approx_grad=True)
              res_st.append(r)
              err_st.append(errfunc_st(r[0],numpy.array(X),numpy.array(Y)))

          res_st=res_st[numpy.nanargmin(err_st)]
          p0[0:4] = res_st[0][0:-1]
          p0[-1] = res_st[0][-1]
          res = []
          for j in range(5,33):
            for k in range(1,15):
                p0[3] = j/30.0
                p0[5] = k/6.0
                r = scipy.optimize.fmin_tnc(errfunc, numpy.array(p0), args=(numpy.array(X),numpy.array(Y)),disp=0,bounds=[(p0[0]*9/10,p0[0]*10/9),(p0[1]*9/10,p0[1]*10/9),(0,None),(0,None),(0,None),(0,None),(0,None)],approx_grad=True)

                res.append(r)
                err.append(errfunc(r[0],numpy.array(X),numpy.array(Y)))

          x = numpy.linspace(0,X[-1],100)
          res=res[numpy.nanargmin(err)]
          if numpy.linalg.norm(Y-numpy.mean(Y),2) != 0:
                err = numpy.linalg.norm(fitfunc(res[0],X)-Y,2)/numpy.linalg.norm(Y-numpy.mean(Y),2)
          else:
                err = 0
          return fitfunc(res[0],x), err

    def _fitgaussian_cond(self,X,Y):
          from scipy.special import erf

          fitfunc = lambda p,x:  p[0]*erf(x/p[1])**2 - p[2] *erf(x/(p[1] + p[3]))**2 + p[4] *erf(x/(p[1]+ p[3]+p[5]))**2 + p[6]
          errfunc = lambda p, x, y: numpy.linalg.norm(fitfunc(p,x) - y) # Distance to the target function

          err = []
          res = []
          p0 = [8.0, 0.43, 8.0, 0.18, 3.0 ,1.4,numpy.min(Y)] # Initial guess for the parameters



          for i in range(2,15):
           for j in range(5,11):
                for k in range(1,5):
                    p0[1] = i/15.0
                    p0[3] = j/10.0
                    p0[5] = k/2.0
                    r = scipy.optimize.fmin_tnc(errfunc, numpy.array(p0), args=(numpy.array(X),numpy.array(Y)),disp=0,bounds=[(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(None,None)],approx_grad=True)
                    res.append(r)
                    err.append(errfunc(r[0],numpy.array(X),numpy.array(Y)))

          x = numpy.linspace(0,X[-1],100)
          res=res[numpy.nanargmin(err)]

          if numpy.linalg.norm(Y-numpy.mean(Y),2) != 0:
                err = numpy.linalg.norm(fitfunc(res[0],X)-Y,2)/numpy.linalg.norm(Y-numpy.mean(Y),2)
          else:
                err = 0
          return fitfunc(res[0],x), err

    def get_vals(self,dsv,neuron):
        assert queries.ads_with_equal_stimulus_type(dsv)
        assert queries.equal_ads(dsv,except_params=['stimulus_id'])
        pnvs = dsv.get_analysis_result()

        st = [MozaikParametrized.idd(s.stimulus_id) for s in pnvs]
        tc_dict = colapse_to_dictionary([z.get_value_by_id(neuron) for z in pnvs],st,"radius")

        rads = list(tc_dict.values())[0][0]*2
        values = list(tc_dict.values())[0][1]
        a, b = list(zip(*sorted(zip(rads,values))))
        return numpy.array(a),numpy.array(b)
        

    def subplot(self, subplotspec):
        plots = {}
        gs = gridspec.GridSpecFromSubplotSpec(27,30, subplot_spec=subplotspec,hspace=2.0, wspace=1.2)
        fontsize = 12

        max_radius =  numpy.max(list(set([MozaikParametrized.idd(s).radius for s in queries.param_filter_query(self.datastore,st_name='DriftingSinusoidalGratingDisk').get_stimuli()])))
        orr =  MozaikParametrized.idd(queries.param_filter_query(self.datastore,st_name='DriftingSinusoidalGratingDisk').get_stimuli()[0]).orientation

        if len(self.parameters.l23_neurons) == 0:
            self.parameters.l23_neurons = None

        if len(self.parameters.l23_neurons_analog) == 0:
            self.parameters.l23_neurons_analog = None

        r = 2
        max_err = 0.3

        # NICE L4 NEURON
        def example_neuron(neuron,line,sheet):

          rads_lc , values_lc  = self.get_vals(queries.param_filter_query(self.datastore,identifier='PerNeuronValue',sheet_name=sheet,st_name='DriftingSinusoidalGratingDisk',value_name='Firing rate',analysis_algorithm='TrialAveragedFiringRate',st_contrast=low_contrast),neuron)
          fitvalues_lc, err = self._fitgaussian(rads_lc , values_lc)

          rads_hc , values_hc  = self.get_vals(queries.param_filter_query(self.datastore,identifier='PerNeuronValue',sheet_name=sheet,st_name='DriftingSinusoidalGratingDisk',value_name='Firing rate',analysis_algorithm='TrialAveragedFiringRate',st_contrast=100),neuron)
          fitvalues_hc, err = self._fitgaussian(rads_hc , values_hc)
                              
          ax = pylab.subplot(gs[6*line:6*line+6,1:9])
          ax.plot(rads_lc*2,values_lc,'ok')
          ax.plot(numpy.linspace(0,10.0,100),fitvalues_lc,'k')
          ax.plot(rads_hc*2,values_hc,'o',color='#0073B3',markeredgecolor='#0073B3',markeredgewidth=0)
          ax.plot(numpy.linspace(0,10.0,100),fitvalues_hc,color='#0073B3')
          if line == 2:
            ax.set_ylim(0,15.0)
          elif line == 1:
            ax.set_ylim(0,25.0)
          else:
            ax.set_ylim(0,5.0)
          disable_top_right_axis(pylab.gca())
          three_tick_axis(ax.yaxis)
          ax.yaxis.set_label_coords(-0.18, 0.5)
          if line == 2:
            #three_tick_axis(ax.xaxis)
            ax.set_xticks([0,5,10])
            ax.set_xlabel('Diameter (°)',fontsize=fontsize)
          else:
            remove_x_tick_labels()
            disable_xticks(ax)
          for label in pylab.gca().get_xticklabels() + pylab.gca().get_yticklabels():
                  label.set_fontsize(19)
          pylab.ylabel('firing rate (sp/s)',fontsize=fontsize)

          var = 'F1_Vm'

          rads_lc , values_lc  = self.get_vals(queries.param_filter_query(self.datastore,identifier='PerNeuronValue',sheet_name=sheet,st_name='DriftingSinusoidalGratingDisk',value_name=[var],st_contrast=low_contrast),neuron)
          fitvalues_lc, err = self._fitgaussian(rads_lc , values_lc)

          rads_hc , values_hc  = self.get_vals(queries.param_filter_query(self.datastore,identifier='PerNeuronValue',sheet_name=sheet,st_name='DriftingSinusoidalGratingDisk',value_name=[var],st_contrast=100),neuron)
          fitvalues_hc, err = self._fitgaussian(rads_hc , values_hc)
                              
          ax = pylab.subplot(gs[6*line:6*line+6,11:19])
          ax.plot(2*rads_lc,values_lc,'ok')
          ax.plot(numpy.linspace(0,10.0,100),fitvalues_lc,'k')
          ax.plot(2*rads_hc,values_hc,'o',color='#0073B3',markeredgecolor='#0073B3',markeredgewidth=0)
          ax.plot(numpy.linspace(0,10.0,100),fitvalues_hc,color='#0073B3')
          if line == 2:
            ax.set_ylim(0,1.8)
          elif line == 1:
            ax.set_ylim(0,7)
          elif line == 0:
            ax.set_ylim(0,7)

          disable_top_right_axis(pylab.gca())  
          three_tick_axis(ax.yaxis)  
          if line == 2:
            #three_tick_axis(ax.xaxis)
            ax.set_xticks([0,5,10.0])
            ax.set_xlabel('Diameter (°)',fontsize=fontsize)
          else:
            disable_xticks(ax)
            remove_x_tick_labels()

          for label in pylab.gca().get_xticklabels() + pylab.gca().get_yticklabels():
                  label.set_fontsize(19)
          pylab.ylabel('Vm (mV)',fontsize=fontsize)

          rads_lc_e , values_lc_e  = self.get_vals(queries.param_filter_query(self.datastore,identifier='PerNeuronValue',sheet_name=sheet,st_name='DriftingSinusoidalGratingDisk',value_name=['x-y(F0_Exc_Cond,Mean(ECond))'],st_contrast=low_contrast),neuron)
          values_lc_e*=1000
          fitvalues_lc_e, err = self._fitgaussian_cond(rads_lc_e , values_lc_e)

          rads_hc_e , values_hc_e  = self.get_vals(queries.param_filter_query(self.datastore,identifier='PerNeuronValue',sheet_name=sheet,st_name='DriftingSinusoidalGratingDisk',value_name=['x-y(F0_Exc_Cond,Mean(ECond))'],st_contrast=100),neuron)
          values_hc_e*=1000
          fitvalues_hc_e, err = self._fitgaussian_cond(rads_hc_e, values_hc_e)

          rads_lc_i , values_lc_i  = self.get_vals(queries.param_filter_query(self.datastore,identifier='PerNeuronValue',sheet_name=sheet,st_name='DriftingSinusoidalGratingDisk',value_name=['x-y(F0_Inh_Cond,Mean(ICond))'],st_contrast=low_contrast),neuron)
          values_lc_i*=1000
          fitvalues_lc_i, err = self._fitgaussian_cond(rads_lc_i , values_lc_i)

          rads_hc_i , values_hc_i  = self.get_vals(queries.param_filter_query(self.datastore,identifier='PerNeuronValue',sheet_name=sheet,st_name='DriftingSinusoidalGratingDisk',value_name=['x-y(F0_Inh_Cond,Mean(ICond))'],st_contrast=100),neuron)
          values_hc_i*=1000
          fitvalues_hc_i, err = self._fitgaussian_cond(rads_hc_i, values_hc_i)


          ax = pylab.subplot(gs[6*line:6*line+6,21:29])
          ax.plot(2*rads_lc_e,values_lc_e,'o',color='#FFACAC',markeredgecolor='#FFACAC',markeredgewidth=0)
          ax.plot(numpy.linspace(0,10.0,100),fitvalues_lc_e,color='#FFACAC')
          ax.plot(2*rads_hc_e,values_hc_e,'o',color='#FF0000',markeredgecolor='#FF0000',markeredgewidth=0)
          ax.plot(numpy.linspace(0,10.0,100),fitvalues_hc_e,color='#FF0000')

          ax.plot(2*rads_lc_i,values_lc_i,'o',color='#ACACFF',markeredgecolor='#ACACFF',markeredgewidth=0)
          ax.plot(numpy.linspace(0,10.0,100),fitvalues_lc_i,color='#ACACFF')
          ax.plot(2*rads_hc_i,values_hc_i,'o',color='#0000FF',markeredgecolor='#0000FF',markeredgewidth=0)
          ax.plot(numpy.linspace(0,10.0,100),fitvalues_hc_i,color='#0000FF')
          #ax.set_ylim(0,8)
          if line == 2:
            ax.set_ylim(0,15.0)
          elif line == 0:
            ax.set_ylim(0,3.0)
          else:
            ax.set_ylim(0,3.0)

          if line == 2:
            #three_tick_axis(ax.xaxis)
            ax.set_xticks([0,5,10.0])
            ax.set_xlabel('Diameter (°)',fontsize=fontsize)
          else:
            disable_xticks(ax)
            remove_x_tick_labels()

          disable_top_right_axis(pylab.gca())  
          three_tick_axis(ax.yaxis)  
          for label in pylab.gca().get_xticklabels() + pylab.gca().get_yticklabels():
                  label.set_fontsize(19)
          pylab.ylabel('conductance (nS)',fontsize=fontsize)
        
        nice_neuron_l4 = self.parameters.l4_neurons_analog[45]
        not_nice_neuron_l4 = self.parameters.l4_neurons_analog[46]
        if self.parameters.l23_neurons_analog is not None:
            nice_neuron_l23 = self.parameters.l23_neurons_analog[27]

        example_neuron(nice_neuron_l4,0,'V1_Exc_L4')
        example_neuron(not_nice_neuron_l4,1,'V1_Exc_L4')
        if self.parameters.l23_neurons_analog is not None:
            example_neuron(nice_neuron_l23,2,'V1_Exc_L2/3')

        def size_tuning_measures(rads,values):
              crf_index  = numpy.argmax(values[:-1]-values[1:] > 0)
              if crf_index == 0: crf_index = len(values)-1
        
              crf_size = 2 * rads[crf_index]
              
              if crf_index < len(values)-1 and crf_index != 0:
                  supp_index = crf_index+numpy.argmin(values[crf_index+1:])+1
              else:
                  supp_index = len(values)-1

              if supp_index < len(values)-1 and supp_index != 0:
                  cs_index = supp_index+numpy.argmax(values[supp_index+1:])+1
              else:
                  cs_index = len(values)-1

              if values[crf_index] != 0:
                  si = (values[crf_index]-values[supp_index])/values[crf_index]
              else:
                  si = 0

              if values[crf_index] != 0:
                  csi = (values[cs_index]-values[supp_index])/values[crf_index]
              else:
                  csi = 0
              return [crf_size,si,csi]        

        selected_l4_neurons=[neuron for neuron in self.parameters.l4_neurons if numpy.max(self.get_vals(queries.param_filter_query(self.datastore,identifier='PerNeuronValue',sheet_name='V1_Exc_L4',st_name='DriftingSinusoidalGratingDisk',analysis_algorithm='TrialAveragedFiringRate',value_name='Firing rate',st_contrast=100),neuron)) > r]
        selected_l23_neurons=[neuron for neuron in self.parameters.l23_neurons if numpy.max(self.get_vals(queries.param_filter_query(self.datastore,identifier='PerNeuronValue',sheet_name='V1_Exc_L2/3',st_name='DriftingSinusoidalGratingDisk',analysis_algorithm='TrialAveragedFiringRate',value_name='Firing rate',st_contrast=100),neuron)) > r]
        print(str(len(self.parameters.l4_neurons)) + " " +  str(len(selected_l4_neurons)))
        print(str(len(self.parameters.l23_neurons)) + " " +  str(len(selected_l23_neurons)))

        l4_hc_crf_size = []
        l4_hc_si = []
        l4_hc_csi = []
        selected_l4_neurons_hc = []

        dsv = queries.param_filter_query(self.datastore,identifier='PerNeuronValue',sheet_name='V1_Exc_L4',st_name='DriftingSinusoidalGratingDisk',analysis_algorithm='TrialAveragedFiringRate',value_name='Firing rate',st_contrast=high_contrast)
        for neuron in selected_l4_neurons:
            rad, vals = self.get_vals(dsv,neuron)
            f, err = self._fitgaussian(rad,vals)
            if err <= max_err:
                selected_l4_neurons_hc.append(neuron)
                crf, si, csi = size_tuning_measures(numpy.linspace(0,5.0,100),f)
                l4_hc_crf_size.append(crf)
                l4_hc_si.append(si)
                l4_hc_csi.append(csi)

        l4_lc_crf_size = []
        l4_lc_si = []
        l4_lc_csi = []
        selected_l4_neurons_lc = []
        to_delete = []

        dsv = queries.param_filter_query(self.datastore,identifier='PerNeuronValue',sheet_name='V1_Exc_L4',st_name='DriftingSinusoidalGratingDisk',analysis_algorithm='TrialAveragedFiringRate',value_name='Firing rate',st_contrast=low_contrast)
        for i, neuron in enumerate(selected_l4_neurons_hc):
            rad, vals = self.get_vals(dsv,neuron)
            f, err = self._fitgaussian(rad,vals)
            if err <= max_err:
                selected_l4_neurons_lc.append(neuron)
                crf, si, csi = size_tuning_measures(numpy.linspace(0,5.0,100),f)
                l4_lc_crf_size.append(crf)
                l4_lc_si.append(si)
                l4_lc_csi.append(csi)
            else:
                to_delete.append(i)

        for i,j in enumerate(to_delete):
            del l4_hc_crf_size[j-i]
            del l4_hc_si[j-i]
            del l4_hc_csi[j-i]

        selected_l4_neurons = selected_l4_neurons_lc
        print('Removed \% of L4 neurons:' + str(float(len(self.parameters.l4_neurons)-len(selected_l4_neurons))/len(self.parameters.l4_neurons)))

        l4_hc_crf_size_fr = l4_hc_crf_size
        l4_hc_si_fr = l4_hc_si
        l4_hc_csi_fr = l4_hc_csi
        l4_lc_crf_size_fr = l4_lc_crf_size
        l4_lc_si_fr = l4_lc_si
        l4_lc_csi_fr = l4_lc_csi
        
        if self.parameters.l23_neurons is not None:
            l23_hc_crf_size = []
            l23_hc_si = []
            l23_hc_csi = []
            selected_l23_neurons_hc = []

            dsv = queries.param_filter_query(self.datastore,identifier='PerNeuronValue',sheet_name='V1_Exc_L2/3',st_name='DriftingSinusoidalGratingDisk',analysis_algorithm='TrialAveragedFiringRate',value_name='Firing rate',st_contrast=high_contrast)
            for neuron in selected_l23_neurons:
                rad, vals = self.get_vals(dsv,neuron)
                f, err = self._fitgaussian(rad,vals)
                if err <= max_err:
                    selected_l23_neurons_hc.append(neuron)
                    crf, si, csi = size_tuning_measures(numpy.linspace(0,5.0,100),f)
                    l23_hc_crf_size.append(crf)
                    l23_hc_si.append(si)
                    l23_hc_csi.append(csi)

            l23_lc_crf_size = []
            l23_lc_si = []
            l23_lc_csi = []
            selected_l23_neurons_lc = []
            to_delete = []

            dsv = queries.param_filter_query(self.datastore,identifier='PerNeuronValue',sheet_name='V1_Exc_L2/3',st_name='DriftingSinusoidalGratingDisk',analysis_algorithm='TrialAveragedFiringRate',value_name='Firing rate',st_contrast=low_contrast)
            for i, neuron in enumerate(selected_l23_neurons_hc):
                rad, vals = self.get_vals(dsv,neuron)
                f, err = self._fitgaussian(rad,vals)
                if err <= max_err:
                    selected_l23_neurons_lc.append(neuron)
                    crf, si, csi = size_tuning_measures(numpy.linspace(0,5.0,100),f)
                    l23_lc_crf_size.append(crf)
                    l23_lc_si.append(si)
                    l23_lc_csi.append(csi)
                else:
                    to_delete.append(i)

            for i,j in enumerate(to_delete):
                del l23_hc_crf_size[j-i]
                del l23_hc_si[j-i]
                del l23_hc_csi[j-i]
                
            selected_l23_neurons = selected_l23_neurons_lc
            print('Removed \% of L2/3 neurons:' + str(float(len(self.parameters.l23_neurons)-len(selected_l23_neurons))/len(self.parameters.l23_neurons)))

            l23_hc_crf_size_fr = l23_hc_crf_size
            l23_hc_si_fr = l23_hc_si
            l23_hc_csi_fr = l23_hc_csi
            l23_lc_crf_size_fr = l23_lc_crf_size
            l23_lc_si_fr = l23_lc_si
            l23_lc_csi_fr = l23_lc_csi

        ax = pylab.subplot(gs[20:27,1:6])
        ax.plot(l4_hc_si,l4_lc_si,'ow',markeredgecolor='k')         
        ax.plot(l23_hc_si,l23_lc_si,'ok') 
        ax.plot([0,1],[0,1],'k')
        disable_top_right_axis(pylab.gca())  
        three_tick_axis(ax.yaxis)  
        three_tick_axis(ax.xaxis)
        pylab.xlim(0,0.6)
        pylab.ylim(0,0.6)
        #pylab.title('spikes',fontsize=fontsize)
        
        ax.annotate("",xy=(numpy.mean(l4_hc_si+l23_hc_si), 0.55), xycoords='data',xytext=(numpy.mean(l4_hc_si+l23_hc_si), 0.6), textcoords='data',arrowprops=dict(arrowstyle="->",connectionstyle="arc3",linewidth=3.0,color='k'))
        ax.annotate("",xy=(0.55,numpy.mean(l4_lc_si+l23_lc_si)), xycoords='data',xytext=(0.6,numpy.mean(l4_lc_si+l23_lc_si)), textcoords='data',arrowprops=dict(arrowstyle="->",connectionstyle="arc3",linewidth=3.0,color='k'))

        for label in pylab.gca().get_xticklabels() + pylab.gca().get_yticklabels():
                label.set_fontsize(19)
        pylab.xlabel('SI (high-contrast)',fontsize=fontsize)
        pylab.ylabel('SI (low-contrast)',fontsize=fontsize)

        mean_and_sem = lambda x : (numpy.mean(x),numpy.std(x)/numpy.sqrt(len(x)))

        print('SI (high-contrast): L4 '+ str(mean_and_sem(l4_hc_si)))
        print('SI (high-contrast): L23 '+ str(mean_and_sem(l23_hc_si)))
        print('SI (low-contrast): L4'+ str(mean_and_sem(l4_lc_si)))
        print('SI (low-contrast): L23'+ str(mean_and_sem(l23_lc_si)))


        ax = pylab.subplot(gs[20:27,7:12])
        ax.plot(l4_hc_csi,l4_lc_csi,'ow',markeredgecolor='k')         
        ax.plot(l23_hc_csi,l23_lc_csi,'ok') 
        ax.plot([0,1],[0,1],'k')
        disable_top_right_axis(pylab.gca())  
        three_tick_axis(ax.yaxis)  
        three_tick_axis(ax.xaxis)
        pylab.xlim(0,0.6)
        pylab.ylim(0,0.6)
        #pylab.title('spikes',fontsize=fontsize)

        ax.annotate("",xy=(numpy.mean(l4_hc_csi+l23_hc_csi), 0.55), xycoords='data',xytext=(numpy.mean(l4_hc_csi+l23_hc_csi), 0.6), textcoords='data',arrowprops=dict(arrowstyle="->",connectionstyle="arc3",linewidth=3.0,color='k'))
        ax.annotate("",xy=(0.55,numpy.mean(l4_lc_csi+l23_lc_csi)), xycoords='data',xytext=(0.6,numpy.mean(l4_lc_csi+l23_lc_csi)), textcoords='data',arrowprops=dict(arrowstyle="->",connectionstyle="arc3",linewidth=3.0,color='k'))

        
        for label in pylab.gca().get_xticklabels() + pylab.gca().get_yticklabels():
                label.set_fontsize(19)
        pylab.xlabel('CSI (high-contrast)',fontsize=fontsize)
        pylab.ylabel('CSI (low-contrast)',fontsize=fontsize)
        print('CSI (high-contrast): L4 ' + str(mean_and_sem(l4_hc_csi)))
        print('CSI (high-contrast): L23 ' + str(mean_and_sem(l23_hc_csi)))
        print('CSI (low-contrast): L4' + str(mean_and_sem(l4_lc_csi)))
        print('CSI (low-contrast): L23' + str(mean_and_sem(l23_lc_csi)))



        ax = pylab.subplot(gs[20:27,13:18])
        ax.plot(l4_hc_si,l4_hc_csi,'ow',markeredgecolor='k')         
        ax.plot(l23_hc_si,l23_hc_csi,'ok') 
        ax.plot([0,1],[0,1],'k')
        disable_top_right_axis(pylab.gca())  
        three_tick_axis(ax.yaxis)  
        three_tick_axis(ax.xaxis)
        pylab.xlim(0,0.6)
        pylab.ylim(0,0.6)
        #pylab.title('spikes',fontsize=fontsize)
        
        for label in pylab.gca().get_xticklabels() + pylab.gca().get_yticklabels():
                label.set_fontsize(19)
        pylab.xlabel('SI (high-contrast)',fontsize=fontsize)
        pylab.ylabel('CSI (high-contrast)',fontsize=fontsize)

        ax.annotate("",xy=(numpy.mean(l4_hc_si+l23_hc_si), 0.55), xycoords='data',xytext=(numpy.mean(l4_hc_si+l23_hc_si), 0.6), textcoords='data',arrowprops=dict(arrowstyle="->",connectionstyle="arc3",linewidth=3.0,color='k'))
        ax.annotate("",xy=(0.55,numpy.mean(l4_hc_csi+l23_hc_csi)), xycoords='data',xytext=(0.6,numpy.mean(l4_hc_csi+l23_hc_csi)), textcoords='data',arrowprops=dict(arrowstyle="->",connectionstyle="arc3",linewidth=3.0,color='k'))

        ax = pylab.subplot(gs[20:27,19:24])
        l4_lc_crf_size = [size for i,size in enumerate(l4_lc_crf_size) if l4_hc_si_fr[i] > 0 and l4_lc_si_fr[i] > 0]
        l4_hc_crf_size = [size for i,size in enumerate(l4_hc_crf_size) if l4_hc_si_fr[i] > 0 and l4_lc_si_fr[i] > 0]

        if self.parameters.l23_neurons is not None:
            l23_lc_crf_size = [size for i,size in enumerate(l23_lc_crf_size) if l23_hc_si_fr[i] > 0 and l23_lc_si_fr[i] > 0]
            l23_hc_crf_size = [size for i,size in enumerate(l23_hc_crf_size) if l23_hc_si_fr[i] > 0 and l23_lc_si_fr[i] > 0]

        ax.plot(l4_hc_crf_size,l4_lc_crf_size,'ow',markeredgecolor='k')         
        ax.plot(l23_hc_crf_size,l23_lc_crf_size,'ok') 
        ax.plot([0,5],[0,5],'k')
        disable_top_right_axis(pylab.gca())  
        three_tick_axis(ax.yaxis)  
        three_tick_axis(ax.xaxis)
        pylab.xlim(0,5.0)
        pylab.ylim(0,5.0)
        #pylab.title('membrane potential',fontsize=fontsize)
        
        ax.annotate("",xy=(numpy.mean(l4_hc_crf_size+l23_hc_crf_size), 5.7), xycoords='data',xytext=(numpy.mean(l4_hc_crf_size+l23_hc_crf_size), 6.0), textcoords='data',arrowprops=dict(arrowstyle="->",connectionstyle="arc3",linewidth=3.0,color='k'))
        ax.annotate("",xy=(5.7,numpy.mean(l4_lc_crf_size+l23_lc_crf_size)), xycoords='data',xytext=(6.0,numpy.mean(l4_lc_crf_size+l23_lc_crf_size)), textcoords='data',arrowprops=dict(arrowstyle="->",connectionstyle="arc3",linewidth=3.0,color='k'))

        for label in pylab.gca().get_xticklabels() + pylab.gca().get_yticklabels():
                label.set_fontsize(19)
        pylab.xlabel('MFD size (high-contrast)',fontsize=fontsize)
        pylab.ylabel('MFD size (low-contrast)',fontsize=fontsize)
        
        print('MFD (high-contrast): L4 ' + str(mean_and_sem(l4_hc_crf_size)))
        print('MFD (high-contrast): L23 ' + str(mean_and_sem(l23_hc_crf_size)))
        print('MFD (low-contrast): L4' + str(mean_and_sem(l4_lc_crf_size)))
        print('MFD (low-contrast): L23' + str(mean_and_sem(l23_lc_crf_size)))

        dsv = queries.param_filter_query(self.datastore,identifier='PerNeuronValue',sheet_name='V1_Exc_L4',st_name='DriftingSinusoidalGratingDisk',value_name='x-y(F0_Exc_Cond,Mean(ECond))',st_contrast=high_contrast)
        l4_hc_crf_size,l4_hc_si,l4_hc_csi = zip(*[size_tuning_measures(numpy.linspace(0,5.0,100),self._fitgaussian_cond(*self.get_vals(dsv,neuron))[0]) for neuron in self.parameters.l4_neurons_analog])
        dsv = queries.param_filter_query(self.datastore,identifier='PerNeuronValue',sheet_name='V1_Exc_L4',st_name='DriftingSinusoidalGratingDisk',value_name='x-y(F0_Exc_Cond,Mean(ECond))',st_contrast=low_contrast)
        l4_lc_crf_size,l4_lc_si,l4_lc_csi = zip(*[size_tuning_measures(numpy.linspace(0,5.0,100),self._fitgaussian_cond(*self.get_vals(dsv,neuron))[0]) for neuron in self.parameters.l4_neurons_analog])


        if self.parameters.l23_neurons is not None:
            dsv = queries.param_filter_query(self.datastore,identifier='PerNeuronValue',sheet_name='V1_Exc_L2/3',st_name='DriftingSinusoidalGratingDisk',value_name='x-y(F0_Exc_Cond,Mean(ECond))',st_contrast=high_contrast)
            l23_hc_crf_size,l23_hc_si,l23_hc_csi = zip(*[size_tuning_measures(numpy.linspace(0,5.0,100),self._fitgaussian_cond(*self.get_vals(dsv,neuron))[0]) for neuron in self.parameters.l23_neurons_analog])
            dsv = queries.param_filter_query(self.datastore,identifier='PerNeuronValue',sheet_name='V1_Exc_L2/3',st_name='DriftingSinusoidalGratingDisk',value_name='x-y(F0_Exc_Cond,Mean(ECond))',st_contrast=low_contrast)
            l23_lc_crf_size,l23_lc_si,l23_lc_csi = zip(*[size_tuning_measures(numpy.linspace(0,5.0,100),self._fitgaussian_cond(*self.get_vals(dsv,neuron))[0]) for neuron in self.parameters.l23_neurons_analog])

        ax = pylab.subplot(gs[20:27,25:30])
        ax.plot(l4_hc_si,l4_lc_si,'ow',markeredgecolor='#FF0000')         
        ax.plot(l23_hc_si,l23_lc_si,'o',color='#FF0000',markeredgecolor='#FF0000') 

        ax.annotate("",xy=(numpy.mean(l4_hc_si+l23_hc_si), 0.55), xycoords='data',xytext=(numpy.mean(l4_hc_si+l23_hc_si), 0.6), textcoords='data',arrowprops=dict(arrowstyle="->",connectionstyle="arc3",linewidth=3.0,color='#FF0000'))
        ax.annotate("",xy=(0.55,numpy.mean(l4_lc_si+l23_lc_si)), xycoords='data',xytext=(0.6,numpy.mean(l4_lc_si+l23_lc_si)), textcoords='data',arrowprops=dict(arrowstyle="->",connectionstyle="arc3",linewidth=3.0,color='#FF0000'))

        dsv = queries.param_filter_query(self.datastore,identifier='PerNeuronValue',sheet_name='V1_Exc_L4',st_name='DriftingSinusoidalGratingDisk',value_name='x-y(F0_Inh_Cond,Mean(ICond))',st_contrast=high_contrast)
        l4_hc_crf_size,l4_hc_si,l4_hc_csi = zip(*[size_tuning_measures(numpy.linspace(0,5.0,100),self._fitgaussian_cond(*self.get_vals(dsv,neuron))[0]) for neuron in self.parameters.l4_neurons_analog])
        dsv = queries.param_filter_query(self.datastore,identifier='PerNeuronValue',sheet_name='V1_Exc_L4',st_name='DriftingSinusoidalGratingDisk',value_name='x-y(F0_Inh_Cond,Mean(ICond))',st_contrast=low_contrast)
        l4_lc_crf_size,l4_lc_si,l4_lc_csi = zip(*[size_tuning_measures(numpy.linspace(0,5.0,100),self._fitgaussian_cond(*self.get_vals(dsv,neuron))[0]) for neuron in self.parameters.l4_neurons_analog])
        if self.parameters.l23_neurons is not None:
            dsv = queries.param_filter_query(self.datastore,identifier='PerNeuronValue',sheet_name='V1_Exc_L2/3',st_name='DriftingSinusoidalGratingDisk',value_name='x-y(F0_Inh_Cond,Mean(ICond))',st_contrast=high_contrast)
            l23_hc_crf_size,l23_hc_si,l23_hc_csi = zip(*[size_tuning_measures(numpy.linspace(0,5.0,100),self._fitgaussian_cond(*self.get_vals(dsv,neuron))[0]) for neuron in self.parameters.l23_neurons_analog])
            dsv = queries.param_filter_query(self.datastore,identifier='PerNeuronValue',sheet_name='V1_Exc_L2/3',st_name='DriftingSinusoidalGratingDisk',value_name='x-y(F0_Inh_Cond,Mean(ICond))',st_contrast=low_contrast)
            l23_lc_crf_size,l23_lc_si,l23_lc_csi = zip(*[size_tuning_measures(numpy.linspace(0,5.0,100),self._fitgaussian_cond(*self.get_vals(dsv,neuron))[0]) for neuron in self.parameters.l23_neurons_analog])

        ax.plot(l4_hc_si,l4_lc_si,'ow',markeredgecolor='#0000FF')         
        ax.plot(l23_hc_si,l23_lc_si,'o',color='#0000FF',markeredgecolor='#0000FF') 

        ax.annotate("",xy=(numpy.mean(l4_hc_si+l23_hc_si), 0.55), xycoords='data',xytext=(numpy.mean(l4_hc_si+l23_hc_si), 0.6), textcoords='data',arrowprops=dict(arrowstyle="->",connectionstyle="arc3",linewidth=3.0,color='#0000FF'))
        ax.annotate("",xy=(0.55,numpy.mean(l4_lc_si+l23_lc_si)), xycoords='data',xytext=(0.6,numpy.mean(l4_lc_si+l23_lc_si)), textcoords='data',arrowprops=dict(arrowstyle="->",connectionstyle="arc3",linewidth=3.0,color='#0000FF'))


        ax.plot([0,1],[0,1],'k')
        disable_top_right_axis(pylab.gca())  
        three_tick_axis(ax.yaxis)  
        three_tick_axis(ax.xaxis)
        pylab.xlim(0,0.3)
        pylab.ylim(0,0.3)
        #pylab.title('syn. conductances',fontsize=fontsize)
        
        for label in pylab.gca().get_xticklabels() + pylab.gca().get_yticklabels():
                label.set_fontsize(19)
        pylab.xlabel('SI (high-contrast)',fontsize=fontsize)
        pylab.ylabel('SI (low-contrast)',fontsize=fontsize)

        return plots


class TrialToTrialVariabilityComparisonNew(Plotting):
    """
    This figure plots compares the trial-to-trial variability measure in the model to the one published in Baudot et al. 2016. 
      
    Parameters
    ----------
    sheet_name1 : str
               The name of the sheet corresponding to layer 4 excitatory neurons.
              
    sheet_name2 : str
          The name of the sheet corresponding to layer 2/3 excitatory neurons.


    data_ni : str
               The corresponding statistic for natural images in Baudot et al. 2016.
              
    data_dg : str
          The corresponding statistic for drifting gratings in Baudot et al. 2016.

    """

    required_parameters = ParameterSet({
        'sheet_name1' : str, # The name of the sheet in which to do the analysis
        'sheet_name2' : str, # The name of the sheet in which to do the analysis
        'data_ni' : float,
        'data_dg' : float,
    })


    def plot(self):
        self.fig = pylab.figure(facecolor='w', **self.fig_param)
        gs = gridspec.GridSpec(1, 4)
        gs.update(left=0.07, right=0.97, top=0.9, bottom=0.1,wspace=0.1)

        orr = list(set([MozaikParametrized.idd(s).orientation for s in queries.param_filter_query(self.datastore,st_name='FullfieldDriftingSinusoidalGrating',st_contrast=ttcc_contrast).get_stimuli()]))   
        l4_exc_or = self.datastore.get_analysis_result(identifier='PerNeuronValue',value_name = 'LGNAfferentOrientation', sheet_name = self.parameters.sheet_name1)

        if self.parameters.sheet_name2 != 'None':
             l23_exc_or = self.datastore.get_analysis_result(identifier='PerNeuronValue',value_name = 'LGNAfferentOrientation', sheet_name = self.parameters.sheet_name2)

        mean_and_sem = lambda x : (numpy.mean(x),numpy.std(x)/numpy.sqrt(len(x)))
        # lets calculate spont. activity trial to trial variability
        # we assume that the spontaneous activity had already the spikes removed

        def calculate_sp(datastore,sheet_name):
            dsv = queries.param_filter_query(datastore,st_name='InternalStimulus',st_direct_stimulation_name=None,sheet_name=sheet_name,analysis_algorithm='ActionPotentialRemoval',ads_unique=True)
            ids = dsv.get_analysis_result()[0].ids
            sp= {}
            for idd in ids:
                assert len(dsv.get_analysis_result()) == 1
                s = dsv.get_analysis_result()[0].get_asl_by_id(idd).magnitude
                logger.info(str(s))
                logger.info(str(numpy.shape(s)))
                l = int(len(s)/10)
                z = [s[i*l:(i+1)*l] for i in range(0,10)]
                logger.info(str(numpy.array(z)))
                logger.info(str(numpy.shape(numpy.array(z))))

                sp[idd] = 1/numpy.mean(numpy.std(numpy.array(z),axis=0,ddof=1))

            return sp

        sp_l4 = calculate_sp(self.datastore,self.parameters.sheet_name1)
        if self.parameters.sheet_name2 != 'None':
            sp_l23 = calculate_sp(self.datastore,self.parameters.sheet_name2)
        else:
            sp_l23=0
        
        def calculate_var_ratio(datastore,sheet_names,sp,ors):
            #lets calculate the mean of trial-to-trial variances across the neurons in the datastore for gratings 
            std_gr = []

            for j,sheet_name in enumerate(sheet_names):
                dsv = queries.param_filter_query(datastore,st_name='FullfieldDriftingSinusoidalGrating',sheet_name=sheet_name,st_contrast=ttcc_contrast,analysis_algorithm='ActionPotentialRemoval')
                assert queries.equal_ads(dsv, except_params=['stimulus_id'])
                ids = dsv.get_analysis_result()[0].ids

                for i in ids:
                    # find the or pereference of the neuron
                    o = orr[numpy.argmin([circular_dist(o,ors[j][0].get_value_by_id(i),numpy.pi) for o in orr])]
                    #assert len(queries.param_filter_query(dsv,st_orientation=o).get_analysis_result())==10

                    s = [d.get_asl_by_id(i).magnitude[200:] for d in dsv.get_analysis_result()]
                    a = 1/numpy.mean(numpy.std(s,axis=0,ddof=1))

                    std_gr.append(a / sp[j][i])

            std_gr,sem_gr = mean_and_sem(std_gr)

            #lets calculate the mean of trial-to-trial variances across the neurons in the datastore for natural images 
            s = []
            for j,sheet_name in enumerate(sheet_names):
                dsv = queries.param_filter_query(datastore,st_name='NaturalImageWithEyeMovement',sheet_name=sheet_name,analysis_algorithm='ActionPotentialRemoval')
                ids = dsv.get_analysis_result()[0].ids
                s += [1/numpy.mean(numpy.std([d.get_asl_by_id(idd).magnitude for d in dsv.get_analysis_result()],axis=0,ddof=1))/sp[j][idd] for idd in ids]

            std_ni,sem_ni = mean_and_sem(s)

            return std_gr,std_ni,sem_gr,sem_ni

        var_gr_l4,var_ni_l4,sem_gr_l4,sem_ni_l4 = calculate_var_ratio(self.datastore,[self.parameters.sheet_name1],[sp_l4],[l4_exc_or])
        print('Noise magnitude L4 gratings: ' + str(var_gr_l4))
        print('Standard error of noise magnitude L4 gratings: ' + str(sem_gr_l4))
        print('Noise magnitude L4 natural images: ' + str(var_ni_l4))
        print('Standard error of noise magnitude L4 natural images: ' + str(sem_ni_l4))

        if self.parameters.sheet_name2 != 'None':
            var_gr_l23,var_ni_l23,sem_gr_l23,sem_ni_l23 = calculate_var_ratio(self.datastore,[self.parameters.sheet_name2],[sp_l23],[l23_exc_or])
            print('Noise magnitude L2/3 gratings: ' + str(var_gr_l23))
            print('Standard error of noise magnitude L2/3 gratings: ' + str(sem_gr_l23))
            print('Noise magnitude L2/3 natural images: ' + str(var_ni_l23))
            print('Standard error of noise magnitude L2/3 natural images: ' + str(sem_ni_l23))

            var_gr_pooled,var_ni_pooled,sem_gr_pooled,sem_ni_pooled = calculate_var_ratio(self.datastore,[self.parameters.sheet_name1,self.parameters.sheet_name2],[sp_l4,sp_l23],[l4_exc_or,l23_exc_or])
            print('Noise magnitude pooled gratings: ' + str(var_gr_pooled))
            print('Standard error of noise magnitude pooled gratings: ' + str(sem_gr_pooled))
            print('Noise magnitude pooled natural images: ' + str(var_ni_pooled))
            print('Standard error of noise magnitude pooled natural images: ' + str(sem_ni_pooled))

        else:
            var_gr_l23,var_ni_l23,sem_gr_l23,sem_ni_l23 = 0,0,0,0
            var_gr_pooled,var_ni_pooled,sem_gr_pooled,sem_ni_pooled = var_gr_l4,var_ni_l4,sem_gr_l4,sem_ni_l4

        lw = pylab.rcParams['axes.linewidth']
        pylab.rc('axes', linewidth=3)
        width = 0.25
        x = numpy.array([width,1-width])

        def plt(a,b,a_err=None,b_err=None):
            if a_err is None or b_err is None:
                rects = pylab.bar(x,[a*100-100,b*100-100],width = width,color='k')
            else:
                rects = pylab.bar(x,[a*100-100,b*100-100], yerr = [a_err*100,b_err*100],capsize=5,width = width,color='k')
                #rects.errorbar[0].set_color('r')
            rects[0].set_color('r')
            pylab.xlim(0,1.0)
            pylab.ylim(-20,50)
            pylab.xticks(x,["DG","NI"])
            pylab.yticks([-20,0,50],["80%","100%","150%"])
            pylab.axhline(0.0,color='k',linewidth=3)
            disable_top_right_axis(pylab.gca())
            disable_xticks(pylab.gca())
            for label in pylab.gca().get_xticklabels() + pylab.gca().get_yticklabels():
                label.set_fontsize(19)

        ax = pylab.subplot(gs[0,0])
        plt(var_gr_l4,var_ni_l4)
        pylab.title("Layer 4",fontsize=19,y=1.05)

        ax = pylab.subplot(gs[0,1])
        plt(var_gr_l23,var_ni_l23)
        disable_left_axis(ax)
        remove_y_tick_labels()
        pylab.title("Layer 2/3",fontsize=19,y=1.05)

        ax = pylab.subplot(gs[0,2])
        plt(var_gr_pooled,var_ni_pooled)
        disable_left_axis(ax)
        remove_y_tick_labels()
        pylab.title("Pooled",fontsize=19,y=1.05)

        ax = pylab.subplot(gs[0,3])
        plt(self.parameters.data_dg,self.parameters.data_ni)
        disable_left_axis(ax)
        remove_y_tick_labels()
        pylab.title("Data",fontsize=19,y=1.05)

        pylab.rc('axes', linewidth=lw)

        if self.plot_file_name:
                        pylab.savefig(Global.root_directory+self.plot_file_name)

class StimulusResponseComparison(Plotting):
    required_parameters = ParameterSet({
        'sheet_name': str,  # the name of the sheet for which to plot
        'neuron': int,  # which neuron to show
    })

    def subplot(self, subplotspec):
        plots = {}
        gs = gridspec.GridSpecFromSubplotSpec(1, 21, subplot_spec=subplotspec,
                                              hspace=1.0, wspace=1.0)

        orr = list(set([MozaikParametrized.idd(s).orientation for s in queries.param_filter_query(self.datastore,st_name='FullfieldDriftingSinusoidalGrating',st_contrast=ttcc_contrast).get_stimuli()]))
        #ors = self.datastore.get_analysis_result(identifier='PerNeuronValue',value_name = 'LGNAfferentOrientation', sheet_name = self.parameters.sheet_name)

        #dsv = queries.param_filter_query(self.datastore,st_name='FullfieldDriftingSinusoidalGrating',st_orientation=orr[numpy.argmin([circular_dist(o,ors[0].get_value_by_id(self.parameters.neuron),numpy.pi)  for o in orr])],st_contrast=100)
        dsv = queries.param_filter_query(self.datastore,st_name='FullfieldDriftingSinusoidalGrating',st_orientation=0,st_contrast=ttcc_contrast)
        plots['Gratings'] = (OverviewPlot(dsv, ParameterSet({'sheet_name': self.parameters.sheet_name,'neuron': self.parameters.neuron,'spontaneous' : True, 'sheet_activity' : {}})),gs[:,11:],{'y_label': None})
        #dsv = queries.param_filter_query(self.datastore,st_name='DriftingGratingWithEyeMovement')
        #plots['GratingsWithEM'] = (OverviewPlot(dsv, ParameterSet({'sheet_name': self.parameters.sheet_name,'neuron': self.parameters.neuron, 'spontaneous' : True,'sheet_activity' : {}})),gs[2:4,:],{'x_label': None})
        dsv = queries.param_filter_query(self.datastore,st_name='NaturalImageWithEyeMovement')
        plots['NIwEM'] = (OverviewPlot(dsv, ParameterSet({'sheet_name': self.parameters.sheet_name,'neuron': self.parameters.neuron,'spontaneous' : True, 'sheet_activity' : {}})),gs[:,:10],{})

        return plots

class OrientationMapMatching(Plotting):
    required_parameters = ParameterSet({
    })

    def subplot(self, subplotspec):
        plots = {}
        fontsize = 10
        gs = gridspec.GridSpecFromSubplotSpec(2, 2, subplot_spec=subplotspec,hspace=0.1, wspace=0.1)

        ads = param_filter_query(self.datastore,sheet_name='V1_Exc_L4', value_name='orientation preference of Firing rate').get_analysis_result()[0]
        l4_ids = ads.ids
        real_orl4 = ads.values
        ads = param_filter_query(self.datastore,sheet_name='V1_Exc_L2/3', value_name='orientation preference of Firing rate').get_analysis_result()[0]
        l23_ids = ads.ids
        real_orl23 = ads.values

        dsv = param_filter_query(self.datastore,sheet_name='V1_Exc_L4', value_name='LGNAfferentOrientation')
        pos = dsv.get_neuron_positions()['V1_Exc_L4']
        pnv = dsv.get_analysis_result()[0]
        posx = pos[0,self.datastore.get_sheet_indexes('V1_Exc_L4',pnv.ids)]
        posy = pos[1,self.datastore.get_sheet_indexes('V1_Exc_L4',pnv.ids)]
        plots['OrMapL4'] = (ScatterPlot(posx, posy, pnv.values, periodic=True,period=pnv.period),gs[0,0],{'dot_size':5,'x_label': None,'y_label': None,'x_ticks': [],'y_ticks': [], 'title':'Layer 4', 'fontsize':fontsize})
        or_mapl4 = dsv.get_analysis_result()[0].get_value_by_id(l4_ids)

        dsv = param_filter_query(self.datastore,sheet_name='V1_Exc_L2/3', value_name='LGNAfferentOrientation')
        pos = dsv.get_neuron_positions()['V1_Exc_L2/3']
        pnv = dsv.get_analysis_result()[0]
        posx = pos[0,self.datastore.get_sheet_indexes('V1_Exc_L2/3',pnv.ids)]
        posy = pos[1,self.datastore.get_sheet_indexes('V1_Exc_L2/3',pnv.ids)]
        plots['OrMapL2/3'] = (ScatterPlot(posx, posy, pnv.values, periodic=True,period=pnv.period),gs[0,1],{'dot_size':5,'x_label': None,'y_label': None,'x_ticks': [],'y_ticks': [], 'title':'Layer 2/3', 'fontsize':fontsize})
        or_mapl23 = dsv.get_analysis_result()[0].get_value_by_id(l23_ids)

        axis = pylab.subplot(gs[1,0])
        pylab.scatter(real_orl4,or_mapl4, s=1, c='black')
        pylab.plot([0,numpy.pi],[0,numpy.pi], c='black')
        pylab.xlim(0,numpy.pi)
        pylab.ylim(0,numpy.pi)
        pylab.xticks([0,numpy.pi], labels = ['0','π'])
        pylab.yticks([0,numpy.pi], labels = ['0','π'])
        pylab.xlabel('measured orientation pref. (rad)')
        pylab.ylabel('set orientation pref. (rad)')

        axis = pylab.subplot(gs[1,1])
        pylab.scatter(real_orl23,or_mapl23, s=1,  c='black')
        pylab.plot([0,numpy.pi],[0,numpy.pi], c='black')
        pylab.xlim(0,numpy.pi)
        pylab.ylim(0,numpy.pi)
        pylab.xticks([0,numpy.pi], labels = ['0','π'])
        pylab.yticks([0,numpy.pi], labels = ['0','π'])
        pylab.xlabel('measured orientation pref. (rad)')

        return plots

