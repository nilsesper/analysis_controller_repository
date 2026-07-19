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
printf "${CYAN}+++${WHITE} env/export-to-file_micromamba_env.sh                           ${CYAN}+++${RESET}\n"
printf "${CYAN}++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++${RESET}\n"
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

printf "${CYAN}++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++${RESET}\n"
