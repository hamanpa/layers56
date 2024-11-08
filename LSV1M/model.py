import sys
from parameters import ParameterSet
from mozaik.models import Model
from mozaik.connectors.meta_connectors import GaborConnector
from mozaik.connectors.modular import ModularSamplingProbabilisticConnector, ModularSamplingProbabilisticConnectorAnnotationSamplesCount
from mozaik import load_component
from mozaik.space import VisualRegion


class SelfSustainedPushPull(Model):
    """"""

    required_parameters = ParameterSet({
        'sheets': ParameterSet({
            'l4_cortex_exc': ParameterSet,
            'l4_cortex_inh': ParameterSet,
            'l23_cortex_exc': ParameterSet,
            'l23_cortex_inh': ParameterSet,
            'l5_cortex_exa': ParameterSet,
            'l5_cortex_exb': ParameterSet,
            'l5_cortex_inh': ParameterSet,
            'l6_cortex_exa': ParameterSet,
            'l6_cortex_exb': ParameterSet,
            'l6_cortex_inh': ParameterSet,
            'retina_lgn': ParameterSet}),
        'visual_field': ParameterSet,
        'density_frac' : float,
        'l5_density_ratio' : float,
        'l5_conn_ratio' : float,
        'l5a_density' : float,
        'only_afferent': bool,
        'l23': bool,
        'l5': bool,
        'l6': bool,
        'feedback_l5' :  bool,
        'feedback_l6a' :  bool,  # cells sending to L4 (feedback to L5, L4) 
        'feedback_l6b' :  bool,  # cells sending to L5/6 (horizontal feedback to L5)

        'trial': int,
    })

    def __init__(self, sim, num_threads, parameters):
        Model.__init__(self, sim, num_threads, parameters)
        # Load components
        CortexExcL4 = load_component(
            self.parameters.sheets.l4_cortex_exc.component)
        CortexInhL4 = load_component(
            self.parameters.sheets.l4_cortex_inh.component)
        CortexExaL6 = load_component(
            self.parameters.sheets.l6_cortex_exa.component)
        CortexInhL6 = load_component(
            self.parameters.sheets.l6_cortex_inh.component)
        if not self.parameters.only_afferent:
            if self.parameters.l23:
                CortexExcL23 = load_component(
                    self.parameters.sheets.l23_cortex_exc.component)
                CortexInhL23 = load_component(
                    self.parameters.sheets.l23_cortex_inh.component)
            if self.parameters.l5:
                CortexExaL5 = load_component(
                    self.parameters.sheets.l5_cortex_exa.component)
                CortexExbL5 = load_component(
                    self.parameters.sheets.l5_cortex_exb.component)
                CortexInhL5 = load_component(
                    self.parameters.sheets.l5_cortex_inh.component)
            if self.parameters.l6:
                CortexExbL6 = load_component(
                    self.parameters.sheets.l6_cortex_exb.component)

        RetinaLGN = load_component(self.parameters.sheets.retina_lgn.component)

        # Build and instrument the network
        self.visual_field = VisualRegion(location_x=self.parameters.visual_field.centre[0], 
                                         location_y=self.parameters.visual_field.centre[1], 
                                         size_x=self.parameters.visual_field.size[0], 
                                         size_y=self.parameters.visual_field.size[1])
        self.input_layer = RetinaLGN(
            self, self.parameters.sheets.retina_lgn.params)
        cortex_exc_l4 = CortexExcL4(
            self, self.parameters.sheets.l4_cortex_exc.params)
        cortex_inh_l4 = CortexInhL4(
            self, self.parameters.sheets.l4_cortex_inh.params)

        # same as layer 4, recipient of connections from LGN
        if self.parameters.l6:
            cortex_exa_l6 = CortexExaL6(
                self, self.parameters.sheets.l6_cortex_exa.params)
            cortex_inh_l6 = CortexInhL6(
                self, self.parameters.sheets.l6_cortex_inh.params)

        if not self.parameters.only_afferent:
            if self.parameters.l23:
                cortex_exc_l23 = CortexExcL23(
                    self, self.parameters.sheets.l23_cortex_exc.params)
                cortex_inh_l23 = CortexInhL23(
                    self, self.parameters.sheets.l23_cortex_inh.params)
            if self.parameters.l5:
                cortex_exa_l5 = CortexExaL5(
                    self, self.parameters.sheets.l5_cortex_exa.params)
                cortex_exb_l5 = CortexExbL5(
                    self, self.parameters.sheets.l5_cortex_exb.params)
                cortex_inh_l5 = CortexInhL5(
                    self, self.parameters.sheets.l5_cortex_inh.params)
            if self.parameters.l6:
                cortex_exb_l6 = CortexExbL6(
                    self, self.parameters.sheets.l6_cortex_exb.params)

        # initialize afferent layer 4 projections
        GaborConnector(self, 
                       self.input_layer.sheets['X_ON'], 
                       self.input_layer.sheets['X_OFF'],
                       cortex_exc_l4, 
                       self.parameters.sheets.l4_cortex_exc.AfferentConnection, 
                       'V1AffL4ExcConnection')
        GaborConnector(self, 
                       self.input_layer.sheets['X_ON'], 
                       self.input_layer.sheets['X_OFF'],
                       cortex_inh_l4, 
                       self.parameters.sheets.l4_cortex_inh.AfferentConnection, 
                       'V1AffL4InhConnection')

        if self.parameters.l6:
            # initialize afferent layer 6 projections
            GaborConnector(self, 
                        self.input_layer.sheets['X_ON'], 
                        self.input_layer.sheets['X_OFF'],
                        cortex_exa_l6,
                        self.parameters.sheets.l6_cortex_exa.AfferentConnection, 
                        'V1AffL6ExaConnection')
            GaborConnector(self, 
                        self.input_layer.sheets['X_ON'], 
                        self.input_layer.sheets['X_OFF'],
                        cortex_inh_l6, 
                        self.parameters.sheets.l6_cortex_inh.AfferentConnection, 
                        'V1AffL6InhConnection')

        # initialize lateral layer 4 projections


        if not self.parameters.only_afferent:

            ModularSamplingProbabilisticConnectorAnnotationSamplesCount(
                self, 
                'V1L4ExcL4ExcConnection', 
                cortex_exc_l4, 
                cortex_exc_l4, 
                self.parameters.sheets.l4_cortex_exc.L4ExcL4ExcConnection
                ).connect()

            ModularSamplingProbabilisticConnectorAnnotationSamplesCount(
                self, 
                'V1L4ExcL4InhConnection', 
                cortex_exc_l4, 
                cortex_inh_l4, 
                self.parameters.sheets.l4_cortex_exc.L4ExcL4InhConnection
                ).connect()

            ModularSamplingProbabilisticConnector(
                self, 
                'V1L4InhL4ExcConnection', 
                cortex_inh_l4,
                cortex_exc_l4, 
                self.parameters.sheets.l4_cortex_inh.L4InhL4ExcConnection
                ).connect()
            
            ModularSamplingProbabilisticConnector(
                self, 
                'V1L4InhL4InhConnection', 
                cortex_inh_l4,
                cortex_inh_l4, 
                self.parameters.sheets.l4_cortex_inh.L4InhL4InhConnection
                ).connect()

            if self.parameters.l23:

                # initialize layer 4 to layer 2/3 projection
                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L4ExcL23ExcConnection', 
                    cortex_exc_l4,
                    cortex_exc_l23, 
                    self.parameters.sheets.l4_cortex_exc.L4ExcL23ExcConnection
                ).connect()
                
                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L4ExcL23InhConnection', 
                    cortex_exc_l4,
                    cortex_inh_l23, 
                    self.parameters.sheets.l4_cortex_exc.L4ExcL23InhConnection
                ).connect()
                
                # initialize lateral projections in layer 2/3

                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L23ExcL23ExcConnection', 
                    cortex_exc_l23,
                    cortex_exc_l23, 
                    self.parameters.sheets.l23_cortex_exc.L23ExcL23ExcConnection
                ).connect()

                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L23ExcL23InhConnection', 
                    cortex_exc_l23,
                    cortex_inh_l23, 
                    self.parameters.sheets.l23_cortex_exc.L23ExcL23InhConnection
                ).connect()

                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L23InhL23ExcConnection', 
                    cortex_inh_l23,
                    cortex_exc_l23, 
                    self.parameters.sheets.l23_cortex_inh.L23InhL23ExcConnection
                ).connect()

                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L23InhL23InhConnection', 
                    cortex_inh_l23,
                    cortex_inh_l23, 
                    self.parameters.sheets.l23_cortex_inh.L23InhL23InhConnection
                ).connect()

            if self.parameters.l5:

                # initialize lateral projections in layer 5

                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L5ExaL5ExaConnection', 
                    cortex_exa_l5,
                    cortex_exa_l5,
                    self.parameters.sheets.l5_cortex_exa.L5ExaL5ExaConnection
                ).connect()
                
                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L5ExaL5ExbConnection', 
                    cortex_exa_l5,
                    cortex_exb_l5,
                    self.parameters.sheets.l5_cortex_exa.L5ExaL5ExbConnection
                ).connect()

                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L5ExaL5InhConnection', 
                    cortex_exa_l5,
                    cortex_inh_l5,
                    self.parameters.sheets.l5_cortex_exa.L5ExaL5InhConnection
                ).connect()

                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L5ExbL5ExaConnection', 
                    cortex_exb_l5,
                    cortex_exa_l5,
                    self.parameters.sheets.l5_cortex_exb.L5ExbL5ExaConnection
                ).connect()
                
                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L5ExbL5ExbConnection', 
                    cortex_exb_l5,
                    cortex_exb_l5,
                    self.parameters.sheets.l5_cortex_exb.L5ExbL5ExbConnection
                ).connect()

                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L5ExbL5InhConnection', 
                    cortex_exb_l5,
                    cortex_inh_l5,
                    self.parameters.sheets.l5_cortex_exb.L5ExbL5InhConnection
                ).connect()

                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L5InhL5ExaConnection', 
                    cortex_inh_l5,
                    cortex_exa_l5,
                    self.parameters.sheets.l5_cortex_inh.L5InhL5ExaConnection
                ).connect()
                
                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L5InhL5ExbConnection', 
                    cortex_inh_l5,
                    cortex_exb_l5,
                    self.parameters.sheets.l5_cortex_inh.L5InhL5ExbConnection
                ).connect()

                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L5InhL5InhConnection', 
                    cortex_inh_l5,
                    cortex_inh_l5,
                    self.parameters.sheets.l5_cortex_inh.L5InhL5InhConnection
                ).connect()


                if self.parameters.l23:
                    # initialize layer 2/3 to layer 5 projection
                    ModularSamplingProbabilisticConnector(
                        self, 
                        'V1L23ExcL5ExaConnection', 
                        cortex_exc_l23, 
                        cortex_exa_l5,
                        self.parameters.sheets.l23_cortex_exc.L23ExcL5ExaConnection
                    ).connect()
                    
                    ModularSamplingProbabilisticConnector(
                        self, 
                        'V1L23ExcL5ExbConnection', 
                        cortex_exc_l23, 
                        cortex_exb_l5,
                        self.parameters.sheets.l23_cortex_exc.L23ExcL5ExbConnection
                    ).connect()
                    
                    ModularSamplingProbabilisticConnector(
                        self, 
                        'V1L23ExcL5InhConnection', 
                        cortex_exc_l23,
                        cortex_inh_l5, 
                        self.parameters.sheets.l23_cortex_exc.L23ExcL5InhConnection
                    ).connect()

            if self.parameters.l6:
                # initialize lateral projections in layer 6

                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L6ExaL6ExaConnection', 
                    cortex_exa_l6,
                    cortex_exa_l6,
                    self.parameters.sheets.l6_cortex_exa.L6ExaL6ExaConnection
                ).connect()
                
                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L6ExaL6ExbConnection', 
                    cortex_exa_l6,
                    cortex_exb_l6,
                    self.parameters.sheets.l6_cortex_exa.L6ExaL6ExbConnection
                ).connect()

                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L6ExaL6InhConnection', 
                    cortex_exa_l6,
                    cortex_inh_l6,
                    self.parameters.sheets.l6_cortex_exa.L6ExaL6InhConnection
                ).connect()

                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L6ExbL6ExaConnection', 
                    cortex_exb_l6,
                    cortex_exa_l6,
                    self.parameters.sheets.l6_cortex_exb.L6ExbL6ExaConnection
                ).connect()
                
                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L6ExbL6ExbConnection', 
                    cortex_exb_l6,
                    cortex_exb_l6,
                    self.parameters.sheets.l6_cortex_exb.L6ExbL6ExbConnection
                ).connect()

                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L6ExbL6InhConnection', 
                    cortex_exb_l6,
                    cortex_inh_l6,
                    self.parameters.sheets.l6_cortex_exb.L6ExbL6InhConnection
                ).connect()

                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L6InhL6ExaConnection', 
                    cortex_inh_l6,
                    cortex_exa_l6,
                    self.parameters.sheets.l6_cortex_inh.L6InhL6ExaConnection
                ).connect()
                
                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L6InhL6ExbConnection', 
                    cortex_inh_l6,
                    cortex_exb_l6,
                    self.parameters.sheets.l6_cortex_inh.L6InhL6ExbConnection
                ).connect()

                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L6InhL6InhConnection', 
                    cortex_inh_l6,
                    cortex_inh_l6,
                    self.parameters.sheets.l6_cortex_inh.L6InhL6InhConnection
                ).connect()

                if self.parameters.l5:
                    # initialize layer 5 to layer 6 projection
                    ModularSamplingProbabilisticConnector(
                        self, 
                        'V1L5ExbL6ExaConnection', 
                        cortex_exb_l5,
                        cortex_exa_l6,
                        self.parameters.sheets.l5_cortex_exb.L5ExbL6ExaConnection
                    ).connect()
                    
                    ModularSamplingProbabilisticConnector(
                        self, 
                        'V1L5ExbL6ExbConnection', 
                        cortex_exb_l5,
                        cortex_exb_l6,
                        self.parameters.sheets.l5_cortex_exb.L5ExbL6ExbConnection
                    ).connect()

                    ModularSamplingProbabilisticConnector(
                        self, 
                        'V1L5ExbL6InhConnection', 
                        cortex_exb_l5,
                        cortex_inh_l6,
                        self.parameters.sheets.l5_cortex_exb.L5ExbL6InhConnection
                    ).connect()

            if (self.parameters.l23 and self.parameters.l5 
                and self.parameters.feedback_l5):
                
                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L5ExaL23ExcConnection', 
                    cortex_exa_l5,
                    cortex_exc_l23, 
                    self.parameters.sheets.l5_cortex_exa.L5ExaL23ExcConnection
                ).connect()

                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L5ExaL23InhConnection', 
                    cortex_exa_l5,
                    cortex_inh_l23, 
                    self.parameters.sheets.l5_cortex_exa.L5ExaL23InhConnection
                ).connect()

            if (self.parameters.l5 and self.parameters.l6 
                and self.parameters.feedback_l6b):

                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L6ExbL5ExaConnection', 
                    cortex_exa_l6,
                    cortex_exa_l5, 
                    self.parameters.sheets.l6_cortex_exb.L6ExbL5ExaConnection
                ).connect()

                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L6ExbL5ExbConnection', 
                    cortex_exa_l6,
                    cortex_exb_l5, 
                    self.parameters.sheets.l6_cortex_exb.L6ExbL5ExbConnection
                ).connect()

                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L6ExbL5InhConnection', 
                    cortex_exa_l6,
                    cortex_inh_l5, 
                    self.parameters.sheets.l6_cortex_exb.L6ExbL5InhConnection
                ).connect()


            if (self.parameters.l5 and self.parameters.l6 
                and self.parameters.feedback_l6a):

                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L6ExaL4ExcConnection', 
                    cortex_exa_l6,
                    cortex_exc_l4, 
                    self.parameters.sheets.l6_cortex_exa.L6ExaL4ExcConnection
                ).connect()

                ModularSamplingProbabilisticConnector(
                    self, 
                    'V1L6ExaL4InhConnection', 
                    cortex_exa_l6,
                    cortex_inh_l4, 
                    self.parameters.sheets.l6_cortex_exa.L6ExaL4InhConnection
                ).connect()



