######################################
### ANALYSIS1 STEP: JOB MONITORING ###
######################################

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

### define analysis step
analysis_step = "analysis1"
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Analysis step is \"{analysis_step}\"")

#############################
### ARGUMENT PARSER

parser = argparse.ArgumentParser()
# mandatory:
parser.add_argument(
    "--submission",
    help="path to \"ConfigSkimmingSubmission\" yaml file (str)",
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
    console_utils.raise_exception(string=f"Invalid action \"{action_type}\" specified. Allowed are only {allowed_action_types}")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Specified action is \"{action_type}\"")

### import submit config file
ConfigAnalysis1Submission = config_utils.load_config_file(filepath=args.submission, config_type="ConfigAnalysis1Submission", replace_wildcards=True, verbose=1)
# extract config info
Analysis1Input = ConfigAnalysis1Submission.Analysis1Input
Analysis1ParamsSubmission = ConfigAnalysis1Submission.Analysis1ParamsSubmission
Analysis1Submission = ConfigAnalysis1Submission.Analysis1Submission
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Submission type of this submission is \"{Analysis1ParamsSubmission.submission_type}\"")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Output type of this submission is \"{Analysis1ParamsSubmission.output_type}\"")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Submission timestamp of this submission is \"{Analysis1Submission.submission_timestamp}\"")

### parse optional arguments
command_arg = None
if args.command:
    command_arg = args.command

### check optional arguments
if (command_arg == None) and (action_type in ["command"]):
    console_utils.raise_exception(string=f"Missing argument --command for specified action \"command\"")
elif (command_arg != None) and (action_type not in ["command"]):
    console_utils.raise_exception(string=f"Unexpected argument --command")

#=============================================================================
#====== SUBMISSION_TYPE: AACHEN-CONDOR
if Analysis1ParamsSubmission.submission_type == "aachen-condor":
    
    #====== ACTION_TYPE: MONITOR
    # monitor the crab submission status
    if action_type == "monitor":

        ### derive condor workarea
        condor_workarea = Analysis1Submission.condor_workarea
        condor_cluster_id = Analysis1Submission.condor_cluster_id

        ### poll status from crab
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Attempting to poll submission status from CONDOR, using the CONDOR workarea \"{condor_workarea}\" and the CONDOR ClusterId \"{condor_cluster_id}\"")
        bash_commands = f''
        # cd into condor workarea
        bash_commands += f'cd {condor_workarea}\n'
        # condor status commands
        bash_commands += f'condor_q {condor_cluster_id}\n'
        bash_commands += f'condor_userprio\n'
        bash_commands += f'condor_qusers\n'
        # execute commands
        _, _ = console_utils.run_command(bash_command=bash_commands)
        # print
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Finished executing the commands for the CONDOR status polling")

    # #====== ACTION_TYPE: COMMAND
    # # manually execute crab command for the current submission
    # # execute the following: "crab {command_arg} -d {crab_submitpath}"
    # elif action_type == "command":

    #     ### derive crab submitpath
    #     crab_submitpath = os.path.join(SkimmingSubmission.crab_workarea, f"crab_{SkimmingSubmission.crab_requestname}")

    #     ### execute custom crab command (specified in )
    #     console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Attempting execute specified command \"{command_arg}\" with CRAB, using the CRAB submit directory \"{crab_submitpath}\"")
    #     bash_commands = f''
    #     bash_commands += f'\n'
    #     # source cms base env
    #     bash_commands += f'source /cvmfs/cms.cern.ch/cmsset_default.sh\n'
    #     # # prepare voms
    #     # bash_commands += f'voms-proxy-init --rfc --voms cms -valid 192:00\n'
    #     # cd into cmssw workarea
    #     bash_commands += f'cd {SkimmingParamsSubmission.cmssw_src_path}\n'
    #     # source cmssw env
    #     bash_commands += f'cmsenv\n'
    #     # cd into submitpath
    #     bash_commands += f'cd {SkimmingSubmission.submission_path}\n'
    #     # custom crab command
    #     bash_commands += f'crab {command_arg} -d {crab_submitpath}\n'
    #     # execute commands
    #     _, _ = console_utils.run_command(bash_command=bash_commands)

    #======
    else:
        console_utils.raise_exception(string=f"Unsupported action type \"{action_type}\"")

#======
else:
    console_utils.raise_exception(string=f"Unsupported submission type \"{Analysis1Submission.submission_type}\"")
#=============================================================================

# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Finished the specified action")

#****************************
#############################

stop_time = time.time()
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The execution took \"{(stop_time - start_time):03f} seconds\"")
console_utils.print_console_footer()
