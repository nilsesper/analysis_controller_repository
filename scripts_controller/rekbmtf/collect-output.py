#######################################
### REKBMTF STEP: OUTPUT COLLECTION ###
#######################################

############################
### IMPORTS

import os
import argparse
import time
from datetime import datetime

from analysis_controller.src import path_utils
from analysis_controller.src import file_utils
from analysis_controller.src import console_utils
from analysis_controller.src import config_utils
from analysis_controller.src import constants

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
    "--collection",
    help="path to \"ConfigRekbmtfCollection\" yaml file (str)",
    type=str,
    required=True,
)
parser.add_argument(
    "--submission",
    help="path to \"ConfigRekbmtfSubmission\" yaml file (str)",
    type=str,
    required=True,
)
# optional:
args = parser.parse_args()

#############################
#****************************
### MAIN PART

### import ConfigRekbmtfCollection file
ConfigRekbmtfCollection = config_utils.load_config_file(filepath=args.collection, config_type="ConfigRekbmtfCollection", replace_wildcards=True, verbose=1)
# extract config info
RekbmtfCollection = ConfigRekbmtfCollection.RekbmtfCollection
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Output type of this collection is \"{RekbmtfCollection.output_type}\"")

### import ConfigRekbmtfSubmission file
ConfigRekbmtfSubmission = config_utils.load_config_file(filepath=args.submission, config_type="ConfigRekbmtfSubmission", replace_wildcards=True, verbose=1)
# extract config info
RekbmtfInput = ConfigRekbmtfSubmission.RekbmtfInput
RekbmtfParams = ConfigRekbmtfSubmission.RekbmtfParams
RekbmtfParamsSubmission = ConfigRekbmtfSubmission.RekbmtfParamsSubmission
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Submission type of this submission is \"{RekbmtfParams.submission_type}\"")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Output type of this submission is \"{RekbmtfParams.output_type}\"")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Submission timestamp of this submission is \"{RekbmtfParamsSubmission.submission_timestamp}\"")

### define submission timestamp
collection_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Setting collection timestamp as \"{collection_timestamp}\"")

### collect name
collection_name = f"{analysis_step}_{RekbmtfInput.data_type}_{RekbmtfInput.data_label}_{collection_timestamp}"

### collection path, where all info about this data collection is stored
collection_path = os.path.join(constants.output_basepath, collection_name)
# create collect path
os.mkdir(collection_path)
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Prepared collection directory at \"{collection_path}\"")

#=============================================================================
#====== OUTPUT_TYPE: CERN-GRID
if RekbmtfParams.output_type == "cern-grid":

    #====== OUTPUT_SITE: T2_DE_RWTH
    if RekbmtfParams.output_site == "T2_DE_RWTH":
    
        #====== SUBMISSION_TYPE: CERN-CRAB
        if RekbmtfParams.submission_type == "cern-crab":

            ########################
            ### prepare input

            ### derive crab submitpath
            input_das_name_firstword = RekbmtfInput.input_das_name.split("/")[1] # extract first word of input_das_name: "L1Scouting" = first word of "/L1Scouting/Run2024I-v1/L1SCOUT"
            output_path = f"{RekbmtfParams.output_basepath}/{input_das_name_firstword}/crab_{RekbmtfParamsSubmission.crab_requestname}"

            ### obtain list of output files on grid storage
            # prepare grid access
            gfal_prefix = "davs://grid-webdav.physik.rwth-aachen.de:2889/"
            gfal_basepath = f"{gfal_prefix}{output_path}/"
            console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Attempting to recursively list root files in GRID output path \"{gfal_basepath}\"")
            # ls grid files recursively
            input_file_list, input_total_size = file_utils.recursive_file_scan(basepath=gfal_basepath, ls_command="gfal-ls -l", file_suffix=".root", maxdepth=5, verbose=1)
            # replace gfal prefix with xrood redirector, so one can access the files on the grid via xrootd
            xrootd_redirector_prefix = "root://xrootd-cms.infn.it//"
            file_utils.replace_substring_filepath(file_list=input_file_list, subs_from=gfal_prefix, subs_with=xrootd_redirector_prefix)

            ### group together output files
            input_file_groups = file_utils.group_files(file_list=input_file_list, target_group_size=RekbmtfCollection.hadd_file_size)

            ########################
            ### merge files

            ### prepare collection basepath
            collection_basepath = os.path.join(RekbmtfCollection.output_basepath, collection_name)

            ### make sure output basepath exists
            if not os.path.isdir(RekbmtfCollection.output_basepath):
                console_utils.raise_exception(string=f"The output base path \"{RekbmtfCollection.output_basepath}\" does not exist")
            
            ### create collection basepath
            # make sure it did not exist before
            if os.path.isdir(collection_basepath):
                console_utils.raise_exception(string=f"The collection base path subdirectory \"{collection_basepath}\" does already exist")
            # create dir
            console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Attempting to create collection base path subdirectory \"{collection_basepath}\"")
            os.mkdir(collection_basepath)

            ### generate hadd file paths from file groups
            collection_file_list = file_utils.hadd_names_from_file_groups(file_group_list=input_file_groups, hadd_basepath=collection_basepath, hadd_name_prefix=RekbmtfCollection.hadd_file_prefix, verbose=1)

            ### actually perform hadd-ing of files
            collection_file_list = file_utils.run_hadd_commands(hadd_file_list=collection_file_list, check_exists=True)

            ########################
            ### store output object

            ### prepare output object
            RekbmtfOutput = config_utils.create_config(
                config_type="RekbmtfOutput",
                replace_wildcards=True, verbose=1,
                **{
                    "collection_basepath": collection_basepath,
                    "collection_files": collection_file_list,
                    "collection_timestamp": collection_timestamp,
                    "collection_name": collection_name,
                }
            )
            ### prepare and store config file object
            collection_filename = "ConfigRekbmtfOutput.yaml"
            collection_filepath = os.path.join(collection_path, collection_filename)
            ConfigRekbmtfOutput = config_utils.create_config(
                config_type="ConfigRekbmtfOutput",
                replace_wildcards=True, verbose=1,
                **{
                    "RekbmtfInput": RekbmtfInput,
                    "RekbmtfParams": RekbmtfParams,
                    "RekbmtfParamsSubmission": RekbmtfParamsSubmission,
                    "RekbmtfCollection": RekbmtfCollection,
                    "RekbmtfOutput": RekbmtfOutput,
                }
            )
            config_utils.store_config_file(filepath=collection_filepath, config=ConfigRekbmtfOutput, config_type="ConfigRekbmtfOutput", verbose=1)

            ########################
            ### do some verification

            ### verify file size of created hadd files
            # get hadd files total size
            collection_verification_file_list, collection_verification_total_size = file_utils.recursive_file_scan(basepath=collection_basepath, ls_command="ls -l", file_suffix=".root", maxdepth=5, verbose=1)
            # compare with input file size
            file_size_abs_diff = abs(collection_verification_total_size - input_total_size)
            file_size_rel_diff = file_size_abs_diff / collection_verification_total_size
            file_size_rel_diff_thres = 0.05
            if file_size_rel_diff > file_size_rel_diff_thres:
                console_utils.raise_exception(string=f"The created hadd files do not match in total size with the input files within \"{file_size_rel_diff_thres*100:03f} %\"")
            console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The created hadd files do match in total size with the input files within \"{file_size_rel_diff_thres*100:03f} %\"")

        #======
        else:
            console_utils.raise_exception(string=f"Unsupported submission type \"{RekbmtfParams.submission_type}\"")
    #======
    else:
        console_utils.raise_exception(string=f"{console_utils.color.red}Unsupported output site \"{RekbmtfParams.output_site}\"")

#======
else:
    console_utils.raise_exception(string=f"{console_utils.color.red}Unsupported output type \"{RekbmtfParams.output_type}\"")
#=============================================================================

# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Finished the output collection")




#****************************
#############################

stop_time = time.time()
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The execution took \"{(stop_time - start_time):03f} seconds\"")
console_utils.print_console_footer()
