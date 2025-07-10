from pathlib import Path
import os
import json

from mozaik.tools.distribution_parametrization import load_parameters

PROJECT_ROOT = Path('/home/haman/layers56/')

# predefined recorders
RECS = {
    "l4_exc_rec": {
        "2" : {
            'component' :  'mozaik.sheets.population_selector.RCGrid',
            'variables' : ("spikes","v","gsyn_exc" , "gsyn_inh"),
            'params' :  {
                'size': 200.0,  # the size of the grid (it is assumed to be square) - it has to be multiple of spacing (micro meters)
                'spacing' : 10.0, #the space between two electrodes (micro meters)
                'offset_x' : 0.0, # the x axis offset from the center of the sheet (micro meters)
                'offset_y' : 0.0, # the y axis offset from the center of the sheet (micro meters)
            }
        },
        "3" : {
            'component' :  'mozaik.sheets.population_selector.RCGrid',
            'variables' : ("spikes"),
            'params' :  {
                'size': 600.0,  # the size of the grid (it is assumed to be square) - it has to be multiple of spacing (micro meters)
                'spacing' : 20.0, #the space between two electrodes (micro meters)
                'offset_x' : 0.0, # the x axis offset from the center of the sheet (micro meters)
                'offset_y' : 0.0, # the y axis offset from the center of the sheet (micro meters)
            }
        },
        "4" : {
            'component' :  'mozaik.sheets.population_selector.RCGrid',
            'variables' : ("spikes"),
            'params' :  {
                'size': 2000.0,  # the size of the grid (it is assumed to be square) - it has to be multiple of spacing (micro meters)
                'spacing' : 100.0, #the space between two electrodes (micro meters)
                'offset_x' : 0.0, # the x axis offset from the center of the sheet (micro meters)
                'offset_y' : 0.0, # the y axis offset from the center of the sheet (micro meters)
            }
        },
    },
    "l4_inh_rec": {
        "2" : {
            'component' :  'mozaik.sheets.population_selector.RCGrid',
            'variables' : ("spikes","v","gsyn_exc" , "gsyn_inh"),
            'params' :  {
                'size': 200.0,  # the size of the grid (it is assumed to be square) - it has to be multiple of spacing (micro meters)
                'spacing' : 20.0, #the space between two electrodes (micro meters)
                'offset_x' : 0.0, # the x axis offset from the center of the sheet (micro meters)
                'offset_y' : 0.0, # the y axis offset from the center of the sheet (micro meters)
            }
        },
        "3" : {
            'component' :  'mozaik.sheets.population_selector.RCGrid',
            'variables' : ("spikes"),
            'params' :  {
                'size': 600.0,  # the size of the grid (it is assumed to be square) - it has to be multiple of spacing (micro meters)
                'spacing' : 20.0, #the space between two electrodes (micro meters)
                'offset_x' : 0.0, # the x axis offset from the center of the sheet (micro meters)
                'offset_y' : 0.0, # the y axis offset from the center of the sheet (micro meters)
            }
        },
    },
    "l23_exc_rec": {
        "2" : {
            'component' :  'mozaik.sheets.population_selector.RCGrid',
            'variables' : ("spikes","v","gsyn_exc" , "gsyn_inh"),
            'params' :  {
                'size': 200.0,  # the size of the grid (it is assumed to be square) - it has to be multiple of spacing (micro meters)
                'spacing' : 10.0, #the space between two electrodes (micro meters)
                'offset_x' : 0.0, # the x axis offset from the center of the sheet (micro meters)
                'offset_y' : 0.0, # the y axis offset from the center of the sheet (micro meters)
            }
        },
        "3" : {
            'component' :  'mozaik.sheets.population_selector.RCGrid',
            'variables' : ("spikes"),
            'params' :  {
                'size': 600.0,  # the size of the grid (it is assumed to be square) - it has to be multiple of spacing (micro meters)
                'spacing' : 20.0, #the space between two electrodes (micro meters)
                'offset_x' : 0.0, # the x axis offset from the center of the sheet (micro meters)
                'offset_y' : 0.0, # the y axis offset from the center of the sheet (micro meters)
            }
        },
        "4" : {
            'component' :  'mozaik.sheets.population_selector.RCGrid',
            'variables' : ("spikes"),
            'params' :  {
                'size': 2000.0,  # the size of the grid (it is assumed to be square) - it has to be multiple of spacing (micro meters)
                'spacing' : 100.0, #the space between two electrodes (micro meters)
                'offset_x' : 0.0, # the x axis offset from the center of the sheet (micro meters)
                'offset_y' : 0.0, # the y axis offset from the center of the sheet (micro meters)
            }
        },
    },
    "l23_inh_rec": {
        "2" : {
            'component' :  'mozaik.sheets.population_selector.RCGrid',
            'variables' : ("spikes","v","gsyn_exc" , "gsyn_inh"),
            'params' :  {
                'size': 200.0,  # the size of the grid (it is assumed to be square) - it has to be multiple of spacing (micro meters)
                'spacing' : 20.0, #the space between two electrodes (micro meters)
                'offset_x' : 0.0, # the x axis offset from the center of the sheet (micro meters)
                'offset_y' : 0.0, # the y axis offset from the center of the sheet (micro meters)
            }
        },
        "3" : {
            'component' :  'mozaik.sheets.population_selector.RCGrid',
            'variables' : ("spikes"),
            'params' :  {
                'size': 600.0,  # the size of the grid (it is assumed to be square) - it has to be multiple of spacing (micro meters)
                'spacing' : 20.0, #the space between two electrodes (micro meters)
                'offset_x' : 0.0, # the x axis offset from the center of the sheet (micro meters)
                'offset_y' : 0.0, # the y axis offset from the center of the sheet (micro meters)
            }
        },
    },
    "lgn_rec": {
        "1" : {
            'component' :  'mozaik.sheets.population_selector.RCRandomN',
            'variables' : ("spikes","V_m","g_ex" , "g_in"),
            'params' :  {
                'num_of_cells' : 5,
            }
        },
    }
}

RECS_SPONT = {
    "l4_exc_rec": {
        "2" : {
            'component' :  'mozaik.sheets.population_selector.RCGrid',
            'variables' : ("v","gsyn_exc" , "gsyn_inh"),
            'params' :  {
                'size': 2000.0,  # the size of the grid (it is assumed to be square) - it has to be multiple of spacing (micro meters)
                'spacing' : 100.0, #the space between two electrodes (micro meters)
                'offset_x' : 0.0, # the x axis offset from the center of the sheet (micro meters)
                'offset_y' : 0.0, # the y axis offset from the center of the sheet (micro meters)
            }
        },
        "4" : {
            'component' :  'mozaik.sheets.population_selector.RCGrid',
            'variables' : ("spikes"),
            'params' :  {
                'size': 3000.0,  # the size of the grid (it is assumed to be square) - it has to be multiple of spacing (micro meters)
                'spacing' : 20.0, #the space between two electrodes (micro meters)
                'offset_x' : 0.0, # the x axis offset from the center of the sheet (micro meters)
                'offset_y' : 0.0, # the y axis offset from the center of the sheet (micro meters)
            }
        },
    },
    "l4_inh_rec": {
        "2" : {
            'component' :  'mozaik.sheets.population_selector.RCGrid',
            'variables' : ("v","gsyn_exc" , "gsyn_inh"),
            'params' :  {
                'size': 2000.0,  # the size of the grid (it is assumed to be square) - it has to be multiple of spacing (micro meters)
                'spacing' : 100.0, #the space between two electrodes (micro meters)
                'offset_x' : 0.0, # the x axis offset from the center of the sheet (micro meters)
                'offset_y' : 0.0, # the y axis offset from the center of the sheet (micro meters)
            }
        },
        "4" : {
            'component' :  'mozaik.sheets.population_selector.RCGrid',
            'variables' : ("spikes"),
            'params' :  {
                'size': 3000.0,  # the size of the grid (it is assumed to be square) - it has to be multiple of spacing (micro meters)
                'spacing' : 20.0, #the space between two electrodes (micro meters)
                'offset_x' : 0.0, # the x axis offset from the center of the sheet (micro meters)
                'offset_y' : 0.0, # the y axis offset from the center of the sheet (micro meters)
            }
        },
    },
    "l23_exc_rec": {
        "2" : {
            'component' :  'mozaik.sheets.population_selector.RCGrid',
            'variables' : ("v","gsyn_exc" , "gsyn_inh"),
            'params' :  {
                'size': 2000.0,  # the size of the grid (it is assumed to be square) - it has to be multiple of spacing (micro meters)
                'spacing' : 100.0, #the space between two electrodes (micro meters)
                'offset_x' : 0.0, # the x axis offset from the center of the sheet (micro meters)
                'offset_y' : 0.0, # the y axis offset from the center of the sheet (micro meters)
            }
        },
        "4" : {
            'component' :  'mozaik.sheets.population_selector.RCGrid',
            'variables' : ("spikes"),
            'params' :  {
                'size': 3000.0,  # the size of the grid (it is assumed to be square) - it has to be multiple of spacing (micro meters)
                'spacing' : 20.0, #the space between two electrodes (micro meters)
                'offset_x' : 0.0, # the x axis offset from the center of the sheet (micro meters)
                'offset_y' : 0.0, # the y axis offset from the center of the sheet (micro meters)
            }
        },
    },
    "l23_inh_rec": {
        "2" : {
            'component' :  'mozaik.sheets.population_selector.RCGrid',
            'variables' : ("v","gsyn_exc" , "gsyn_inh"),
            'params' :  {
                'size': 2000.0,  # the size of the grid (it is assumed to be square) - it has to be multiple of spacing (micro meters)
                'spacing' : 100.0, #the space between two electrodes (micro meters)
                'offset_x' : 0.0, # the x axis offset from the center of the sheet (micro meters)
                'offset_y' : 0.0, # the y axis offset from the center of the sheet (micro meters)
            }
        },
        "4" : {
            'component' :  'mozaik.sheets.population_selector.RCGrid',
            'variables' : ("spikes"),
            'params' :  {
                'size': 3000.0,  # the size of the grid (it is assumed to be square) - it has to be multiple of spacing (micro meters)
                'spacing' : 20.0, #the space between two electrodes (micro meters)
                'offset_x' : 0.0, # the x axis offset from the center of the sheet (micro meters)
                'offset_y' : 0.0, # the y axis offset from the center of the sheet (micro meters)
            }
        },
    },
    "lgn_rec": {
        "1" : {
            'component' :  'mozaik.sheets.population_selector.RCRandomN',
            'variables' : ("spikes","V_m","g_ex" , "g_in"),
            'params' :  {
                'num_of_cells' : 5,
            }
        },
    }
}

RECS_OPTIM = {
    "l4_exc_rec": {
        "1" : {
            'component':  'mozaik.sheets.population_selector.RCAll',
            'variables': ("spikes"),
            'params': {
            }
        }
    },
    "l4_inh_rec": {
        "1" : {
            'component':  'mozaik.sheets.population_selector.RCAll',
            'variables': ("spikes"),
            'params': {
            }
        }
    },
    "l23_exc_rec": {
        "1" : {
            'component':  'mozaik.sheets.population_selector.RCAll',
            'variables': ("spikes"),
            'params': {
            }
        }
    },
    "l23_inh_rec": {
        "1" : {
            'component':  'mozaik.sheets.population_selector.RCAll',
            'variables': ("spikes"),
            'params': {
            }
        }
    },
    "lgn_rec": {
        "1" : {
            'component' :  'mozaik.sheets.population_selector.RCRandomN',
            'variables' : ("spikes"),
            'params' :  {
                'num_of_cells' : 5,
            }
        }
    }
}

def flatten_dict(d, parent_key='', sep='.'):
    """
    Flatten a nested dictionary.
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def unflatten_dict(d, sep='.'):
    """
    Unflatten a flattened dictionary.
    """
    result = {}
    for key, value in d.items():
        parts = key.split(sep)
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result

def compare_parameters(param1:dict, param2:dict, ignore_keys=None):
    """
    Compare two dictionaries and return differences.
    """
    if ignore_keys is None:
        ignore_keys = set()
    flat1 = flatten_dict(param1)
    flat2 = flatten_dict(param2)
    
    differences = {}
    for key in set(flat1.keys()).union(flat2.keys()):
        if any(ignored in key for ignored in ignore_keys):
            continue
        if flat1.get(key) != flat2.get(key):
            differences[key] = (flat1.get(key), flat2.get(key))
    
    return differences

def load_parameters_with_references(param_path):
    """ Load parameters while keeping values with references as string
    """

    param_path = (Path.cwd() / param_path).parent
    param_name = param_path.name

    tmp_path = param_path / "tmp"
    tmp_path.mkdir(parents=False, exist_ok=False)

    for file_name in param_path.glob("*"):
        if file_name.is_dir():
            # print(f"Skipping directory: {file_name}")
            continue
        # print(f"Processing file: {file_name}")
        with open(file_name, 'r') as src_file, open(tmp_path / file_name.name, 'w') as dest_file:
            string_flag = False
            for line in src_file:
                line = line.replace('"',"'")
                if 'url(' in line:
                    line = line.replace(param_name, f'{param_name}/tmp')

                if 'ref(' in line or string_flag:
                    if ":" in line:
                        line = line. replace(':', ':"')
                        string_flag = True

                    if line.rstrip().endswith(','):
                        line = line.replace(',', '",')  # add string end "
                        string_flag = False
                    elif "\\" not in line and (line.count('(') == line.count(')')):
                        line = line.replace("\n", '",\n')
                        string_flag = False
                dest_file.write(line)

    str_param = load_parameters(f"{param_name}/tmp/defaults",{}).to_dict()
    str_param = flatten_dict(str_param)
    for key, value in str_param.items():
        if isinstance(value, str):
            str_param[key] = value.strip()
    str_param = unflatten_dict(str_param)

    for tmp_file in tmp_path.glob("*"):
        # print(f"Removing temporary file: {tmp_file}")
        tmp_file.unlink()
    # print(f"Removing temporary directory: {tmp_path}")
    tmp_path.rmdir() 

    return str_param

def compare_model_parameters(model_path, ignore_keys):
    print(f"Comparing parameters for {model_path}\n")
    os.chdir(model_path)

    print("Comparing LOADED parameters:")
    param = load_parameters("param/defaults",{}).to_dict()
    param_spont = load_parameters("param_spont/defaults", {}).to_dict()
    try:
        param_optim = load_parameters("param_optim/defaults", {}).to_dict()
    except (NameError, FileNotFoundError):
        print("No 'param_optim' found, skipping optimization parameters.")
        param_optim = None
    print('Differences between "param"       and  "param_spont": ', compare_parameters(param, param_spont, ignore_keys))
    if param_optim:
        print('Differences between "param"       and  "param_optim": ', compare_parameters(param, param_optim, ignore_keys))
        print('Differences between "param_spont" and  "param_optim": ', compare_parameters(param_spont, param_optim, ignore_keys))
    print("="*80)

    print('Checking recorders:')

    param_list = [param, param_spont]
    recorder_list = [RECS, RECS_SPONT]
    if param_optim:
        param_list.append(param_optim)
        recorder_list.append(RECS_OPTIM)
    for p, r in zip(param_list, recorder_list):
        for sheet in p['sheets'].keys():
            s = sheet.split('_')
            if s[1] == 'cortex':
                assert p['sheets'][sheet]['params']['recorders'] == r[f'{s[0]}_{s[-1]}_rec']
            elif s[1] == 'lgn':
                assert p['sheets'][sheet]['params']['recorders'] == r[f'{s[-1]}_rec']
            else:
                print(f"Unknown sheet type: {sheet}")
    print('All recorders match the predefined ones.')
    print("="*80)

    print("Comparing parameters with REFS:")

    param = load_parameters_with_references("param/defaults")
    param_spont = load_parameters_with_references("param_spont/defaults")

    try:
        param_optim = load_parameters_with_references("param_optim/defaults")
    except (NameError, FileNotFoundError):
        print("No 'param_optim' found, skipping optimization parameters.")
        param_optim = None
    print('Differences between "param"       and  "param_spont": ', compare_parameters(param, param_spont, ignore_keys))
    if param_optim:
        print('Differences between "param"       and  "param_optim": ', compare_parameters(param, param_optim, ignore_keys))
        print('Differences between "param_spont" and  "param_optim": ', compare_parameters(param_spont, param_optim, ignore_keys))