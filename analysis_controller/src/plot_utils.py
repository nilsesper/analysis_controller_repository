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

mh.style.use("CMS")

############################
### HELPER FUNCTIONS & CLASSES (with prefix "_")

class StructPlotHistParams:
    __slots__ = (
        "ax",
        "HistEdges",
        "show_uf", "show_of",
        "xlabel", "ylabel",
        "xscale", "yscale",
        "xlim", "ylim",
    )
    def __init__(self, *,
            ax,
            HistEdges,
            show_uf=True, show_of=True,
            xlabel="", ylabel="",
            xscale="norm", yscale="log",
            xlim=None, ylim=None,
        ):
        self.ax = ax
        self.HistEdges = HistEdges
        self.show_uf = show_uf
        self.show_of = show_of
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.xscale = xscale
        self.yscale = yscale
        self.xlim = xlim
        self.ylim = ylim
        self.update()
    def update(self):
        pass

class StructPlotHistAx:
    __slots__ = (
        "ax",
        "HistEdges",
        "show_uf", "show_of",
        "xlabel", "ylabel",
        "xscale", "yscale",
        "xlim", "ylim",
        #---
        "uf_width", "of_width",
        "uf_distance", "of_distance",
        "uf_center", "of_center",
        "edges_ou_plot",
    )
    def __init__(self, *,
            PlotHistParams,
        ):
        self.ax = PlotHistParams.ax
        self.HistEdges = PlotHistParams.HistEdges
        self.show_uf = PlotHistParams.show_uf
        self.show_of = PlotHistParams.show_of
        self.xlabel = PlotHistParams.xlabel
        self.ylabel = PlotHistParams.ylabel
        self.xscale = PlotHistParams.xscale
        self.yscale = PlotHistParams.yscale
        self.xlim = PlotHistParams.xlim
        self.ylim = PlotHistParams.ylim
        self.update()
    def update(self):
        self.uf_width = self.HistEdges.total_edges_width*0.05
        self.of_width = self.HistEdges.total_edges_width*0.05
        self.uf_distance = self.HistEdges.total_edges_width*0.05
        self.of_distance = self.HistEdges.total_edges_width*0.05
        self.uf_center = self.HistEdges.edges[0]-self.uf_distance-self.uf_width/2
        self.of_center = self.HistEdges.edges[-1]+self.of_distance+self.of_width/2
        self.edges_ou_plot = np.concatenate([[self.uf_center-self.uf_width/2 , self.uf_center+self.uf_width/2], self.HistEdges.edges, [self.of_center-self.of_width/2 , self.of_center+self.of_width/2]])

############################
### MAIN FUNCTIONS & CLASSES

# PlotHistAx = StructPlotHistAx(ax=ax, HistEdges=HistEdges, show_uf=True, show_of=True)

### create ax for hist plotting, with specified bins
def create_PlotHistAx_from_PlotHistParams(*, PlotHistParams):
    #-----------------------
    #--- create struct

    PlotHistAx = StructPlotHistAx(PlotHistParams=PlotHistParams)

    #-----------------------
    #--- prepare ax

    mh.style.use("CMS")

    # set xlim
    PlotHistAx.ax.set_xlim(xmin=PlotHistAx.uf_center-PlotHistAx.uf_width/2-PlotHistAx.uf_distance/2, xmax=PlotHistAx.of_center+PlotHistAx.of_width/2+PlotHistAx.of_distance/2)

    # cut xticks to be within edges
    xticks = [x for x in PlotHistAx.ax.get_xticks() if PlotHistAx.HistEdges.edges[0] <= x <= PlotHistAx.HistEdges.edges[-1]]
    PlotHistAx.ax.xaxis.set_major_locator(mpl.ticker.FixedLocator(xticks))

    # add custom xtick labels for underflow / overflow
    xticks = PlotHistAx.ax.get_xticks()
    xticklabels_text = [xticklabel.get_text() for xticklabel in PlotHistAx.ax.get_xticklabels()]
    xticks = np.concatenate(([PlotHistAx.uf_center], xticks, [PlotHistAx.of_center]))
    xticklabels_text = ["UF"] + xticklabels_text + ["OF"]
    # ax.set_xticks(xticks)
    # ax.set_xticklabels(xticklabels_text)
    PlotHistAx.ax.xaxis.set_major_locator(mpl.ticker.FixedLocator(xticks))
    PlotHistAx.ax.xaxis.set_major_formatter(mpl.ticker.FixedFormatter(xticklabels_text))

    # hide numeric xticks outside of edges (dont show for underflow / overflow)
    # rotate custom underflow / overflow xtick labels
    major_xticks = PlotHistAx.ax.xaxis.get_major_ticks()
    n_xticks = len(major_xticks)
    for i_xtick, xtick in enumerate(major_xticks):
        xloc = xtick.get_loc()
        # if ((xloc < NpHist.HistEdges.edges[0]-uf_distance/2 or xloc > NpHist.HistEdges.edges[-1]+of_distance/2) and xloc != uf_center and xloc != of_center):
        #     xtick.tick1line.set_visible(False)
        #     xtick.tick2line.set_visible(False)
        if i_xtick == 0 or i_xtick == n_xticks-1:
            xtick.label1.set_rotation(90)

    # draw minor ticks only in range of edges
    major_xticks = PlotHistAx.ax.get_xticks()[1:-1]
    major_tick_step = np.mean(np.diff(major_xticks))
    minor_xticks = []
    for major_xtick in major_xticks:
        minor_step = major_tick_step / 5
        for i in [-2,-1,1,2]:
            minor_pos = major_xtick+i*minor_step
            if minor_pos >= PlotHistAx.HistEdges.edges[0] and minor_pos <= PlotHistAx.HistEdges.edges[-1]:
                minor_xticks.append(minor_pos)
    PlotHistAx.ax.xaxis.set_minor_locator(mpl.ticker.FixedLocator(minor_xticks))

    # draw separation lines between edges and underflow / overflow
    PlotHistAx.ax.axvline(x=PlotHistAx.HistEdges.edges[0]-PlotHistAx.uf_distance/2, color="black", linewidth=1, linestyle="--")
    PlotHistAx.ax.axvline(x=PlotHistAx.HistEdges.edges[-1]+PlotHistAx.of_distance/2, color="black", linewidth=1, linestyle="--")

    # set xlabel
    if PlotHistAx.xlabel != None:
        xlabel = PlotHistAx.xlabel
    else:
        xlabel = ""
    PlotHistAx.ax.set_xlabel(xlabel)

    # set ylabel and note bin width
    bin_width_max_digits = 3
    bin_width_str = f"{PlotHistAx.HistEdges.mean_bin_width:.{bin_width_max_digits}f}".rstrip("0").rstrip(".")
    PlotHistAx.ax.set_ylabel(f"Events / {bin_width_str} GeV")

    return PlotHistAx

### add NpHist histogram to existing ax with mplhep
def add_NpHist_to_PlotHistAx(*, NpHist, PlotHistAx):

    hist_ou_plot = np.concatenate([[NpHist.uf, 0] , NpHist.hist, [0, NpHist.of]])
    err_hist_ou_plot = np.concatenate([[NpHist.err_uf, 0] , NpHist.err_hist, [0, NpHist.err_of]])

    mh.histplot(H=hist_ou_plot, bins=PlotHistAx.edges_ou_plot, yerr=err_hist_ou_plot, ax=PlotHistAx.ax, histtype="barstep", label="Data")

    # set yscale and ylim
    if PlotHistAx.yscale == "linear":
        PlotHistAx.ax.set_yscale("linear")
        PlotHistAx.ax.set_ylim(ymin=np.amin(NpHist.hist_ou)*1.2, ymax=np.amax(NpHist.hist_ou)*1.2)
    elif PlotHistAx.yscale == "log":
        PlotHistAx.ax.set_yscale("log")
        PlotHistAx.ax.set_ylim(ymin=0.5, ymax=np.amax(NpHist.hist_ou)*10)



# ### add NpHist histogram to existing ax with mplhep
# def add_NpHist_to_ax(*, NpHist, PlotHistAx):

#     mean_width = np.mean(np.diff(NpHist.HistEdges.edges))
#     total_width = NpHist.HistEdges.edges[-1] - NpHist.HistEdges.edges[0]

#     uf_width, of_width = total_width*0.05, total_width*0.05
#     # uf_distance, of_distance = uf_width*3, of_width*3
#     uf_distance, of_distance = total_width*0.05, total_width*0.05

#     uf_center, of_center = NpHist.HistEdges.edges[0]-uf_distance-uf_width/2, NpHist.HistEdges.edges[-1]+of_distance+of_width/2
#     edges_ou_plot = np.concatenate([[uf_center-uf_width/2 , uf_center+uf_width/2], NpHist.HistEdges.edges, [of_center-of_width/2 , of_center+of_width/2]])
#     hist_ou_plot = np.concatenate([[NpHist.uf, 0] , NpHist.hist, [0, NpHist.of]])
#     err_hist_ou_plot = np.concatenate([[NpHist.err_uf, 0] , NpHist.err_hist, [0, NpHist.err_of]])

#     mh.style.use("CMS")
#     mh.histplot(H=hist_ou_plot, bins=edges_ou_plot, yerr=err_hist_ou_plot, ax=PlotHistAx.ax, histtype="band", label="Data") # histtype="barstep"

#     # cut xticks to be within edges
#     xticks = [x for x in PlotHistAx.ax.get_xticks() if NpHist.HistEdges.edges[0] <= x <= NpHist.HistEdges.edges[-1]]
#     PlotHistAx.ax.xaxis.set_major_locator(mpl.ticker.FixedLocator(xticks))
#    # ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())

#     # add custom xtick labels for underflow / overflow
#     xticks = PlotHistAx.ax.get_xticks()
#     xticklabels_text = [xticklabel.get_text() for xticklabel in PlotHistAx.ax.get_xticklabels()]
#     xticks = np.concatenate(([uf_center], xticks, [of_center]))
#     xticklabels_text = ["UF"] + xticklabels_text + ["OF"]
#     # ax.set_xticks(xticks)
#     # ax.set_xticklabels(xticklabels_text)
#     PlotHistAx.ax.xaxis.set_major_locator(mpl.ticker.FixedLocator(xticks))
#     PlotHistAx.ax.xaxis.set_major_formatter(mpl.ticker.FixedFormatter(xticklabels_text))

#     # hide numeric xticks outside of edges (dont show for underflow / overflow)
#     # rotate custom underflow / overflow xtick labels
#     major_xticks = PlotHistAx.ax.xaxis.get_major_ticks()
#     n_xticks = len(major_xticks)
#     for i_xtick, xtick in enumerate(major_xticks):
#         xloc = xtick.get_loc()
#         # if ((xloc < NpHist.HistEdges.edges[0]-uf_distance/2 or xloc > NpHist.HistEdges.edges[-1]+of_distance/2) and xloc != uf_center and xloc != of_center):
#         #     xtick.tick1line.set_visible(False)
#         #     xtick.tick2line.set_visible(False)
#         if i_xtick == 0 or i_xtick == n_xticks-1:
#             xtick.label1.set_rotation(90)
    
#     # # hide numeric minor xticks outside of edges (dont show for underflow / overflow)
#     # minor_xticks = ax.xaxis.get_minor_ticks()
#     # for xtick in minor_xticks:
#     #     xloc = xtick.get_loc()
#     #     if ((xloc < NpHist.HistEdges.edges[0]-uf_distance/2 or xloc > NpHist.HistEdges.edges[-1]+of_distance/2) and xloc != uf_center and xloc != of_center):
#     #         xtick.tick1line.set_visible(False)
#     #         xtick.tick2line.set_visible(False)

#     # draw minor ticks only in range of edges
#     major_xticks = PlotHistAx.ax.get_xticks()[1:-1]
#     major_tick_step = np.mean(np.diff(major_xticks))
#     minor_xticks = []
#     for major_xtick in major_xticks:
#         minor_step = major_tick_step / 5
#         for i in [-2,-1,1,2]:
#             minor_pos = major_xtick+i*minor_step
#             if minor_pos >= NpHist.HistEdges.edges[0] and minor_pos <= NpHist.HistEdges.edges[-1]:
#                 minor_xticks.append(minor_pos)

#     PlotHistAx.ax.xaxis.set_minor_locator(mpl.ticker.FixedLocator(minor_xticks))

#     # draw separation lines between edges and underflow / overflow
#     PlotHistAx.ax.axvline(x=NpHist.HistEdges.edges[0]-uf_distance/2, color="black", linewidth=1, linestyle="--")
#     PlotHistAx.ax.axvline(x=NpHist.HistEdges.edges[-1]+of_distance/2, color="black", linewidth=1, linestyle="--")

#     # set xlim
#     PlotHistAx.ax.set_xlim(xmin=uf_center-uf_width/2-uf_distance/2, xmax=of_center+of_width/2+of_distance/2)

#     # set yscale and ylim
#     PlotHistAx.ax.set_yscale("log")
#     PlotHistAx.ax.set_ylim(ymin=0.5, ymax=np.amax(NpHist.hist_ou)*10)

#     # set xlabel
#     PlotHistAx.ax.set_xlabel(f"$p_{{T}}(\\mu_{{1}})$ [GeV]")

#     # set ylabel and note bin width
#     bin_width_max_digits = 3
#     bin_width_str = f"{mean_width:.{bin_width_max_digits}f}".rstrip("0").rstrip(".")
#     PlotHistAx.ax.set_ylabel(f"Events / {bin_width_str} GeV")