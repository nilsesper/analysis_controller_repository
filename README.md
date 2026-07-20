# analysis_controller_repository
**Slow-moving HSCP analysis with CMS Level-1 trigger data scouting in Run-3**.  

This repository contains control scripts for the CMS L1 Scouting slow-moving HSCP EXO analysis.  
It contains the scripts to submit the analysis steps, monitor them, and manage the files.  

## References

The main reference analysis is [CMS-EXO-25-010](https://cmsfence.cern.ch/alcm/cmsanalysis/details/ancode=EXO-25-010) ([Link to paper](https://linkinghub.elsevier.com/retrieve/pii/S0370269326003515)), with authors Cecile Caillol and Rocco Ardino on the analysis note, which uses a fraction of the CMS Level-1 trigger data scouting dataset from 2024.  
Their code was very kindly provided to me, and adapted accordingly for my analysis.  

## Summary of analysis workflow


## Step by step description

### Initial setup
- Install micromamba:  
    Follow instructions given in the [micromamba documentation](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html).  
    I think you can use the following command to install micromamba:  
    ```
    "${SHELL}" <(curl -L micro.mamba.pm)
    ```
- Install micromamba environment:  
    ```
    env/install-from-file_micromamba_env.sh
    ```

### Update existing installation
- Update micromamba environment:  
    ```
    env/install-from-file_micromamba_env.sh
    ```

### Setup for each new terminal
- Source the environment:  
    ```
    source env.sh
    ```

### **MC:** Drell-Yan and signal MC generation (in L1 scouting data format, including BMTF stubs)

### **Data:** CMS L1 Scouting dataset (from L1 scouting system, including BMTF stubs)

### **`rekbmtf`:** Re-run the KBMTF algorithm on the scouted BMTF stubs

#### For data:
- Prepare input config file where the datasets and the unique labels are specified:  
    > Example for `config/rekbmtf/ConfigRekbmtfInput.yaml`:
    > ```
    > RekbmtfInput:
    > 
    >     data_type: "data"
    >     data_label: "Scouting_2024H"
    >     input_das_name: "/L1Scouting/Run2024H-v1/L1SCOUT"
    >     input_lumi_mask: "https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions24/Cert_Collisions2024_378981_386951_Golden.json"
    >     input_run_range: ""
    > ```
- Prepare params config file where the parameters of the analysis step are specified:  
    > Example for `config/rekbmtf/ConfigRekbmtfParamsSubmission.yaml`:
    > ```
    > RekbmtfParamsSubmission:
    > 
    >     submission_type: cern-crab
    >     submission_splitting: automatic
    >     
    >     output_type: cern-grid
    >     output_site: T2_DE_RWTH
    >     output_basepath: /store/user/nesper/test_analysis_hscp_l1/
    > 
    >     crab_config_template_filepath: ++++ANALYSIS_CONTROLLER_REPO_PATH++++/templates_submission/crab_rekbmtf/rekbmtf_data_crab_cfg.py
    > 
    >     cmssw_src_path: ++++ANALYSIS_CONTROLLER_REPO_PATH++++/../1_reKBMTF/CMSSW_14_0_12/src/
    >     cmssw_config_template_filepath: ++++ANALYSIS_CONTROLLER_REPO_PATH++++/config_analysis/rekbmtf/rekbmtf_data_cmssw_cfg.py
    > ```
- Submit the analysis step for execution:  
    ```
    python analysis_controller/scripts_controller/rekbmtf/submit-job.py --input config/rekbmtf/ConfigRekbmtfInput.yaml --paramssubmission config/rekbmtf/ConfigRekbmtfParamsSubmission.yaml
    ```
- Now the analysis has been submitted and is running remotely.  
- In the directory `submissions/`, a subdirectory is automatically created, called `rekbmtf_{data_type_}_{data_label}_YYYY-MM-DD_hh-mm-ss/`, which in the following is referred to as `submit_path`  
- In the `submit_path`, the submit config file `ConfigRekbmtfSubmission.yaml` is stored, which holds the relevant information about the submitted task, to monitor it, and to retrieve the outputs from it  
- Also, all other related files to the submission are stored in the `submit_path`, such as the CRAB project directory, the CMSSW and CRAB config files, and others   
- Monitor the execution of the submitted analysis step, when pointing to the respective `ConfigRekbmtfSubmission.yaml` file and specifying the current analysis step:  
    ```
    python analysis_controller/scripts_controller/rekbmtf/monitor-job.py --action monitor --submission {submit_path}/ConfigRekbmtfSubmission.yaml
    ```
- Run another user-specified command `{user_command}` on the submitted analysis step, e.g. resubmission of some jobs in case of problems:
    ```
    python analysis_controller/scripts_controller/rekbmtf/monitor-job.py --action command --command {user_command} --submission {submit_path}/ConfigRekbmtfSubmission.yaml
    ```
- When the job is done, collect the output data.

### **`skimming`:** Extract relevant data and calculating higher-level quantities

### **`cleaning`:** Remove duplicate tracks

### **`classification`:** Classify the tracks in different categories and filling the histograms with track pT

### **`datacards`:** Prepare the datacards for statistical analysis with CMS Combine

### **`combine`:** Perform the statistical analysis with CMS Combine, respecting systematics, and perform limit setting

