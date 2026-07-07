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
            r"%%%ANALYSIS_CONTROLLER_PATH%%%": _ANALYSIS_CONTROLLER_PATH,
            r"%%%ANALYSIS_CONTROLLER_REPO_PATH%%%": _ANALYSIS_CONTROLLER_REPO_PATH,
        }
        for wildcard, wildcard_replacement in wildcards.items():
            new_value = new_value.replace(wildcard, wildcard_replacement)
    return new_value

### determination of file type (file, directory) with first char of permissions (from ls -lH output)
_perm_to_type = {
    "-": "file",
    "d": "directory",
    "l": "symlink",
    "b": "block",
    "c": "char",
    "s": "socket",
    "p": "fifo",
}

### recursive scan for files in subdirs
def _recursive_file_scan(*, cur_basepath, ls_command, file_suffix="", maxdepth=9999, verbose=1, cur_found_files=[], cur_depth=0):
    # check whether depth is not too high, else immediately exit
    if cur_depth > maxdepth:
        return cur_found_files
    # run ls command
    returnvalue, cmdout = console_utils.run_command(bash_command=f'{ls_command} {cur_basepath}\n', verbose=verbose)
    # analyze output of ls command
    subdir_basepaths = []
    for ls_line in cmdout.split("\n"):
        # make sure line is not empty
        if ls_line.lower().startswith("total"):
            continue
        if len(ls_line) == 0:
            continue
        # extract information from ls output
        ls_line_parts = ls_line.split(maxsplit=8) # maxsplit=8 ensures that spaces in last column (filename) are not misinterpreted
        ls_line_parts = [console_utils.remove_console_characters(input_str=ls_item) for ls_item in ls_line_parts]
        perms, links, owner, group, size, month, day, time_or_year, name = ls_line_parts
        # determine type from permission string
        perms_firstchar = perms[0]
        dtype = _perm_to_type[perms_firstchar]
        # remove trailing spaces from name
        name = name.rstrip()
        # determine rel filepath / objpath
        rel_objath = os.path.join(cur_basepath, name)
        # check if directory: call recursively (later)
        if dtype == "directory":
            subdir_basepaths.append(rel_objath)
        # skip if not file
        if dtype != "file":
            continue
        # check file suffix (if desired)
        if file_suffix != None:
            if not name.endswith(file_suffix):
                continue
        # add found file to list, use rel filepath as key
        cur_found_files.append({
            "path": rel_objath,
            "perms": perms,
            "links": links,
            "owner": owner,
            "group": group,
            "size": int(size),
            "month": month,
            "day": day,
            "time_or_year": time_or_year,
            "dtype": dtype,
        })
    # recusively analyze subdirs, if depth not too high
    next_depth = cur_depth+1
    for subdir_basepath in subdir_basepaths:
        cur_found_files = _recursive_file_scan(cur_basepath=subdir_basepath, ls_command=ls_command, file_suffix=file_suffix, maxdepth=maxdepth, verbose=verbose, cur_found_files=cur_found_files, cur_depth=next_depth)
    return cur_found_files

### convert file size in bytes to human readable file size
# human readable format: "1.3 GiB"
def byte_size_to_human_readable_size(*, bytesize, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(bytesize) < 1024.0:
            return f"{bytesize:3.1f} {unit}B"
        bytesize /= 1024.0
    return f"{bytesize:.1f} YiB"

### convert human readable file size to byte file size
# human readable format: "1.3 GiB"
def human_readable_size_to_byte_size(*, humanreadablesize):
    units = {"":1, "Ki":1024, "Mi":1024**2, "Gi":1024**3,
             "Ti":1024**4, "Pi":1024**5, "Ei":1024**6,
             "Zi":1024**7, "Yi":1024**8}
    import re
    m = re.match(r'^\s*([0-9.]+)\s*([KMGTPEZY]?i?)?\s*B?\s*$', humanreadablesize, re.I)
    if not m: raise ValueError
    num = float(m.group(1))
    unit = (m.group(2) or "").title()
    return int(round(num * units[unit]))

############################
### MAIN FUNCTIONS & CLASSES

### load local file
def load_local_file(*, filepath):
    if not os.path.isfile(filepath):
        raise Exception(f"{console_utils.color.red} Could not find the file \"{filepath}\" {console_utils.color.reset}")
    with open(filepath, "r") as file:
        content = str(file.read())
    return content

### store local file
def store_local_file(*, filepath, new_content):
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

### load local yaml file
def load_local_yaml_file(*, filepath):
    if not os.path.isfile(filepath):
        raise Exception(f"{console_utils.color.red} Could not find the file \"{filepath}\" {console_utils.color.reset}")
    with open(filepath, "r") as file:
        yaml_content = yaml.safe_load(file)
    return yaml_content

### store local yaml file
def store_local_yaml_file(*, filepath, yaml_content):
    content = yaml.safe_dump(yaml_content)
    with open(filepath, "w") as file:
        file.write(content)

### load yaml config, and check whether it is conform for the specified type of config file (check keys and structure)
def load_config(*, filepath, config_type, verbose=1):
    ### make abspath
    filepath = os.path.abspath(filepath)
    ### print statement
    if verbose >= 1:
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"Attempting to import config file of type \"{config_type}\" from path \"{filepath}\"")
    ### load yaml contents
    config = load_local_yaml_file(filepath=filepath)
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

### recursively scan for files
# basepath: path from where to start the recursive scan
# ls_command: "ls -h"-like command that produces the following output format, e.g. "ls -h" or "gfal-ls -h":
#   "drwxrwxrwx  0 0     0        0.0    Jun 27 00:43 260626_075212" for directory
#   "-rw-------. 1 esper inst3a   205275 Jun 17 12:07 output.root" for file
# file_suffix: optional file suffix to filter on, e.g. ".root"
# maxdepth: max directory depth of recursive search
# verbose: change print statement behavior
## returns: found_files: [{path (wrt basepath), perms, links, owner, group, size (in bytes), month, day, time_or_year, dtype}]
def recursive_file_scan(*, basepath, ls_command="ls -l", file_suffix="", maxdepth=9999, verbose=1):
    # print
    if verbose >= 1:
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"Attempting to recursively find files with the command \"{ls_command}\" starting from path \"{basepath}\"")
    # recursive scan, starting at basepath
    found_files = _recursive_file_scan(cur_basepath=basepath, ls_command=ls_command, file_suffix=file_suffix, maxdepth=maxdepth, verbose=max(0,verbose-1))
    # calculate file no
    n_files = len(found_files)
    # calculate file size
    total_size = 0
    for file in found_files:
        total_size += file["size"]
    total_size_str = byte_size_to_human_readable_size(bytesize=total_size)
    # print
    if verbose >= 1:
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"Found \"{n_files}\" files with a total size of \"{total_size_str}\"")
    return found_files

### combine files into groups which should be hadd-ed together, respecting the file sizes
# file_list: [files = {size, path}]
# target_group_size: target size of group of files (if group >= this size, a new group is begun), in human readable form
## returns:
# file_group_list: [{size (sum of all file sizes in group), paths: [path of files in group]}]
def group_files(*, file_list, target_group_size="1 GiB", verbose=1):
        n_files = len(file_list)
        # print
        if verbose >= 1:
            console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"Attempting to build file groups of target size \"{target_group_size}\" from \"{n_files}\" input files")
        # parse target size
        target_file_group_size = human_readable_size_to_byte_size(humanreadablesize=target_group_size)
        # build groups
        file_group_list = []
        file_group = {"size": 0, "paths": []}
        for i_file, file in enumerate(file_list):
            # continue to fill current group
            file_group["size"] += file["size"]
            file_group["paths"].append(file["path"])
            # if too large or last file, stop current group and start new group
            if file_group["size"] > target_file_group_size or i_file == n_files-1:
                file_group_list.append(file_group)
                file_group = {"size": 0, "paths": []}
        n_file_groups = len(file_group_list)
        # print
        if verbose >= 1:
            console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"Built \"{n_file_groups}\" file groups")
        return file_group_list



