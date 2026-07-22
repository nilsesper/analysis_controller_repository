#########################################
### ANALYSIS1 STEP: OUTPUT COLLECTION ###
#########################################

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
analysis_step = "analysis1"
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Analysis step is \"{analysis_step}\"")

#############################
### ARGUMENT PARSER

parser = argparse.ArgumentParser()
# mandatory:
parser.add_argument(
    "--collection",
    help="path to \"ConfigAnalysis1Collection\" yaml file (str)",
    type=str,
    required=True,
)
parser.add_argument(
    "--submission",
    help="path to \"ConfigAnalysis1Submission\" yaml file (str)",
    type=str,
    required=True,
)
# optional:
args = parser.parse_args()

#############################
#****************************
### MAIN PART

### import collection config file
ConfigAnalysis1Collection = config_utils.load_config_file(filepath=args.collection, config_type="ConfigAnalysis1Collection", replace_wildcards=True, verbose=1)
# extract config info
Analysis1Collection = ConfigAnalysis1Collection.Analysis1Collection
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Output type of this collection is \"{Analysis1Collection.output_type}\"")

### import submission config file
ConfigAnalysis1Submission = config_utils.load_config_file(filepath=args.submission, config_type="ConfigAnalysis1Submission", replace_wildcards=True, verbose=1)
# extract config info
Analysis1Input = ConfigAnalysis1Submission.Analysis1Input
Analysis1ParamsSubmission = ConfigAnalysis1Submission.Analysis1ParamsSubmission
Analysis1Submission = ConfigAnalysis1Submission.Analysis1Submission
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Submission type of this submission is \"{Analysis1ParamsSubmission.submission_type}\"")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Output type of this submission is \"{Analysis1ParamsSubmission.output_type}\"")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Submission timestamp of this submission is \"{Analysis1Submission.submission_timestamp}\"")

### define submission timestamp
collection_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Setting collection timestamp as \"{collection_timestamp}\"")

### collect name: {analysis_step}_ ({prefix}_) {data_type}_{data_label} (_{timestamp})
if Analysis1Collection.output_dir_prefix != "":
    collection_name = f"{analysis_step}_{Analysis1Collection.output_dir_prefix}_{Analysis1Input.data_type}_{Analysis1Input.data_label}"
else:
    collection_name = f"{analysis_step}_{Analysis1Input.data_type}_{Analysis1Input.data_label}"
if Analysis1Collection.output_dir_timestamp_suffix:
    collection_name += f"{collection_timestamp}"
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Setting collection name as \"{collection_name}\"")

### collection path, where all info about this data collection is stored
collection_path = os.path.join(constants.output_basepath, collection_name)
# make sure it did not exist before
if os.path.isdir(collection_path) and not Analysis1Collection.overwrite_output:
    console_utils.raise_exception(string=f"The config output subdirectory \"{collection_path}\" does already exist, and not allowed to overwrite")
elif os.path.isdir(collection_path) and Analysis1Collection.overwrite_output:
    console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The config output subdirectory \"{collection_path}\" does already exist, but allowed to overwrite. Attempting to delete old directory")
    _, _ = console_utils.run_command(bash_command=f"rm -rf {collection_path}")
# create dir
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Attempting to create config output subdirectory \"{collection_path}\"")
os.mkdir(collection_path)
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Prepared config output subdirectory at \"{collection_path}\"")

#=============================================================================
#====== OUTPUT_TYPE: AACHEN-NET
if Analysis1ParamsSubmission.output_type == "aachen-net":

    #====== OUTPUT_SITE: 
    if Analysis1ParamsSubmission.output_site == "":
    
        #====== SUBMISSION_TYPE: AACHEN-CONDOR
        if Analysis1ParamsSubmission.submission_type == "aachen-condor":

            ########################
            ### prepare input

            ### derive condor output path
            output_path = os.path.join(Analysis1ParamsSubmission.output_basepath, f"_submission_{Analysis1Submission.submission_name}")

            ### obtain list of output files on storage
            console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Attempting to recursively list root files in CONDOR output path \"{output_path}\"")
            # ls grid files recursively
            input_file_list, input_total_size = file_utils.recursive_file_scan(basepath=output_path, ls_command="ls -l", file_suffix=".root", maxdepth=5, verbose=1)

            ### group together output files
            input_file_groups = file_utils.group_files(file_list=input_file_list, target_group_size=Analysis1Collection.hadd_file_size)

            ########################
            ### merge files

            ### prepare collection basepath
            collection_basepath = os.path.join(Analysis1Collection.output_basepath, collection_name)

            ### make sure output basepath exists
            if not os.path.isdir(Analysis1Collection.output_basepath):
                console_utils.raise_exception(string=f"The output base path \"{Analysis1Collection.output_basepath}\" does not exist")
            
            ### create collection basepath
            # make sure it did not exist before
            if os.path.isdir(collection_basepath) and not Analysis1Collection.overwrite_output:
                console_utils.raise_exception(string=f"The output subdirectory \"{collection_basepath}\" does already exist, and not allowed to overwrite")
            elif os.path.isdir(collection_basepath) and Analysis1Collection.overwrite_output:
                console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The output subdirectory \"{collection_basepath}\" does already exist, but allowed to overwrite. Attempting to delete old directory")
                _, _ = console_utils.run_command(bash_command=f"rm -rf {collection_basepath}")
            # create dir
            console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Attempting to create output subdirectory \"{collection_basepath}\"")
            os.mkdir(collection_basepath)
            # print
            console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Prepared output subdirectory at \"{collection_basepath}\"")

            ### generate hadd file paths from file groups
            collection_file_list = file_utils.hadd_names_from_file_groups(file_group_list=input_file_groups, hadd_basepath=collection_basepath, hadd_name_prefix=Analysis1Collection.hadd_file_prefix, verbose=1)

            ### actually perform hadd-ing of files
            # prepare remove command in case of requested source deletion
            rm_command = "rm -f"
            # perform hadding
            check_hadd_file_size = False # it seems to give problems when those root files with the hists and the folder structure...
            collection_file_list = file_utils.run_hadd_commands(hadd_file_list=collection_file_list, check_exists=True, check_hadd_file_size=check_hadd_file_size, delete_source_files=Analysis1Collection.delete_source_files, rm_command=rm_command, verbose=2)
            # remove top dir if desired
            rm_command = "rm -rf"
            if Analysis1Collection.delete_source_files:
                console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Removing output subdirectory \"{collection_basepath}\"")
                _, _ = console_utils.run_command(bash_command=f"{rm_command} {output_path}")

            ########################
            ### store output object

            ### prepare output object
            Analysis1Output = config_utils.create_config(
                config_type="Analysis1Output",
                replace_wildcards=True, verbose=1,
                **{
                    "collection_basepath": collection_basepath,
                    "collection_files": collection_file_list,
                    "collection_timestamp": collection_timestamp,
                    "collection_name": collection_name,
                }
            )
            ### prepare and store config file object
            collection_filename = "ConfigAnalysis1Output.yaml"
            collection_filepath = os.path.join(collection_path, collection_filename)
            ConfigAnalysis1Output = config_utils.create_config(
                config_type="ConfigAnalysis1Output",
                replace_wildcards=True, verbose=1,
                **{
                    "Analysis1Input": Analysis1Input,
                    "Analysis1ParamsSubmission": Analysis1ParamsSubmission,
                    "Analysis1Submission": Analysis1Submission,
                    "Analysis1Collection": Analysis1Collection,
                    "Analysis1Output": Analysis1Output,
                }
            )
            config_utils.store_config_file(filepath=collection_filepath, config=ConfigAnalysis1Output, config_type="ConfigAnalysis1Output", verbose=1)

        #======
        else:
            console_utils.raise_exception(string=f"Unsupported submission type \"{Analysis1ParamsSubmission.submission_type}\"")
    #======
    else:
        console_utils.raise_exception(string=f"{console_utils.color.red}Unsupported output site \"{Analysis1ParamsSubmission.output_site}\"")

#======
else:
    console_utils.raise_exception(string=f"{console_utils.color.red}Unsupported output type \"{Analysis1ParamsSubmission.output_type}\"")
#=============================================================================

# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Finished the output collection")




#****************************
#############################

stop_time = time.time()
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The execution took \"{(stop_time - start_time):03f} seconds\"")
console_utils.print_console_footer()
