################################################
echo "start bash"
InputFile=$1
OutputFile=$2
################################################
echo "parameters: InputFile=${InputFile}, OutputFile=${OutputFile}"

source /home/home1/institut_3a/esper/promotion/test_analysis_hscp_l1/analysis_controller_repository/env_no-voms.sh

python /home/home1/institut_3a/esper/promotion/test_analysis_hscp_l1/analysis_controller_repository/scripts_analysis/finalselection/finalselection_slowdata.py --input ${InputFile} --output ${OutputFile}

################################################
echo "finish bash"
################################################
