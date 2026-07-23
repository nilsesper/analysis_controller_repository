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
from analysis_controller.src import hist_utils

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_PATH, _ANALYSIS_CONTROLLER_REPO_PATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)

mh.style.use("CMS")

############################
### HELPER FUNCTIONS & CLASSES (with prefix "_")

### tick scalar formatter (respecting power limits), but keeping the underflow / overflow labels untouched
class _UFOFScalarFormatter(mpl.ticker.ScalarFormatter):
    def __init__(self, uf_center, of_center, uf_tick_label, of_tick_label, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uf_center = uf_center
        self.of_center = of_center
        self.uf_tick_label = uf_tick_label
        self.of_tick_label = of_tick_label

    def __call__(self, x, pos=None):
        if np.isclose(x, self.uf_center):
            return self.uf_tick_label
        if np.isclose(x, self.of_center):
            return self.of_tick_label
        return super().__call__(x, pos)

############################
### MAIN FUNCTIONS & CLASSES

class StructPlotHistAxParams:
    __slots__ = (
        "ax",
        "HistEdges",
        "show_uf", "show_of",
        "xlabel", "ylabel",
        "xunit", "yunit",
        "xscale", "yscale",
        "xlim_low", "xlim_high",
        "ylim_low", "ylim_high",
        "show_legend",
        "xticks_low_power_lim", "xticks_high_power_lim",
        "yticks_low_power_lim", "yticks_high_power_lim",
        "uf_tick_label", "of_tick_label",
        "yscale_if_same_yminmax",
        "auto_ylim_respect_err",
    )
    def __init__(self, *,
            ax,
            HistEdges,
            show_uf=True, show_of=True,
            xlabel=None, ylabel=None,
            xunit=None, yunit=None,
            xscale="linear", yscale="linear",
            xlim_low=None, xlim_high=None,
            ylim_low=None, ylim_high=None,
            show_legend=False,
            xticks_low_power_lim = -2, xticks_high_power_lim = 3,
            yticks_low_power_lim = -2, yticks_high_power_lim = 3,
            uf_tick_label="UF", of_tick_label="OF",
            yscale_if_same_yminmax = 0.5,
            auto_ylim_respect_err=False,
        ):
        self.ax = ax
        self.HistEdges = HistEdges
        self.show_uf = show_uf
        self.show_of = show_of
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.xunit = xunit
        self.yunit = yunit
        self.xscale = xscale
        self.yscale = yscale
        self.xlim_low = xlim_low
        self.xlim_high = xlim_high
        self.ylim_low = ylim_low
        self.ylim_high = ylim_high
        self.show_legend = show_legend
        self.xticks_low_power_lim = xticks_low_power_lim
        self.xticks_high_power_lim = xticks_high_power_lim
        self.yticks_low_power_lim = yticks_low_power_lim
        self.yticks_high_power_lim = yticks_high_power_lim
        self.uf_tick_label = uf_tick_label
        self.of_tick_label = of_tick_label
        self.yscale_if_same_yminmax = yscale_if_same_yminmax
        self.auto_ylim_respect_err = auto_ylim_respect_err
        self.update()
    def update(self):
        pass

class StructPlotHistAx:
    __slots__ = (
        "ax",
        "HistEdges",
        "show_uf", "show_of",
        "xlabel", "ylabel",
        "xunit", "yunit",
        "xscale", "yscale",
        "xlim_low", "xlim_high",
        "ylim_low", "ylim_high",
        "show_legend",
        "xticks_low_power_lim", "xticks_high_power_lim",
        "yticks_low_power_lim", "yticks_high_power_lim",
        "uf_tick_label", "of_tick_label",
        "yscale_if_same_yminmax",
        "auto_ylim_respect_err",
        #---
        "uf_width", "of_width",
        "uf_distance", "of_distance",
        "uf_center", "of_center",
        "uf_edges", "of_edges",
        "edges_ou_plot",
    )
    def __init__(self, *,
            PlotHistAxParams,
        ):
        self.ax = PlotHistAxParams.ax
        self.HistEdges = PlotHistAxParams.HistEdges
        self.show_uf = PlotHistAxParams.show_uf
        self.show_of = PlotHistAxParams.show_of
        self.xlabel = PlotHistAxParams.xlabel
        self.ylabel = PlotHistAxParams.ylabel
        self.xunit = PlotHistAxParams.xunit
        self.yunit = PlotHistAxParams.yunit
        self.xscale = PlotHistAxParams.xscale
        self.yscale = PlotHistAxParams.yscale
        self.xlim_low = PlotHistAxParams.xlim_low
        self.xlim_high = PlotHistAxParams.xlim_high
        self.ylim_low = PlotHistAxParams.ylim_low
        self.ylim_high = PlotHistAxParams.ylim_high
        self.show_legend = PlotHistAxParams.show_legend
        self.xticks_low_power_lim = PlotHistAxParams.xticks_low_power_lim
        self.xticks_high_power_lim = PlotHistAxParams.xticks_high_power_lim
        self.yticks_low_power_lim = PlotHistAxParams.yticks_low_power_lim
        self.yticks_high_power_lim = PlotHistAxParams.yticks_high_power_lim
        self.uf_tick_label = PlotHistAxParams.uf_tick_label
        self.of_tick_label = PlotHistAxParams.of_tick_label
        self.yscale_if_same_yminmax = PlotHistAxParams.yscale_if_same_yminmax
        self.auto_ylim_respect_err = PlotHistAxParams.auto_ylim_respect_err
        self.update()
    def update(self):
        self.uf_width = self.HistEdges.total_edges_width*0.05
        self.of_width = self.HistEdges.total_edges_width*0.05
        self.uf_distance = self.HistEdges.total_edges_width*0.05
        self.of_distance = self.HistEdges.total_edges_width*0.05
        self.uf_center = self.HistEdges.edges[0]-self.uf_distance-self.uf_width/2
        self.of_center = self.HistEdges.edges[-1]+self.of_distance+self.of_width/2
        self.uf_edges = [self.uf_center-self.uf_width/2, self.uf_center+self.uf_width/2]
        self.of_edges = [self.of_center-self.of_width/2, self.of_center+self.of_width/2]
        self.edges_ou_plot = np.concatenate([[self.uf_center-self.uf_width/2 , self.uf_center+self.uf_width/2], self.HistEdges.edges, [self.of_center-self.of_width/2 , self.of_center+self.of_width/2]])

class StructPlotHistParams:
    __slots__ = (
        "label",
        "color",
        "show_in_legend",
        "histtype",
        "markersize",
        "linewidth",
        "errorlinewidth",
    )
    def __init__(self, *,
            label=None,
            color="b",
            show_in_legend=False,
            histtype="barstep",
            markersize=5,
            linewidth=2,
            errorlinewidth=2,
        ):
        self.label = label
        self.color = color
        self.show_in_legend = show_in_legend
        self.histtype = histtype
        self.markersize = markersize
        self.linewidth = linewidth
        self.errorlinewidth = errorlinewidth
        self.update()
    def update(self):
        pass

class StructColorWheel:
    __slots__ = (
        "n_colors",
        "colors",
    )
    def __init__(self, *,
            colors
        ):
        self.colors = colors
        self.update()
    def update(self):
        self.n_colors = len(self.colors)
CMS6ColorWheel = StructColorWheel(colors=[
    "#5790fc",
    "#f89c20",
    "#e42536",
    "#964a8b",
    "#9c9ca1",
    "#7a21dd",
])
CMS10ColorWheel = StructColorWheel(colors=[
    "#3f90da",
    "#ffa90e",
    "#bd1f01",
    "#94a4a2",
    "#832db6",
    "#a96b59",
    "#e76300",
    "#b9ac70",
    "#717581",
    "#92dadd",
])

### get color from color wheel by index
def get_color_from_ColorWheel(*, index=0, ColorWheel=CMS6ColorWheel):
    n_colors = ColorWheel.n_colors
    sel_index = index % n_colors
    color = ColorWheel.colors[sel_index]
    return color

### create ax for hist plotting, with specified bins
def create_PlotHistAx_from_PlotHistAxParams(*, PlotHistAxParams):
    # create struct
    PlotHistAx = StructPlotHistAx(PlotHistAxParams=PlotHistAxParams)

    # set xlim
    if (not PlotHistAx.show_uf) and (not PlotHistAx.show_of):
        PlotHistAx.ax.set_xlim(xmin=PlotHistAx.HistEdges.edges[0], xmax=PlotHistAx.HistEdges.edges[-1])
    elif (PlotHistAx.show_uf) and (not PlotHistAx.show_of):
        PlotHistAx.ax.set_xlim(xmin=PlotHistAx.uf_center-PlotHistAx.uf_width/2-PlotHistAx.uf_distance/2, xmax=PlotHistAx.HistEdges.edges[-1])
    elif (not PlotHistAx.show_uf) and (PlotHistAx.show_of):
        PlotHistAx.ax.set_xlim(xmin=PlotHistAx.HistEdges.edges[0], xmax=PlotHistAx.of_center+PlotHistAx.of_width/2+PlotHistAx.of_distance/2)
    else:
        PlotHistAx.ax.set_xlim(xmin=PlotHistAx.uf_center-PlotHistAx.uf_width/2-PlotHistAx.uf_distance/2, xmax=PlotHistAx.of_center+PlotHistAx.of_width/2+PlotHistAx.of_distance/2)

    # cut xticks of hist to be within edges and add undeflow / overflow custom tick
    xticks = [x for x in PlotHistAx.ax.get_xticks() if PlotHistAx.HistEdges.edges[0] <= x <= PlotHistAx.HistEdges.edges[-1]]
    xticks = np.concatenate(([PlotHistAx.uf_center], xticks, [PlotHistAx.of_center]))
    PlotHistAx.ax.xaxis.set_major_locator(mpl.ticker.FixedLocator(xticks))

    # format xtick label numbers with scalar formatter (respect power limits), while setting custom underflow / overflow string tick labels
    custom_formatter = _UFOFScalarFormatter(uf_center=PlotHistAx.uf_center, of_center=PlotHistAx.of_center, uf_tick_label=PlotHistAx.uf_tick_label, of_tick_label=PlotHistAx.of_tick_label, useMathText=True)
    custom_formatter.set_powerlimits((PlotHistAxParams.xticks_low_power_lim, PlotHistAxParams.xticks_high_power_lim))
    PlotHistAx.ax.xaxis.set_major_formatter(custom_formatter)

    # move scalarformatter offset label, so it does not overlap with the xlabel
    if PlotHistAx.ax.xaxis.get_offset_text() is not None:
        xaxis_offset = PlotHistAx.ax.xaxis.get_offset_text()
        xaxis_offset.set_position((1, 0))
        xaxis_offset.set_ha("left")
        xaxis_offset.set_va("bottom")

    # hide numeric xticks outside of edges (dont show for underflow / overflow)
    # rotate custom underflow / overflow xtick labels
    major_xticks = PlotHistAx.ax.xaxis.get_major_ticks()
    n_xticks = len(major_xticks)
    for i_xtick, xtick in enumerate(major_xticks):
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
    if PlotHistAx.show_uf:
        PlotHistAx.ax.axvline(x=PlotHistAx.HistEdges.edges[0]-PlotHistAx.uf_distance/2, color="black", linewidth=1, linestyle="--")
    if PlotHistAx.show_of:
        PlotHistAx.ax.axvline(x=PlotHistAx.HistEdges.edges[-1]+PlotHistAx.of_distance/2, color="black", linewidth=1, linestyle="--")

    # set xlabel
    xunit = ""
    xunit_str = ""
    if PlotHistAxParams.xunit != None:
        xunit = PlotHistAxParams.xunit
        xunit_str = f" [{xunit}]"
    if PlotHistAx.xlabel != None:
        xlabel = f"{PlotHistAx.xlabel}{xunit_str}"
    else:
        xlabel = ""
    PlotHistAx.ax.set_xlabel(xlabel=xlabel)
    
    # xlabel_pos = PlotHistAx.ax.xaxis.get_label().get_position()
    # PlotHistAx.ax.xaxis.set_label_coords(0.5, xlabel_pos[1]+0.05)
    
    # PlotHistAx.ax.xaxis.set_label_coords(-0.3, -0.07)

    # xlabel = PlotHistAx.ax.xaxis.get_label()
    # xlabel_x, xlabel_y = xlabel.get_position()
    # PlotHistAx.ax.xaxis.set_label_coords(xlabel_x, xlabel_y -0.07)

    # set ylabel and note bin width
    yunit = "Events"
    if PlotHistAxParams.yunit != None:
        yunit = PlotHistAxParams.yunit
    bin_width_max_digits = 3
    bin_width_str = f"{PlotHistAx.HistEdges.mean_bin_width:.{bin_width_max_digits}f}".rstrip("0").rstrip(".")
    PlotHistAx.ax.set_ylabel(f"{yunit} / {bin_width_str} GeV")

    return PlotHistAx

### add NpHist histogram to existing ax with mplhep
def add_NpHist_to_PlotHistAx(*, NpHist, PlotHistAx, PlotHistParams):

    # plot histogram
    if PlotHistParams.histtype in ["step", "fill", "band", "bar", "barstep"]:
        # plot hist
        mh.histplot(H=NpHist.hist, bins=PlotHistAx.HistEdges.edges, yerr=NpHist.err_hist, ax=PlotHistAx.ax, histtype=PlotHistParams.histtype, color=PlotHistParams.color, linewidth=PlotHistParams.linewidth)
        # plot underflow
        if PlotHistAx.show_uf:
            mh.histplot(H=[NpHist.uf], bins=PlotHistAx.uf_edges, yerr=[NpHist.err_uf], ax=PlotHistAx.ax, histtype=PlotHistParams.histtype, color=PlotHistParams.color, linewidth=PlotHistParams.linewidth)
        # plot overflow
        if PlotHistAx.show_of:
            mh.histplot(H=[NpHist.of], bins=PlotHistAx.of_edges, yerr=[NpHist.err_of], ax=PlotHistAx.ax, histtype=PlotHistParams.histtype, color=PlotHistParams.color, linewidth=PlotHistParams.linewidth)
    elif PlotHistParams.histtype in ["errorbar"]:
        # plot hist
        mh.histplot(H=NpHist.hist, bins=PlotHistAx.HistEdges.edges, yerr=NpHist.err_hist, ax=PlotHistAx.ax, histtype=PlotHistParams.histtype, color=PlotHistParams.color, ms=PlotHistParams.markersize, linewidth=PlotHistParams.linewidth, elinewidth=PlotHistParams.errorlinewidth)
        # plot underflow
        if PlotHistAx.show_uf:
            mh.histplot(H=[NpHist.uf], bins=PlotHistAx.uf_edges, yerr=[NpHist.err_uf], ax=PlotHistAx.ax, histtype=PlotHistParams.histtype, color=PlotHistParams.color, ms=PlotHistParams.markersize, linewidth=PlotHistParams.linewidth, elinewidth=PlotHistParams.errorlinewidth)
        # plot overflow
        if PlotHistAx.show_of:
            mh.histplot(H=[NpHist.of], bins=PlotHistAx.of_edges, yerr=[NpHist.err_of], ax=PlotHistAx.ax, histtype=PlotHistParams.histtype, color=PlotHistParams.color, ms=PlotHistParams.markersize, linewidth=PlotHistParams.linewidth, elinewidth=PlotHistParams.errorlinewidth)

    # linear yscale:
    if PlotHistAx.yscale == "linear":
        # set yscale
        PlotHistAx.ax.set_yscale("linear")
        # determine ylim
        if PlotHistAx.auto_ylim_respect_err: # if should include errors in ylim
            ymin = np.amin(NpHist.hist_ou - NpHist.err_hist_ou)*1.2
            ymax = np.amax(NpHist.hist_ou + NpHist.err_hist_ou)*1.2
        else:
            ymin = np.amin(NpHist.hist_ou)*1.2
            ymax = np.amax(NpHist.hist_ou)*1.2
        if PlotHistAx.ylim_low != None:
            ymin = PlotHistAx.ylim_low
        if PlotHistAx.ylim_high != None:
            ymax = PlotHistAx.ylim_high
        if ymin == ymax:
            ymin -= PlotHistAx.yscale_if_same_yminmax/2
            ymax += PlotHistAx.yscale_if_same_yminmax/2
        # set ylim
        PlotHistAx.ax.set_ylim(ymin=ymin, ymax=ymax)
        # set yticks power limits
        formatter = mpl.ticker.ScalarFormatter(useMathText=True)
        formatter.set_powerlimits((PlotHistAx.yticks_low_power_lim, PlotHistAx.yticks_high_power_lim))
        PlotHistAx.ax.yaxis.set_major_formatter(formatter)
    # log yscale:
    elif PlotHistAx.yscale == "log":
        # set yscale
        PlotHistAx.ax.set_yscale("log")
        # set ylim
        # determine ylim
        if PlotHistAx.auto_ylim_respect_err: # if should include errors in ylim
            ymin = 0.5
            ymax = np.amax(NpHist.hist_ou + NpHist.err_hist_ou)*10
        else:
            ymin = 0.5
            ymax = np.amax(NpHist.hist_ou)*10
        if PlotHistAx.ylim_low != None:
            ymin = PlotHistAx.ylim_low
        if PlotHistAx.ylim_high != None:
            ymax = PlotHistAx.ylim_high
        if ymin == ymax:
            ymin -= PlotHistAx.yscale_if_same_yminmax/2
            ymax += PlotHistAx.yscale_if_same_yminmax/2
        PlotHistAx.ax.set_ylim(ymin=ymin, ymax=ymax)

    # add entry to legend, if desired
    if PlotHistAx.show_legend and PlotHistParams.show_in_legend:
        label = ""
        if PlotHistParams.label != None:
            label = PlotHistParams.label
        # get existing handles
        if PlotHistAx.ax.get_legend() is not None:
            legend = PlotHistAx.ax.get_legend()
            handles = legend.legend_handles
            labels = [text.get_text() for text in legend.get_texts()]
        else:
            handles = []
            labels = []
        # insert new handle
        #   histtypes: ["step", "fill", "errorbar", "band", "bar", "barstep"]
        if PlotHistParams.histtype in ["step", "barstep"]:
            handle = mpl.lines.Line2D([], [], color=PlotHistParams.color)
        elif PlotHistParams.histtype in ["errorbar"]:
            handle = PlotHistAx.ax.errorbar([], [], xerr=1, yerr=1, linestyle="None", marker="o", color=PlotHistParams.color, linewidth=PlotHistParams.errorlinewidth)
        elif PlotHistParams.histtype in ["band", "bar", "fill"]:
            # handle = mpl.lines.Line2D([], [], color=PlotHistParams.color)
            handle = mpl.patches.Patch(facecolor=PlotHistParams.color) #edgecolor="black",
        # update legend
        PlotHistAx.ax.legend(handles=handles+[handle], labels=labels+[label], frameon=True, facecolor='white', edgecolor='lightgray', framealpha=0.5, fancybox=False)
    
    return PlotHistAx


### add NpHist histogram to existing ax with mplhep
# pass list of NpHist, PlotHistParams
def add_NpHist_stack_to_PlotHistAx(*, NpHist_list, PlotHistAx, PlotHistParams_list):

    n_hists = len(NpHist_list)
    if n_hists == 0:
        return PlotHistAx

    # plot histogram
    histtype = PlotHistParams_list[0].histtype
    hists = [NpHist_list[i_hist].hist for i_hist in range(n_hists)]
    ufs = [[NpHist_list[i_hist].uf] for i_hist in range(n_hists)]
    ofs = [[NpHist_list[i_hist].of] for i_hist in range(n_hists)]
    colors = [PlotHistParams_list[i_hist].color for i_hist in range(n_hists)]
    linewidths = [PlotHistParams_list[i_hist].linewidth for i_hist in range(n_hists)]
    errorlinewidths = [PlotHistParams_list[i_hist].errorlinewidth for i_hist in range(n_hists)]
    markersizes = [PlotHistParams_list[i_hist].markersize for i_hist in range(n_hists)]
    if histtype in ["step", "fill", "band", "bar", "barstep"]:
        # plot hist
        mh.histplot(H=hists, stack=True, bins=PlotHistAx.HistEdges.edges, ax=PlotHistAx.ax, histtype=histtype, color=colors, linewidth=linewidths)
        # plot underflow
        if PlotHistAx.show_uf:
            mh.histplot(H=ufs, stack=True, bins=PlotHistAx.uf_edges, ax=PlotHistAx.ax, histtype=histtype, color=colors, linewidth=linewidths)
        # plot overflow
        if PlotHistAx.show_of:
            mh.histplot(H=ofs, stack=True, bins=PlotHistAx.of_edges, ax=PlotHistAx.ax, histtype=histtype, color=colors, linewidth=linewidths)
    elif histtype in ["errorbar"]:
        # plot hist
        mh.histplot(H=hists, stack=True, bins=PlotHistAx.HistEdges.edges, ax=PlotHistAx.ax, histtype=histtype, color=colors, ms=markersizes, linewidth=linewidths, elinewidth=errorlinewidths)
        # plot underflow
        if PlotHistAx.show_uf:
            mh.histplot(H=ufs, stack=True, bins=PlotHistAx.uf_edges, ax=PlotHistAx.ax, histtype=histtype, color=colors, ms=markersizes, linewidth=linewidths, elinewidth=errorlinewidths)
        # plot overflow
        if PlotHistAx.show_of:
            mh.histplot(H=ofs, stack=True, bins=PlotHistAx.of_edges, ax=PlotHistAx.ax, histtype=histtype, color=colors, ms=markersizes, linewidth=linewidths, elinewidth=errorlinewidths)

    """
    # linear yscale:
    if PlotHistAx.yscale == "linear":
        # set yscale
        PlotHistAx.ax.set_yscale("linear")
        # determine ylim
        if PlotHistAx.auto_ylim_respect_err: # if should include errors in ylim
            ymin = np.amin(NpHist.hist_ou - NpHist.err_hist_ou)*1.2
            ymax = np.amax(NpHist.hist_ou + NpHist.err_hist_ou)*1.2
        else:
            ymin = np.amin(NpHist.hist_ou)*1.2
            ymax = np.amax(NpHist.hist_ou)*1.2
        if PlotHistAx.ylim_low != None:
            ymin = PlotHistAx.ylim_low
        if PlotHistAx.ylim_high != None:
            ymax = PlotHistAx.ylim_high
        if ymin == ymax:
            ymin -= PlotHistAx.yscale_if_same_yminmax/2
            ymax += PlotHistAx.yscale_if_same_yminmax/2
        # set ylim
        PlotHistAx.ax.set_ylim(ymin=ymin, ymax=ymax)
        # set yticks power limits
        formatter = mpl.ticker.ScalarFormatter(useMathText=True)
        formatter.set_powerlimits((PlotHistAx.yticks_low_power_lim, PlotHistAx.yticks_high_power_lim))
        PlotHistAx.ax.yaxis.set_major_formatter(formatter)
    # log yscale:
    elif PlotHistAx.yscale == "log":
        # set yscale
        PlotHistAx.ax.set_yscale("log")
        # set ylim
        # determine ylim
        if PlotHistAx.auto_ylim_respect_err: # if should include errors in ylim
            ymin = 0.5
            ymax = np.amax(NpHist.hist_ou + NpHist.err_hist_ou)*10
        else:
            ymin = 0.5
            ymax = np.amax(NpHist.hist_ou)*10
        if PlotHistAx.ylim_low != None:
            ymin = PlotHistAx.ylim_low
        if PlotHistAx.ylim_high != None:
            ymax = PlotHistAx.ylim_high
        if ymin == ymax:
            ymin -= PlotHistAx.yscale_if_same_yminmax/2
            ymax += PlotHistAx.yscale_if_same_yminmax/2
        PlotHistAx.ax.set_ylim(ymin=ymin, ymax=ymax)
    """
        
    # add entry to legend, if desired
    for i_hist in range(n_hists):
        if PlotHistAx.show_legend and PlotHistParams_list[i_hist].show_in_legend:
            label = ""
            if PlotHistParams_list[i_hist].label != None:
                label = PlotHistParams_list[i_hist].label
            # get existing handles
            if PlotHistAx.ax.get_legend() is not None:
                legend = PlotHistAx.ax.get_legend()
                handles = legend.legend_handles
                labels = [text.get_text() for text in legend.get_texts()]
            else:
                handles = []
                labels = []
            # insert new handle
            #   histtypes: ["step", "fill", "errorbar", "band", "bar", "barstep"]
            if PlotHistParams_list[i_hist].histtype in ["step", "barstep"]:
                handle = mpl.lines.Line2D([], [], color=PlotHistParams_list[i_hist].color)
            elif PlotHistParams_list[i_hist].histtype in ["errorbar"]:
                handle = PlotHistAx.ax.errorbar([], [], xerr=1, yerr=1, linestyle="None", marker="o", color=PlotHistParams_list[i_hist].color, linewidth=PlotHistParams_list[i_hist].errorlinewidth)
            elif PlotHistParams_list[i_hist].histtype in ["band", "bar", "fill"]:
                # handle = mpl.lines.Line2D([], [], color=PlotHistParams.color)
                handle = mpl.patches.Patch(facecolor=PlotHistParams_list[i_hist].color) #edgecolor="black",
            # update legend
            PlotHistAx.ax.legend(handles=handles+[handle], labels=labels+[label], frameon=True, facecolor='white', edgecolor='lightgray', framealpha=0.5, fancybox=False)
    
    return PlotHistAx


