##############################
### PLOTTING
##############################

############################
### IMPORTS

import os
import uproot
import awkward as ak
import numba as nb
import numpy as np
import time
import argparse
import copy
import matplotlib as mpl
import matplotlib.pyplot as plt
import mplhep as mh

from analysis_controller.src import path_utils
from analysis_controller.src import file_utils
from analysis_controller.src import console_utils
from analysis_controller.src import analysis_utils
from analysis_controller.src import analysis_params
from analysis_controller.src import hist_utils
from analysis_controller.src import plot_utils

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_PATH, _ANALYSIS_CONTROLLER_REPO_PATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)
console_utils.print_console_header(analysis_controller_filepath=_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH)

start_time = time.time()
mh.style.use("CMS")

#############################
### ARGUMENT PARSER

parser = argparse.ArgumentParser()
# mandatory:
parser.add_argument(
    "--input",
    help="path to input root file (str)",
    type=str,
    required=True,
)
# optional:
#
args = parser.parse_args()

#############################
#****************************
### MAIN PART

### parse args
infile_path = args.input

#############################
### IMPORT DATA

### import root file
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Opening input ROOT file from \"{infile_path}\"")
infile = uproot.open(infile_path)

### extract "Events" root tree
roottree = infile["Events"]
roottree_branches = roottree.keys()
#console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"ROOT tree \"Events\" contains branches {roottree_branches}")

### convert root tree to awkward array
arr = roottree.arrays(roottree_branches)
arr = ak.with_name(arr, name="Events")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Converting ROOT tree \"Events\" to awkward array")
row_indices = ak.local_index(arr, axis=0)
n_entries = len(row_indices)
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The imported dataset has \"{n_entries:,}\" events")

#############################
### CREATE HISTOGRAM

###--------------------------
### define bins

low_edge = 10
high_edge = 100
# num_bins = 50
target_bin_width = 2
n_bins = (high_edge-low_edge)//target_bin_width

HistEdges = hist_utils.create_HistEdges_uniform(low_edge=low_edge, high_edge=high_edge, n_bins=n_bins)

data_pts = np.array(arr.pt1)
DataPts = hist_utils.create_DataPts(data_pts=data_pts)

###--------------------------
### create hist with numpy

fig, ax = plt.subplots(1, 1)
PlotHistParams = plot_utils.StructPlotHistParams(
    ax=ax,
    HistEdges=HistEdges,
    show_uf=True,
    show_of=True,
    xlabel=f"$p_{{T}}(\\mu_{{1}})$ [GeV]",
    ylabel=None,
    xscale="norm",
    yscale="log",
    xlim=None,
    ylim=None
)

PlotHistAx = plot_utils.create_PlotHistAx_from_PlotHistParams(PlotHistParams=PlotHistParams)

NpHist = hist_utils.create_NpHist(HistEdges=HistEdges, DataPts=DataPts)

###--------------------------
### create hist with pyroot

# RootHist = hist_utils.create_RootHist(HistEdges=HistEdges, DataPts=DataPts)

###--------------------------
### generic

# NpHist = hist_utils.convert_RootHist_to_NpHist(RootHist=RootHist)

edges = NpHist.HistEdges.edges
hist_ou = NpHist.hist_ou
uf, hist, of = NpHist.uf, NpHist.hist, NpHist.of
err_hist_ou = NpHist.err_hist_ou
err_uf, err_hist, err_of = NpHist.err_uf, NpHist.err_hist, NpHist.err_of

#############################
### PLOT HISTOGRAM

plot_utils.add_NpHist_to_PlotHistAx(NpHist=NpHist, PlotHistAx=PlotHistAx)

fig.show()

#****************************
#############################

stop_time = time.time()
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The execution took \"{(stop_time - start_time):03f} seconds\"")
console_utils.print_console_footer()

input("Press [Enter] to exit")
