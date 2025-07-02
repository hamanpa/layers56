"""
Script to move directories of parameter searches that have been completed to a new directory while deleting datastores and log files.

TODO:
1. remove ParameterSearch directory after copying
2. create a helper function to remove directory
"""

from pathlib import Path
from shutil import copytree, ignore_patterns, rmtree
from fnmatch import filter

MODEL_DIR = Path('/home/haman/layers56/LSV1M')
CLEAN_RUNS = Path('/home/haman/layers56/ParameterSearches')

IGNORED = [
    'OUTFILE*',
    'slurm*.out',
    'Segment*',
    'datastore*',
    'log*',
    'parameter_combinations',
    '[0-9]/*',

]
REMOVE_DIR = False
KEEP = [
    '*.json',
    '*.png',
    '*.gif',
    'results.pickle',
]

# How to ignore parallel processes? (directories like ./1/ etc.)

def ensure_dir_exists(path):
    if not path.exists():
        path.mkdir()

def include_patterns(*patterns):
    """Factory function that can be used with copytree() ignore parameter.

    Arguments define a sequence of glob-style patterns
    that are used to specify what files to NOT ignore.
    Creates and returns a function that determines this for each directory
    in the file hierarchy rooted at the source directory when used with
    shutil.copytree().
    """
    def _ignore_patterns(path, names):
        # path is the directory where the patterns are applied
        # names is the list of files and directories in the directory (path)
        keep = set(name for pattern in patterns for name in filter(names, pattern))
        ignore = set(name for name in names if name not in keep and not Path(path, name).is_dir())
        return ignore
    return _ignore_patterns

def main():
    ensure_dir_exists(CLEAN_RUNS)
    for param_search in MODEL_DIR.glob("[0-9]*CombinationParamSearch*"):
        new_dir = CLEAN_RUNS / param_search.name
        if new_dir.exists():  # Skip if directory already exists
            continue
        else:
            print(param_search.name)
        copytree(param_search, new_dir, ignore=include_patterns(*KEEP))
        # Clean copied empty directories
        for sim_run in new_dir.glob('**/[0-9]*/'):  
            # if sim_run.is_dir() and not any(sim_run.iterdir()):
            if sim_run.is_dir() and not any(child.is_dir() for child in sim_run.iterdir()):
                rmtree(sim_run)

if __name__ == '__main__':
    main()

