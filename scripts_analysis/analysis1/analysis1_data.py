######################
### ANALYSIS1 STEP ###
### for data       ###
######################

############################
### IMPORTS

import os
import uproot
import awkward as ak
import numba as nb
import numpy as np
from tabulate import tabulate
import vector
import time
import argparse
import ROOT
import psutil
import matplotlib.pyplot as plt

from analysis_controller.src import path_utils
from analysis_controller.src import console_utils
from analysis_controller.src import analysis_utils
from analysis_controller.src import config_utils
from analysis_controller.src import hist_utils
from analysis_controller.src import plot_utils

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_PATH, _ANALYSIS_CONTROLLER_REPO_PATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)
console_utils.print_console_header(analysis_controller_filepath=_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH)

start_time = time.time()
process = psutil.Process(os.getpid())
# print(f"memory usage = {process.memory_info().rss / 1024**2} MB")

vector.register_awkward()

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
parser.add_argument(
    "--output",
    help="path to target output root file (str)",
    type=str,
    required=True,
)
parser.add_argument(
    "--params",
    help="path to Analysis1ParmsAnalysis yaml file (str)",
    type=str,
    required=True,
)
# optional:
args = parser.parse_args()

#############################
#****************************
### MAIN PART

### parse args
infile_path = args.input
outfile_path = args.output
paramsfile_path = args.params

###################
### IMPORT PARAMS

console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Loading analysis parameters")
Analysis1ParamsAnalysis = config_utils.load_config_file(filepath=paramsfile_path, config_type="Analysis1ParamsAnalysis", replace_wildcards=True, verbose=1)

###################
### IMPORT DATA

### import root file
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Opening input ROOT file from \"{infile_path}\"")
infile = uproot.open(infile_path)

### extract "Events" root tree
roottree = infile["Events"]
roottree_branches = roottree.keys()
#console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"ROOT tree \"Events\" contains branches {roottree_branches}")

###################
### PREPARE HISTOGRAMS

def add_proto_hist(*, hists, hist_params):
    if hist_params.hist_name in hists.keys():
        raise Exception(f"Specified \"hist_name\" = \"{hist_params.hist_name}\" is already a defined histogram")
    # create edges
    if hist_params.edge_type == "uniform":
        if not len(hist_params.edges) == 3:
            raise Exception(f"For histogram \"hist_name\" = \"{hist_params.hist_name}\": Require \"edges\" of the format \"[min_edge_corner, max_edge_corner, n_bins]\"")
        try:
            n_edges = int(hist_params.edges[2])
        except:
            raise Exception(f"For histogram \"hist_name\" = \"{hist_params.hist_name}\": Require \"edges\" of the format \"[min_edge_corner, max_edge_corner, n_bins]\". n_bins must be convertable to integer")
        HistEdges = hist_utils.create_HistEdges_uniform(low_edge=hist_params.edges[0], high_edge=hist_params.edges[1], n_bins=n_edges)
    elif hist_params.edge_type == "custom":
        if not len(hist_params.edges) >= 2:
            raise Exception(f"For histogram \"hist_name\" = \"{hist_params.hist_name}\": Require \"edges\" of the format \"[edge_corners]\", i.e. at least 2 entries")
        HistEdges = hist_utils.StructHistEdges(edges=np.array(hist_params.edges))
    else:
        raise Exception(f"For histogram \"hist_name\" = \"{hist_params.hist_name}\": Require one of the following \"edge_type\" values: \"uniform\", \"custom\"")
    # create hist
    hists[hist_params.hist_name] = hist_utils.create_RootHist(HistEdges=HistEdges)
    # return added hists
    return hists

### col_hists: natural column histograms, with values being taken from data columns

hists = {}

col_hist_params_list = Analysis1ParamsAnalysis.col_hists

for hist_params in col_hist_params_list:
    if hist_params.hist_name not in roottree_branches:
        raise Exception(f"Specified col_hist \"hist_name\" = \"{hist_params.hist_name}\" is not a branch name in the input file. Available branch names are {roottree_branches}")
    hists = add_proto_hist(hists=hists, hist_params=hist_params)

### ana_hists: analysis histograms, with values being computed during the analysis

ana_hist_params_list = Analysis1ParamsAnalysis.ana_hists

for hist_params in ana_hist_params_list:
    hists = add_proto_hist(hists=hists, hist_params=hist_params)

###################
### EVENT LOOP

eventloop_iteration_size = Analysis1ParamsAnalysis.eventloop_iteration_size.replace("iB","B") # replace GiB -> GB etc.
eventloop_branch_names = roottree_branches

print(f"memory usage = {process.memory_info().rss / 1024**2} MB")
print("do event loop")

for i, arrays in enumerate(roottree.iterate(eventloop_branch_names, step_size=eventloop_iteration_size, library="ak")):
    print(f"iteration {i}")

    cut_mask = (arrays["nseltracks"] == 2)
    arrays = arrays[cut_mask]

    cut_mask = (arrays["pt1"] > 15)
    arrays = arrays[cut_mask]
    cut_mask = (arrays["pt2"] > 15)
    arrays = arrays[cut_mask]

    cut_mask = (arrays["dxy1"] < 1)
    arrays = arrays[cut_mask]
    cut_mask = (arrays["dxy2"] < 1)
    arrays = arrays[cut_mask]

    cut_mask = (np.abs(arrays["eta1"]) < 0.83)
    arrays = arrays[cut_mask]
    cut_mask = (np.abs(arrays["eta2"]) < 0.83)
    arrays = arrays[cut_mask]

    cut_mask = (arrays["qual1"] > 11)
    arrays = arrays[cut_mask]
    cut_mask = (arrays["qual2"] > 11)
    arrays = arrays[cut_mask]

    initial_arrays = arrays

    ### different sign combinations
    for mode in ["osgn", "ssgn"]:

        if mode == "osgn":
            cut_mask = (initial_arrays["charge1"] != initial_arrays["charge2"])
        elif mode == "ssgn":
            cut_mask = (initial_arrays["charge1"] == initial_arrays["charge2"])

        arrays = initial_arrays[cut_mask]

        for hist_params in col_hist_params_list:
            hist_name = hist_params.hist_name
            DataPts = hist_utils.create_DataPts(data_pts=np.array( arrays[hist_name] ))
            hists[hist_name] = hist_utils.add_DataPts_to_RootHist(RootHist=hists[hist_name], DataPts=DataPts)

        muon_mass = Analysis1ParamsAnalysis.muon_mass
        fourvec1 = ak.zip({"pt": arrays["pt1"], "eta": arrays["eta1"], "phi": arrays["phi1"], "m": muon_mass}, with_name="Momentum4D")
        fourvec2 = ak.zip({"pt": arrays["pt2"], "eta": arrays["eta2"], "phi": arrays["phi2"], "m": muon_mass}, with_name="Momentum4D")

        # mt
        fourvecsum = fourvec1 + fourvec2
        mt = fourvecsum.mass
        hist_name = f"{mode}_mt"
        DataPts = hist_utils.create_DataPts(data_pts=np.array( mt ))
        hists[hist_name] = hist_utils.add_DataPts_to_RootHist(RootHist=hists[hist_name], DataPts=DataPts)

        # delta r
        dr = fourvec1.deltaR(fourvec2)
        hist_name = f"{mode}_dr"
        DataPts = hist_utils.create_DataPts(data_pts=np.array( dr ))
        hists[hist_name] = hist_utils.add_DataPts_to_RootHist(RootHist=hists[hist_name], DataPts=DataPts)

        # delta phi
        dphi = fourvec1.deltaphi(fourvec2)
        hist_name = f"{mode}_dphi"
        DataPts = hist_utils.create_DataPts(data_pts=np.array( dphi ))
        hists[hist_name] = hist_utils.add_DataPts_to_RootHist(RootHist=hists[hist_name], DataPts=DataPts)

        # delta eta
        deta = fourvec1.deltaeta(fourvec2)
        hist_name = f"{mode}_deta"
        DataPts = hist_utils.create_DataPts(data_pts=np.array( deta ))
        hists[hist_name] = hist_utils.add_DataPts_to_RootHist(RootHist=hists[hist_name], DataPts=DataPts)

        # charge product
        qproduct = arrays["charge1"] * arrays["charge2"]
        hist_name = f"{mode}_chargeprod"
        DataPts = hist_utils.create_DataPts(data_pts=np.array( qproduct ))
        hists[hist_name] = hist_utils.add_DataPts_to_RootHist(RootHist=hists[hist_name], DataPts=DataPts)

    print(f"memory usage = {process.memory_info().rss / 1024**2} MB")

print("event loop done")
print(f"memory usage = {process.memory_info().rss / 1024**2} MB")

###################
### STORE OUTPUT

for hist_name in hists.keys():

    NpHist_from_RootHist = hist_utils.convert_RootHist_to_NpHist(RootHist=hists[hist_name])

    fig, ax = plt.subplots(1, 1)
    PlotHistAxParams = plot_utils.StructPlotHistAxParams(
        ax=ax,
        HistEdges=hists[hist_name].HistEdges,
        show_uf=True,
        show_of=True,
        xlabel=f"{hist_name}",
        yscale="log",
        show_legend=True,
    )
    PlotHistAx = plot_utils.create_PlotHistAx_from_PlotHistAxParams(PlotHistAxParams=PlotHistAxParams)

    # PlotHistParams = plot_utils.StructPlotHistParams(
    #     histtype="errorbar",
    #     label="Data",
    #     color="black",
    #     markersize=12,
    #     errorlinewidth=1.5,
    #     show_in_legend=True,
    # )
    PlotHistParams = plot_utils.StructPlotHistParams(
        histtype="bar",
        # histtype="step",
        label="DY",
        color=plot_utils.get_color_from_ColorWheel(index=0),
        markersize=12,
        errorlinewidth=1.5,
        show_in_legend=True,
    )
    PlotHistAx = plot_utils.add_NpHist_to_PlotHistAx(NpHist=NpHist_from_RootHist, PlotHistAx=PlotHistAx, PlotHistParams=PlotHistParams)
    fig.show()

print(f"memory usage = {process.memory_info().rss / 1024**2} MB")

#****************************
#############################

stop_time = time.time()
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The execution took \"{(stop_time - start_time):03f} seconds\"")
console_utils.print_console_footer()

input("Press [Enter] to exit")
