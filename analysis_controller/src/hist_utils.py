#######################
### HISTOGRAM UTILS ###
#######################

############################
### IMPORTS

import os
import numpy as np
import ROOT
import matplotlib as mpl
import matplotlib.pyplot as plt
import mplhep as mh

from analysis_controller.src import path_utils

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
        self.err_uf = self.hist_ou[0]
        self.err_of = self.hist_ou[-1]

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

### create uniform bin edges in [low_edge, high_edge] with num_bins
def create_HistEdges_uniform(*, low_edge, high_edge, n_bins):
    # create uniform edges as linspace
    edges = np.linspace(start=low_edge, stop=high_edge, num=n_bins+1)
    # create struct
    HistEdges = StructHistEdges(edges=edges)
    return HistEdges

### create data points
def create_DataPts(*, data_pts=[], data_weights=None):
    # set weights to one if none given
    if data_weights == None:
        data_weights = np.ones(len(data_pts))
    # create struct
    DataPts = StructDataPts(data_pts=data_pts, data_weights=data_weights)
    return DataPts

### create root hist with given edges, and optionally fill it with data points
def create_RootHist(*, HistEdges, DataPts=create_DataPts(data_pts=[])):
    # prepare root hist
    roothist = ROOT.TH1D("h", "Histogram", HistEdges.n_bins, HistEdges.low_edge, HistEdges.high_edge)
    roothist.Sumw2()
    # fill root hist
    data_pts_root = np.ascontiguousarray(DataPts.data_pts, dtype=np.float64)
    data_weights_root = np.ascontiguousarray(DataPts.data_weights, dtype=np.float64)
    roothist.FillN(DataPts.n_data_pts, data_pts_root, data_weights_root)
    # create struct
    RootHist = StructRootHist(HistEdges=HistEdges, roothist=roothist)
    return RootHist

### create np hist with given edges, and optionally fill it with data points
def create_NpHist(*, HistEdges, DataPts=create_DataPts(data_pts=[])):
    # fill np hist
    hist_ou, edges_ou = np.histogram(a=DataPts.data_pts, bins=HistEdges.edges_ou, weights=DataPts.data_weights)
    err_hist_ou = np.sqrt( np.histogram(a=DataPts.data_pts, bins=HistEdges.edges_ou, weights=DataPts.data_weights**2)[0] )
    # create struct
    NpHist = StructNpHist(HistEdges=HistEdges, hist_ou=hist_ou, err_hist_ou=err_hist_ou)
    return NpHist

### convert RootHist to NpHist
def convert_RootHist_to_NpHist(*, RootHist):
    hist_ou = np.array([ RootHist.roothist.GetBinContent(i) for i in range(RootHist.HistEdges.n_bins+2) ]) # [uf, hist, of]
    err_hist_ou = np.array([ RootHist.roothist.GetBinError(i) for i in range(RootHist.HistEdges.n_bins+2) ]) # [err_uf, err_hist, err_of]
    NpHist = StructNpHist(HistEdges=RootHist.HistEdges, hist_ou=hist_ou, err_hist_ou=err_hist_ou)
    return NpHist

### generic of/uf handling
# edges = edges_ou[1:-1]
# uf, hist, of = hist_ou[0], hist_ou[1:-1], hist_ou[-1]
# err_uf, err_hist, err_of = err_hist_ou[0], err_hist_ou[1:-1], err_hist_ou[-1]
