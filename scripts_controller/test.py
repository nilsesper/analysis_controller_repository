###################
### TEST SCRIPT ###
###################

############################
### IMPORTS

import os
import argparse
import time

from analysis_controller.src import path_utils
from analysis_controller.src import console_utils
from analysis_controller.src import config_utils

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_PATH, _ANALYSIS_CONTROLLER_REPO_PATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)
console_utils.print_console_header(analysis_controller_filepath=_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH)

start_time = time.time()

#############################
### ARGUMENT PARSER

#############################
#****************************
### MAIN PART

RekbmtfInputObject = config_utils.RekbmtfInput(
    data_type="",
    data_label="",
    input_das_name="",
    input_lumi_mask="",
)
RekbmtfInputObject = config_utils.RekbmtfInput(
    **{
        "data_type": "",
        "data_label": "",
        "input_das_name": "",
        "input_lumi_mask": "",
    }
)
config_rekbmtf_input = config_utils.ConfigFileRekbmtfInput(
    RekbmtfInput=RekbmtfInputObject,
)
config_rekbmtf_input = config_utils.load_ConfigFileRekbmtfInput(filepath="config/rekbmtf_input_config.yaml")
config_rekbmtf_params = config_utils.load_ConfigFileRekbmtfParams(filepath="config/rekbmtf_params_config.yaml")
config_rekbmtf_submission = config_utils.load_ConfigFileRekbmtfSubmission(filepath="submissions/rekbmtf_2026-06-18_11-52-59_data_Scouting_2024H/submit_config.yaml")

#****************************
#############################

stop_time = time.time()
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The execution took \"{stop_time - start_time} seconds\"")
console_utils.print_console_footer()
