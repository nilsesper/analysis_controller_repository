#!/bin/bash

CURRENT_WORKING_DIR="`pwd`"
###################################

cd /home/home1/institut_3a/esper/promotion/test_analysis_hscp_l1/analysis_controller_repository/scripts_analysis/skimming/condor_test/
condor_submit condor_submit.sub

###################################
cd ${CURRENT_WORKING_DIR}
