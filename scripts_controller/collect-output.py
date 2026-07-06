####################################
### SUBMISSION OUTPUT COLLECTION ###
####################################

############################
### IMPORTS

import os
import argparse
import subprocess
import time

from analysis_controller.src import path_utils
from analysis_controller.src import file_utils
from analysis_controller.src import console_utils

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_PATH, _ANALYSIS_CONTROLLER_REPO_PATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)
console_utils.print_console_header(analysis_controller_filepath=_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH)

start_time = time.time()
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Starting execution at time.time() value of \"{start_time} seconds\"")

#############################
### ARGUMENT PARSER

parser = argparse.ArgumentParser()
# mandatory:
parser.add_argument(
    "--submit_config",
    help="path to submit config yaml file \"*_submit\" (str)",
    type=str,
    required=True,
)
parser.add_argument(
    "--step",
    help="analysis step that was submitted, e.g. \"rekbmtf\" (str)",
    type=str,
    required=True,
)
# optional:
args = parser.parse_args()

#############################
#****************************
### MAIN PART

### check analysis step
analysis_step = args.step
allowed_analysis_steps = ["rekbmtf"]
if analysis_step not in allowed_analysis_steps:
    raise Exception(f"{console_utils.color.red}Invalid analysis step \"{analysis_step}\" specified. Allowed are only {allowed_analysis_steps} {console_utils.color.reset}")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Analysis step is \"{analysis_step}\"")

### import submit file
submit_config = file_utils.load_config(
    filepath=args.submit_config,
    config_type=f"{analysis_step}_submission"
)

### prepare variables from config
data_type = submit_config["data_type"]
data_label = submit_config["data_label"]
input_das_name = submit_config["input_das_name"]
input_lumi_mask = submit_config["input_lumi_mask"]

output_type = submit_config["output_type"]
output_site = submit_config["output_site"]
output_basepath = submit_config["output_basepath"]

submission_type = submit_config["submission_type"]
submission_splitting = submit_config["submission_splitting"]

cmssw_src_path = submit_config["cmssw_src_path"]

crab_config_filepath = submit_config["crab_config_filepath"]
cmssw_config_filepath = submit_config["cmssw_config_filepath"]

crab_workarea = submit_config["crab_workarea"]
crab_requestname = submit_config["crab_requestname"]

submit_path = submit_config["submit_path"]
submit_name = submit_config["submit_name"]
submit_timestamp = submit_config["submit_timestamp"]

# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Submission type of this dataset is \"{submission_type}\"")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Output type of this dataset is \"{output_type}\"")

#=============================================================================
#== OUTPUT_TYPE: CERN-GRID
if output_type == "cern-grid":
    
    #== SUBMISSION_TYPE: CERN-CRAB
    if submission_type == "cern-crab":

        ### derive crab submitpath
        input_das_name_firstword = input_das_name.split("/")[1] # extract first word of input_das_name: "L1Scouting" = first word of "/L1Scouting/Run2024I-v1/L1SCOUT"
        output_path = f"{output_basepath}/{input_das_name_firstword}/crab_{crab_requestname}"

        ### poll status from crab
        gfal_basepath = f"davs://grid-webdav.physik.rwth-aachen.de:2889/{output_path}/"
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Attempting to list output path on GRID \"{gfal_basepath}\"")
        bash_commands = f''
        # ls grid files
        _, _ = console_utils.run_command(bash_command=f'gfal-ls -lH {gfal_basepath}\n')
        # print
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Finished executing the commands for the CRAB status polling")

    #== 
    else:
        raise Exception(f"{console_utils.color.red}Unsupported submission type \"{submission_type}\"{console_utils.color.reset}")

#=============================================================================
else:
    raise Exception(f"{console_utils.color.red}Unsupported output type \"{output_type}\"{console_utils.color.reset}")
#=============================================================================

# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Finished the output collection")




#****************************
#############################

stop_time = time.time()
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Finshing execution at time.time() value of \"{stop_time} seconds\"")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The execution took \"{stop_time - start_time} seconds\"")
console_utils.print_console_footer()
