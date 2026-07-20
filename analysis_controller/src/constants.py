############################################################
### analysis_controller CONSTANTS & HARDCODED PARAMETERS ###
############################################################

############################
### IMPORTS

import os

from analysis_controller.src import path_utils

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_PATH, _ANALYSIS_CONTROLLER_REPO_PATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)

############################
### HELPER FUNCTIONS & CLASSES (with prefix "_")

submission_basepath = os.path.join(_ANALYSIS_CONTROLLER_REPO_PATH, "output_controller", "submission")
output_basepath = os.path.join(_ANALYSIS_CONTROLLER_REPO_PATH, "output_controller", "output")

############################
### MAIN FUNCTIONS & CLASSES



