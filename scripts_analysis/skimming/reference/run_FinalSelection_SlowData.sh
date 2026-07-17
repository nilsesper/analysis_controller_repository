#!/bin/bash

InputFile=$1
OutputFile=$2

#>>>>> usage example: >>>>>>>>>>>>>>>
# source  scripts_analysis/skimming/reference/run_FinalSelection_SlowData.sh {InputFile.root} {OutputFile.root}
#
# source scripts_analysis/skimming/reference/run_FinalSelection_SlowData.sh scripts_analysis/skimming/test_files/input_test_0.root scripts_analysis/skimming/test_files/ref_output_test_0.root
#
## source scripts_analysis/skimming/reference/run_FinalSelection_SlowData.sh scripts_analysis/skimming/test_files/input_large_test_0.root scripts_analysis/skimming/test_files/ref_output_large_test_0.root
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

printf "${GREEN}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>${RESET}\n"
printf "${GREEN}>>>>>>${WHITEBOLD} ANALYSIS_CONTROLLER_REPOSITORY: l1 scouting slow hscp analysis ${RESET}\n"
printf "${GREEN}>>>>>>${WHITE} run_FinalSelection_SlowData.sh ${RESET}\n"

printf "${GREEN}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>${RESET}\n"
printf "${GREEN}>>>>>> ${WHITE} SOURCING ENVIRONMENT ${RESET}\n"
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /home/home1/institut_3a/esper/promotion/test_analysis_hscp_l1/2_HSCPanalysis/CMSSW_14_0_12/src/
cmsenv

printf "${GREEN}>>>>>> ${WHITE} STARTING SCRIPT AND TIMING IT ${RESET}\n"
cd /home/home1/institut_3a/esper/promotion/test_analysis_hscp_l1/2_HSCPanalysis/CMSSW_14_0_12/src/L1ScoutingAnalysisRDataFrame/NtupleAnalyzer/scripts/
/usr/bin/time --verbose python3 FinalSelection_SlowData.py ${InputFilePath} ${OutputFilePath}

printf "${GREEN}>>>>>> ${WHITE} DONE ${RESET}\n"
cd ${CURRENT_WORKING_DIR}

printf "${GREEN}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>${RESET}\n"
