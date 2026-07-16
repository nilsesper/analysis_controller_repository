#######################
### HISTOGRAM UTILS ###
#######################

############################
### IMPORTS

import os
import numpy as np
import ROOT

from analysis_controller.src import path_utils
from analysis_controller.src import console_utils

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_PATH, _ANALYSIS_CONTROLLER_REPO_PATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)

############################
### HELPER FUNCTIONS & CLASSES (with prefix "_")

class StructHistEdges:
    __slots__ = (
        "edges",
        #---
        "n_edges",
        "low_edge", "high_edge",
        "edges_ou",
        "bins",
        "n_bins",
        "uniform",
        "mean_bin_width",
        "total_edges_width",
    )
    def __init__(self, *, edges):
        self.edges = edges
        self.update()
    def update(self):
        # get num of edges
        self.n_edges = len(self.edges)
        # get min and max edge
        self.low_edge = np.amin(self.edges)
        self.high_edge = np.amax(self.edges)
        # add underflow and overflow bins
        self.edges_ou = np.concatenate([[-np.inf], self.edges, [np.inf]])
        # calculate bin centers
        self.bins = np.array([self.edges[i+1] - self.edges[i] for i in range(self.n_edges-1)])
        # get num of bins
        self.n_bins = self.n_edges-1
        # determine if bins are uniform
        # (this is the case if the distance between neighboring edges is the same everywhere)
        edge_diff = np.diff(self.edges)
        self.uniform = all(x == edge_diff[0] for x in edge_diff)
        # calculate mean bin width
        self.mean_bin_width = np.mean(np.diff(self.edges))
        # calculate total width of edges (without underflow / overflow)
        self.total_edges_width = self.edges[-1] - self.edges[0]

class StructDataPts:
    __slots__ = (
        "data_pts",
        "data_weights",
        #---
        "n_data_pts",
    )
    def __init__(self, *, data_pts, data_weights):
        self.data_pts = data_pts
        self.data_weights = data_weights
        self.update()
    def update(self):
        self.n_data_pts = len(self.data_pts)

class StructNpHist:
    __slots__ = (
        "HistEdges",
        "hist_ou",
        "err_hist_ou",
        #---
        "hist",
        "uf", "of",
        "err_hist",
        "err_uf", "err_of",
    )
    def __init__(self, *, HistEdges, hist_ou, err_hist_ou):
        self.HistEdges = HistEdges
        self.hist_ou = hist_ou
        self.err_hist_ou = err_hist_ou
        self.update()
    def update(self):
        # hist entries w/o underflow and overflow
        self.hist = self.hist_ou[1:-1]
        # underflow and overflow
        self.uf = self.hist_ou[0]
        self.of = self.hist_ou[-1]
        # errors on hist entries w/o underflow and overflow
        self.err_hist = self.err_hist_ou[1:-1]
        # errors on underflow and overflow
        self.err_uf = self.err_hist_ou[0]
        self.err_of = self.err_hist_ou[-1]

class StructRootHist:
    __slots__ = (
        "HistEdges",
        "roothist"
        #---
    )
    def __init__(self, *, HistEdges, roothist):
        self.HistEdges = HistEdges
        self.roothist = roothist
        self.update()
    def update(self):
        pass

############################
### MAIN FUNCTIONS & CLASSES

#####################
### hist edges

### create uniform bin edges in [low_edge, high_edge] with num_bins
def create_HistEdges_uniform(*, low_edge, high_edge, n_bins):
    # create uniform edges as linspace
    edges = np.linspace(start=low_edge, stop=high_edge, num=n_bins+1)
    # create struct
    HistEdges = StructHistEdges(edges=edges)
    return HistEdges

#####################
### data points

### create data points
def create_DataPts(*, data_pts=[], data_weights=None):
    # set weights to one if none given
    if data_weights is None:
        data_weights = np.ones(len(data_pts))
    # create struct
    DataPts = StructDataPts(data_pts=data_pts, data_weights=data_weights)
    return DataPts

#####################
### root hist

### create RootHist with given edges
# and optionally fill it with data points
def create_RootHist(*, HistEdges, DataPts=create_DataPts(data_pts=[])):
    # prepare root hist
    roothist = ROOT.TH1D("h", "Histogram", HistEdges.n_bins, HistEdges.low_edge, HistEdges.high_edge)
    roothist.Sumw2()
    # fill root hist, with weights
    data_pts_root = np.ascontiguousarray(DataPts.data_pts, dtype=np.float64)
    data_weights_root = np.ascontiguousarray(DataPts.data_weights, dtype=np.float64)
    roothist.FillN(DataPts.n_data_pts, data_pts_root, data_weights_root)
    # create struct
    RootHist = StructRootHist(HistEdges=HistEdges, roothist=roothist)
    return RootHist

### add data points to RootHist
def add_DataPts_to_RootHist(*, RootHist, DataPts):
    # add data to root hist, with weights
    data_pts_root = np.ascontiguousarray(DataPts.data_pts, dtype=np.float64)
    data_weights_root = np.ascontiguousarray(DataPts.data_weights, dtype=np.float64)
    RootHist.roothist.FillN(DataPts.n_data_pts, data_pts_root, data_weights_root)
    # update internal hist parameters
    RootHist.update()
    return RootHist

### calculate linear combination of N RootHists with factor scaling each hist globally
def linear_combination_RootHists(*, RootHists, factors=None):
    n_hists = len(RootHists)
    # determine hist edges
    HistEdges = RootHists[0].HistEdges
    # check if all edges are actually the same
    has_same_edges = True
    for i_hist in range(n_hists):
        # compare edge count
        has_same_edges &= (HistEdges.n_edges == RootHists[i_hist].HistEdges.n_edges)
        # compare edge values
        if has_same_edges:
            has_same_edges &= all([HistEdges.edges[i_edge] == RootHists[i_hist].HistEdges.edges[i_edge] for i_edge in range(HistEdges.n_edges)])
    if not has_same_edges:
        console_utils.raise_exception(string="Histograms must have the same HistEdges in order to add them together")
    # import factor
    if factors == None:
        factors = np.ones(n_hists)
    factors = np.array(factors)
    if len(factors) != n_hists:
        console_utils.raise_exception(string="Factor must have same length as no of histograms")
    # add roothists together
    roothist_combined = ROOT.TH1D("h", "Histogram", HistEdges.n_bins, HistEdges.low_edge, HistEdges.high_edge)
    roothist_combined.Sumw2()
    for i_hist in range(n_hists):
        roothist_combined.Add(RootHists[i_hist].roothist, factors[i_hist])
    # create struct
    RootHist_combined = StructRootHist(HistEdges=HistEdges, roothist=roothist_combined)
    return RootHist_combined

### convert RootHist to NpHist
def convert_RootHist_to_NpHist(*, RootHist):
    hist_ou = np.array([ RootHist.roothist.GetBinContent(i) for i in range(RootHist.HistEdges.n_bins+2) ]) # [uf, hist, of]
    err_hist_ou = np.array([ RootHist.roothist.GetBinError(i) for i in range(RootHist.HistEdges.n_bins+2) ]) # [err_uf, err_hist, err_of]
    NpHist = StructNpHist(HistEdges=RootHist.HistEdges, hist_ou=hist_ou, err_hist_ou=err_hist_ou)
    return NpHist

#####################
### numpy hist

### create NpHist with given edges
# and optionally fill it with data points
def create_NpHist(*, HistEdges, DataPts=create_DataPts(data_pts=[])):
    # fill np hist, with weights
    hist_ou, _ = np.histogram(a=DataPts.data_pts, bins=HistEdges.edges_ou, weights=DataPts.data_weights)
    # determine hist error
    #   root as reference:
    #   - unweighted histogram: square root of bin content
    #   - weighted histogram: square root of the bin sum of the weights square
    hist_ou_square_weights, _ = np.histogram(a=DataPts.data_pts, bins=HistEdges.edges_ou, weights=DataPts.data_weights**2)
    err_hist_ou = np.sqrt(hist_ou_square_weights)
    # create struct
    NpHist = StructNpHist(HistEdges=HistEdges, hist_ou=hist_ou, err_hist_ou=err_hist_ou)
    return NpHist

### add data points to NpHist
def add_DataPts_to_NpHist(*, NpHist, DataPts):
    ### calculate hist for new data points
    NpHist_add = create_NpHist(HistEdges=NpHist.HistEdges, DataPts=DataPts)
    ### merge old histogram with new one
    NpHist_combined = linear_combination_NpHists(NpHists=[NpHist, NpHist_add])
    return NpHist_combined

### calculate linear combination of N NpHists with factor scaling each hist globally
def linear_combination_NpHists(*, NpHists, factors=None):
    n_hists = len(NpHists)
    # determine hist edges
    HistEdges = NpHists[0].HistEdges
    # check if all edges are actually the same
    has_same_edges = True
    for i_hist in range(n_hists):
        # compare edge count
        has_same_edges &= (HistEdges.n_edges == NpHists[i_hist].HistEdges.n_edges)
        # compare edge values
        if has_same_edges:
            has_same_edges &= all([HistEdges.edges[i_edge] == NpHists[i_hist].HistEdges.edges[i_edge] for i_edge in range(HistEdges.n_edges)])
    if not has_same_edges:
        console_utils.raise_exception(string="Histograms must have the same HistEdges in order to add them together")
    # import factor
    if factors == None:
        factors = np.ones(n_hists)
    factors = np.array(factors)
    if len(factors) != n_hists:
        console_utils.raise_exception(string="Factor must have same length as no of histograms")
    # prepare new np hist
    NpHist_combined = create_NpHist(HistEdges=HistEdges)
    # combine histogram bins:
    #   - hist_single[bin] = sum(weights_single[bin])
    #   - hist_combined[bin] = sum(weights_combined[bin]) = sum(weights_0[bin] + weights_1[bin]) = sum(weights_0[bin]) + sum(weights_1[bin])
    #     = hist_0[bin] + hist_1[bin]
    hists_ou = np.array([NpHists[i_hist].hist_ou * factors[i_hist] for i_hist in range(n_hists)]) # [i_hist: hist_ou] + apply scaling factor
    NpHist_combined.hist_ou = np.sum(hists_ou, axis=0) # sum hist entries bin by bin
    # NpHist.hist_ou = NpHist1.hist_ou + NpHist2.hist_ou
    # combine bin error:
    #   - err_hist_single[bin] = sqrt( sum(weights_single[bin]**2) )
    #   - err_hist_combined[bin] = sqrt{ sum(weights_combined[bin]**2) } = sqrt( sum(weights_0[bin]**2 + weights_1[bin]**2) } = sqrt{ sum(weights_0[bin]**2) + sum(weights_1[bin]**2) } = sqrt{ sqrt( sum(weights_0[bin]**2) )**2 + sqrt( sum(weights_1[bin]**2) )**2 }
    #      = sqrt{ err_hist_0[bin]**2 + err_hist_1[bin]**2 }
    err_hists_ou = np.array([NpHists[i_hist].err_hist_ou * np.abs(factors[i_hist]) for i_hist in range(n_hists)]) # [i_hist: hist_ou] + apply scaling factor
    NpHist_combined.err_hist_ou = np.sqrt(np.sum(err_hists_ou**2, axis=0)) # sum sum of square weights bin by bin
    # NpHist.err_hist_ou = np.sqrt(NpHist1.err_hist_ou**2 + NpHist2.err_hist_ou**2)
    # update internal hist parameters
    NpHist_combined.update()
    return NpHist_combined


