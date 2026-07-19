#!/bin/bash

InputFile=$1
OutputFile=$2
ParamsFile=$3

ClusterId=$4
ProcId=$5

#>>>>> usage example: >>>>>>>>>>>>>>>
# source scripts_analysis/skimming/run_skimming_data.sh {InputFile.root} {OutputFile.root} {SkimmingParamsAnalysis.yaml}
#
# source scripts_analysis/skimming/run_skimming_data.sh scripts_analysis/skimming/test_files/input_test_0.root scripts_analysis/skimming/test_files/output_test_0_nocuts.root config_analysis/skimming/SkimmingParamsAnalysis_data.yaml
#
# source scripts_analysis/skimming/run_skimming_data.sh scripts_analysis/skimming/test_files/input_large_test_0.root scripts_analysis/skimming/test_files/output_large_test_0_nocuts.root config_analysis/skimming/SkimmingParamsAnalysis_data.yaml
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

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

CURRENT_WORKING_DIR="`pwd`"

InputFilePath="`realpath -s ${InputFile}`"
OutputFilePath="`realpath -s ${OutputFile}`"
ParamsFilePath="`realpath -s ${ParamsFile}`"


printf "${GREEN}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>${RESET}\n"
printf "${GREEN}>>>>>>${WHITEBOLD} ANALYSIS_CONTROLLER_REPOSITORY: l1 scouting slow hscp analysis ${RESET}\n"
printf "${GREEN}>>>>>>${WHITE} run_skimming_data.sh ${RESET}\n"

printf "${GREEN}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>${RESET}\n"
printf "${GREEN}>>>>>> ${WHITE} BASIC INFO ${RESET}\n"
printf "${GREEN}>>>>>> ${WHITE}   InputFile = ${InputFile} ${RESET}\n"
printf "${GREEN}>>>>>> ${WHITE}   OutputFile = ${OutputFile} ${RESET}\n"
printf "${GREEN}>>>>>> ${WHITE}   ParamsFile = ${ParamsFile} ${RESET}\n"
printf "${GREEN}>>>>>> ${WHITE}   ClusterId = ${ClusterId} ${RESET}\n"
printf "${GREEN}>>>>>> ${WHITE}   ProcId = ${ProcId} ${RESET}\n"

printf "${GREEN}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>${RESET}\n"
printf "${GREEN}>>>>>> ${WHITE} SOURCING ENVIRONMENT ${RESET}\n"

cd /home/home1/institut_3a/esper/promotion/test_analysis_hscp_l1/analysis_controller_repository/
source env_no-voms.sh

printf "${GREEN}>>>>>> ${WHITE} STARTING SCRIPT AND TIMING IT ${RESET}\n"

cd /home/home1/institut_3a/esper/promotion/test_analysis_hscp_l1/analysis_controller_repository/scripts_analysis/skimming/
python skimming_data.py --input ${InputFilePath} --output ${OutputFilePath} --params ${ParamsFilePath}

printf "${GREEN}>>>>>> ${WHITE} DONE ${RESET}\n"
cd ${CURRENT_WORKING_DIR}
printf "${GREEN}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>${RESET}\n"
