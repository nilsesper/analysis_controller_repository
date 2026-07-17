#!/bin/bash

Executable=$1
OtherArgs=("${@:2}")

echo "[condor_exec] Start condor_exec.sh"
echo "[condor_exec] Executable = ${Executable}"
echo "[condor_exec] Additional arguments = ${OtherArgs[@]}"
echo "[condor_exec] Start executable with the following command \"source ${Executable} ${OtherArgs[@]}\""
source ${Executable} ${OtherArgs[@]}
echo "[condor_exec] Finished executable"
echo "[condor_exec] finish condor_exec.sh"
