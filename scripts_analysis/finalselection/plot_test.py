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
import matplotlib as mpl
import matplotlib.pyplot as plt
import mplhep as mh
import copy
import ROOT

from analysis_controller.src import path_utils
from analysis_controller.src import file_utils
from analysis_controller.src import console_utils
from analysis_controller.src import analysis_utils
from analysis_controller.src import analysis_params

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_PATH, _ANALYSIS_CONTROLLER_REPO_PATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)
console_utils.print_console_header(analysis_controller_filepath=_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH)

start_time = time.time()

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
num_bins = (high_edge-low_edge)//target_bin_width

data_pts = np.array(arr.pt1)
n_data_pts = len(data_pts)

data_weights = np.ones(n_data_pts)

###--------------------------
### create hist with numpy

edges = np.linspace(start=low_edge, stop=high_edge, num=num_bins+1)
edges_ou = np.concatenate([[-np.inf], edges, [np.inf]])

hist_ou, edges_ou = np.histogram(a=data_pts, bins=edges_ou, weights=data_weights)
err_hist_ou = np.sqrt( np.histogram(a=data_pts, bins=edges_ou, weights=data_weights**2)[0] )

print("*** numpy ***")
print("edges_ou", len(edges_ou), edges_ou)
print("hist_ou", len(hist_ou), hist_ou)

###--------------------------
### create hist with pyroot

roothist = ROOT.TH1D("h", "Histogram", num_bins, low_edge, high_edge)
roothist.Sumw2()
data_pts_root = np.ascontiguousarray(data_pts, dtype=np.float64)
data_weights_root = np.ascontiguousarray(data_weights, dtype=np.float64)
roothist.FillN(n_data_pts, data_pts_root, data_weights_root)

edges = np.array([ roothist.GetBinLowEdge(i) for i in range(1, num_bins+2) ])
edges_ou = np.concatenate([[-np.inf], edges, [np.inf]])

hist_ou = np.array([ roothist.GetBinContent(i) for i in range(num_bins+2) ]) # [uf, hist, of]
err_hist_ou = np.array([ roothist.GetBinError(i) for i in range(num_bins+2) ]) # [err_uf, err_hist, err_of]

print("*** pyroot ***")
print("edges_ou", len(edges_ou), edges_ou)
print("hist_ou", len(hist_ou), hist_ou)

###--------------------------
### generic

edges = edges_ou[1:-1]
uf, hist, of = hist_ou[0], hist_ou[1:-1], hist_ou[-1]
err_uf, err_hist, err_of = err_hist_ou[0], err_hist_ou[1:-1], err_hist_ou[-1]

#############################
### PLOT HISTOGRAM

# mh.style.use("CMS")
# fig, ax = plt.subplots()
# mh.histplot(histogram, edges, ax=ax, label="Data")
# mh.cms.label("Preliminary", ax=ax, data=False, lumi=100, com=15)
# fig.show()

mean_width = np.mean(np.diff(edges))
total_width = edges[-1]-edges[0]

uf_width, of_width = total_width*0.05, total_width*0.05
# uf_distance, of_distance = uf_width*3, of_width*3
uf_distance, of_distance = total_width*0.03, total_width*0.03

uf_center, of_center = edges[0]-uf_distance-uf_width/2, edges[-1]+of_distance+of_width/2
edges_ou_plot = np.concatenate([[uf_center-uf_width/2 , uf_center+uf_width/2], edges, [of_center-of_width/2 , of_center+of_width/2]])
hist_ou_plot = np.concatenate([[uf, 0] , hist, [0, of]])
err_hist_ou_plot = np.concatenate([[err_uf, 0] , err_hist, [0, err_of]])

mh.style.use("CMS")
fig, ax = plt.subplots()
mh.histplot(H=hist_ou_plot, bins=edges_ou_plot, yerr=err_hist_ou_plot, ax=ax, histtype='barstep', label="Data")

# ax.set_xticks([plot_edges[0], *plot_edges[1:-1], plot_edges[-1]], ["UF", *map(str, plot_edges[1:-1]), "OF"])

xticks = ax.get_xticks()
xticks = xticks[(xticks >= edges[0]) & (xticks <= edges[-1])]
ax.xaxis.set_major_locator(mpl.ticker.FixedLocator(xticks))
xticks = ax.get_xticks()
xticklabels_text = [xticklabel.get_text() for xticklabel in ax.get_xticklabels()]
xticks = np.concatenate(([uf_center], xticks, [of_center]))
xticklabels_text = ["UF"] + xticklabels_text + ["OF"]
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels_text)
xticklabels = ax.get_xticklabels()
if len(xticklabels) >= 4:
    xticklabels[1].set_ha("left")
    xticklabels[-2].set_ha("right")
# xticklabels[0].set_rotation(90)
# xticklabels[-1].set_rotation(90)

ax.axvline(x=edges[0]-uf_distance/2, color="black", linewidth=1, linestyle="--")
ax.axvline(x=edges[-1]+of_distance/2, color="black", linewidth=1, linestyle="--")

ax.set_xlim(xmin=uf_center-uf_width/2-uf_distance/2, xmax=of_center+of_width/2+of_distance/2)

ax.set_yscale("log")
ax.set_ylim(ymin=0.5, ymax=np.amax(hist_ou)*10)

ax.set_xlabel(f"$p_{{T}}(\\mu_{{1}})$ [GeV]")

bin_width_max_digits = 3
bin_width_str = f"{mean_width:.{bin_width_max_digits}f}".rstrip("0").rstrip(".")
ax.set_ylabel(f"Events / {bin_width_str} GeV")

fig.show()

#****************************
#############################

stop_time = time.time()
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The execution took \"{(stop_time - start_time):03f} seconds\"")
console_utils.print_console_footer()

input("Press [Enter] to exit")
