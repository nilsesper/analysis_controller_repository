#!/bin/bash

CYAN="\033[0;36m"
WHITE="\033[0;37m"
WHITEBOLD="\033[1;37m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

printf "${CYAN}+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++${RESET}\n"
printf "${CYAN}+++${WHITEBOLD} ANALYSIS_CONTROLLER: l1 scouting slow hscp analysis ${CYAN}+++${RESET}\n"
printf "${CYAN}+++${WHITE} env/export-to-file_micromamba_env.sh                ${CYAN}+++${RESET}\n"
printf "${CYAN}+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++${RESET}\n"
#                                                                              |{CYAN}

### find script abs path when not executing but sourcing the script and cd into it
# (taken from https://stackoverflow.com/questions/4774054/reliable-way-for-a-bash-script-to-get-the-full-path-to-itself)
SCRIPT_PATH="${BASH_SOURCE[0]}";
while([ -h "${SCRIPT_PATH}" ]); do
    cd "`dirname "${SCRIPT_PATH}"`"
    SCRIPT_PATH="$(readlink "`basename "${SCRIPT_PATH}"`")";
done
cd "`dirname "${SCRIPT_PATH}"`" > /dev/null
SCRIPT_PATH="`pwd`";

printf "${YELLOW}Initializing micromamba environment manager.${RESET}\n"

### initialize micromamba
source init_micromamba.sh

printf "${YELLOW}Exporting current micromamba environment to file \"env/micromamba_env.yaml\".${RESET}\n"

### export current micromamba env to file
micromamba env export > micromamba_env.yaml

printf "${CYAN}+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++${RESET}\n"
