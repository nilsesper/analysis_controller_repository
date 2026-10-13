# analysis_controller_repository
**Slow-moving HSCP analysis with CMS Level-1 trigger data scouting in Run-3**.  

This repository contains control and analysis scripts for the CMS L1 Scouting slow-moving HSCP EXO analysis.  

## References

The main reference analysis is CMS-EXO-25-010 ([Link to CADI line](https://cmsfence.cern.ch/alcm/cmsanalysis/details/ancode=EXO-25-010), [Link to paper](https://linkinghub.elsevier.com/retrieve/pii/S0370269326003515)), with authors Cecile Caillol and Rocco Ardino on the analysis note, which uses a fraction of the CMS Level-1 trigger data scouting dataset from 2024.  
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

