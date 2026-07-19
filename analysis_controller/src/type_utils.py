###########################
### CONFIGURATION UTILS ###
###########################

############################
### IMPORTS

import os

from analysis_controller.src import path_utils
from analysis_controller.src import console_utils
from analysis_controller.src import type_definitions

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_PATH, _ANALYSIS_CONTROLLER_REPO_PATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)

############################
### HELPER FUNCTIONS & CLASSES (with prefix "_")



############################
### MAIN FUNCTIONS & CLASSES

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
    if type(dictionary) != type_definitions.PythonTypes["*dict*"] and type(dictionary) != type_definitions.PythonTypes["*attridict*"]:
        err_list.append(f"\"{dictionary_name}\" dictionary was not actually a dictionary but had the type \"{type(dictionary)}\".")
    else: # if input type is dictionary, continue with the check
        python_type_has_match = [blueprint.startswith(PythonTypeName) for PythonTypeName in type_definitions.PythonTypeNames]
        # if blueprint is named blueprint in type_definitions.DictBlueprints, perform explicit check
        if blueprint in type_definitions.DictBlueprints.keys():
            blueprint_obj = type_definitions.DictBlueprints[blueprint]
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
            python_type_match = type_definitions.PythonTypeNames[python_type_match_idx]
            # check value types & recursively lists and dicts
            for key, value in dictionary.items():
                blueprintvalue_key = python_type_match
                blueprintvalue_value = blueprint[len(python_type_match)+len("::"):]
                err_list.extend( check_one_element(value=key, blueprintvalue=blueprintvalue_key, element_name=f"{dictionary_name} key", top_level=False) )
                err_list.extend( check_one_element(value=value, blueprintvalue=blueprintvalue_value, element_name=f"{dictionary_name} -> {key}", top_level=False) )
        else:
            err_list.append(f"\"{dictionary_name}\" dictionary has an unexpected element blueprint \"{blueprint}\". The blueprint must be either in type_definitions.DictBlueprints or a valid PythonType.")
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
    #print(f"check_dict(): {dictionary_name}\n    blueprint = {blueprint}\n    result = {len(err_list)==0}")
    return err_list

### check list
def check_list(*, listobj, list_name="", elementblueprint="", top_level=True):
    #print(f"check_list : {list_name}\n   listobj = {listobj}\n   elementblueprint = {elementblueprint}")
    err_list = []
    # check input type
    if type(listobj) != type_definitions.PythonTypes["*list*"]:
        err_list.append(f"\"{list_name}\" list was not actually a list but had the type \"{type(listobj)}\".")
    else:
        python_type_has_match = [elementblueprint.startswith(PythonTypeName) for PythonTypeName in type_definitions.PythonTypeNames]
        # if blueprint is named blueprint in type_definitions.DictBlueprints, perform explicit check
        if elementblueprint in type_definitions.DictBlueprints.keys():
            # check dict with blueprint for each element
            for i in range(len(listobj)):
                listelement = listobj[i]
                # check type of each list element (if not dict then give alarm)
                if type(listelement) != type_definitions.PythonTypes["*dict*"] and type(listelement) != type_definitions.PythonTypes["*attridict*"]:
                    err_list.append(f"\"{list_name}\" list has an unexpected value type for index {i}. Expected type \"{type_definitions.PythonTypes["*dict*"]}\" but found type \"{type(listelement)}\".")
                # check dict at this list position
                else:
                    err_list.extend( check_dict(dictionary=listelement, dictionary_name=f"{list_name} [{i}]", blueprint=elementblueprint, top_level=False) )
        # if blueprint is PythonType, perform type-only check
        elif any(python_type_has_match):
            python_type_match_idx = python_type_has_match.index(True)
            python_type_match = type_definitions.PythonTypeNames[python_type_match_idx]
            # check value types & recursively lists and dicts
            for i in range(len(listobj)):
                listelement = listobj[i]
                err_list.extend( check_one_element(value=listelement, blueprintvalue=elementblueprint, element_name=f"{list_name} -> {i}", top_level=False) )
        else:
            err_list.append(f"\"{list_name}\" list has an unexpected element blueprint \"{elementblueprint}\". The blueprint must be either in type_definitions.DictBlueprints or a valid PythonType.")
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
    #print(f"check_list(): {list_name}\n    elementblueprint = {elementblueprint}\n    result = {len(err_list)==0}")
    return err_list

### check one element
def check_one_element(*, value, blueprintvalue, element_name="", top_level=True):
    #print(f"check_one_element : key = {key}\n   value = {value}\n   blueprintvalue = {blueprintvalue}")
    err_list = []
    # if python type: do normal type check
    if blueprintvalue in type_definitions.PythonTypeNames:
        if type(value) != type_definitions.PythonTypes[blueprintvalue]:
            err_list.append(f"\"{element_name}\" has an unexpected value type. Expect type \"{type_definitions.PythonTypes[blueprintvalue]}\" but found type \"{type(value)}\". The current wrong value is \"{value}\".")
    # if list: check all list elements (only possible for list of dicts)
    elif blueprintvalue.startswith("*list*::"):
        if type(value) != type_definitions.PythonTypes["*list*"]:
            err_list.append(f"\"{element_name}\" has an unexpected value type. Expect type \"{blueprintvalue}\" but found type \"{type(value)}\".")
        # check list elements
        newblueprint = blueprintvalue[len("*list*::"):]
        err_list.extend( check_list(listobj=value, list_name=f"{element_name}", elementblueprint=newblueprint, top_level=False) )
    # if dict: check dict keys and values
    elif blueprintvalue.startswith("*dict*::"):
        if type(value) != type_definitions.PythonTypes["*dict*"] and type(value) != type_definitions.PythonTypes["*attridict*"]:
            err_list.append(f"\"{element_name}\" dictionary has an unexpected value type. Expect type \"{blueprintvalue}\" but found type \"{type(value)}\".")
        # check dict keys and values
        newblueprint = blueprintvalue[len("*dict*::"):]
        err_list.extend( check_dict(dictionary=value, dictionary_name=f"{element_name}", blueprint=newblueprint, top_level=False) )
    else:
        err_list.append(f"\"{element_name}\" has invalid blueprint value \"{blueprintvalue}\".")
    #print(f"check_one_element(): {element_name}\n    blueprintvalue = {blueprintvalue}\n    result = {len(err_list)==0}")
    return err_list

