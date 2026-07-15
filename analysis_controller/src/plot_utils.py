##################
### PLOT UTILS ###
##################

############################
### IMPORTS

import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import mplhep as mh

from analysis_controller.src import path_utils

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_PATH, _ANALYSIS_CONTROLLER_REPO_PATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)

############################
### HELPER FUNCTIONS & CLASSES (with prefix "_")



############################
### MAIN FUNCTIONS & CLASSES

### plot NpHist histogram with mplhep
def plot_NpHist(*, NpHist):

    mean_width = np.mean(np.diff(NpHist.HistEdges.edges))
    total_width = NpHist.HistEdges.edges[-1] - NpHist.HistEdges.edges[0]

    uf_width, of_width = total_width*0.05, total_width*0.05
    # uf_distance, of_distance = uf_width*3, of_width*3
    uf_distance, of_distance = total_width*0.03, total_width*0.03

    uf_center, of_center = NpHist.HistEdges.edges[0]-uf_distance-uf_width/2, NpHist.HistEdges.edges[-1]+of_distance+of_width/2
    edges_ou_plot = np.concatenate([[uf_center-uf_width/2 , uf_center+uf_width/2], NpHist.HistEdges.edges, [of_center-of_width/2 , of_center+of_width/2]])
    hist_ou_plot = np.concatenate([[NpHist.uf, 0] , NpHist.hist, [0, NpHist.of]])
    err_hist_ou_plot = np.concatenate([[NpHist.err_uf, 0] , NpHist.err_hist, [0, NpHist.err_of]])

    mh.style.use("CMS")
    fig, ax = plt.subplots()
    mh.histplot(H=hist_ou_plot, bins=edges_ou_plot, yerr=err_hist_ou_plot, ax=ax, histtype='barstep', label="Data")

    # ax.set_xticks([plot_edges[0], *plot_edges[1:-1], plot_edges[-1]], ["UF", *map(str, plot_edges[1:-1]), "OF"])

    xticks = ax.get_xticks()
    xticks = xticks[(xticks >= NpHist.HistEdges.edges[0]) & (xticks <= NpHist.HistEdges.edges[-1])]
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

    ax.axvline(x=NpHist.HistEdges.edges[0]-uf_distance/2, color="black", linewidth=1, linestyle="--")
    ax.axvline(x=NpHist.HistEdges.edges[-1]+of_distance/2, color="black", linewidth=1, linestyle="--")

    ax.set_xlim(xmin=uf_center-uf_width/2-uf_distance/2, xmax=of_center+of_width/2+of_distance/2)

    ax.set_yscale("log")
    ax.set_ylim(ymin=0.5, ymax=np.amax(NpHist.hist_ou)*10)

    ax.set_xlabel(f"$p_{{T}}(\\mu_{{1}})$ [GeV]")

    bin_width_max_digits = 3
    bin_width_str = f"{mean_width:.{bin_width_max_digits}f}".rstrip("0").rstrip(".")
    ax.set_ylabel(f"Events / {bin_width_str} GeV")

    fig.show()

