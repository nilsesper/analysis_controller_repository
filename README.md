# analysis_controller_repository  

This repository contains control scripts for the CMS L1 Scouting slow-moving HSCP EXO analysis.  

It contains the scripts to submit the analysis steps, monitor them, and manage the files.  

## References

The analysis uses CMS [EXO-25-010](https://cmsfence.cern.ch/alcm/cmsanalysis/details/ancode=EXO-25-010) ([Paper](https://linkinghub.elsevier.com/retrieve/pii/S0370269326003515)), with authors Cecile Caillol and Rocco Ardino on the AN, as reference.  
The analysis code is also provided from them, and adapted accordingly for my analysis.  

## Summary of analysis workflow


## Step by step description

### **MC:** Drell-Yan and signal MC generation

### **Data:** CMS L1 Scouting dataset

### **`reKBMTF`:** Re-run the KBMTF algorithm

### **`skimming`:** Extract relevant data and calculating higher-level quantities

### **`cleaning`:** Remove duplicate tracks

### **`classification`:** Classify the tracks in different categories and filling the histograms with track pT

### **`datacards`:** Prepare the datacards for statistical analysis with CMS Combine

### **`combine`:** Perform the statistical analysis with CMS Combine, respecting systematics, and perform limit setting

