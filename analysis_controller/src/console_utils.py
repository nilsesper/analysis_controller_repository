##################################
### CONSOLE PRINTING UTILITIES ###
##################################

############################
### IMPORTS

import os
import sys
import subprocess

from analysis_controller.src import path_utils

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_PATH, _ANALYSIS_CONTROLLER_REPO_PATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)

############################
### HELPER FUNCTIONS & CLASSES (with prefix "_")

############################
### MAIN FUNCTIONS & CLASSES

### console text foreground colors
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

### console text background colors
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

### suppress print statements (redirect from stdout away to devnull)
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

### make all text in quotes "" color-highlighted
def _highlight_quotes(input_str, highlightcolor=color.cyan):
    output_str = ""
    is_highlighted = False
    for part in input_str.split("\""):
        output_str += f"{highlightcolor if is_highlighted == True else color.reset}{part}"
        is_highlighted = not is_highlighted
    output_str += f"{color.reset}"
    return output_str

### print header with relative file path
def print_console_header(*, filepath="", analysis_controller_filepath="", verbose=1):
    if analysis_controller_filepath != "":
        _filepath = analysis_controller_filepath
    else:
        _filepath = path_utils.relative_path_analysis_controller(filepath=filepath)
    if len(_filepath) < 62:
        _filepath += " "*(62-len(_filepath))
    print(f"{color.cyan}++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++{color.reset}")
    print(f"{color.cyan}+++{color.bold_white} ANALYSIS_CONTROLLER_REPOSITORY: l1 scouting slow hscp analysis {color.cyan}+++{color.reset}")
    print(f"{color.cyan}+++{color.white} {_filepath} {color.cyan}+++{color.reset}")
    print(f"{color.cyan}++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++{color.reset}")

### print footer
def print_console_footer(*, verbose=1):
    print(f"{color.cyan}++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++{color.reset}")

### print string with highlighted topic and normal string in the format "[topic] string"
def print_topic_string(*, topic="", string="", verbose=1, highlightcolor=color.yellow, highlightquotes=True, highlightquotescolor=color.cyan):
    if highlightquotes == True:
        string = _highlight_quotes(input_str=string, highlightcolor=highlightquotescolor)
    print(f"{highlightcolor}[ {topic} ]{color.reset} {string}")

### print string with highlighted prefix and normal string in the format "prefix string"
def print_prefix_string(*, prefix="", string="", verbose=1, highlightcolor=color.yellow, highlightquotes=True, highlightquotescolor=color.cyan):
    if highlightquotes == True:
        string = _highlight_quotes(input_str=string, highlightcolor=highlightquotescolor)
    print(f"{highlightcolor}{prefix} {color.reset} {string}")

### print highlighted string in the format "string"
def print_highlight_string(*, topic="", string="", verbose=1, highlightcolor=color.yellow, highlightquotes=True, highlightquotescolor=color.cyan):
    if highlightquotes == True:
        string = _highlight_quotes(input_str=string, highlightcolor=highlightquotescolor)
    print(f"{highlightcolor}{string}{color.reset}")

### print normal string in the format "string"
def print_string(*, topic="", string="", verbose=1, highlightquotes=True, highlightquotescolor=color.cyan):
    if highlightquotes == True:
        string = _highlight_quotes(input_str=string, highlightcolor=highlightquotescolor)
    print(f"{string}")

### run console command as subprocess
# bash_command: command string to be executed
# copy_env: if True, copy current bash env, else use clear env
def run_command(bash_command="", *, copy_env=False, verbose=1, print_cmd=True, print_stdout=True, print_stderr=True, always_print_when_retval_not_zero=True):
    # print info
    already_printed_cmd = False
    if verbose >= 1:
        print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"Attempting to execute bash command")
        if print_cmd == True and len(bash_command) > 0:
            for bash_command_line in bash_command.split("\n"):
                if bash_command_line != "":
                    print_prefix_string(prefix=">BASHCMD>", string=bash_command_line)
        already_printed_cmd = True
    # prepare cmd string
    bash_command_chained = ""
    is_first = True
    for bash_command_line in bash_command.split("\n"):
            if bash_command_line != "":
                if is_first == False:
                    bash_command_chained += " && "    
                bash_command_chained += f"{bash_command_line}"
                is_first = False
    subprocess_cmd_str = f"script -q -e -c '{bash_command_chained}' /dev/null"
    # copy env if desired
    if copy_env == True:
        # get current env
        cur_env = os.environ.copy()
        # run command with env
        completed_process = subprocess.run(
            subprocess_cmd_str,
            shell=True,
            #check=True,
            executable="/bin/bash",
            env=cur_env,
            capture_output=True,
            text=True,
        )
    else:
        # run command with env
        completed_process = subprocess.run(
            subprocess_cmd_str,
            shell=True,
            #check=True,
            executable="/bin/bash",
            capture_output=True,
            text=True,
        )
    # extract info
    retval = completed_process.returncode
    stdout = completed_process.stdout
    # stderr remains always empty due to the construction
    # print info
    if verbose >= 1 or (always_print_when_retval_not_zero == True and retval != 0):
        print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"Completed bash command with return code \"{retval}\"")
        if print_cmd == True and len(bash_command) > 0 and already_printed_cmd == False: # only print cmd once...
            for bash_command_line in bash_command.split("\n"):
                if bash_command_line != "":
                    print_prefix_string(prefix=">BASHCMD>", string=bash_command_line)
        if print_stdout == True and len(stdout) > 0:
            for stdout_line in stdout.split("\n"):
                if stdout_line != "":
                    if retval == 0:
                        print_prefix_string(prefix=">BASHOUT>", string=stdout_line)
                    else:
                        print_prefix_string(prefix=">BASHERR>", string=stdout_line, highlightcolor=color.red)
    # return info
    return retval, stdout


