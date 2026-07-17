"*none*"###########################
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

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_PATH, _ANALYSIS_CONTROLLER_REPO_PATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)

############################
### HELPER FUNCTIONS & CLASSES (with prefix "_")

### replace wildcard in str if possible
def _replace_wildcard_if_possible(*, value):
    new_value = value
    wildcards = {
        r"%%%ANALYSIS_CONTROLLER_PATH%%%": _ANALYSIS_CONTROLLER_PATH,
        r"%%%ANALYSIS_CONTROLLER_REPO_PATH%%%": _ANALYSIS_CONTROLLER_REPO_PATH,
    }
    for wildcard, wildcard_replacement in wildcards.items():
        new_value = new_value.replace(wildcard, wildcard_replacement)
    return new_value

###### blueprints

PythonTypes = {
    "*none*": type(None),
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
    ### lower-level dicts (part of info dicts)
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
    "_FinalselectionCollection": {
        "user_label": "*str*",
        "rekbmtf_output_config": "*str*",
    },
    "_GenericDictIntStr": "*int*-*str*",
    "_GenericDictStrListInt": "*str*-*list*::*int*",
    #########################
    ###*** for scripts_controller ***
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
    },
    "RekbmtfOutput": {
        "input_files": "*list*::_LsFile",
        "input_size": "*int*",
        
        "collection_basepath": "*str*",
        "collection_files": "*list*::_CollectionFileGroup",
        "collection_timestamp": "*str*",
    },
    #--- finalselection
    "FinalselectionInput": {
        "collections": "*list*::_FinalselectionCollection"
    },
    ###*** for scripts_analysis ***
    #--- finalselection
    "FinalselectionParamsAnalysis": {
        "muon_mass": "*float*",
        "delta_r_max_for_track_l1mu_match": "*float*",
        "delta_r_min_distance_between_tracks": "*float*",
        "bx_interval_earlier_colliding": "*int*",
        "run_to_lhcscheme": "*dict*::*int*::*str*",
        "lhcscheme_to_filledbx": "*dict*::*str*::*list*::*int*",
    },
    #########################
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
    #--- finalselection
    "ConfigFinalselectionInput": {
        "FinalselectionInput": "*dict*::FinalselectionInput",
    },
    "ConfigFinalselectionParamsSubmission": {
        "FinalselectionParamsSubmission": "*dict*::FinalselectionParamsSubmission",
    },
}

### check dict
# check if exactly the same keys as in blueprint are in dict
# check recursively dicts and lists in the dict
# check the types of the values
# specify dictionary_name string for more conclusive error messages
def check_dict(*, dictionary, dictionary_name="", blueprint="", top_level=True):
    #print(f"check_dict : {dictionary_name}\n   dictionary = {dictionary}\n   blueprint = {blueprint}")
    err_list = []
    blueprint_obj = None
    # check whether input type is dictionary
    if type(dictionary) != PythonTypes["*dict*"] and type(dictionary) != PythonTypes["*attridict*"]:
        err_list.append(f"\"{dictionary_name}\" dictionary was not actually a dictionary but had the type \"{type(dictionary)}\".")
    else: # if input type is dictionary, continue with the check
        python_type_has_match = [blueprint.startswith(PythonTypeName) for PythonTypeName in PythonTypeNames]
        # if blueprint is named blueprint in DictBlueprints, perform explicit check
        if blueprint in DictBlueprints.keys():
            blueprint_obj = DictBlueprints[blueprint]
            # check exactly same keys
            for key in blueprint_obj.keys():
                if key not in dictionary.keys():
                    err_list.append(f"\"{dictionary_name}\" dictionary did not include the required key \"{key}\".")
            for key in dictionary.keys():
                if key not in blueprint_obj.keys():
                    err_list.append(f"\"{dictionary_name}\" dictionary did include the unexpected key \"{key}\".")
            # check value types & recursively lists and dicts
            for key, value in dictionary.items():
                if key in blueprint_obj.keys():
                    blueprintvalue = blueprint_obj[key]
                    err_list.extend( check_one_element(value=value, blueprintvalue=blueprintvalue, element_name=f"{dictionary_name} -> {key}", top_level=False) )
        # if blueprint is PythonType, perform type-only check
        elif any(python_type_has_match):
            python_type_match_idx = python_type_has_match.index(True)
            python_type_match = PythonTypeNames[python_type_match_idx]
            # check value types & recursively lists and dicts
            for key, value in dictionary.items():
                blueprintvalue_key = python_type_match
                blueprintvalue_value = blueprint[len(python_type_match)+len("::"):]
                err_list.extend( check_one_element(value=key, blueprintvalue=blueprintvalue_key, element_name=f"{dictionary_name} key", top_level=False) )
                err_list.extend( check_one_element(value=value, blueprintvalue=blueprintvalue_value, element_name=f"{dictionary_name} -> {key}", top_level=False) )
        else:
            err_list.append(f"\"{dictionary_name}\" dictionary has an unexpected element blueprint \"{blueprint}\". The blueprint must be either in DictBlueprints or a valid PythonType.")
    # generate error message if top level
    if len(err_list) > 0:
        if blueprint_obj != None:
            err_list.append(f"INFO: One expects the following structure for a \"{dictionary_name}\" dictionary:  \"{blueprint_obj}\".")
        if top_level:
            err_str = ""
            n_err = len(err_list)
            for i in range(n_err):
                err_str += f"- {err_list[i]}"
                if i < n_err-1:
                    err_str += "\n"
            console_utils.raise_exception(string=err_str)
    print(f"check_dict(): {dictionary_name}\n    blueprint = {blueprint}\n    result = {len(err_list)==0}")
    return err_list

### check list
def check_list(*, listobj, list_name="", elementblueprint="", top_level=True):
    #print(f"check_list : {list_name}\n   listobj = {listobj}\n   elementblueprint = {elementblueprint}")
    err_list = []
    # check input type
    if type(listobj) != PythonTypes["*list*"]:
        err_list.append(f"\"{list_name}\" list was not actually a list but had the type \"{type(listobj)}\".")
    else:
        print(list_name, elementblueprint)
        python_type_has_match = [elementblueprint.startswith(PythonTypeName) for PythonTypeName in PythonTypeNames]
        # if blueprint is named blueprint in DictBlueprints, perform explicit check
        if elementblueprint in DictBlueprints.keys():
            # check dict with blueprint for each element
            for i in range(len(listobj)):
                listelement = listobj[i]
                # check type of each list element (if not dict then give alarm)
                if type(listelement) != PythonTypes["*dict*"] and type(listelement) != PythonTypes["*attridict*"]:
                    err_list.append(f"\"{list_name}\" list has an unexpected value type for index {i}. Expected type \"{PythonTypes["*dict*"]}\" but found type \"{type(listelement)}\".")
                # check dict at this list position
                else:
                    err_list.extend( check_dict(dictionary=listelement, dictionary_name=f"{list_name} [{i}]", blueprint=elementblueprint, top_level=False) )
        # if blueprint is PythonType, perform type-only check
        elif any(python_type_has_match):
            python_type_match_idx = python_type_has_match.index(True)
            python_type_match = PythonTypeNames[python_type_match_idx]
            # check value types & recursively lists and dicts
            for i in range(len(listobj)):
                listelement = listobj[i]
                err_list.extend( check_one_element(value=listelement, blueprintvalue=elementblueprint, element_name=f"{list_name} -> {i}", top_level=False) )
        else:
            err_list.append(f"\"{list_name}\" list has an unexpected element blueprint \"{elementblueprint}\". The blueprint must be either in DictBlueprints or a valid PythonType.")
    # generate error message if top level
    if len(err_list) > 0:
        if top_level:
            err_str = ""
            n_err = len(err_list)
            for i in range(n_err):
                err_str += f"- {err_list[i]}"
                if i < n_err-1:
                    err_str += "\n"
            console_utils.raise_exception(string=err_str)
    print(f"check_list(): {list_name}\n    elementblueprint = {elementblueprint}\n    result = {len(err_list)==0}")
    return err_list

### check one element
def check_one_element(*, value, blueprintvalue, element_name="", top_level=True):
    #print(f"check_one_element : key = {key}\n   value = {value}\n   blueprintvalue = {blueprintvalue}")
    err_list = []
    # if python type: do normal type check
    if blueprintvalue in PythonTypeNames:
        if type(value) != PythonTypes[blueprintvalue]:
            err_list.append(f"\"{element_name}\" has an unexpected value type. Expect type \"{PythonTypes[blueprintvalue]}\" but found type \"{type(value)}\". The current wrong value is \"{value}\".")
    # if list: check all list elements (only possible for list of dicts)
    elif blueprintvalue.startswith("*list*::"):
        if type(value) != PythonTypes["*list*"]:
            err_list.append(f"\"{element_name}\" has an unexpected value type. Expect type \"{blueprintvalue}\" but found type \"{type(value)}\".")
        # check list elements
        newblueprint = blueprintvalue[len("*list*::"):]
        err_list.extend( check_list(listobj=value, list_name=f"{element_name}", elementblueprint=newblueprint, top_level=False) )
    # if dict: check dict keys and values
    elif blueprintvalue.startswith("*dict*::"):
        if type(value) != PythonTypes["*dict*"] and type(value) != PythonTypes["*attridict*"]:
            err_list.append(f"\"{element_name}\" dictionary has an unexpected value type. Expect type \"{blueprintvalue}\" but found type \"{type(value)}\".")
        # check dict keys and values
        newblueprint = blueprintvalue[len("*dict*::"):]
        err_list.extend( check_dict(dictionary=value, dictionary_name=f"{element_name}", blueprint=newblueprint, top_level=False) )
    else:
        err_list.append(f"\"{element_name}\" has invalid blueprint value \"{blueprintvalue}\".")
    print(f"check_one_element(): {element_name}\n    blueprintvalue = {blueprintvalue}\n    result = {len(err_list)==0}")
    return err_list

### replace wildcards in dictionary
def replace_wildcards_dict_recursive(*, dictionary):
    if type(dictionary) != PythonTypes["*dict*"] and type(dictionary) != PythonTypes["*attridict*"]:
        return dictionary
    for k in dictionary.keys():
        if type(dictionary[k]) == PythonTypes["*str*"]:
            dictionary[k] = _replace_wildcard_if_possible(value=dictionary[k])
        elif type(dictionary[k]) == PythonTypes["*dict*"] or type(dictionary[k]) == PythonTypes["*attridict*"]:
            dictionary[k] = replace_wildcards_dict_recursive(dictionary=dictionary[k])
        elif type(dictionary[k]) == PythonTypes["*list*"]: # assume list of dicts
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
    check_dict(dictionary=config, dictionary_name=config_type, blueprint=config_type, top_level=True)
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
    check_dict(dictionary=config, dictionary_name=config_type, blueprint=config_type, top_level=True)
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
    check_dict(dictionary=config, dictionary_name=config_type, blueprint=config_type, top_level=True)
    # replace wildcards
    if replace_wildcards == True:
        config = replace_wildcards_dict_recursive(dictionary=config)
    # create attridict
    config = attridict(config)
    return config


