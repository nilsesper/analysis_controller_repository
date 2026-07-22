##################################
### ANALYSIS1 STEP: SUBMISSION ###
##################################

############################
### IMPORTS

import os
import argparse
from datetime import datetime
import time

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
    "--input",
    help=f"path to \"ConfigAnalysis1Input\" yaml file (str)",
    type=str,
    required=True,
)
parser.add_argument(
    "--paramssubmission",
    help=f"path to \"ConfigAnalysis1ParamsSubmission\" yaml file (str)",
    type=str,
    required=True,
)
# optional:
args = parser.parse_args()

#############################
#****************************
### MAIN PART

### import input config file
ConfigAnalysis1Input = config_utils.load_config_file(filepath=args.input, config_type="ConfigAnalysis1Input", replace_wildcards=True, verbose=1)
# extract config info
Analysis1Input = ConfigAnalysis1Input.Analysis1Input
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Data type of this submission is \"{Analysis1Input.data_type}\"")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Data label of this submission is \"{Analysis1Input.data_label}\"")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Data of this submission consists of \"{len(Analysis1Input.skimming_outputs)}\" individual skimming outputs")

### import params config file
ConfigAnalysis1ParamsSubmission = config_utils.load_config_file(filepath=args.paramssubmission, config_type="ConfigAnalysis1ParamsSubmission", replace_wildcards=True, verbose=1)
# extract config info
Analysis1ParamsSubmission = ConfigAnalysis1ParamsSubmission.Analysis1ParamsSubmission
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Analysis parameters of this submission are \"{Analysis1ParamsSubmission.params_analysis}\"")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Submission type of this submission is \"{Analysis1ParamsSubmission.submission_type}\"")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Output type of this submission is \"{Analysis1ParamsSubmission.output_type}\"")

### define submission timestamp
submission_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Setting submission timestamp as \"{submission_timestamp}\"")

### start submission
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Attempting to submit data")

### submit name
submission_name = f"{analysis_step}_{Analysis1Input.data_type}_{Analysis1Input.data_label}_{submission_timestamp}"

### submission path, where all info about this submission is stored
submission_path = os.path.join(constants.submission_basepath, submission_name)
# create submit path
os.mkdir(submission_path)
# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Prepared submission directory at \"{submission_path}\"")

#=============================================================================
#== SUBMISSION_TYPE: AACHEN-CONDOR  &&  OUTPUT_TYPE: AACHEN-NET
if Analysis1ParamsSubmission.submission_type == "aachen-condor" and Analysis1ParamsSubmission.output_type == "aachen-net":

    ### prepare variables
    crab_requestname = submission_name

    ### prepare collection basepath
    output_basepath = os.path.join(Analysis1ParamsSubmission.output_basepath, f"_submission_{submission_name}")

    ### create output basepath
    # make sure it did not exist before
    if os.path.isdir(output_basepath):
        console_utils.raise_exception(string=f"The output subdirectory \"{output_basepath}\" does already exist")
    # create dir
    console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Attempting to create output subdirectory \"{output_basepath}\"")
    os.mkdir(output_basepath)

    ### locate input files, determine output file paths and prepare submission list
    submission_list = [] # [(executable, innputfile, outputfile, paramsfile)]

    ### determine executable path
    executable = os.path.join(_ANALYSIS_CONTROLLER_REPO_PATH, "scripts_analysis/analysis1/run_analysis1_data.sh")

    # loop over all input collections
    n_skimming = len(Analysis1Input.skimming_outputs)
    console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Collecting information about all individual skimming output collections for this submission dataset")
    for i_skimming in range(n_skimming):
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Collecting information about skimming output collection \"{(i_skimming+1):,} / {n_skimming:,} = {((i_skimming+1)/n_skimming if n_skimming > 0 else 0)*100:.3f} %\"")
        ### locate skimming output config file
        skimming_output_config_file = Analysis1Input.skimming_outputs[i_skimming].skimming_output_config

        ### import skimming output config file
        ConfigSkimmingOutput = config_utils.load_config_file(filepath=skimming_output_config_file, config_type="ConfigSkimmingOutput", replace_wildcards=True, verbose=1)
        ### extract config info
        SkimmingInput = ConfigSkimmingOutput.SkimmingInput
        SkimmingParamsSubmission = ConfigSkimmingOutput.SkimmingParamsSubmission
        SkimmingCollection = ConfigSkimmingOutput.SkimmingCollection
        SkimmingSubmission = ConfigSkimmingOutput.SkimmingSubmission
        SkimmingOutput = ConfigSkimmingOutput.SkimmingOutput
        # print
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Skimming output \"{(i_skimming+1):,}\" is type \"{SkimmingInput.data_type}\"")
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Skimming output \"{(i_skimming+1):,}\" has label \"{SkimmingInput.data_label}\"")
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Skimming output \"{(i_skimming+1):,}\" has skimming submission name \"{SkimmingSubmission.submission_timestamp}\"")
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Skimming output \"{(i_skimming+1):,}\" has skimming collection name \"{SkimmingOutput.collection_name}\"")

        ### prepare submission parameters
        # determine output file suffix
        #   desired file naming: {SkimmingOutput.collection_name}_{i_file}.root
        paramsfile = Analysis1ParamsSubmission.params_analysis
        outfile_prefix = f"skimming_{SkimmingOutput.collection_name}"
        # determine inputfile and outputfile paths
        n_files = len(SkimmingOutput.collection_files)
        for i_file in range(n_files):
            # inputfile path
            infile = SkimmingOutput.collection_files[i_file].path
            # outputfile path
            outfile = os.path.join(output_basepath, f"{outfile_prefix}_{i_file}.root")
            # add to submission_list
            submission_list.append( (executable, infile, outfile, paramsfile) )
    # print
    console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Finished collecting information about all individual skimming output collections for this submission dataset")
    n_jobs = len(submission_list)
    console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"In total \"{n_jobs}\" jobs are foreseen for this submission")

    ### prepare condor work area
    condor_workarea = os.path.join(submission_path, "condor_project")
    os.mkdir(condor_workarea)

    ### prepare condor job list csv file from created submission list
    job_list_filename = f"CondorJobList.csv"
    job_list_filepath = os.path.join(condor_workarea, job_list_filename)
    # prepare csv file content
    job_list_str = ""
    for i_job in range(n_jobs):
        n_cols = len(submission_list[i_job])
        for i_col in range(n_cols):
            job_list_str += f"{submission_list[i_job][i_col]}"
            if i_col < n_cols-1:
                job_list_str += ","
        if i_job < n_jobs-1:
            job_list_str += "\n"
    # write csv file
    file_utils.store_local_file(filepath=job_list_filepath, new_content=job_list_str)

    ### prepare condor exec file
    # copy condor exec template file to submitpath
    condor_executable_config_filename = f"condor_exec.sh"
    condor_executable_config_filepath = os.path.join(condor_workarea, condor_executable_config_filename)
    # copy template file
    _, _ = console_utils.run_command(bash_command=f'cp {Analysis1ParamsSubmission.condor_executable_template_filepath} {condor_executable_config_filepath}\n')
    # prepare wildcards
    condor_submission_config_wildcards = {

    }
    # open template, and replace wildcards
    content = file_utils.load_local_file(filepath=condor_executable_config_filepath)
    new_content = file_utils.replace_wildcards_if_possible(content=content, wildcards=condor_submission_config_wildcards)
    file_utils.store_local_file(filepath=condor_executable_config_filepath, new_content=new_content)
    # print
    console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Prepared condor executable file at \"{condor_executable_config_filepath}\", based on template file \"{Analysis1ParamsSubmission.condor_executable_template_filepath}\"")

    ### prepare condor submit file
    # copy condor submit template file to submitpath
    condor_submission_config_filename = f"condor_submit.sub"
    condor_submission_config_filepath = os.path.join(condor_workarea, condor_submission_config_filename)
    # determine default parameters
    condor_request_cpus = "1"
    condor_request_memory = "4G"
    condor_request_disk = "1G"
    # update parameters from submission parameters, if not empty
    if Analysis1ParamsSubmission.condor_request_cpus != "":
        condor_request_cpus = Analysis1ParamsSubmission.condor_request_cpus
    if Analysis1ParamsSubmission.condor_request_memory != "":
        condor_request_memory = Analysis1ParamsSubmission.condor_request_memory
    if Analysis1ParamsSubmission.condor_request_disk != "":
        condor_request_disk = Analysis1ParamsSubmission.condor_request_disk
    # copy template file
    _, _ = console_utils.run_command(bash_command=f'cp {Analysis1ParamsSubmission.condor_submission_config_template_filepath} {condor_submission_config_filepath}\n')
    # prepare wildcards
    condor_submission_config_wildcards = {
        "++++EXECUTABLE++++": condor_executable_config_filepath,
        "++++REQUEST_CPUS++++": condor_request_cpus,
        "++++REQUEST_MEMORY++++": condor_request_memory,
        "++++REQUEST_DISK++++": condor_request_disk,
        "++++JOB_LIST_FILE++++": job_list_filename,
    }
    # open template, and replace wildcards
    content = file_utils.load_local_file(filepath=condor_submission_config_filepath)
    new_content = file_utils.replace_wildcards_if_possible(content=content, wildcards=condor_submission_config_wildcards)
    file_utils.store_local_file(filepath=condor_submission_config_filepath, new_content=new_content)
    # print
    console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Prepared condor submission config file at \"{condor_submission_config_filepath}\", based on template file \"{Analysis1ParamsSubmission.condor_submission_config_template_filepath}\"")

    ### finally: submit to condor
    console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Attempting to submit to CONDOR, using the CONDOR workarea \"{condor_workarea}\"")
    bash_commands = f''
    bash_commands += f'\n'
    # cd into condor workarea
    bash_commands += f'cd {condor_workarea}\n'
    # condor submit command
    bash_commands += f'condor_submit {condor_submission_config_filepath}\n'
    # execute commands
    _, cmdout = console_utils.run_command(bash_command=bash_commands)

    ### extract cluster id
    condor_cluster_id = "none"
    if "submitted to cluster" in cmdout:
        tmp_str = cmdout.split("submitted to cluster")[-1]
        tmp_str = tmp_str.replace(".","").replace(" ","").replace("\n","")
        condor_cluster_id = tmp_str
    console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"CONDOR submission succeeded with ClusterId \"{condor_cluster_id}\"")

    ### prepare list of submitted data: input and output files
    # submission_list = [(executable, innputfile, outputfile, paramsfile)]
    submitted_jobs = [{
        "input": submission_list[i_job][1],
        "output": submission_list[i_job][2],
    } for i_job in range(n_jobs)]

    ### prepare submission object
    Analysis1Submission = config_utils.create_config(
        config_type="Analysis1Submission",
        replace_wildcards=True, verbose=1,
        **{
            "submission_name": submission_name,
            "submission_path": submission_path,
            "submission_timestamp": submission_timestamp,

            "condor_submission_config_filepath": condor_submission_config_filepath,
            "condor_executable_filepath": condor_executable_config_filepath,
            "condor_workarea": condor_workarea,
            "condor_cluster_id": condor_cluster_id,

            "executable": executable,

            "submitted_jobs": submitted_jobs,
        }
    )
    ### prepare and store config file object
    submission_filename = "ConfigAnalysis1Submission.yaml"
    submission_filepath = os.path.join(submission_path, submission_filename)
    ConfigAnalysis1Submission = config_utils.create_config(
        config_type="ConfigAnalysis1Submission",
        replace_wildcards=True, verbose=1,
        **{
            "Analysis1Input": Analysis1Input,
            "Analysis1ParamsSubmission": Analysis1ParamsSubmission,
            "Analysis1Submission": Analysis1Submission,
        }
    )
    config_utils.store_config_file(filepath=submission_filepath, config=ConfigAnalysis1Submission, config_type="ConfigAnalysis1Submission", verbose=1)
    #"""

#======
else:
    console_utils.raise_exception(string=f"Unsupported combination of submission type \"{Analysis1ParamsSubmission.submission_type}\" and output type \"{Analysis1ParamsSubmission.output_type}\"")
#=============================================================================

# print
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Finished submitting the data union")

#****************************
#############################

stop_time = time.time()
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The execution took \"{(stop_time - start_time):03f} seconds\"")
console_utils.print_console_footer()
