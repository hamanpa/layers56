Directory related to the project of adding deep layers into LSV1M model

Models
- **LSV1M_remy**: The default V1 model that was published
- **LSV1M_refs-update**: Update of `LSV1M_remy` model, where more parameters are referenced, should give the same results as `LSV1M_remy` model 
    - Comparison of the models ... 
- **LSV1M_tsodyks2**: This model was supposed to test different type of synapse
    - To run this model one has to make changes in mozaik!
    `mozaik.connectors.Connector` class has predefined `static_synapse` or `tsodyks_synapse` (for details check NEST documentation)
    - Reason for this model: It turned out PyNN has unexpected behavior with `tsodyks_synapse`
- **LSV1M_optimization**: 
- **LSV1M_split_ee**: Model suggested by Tanguy, the long-range connections of L23 are split into two short and long connections are optimized separately
    - model for optimization
- **LSV1M_split_full**
- **LSV1M_infragranular**
- Details on file structure of models is at the end of this file

optimization
- Folder based on Tanguys optimization approach
- `optimisation.sbatch`
- `run_optimisation.py`
- `evaluator.py`
- `targets.py`: defines Target classes to evaluate results
- `utils.py`

scripts
- 

ntbs
- Folder collecting relevant jupyter notebooks
-




# Mozaik updates
For this project I did few changes in mozaik
- Explosion monitoring
- length of the folder

possible to add
- tsodyks2_synapse (based on specification of `tau_psc`)
- connectivity


# How to run stuff

### single experiment (ParameterSearch)

1. change directory to the model of choice
2. Update `run_parameter_search.py` file with parameters of interest
3. run one of the following commands

**Drifting grating** and natural images protocol (~10h of runtime with our setup)
    `python run_parameter_search.py run.py nest param/defaults` 
**Size tuning** protocol (~10h of runtime with our setup)
    `python run_parameter_search.py run_stc.py nest param/defaults` 
**Spontaneous** activity protocol (~1h30 of runtime with our setup)
    `python run_parameter_search.py run_spont.py nest param_spont/defaults`
**optimization** experiments protocol (~1h30 of runtime with our setup)
    `python run_parameter_search.py run_optimization_experiment.py nest param_optim/defaults`

### Optimization

In the *model* folder
1. create `param_optim` folder with parameters
2. make `config_optimisation` file in there
    - should contain keys [`parameters`, `optimiser_centroid`, `targets`]
3. make `run_optimization_experiment.py` protocol file

In the *optimization* folder
1. edit `run_optimisation.py` file
    - model
    - continue_cp (optional, if we want to continue from previous point)
2. ensure `evaluator` has correct slurm options
    - in `define_evaluator` function
3. run `sbatch optimisation.sbatch`

Notes:
    optimization log is in *optimization* folder
    optimization result folder is in *model* folder
    after running optimization remove slurm logs

# Inspecting results

### Arkheia

### online mozaik

# Other stuff

### Table with model parameters

### Table with information about V1 cortex



# Issues





---

1.2 Description of the files:

    - analysis_and_visualization.py: Contains the code for the different analysis and plotting. The function `perform_analysis_and_visualization` runs the analysis and the plots corresponding to the fullfield drifting grating and natural images protocol. The functions `perform_analysis_and_visualization_stc` and `perform_analysis_and_visualization_spont` do the same respectively for the size tuning and spontaneous activity protocol.
    - experiments.py: Defines for each protocol which experiments will be run as well as their parameters. `create_experiments` corresponds to the fullfield drifting grating protocol, `create_experiments_stc` corresponds to the size tuning protocol, and `create_experiments_spont` corresponds to the spontaneous activity protocol.
    - eye_path.pickle: Contains the coordinates of the eye path that is used by default in the natural image protocol. 
    - image_naturelle_HIGHC.bmp: The natural image that is used by default in the natural image protocol.
    - model.py: Contains the code which creates each layers of the model and build the connections based on the parameters used to run the model.
    - or_map_new_16x16: Contains the precomputed orientation map. A specific central portion of it can be cropped based on the or_map_stretch parameters.
    - param: Defines the parameters used in the fullfield drifting gratings and natural images protocol as well as for the size tuning protocol. The 'default' file contains the basic parameters of the model as well as the path of the parameters corresponding to each sheets of the model. 'SpatioTemporalFilterRetinaLGN_defaults' contains the parameters of the input model as well as the parameters of the LGN neurons. `l4_cortex_exc', `l4_cortex_inh`, `l23_cortex_exc`, `l23_cortex_inh` contains the parameters of each cortical population as well as the parameters of the connections of the model. Each '_rec' file contains the recording parameters for each population of the model.
    - param_spont: Contains the parameters for the spontaneous activity protocol of the model. The only difference with the `param` directory resides in the recording parameters.
    - parameter_search_analysis.py: Runs the analysis one multiple simulation directories belonging to the same parameter search, distributed on multiple computational nodes and using by default Slurm for scheduling.
    - run.py: Runs the model. Defines which experimental protocol (as defined in experiments.py) and which analysis (as defined in analysis_and_visualization.py) will be run. By default runs the fullfield drifting grating and natural images protocol.
    - run_analysis.py: Runs only the analysis on the model on a mozaik datastore. Defines which analysis  (as defined in analysis_and_visualization.py) will be run. By default runs the fullfield drifting grating and natural images protocol analysis.
    - run_parameter_search.py: Defines the parameters that will be used when running a search across multiple parameters. The parameter search will be distributed on different computational nodes, using Slurm as the scheduler by default. 
    - run_spont.py: Same as `run.py`, but runs the spontaneous activity protocol by default. 
    - run_stc.py: Same as `run.py`, but runs the size tuning protocol by default. 
    - visualization_functions.py: Contains the code specific to each figure. 
