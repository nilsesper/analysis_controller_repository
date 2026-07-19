#!/bin/bash

RESET="\033[0m"
BLACK='\033[0;30m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'
BGBLACK='\033[0;40m'
BGRED='\033[0;41m'
BGGREEN='\033[0;42m'
BGYELLOW='\033[0;43m'
BGBLUE='\033[0;44m'
BGPRUPLE='\033[0;45m'
BGCYAN='\033[0;46m'
BGWHITE='\033[0;47m'

printf "${CYAN}++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++${RESET}\n"
printf "${CYAN}+++${WHITEBOLD} ANALYSIS_CONTROLLER_REPOSITORY: l1 scouting slow hscp analysis ${CYAN}+++${RESET}\n"
printf "${CYAN}+++${WHITE} env.sh                                                         ${CYAN}+++${RESET}\n"
printf "${CYAN}++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++${RESET}\n"
#                                                                              |{CYAN}

printf "${YELLOW}Locating the repository directory and change working directory into it.${RESET}\n"

### store original path
CURRENT_WORKING_DIR="`pwd`"
printf "  CURRENT_WORKING_DIR = ${CURRENT_WORKING_DIR}\n"

### find script abs path when not executing but sourcing the script and cd into it
# (taken from https://stackoverflow.com/questions/4774054/reliable-way-for-a-bash-script-to-get-the-full-path-to-itself)
SCRIPT_PATH="${BASH_SOURCE[0]}";
while([ -h "${SCRIPT_PATH}" ]); do
    cd "`dirname "${SCRIPT_PATH}"`"
    SCRIPT_PATH="$(readlink "`basename "${SCRIPT_PATH}"`")";
done
cd "`dirname "${SCRIPT_PATH}"`" > /dev/null
SCRIPT_PATH="`pwd`"

### export path of this script (which is into the top dir of the repo) as REPO_PATH
REPO_PATH=$SCRIPT_PATH
printf "  ANALYSIS_CONTROLLER_PATH = ${REPO_PATH}\n"

### init micromamba
printf "${YELLOW}Initializing micromamba environment manager.${RESET}\n"
source env/init_micromamba.sh

### activate micromamba env
printf "${YELLOW}Activating micromamba environment.${RESET}\n"
source env/activate_micromamba_env.sh

### add variables to pythonpath
printf "${YELLOW}Adding variables to PYTHONPATH.${RESET}\n"
# add repo directory (minicrate-testing-software) to pythonpath
export PYTHONPATH="${PYTHONPATH}:${REPO_PATH}"
printf "  PYTHONPATH += ${REPO_PATH}\n"

### source cms base env
printf "${YELLOW}Sourcing CMS base environment \"cmsset_default.sh\".${RESET}\n"
source /cvmfs/cms.cern.ch/cmsset_default.sh

### go back to original working dir
printf "${YELLOW}Going back to original working directory.${RESET}\n"
cd ${CURRENT_WORKING_DIR}
NEW_WORKING_DIR="`pwd`"
printf "  NEW_WORKING_DIR = ${NEW_WORKING_DIR}\n"

printf "${CYAN}++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++${RESET}\n"
