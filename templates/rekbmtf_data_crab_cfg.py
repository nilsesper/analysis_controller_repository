import CRABClient
from CRABClient.UserUtilities import config
config = config()

config.General.requestName = "++++CRAB_REQUESTNAME++++" #'Scouting_2024G'

config.General.workArea = "++++CRAB_WORKAREA++++" #'crab_projects'
config.General.transferOutputs = True
config.General.transferLogs = False

config.JobType.pluginName = "Analysis"
config.JobType.psetName = "++++CMSSW_CONFIGFILE++++" #'kbmtFlatTableProducer_cfg.py'
config.JobType.allowUndistributedCMSSW = True

config.Data.inputDataset = "++++INPUT_DAS_NAME++++" #"/L1Scouting/Run2024G-v1/L1SCOUT"
config.Data.inputDBS = "global"
config.Data.splitting = "Automatic"

config.Data.lumiMask = "++++INPUT_LUMI_MASK++++" #'https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions24/Cert_Collisions2024_378981_386951_Golden.json'

config.Data.outLFNDirBase = "++++CRAB_OUTPUT_BASEDIR++++" #'/store/group/cmst3/group/slowmuons/' #"/store/user/nesper/test_analysis_hscp_l1/"

config.Data.publication = False

config.Site.storageSite = "++++CRAB_STORAGE_SITE++++" #'T2_DE_RWTH'
