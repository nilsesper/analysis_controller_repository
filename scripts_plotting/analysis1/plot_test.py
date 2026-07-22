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
input_dict = file_utils.read_dict_from_rootfile(rootfile_path=infile_path)
print(f"input_dict = {input_dict}")

#############################
### PLOT HISTOGRAMS

print(input_dict["z_peak_opposite_sign"]["opposite_sign"]["h__mt"])
print(input_dict["z_peak_opposite_sign"]["opposite_sign"]["h__mt"].roothist)

hists = {
    "mt": input_dict["z_peak_opposite_sign"]["opposite_sign"]["h__mt"],
}
print(hists)

for hist_name in hists.keys():

    console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Plotting histogram \"{hist_name}\"")

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

#****************************
#############################

stop_time = time.time()
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The execution took \"{(stop_time - start_time):03f} seconds\"")
console_utils.print_console_footer()

input("Press [Enter] to exit")
