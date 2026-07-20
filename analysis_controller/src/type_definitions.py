###########################
### CONFIGURATION UTILS ###
###########################

############################
### IMPORTS

import os
import attridict

from analysis_controller.src import path_utils

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_PATH, _ANALYSIS_CONTROLLER_REPO_PATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)

############################
### TYPE DEFINTITIONS

###### blueprints

PythonTypes = {
    "*none*": type(None),
    "*bool*": type(True),
    "*int*": type(0),
    "*float*": type(0.0),
    "*str*": type(""),
    "*dict*": type({}),
    "*list*": type([]),
    "*attridict*": attridict.AttriDict,
}
PythonTypeNames = list(PythonTypes.keys())

DictBlueprints = {
    #########################
    ### *** lower-level dicts (part of info dicts) ***
    "_LsFile": {
        "path": "*str*",
        "size": "*int*",
    },
    "_CollectionFileGroup": {
        "input_files": "*list*::_LsFile",
        "input_size": "*int*",
        "path": "*str*",
        "size": "*int*",
    },
    "_RekbmtfOutputItem": {
        "data_label": "*str*",
        "rekbmtf_output_config": "*str*",
    },
    "_JobInOutInfo": {
        "input": "*str*",
        "output": "*str*"
    },
    "_HistParams": {
        "hist_name": "*str*",
        "edge_type": "*str*",
        "edges": "*list*::*float*",
    },
    #########################
    ### *** scripts_controller configuration files ***
    ### info dicts (part of config file dicts)
    #--- rekbmtf
    "RekbmtfInput": {
        "data_type": "*str*",
        "data_label": "*str*",

        "input_das_name": "*str*",
        "input_lumi_mask": "*str*",
        "input_run_range": "*str*",
    },
    "RekbmtfParamsSubmission": {
        "submission_type": "*str*",
        "submission_splitting": "*str*",

        "output_type": "*str*",
        "output_site": "*str*",
        "output_basepath": "*str*",

        "cmssw_src_path": "*str*",

        "crab_config_template_filepath": "*str*",
        "cmssw_config_template_filepath": "*str*",
    },
    "RekbmtfSubmission": {
        "submission_name": "*str*",
        "submission_path": "*str*",
        "submission_timestamp": "*str*",

        "cmssw_config_filepath": "*str*",
        "crab_config_filepath": "*str*",
        "crab_requestname": "*str*",
        "crab_workarea": "*str*",
    },
    "RekbmtfCollection": {
        "hadd_file_size": "*str*",
        "hadd_file_prefix": "*str*",

        "output_type": "*str*",
        "output_site": "*str*",
        "output_basepath": "*str*",

        "output_dir_prefix": "*str*",
        "output_dir_timestamp_suffix": "*bool*",
        "overwrite_output": "*bool*",

        "delete_source_files": "*bool*",
    },
    "RekbmtfOutput": {
        "collection_basepath": "*str*",
        "collection_files": "*list*::_CollectionFileGroup",
        "collection_timestamp": "*str*",
        "collection_name": "*str*",
    },
    #--- skimming
    "SkimmingInput": {
        "data_type": "*str*",
        "data_label": "*str*", 

        "rekbmtf_outputs": "*list*::_RekbmtfOutputItem",
    },
    "SkimmingParamsSubmission": {
        "submission_type": "*str*",
        "submission_splitting": "*str*",

        "output_type": "*str*",
        "output_site": "*str*",
        "output_basepath": "*str*",

        "params_analysis": "*str*",

        "condor_request_cpus": "*str*",
        "condor_request_memory": "*str*",
        "condor_request_disk": "*str*",

        "condor_submission_config_template_filepath": "*str*",
        "condor_executable_template_filepath": "*str*",
    },
    "SkimmingSubmission": {
        "submission_name": "*str*",
        "submission_path": "*str*",
        "submission_timestamp": "*str*",

        "condor_submission_config_filepath": "*str*",
        "condor_executable_filepath": "*str*",
        "condor_workarea": "*str*",
        "condor_cluster_id": "*str*",

        "executable": "*str*",

        "submitted_jobs": "*list*::_JobInOutInfo",
    },
    "SkimmingCollection": {
        "hadd_file_size": "*str*",
        "hadd_file_prefix": "*str*",

        "output_type": "*str*",
        "output_site": "*str*",
        "output_basepath": "*str*",

        "output_dir_prefix": "*str*",
        "output_dir_timestamp_suffix": "*bool*",
        "overwrite_output": "*bool*",

        "delete_source_files": "*bool*",
    },
    "SkimmingOutput": {
        "collection_basepath": "*str*",
        "collection_files": "*list*::_CollectionFileGroup",
        "collection_timestamp": "*str*",
        "collection_name": "*str*",
    },
    ### configuration file dicts
    #--- rekbmtf
    "ConfigRekbmtfInput": {
        "RekbmtfInput": "*dict*::RekbmtfInput",
    },
    "ConfigRekbmtfParamsSubmission": {
        "RekbmtfParamsSubmission": "*dict*::RekbmtfParamsSubmission",
    },
    "ConfigRekbmtfSubmission": {
        "RekbmtfInput": "*dict*::RekbmtfInput",
        "RekbmtfParamsSubmission": "*dict*::RekbmtfParamsSubmission",
        "RekbmtfSubmission": "*dict*::RekbmtfSubmission",
    },
    "ConfigRekbmtfCollection": {
        "RekbmtfCollection": "*dict*::RekbmtfCollection",
    },
    "ConfigRekbmtfOutput": {
        "RekbmtfInput": "*dict*::RekbmtfInput",
        "RekbmtfParamsSubmission": "*dict*::RekbmtfParamsSubmission",
        "RekbmtfSubmission": "*dict*::RekbmtfSubmission",
        "RekbmtfCollection": "*dict*::RekbmtfCollection",
        "RekbmtfOutput": "*dict*::RekbmtfOutput",
    },
    #--- skimming
    "ConfigSkimmingInput": {
        "SkimmingInput": "*dict*::SkimmingInput",
    },
    "ConfigSkimmingParamsSubmission": {
        "SkimmingParamsSubmission": "*dict*::SkimmingParamsSubmission",
    },
    "ConfigSkimmingSubmission": {
        "SkimmingInput": "*dict*::SkimmingInput",
        "SkimmingParamsSubmission": "*dict*::SkimmingParamsSubmission",
        "SkimmingSubmission": "*dict*::SkimmingSubmission",
    },
    "ConfigSkimmingCollection": {
        "SkimmingCollection": "*dict*::SkimmingCollection",
    },
    "ConfigSkimmingOutput": {
        "SkimmingInput": "*dict*::SkimmingInput",
        "SkimmingParamsSubmission": "*dict*::SkimmingParamsSubmission",
        "SkimmingSubmission": "*dict*::SkimmingSubmission",
        "SkimmingCollection": "*dict*::SkimmingCollection",
        "SkimmingOutput": "*dict*::SkimmingOutput",
    },
    #########################
    ### scripts_analysis configuration files
    #--- rekbmtf
    #
    #--- skimming
    "SkimmingParamsAnalysis": {
        "muon_mass": "*float*",
        "evaluate_gen_cols": "*bool*",
        "evaluate_filling_scheme": "*bool*",
        "delta_r_max_for_track_l1mu_match": "*float*",
        "delta_r_min_distance_between_tracks": "*float*",
        "bx_interval_earlier_colliding": "*int*",
        "run_to_lhcscheme": "*dict*::*int*::*str*",
        "lhcscheme_to_filledbx": "*dict*::*str*::*list*::*int*",
    },
    #--- analysis1
    "Analysis1ParamsAnalysis": {
        "muon_mass": "*float*",
        "eventloop_iteration_size": "*str*",
        "col_hists": "*list*::_HistParams",
        "ana_hists": "*list*::_HistParams",
    },
}


