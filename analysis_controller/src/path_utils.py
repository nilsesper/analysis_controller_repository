##################
### PATH UTILS ###
##################

############################
### IMPORTS

import os

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)

### repo dir name
REPO_DIR_NAME = f"analysis_controller_repository"

### return relative path wrt "analysis_controller/" base path, not wrt "/home/..."
def relative_path_analysis_controller(*, filepath):
    filepath = os.path.abspath(filepath)
    if not os.path.isfile(filepath):
        raise Exception(f"Could not find the file \"{filepath}\"")
    if f"{REPO_DIR_NAME}/" not in filepath:
        raise Exception(f"Invalid {REPO_DIR_NAME} file dir. Must contain \"{REPO_DIR_NAME}/\".")
    _filepath = filepath.split(f"{REPO_DIR_NAME}/")[-1] # relative to REPO_DIR_NAME
    _analysiscontrollerpath = os.path.abspath(os.path.join(filepath.split(f"{REPO_DIR_NAME}/")[0], f"{REPO_DIR_NAME}", "analysis_controller"))
    _analysiscontrollerrepopath = os.path.abspath(os.path.join(filepath.split(f"{REPO_DIR_NAME}/")[0], f"{REPO_DIR_NAME}"))
    #print(f"_filepath = {_filepath}\n_analysiscontrollerpath = {_analysiscontrollerpath}\n_analysiscontrollerrepopath = {_analysiscontrollerrepopath}")
    return _filepath, _analysiscontrollerpath, _analysiscontrollerrepopath

_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_PATH, _ANALYSIS_CONTROLLER_REPO_PATH = relative_path_analysis_controller(filepath=_FILEPATH)

############################
### HELPER FUNCTIONS & CLASSES (with prefix "_")



############################
### MAIN FUNCTIONS & CLASSES




