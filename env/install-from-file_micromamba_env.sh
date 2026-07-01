#!/bin/bash

CYAN="\033[0;36m"
WHITE="\033[0;37m"
WHITEBOLD="\033[1;37m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

printf "${CYAN}+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++${RESET}\n"
printf "${CYAN}+++${WHITEBOLD} ANALYSIS_CONTROLLER: l1 scouting slow hscp analysis ${CYAN}+++${RESET}\n"
printf "${CYAN}+++${WHITE} env/install-from-file_micromamba_env.sh             ${CYAN}+++${RESET}\n"
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

printf "${YELLOW}Removing current micromamba environment.\nThis is needed because one not update an environment, but only re-install it.\nThis may take some time...${RESET}\n"

### remove current environment
yes | micromamba env remove -n micromamba_env

printf "${YELLOW}Re-installing micromamba environment from file \"env/micromamba_env.yaml\".\nThis may take some time...${RESET}\n"

### install new environment from file
yes | micromamba env create -f micromamba_env.yaml

printf "${CYAN}+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++${RESET}\n"
