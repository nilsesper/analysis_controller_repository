###########################
### CONFIGURATION UTILS ###
###########################

############################
### IMPORTS

import os
import sys
from attrdict import AttrDict

from analysis_controller.src import path_utils
from analysis_controller.src import file_utils
from analysis_controller.src import console_utils

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_PATH, _ANALYSIS_CONTROLLER_REPO_PATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)

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
# value_type can be = int, str, list, float, dict
# for custom classes use value_type = "CLASSNAME" (with location of class, e.g. "analysis_controller.src.config_utils.RekbmtfInput")
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
            r"%%%ANALYSIS_CONTROLLER_PATH%%%": _ANALYSIS_CONTROLLER_PATH,
            r"%%%ANALYSIS_CONTROLLER_REPO_PATH%%%": _ANALYSIS_CONTROLLER_REPO_PATH,
        }
        for wildcard, wildcard_replacement in wildcards.items():
            new_value = new_value.replace(wildcard, wildcard_replacement)
    return new_value

### for constructor to check passed attributes, and then return attribute dict, to be added to self.__dict___
# easier way to control the members of class and not needing to write each member name multiple times...
def _create_property_dict(*, constructor_attrs={}, class_name="", required_keys=[], optional_keys=[], default_value=None, verbose=1):
    # check constructor attrs vs. required & optional attrs
    err_list = []
    dict_keys = constructor_attrs.keys()
    allowed_attrs = list(required_keys)+list(optional_keys)
    for key in required_keys:
        if key not in dict_keys:
            err_list.append(f"[Class \"{class_name}\" constructor]  Attribute list is missing the required attribute \"{key}\".")
    for key in dict_keys:
        if key not in allowed_attrs:
            err_list.append(f"[Class \"{class_name}\" constructor]  Attribute list is containing the unexpected attribute \"{key}\".")
    if len(err_list)>0:
        err_str = "----------------------------------\n"
        for err in err_list:
            err_str += f"{err}\n"
        err_str += f"[Class \"{class_name}\" constructor]  INFO: One expects the following attributes for the \"{class_name}\" class constructor:  required = {required_keys}  --  optional = {optional_keys}.\n"
        err_str += "----------------------------------"
        raise Exception(f"{console_utils.color.red}{err_str}{console_utils.color.reset}")
    # prepare attr_dict, where all non-given optional attrs are assigned to None
    attr_dict = {}
    for key in allowed_attrs:
        if key in constructor_attrs.keys(): # add constructor_attr value to attribute, if given
            attr_dict[key] = constructor_attrs[key]
        else: # else, assign default value to attribute
            attr_dict[key] = default_value
    # print statement
    if verbose >= 1:
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"Prepared attributes for object of type \"{class_name}\"")
    return attr_dict

### for constructor to check passed attributes, and then return attribute dict, to be added to self.__dict___
# easier way to control the members of class and not needing to write each member name multiple times...
def _create_property_dict_check_type(*, constructor_attrs={}, class_name="", required_keys_with_type={}, optional_keys_with_type={}, default_value=None, verbose=1):
    # check constructor attrs vs. required & optional attrs
    err_list = []
    allowed_attrs_with_type = required_keys_with_type | optional_keys_with_type
    for key in required_keys_with_type.keys():
        if key not in constructor_attrs.keys():
            err_list.append(f"[Class \"{class_name}\" constructor]  Attribute list is missing the required attribute \"{key}\".")
    for key, value in constructor_attrs.items():
        if key not in allowed_attrs_with_type.keys():
            err_list.append(f"[Class \"{class_name}\" constructor]  Attribute list is containing the unexpected attribute \"{key}\".")
        else:
            expected_type = allowed_attrs_with_type[key]
            if _bool_check_value_type(value=value, value_type=expected_type) == False:
                err_list.append(f"[Class \"{class_name}\" constructor]  Attribute with key \"{key}\" has wrong type \"{type(value)}\" instead of expected type \"{expected_type}\".")
    if len(err_list)>0:
        err_str = "----------------------------------\n"
        for err in err_list:
            err_str += f"{err}\n"
        err_str += f"[Class \"{class_name}\" constructor]  INFO: One expects the following attributes for the \"{class_name}\" class constructor:  required (with type) = {required_keys_with_type}  --  optional (with type) = {optional_keys_with_type}.\n"
        err_str += "----------------------------------"
        raise Exception(f"{console_utils.color.red}{err_str}{console_utils.color.reset}")
    # prepare attr_dict, where all non-given optional attrs are assigned to None
    attr_dict = {}
    for key, value in allowed_attrs_with_type.items():
        if key in constructor_attrs.keys(): # add constructor_attr value to attribute, if given
            attr_dict[key] = constructor_attrs[key]
        else: # else, assign default value to attribute
            attr_dict[key] = default_value
    # print statement
    if verbose >= 1:
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"Prepared attributes for object of type \"{class_name}\"")
    return attr_dict

### generic config file import
def load_generic_config_file(*, filepath, verbose=1, config_type=""):
    # print statement
    if verbose >= 1:
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"Attempting to import config file of type \"{config_type}\" from \"{filepath}\"")
    # make abspath
    filepath = os.path.abspath(filepath)
    # load yaml contents
    config = file_utils.load_local_yaml_file(filepath=filepath)
    return config

### generic config file storage
def store_generic_config_file(*, filepath, config, verbose=1, config_type=""):
    # print statement
    if verbose >= 1:
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"Attempting to store config file of type \"{config_type}\" to \"{filepath}\"")
    # make abspath
    filepath = os.path.abspath(filepath)
    # store yaml contents
    file_utils.store_local_yaml_file(filepath=filepath, yaml_content=config)

###### config classes (tracks one step of the analysis)

BlueprintRekbmtfInput = {
    "data_type": "str",
    "data_label": "str",

    "input_das_name": "str",
    "input_lumi_mask": "str",
}

class RekbmtfInput:
    def __init__(self, verbose=1, replace_wildcards=True, **attrs):
        computed_attrs = _create_property_dict_check_type(constructor_attrs=attrs,
            class_name="RekbmtfInput",
            required_keys_with_type={
                "data_type": "str",
                "data_label": "str",

                "input_das_name": "str",
                "input_lumi_mask": "str",
            }, optional_keys_with_type={
            }, default_value=None, verbose=verbose)
        self.__dict__.update(computed_attrs)
        if replace_wildcards == True:
            pass

BlueprintRekbmtfParams = {
    "submission_type": "str",
    "submission_splitting": "str",

    "output_type": "str",
    "output_site": "str",
    "output_basepath": "str",

    "cmssw_src_path": "str",

    "crab_config_template_filepath": "str",
    "cmssw_config_template_filepath": "str",
}

class RekbmtfParams:
    def __init__(self, verbose=1, replace_wildcards=True, **attrs):
        computed_attrs = _create_property_dict_check_type(constructor_attrs=attrs,
            class_name="RekbmtfParams",
            required_keys_with_type={
                "submission_type": "str",
                "submission_splitting": "str",

                "output_type": "str",
                "output_site": "str",
                "output_basepath": "str",

                "cmssw_src_path": "str",

                "crab_config_template_filepath": "str",
                "cmssw_config_template_filepath": "str",
            }, optional_keys_with_type={
            }, default_value=None, verbose=verbose)
        self.__dict__.update(computed_attrs)
        if replace_wildcards == True:
            self.output_basepath = _replace_wildcard_if_possible( value=self.output_basepath )
            self.crab_config_template_filepath = os.path.abspath(_replace_wildcard_if_possible( value=self.crab_config_template_filepath ))
            self.cmssw_src_path = os.path.abspath(_replace_wildcard_if_possible( value=self.cmssw_src_path ))
            self.cmssw_config_template_filepath = os.path.abspath(_replace_wildcard_if_possible( value=self.cmssw_config_template_filepath ))

BlueprintRekbmtfSubmission = {
    "submission_name": "str",
    "submission_path": "str",
    "submission_timestamp": "str",

    "cmssw_config_filepath": "str",
    "crab_config_filepath": "str",
    "crab_requestname": "str",
    "crab_workarea": "str",
}

class RekbmtfSubmission:
    def __init__(self, verbose=1, replace_wildcards=True, **attrs):
        computed_attrs = _create_property_dict_check_type(constructor_attrs=attrs,
            class_name="RekbmtfSubmission",
            required_keys_with_type={
                "submission_name": "str",
                "submission_path": "str",
                "submission_timestamp": "str",

                "cmssw_config_filepath": "str",
                "crab_config_filepath": "str",
                "crab_requestname": "str",
                "crab_workarea": "str",
            },
            optional_keys_with_type={
            }, default_value=None, verbose=verbose)
        self.__dict__.update(computed_attrs)
        if replace_wildcards == True:
            pass

BlueprintRekbmtfOutput = {
    "output_files": "list",
    "output_file_groups": "list",
    "target_output_file_size": "str",

    "collection_output_type": "str",
    "collection_output_site": "str",
    
    "collection_basepath": "str",
    "collected_files": "list",
}

class RekbmtfOutput:
    def __init__(self, verbose=1, replace_wildcards=True, **attrs):
        computed_attrs = _create_property_dict_check_type(constructor_attrs=attrs,
            class_name="RekbmtfOutput",
            required_keys_with_type={
                "output_files": "list",
                "output_file_groups": "list",
                "target_output_file_size": "str",

                "collection_output_type": "str",
                "collection_output_site": "str",
                
                "collection_basepath": "str",
                "collected_files": "list",
            },
            optional_keys_with_type={
            }, default_value=None, verbose=verbose)
        self.__dict__.update(computed_attrs)
        if replace_wildcards == True:
            pass

###### config file classes (may include several config classes, to track the history)

class ConfigFileRekbmtfInput:
    def __init__(self, verbose=1, **attrs):
        computed_attrs = _create_property_dict_check_type(constructor_attrs=attrs,
            class_name="ConfigFileRekbmtfInput",
            required_keys_with_type={
                "RekbmtfInput": "analysis_controller.src.config_utils.RekbmtfInput",
            },
            optional_keys_with_type={
            }, default_value=None, verbose=verbose)
        self.__dict__.update(computed_attrs)
def load_ConfigFileRekbmtfInput(*, filepath, verbose=1, replace_wildcards=True):
    config_file = load_generic_config_file(filepath=filepath, config_type="ConfigFileRekbmtfInput", verbose=verbose)
    ConfigObject = ConfigFileRekbmtfInput(
        RekbmtfInput=RekbmtfInput(**config_file["RekbmtfInput"], verbose=min(0,verbose-1), replace_wildcards=replace_wildcards, ),
        verbose=min(0,verbose-1), )
    return ConfigObject

class ConfigFileRekbmtfParams:
    def __init__(self, verbose=1, **attrs):
        computed_attrs = _create_property_dict_check_type(constructor_attrs=attrs,
            class_name="ConfigFileRekbmtfParams",
            required_keys_with_type={
                "RekbmtfParams": "analysis_controller.src.config_utils.RekbmtfParams",
            },
            optional_keys_with_type={
            }, default_value=None, verbose=verbose)
        self.__dict__.update(computed_attrs)
def load_ConfigFileRekbmtfParams(*, filepath, verbose=1, replace_wildcards=True):
    config_file = load_generic_config_file(filepath=filepath, config_type="ConfigFileRekbmtfParams", verbose=verbose)
    ConfigObject = ConfigFileRekbmtfParams(
        RekbmtfParams=RekbmtfParams(**config_file["RekbmtfParams"], verbose=min(0,verbose-1), replace_wildcards=replace_wildcards, ),
        verbose=min(0,verbose-1), )
    return ConfigObject

class ConfigFileRekbmtfSubmission:
    def __init__(self, verbose=1, **attrs):
        computed_attrs = _create_property_dict_check_type(constructor_attrs=attrs,
            class_name="ConfigFileRekbmtfSubmission",
            required_keys_with_type={
                "RekbmtfInput": "analysis_controller.src.config_utils.RekbmtfInput",
                "RekbmtfParams": "analysis_controller.src.config_utils.RekbmtfParams",
                "RekbmtfSubmission": "analysis_controller.src.config_utils.RekbmtfSubmission",
            },
            optional_keys_with_type={
            }, default_value=None, verbose=verbose)
        self.__dict__.update(computed_attrs)
def load_ConfigFileRekbmtfSubmission(*, filepath, verbose=1, replace_wildcards=True):
    config_file = load_generic_config_file(filepath=filepath, config_type="ConfigFileRekbmtfSubmission", verbose=verbose)
    ConfigObject = ConfigFileRekbmtfSubmission(
        RekbmtfInput=RekbmtfInput(**config_file["RekbmtfInput"], verbose=min(0,verbose-1), replace_wildcards=replace_wildcards, ),
        RekbmtfParams=RekbmtfParams(**config_file["RekbmtfParams"], verbose=min(0,verbose-1), replace_wildcards=replace_wildcards, ),
        RekbmtfSubmission=RekbmtfSubmission(**config_file["RekbmtfSubmission"], verbose=min(0,verbose-1), replace_wildcards=replace_wildcards, ),
        verbose=min(0,verbose-1), )
    return ConfigObject
def store_ConfigFileRekbmtfSubmission(*, filepath, ConfigObject, verbose=1):
    config_data = {
        "RekbmtfInput": ConfigObject.RekbmtfInput.__dict__,
        "RekbmtfParams": ConfigObject.RekbmtfParams.__dict__,
        "RekbmtfSubmission": ConfigObject.RekbmtfSubmission.__dict__,
    }
    store_generic_config_file(filepath=filepath, config=config_data, config_type="ConfigFileRekbmtfSubmission", verbose=verbose)
    return ConfigObject

############################
### MAIN FUNCTIONS & CLASSES

### load yaml config, and check whether it is conform for the specified type of config file (check keys and structure)
def load_config(*, filepath, config_type, verbose=1):
    ### make abspath
    filepath = os.path.abspath(filepath)
    ### print statement
    if verbose >= 1:
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"Attempting to import config file of type \"{config_type}\" from path \"{filepath}\"")
    ### load yaml contents
    config = file_utils.load_local_yaml_file(filepath=filepath)
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
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"Successfully imported config file")
    ### return config file
    return config

