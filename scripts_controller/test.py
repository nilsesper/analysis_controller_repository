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
from analysis_controller.src import file_utils

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_PATH, _ANALYSIS_CONTROLLER_REPO_PATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)
console_utils.print_console_header(analysis_controller_filepath=_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH)

start_time = time.time()

#############################
### ARGUMENT PARSER

#############################
#****************************
### MAIN PART

base_path = "/net/data_cms3a-1/esper/test_analysis_hscp_l1/analysis_controller_output/rekbmtf_2026-07-09_10-54-04_data_Scouting_2024H/"
file_path = "/net/data_cms3a-1/esper/test_analysis_hscp_l1/analysis_controller_output/rekbmtf_2026-07-09_10-54-04_data_Scouting_2024H/rekbmtf_output_0.root"

file_size = file_utils.get_file_size(file_path=file_path, ls_command="ls -l")
print(file_size)

collection_verification_file_list, collection_verification_total_size = file_utils.recursive_file_scan(basepath=base_path, ls_command="ls -l", file_suffix=".root", maxdepth=5, verbose=1)
print(collection_verification_total_size)

#****************************
#############################

stop_time = time.time()
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The execution took \"{stop_time - start_time} seconds\"")
console_utils.print_console_footer()
