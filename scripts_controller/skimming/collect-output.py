########################################
### SKIMMING STEP: OUTPUT COLLECTION ###
########################################

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
analysis_step = "skimming"
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Analysis step is \"{analysis_step}\"")

#############################
### ARGUMENT PARSER

parser = argparse.ArgumentParser()
# mandatory:
parser.add_argument(
    "--collection",
    help="path to \"ConfigSkimmingCollection\" yaml file (str)",
    type=str,
    required=True,
)
parser.add_argument(
    "--submission",
    help="path to \"ConfigSkimmingSubmission\" yaml file (str)",
    type=str,
    required=True,
)
# optional:
args = parser.parse_args()

#############################
#****************************
### MAIN PART

### import collection config file
ConfigSkimmingCollection = config_utils.load_config_file(filepath=args.collection, config_type="ConfigSkimmingCollection", replace_wildcards=True, verbose=1)
# extract config info
SkimmingCollection = ConfigSkimmingCollection.SkimmingCollection
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Output type of this collection is \"{SkimmingCollection.output_type}\"")

### import submission config file
ConfigSkimmingSubmission = config_utils.load_config_file(filepath=args.submission, config_type="ConfigSkimmingSubmission", replace_wildcards=True, verbose=1)
# extract config info
SkimmingInput = ConfigSkimmingSubmission.SkimmingInput
SkimmingParamsSubmission = ConfigSkimmingSubmission.SkimmingParamsSubmission
SkimmingSubmission = ConfigSkimmingSubmission.SkimmingSubmission
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Submission type of this submission is \"{SkimmingParamsSubmission.submission_type}\"")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Output type of this submission is \"{SkimmingParamsSubmission.output_type}\"")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Submission timestamp of this submission is \"{SkimmingSubmission.submission_timestamp}\"")

### define submission timestamp
collection_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Setting collection timestamp as \"{collection_timestamp}\"")

### collect name: {analysis_step}_ ({prefix}_) {data_type}_{data_label} (_{timestamp})
if SkimmingCollection.output_dir_prefix != "":
    collection_name = f"{analysis_step}_{SkimmingCollection.output_dir_prefix}_{SkimmingInput.data_type}_{SkimmingInput.data_label}"
else:
    collection_name = f"{analysis_step}_{SkimmingInput.data_type}_{SkimmingInput.data_label}"
if SkimmingCollection.output_dir_timestamp_suffix:
    collection_name += f"{collection_timestamp}"
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Setting collection name as \"{collection_name}\"")

### collection path, where all info about this data collection is stored
collection_path = os.path.join(constants.output_basepath, collection_name)
# make sure it did not exist before
if os.path.isdir(collection_path) and not SkimmingCollection.overwrite_output:
    console_utils.raise_exception(string=f"The config output subdirectory \"{collection_path}\" does already exist, and not allowed to overwrite")
elif os.path.isdir(collection_path) and SkimmingCollection.overwrite_output:
    console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The config output subdirectory \"{collection_path}\" does already exist, but allowed to overwrite. Attempting to delete old directory")
    _, _ = console_utils.run_command(bash_command=f"rm -rf {collection_path}")
# create dir
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Attempting to create config output subdirectory \"{collection_path}\"")
os.mkdir(collection_path)
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Prepared config output subdirectory at \"{collection_path}\"")

#=============================================================================
#====== OUTPUT_TYPE: AACHEN-NET
if SkimmingParamsSubmission.output_type == "aachen-net":

    #====== OUTPUT_SITE: 
    if SkimmingParamsSubmission.output_site == "":
    
        #====== SUBMISSION_TYPE: AACHEN-CONDOR
        if SkimmingParamsSubmission.submission_type == "aachen-condor":

            ########################
            ### prepare input

            ### derive condor output path
            output_path = os.path.join(SkimmingParamsSubmission.output_basepath, f"_submission_{SkimmingSubmission.submission_name}")

            ### obtain list of output files on storage
            console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Attempting to recursively list root files in CONDOR output path \"{output_path}\"")
            # ls grid files recursively
            input_file_list, input_total_size = file_utils.recursive_file_scan(basepath=output_path, ls_command="ls -l", file_suffix=".root", maxdepth=5, verbose=1)

            ### group together output files
            input_file_groups = file_utils.group_files(file_list=input_file_list, target_group_size=SkimmingCollection.hadd_file_size)

            ########################
            ### merge files

            ### prepare collection basepath
            collection_basepath = os.path.join(SkimmingCollection.output_basepath, collection_name)

            ### make sure output basepath exists
            if not os.path.isdir(SkimmingCollection.output_basepath):
                console_utils.raise_exception(string=f"The output base path \"{SkimmingCollection.output_basepath}\" does not exist")
            
            ### create collection basepath
            # make sure it did not exist before
            if os.path.isdir(collection_basepath) and not SkimmingCollection.overwrite_output:
                console_utils.raise_exception(string=f"The output subdirectory \"{collection_basepath}\" does already exist, and not allowed to overwrite")
            elif os.path.isdir(collection_basepath) and SkimmingCollection.overwrite_output:
                console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The output subdirectory \"{collection_basepath}\" does already exist, but allowed to overwrite. Attempting to delete old directory")
                _, _ = console_utils.run_command(bash_command=f"rm -rf {collection_basepath}")
            # create dir
            console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Attempting to create output subdirectory \"{collection_basepath}\"")
            os.mkdir(collection_basepath)
            # print
            console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Prepared output subdirectory at \"{collection_basepath}\"")

            ### generate hadd file paths from file groups
            collection_file_list = file_utils.hadd_names_from_file_groups(file_group_list=input_file_groups, hadd_basepath=collection_basepath, hadd_name_prefix=SkimmingCollection.hadd_file_prefix, verbose=1)

            ### actually perform hadd-ing of files
            collection_file_list = file_utils.run_hadd_commands(hadd_file_list=collection_file_list, check_exists=True, check_hadd_file_size=True, delete_source_files=SkimmingCollection.delete_source_files)

            ### actually perform hadd-ing of files
            # prepare remove command in case of requested source deletion
            rm_command = "rm -f"
            # perform hadding
            collection_file_list = file_utils.run_hadd_commands(hadd_file_list=collection_file_list, check_exists=True, check_hadd_file_size=True, delete_source_files=SkimmingCollection.delete_source_files, rm_command=rm_command)
            # remove top dir if desired
            if SkimmingCollection.delete_source_files:
                _, _ = console_utils.run_command(bash_command=f"{rm_command} {output_path}")

            ########################
            ### store output object

            ### prepare output object
            SkimmingOutput = config_utils.create_config(
                config_type="SkimmingOutput",
                replace_wildcards=True, verbose=1,
                **{
                    "collection_basepath": collection_basepath,
                    "collection_files": collection_file_list,
                    "collection_timestamp": collection_timestamp,
                    "collection_name": collection_name,
                }
            )
            ### prepare and store config file object
            collection_filename = "ConfigSkimmingOutput.yaml"
            collection_filepath = os.path.join(collection_path, collection_filename)
            ConfigSkimmingOutput = config_utils.create_config(
                config_type="ConfigSkimmingOutput",
                replace_wildcards=True, verbose=1,
                **{
                    "SkimmingInput": SkimmingInput,
                    "SkimmingParamsSubmission": SkimmingParamsSubmission,
                    "SkimmingSubmission": SkimmingSubmission,
                    "SkimmingCollection": SkimmingCollection,
                    "SkimmingOutput": SkimmingOutput,
                }
            )
            config_utils.store_config_file(filepath=collection_filepath, config=ConfigSkimmingOutput, config_type="ConfigSkimmingOutput", verbose=1)

        #======
        else:
            console_utils.raise_exception(string=f"Unsupported submission type \"{SkimmingParamsSubmission.submission_type}\"")
    #======
    else:
        console_utils.raise_exception(string=f"{console_utils.color.red}Unsupported output site \"{SkimmingParamsSubmission.output_site}\"")

#======
else:
    console_utils.raise_exception(string=f"{console_utils.color.red}Unsupported output type \"{SkimmingParamsSubmission.output_type}\"")
#=============================================================================

# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Finished the output collection")




#****************************
#############################

stop_time = time.time()
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The execution took \"{(stop_time - start_time):03f} seconds\"")
console_utils.print_console_footer()
