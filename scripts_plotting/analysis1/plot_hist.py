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
import attridict

from analysis_controller.src import path_utils
from analysis_controller.src import file_utils
from analysis_controller.src import console_utils
from analysis_controller.src import analysis_utils
from analysis_controller.src import hist_utils
from analysis_controller.src import plot_utils
from analysis_controller.src import config_utils

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
    help=f"path to \"PlotAnalysis1Input\" yaml file (str)",
    type=str,
    required=True,
)
parser.add_argument(
    "--paramshist",
    help=f"path to \"PlotAnalysis1ParamsHist\" yaml file (str)",
    type=str,
    required=True,
)
# optional:
args = parser.parse_args()

#############################
#****************************
### MAIN PART

###################
### import config files

### import input config file
PlotAnalysis1Input = config_utils.load_config_file(filepath=args.input, config_type="PlotAnalysis1Input", replace_wildcards=True, verbose=1)
# print(PlotAnalysis1Input)

### import params config file
PlotAnalysis1ParamsHist = config_utils.load_config_file(filepath=args.paramshist, config_type="PlotAnalysis1ParamsHist", replace_wildcards=True, verbose=1)
# print(PlotAnalysis1ParamsHist)

# collect datasets
data_infos = []
n_data = len(PlotAnalysis1Input.analysis1_outputs)
for i_data, data_info in enumerate(PlotAnalysis1Input.analysis1_outputs):
    #if data_info.data_label in [dataset.data_label for dataset in data_infos]:
    #    console_utils.raise_exception(string=f"Non-unique \"data_label\" was specified in plot config file: \"{data_info.data_label}\"")
    data_infos.append(data_info)
data_names_str = ", ".join([f"{data_info.data_label} ({data_info.data_type})" for data_info in data_infos])
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The following input datasets are specified: \"{data_names_str}\"")

# collect dataset output configs
data_configs = []
n_datas = len(data_infos)
for i_data, data_info in enumerate(PlotAnalysis1Input.analysis1_outputs):
    data_config_path = data_info.analysis1_output_config
    # import output config
    ConfigAnalysis1Output = config_utils.load_config_file(filepath=data_config_path, config_type="ConfigAnalysis1Output", replace_wildcards=True, verbose=1)
    Analysis1Output = ConfigAnalysis1Output.Analysis1Output
    data_configs.append(Analysis1Output)

# collect plot names
plot_infos = []
n_plots = len(PlotAnalysis1ParamsHist.plot_histograms)
for i_plot, plot_info in enumerate(PlotAnalysis1ParamsHist.plot_histograms):
    if plot_info.plot_name in plot_infos:
        console_utils.raise_exception(string=f"Non-unique \"plot_name\" was specified in plot config file: \"{plot_info.plot_name}\"")
    plot_infos.append(plot_info)
plot_names_str = ", ".join([f"{plot_info.plot_name}" for plot_info in plot_infos])
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The following histogram plots are requested: \"{plot_names_str}\"")
n_plots = len(plot_infos)

###################
### create plots one by one

for i_plot, plot_info in enumerate(plot_infos):
    console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Starting to prepare the histogram plot \"{(i_plot+1):,} / {n_plots:,} = {((i_plot+1)/n_plots if n_plots > 0 else 0)*100:.3f} %\" named \"{plot_info.plot_name}\"")

    ###############
    ### prepare some stuff

    plot_hist_ax_params = plot_info.plot_style

    plot_hists = { # data_type : data_label : hist
        "data": {},
        "sim": {},
        "sig": {},
    }
    allowed_data_types = list(plot_hists.keys())
    plot_hist_edges = None

    ###############
    ### import all data
    for i_data, data_info in enumerate(data_infos):

        data_config = data_configs[i_data]
        data_type = data_info.data_type
        if data_type not in plot_hists.keys():
            console_utils.raise_exception(string=f"Invalid \"data_type\" named \"{data_type}\". Only expect one of the following: \"{allowed_data_types}\".")
        data_label = data_info.data_label
        input_analysis_branch = data_info.analysis_branch
        input_analysis_step = data_info.analysis_step
        input_hist_name = data_info.analysis_hist_name
        plot_scale_factor = data_info.plot_scale_factor

        plot_hists[data_type][data_label] = {}

        ### import histogram from all files from this dataset
        plot_hists[data_type][data_label] = None
        data_files = [data_config.collection_files[i_collection].path for i_collection in range(len(data_config.collection_files))]
        for i_file, file_path in enumerate(data_files):
            input_data = file_utils.read_dict_from_rootfile(rootfile_path=file_path)
            input_hist = input_data[input_analysis_branch][input_analysis_step][input_hist_name]
            # store input hist
            if plot_hists[data_type][data_label] is None:
                plot_hists[data_type][data_label] = input_hist
            else:
                plot_hists[data_type][data_label] = hist_utils.linear_combination_RootHists(RootHists=[plot_hists[data_type][data_label], input_hist])
            # store inputhist edges and assert all are same edges
            if plot_hist_edges is None:
                plot_hist_edges = input_hist.HistEdges
            else:
                hist_utils.assert_same_HistEdges(HistEdges=[plot_hist_edges, input_hist.HistEdges])

        # apply scalefactor
        plot_hists[data_type][data_label] = hist_utils.linear_combination_RootHists(RootHists=[plot_hists[data_type][data_label]], factors=[plot_scale_factor])

    data_labels = list(plot_hists["data"].keys())
    n_data_data = len(data_labels)
    sim_labels = list(plot_hists["sim"].keys())
    n_data_sim = len(sim_labels)
    sig_labels = list(plot_hists["sig"].keys())
    n_data_sig = len(sig_labels)

    ### merge all data points i.e. type="data" together under common data label="all"
    data_data_labels = list(plot_hists["data"].keys())
    plot_hists["data"]["all"] = None
    for i_data, data_label in enumerate(data_data_labels):
        data_data_hist = plot_hists["data"][data_label]
        if plot_hists["data"]["all"] is None:
            plot_hists["data"]["all"] = data_data_hist
        else:
            plot_hists["data"]["all"] = hist_utils.linear_combination_RootHists(RootHists=[plot_hists["data"]["all"], data_data_hist])

    ##############
    ### create actual plot

    ### create plot axes
    fig, ax = plt.subplots(1, 1)
    PlotHistAxParams = plot_utils.StructPlotHistAxParams(
        ax=ax,
        HistEdges=plot_hist_edges,
        **plot_hist_ax_params,
    )
    PlotHistAx = plot_utils.create_PlotHistAx_from_PlotHistAxParams(PlotHistAxParams=PlotHistAxParams)

    ### plot simulation
    # stack histograms
    # separate color by label
    sim_NpHist_list = []
    sim_PlotHistParams_list =  []
    for i_sim, sim_label in enumerate(sim_labels):
        sim_hist = plot_hists["sim"][sim_label]
        NpHist_from_RootHist = hist_utils.convert_RootHist_to_NpHist(RootHist=sim_hist)

        if sim_label == "DY":
            NpHist_from_RootHist.hist_ou *= 1 #50
            # in ceciles code it is: 6346.0 * 1 / 164838
            NpHist_from_RootHist.update()
        if sim_label == "Nonprompt":
            NpHist_from_RootHist.hist_ou *= 1 #2
            # rescaling factor "close to 2" according to AN
            NpHist_from_RootHist.update()

        sim_NpHist_list.append(NpHist_from_RootHist)
        # plot
        sim_PlotHistParams_list.append(plot_utils.StructPlotHistParams(
            histtype="fill", #"bar",
            label=sim_label,
            color=plot_utils.get_color_from_ColorWheel(index=i_sim),
            markersize=12,
            errorlinewidth=1.5,
            show_in_legend=True,
        ))
    PlotHistAx = plot_utils.add_NpHist_stack_to_PlotHistAx(NpHist_list=sim_NpHist_list, PlotHistAx=PlotHistAx, PlotHistParams_list=sim_PlotHistParams_list)

    ### plot data together with label "all"
    data_hist = plot_hists["data"]["all"]
    NpHist_from_RootHist = hist_utils.convert_RootHist_to_NpHist(RootHist=data_hist)
    PlotHistParams = plot_utils.StructPlotHistParams(
        histtype="errorbar",
        label="Data",
        color="black",
        markersize=12,
        errorlinewidth=1.5,
        show_in_legend=True,
    )
    PlotHistAx = plot_utils.add_NpHist_to_PlotHistAx(NpHist=NpHist_from_RootHist, PlotHistAx=PlotHistAx, PlotHistParams=PlotHistParams)

    ### show and store plot
    fig.show()

#****************************
#############################

stop_time = time.time()
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The execution took \"{(stop_time - start_time):03f} seconds\"")
console_utils.print_console_footer()

input("Press [Enter] to exit")
