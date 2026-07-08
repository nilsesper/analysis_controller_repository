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
from analysis_controller.src import config_utils

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_PATH, _ANALYSIS_CONTROLLER_REPO_PATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)
console_utils.print_console_header(analysis_controller_filepath=_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH)

start_time = time.time()

### define analysis step
analysis_step = "rekbmtf"
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Analysis step is \"{analysis_step}\"")

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

### import submit config file
ConfigFileRekbmtfSubmission = config_utils.load_ConfigFileRekbmtfSubmission(filepath=args.submit_config, verbose=1)
# extract config info
RekbmtfInput = ConfigFileRekbmtfSubmission.RekbmtfInput
RekbmtfParams = ConfigFileRekbmtfSubmission.RekbmtfParams
RekbmtfSubmission = ConfigFileRekbmtfSubmission.RekbmtfSubmission
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Submission type of this dataset is \"{RekbmtfParams.submission_type}\"")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Output type of this dataset is \"{RekbmtfParams.output_type}\"")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Submission timestamp of this dataset is \"{RekbmtfSubmission.submission_timestamp}\"")

### parse optional arguments
command_arg = None
if args.command:
    command_arg = args.command

### check optional arguments
if (command_arg == None) and (action_type in ["command"]):
    raise Exception(f"{console_utils.color.red}Missing argument --command for specified action \"command\" {console_utils.color.reset}")
elif (command_arg != None) and (action_type not in ["command"]):
    raise Exception(f"{console_utils.color.red}Unexpected argument --command {console_utils.color.reset}")

#=============================================================================
#== SUBMISSION_TYPE: CERN-CRAB
if RekbmtfParams.submission_type == "cern-crab":
    
    #== ACTION_TYPE: MONITOR
    # monitor the crab submission status
    if action_type == "monitor":

        ### derive crab submitpath
        crab_submitpath = os.path.join(RekbmtfSubmission.crab_workarea, f"crab_{RekbmtfSubmission.crab_requestname}")

        ### poll status from crab
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Attempting to poll submission status from CRAB, using the CRAB submit directory \"{crab_submitpath}\"")
        bash_commands = f''
        bash_commands += f'\n'
        # source cms base env
        bash_commands += f'source /cvmfs/cms.cern.ch/cmsset_default.sh\n'
        # # prepare voms
        # bash_commands += f'voms-proxy-init --rfc --voms cms -valid 192:00\n'
        # cd into cmssw workarea
        bash_commands += f'cd {RekbmtfParams.cmssw_src_path}\n'
        # source cmssw env
        bash_commands += f'cmsenv\n'
        # cd into submitpath
        bash_commands += f'cd {RekbmtfSubmission.submission_path}\n'
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
        crab_submitpath = os.path.join(RekbmtfSubmission.crab_workarea, f"crab_{RekbmtfSubmission.crab_requestname}")

        ### execute custom crab command (specified in )
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Attempting execute specified command \"{command_arg}\" with CRAB, using the CRAB submit directory \"{crab_submitpath}\"")
        bash_commands = f''
        bash_commands += f'\n'
        # source cms base env
        bash_commands += f'source /cvmfs/cms.cern.ch/cmsset_default.sh\n'
        # # prepare voms
        # bash_commands += f'voms-proxy-init --rfc --voms cms -valid 192:00\n'
        # cd into cmssw workarea
        bash_commands += f'cd {RekbmtfParams.cmssw_src_path}\n'
        # source cmssw env
        bash_commands += f'cmsenv\n'
        # cd into submitpath
        bash_commands += f'cd {RekbmtfSubmission.submission_path}\n'
        # custom crab command
        bash_commands += f'crab {command_arg} -d {crab_submitpath}\n'
        # execute commands
        _, _ = console_utils.run_command(bash_command=bash_commands)

    #== 
    else:
        raise Exception(f"{console_utils.color.red}Unsupported action type \"{action_type}\"{console_utils.color.reset}")

#=============================================================================
else:
    raise Exception(f"{console_utils.color.red}Unsupported submission type \"{RekbmtfSubmission.submission_type}\"{console_utils.color.reset}")
#=============================================================================

# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Finished the specified action")

#****************************
#############################

stop_time = time.time()
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The execution took \"{stop_time - start_time} seconds\"")
console_utils.print_console_footer()
