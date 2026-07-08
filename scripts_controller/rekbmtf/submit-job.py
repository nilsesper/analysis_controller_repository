#################################
### RE-KBMTF STEP: SUBMISSION ###
#################################

############################
### IMPORTS

import os
import argparse
import subprocess
from datetime import datetime
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
    "--input",
    help=f"path to \"ConfigRekbmtfInput\" yaml file (str)",
    type=str,
    required=True,
)
parser.add_argument(
    "--params",
    help=f"path to \"ConfigRekbmtfParams\" yaml file (str)",
    type=str,
    required=True,
)
# optional:
args = parser.parse_args()

#############################
#****************************
### MAIN PART

### import input config file
ConfigRekbmtfInput = config_utils.load_config_file(filepath=args.input, config_type="ConfigRekbmtfInput", replace_wildcards=True, verbose=1)
# extract config info
RekbmtfInput = ConfigRekbmtfInput.RekbmtfInput
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Data type of this submission is \"{RekbmtfInput.data_type}\"")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Data label of this submission is \"{RekbmtfInput.data_label}\"")

### import params config file
ConfigRekbmtfParams = config_utils.load_config_file(filepath=args.params, config_type="ConfigRekbmtfParams", replace_wildcards=True, verbose=1)
# extract config info
RekbmtfParams = ConfigRekbmtfParams.RekbmtfParams
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Submission type of this submission is \"{RekbmtfParams.submission_type}\"")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Output type of this submission is \"{RekbmtfParams.output_type}\"")

### define submission timestamp
submission_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Setting submission timestamp as \"{submission_timestamp}\"")

### start submission
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Attempting to submit dataset")

### submit name
submission_name = f"{analysis_step}_{submission_timestamp}_{RekbmtfInput.data_type}_{RekbmtfInput.data_label}"

### submission path, where all info about this submission is stored
submission_path = os.path.join(_ANALYSIS_CONTROLLER_REPO_PATH, "submissions", submission_name)
# create submit path
os.mkdir(submission_path)
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Prepared submission directory at \"{submission_path}\"")

#=============================================================================
#== SUBMISSION_TYPE: CERN-CRAB  &&  OUTPUT_TYPE: CERN-GRID
if RekbmtfParams.submission_type == "cern-crab" and RekbmtfParams.output_type == "cern-grid":

    ### prepare variables
    crab_requestname = submission_name
    
    ### prepare crab work area
    crab_workarea = os.path.join(submission_path, "crab_project")
    os.mkdir(crab_workarea)

    ### prepare cmssw config file
    # copy cmssw template file to submitpath
    cmssw_config_filename = f"cmssw_cfg.py"
    cmssw_config_filepath = os.path.join(submission_path, cmssw_config_filename)
    # copy template file
    _, _ = console_utils.run_command(bash_command=f'cp {RekbmtfParams.cmssw_config_template_filepath} {cmssw_config_filepath}\n')
    # prepare cmssw wildcards
    cmssw_config_wildcards = {
        
    }
    # open cmssw template, and replace wildcards
    content = file_utils.load_local_file(filepath=cmssw_config_filepath)
    new_content = file_utils.replace_wildcards_if_possible(content=content, wildcards=cmssw_config_wildcards)
    file_utils.store_local_file(filepath=cmssw_config_filepath, new_content=new_content)
    # print
    console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Prepared CMSSW config file at \"{cmssw_config_filepath}\", based on template file \"{RekbmtfParams.cmssw_config_template_filepath}\"")

    ### prepare crab config file
    # copy crab template file to submitpath
    crab_config_filename = f"crab_cfg.py"
    crab_config_filepath = os.path.join(submission_path, crab_config_filename)
    # copy template file
    _, _ = console_utils.run_command(bash_command=f'cp {RekbmtfParams.crab_config_template_filepath} {crab_config_filepath}\n')
    # prepare crab wildcards
    crab_config_wildcards = {
        "++++CRAB_REQUESTNAME++++": crab_requestname,
        "++++CRAB_WORKAREA++++": crab_workarea,
        "++++CMSSW_CONFIGFILE++++": cmssw_config_filepath,
        "++++INPUT_DAS_NAME++++": RekbmtfInput.input_das_name,
        "++++INPUT_LUMI_MASK++++": RekbmtfInput.input_lumi_mask,
        "++++CRAB_OUTPUT_BASEDIR++++": RekbmtfParams.output_basepath,
        "++++CRAB_STORAGE_SITE++++": RekbmtfParams.output_site,
    }
    # open crab template, and replace wildcards
    content = file_utils.load_local_file(filepath=crab_config_filepath)
    new_content = file_utils.replace_wildcards_if_possible(content=content, wildcards=crab_config_wildcards)
    file_utils.store_local_file(filepath=crab_config_filepath, new_content=new_content)
    # print
    console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Prepared CRAB config file at \"{crab_config_filepath}\", based on template file \"{RekbmtfParams.crab_config_template_filepath}\"")

    ### finally: submit to crab
    console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Attempting to submit to CRAB, using the CRAB workarea \"{crab_workarea}\"")
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
    bash_commands += f'cd {submission_path}\n'
    # crab submit command
    bash_commands += f'crab submit -c {crab_config_filepath}\n'
    #bash_commands += f'crab submit -c {crab_config_filepath} --dryrun\n'
    # execute commands
    _, _ = console_utils.run_command(bash_command=bash_commands)

    ### prepare submission object
    RekbmtfSubmission = config_utils.create_config(
        config_type="RekbmtfSubmission",
        replace_wildcards=True, verbose=1,
        **{
            "submission_name": submission_name,
            "submission_path": submission_path,
            "submission_timestamp": submission_timestamp,

            "cmssw_config_filepath": cmssw_config_filepath,
            "crab_config_filepath": crab_config_filepath,
            "crab_requestname": crab_requestname,
            "crab_workarea": crab_workarea,
        }
    )
    ### prepare and store config file object
    submission_filename = "ConfigRekbmtfSubmission.yaml"
    submission_filepath = os.path.join(submission_path, submission_filename)
    ConfigRekbmtfSubmission = config_utils.create_config(
        config_type="ConfigRekbmtfSubmission",
        replace_wildcards=True, verbose=1,
        **{
            "RekbmtfInput": RekbmtfInput,
            "RekbmtfParams": RekbmtfParams,
            "RekbmtfSubmission": RekbmtfSubmission,
        }
    )
    config_utils.store_config_file(filepath=submission_filepath, config=ConfigRekbmtfSubmission, config_type="ConfigRekbmtfSubmission", verbose=1)
    
#======
else:
    console_utils.raise_exception(string=f"Unsupported combination of submission type \"{RekbmtfParams.submission_type}\" and output type \"{RekbmtfParams.output_type}\"")
#=============================================================================

# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Finished submitting the dataset")

#****************************
#############################

stop_time = time.time()
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The execution took \"{stop_time - start_time} seconds\"")
console_utils.print_console_footer()
