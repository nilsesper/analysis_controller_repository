##################################
### CONSOLE PRINTING UTILITIES ###
##################################

############################
### IMPORTS

import os
import sys

from analysis_controller.src import path_utils

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_REPOPATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)

############################
### HELPER FUNCTIONS & CLASSES (with prefix "_")

############################
### MAIN FUNCTIONS & CLASSES

# console text foreground colors
class color:
    # resets fg and bg
    reset ='\033[0m'
    # normal
    black ='\033[0;30m'
    red ='\033[0;31m'
    green ='\033[0;32m'
    yellow ='\033[0;33m'
    blue ='\033[0;34m'
    purple ='\033[0;35m'
    cyan ='\033[0;36m'
    white ='\033[0;37m'
    # bold
    bold_black ='\033[1;30m'
    bold_red ='\033[1;31m'
    bold_green ='\033[1;32m'
    bold_yellow ='\033[1;33m'
    bold_blue ='\033[1;34m'
    bold_purple ='\033[1;35m'
    bold_cyan ='\033[1;36m'
    bold_white ='\033[1;37m'

# console text background colors
class bgcolor:
    # resets fg and bg
    reset ='\033[0m'
    # normal
    black ='\033[0;40m'
    red ='\033[0;41m'
    green ='\033[0;42m'
    yellow ='\033[0;43m'
    blue ='\033[0;44m'
    purple ='\033[0;45m'
    cyan ='\033[0;46m'
    white ='\033[0;47m'

# suppress print statements (redirect from stdout away to devnull)
# usage: execute code where print should be suppressed inside "with noprint():"
class noprint:
    # when entering "with"
    def __enter__(self):
        self.original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
    # when exiting "with"
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self.original_stdout

