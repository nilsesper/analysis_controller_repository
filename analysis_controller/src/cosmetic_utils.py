##########################
### COSMETIC UTILITIES ###
##########################

############################
### IMPORTS

import os

from analysis_controller.src import path_utils
from analysis_controller.src import console_utils

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_REPOPATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)

############################
### HELPER FUNCTIONS & CLASSES (with prefix "_")

############################
### MAIN FUNCTIONS & CLASSES

### print header with relative file path
def print_console_header(*, filepath="", analysis_controller_filepath="", verbose=1):
    if analysis_controller_filepath != "":
        _filepath = analysis_controller_filepath
    else:
        _filepath = path_utils.relative_path_analysis_controller(filepath=filepath)
    if len(_filepath) < 51:
        _filepath += " "*(51-len(_filepath))
    print(f"{console_utils.color.cyan}+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++{console_utils.color.reset}")
    print(f"{console_utils.color.cyan}+++{console_utils.color.bold_white} ANALYSIS_CONTROLLER: l1 scouting slow hscp analysis {console_utils.color.cyan}+++{console_utils.color.reset}")
    print(f"{console_utils.color.cyan}+++{console_utils.color.white} {_filepath} {console_utils.color.cyan}+++{console_utils.color.reset}")
    print(f"{console_utils.color.cyan}+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++{console_utils.color.reset}")

### print footer
def print_console_footer(*, verbose=1):
    print(f"{console_utils.color.cyan}+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++{console_utils.color.reset}")

### print string with highlighted topic and normal string in the format "[topic] string"
def print_topic_string(*, topic="", string="", verbose=1):
    print(f"{console_utils.color.yellow}[ {topic} ]{console_utils.color.reset} {string}")

### print highlighted string in the format "string"
def print_highlight_string(*, topic="", string="", verbose=1):
    print(f"{console_utils.color.yellow}{string}{console_utils.color.reset}")

### print normal string in the format "string"
def print_string(*, topic="", string="", verbose=1):
    print(f"{string}")
