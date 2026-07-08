####################################
### SUBMISSION OUTPUT COLLECTION ###
####################################

############################
### IMPORTS

import os
import argparse
import subprocess
import time
from datetime import datetime

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
# optional:
args = parser.parse_args()

#############################
#****************************
### MAIN PART

### import submit config file
ConfigRekbmtfSubmission = config_utils.load_config_file(filepath=args.submit_config, config_type="ConfigRekbmtfSubmission", replace_wildcards=True, verbose=1)
# extract config info
RekbmtfInput = ConfigRekbmtfSubmission.RekbmtfInput
RekbmtfParams = ConfigRekbmtfSubmission.RekbmtfParams
RekbmtfSubmission = ConfigRekbmtfSubmission.RekbmtfSubmission
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Submission type of this dataset is \"{RekbmtfParams.submission_type}\"")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Output type of this dataset is \"{RekbmtfParams.output_type}\"")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Submission timestamp of this dataset is \"{RekbmtfSubmission.submission_timestamp}\"")

### define submission timestamp
collect_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Setting collection timestamp as \"{collect_timestamp}\"")

### collect name
collect_name = f"{analysis_step}_{collect_timestamp}_{RekbmtfInput.data_type}_{RekbmtfInput.data_label}"

### collection path, where all info about this data collection is stored
collect_path = os.path.join(_ANALYSIS_CONTROLLER_REPO_PATH, "collections", collect_name)
# create collect path
os.mkdir(collect_path)
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Prepared collection directory at \"{collect_path}\"")

#=============================================================================
#== OUTPUT_TYPE: CERN-GRID
if RekbmtfParams.output_type == "cern-grid":
    
    #== SUBMISSION_TYPE: CERN-CRAB
    if RekbmtfParams.submission_type == "cern-crab":

        ### derive crab submitpath
        input_das_name_firstword = RekbmtfInput.input_das_name.split("/")[1] # extract first word of input_das_name: "L1Scouting" = first word of "/L1Scouting/Run2024I-v1/L1SCOUT"
        output_path = f"{RekbmtfParams.output_basepath}/{input_das_name_firstword}/crab_{RekbmtfSubmission.crab_requestname}"

        ### obtain list of output files on grid storage
        gfal_prefix = "davs://grid-webdav.physik.rwth-aachen.de:2889/"
        gfal_basepath = f"{gfal_prefix}{output_path}/"
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Attempting to recursively list root files in GRID output path \"{gfal_basepath}\"")
        # ls grid files recursively
        file_list = file_utils.recursive_file_scan(basepath=gfal_basepath, ls_command="gfal-ls -l", file_suffix=".root", maxdepth=5, verbose=1)
        
        ### group together output files
        target_group_size = "1 GiB"
        file_groups = file_utils.group_files(file_list=file_list, target_group_size=target_group_size)

        ### prepare file paths (remove gfal prefix, add xrootd redirector prefix)
        xrootd_redirector_prefix = "root://xrootd-cms.infn.it//"
        for i_group in range(len(file_groups)):
            for i_file in range(len(file_groups[i_group]["files"])):
                file_path = file_groups[i_group]["files"][i_file]["path"]
                # remove gfal prefix from file path
                file_path = file_path.replace(gfal_prefix, "")
                # add xrootd redirector prefix to file path
                file_path = f"{xrootd_redirector_prefix}{file_path}"
                # replace file path
                file_groups[i_group]["files"][i_file]["path"] = file_path
                #print(file_path)

        ### prepare hadd-ed file paths (add grouppath to file_group dict)

        # ### hadd together grouped output files, and store them in target file path
        # hadd_output_basepath = ""
        # merged_files = file_utils.hadd_file_groups(file_groups=file_groups)

        ### prepare output object
        RekbmtfOutput = config_utils.create_config(
            config_type="RekbmtfOutput",
            replace_wildcards=True, verbose=1,
            **{
                "output_files": file_list,
                "output_file_groups": file_groups,
                "target_output_file_size": target_group_size,
                "collection_output_type": "",
                "collection_output_site": "",
                "collection_basepath": "",
                "collected_files": [],
            }
        )
        ### prepare and store config file object
        collection_filename = "ConfigRekbmtfOutput.yaml"
        collection_filepath = os.path.join(collect_path, collection_filename)
        ConfigRekbmtfOutput = config_utils.create_config(
            config_type="ConfigRekbmtfOutput",
            replace_wildcards=True, verbose=1,
            **{
                "RekbmtfInput": RekbmtfInput,
                "RekbmtfParams": RekbmtfParams,
                "RekbmtfSubmission": RekbmtfSubmission,
                "RekbmtfOutput": RekbmtfOutput,
            }
        )
        config_utils.store_config_file(filepath=collection_filepath, config=ConfigRekbmtfOutput, config_type="ConfigRekbmtfOutput", verbose=1)

    #== 
    else:
        raise Exception(f"{console_utils.color.red}Unsupported submission type \"{RekbmtfParams.submission_type}\"{console_utils.color.reset}")

#=============================================================================
else:
    raise Exception(f"{console_utils.color.red}Unsupported output type \"{RekbmtfParams.output_type}\"{console_utils.color.reset}")
#=============================================================================

# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Finished the output collection")




#****************************
#############################

stop_time = time.time()
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The execution took \"{stop_time - start_time} seconds\"")
console_utils.print_console_footer()
