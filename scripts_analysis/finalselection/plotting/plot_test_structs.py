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

### bin edges
low_edge = 10
high_edge = 100
# num_bins = 50
target_bin_width = 2
n_bins = (high_edge-low_edge)//target_bin_width
HistEdges = hist_utils.create_HistEdges_uniform(low_edge=low_edge, high_edge=high_edge, n_bins=n_bins)

### data points
data_pts = arr.pt1
common_weight = 0.5
data_weights = np.ones(len(data_pts))*common_weight
data_pts = np.array(arr.pt1)
DataPts = hist_utils.create_DataPts(data_pts=data_pts, data_weights=data_weights)

### create NpHist
NpHist1 = hist_utils.create_NpHist(HistEdges=HistEdges, DataPts=DataPts)
NpHist2 = hist_utils.create_NpHist(HistEdges=HistEdges, DataPts=DataPts)
NpHist = hist_utils.linear_combination_NpHists(NpHists=[NpHist1, NpHist1], factors=[1,2])

### create RootHist
RootHist1 = hist_utils.create_RootHist(HistEdges=HistEdges, DataPts=DataPts)
RootHist2 = hist_utils.create_RootHist(HistEdges=HistEdges, DataPts=DataPts)
RootHist = hist_utils.linear_combination_RootHists(RootHists=[RootHist1, RootHist2], factors=[1,2])
# in the end convert only final RootHist to NpHist (for plotting)
NpHist_from_RootHist = hist_utils.convert_RootHist_to_NpHist(RootHist=RootHist)

### calculate bin by bin difference
diff_hist_ou = copy.deepcopy( NpHist.hist_ou - NpHist_from_RootHist.hist_ou )
diff_err_hist_ou = copy.deepcopy( np.sqrt( NpHist.hist_ou**2 + NpHist_from_RootHist.hist_ou**2 ) )
NpHist_diff = hist_utils.StructNpHist(HistEdges=HistEdges, hist_ou=diff_hist_ou, err_hist_ou=diff_err_hist_ou)
# calculate also bin by bin difference in error
diff_err_hist_ou = copy.deepcopy( NpHist.err_hist_ou - NpHist_from_RootHist.err_hist_ou )
diff_err_err_hist_ou = copy.deepcopy( np.sqrt( NpHist.err_hist_ou**2 + NpHist_from_RootHist.err_hist_ou**2 ) )
NpHist_diff_err = hist_utils.StructNpHist(HistEdges=HistEdges, hist_ou=diff_err_hist_ou, err_hist_ou=diff_err_err_hist_ou)

#############################
### PLOT HISTOGRAM

### plot hists on top of each other -> linear scape
fig, ax = plt.subplots(1, 1)
PlotHistAxParams = plot_utils.StructPlotHistAxParams(
    ax=ax,
    HistEdges=HistEdges,
    show_uf=True,
    show_of=True,
    yscale="linear",
    show_legend=True,
)
PlotHistAx = plot_utils.create_PlotHistAx_from_PlotHistAxParams(PlotHistAxParams=PlotHistAxParams)
PlotHistParams = plot_utils.StructPlotHistParams(
    label="NpHist",
    color=plot_utils.get_color_from_ColorWheel(index=0),
    show_in_legend=True,
)
PlotHistAx = plot_utils.add_NpHist_to_PlotHistAx(NpHist=NpHist, PlotHistAx=PlotHistAx, PlotHistParams=PlotHistParams)

PlotHistParams = plot_utils.StructPlotHistParams(
    label="NpHist_from_RootHist",
    color=plot_utils.get_color_from_ColorWheel(index=1),
    show_in_legend=True,
)
PlotHistAx = plot_utils.add_NpHist_to_PlotHistAx(NpHist=NpHist_from_RootHist, PlotHistAx=PlotHistAx, PlotHistParams=PlotHistParams)
fig.show()

### plot hists on top of each other -> log scale
fig, ax = plt.subplots(1, 1)
PlotHistAxParams = plot_utils.StructPlotHistAxParams(
    ax=ax,
    HistEdges=HistEdges,
    show_uf=True,
    show_of=True,
    yscale="log",
    show_legend=True,
)
PlotHistAx = plot_utils.create_PlotHistAx_from_PlotHistAxParams(PlotHistAxParams=PlotHistAxParams)
PlotHistParams = plot_utils.StructPlotHistParams(
    label="NpHist",
    color=plot_utils.get_color_from_ColorWheel(index=0),
    show_in_legend=True,
)
PlotHistAx = plot_utils.add_NpHist_to_PlotHistAx(NpHist=NpHist, PlotHistAx=PlotHistAx, PlotHistParams=PlotHistParams)

PlotHistParams = plot_utils.StructPlotHistParams(
    label="NpHist_from_RootHist",
    color=plot_utils.get_color_from_ColorWheel(index=1),
    show_in_legend=True,
)
PlotHistAx = plot_utils.add_NpHist_to_PlotHistAx(NpHist=NpHist_from_RootHist, PlotHistAx=PlotHistAx, PlotHistParams=PlotHistParams)
fig.show()

### plot difference between hist bin by bin -> linear scale, respect yerr for ylim
fig, ax = plt.subplots(1, 1)
PlotHistAxParams = plot_utils.StructPlotHistAxParams(
    ax=ax,
    HistEdges=HistEdges,
    show_uf=True,
    show_of=True,
    yscale="linear",
    show_legend=True,
    auto_ylim_respect_err=True,
)
PlotHistAx = plot_utils.create_PlotHistAx_from_PlotHistAxParams(PlotHistAxParams=PlotHistAxParams)
PlotHistParams = plot_utils.StructPlotHistParams(
    label="NpHist $-$ NpHist_from_RootHist",
    color=plot_utils.get_color_from_ColorWheel(index=0),
    show_in_legend=True,
)
PlotHistAx = plot_utils.add_NpHist_to_PlotHistAx(NpHist=NpHist_diff, PlotHistAx=PlotHistAx, PlotHistParams=PlotHistParams)
fig.show()

### plot difference between hist bin by bin -> linear scale, dont respect yerr for ylim
fig, ax = plt.subplots(1, 1)
PlotHistAxParams = plot_utils.StructPlotHistAxParams(
    ax=ax,
    HistEdges=HistEdges,
    show_uf=True,
    show_of=True,
    yscale="linear",
    show_legend=True,
)
PlotHistAx = plot_utils.create_PlotHistAx_from_PlotHistAxParams(PlotHistAxParams=PlotHistAxParams)
PlotHistParams = plot_utils.StructPlotHistParams(
    label="NpHist $-$ NpHist_from_RootHist",
    color=plot_utils.get_color_from_ColorWheel(index=0),
    show_in_legend=True,
)
PlotHistAx = plot_utils.add_NpHist_to_PlotHistAx(NpHist=NpHist_diff, PlotHistAx=PlotHistAx, PlotHistParams=PlotHistParams)
fig.show()

### plot difference between hist error bin by bin -> linear scale, respect yerr for ylim
fig, ax = plt.subplots(1, 1)
PlotHistAxParams = plot_utils.StructPlotHistAxParams(
    ax=ax,
    HistEdges=HistEdges,
    show_uf=True,
    show_of=True,
    yscale="linear",
    show_legend=True,
    auto_ylim_respect_err=True,
)
PlotHistAx = plot_utils.create_PlotHistAx_from_PlotHistAxParams(PlotHistAxParams=PlotHistAxParams)
PlotHistParams = plot_utils.StructPlotHistParams(
    label="NpHist_err $-$ NpHist_from_RootHist_err",
    color=plot_utils.get_color_from_ColorWheel(index=0),
    show_in_legend=True,
)
PlotHistAx = plot_utils.add_NpHist_to_PlotHistAx(NpHist=NpHist_diff_err, PlotHistAx=PlotHistAx, PlotHistParams=PlotHistParams)
fig.show()

### plot difference between hist error bin by bin -> linear scale, dont respect yerr for ylim
fig, ax = plt.subplots(1, 1)
PlotHistAxParams = plot_utils.StructPlotHistAxParams(
    ax=ax,
    HistEdges=HistEdges,
    show_uf=True,
    show_of=True,
    yscale="linear",
    show_legend=True,
)
PlotHistAx = plot_utils.create_PlotHistAx_from_PlotHistAxParams(PlotHistAxParams=PlotHistAxParams)
PlotHistParams = plot_utils.StructPlotHistParams(
    label="NpHist_err $-$ NpHist_from_RootHist_err",
    color=plot_utils.get_color_from_ColorWheel(index=0),
    show_in_legend=True,
)
PlotHistAx = plot_utils.add_NpHist_to_PlotHistAx(NpHist=NpHist_diff_err, PlotHistAx=PlotHistAx, PlotHistParams=PlotHistParams)
fig.show()

#****************************
#############################

stop_time = time.time()
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The execution took \"{(stop_time - start_time):03f} seconds\"")
console_utils.print_console_footer()

input("Press [Enter] to exit")
