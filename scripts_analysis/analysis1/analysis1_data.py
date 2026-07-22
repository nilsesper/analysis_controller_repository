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
import copy
import attridict

from analysis_controller.src import path_utils
from analysis_controller.src import console_utils
from analysis_controller.src import analysis_utils
from analysis_controller.src import config_utils
from analysis_controller.src import hist_utils
from analysis_controller.src import plot_utils
from analysis_controller.src import file_utils

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
### PREPARE ANALYSIS OUTPUT (histograms, values etc.)

### create proto HistEdges object from information about hist edges in config file
# hist_name: str name of hist, for identification in error message
# hist_params: {edges, edge_type}
def parse_hist_edges_from_config(*, hist_name, hist_params):
    if hist_params.edge_type == "uniform":
        if not len(hist_params.edges) == 3:
            raise Exception(f"For proto histogram \"{hist_name}\": Require \"edges\" of the format \"[min_edge_corner, max_edge_corner, n_bins]\"")
        try:
            n_edges = int(hist_params.edges[2])
        except:
            raise Exception(f"For proto histogram \"{hist_name}\": Require \"edges\" of the format \"[min_edge_corner, max_edge_corner, n_bins]\". n_bins must be convertable to integer")
        HistEdges = hist_utils.create_HistEdges_uniform(low_edge=hist_params.edges[0], high_edge=hist_params.edges[1], n_bins=n_edges)
    elif hist_params.edge_type == "custom":
        if not len(hist_params.edges) >= 2:
            raise Exception(f"For proto histogram \"{hist_name}\": Require \"edges\" of the format \"[edge_corners]\", i.e. at least 2 entries")
        HistEdges = hist_utils.StructHistEdges(edges=np.array(hist_params.edges))
    else:
        raise Exception(f"For histogram \"{hist_name}\": Require one of the following \"edge_type\" values: \"uniform\", \"custom\"")
    return copy.deepcopy(HistEdges)

### create proto_hist_edges from config file
proto_hist_edges = attridict({
    proto_hist_name: parse_hist_edges_from_config(hist_name=proto_hist_name, hist_params=attridict(proto_hist_params)) for proto_hist_name, proto_hist_params in Analysis1ParamsAnalysis.hist_edges.items()
})

### helper class to fill analysis output
class StructAnalysisOutput:
    # proto_data = { analysis_branch : analysis_step { name : object e.g. plain number, RootHist } }
    def __init__(self, *, proto_data):
        self._data = copy.deepcopy(proto_data)
        self.available_branches = list(self._data.keys())
        self.available_steps = {branch: self._data[branch].keys() for branch in self.available_branches}
        self._analysis_branch = None
        self._analysis_step = None
    def get_data(self):
        return self._data  
    def get_analysis_branch(self):
        return self._analysis_branch
    def get_analysis_step(self):
        return self._analysis_step
    def set_analysis_branch(self, analysis_branch):
        if analysis_branch not in self.available_branches:
            console_utils.raise_exception(string=f"\"analysis_branch\" named \"{analysis_branch}\" does not exist")
        self._analysis_branch = analysis_branch
    def set_analysis_step(self, analysis_step):
        if self._analysis_branch == None:
            console_utils.raise_exception(string="No \"analysis_branch\" selected")
        if analysis_step not in self.available_steps[self._analysis_branch]:
            console_utils.raise_exception(f"\"analysis_step\" named \"{analysis_step}\" does not exist for \"analysis_branch\" named \"{self._analysis_branch}\"")
        self._analysis_step = analysis_step
    def add_to_number(self, name, value):
        if self._analysis_branch == None:
            console_utils.raise_exception(string="No \"analysis_branch\" selected")
        if self._analysis_step == None:
            console_utils.raise_exception(string="No \"analysis_step\" selected")
        if name not in self._data[self._analysis_branch][self._analysis_step].keys():
            console_utils.raise_exception(f"Name \"{name}\" does not exist for \"analysis_branch\" named \"{self._analysis_branch}\" and \"analysis_step\" named \"{self._analysis_step}\"")
        #---
        self._data[self._analysis_branch][self._analysis_step][name] += value
    def add_to_hist(self, name, values):
        if self._analysis_branch == None:
            console_utils.raise_exception(string="No \"analysis_branch\" selected")
        if self._analysis_step == None:
            console_utils.raise_exception(string="No \"analysis_step\" selected")
        # do actual action
        if name not in self._data[self._analysis_branch][self._analysis_step].keys():
            console_utils.raise_exception(string=f"Name \"{name}\" does not exist for \"analysis_branch\" named \"{self._analysis_branch}\" and \"analysis_step\" named \"{self._analysis_step}\"")
        self._data[self._analysis_branch][self._analysis_step][name] = hist_utils.add_DataPts_to_RootHist(
            RootHist=self._data[self._analysis_branch][self._analysis_step][name],
            DataPts=hist_utils.create_DataPts(data_pts=np.array( values )),
        )

### Z peak validation

# sub data proto output
_proto_output_z_peak_validation = {
    ### plain values
    #--- for cut flow: weight sum and event count
    "p__sum_weights": 0,
    "p__n_events": 0,
    ### histograms
    "h__n_tracks": hist_utils.create_RootHist(HistEdges=proto_hist_edges["n_tracks"]),
    "h__pt_1": hist_utils.create_RootHist(HistEdges=proto_hist_edges["pt"]),
    "h__pt_2": hist_utils.create_RootHist(HistEdges=proto_hist_edges["pt"]),
    "h__mt": hist_utils.create_RootHist(HistEdges=proto_hist_edges["mt"]),
}
# filler function
def fill_output___z_peak_validation(*, output, arrays):

    n_events = len(arrays)
    output.add_to_number(name="p__n_events", value=n_events )

    single_event_weight = 1
    sum_weights = n_events * single_event_weight
    output.add_to_number(name="p__sum_weights", value=sum_weights )

    output.add_to_hist(name="h__pt_1", values=arrays["pt1"] )

    output.add_to_hist(name="h__pt_2", values=arrays["pt2"] )

    muon_mass = Analysis1ParamsAnalysis.muon_mass
    transversefourvec1 = ak.zip({"pt": arrays["pt1"], "eta": arrays["eta1"], "phi": arrays["phi1"], "m": muon_mass}, with_name="Momentum4D")
    transversefourvec2 = ak.zip({"pt": arrays["pt2"], "eta": arrays["eta2"], "phi": arrays["phi2"], "m": muon_mass}, with_name="Momentum4D")
    transversefourvecsum = transversefourvec1 + transversefourvec2
    transversemass = transversefourvecsum.mass
    output.add_to_hist(name="h__mt", values=transversemass )

    return output

### main data proto output
#   contains the output of all analysis branches and cuts
def proto(a):
    return copy.deepcopy(a)
proto_output = { # analysis branch name -> analysis step name -> analysis output (histograms, numbers)
    "z_peak_opposite_sign": {
        "initial": proto(_proto_output_z_peak_validation),
        "n_tracks_equal_2": proto(_proto_output_z_peak_validation),
        "pt_greater_threshold": proto(_proto_output_z_peak_validation),
        "dxy_smaller_threshold": proto(_proto_output_z_peak_validation),
        "abs_eta_smaller_threshold": proto(_proto_output_z_peak_validation),
        "qual_greater_threshold": proto(_proto_output_z_peak_validation),
        "opposite_sign": proto(_proto_output_z_peak_validation),
    },
    "z_peak_same_sign": {
        "initial": proto(_proto_output_z_peak_validation),
        "n_tracks_equal_2": proto(_proto_output_z_peak_validation),
        "pt_greater_threshold": proto(_proto_output_z_peak_validation),
        "dxy_smaller_threshold": proto(_proto_output_z_peak_validation),
        "abs_eta_smaller_threshold": proto(_proto_output_z_peak_validation),
        "qual_greater_threshold": proto(_proto_output_z_peak_validation),
        "same_sign": proto(_proto_output_z_peak_validation),
    },
}

### create main output object
output = StructAnalysisOutput(proto_data=proto_output)


###################
### EVENT LOOP

### process events in file in separate batches, to reduce ram usage
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Starting the event loop, which processes events columnarly in batches of \"{Analysis1ParamsAnalysis.eventloop_iteration_size}\"")
eventloop_iteration_size = Analysis1ParamsAnalysis.eventloop_iteration_size.replace("iB","B") # replace GiB -> GB etc.
eventloop_branch_names = roottree_branches
roottree_iterator = roottree.iterate(eventloop_branch_names, step_size=eventloop_iteration_size, library="ak")
### loop over batches
for i_batch, initial_arrays in enumerate(roottree_iterator):
    n_events_initial = len(initial_arrays)
    console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Starting columnar analysis for data batch \"{(i_batch+1)}\", which contains \"{n_events_initial:,}\" events")
    ### do columnar event analysis in each batch
    #*************************************************************

    #********************
    #*** Z peak opposite sign

    output.set_analysis_branch("z_peak_opposite_sign")
    arrays = initial_arrays

    output.set_analysis_step("initial")
    output = fill_output___z_peak_validation(output=output, arrays=arrays)

    output.set_analysis_step("n_tracks_equal_2")
    mask = (arrays["nseltracks"] == 2)
    arrays = arrays[mask]
    output = fill_output___z_peak_validation(output=output, arrays=arrays)

    output.set_analysis_step("pt_greater_threshold")
    mask = (arrays["pt1"] > 15) & (arrays["pt2"] > 15)
    arrays = arrays[mask]
    output = fill_output___z_peak_validation(output=output, arrays=arrays)

    output.set_analysis_step("dxy_smaller_threshold")
    mask = (arrays["dxy1"] < 1) & (arrays["dxy2"] < 1)
    arrays = arrays[mask]
    output = fill_output___z_peak_validation(output=output, arrays=arrays)

    output.set_analysis_step("abs_eta_smaller_threshold")
    mask = (arrays["eta1"] < 0.83) & (arrays["eta2"] < 0.83)
    arrays = arrays[mask]
    output = fill_output___z_peak_validation(output=output, arrays=arrays)

    output.set_analysis_step("qual_greater_threshold")
    mask = (arrays["qual1"] > 11) & (arrays["qual2"] > 11)
    arrays = arrays[mask]
    output = fill_output___z_peak_validation(output=output, arrays=arrays)

    output.set_analysis_step("opposite_sign")
    mask = (arrays["charge1"] != arrays["charge2"])
    arrays = arrays[mask]
    output = fill_output___z_peak_validation(output=output, arrays=arrays)

    #********************
    #*** Z peak same sign

    output.set_analysis_branch("z_peak_same_sign")
    arrays = initial_arrays

    output.set_analysis_step("initial")
    output = fill_output___z_peak_validation(output=output, arrays=arrays)

    output.set_analysis_step("n_tracks_equal_2")
    mask = (arrays["nseltracks"] == 2)
    arrays = arrays[mask]
    output = fill_output___z_peak_validation(output=output, arrays=arrays)

    output.set_analysis_step("pt_greater_threshold")
    mask = (arrays["pt1"] > 15) & (arrays["pt2"] > 15)
    arrays = arrays[mask]
    output = fill_output___z_peak_validation(output=output, arrays=arrays)

    output.set_analysis_step("dxy_smaller_threshold")
    mask = (arrays["dxy1"] < 1) & (arrays["dxy2"] < 1)
    arrays = arrays[mask]
    output = fill_output___z_peak_validation(output=output, arrays=arrays)

    output.set_analysis_step("abs_eta_smaller_threshold")
    mask = (arrays["eta1"] < 0.83) & (arrays["eta2"] < 0.83)
    arrays = arrays[mask]
    output = fill_output___z_peak_validation(output=output, arrays=arrays)

    output.set_analysis_step("qual_greater_threshold")
    mask = (arrays["qual1"] > 11) & (arrays["qual2"] > 11)
    arrays = arrays[mask]
    output = fill_output___z_peak_validation(output=output, arrays=arrays)

    output.set_analysis_step("same_sign")
    mask = (arrays["charge1"] == arrays["charge2"])
    arrays = arrays[mask]
    output = fill_output___z_peak_validation(output=output, arrays=arrays)

    #*************************************************************

### event loop done
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Finished the event loop")

###################
### STORE OUTPUT

"""
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
#"""

#"""
### store output data as rootfile
allow_overwrite = True
output_dictionary = output.get_data()
file_utils.store_dict_as_rootfile(input_dictionary=output_dictionary, rootfile_path=outfile_path, check_exists=(not allow_overwrite))
#"""

"""
output_data_readback = file_utils.read_dict_from_rootfile(rootfile_path=outfile_path)
print(f"output_data_readback = {output_data_readback}")
#"""

#****************************
#############################

stop_time = time.time()
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The execution took \"{(stop_time - start_time):03f} seconds\"")
console_utils.print_console_footer()

input("Press [Enter] to exit")
