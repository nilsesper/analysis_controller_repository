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
    "--input1",
    help="path to input root file 1 (str)",
    type=str,
    required=True,
)
parser.add_argument(
    "--input2",
    help="path to input root file 2 (str)",
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
infile_paths = [args.input1, args.input2]
n_files = 2

#############################
### IMPORT DATA

arrs = []
for i_file in range(n_files):
    infile_path = infile_paths[i_file]
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
    ###
    arrs.append(arr)

#############################
### CREATE HISTOGRAM

###--------------------------
### define bins

low_edge = 0
high_edge = 1200

n_bins = 50

# target_bin_width = 50
# n_bins = (high_edge-low_edge)//target_bin_width

HistEdges = hist_utils.create_HistEdges_uniform(low_edge=low_edge, high_edge=high_edge, n_bins=n_bins)

arr_DataPts = []
for i_file in range(n_files):
    arr = arrs[i_file]
    data_pts = np.array(arr.pt1)
    DataPts = hist_utils.create_DataPts(data_pts=data_pts)
    arr_DataPts.append(DataPts)

###--------------------------
### create hist with numpy

arr_NpHist = []
for i_file in range(n_files):
    DataPts = arr_DataPts[i_file]
    NpHist = hist_utils.create_NpHist(HistEdges=HistEdges, DataPts=DataPts)
    arr_NpHist.append(NpHist)

### bin by bin difference

difference_hist_ou = copy.deepcopy( arr_NpHist[0].hist_ou - arr_NpHist[1].hist_ou )
difference_err_hist_ou = np.zeros(len(difference_hist_ou))
difference_NpHist = hist_utils.StructNpHist(HistEdges=HistEdges, hist_ou=difference_hist_ou, err_hist_ou=difference_err_hist_ou)

difference_err_hist_ou = copy.deepcopy( arr_NpHist[0].err_hist_ou - arr_NpHist[1].err_hist_ou )
difference_err_err_hist_ou = np.zeros(len(difference_err_hist_ou))
difference_NpHist_err = hist_utils.StructNpHist(HistEdges=HistEdges, hist_ou=difference_err_hist_ou, err_hist_ou=difference_err_err_hist_ou)

#############################
### PLOT HISTOGRAM

### linear scale
fig, ax = plt.subplots(1, 1)
PlotHistAxParams = plot_utils.StructPlotHistAxParams(
    ax=ax,
    HistEdges=HistEdges,
    show_uf=True,
    show_of=True,
    xlabel=f"$p_{{T}}(\\mu_{{1}})$ [GeV]",
    yscale="linear",
    show_legend=True,
)
PlotHistAx = plot_utils.create_PlotHistAx_from_PlotHistAxParams(PlotHistAxParams=PlotHistAxParams)
for i_file in range(n_files):
    NpHist = arr_NpHist[i_file]
    PlotHistParams = plot_utils.StructPlotHistParams(
        label=f"Data_{i_file+1}",
        color=plot_utils.get_color_from_ColorWheel(index=i_file),
        show_in_legend=True,
    )
    PlotHistAx = plot_utils.add_NpHist_to_PlotHistAx(NpHist=NpHist, PlotHistAx=PlotHistAx, PlotHistParams=PlotHistParams)
fig.show()

### log scale
fig, ax = plt.subplots(1, 1)
PlotHistAxParams = plot_utils.StructPlotHistAxParams(
    ax=ax,
    HistEdges=HistEdges,
    show_uf=True,
    show_of=True,
    xlabel=f"$p_{{T}}(\\mu_{{1}})$ [GeV]",
    yscale="log",
    show_legend=True,
)
PlotHistAx = plot_utils.create_PlotHistAx_from_PlotHistAxParams(PlotHistAxParams=PlotHistAxParams)
for i_file in range(n_files):
    NpHist = arr_NpHist[i_file]
    PlotHistParams = plot_utils.StructPlotHistParams(
        label=f"Data_{i_file+1}",
        color=plot_utils.get_color_from_ColorWheel(index=i_file),
        show_in_legend=True,
    )
    PlotHistAx = plot_utils.add_NpHist_to_PlotHistAx(NpHist=NpHist, PlotHistAx=PlotHistAx, PlotHistParams=PlotHistParams)
fig.show()

### linear scale difference
fig, ax = plt.subplots(1, 1)
PlotHistAxParams = plot_utils.StructPlotHistAxParams(
    ax=ax,
    HistEdges=HistEdges,
    show_uf=True,
    show_of=True,
    xlabel=f"$p_{{T}}(\\mu_{{1}})$ [GeV]",
    yscale="linear",
    show_legend=True,
)
PlotHistAx = plot_utils.create_PlotHistAx_from_PlotHistAxParams(PlotHistAxParams=PlotHistAxParams)
PlotHistParams = plot_utils.StructPlotHistParams(
    label="Data_1 $-$ Data_2",
    color=plot_utils.get_color_from_ColorWheel(),
    show_in_legend=True,
)
PlotHistAx = plot_utils.add_NpHist_to_PlotHistAx(NpHist=difference_NpHist, PlotHistAx=PlotHistAx, PlotHistParams=PlotHistParams)
fig.show()

### linear scale error difference
fig, ax = plt.subplots(1, 1)
PlotHistAxParams = plot_utils.StructPlotHistAxParams(
    ax=ax,
    HistEdges=HistEdges,
    show_uf=True,
    show_of=True,
    xlabel=f"$p_{{T}}(\\mu_{{1}})$ [GeV]",
    yscale="linear",
    show_legend=True,
)
PlotHistAx = plot_utils.create_PlotHistAx_from_PlotHistAxParams(PlotHistAxParams=PlotHistAxParams)
PlotHistParams = plot_utils.StructPlotHistParams(
    label="Data_1_err $-$ Data_2_err",
    color=plot_utils.get_color_from_ColorWheel(),
    show_in_legend=True,
)
PlotHistAx = plot_utils.add_NpHist_to_PlotHistAx(NpHist=difference_NpHist_err, PlotHistAx=PlotHistAx, PlotHistParams=PlotHistParams)
fig.show()

#****************************
#############################

stop_time = time.time()
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The execution took \"{(stop_time - start_time):03f} seconds\"")
console_utils.print_console_footer()

input("Press [Enter] to exit")
