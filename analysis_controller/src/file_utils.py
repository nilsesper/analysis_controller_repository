#############################
### CONFIG FILE UTILITIES ###
#############################

############################
### IMPORTS

import os
import sys
import yaml

from analysis_controller.src import path_utils
from analysis_controller.src import console_utils 
from analysis_controller.src import cosmetic_utils

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_REPOPATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)

############################
### HELPER FUNCTIONS & CLASSES (with prefix "_")

### check for required and optional keys in dictionary
# check if all required_keys are in dict
# check if no other keys than required_keys + optional_keys are in dict
# specify dictionary_type string for more conclusive error messages
def _check_for_dict_keys(*, dictionary, dictionary_name="", required_keys=[], optional_keys=[]):
    err_list = []
    dict_keys = dictionary.keys()
    allowed_keys = list(required_keys)+list(optional_keys)
    for key in required_keys:
        if key not in dict_keys:
            err_list.append(f"{console_utils.color.red}A \"{dictionary_name}\" dictionary did not include the required key \"{key}\".{console_utils.color.reset}")
    for key in dict_keys:
        if key not in allowed_keys:
            err_list.append(f"{console_utils.color.red}A \"{dictionary_name}\" dictionary did include the unexpected key \"{key}\".{console_utils.color.reset}")
    if len(err_list)>0:
        err_str = ""
        for err in err_list:
            err_str += f"{err}\n"
        err_str += f"{console_utils.color.yellow}INFO: One expects the following keys for a \"{dictionary_name}\" dictionary:  required = {required_keys}  --  optional = {optional_keys}.{console_utils.color.reset}"
        raise Exception(err_str)

### check if value in list of allowed values
def _check_allowed_value(*, value, value_name="", allowed_values=[]):
    if value not in allowed_values:
        raise Exception(f"{console_utils.color.red}Parameter \"{value_name}\" must be in {allowed_values}, and not have the value \"{value}\"{console_utils.color.reset}")

### bool check value type (true if same value)
# value_type can be = int, str, list, float
# for custom classes use value_type = __main__.CLASSNAME
def _bool_check_value_type(*, value, value_type):
    _value_type = f"<class '{value_type}'>"
    if f"{type(value)}" != _value_type:
        return False
    return True

### check type of python object
def _check_value_type(*, value, value_name="", value_type):
    if _bool_check_value_type(value=value, value_type=value_type) == False:
        _value_type = f"<class '{value_type}'>"
        raise Exception(f"{console_utils.color.red}Parameter \"{value_name}\" must be of type \"{_value_type}\", and not have the type \"{type(value)}\"{console_utils.color.reset}")

### replace wildcard if possible
def _replace_wildcard_if_possible(*, value):
    new_value = value
    if _bool_check_value_type(value=value, value_type="str"):
        wildcards = {
            r"%%%ANALYSIS_CONTROLLER%%%": _ANALYSIS_CONTROLLER_REPOPATH,
        }
        for wildcard, wildcard_replacement in wildcards.items():
            new_value = new_value.replace(wildcard, wildcard_replacement)
    return new_value

############################
### MAIN FUNCTIONS & CLASSES

### load file
def load_file(*, filepath):
    if not os.path.isfile(filepath):
        raise Exception(f"{console_utils.color.red} Could not find the file \"{filepath}\" {console_utils.color.reset}")
    with open(filepath, "r") as file:
        content = str(file.read())
    return content

### store file
def store_file(*, filepath, new_content):
    with open(filepath, "w") as file:
        file.write(new_content)

### replace wildcards in file if possible
# content: one large string as file content
# wildcards: {wildcard: meaning}
def replace_wildcards_if_possible(*, content, wildcards):
    new_content = content
    for wildcard, wildcard_replacement in wildcards.items():
        new_content = new_content.replace(wildcard, wildcard_replacement)
    return new_content

### load yaml file
def load_yaml_file(*, filepath):
    if not os.path.isfile(filepath):
        raise Exception(f"{console_utils.color.red} Could not find the file \"{filepath}\" {console_utils.color.reset}")
    with open(filepath, "r") as file:
        yaml_content = yaml.safe_load(file)
    return yaml_content

### store yaml file
def store_yaml_file(*, filepath, yaml_content):
    content = yaml.safe_dump(yaml_content)
    with open(filepath, "w") as file:
        file.write(content)

### load yaml config, and check whether it is conform for the specified type of config file (check keys and structure)
def load_config(*, filepath, config_type, verbose=1):
    ### make abspath
    filepath = os.path.abspath(filepath)
    ### print statement
    if verbose >= 1:
        cosmetic_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_RELATIVE_FILEPATH} {sys._getframe().f_code.co_name}()", string=f"Attempting to import config file of type \"{config_type}\" from path \"{filepath}\"")
    ### load yaml contents
    config = load_yaml_file(filepath=filepath)
    #--------------------------------------------------
    ### rekbmtf_input ----------------------------
    if config_type == "rekbmtf_input":
        _check_for_dict_keys(
            dictionary=config,
            dictionary_name=f"Configuration file \"{config_type}\": Top-level",
            required_keys=[
                "rekbmtf_input",
            ],
            optional_keys=[],
        )
        _check_value_type(
            value=config["rekbmtf_input"],
            value_name=f"Configuration file \"{config_type}\": rekbmtf_input",
            value_type="list",
        )
        data_labels = []
        for i in range(len(config["rekbmtf_input"])):
            _check_for_dict_keys(
                dictionary=config["rekbmtf_input"][i],
                dictionary_name=f"Configuration file \"{config_type}\": rekbmtf_input[{i}]",
                required_keys=[
                    "data_type",
                    "data_label",
                    "input_das_name",
                    "input_lumi_mask"
                ],
                optional_keys=[],
            )
            # check unique data label
            data_label = config["rekbmtf_input"][i]["data_label"]
            if data_label not in data_labels:
                data_labels.append(data_label)
            else:
                raise Exception(f"{console_utils.color.red}Parameter \"data_label\" must be unique. The value \"{data_label}\" was found twice.{console_utils.color.reset}")
        # remove highest level hierarchy
        config = config["rekbmtf_input"]
    ### rekbmtf_params ----------------------------
    elif config_type == "rekbmtf_params":
        _check_for_dict_keys(
            dictionary=config,
            dictionary_name=f"Configuration file \"{config_type}\": Top-level",
            required_keys=[
                "rekbmtf_params"
            ],
            optional_keys=[],
        )
        _check_value_type(
            value=config["rekbmtf_params"],
            value_name=f"Configuration file \"{config_type}\": rekbmtf_params",
            value_type="dict",
        )
        _check_for_dict_keys(
            dictionary=config[
                "rekbmtf_params"
            ],
            dictionary_name=f"Configuration file \"{config_type}\": rekbmtf_params",
            required_keys=["data"],
            optional_keys=[],
        )
        for data_type in config["rekbmtf_params"].keys():
            _check_for_dict_keys(
                dictionary=config["rekbmtf_params"][data_type],
                dictionary_name=f"Configuration file \"{config_type}\": rekbmtf_input[\"{data_type}\"]",
                required_keys=[
                    "submission_type",
                    "submission_splitting",

                    "output_type",
                    "output_site",
                    "output_basepath",

                    "cmssw_src_path",

                    "crab_config_template_filepath",
                    "cmssw_config_template_filepath",
                ],
                optional_keys=[],
            )
            # replace wildcards
            config["rekbmtf_params"][data_type]["output_basepath"] = _replace_wildcard_if_possible( value=config["rekbmtf_params"][data_type]["output_basepath"] )
            config["rekbmtf_params"][data_type]["crab_config_template_filepath"] = os.path.abspath(_replace_wildcard_if_possible( value=config["rekbmtf_params"][data_type]["crab_config_template_filepath"] ))
            config["rekbmtf_params"][data_type]["cmssw_src_path"] = os.path.abspath(_replace_wildcard_if_possible( value=config["rekbmtf_params"][data_type]["cmssw_src_path"] ))
            config["rekbmtf_params"][data_type]["cmssw_config_template_filepath"] = os.path.abspath(_replace_wildcard_if_possible( value=config["rekbmtf_params"][data_type]["cmssw_config_template_filepath"] ))
            # check whether specified files and dirs exist

        # remove highest level hierarchy
        config = config["rekbmtf_params"]
    ### rekbmtf_submission ----------------------------
    elif config_type == "rekbmtf_submission":
        _check_for_dict_keys(
            dictionary=config,
            dictionary_name=f"Configuration file \"{config_type}\": Top-level",
            required_keys=[
                "rekbmtf_submission"
            ],
            optional_keys=[],
        )
        _check_value_type(
            value=config["rekbmtf_submission"],
            value_name=f"Configuration file \"{config_type}\": rekbmtf_submission",
            value_type="dict",
        )
        _check_for_dict_keys(
            dictionary=config["rekbmtf_submission"],
            dictionary_name=f"Configuration file \"{config_type}\": rekbmtf_submission",
            required_keys=[
                "data_type",
                "data_label",
                "input_das_name",
                "input_lumi_mask",

                "submission_type",
                "submission_splitting",

                "cmssw_src_path",

                "cmssw_config_filepath",
                "crab_config_filepath",

                "crab_requestname",
                "crab_workarea",

                "output_type",
                "output_site",
                "output_basepath",

                "submit_name",
                "submit_path",
                "submit_timestamp",
            ],
            optional_keys=[],
        )
        # check whether specified files and dirs exist
        
        # remove highest level hierarchy
        config = config["rekbmtf_submission"]
    #--------------------------------------------------
    else:
        raise Exception(f"{console_utils.color.red}Undefined config_type \"{config_type}\"{console_utils.color.reset}")
    ### print statement
    if verbose >= 1:
        cosmetic_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_RELATIVE_FILEPATH} {sys._getframe().f_code.co_name}()", string=f"Successfully config file of type \"{config_type}\" from path \"{filepath}\"")
    ### return config file
    return config


