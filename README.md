# analysis_controller_repository  

This repository contains control scripts for the CMS L1 Scouting slow-moving HSCP EXO analysis.  

It contains the scripts to submit the analysis steps, monitor them, and manage the files.  

## References

The analysis uses CMS [EXO-25-010](https://cmsfence.cern.ch/alcm/cmsanalysis/details/ancode=EXO-25-010) ([Paper](https://linkinghub.elsevier.com/retrieve/pii/S0370269326003515)), with authors Cecile Caillol and Rocco Ardino on the AN, as reference.  
The analysis code is also provided from them, and adapted accordingly for my analysis.  

## Summary of analysis workflow


## Step by step description

### Initial setup

### Setup for each new terminal
- Source the environment:
    ```
    source env.sh
    ```

### **MC:** Drell-Yan and signal MC generation

### **Data:** CMS L1 Scouting dataset

### **`reKBMTF`:** Re-run the KBMTF algorithm

#### For data:
- Prepare input config file where the datasets and the unique labels are specified:
    > File contents of `analysis_controller/config/rekbmtf_input_config.yaml`:
    > ```
    > rekbmtf_input:
    >
    > -   data_type: "data" # type of data: "data", "background", "signal" etc.
    >     data_label: "Scouting_2024I" # assign custom label
    >     input_das_name: "/L1Scouting/Run2024I-v1/L1SCOUT" # cms das key of data
    >     input_lumi_mask: "https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions24/Cert_Collisions2024_378981_386951_Golden.json" # run / luminosity section mask file ("golden json")
    > ```
- Prepare params config file where the parameters of the analysis step are specified:
    > File contents of `analysis_controller/config/rekbmtf_params_config.yaml`:
    > ```
    > rekbmtf_params: # params are specified separately for each "data_type"
    >
    >     data:
    >         submission_type: "cern-crab" # job submission evironment: "cern-crab", "aachen-condor"
    >         submission_splitting: "automatic" # job splitting specification (only for "cern-crab")
    >         
    >         output_type: "cern-grid" # output type of data from the jobs: "cern-grid", "aachen-netdir"
    >         output_site: "T2_DE_RWTH" # output site name (only for "cern-grid")
    >         output_basepath: "/store/user/nesper/test_analysis_hscp_l1/" # output base path, where the files are stored
    > 
    >         crab_config_template_filepath: "%%%ANALYSIS_CONTROLLER%%%/templates/rekbmtf_data_crab_cfg.py" # crab .py template file for the job to be submitted (some wildcards in this template may be filled automatically with the params given in the config)
    > 
    >         cmssw_src_path: "%%%ANALYSIS_CONTROLLER%%%/../../1_reKBMTF/CMSSW_14_0_12/src/" # cmssw src directory (CMSSW_X_X_XX/src directory), where the cmsenv command is executed
    >         cmssw_config_template_filepath: "%%%ANALYSIS_CONTROLLER%%%/templates/rekbmtf_data_cmssw_cfg.py" # cmssw _cfg.py template file for the job to be submitted (some wildcards in this template may be filled automatically with the params given in the config)
    > ```
- Submit the analysis step for execution:
    ```
    python analysis_controller/scripts/rekbmtf_submit.py --input_config analysis_controller/config/rekbmtf_input.yaml --params_config analysis_controller/config/rekbmtf_params.yaml
    ```
- Now the analysis has been submitted and is running (remotely). The related files (config files, CRAB directory) as well as the submit config are automatically stored in the directory `analysis_controller/submissions/` in the following subdirectory: `rekbmtf_YYYY-MM-DD_hh-mm-ss_{data/mc}_{data_label}/`
- Monitor the execution of the submitted analysis step:
    ```
    python analysis_controller/scripts/monitor_submission.py --step rekbmtf --submit_config analysis_controller/submissions/rekbmtf_2026-06-25_18-21-34_data_Scouting_2024G/submit_config.yaml
    ```

### **`skimming`:** Extract relevant data and calculating higher-level quantities

### **`cleaning`:** Remove duplicate tracks

### **`classification`:** Classify the tracks in different categories and filling the histograms with track pT

### **`datacards`:** Prepare the datacards for statistical analysis with CMS Combine

### **`combine`:** Perform the statistical analysis with CMS Combine, respecting systematics, and perform limit setting

