#!/bin/bash

InputFile=$1
OutputFile=$2
ParamsFile=$3

#>>>>> usage example: >>>>>>>>>>>>>>>
# source scripts_analysis/skimming/run_skimming_data.sh {InputFile.root} {OutputFile.root} {SkimmingParamsAnalysis.yaml}
#
# source scripts_analysis/skimming/run_skimming_data.sh scripts_analysis/skimming/test_files/input_test_0.root scripts_analysis/skimming/test_files/output_test_0_nocuts.root config_analysis/skimming/SkimmingParamsAnalysis_data.yaml
#
# source scripts_analysis/skimming/run_skimming_data.sh scripts_analysis/skimming/test_files/input_large_test_0.root scripts_analysis/skimming/test_files/output_large_test_0_nocuts.root config_analysis/skimming/SkimmingParamsAnalysis_data.yaml
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

CYAN="\033[0;36m"
WHITE="\033[0;37m"
WHITEBOLD="\033[1;37m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
GREEN="\033[0;32m"
RESET="\033[0m"

CURRENT_WORKING_DIR="`pwd`"
InputFilePath="`realpath -s ${InputFile}`"
OutputFilePath="`realpath -s ${OutputFile}`"
ParamsFilePath="`realpath -s ${ParamsFile}`"


printf "${GREEN}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>${RESET}\n"
printf "${GREEN}>>>>>>${WHITEBOLD} ANALYSIS_CONTROLLER_REPOSITORY: l1 scouting slow hscp analysis ${RESET}\n"
printf "${GREEN}>>>>>>${WHITE} run_skimming_data.sh ${RESET}\n"

printf "${GREEN}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>${RESET}\n"
printf "${GREEN}>>>>>> ${WHITE} SOURCING ENVIRONMENT ${RESET}\n"
cd /home/home1/institut_3a/esper/promotion/test_analysis_hscp_l1/analysis_controller_repository/
source env_no-voms.sh

printf "${GREEN}>>>>>> ${WHITE} STARTING SCRIPT AND TIMING IT ${RESET}\n"
cd /home/home1/institut_3a/esper/promotion/test_analysis_hscp_l1/analysis_controller_repository/scripts_analysis/skimming/
/usr/bin/time --verbose  python skimming_data.py --input ${InputFilePath} --output ${OutputFilePath} --params ${ParamsFilePath}

printf "${GREEN}>>>>>> ${WHITE} DONE ${RESET}\n"
cd ${CURRENT_WORKING_DIR}

printf "${GREEN}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>${RESET}\n"
