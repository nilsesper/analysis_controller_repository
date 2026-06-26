#!/bin/bash

CYAN="\033[0;36m"
WHITE="\033[0;37m"
WHITEBOLD="\033[1;37m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

printf "${CYAN}+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++${RESET}\n"
printf "${CYAN}+++${WHITEBOLD} ANALYSIS_CONTROLLER: l1 scouting slow hscp analysis ${CYAN}+++${RESET}\n"
printf "${CYAN}+++${WHITE} ./env.sh                                            ${CYAN}+++${RESET}\n"
printf "${CYAN}+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++${RESET}\n"

printf "Locating the analysis_controller directory.\n"

# find script abs path when not executing but sourcing the script
# (taken from https://stackoverflow.com/questions/4774054/reliable-way-for-a-bash-script-to-get-the-full-path-to-itself)
SCRIPT_PATH="${BASH_SOURCE[0]}";
while([ -h "${SCRIPT_PATH}" ]); do
    cd "`dirname "${SCRIPT_PATH}"`"
    SCRIPT_PATH="$(readlink "`basename "${SCRIPT_PATH}"`")";
done
cd "`dirname "${SCRIPT_PATH}"`" > /dev/null
SCRIPT_PATH="`pwd`";
REPO_PATH=$SCRIPT_PATH
printf "  ANALYSIS_CONTROLLER_PATH = ${REPO_PATH}\n"

printf "Adding variables to PYTHONPATH.\n"

# add repo directory (minicrate-testing-software) to pythonpath
export PYTHONPATH="${PYTHONPATH}:${REPO_PATH}"
printf "  PYTHONPATH += ${REPO_PATH}\n"

# source cms base env
source /cvmfs/cms.cern.ch/cmsset_default.sh

# init voms proxy
voms-proxy-init --rfc --voms cms -valid 192:00

printf "${CYAN}+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++${RESET}\n"
