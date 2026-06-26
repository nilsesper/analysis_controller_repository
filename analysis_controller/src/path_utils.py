##################
### PATH UTILS ###
##################

############################
### IMPORTS

import os

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)

### return relative path wrt "analysis_controller/" base path, not wrt "/home/..."
def relative_path_analysis_controller(*, filepath):
    filepath = os.path.abspath(filepath)
    if not os.path.isfile(filepath):
        raise Exception(f"Could not find the file \"{filepath}\"")
    if "analysis_controller/" not in filepath:
        raise Exception("Invalid analysis_controller file dir. Must contain \"analysis_controller/\".")
    _filepath = os.path.join("analysis_controller", filepath.split("analysis_controller/")[-1])
    _repopath = os.path.abspath(os.path.join(filepath.split("analysis_controller/")[0], "analysis_controller"))
    return _filepath, _repopath

_ANALYSIS_CONTROLLER_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_REPOPATH = relative_path_analysis_controller(filepath=_FILEPATH)

############################
### HELPER FUNCTIONS & CLASSES (with prefix "_")



############################
### MAIN FUNCTIONS & CLASSES




