#################################
### TEMPLATE_SCRIPT ###
#################################

############################
### IMPORTS

import os
import argparse

from analysis_controller.src import path_utils
from analysis_controller.src import cosmetic_utils

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_PATH, _ANALYSIS_CONTROLLER_REPO_PATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)
cosmetic_utils.print_console_header(analysis_controller_filepath=_ANALYSIS_CONTROLLER_RELATIVE_FILEPATH)

#############################
### ARGUMENT PARSER

parser = argparse.ArgumentParser()
# mandatory:
parser.add_argument(
    "--input_config",
    help="path to input config yaml file \"rekbmtf_input\" (str)",
    type=str,
    required=True,
)
# optional:
args = parser.parse_args()

#############################
#****************************
### MAIN PART



#****************************
#############################

cosmetic_utils.print_console_footer()
