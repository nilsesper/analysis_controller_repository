##################################
### MOINTOR SUBMITTED CRAB JOB ###
##################################

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
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Starting execution at time.time() value of {start_time} seconds")

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
parser.add_argument(
    "--action",
    help="action that should be performed with submission: \"monitor\", \"command\" (str)",
    type=str,
    required=True,
)
# optional:
parser.add_argument(
    "--command",
    help="command to be executed, for --action \"command\" (str)",
    type=str,
)
args = parser.parse_args()

#############################
#****************************
### MAIN PART

### check action
action_type = args.action
allowed_action_types = ["monitor", "command"]
if action_type not in allowed_action_types:
    raise Exception(f"{console_utils.color.red}Invalid action \"{action_type}\" specified. Allowed are only {allowed_action_types} {console_utils.color.reset}")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Specified action is \"{action_type}\"")

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

### parse optional arguments
command_arg = None
if args.command:
    command_arg = args.command

### check optional arguments
if (command_arg == None) and (action_type in ["command"]):
    raise Exception(f"{console_utils.color.red}Missing argument --command for specified action \"command\" {console_utils.color.reset}")
elif (command_arg != None) and (action_type not in ["command"]):
    raise Exception(f"{console_utils.color.red}Unexpected argument --command {console_utils.color.reset}")

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
#== SUBMISSION_TYPE: CERN-CRAB
if submission_type == "cern-crab":
    
    #== ACTION_TYPE: MONITOR
    # monitor the crab submission status
    if action_type == "monitor":

        ### derive crab submitpath
        crab_submitpath = os.path.join(crab_workarea, f"crab_{crab_requestname}")

        ### poll status from crab
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Attempting to poll submission status from CRAB, using the CRAB submit directory \"{crab_submitpath}\"")
        bash_commands = f''
        bash_commands += f'\n'
        # source cms base env
        bash_commands += f'source /cvmfs/cms.cern.ch/cmsset_default.sh\n'
        # # prepare voms
        # bash_commands += f'voms-proxy-init --rfc --voms cms -valid 192:00\n'
        # cd into cmssw workarea
        bash_commands += f'cd {cmssw_src_path}\n'
        # source cmssw env
        bash_commands += f'cmsenv\n'
        # cd into submitpath
        bash_commands += f'cd {submit_path}\n'
        # crab status command
        bash_commands += f'crab status -d {crab_submitpath}\n'
        # execute commands
        _, _ = console_utils.run_command(bash_command=bash_commands)
        # print
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Finished executing the commands for the CRAB status polling")

    #== ACTION_TYPE: COMMAND
    # manually execute crab command for the current submission
    # execute the following: "crab {command_arg} -d {crab_submitpath}"
    elif action_type == "command":

        ### derive crab submitpath
        crab_submitpath = os.path.join(crab_workarea, f"crab_{crab_requestname}")

        ### execute custom crab command (specified in )
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Attempting execute specified command \"{command_arg}\" with CRAB, using the CRAB submit directory \"{crab_submitpath}\"")
        bash_commands = f''
        bash_commands += f'\n'
        # source cms base env
        bash_commands += f'source /cvmfs/cms.cern.ch/cmsset_default.sh\n'
        # # prepare voms
        # bash_commands += f'voms-proxy-init --rfc --voms cms -valid 192:00\n'
        # cd into cmssw workarea
        bash_commands += f'cd {cmssw_src_path}\n'
        # source cmssw env
        bash_commands += f'cmsenv\n'
        # cd into submitpath
        bash_commands += f'cd {submit_path}\n'
        # custom crab command
        bash_commands += f'crab {command_arg} -d {crab_submitpath}\n'
        # execute commands
        _, _ = console_utils.run_command(bash_command=bash_commands)
        # print
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Finished executing the specified command with CRAB")

    #== 
    else:
        raise Exception(f"{console_utils.color.red}Unsupported action type \"{action_type}\"{console_utils.color.reset}")

#=============================================================================
else:
    raise Exception(f"{console_utils.color.red}Unsupported submission type \"{submission_type}\"{console_utils.color.reset}")
#=============================================================================

# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Finished the specified action")

#****************************
#############################

stop_time = time.time()
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Finshing execution at time.time() value of {stop_time} seconds")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The execution took {stop_time - start_time} seconds")
console_utils.print_console_footer()
