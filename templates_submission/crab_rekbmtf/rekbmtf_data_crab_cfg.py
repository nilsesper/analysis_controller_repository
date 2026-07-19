import CRABClient
from CRABClient.UserUtilities import config
config = config()

config.General.requestName = "++++CRAB_REQUESTNAME++++"

config.General.workArea = "++++CRAB_WORKAREA++++"
config.General.transferOutputs = True
config.General.transferLogs = False

config.JobType.pluginName = "Analysis"
config.JobType.psetName = "++++CMSSW_CONFIGFILE++++"
config.JobType.allowUndistributedCMSSW = True

config.Data.inputDataset = "++++INPUT_DAS_NAME++++"
config.Data.inputDBS = "global"
config.Data.splitting = "Automatic"

config.Data.lumiMask = "++++INPUT_LUMI_MASK++++"
config.Data.runRange = "++++INPUT_RUN_RANGE++++"

config.Data.outLFNDirBase = "++++CRAB_OUTPUT_BASEDIR++++"

config.Data.publication = False

config.Site.storageSite = "++++CRAB_STORAGE_SITE++++"
