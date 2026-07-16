################################################
echo "[condor_exec] start condor_exec.sh"
echo "[condor_exec] got $# arguments: $@"
ClusterId=$1
ProcId=$2
echo "[condor_exec] job info: ClusterId=${ClusterId}, ProcId=${ProcId}"
################################################

ExecutableFile="++++EXECUTABLE_FILE++++"

InputFile="++++INPUT_FILE++++"
# InputFile="input-ClusterId${ClusterId}-ProcId${ProcId}"

OutputFile="++++OUTPUT_FILE++++"
# OutputFile="output-ClusterId${ClusterId}-ProcId${ProcId}"

sh ${ExecutableFile} ${InputFile} ${OutputFile}

################################################
echo "[condor_exec] finish condor_exec.sh"
################################################
