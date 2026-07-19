###########################
### CONFIGURATION UTILS ###
###########################

############################
### IMPORTS

import os
import sys
import attridict

from analysis_controller.src import path_utils
from analysis_controller.src import file_utils
from analysis_controller.src import console_utils
from analysis_controller.src import type_utils
from analysis_controller.src import type_definitions

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_PATH, _ANALYSIS_CONTROLLER_REPO_PATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)

############################
### HELPER FUNCTIONS & CLASSES (with prefix "_")

### replace wildcard in str if possible
def _replace_wildcard_if_possible(*, value):
    new_value = value
    wildcards = {
        f"++++ANALYSIS_CONTROLLER_PATH++++": _ANALYSIS_CONTROLLER_PATH,
        f"++++ANALYSIS_CONTROLLER_REPO_PATH++++": _ANALYSIS_CONTROLLER_REPO_PATH,
    }
    for wildcard, wildcard_replacement in wildcards.items():
        new_value = new_value.replace(wildcard, wildcard_replacement)
    return new_value

### replace wildcards in dictionary
def replace_wildcards_dict_recursive(*, dictionary):
    if type(dictionary) != type_utils.type_definitions.PythonTypes["*dict*"] and type(dictionary) != type_definitions.PythonTypes["*attridict*"]:
        return dictionary
    for k in dictionary.keys():
        if type(dictionary[k]) == type_definitions.PythonTypes["*str*"]:
            dictionary[k] = _replace_wildcard_if_possible(value=dictionary[k])
        elif type(dictionary[k]) == type_definitions.PythonTypes["*dict*"] or type(dictionary[k]) == type_definitions.PythonTypes["*attridict*"]:
            dictionary[k] = replace_wildcards_dict_recursive(dictionary=dictionary[k])
        elif type(dictionary[k]) == type_definitions.PythonTypes["*list*"]: # assume list of dicts
            for i in range(len(dictionary[k])):
                dictionary[k][i] = replace_wildcards_dict_recursive(dictionary=dictionary[k][i])
    return dictionary

############################
### MAIN FUNCTIONS & CLASSES

### generic config file import
def load_config_file(*, filepath, config_type="", replace_wildcards=True, verbose=1):
    # print statement
    if verbose >= 1:
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"Attempting to import config file of type \"{config_type}\" from \"{filepath}\"")
    # load yaml contents
    filepath = os.path.abspath(filepath)
    config = file_utils.load_local_yaml_file(filepath=filepath)
    # check config file dict
    type_utils.check_dict(dictionary=config, dictionary_name=config_type, blueprint=config_type, top_level=True)
    # replace wildcards
    if replace_wildcards == True:
        config = replace_wildcards_dict_recursive(dictionary=config)
    # create attridict
    config = attridict(config)
    return config

### generic config file storage
def store_config_file(*, filepath, config, config_type="", verbose=1):
    # print statement
    if verbose >= 1:
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"Attempting to store config file of type \"{config_type}\" to \"{filepath}\"")
    # check config file dict
    type_utils.check_dict(dictionary=config, dictionary_name=config_type, blueprint=config_type, top_level=True)
    # store yaml contents
    filepath = os.path.abspath(filepath)
    file_utils.store_local_yaml_file(filepath=filepath, yaml_content=config)

### create config dict
# use keywords of function as input kwargs for config
# check that all keys are there for given config_type
def create_config(*, config_type="", replace_wildcards=True, verbose=1, **attrs):
    # print statement
    if verbose >= 1:
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"Attempting to create config of type \"{config_type}\"")
    # create dict from attrs / kwargs
    config = {}
    config.update(attrs)
    # check config file dict
    type_utils.check_dict(dictionary=config, dictionary_name=config_type, blueprint=config_type, top_level=True)
    # replace wildcards
    if replace_wildcards == True:
        config = replace_wildcards_dict_recursive(dictionary=config)
    # create attridict
    config = attridict(config)
    return config


