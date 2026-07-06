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
    "--input_config",
    help=f"path to input config yaml file \"{analysis_step}_input\" (str)",
    type=str,
    required=True,
)
parser.add_argument(
    "--params_config",
    help=f"path to params config yaml file \"{analysis_step}_params\" (str)",
    type=str,
    required=True,
)
# optional:
args = parser.parse_args()

#############################
#****************************
### MAIN PART

### import config files
input_config = file_utils.load_config(
    filepath=args.input_config,
    config_type=f"{analysis_step}_input"
)
n_inputs = len(input_config)
#print(f"\ninput_config = {input_config}\n")
params_config = file_utils.load_config(
    filepath=args.params_config,
    config_type=f"{analysis_step}_params"
)
#print(f"\nparams_config = {params_config}\n")

### define submission timestamp
submit_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Setting submission timestamp for all datasets as \"{submit_timestamp}\"")


### do submission individually for each data_input entry
for i in range(n_inputs):
    console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Attempting to submit dataset {i+1} / {n_inputs}: data_type=\"{input_config[i]['data_type']}\", data_label=\"{input_config[i]['data_label']}\"")

    ### prepare variables from config files
    data_type = input_config[i]["data_type"]
    data_label = input_config[i]["data_label"]
    input_das_name = input_config[i]["input_das_name"]
    input_lumi_mask = input_config[i]["input_lumi_mask"]

    cmssw_src_path = params_config[data_type]["cmssw_src_path"]
    
    crab_config_template_filepath = params_config[data_type]["crab_config_template_filepath"]
    cmssw_config_template_filepath = params_config[data_type]["cmssw_config_template_filepath"]
    
    submission_type = params_config[data_type]["submission_type"]
    submission_splitting = params_config[data_type]["submission_splitting"]
    
    output_type = params_config[data_type]["output_type"]
    output_site = params_config[data_type]["output_site"]
    output_basepath = params_config[data_type]["output_basepath"]

    ### submitname
    submit_name = f"{analysis_step}_{submit_timestamp}_{data_type}_{data_label}"

    ### submission directory, where all info about this submission is stored
    submit_path = os.path.join(_ANALYSIS_CONTROLLER_REPO_PATH, "submissions", submit_name)
    # create submitdir
    os.mkdir(submit_path)
    # print
    console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Prepared submission directory for current dataset at \"{submit_path}\"")

    #=============================================================================
    #== SUBMISSION_TYPE: CERN-CRAB  &&  OUTPUT_TYPE: CERN-GRID
    if submission_type == "cern-crab" and output_type == "cern-grid":

        # print
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Submission type of this dataset is \"{submission_type}\"")
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Output type of this dataset is \"{output_type}\"")

        ### prepare variables
        crab_requestname = submit_name
        
        ### prepare crab work area
        crab_workarea = os.path.join(submit_path, "crab_project")
        os.mkdir(crab_workarea)
    
        ### prepare cmssw config file
        # copy cmssw template file to submitpath
        cmssw_config_filename = f"cmssw_cfg.py"
        cmssw_config_filepath = os.path.join(submit_path, cmssw_config_filename)
        # copy template file
        _, _ = console_utils.run_command(bash_command=f'cp {cmssw_config_template_filepath} {cmssw_config_filepath}\n')
        # prepare cmssw wildcards
        cmssw_config_wildcards = {
            
        }
        # open cmssw template, and replace wildcards
        content = file_utils.load_file(filepath=cmssw_config_filepath)
        new_content = file_utils.replace_wildcards_if_possible(content=content, wildcards=cmssw_config_wildcards)
        file_utils.store_local_file(filepath=cmssw_config_filepath, new_content=new_content)
        # print
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Prepared CMSSW config file for current dataset at \"{cmssw_config_filepath}\", based on template file \"{cmssw_config_template_filepath}\"")

        ### prepare crab config file
        # copy crab template file to submitpath
        crab_config_filename = f"crab_cfg.py"
        crab_config_filepath = os.path.join(submit_path, crab_config_filename)
        # copy template file
        _, _ = console_utils.run_command(bash_command=f'ccp {crab_config_template_filepath} {crab_config_filepath}\n')
        # prepare crab wildcards
        crab_config_wildcards = {
            "++++CRAB_REQUESTNAME++++": crab_requestname,
            "++++CRAB_WORKAREA++++": crab_workarea,
            "++++CMSSW_CONFIGFILE++++": cmssw_config_filepath,
            "++++INPUT_DAS_NAME++++": input_das_name,
            "++++INPUT_LUMI_MASK++++": input_lumi_mask,
            "++++CRAB_OUTPUT_BASEDIR++++": output_basepath,
            "++++CRAB_STORAGE_SITE++++": output_site,
        }
        # open crab template, and replace wildcards
        content = file_utils.load_file(filepath=crab_config_filepath)
        new_content = file_utils.replace_wildcards_if_possible(content=content, wildcards=crab_config_wildcards)
        file_utils.store_local_file(filepath=crab_config_filepath, new_content=new_content)
        # print
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Prepared CRAB config file for current dataset at \"{crab_config_filepath}\", based on template file \"{crab_config_template_filepath}\"")

        ### prepare submit yaml file with all information, for the next analyis steps and the job monitoring
        submit_yaml = {
            f"{analysis_step}_submission":
            {
                "data_type": data_type,
                "data_label": data_label,

                "input_das_name": input_das_name,
                "input_lumi_mask": input_lumi_mask,

                "submission_type": submission_type,
                "submission_splitting": submission_splitting,

                "cmssw_src_path": cmssw_src_path,

                "cmssw_config_filepath": cmssw_config_filepath,
                "crab_config_filepath": crab_config_filepath,

                "crab_requestname": crab_requestname,
                "crab_workarea": crab_workarea,

                "output_type": output_type,
                "output_site": output_site,
                "output_basepath": output_basepath,

                "submit_name": submit_name,
                "submit_path": submit_path,
                "submit_timestamp": submit_timestamp,
            }
        }
        ### store submit yaml file
        submit_filename = "submit_config.yaml"
        submit_filepath = os.path.join(submit_path, submit_filename)
        file_utils.store_local_yaml_file(filepath=submit_filepath, yaml_content=submit_yaml)
        console_utils.print_string(string=f"Created submit file at \"{submit_filepath}\"")
        # print
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Prepared submit config file for current dataset at \"{submit_filepath}\"")

        ### finally: submit to crab
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Attempting to submit to CRAB, using the CRAB workarea \"{crab_workarea}\"")
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
        # crab submit command
        bash_commands += f'crab submit -c {crab_config_filepath}\n'
        #bash_commands += f'crab submit -c {crab_config_filepath} --dryrun\n'
        # execute commands
        _, _ = console_utils.run_command(bash_command=bash_commands)
    
    #=============================================================================
    else:
        raise Exception(f"{console_utils.color.red}Unsupported combination of submission type \"{submission_type}\" and output type \"{output_type}\" {console_utils.color.reset}")
    #=============================================================================

    # print
    console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Finished submitting the specified datasets")

#****************************
#############################

stop_time = time.time()
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The execution took \"{stop_time - start_time} seconds\"")
console_utils.print_console_footer()
