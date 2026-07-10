##############################
### DEV SCRIPT FOR TESTING ###
##############################

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

from analysis_controller.src import path_utils
from analysis_controller.src import file_utils
from analysis_controller.src import console_utils

from analysis_controller.src import analysis_utils
from analysis_controller.src import analysis_params

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_PATH, _ANALYSIS_CONTROLLER_REPO_PATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)
console_utils.print_console_header(analysis_controller_filepath=_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH)

start_time = time.time()


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
# optional:
args = parser.parse_args()

#############################
#****************************
### MAIN PART

### parse args
infile_path = args.input
outfile_path = args.output

#infile_path = "~/promotion/test_analysis_hscp_l1/_localtest/1_reKBMTF/output.root"
#infile_path = "~/promotion/test_analysis_hscp_l1/_localtest/1_reKBMTF/rekbmtf_example_output_1.root"
#infile_path = "root://xrootd-cms.infn.it///store/user/nesper/test_analysis_hscp_l1/L1Scouting/crab_Scouting_2024H/260618_105926/0000/output_1.root"
#infile_path = "~/promotion/test_analysis_hscp_l1/_localtest/1_reKBMTF/hadd_test_output_0.root"
#infile_path = "/home/home1/institut_3a/esper/promotion/test_analysis_hscp_l1/analysis_controller_repository/scripts_analysis/finalselection/rekbmtf_data.root"
#outfile_path = "/home/home1/institut_3a/esper/promotion/test_analysis_hscp_l1/analysis_controller_repository/scripts_analysis/finalselection/finalselection_slowdata.root"

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

### add initial index to arr
row_indices = ak.local_index(arr, axis=0)
arr["treeidx"] = row_indices
n_entries = len(row_indices)
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The imported dataset has \"{n_entries}\" events")

### overview of input array
# for data:
"""
arr.type.show() = {
    run: uint32,
    luminosityBlock: uint32,
    bunchCrossing: uint32,
    orbitNumber: uint32,
    nL1KBMTFSkimmed: int32,
    L1KBMTFSkimmed_hwCharge: var * int16,
    L1KBMTFSkimmed_hwQual: var * int16,
    L1KBMTFSkimmed_hwDXY: var * int16,
    L1KBMTFSkimmed_hwK: var * int16,
    L1KBMTFSkimmed_processor: var * int16,
    L1KBMTFSkimmed_nStub: var * int16,
    L1KBMTFSkimmed_s1Station: var * int16,
    L1KBMTFSkimmed_s1Sector: var * int16,
    L1KBMTFSkimmed_s1Wheel: var * int16,
    L1KBMTFSkimmed_s1HwQual: var * int16,
    L1KBMTFSkimmed_s1Bx: var * int16,
    L1KBMTFSkimmed_s2Station: var * int16,
    L1KBMTFSkimmed_s2Sector: var * int16,
    L1KBMTFSkimmed_s2Wheel: var * int16,
    L1KBMTFSkimmed_s2HwQual: var * int16,
    L1KBMTFSkimmed_s2Bx: var * int16,
    L1KBMTFSkimmed_s3Station: var * int16,
    L1KBMTFSkimmed_s3Sector: var * int16,
    L1KBMTFSkimmed_s3Wheel: var * int16,
    L1KBMTFSkimmed_s3HwQual: var * int16,
    L1KBMTFSkimmed_s3Bx: var * int16,
    L1KBMTFSkimmed_s4Station: var * int16,
    L1KBMTFSkimmed_s4Sector: var * int16,
    L1KBMTFSkimmed_s4Wheel: var * int16,
    L1KBMTFSkimmed_s4HwQual: var * int16,
    L1KBMTFSkimmed_s4Bx: var * int16,
    L1KBMTFSkimmed_bx: var * int32,
    L1KBMTFSkimmed_pt: var * float32,
    L1KBMTFSkimmed_eta: var * float32,
    L1KBMTFSkimmed_phi: var * float32,
    L1KBMTFSkimmed_met_bxm9: var * float32,
    L1KBMTFSkimmed_met_bxm8: var * float32,
    L1KBMTFSkimmed_met_bxm7: var * float32,
    L1KBMTFSkimmed_met_bxm6: var * float32,
    L1KBMTFSkimmed_met_bxm5: var * float32,
    L1KBMTFSkimmed_met_bxm4: var * float32,
    L1KBMTFSkimmed_met_bxm3: var * float32,
    L1KBMTFSkimmed_met_bxm2: var * float32,
    L1KBMTFSkimmed_met_bxm1: var * float32,
    L1KBMTFSkimmed_met_bx0: var * float32,
    L1KBMTFSkimmed_ptUnconstrained: var * float32,
    L1KBMTFSkimmed_etaAtVtx: var * float32,
    L1KBMTFSkimmed_phiAtVtx: var * float32,
    nSkimmedL1Mu: int32,
    SkimmedL1Mu_hwCharge: var * int32,
    SkimmedL1Mu_hwQual: var * int32,
    SkimmedL1Mu_hwDXY: var * int32,
    SkimmedL1Mu_tfMuonIndex: var * int32,
    SkimmedL1Mu_ptUnconstrained: var * float32,
    SkimmedL1Mu_etaAtVtx: var * float32,
    SkimmedL1Mu_phiAtVtx: var * float32,
    SkimmedL1Mu_pt: var * float32,
    SkimmedL1Mu_eta: var * float32,
    SkimmedL1Mu_phi: var * float32
}
"""
# for simulation:
"""
???
"""


### calculate min_bx for arr
## for single track
@nb.jit
def track_first_bx(nStub, s1Bx, s2Bx, s3Bx, s4Bx):
    first_bx = -1
    if nStub == 1:
        first_bx = min([s1Bx])
    elif nStub == 2:
        first_bx = min([s1Bx, s2Bx])
    elif nStub == 3:
        first_bx = min([s1Bx, s2Bx, s3Bx])
    elif nStub == 4:
        first_bx = min([s1Bx, s2Bx, s3Bx, s4Bx])
    return first_bx
## generate ak arr
@nb.jit
def arr_min_bx(events, builder):
    n_events = len(events)
    for i_event in range(n_events):
        builder.begin_list()
        event = events[i_event]
        n_tracks = len(event.L1KBMTFSkimmed_nStub)
        for i_track in range(n_tracks):
            first_bx = track_first_bx(nStub=event.L1KBMTFSkimmed_nStub[i_track], s1Bx=event.L1KBMTFSkimmed_s1Bx[i_track], s2Bx=event.L1KBMTFSkimmed_s2Bx[i_track], s3Bx=event.L1KBMTFSkimmed_s3Bx[i_track], s4Bx=event.L1KBMTFSkimmed_s4Bx[i_track])
            builder.integer(first_bx)
        builder.end_list()
    return builder
## add field to arr
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Calculating \"firstbx\" for all tracks")
builder = ak.ArrayBuilder()
arr_min_bx(events=arr, builder=builder)
arr["L1KBMTFSkimmed_firstBx"] = builder.snapshot()

### calculate bx_spread for arr
# because of inner order of kbmtf algo, the order is always outer station -> inner station
# therefore a good track coming from the interaction point has outer bx >= inner bx
## for single track
@nb.jit
def track_bx_spread(nStub, firstBx, s1Bx, s2Bx, s3Bx, s4Bx):
    bx_spread = -1
    if nStub == 1:
        bx_spread = 1000*(s1Bx - firstBx)
    elif nStub == 2:
        bx_spread = 1000*(s1Bx - firstBx) + 100*(s2Bx - firstBx)
    elif nStub == 3:
        bx_spread = 1000*(s1Bx - firstBx) + 100*(s2Bx - firstBx) + 10*(s3Bx - firstBx)
    elif nStub == 4:
        bx_spread = 1000*(s1Bx - firstBx) + 100*(s2Bx - firstBx) + 10*(s3Bx - firstBx) + 1*(s4Bx - firstBx)
    return bx_spread
## generate ak arr
@nb.jit
def arr_bx_spread(events, builder):
    n_events = len(events)
    for i_event in range(n_events):
        builder.begin_list()
        event = events[i_event]
        n_tracks = len(event.L1KBMTFSkimmed_nStub)
        for i_track in range(n_tracks):
            bx_spread = track_bx_spread(nStub=event.L1KBMTFSkimmed_nStub[i_track], firstBx=event.L1KBMTFSkimmed_firstBx[i_track], s1Bx=event.L1KBMTFSkimmed_s1Bx[i_track], s2Bx=event.L1KBMTFSkimmed_s2Bx[i_track], s3Bx=event.L1KBMTFSkimmed_s3Bx[i_track], s4Bx=event.L1KBMTFSkimmed_s4Bx[i_track])
            builder.integer(bx_spread)
        builder.end_list()
    return builder
## add field to arr
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Calculating \"bxspread\" for all tracks")
builder = ak.ArrayBuilder()
arr_bx_spread(events=arr, builder=builder)
arr["L1KBMTFSkimmed_bxSpread"] = builder.snapshot()

### calculate st_spread for arr
# because of inner order of kbmtf algo, the order is always outer station -> inner station
# therefore always st_spread monotnically decreasing
## for single track
@nb.jit
def track_st_spread(nStub, s1Station, s2Station, s3Station, s4Station):
    st_spread = -1
    if nStub == 1:
        st_spread = 1000*(s1Station)
    elif nStub == 2:
        st_spread = 1000*(s1Station) + 100*(s2Station)
    elif nStub == 3:
        st_spread = 1000*(s1Station) + 100*(s2Station) + 10*(s3Station)
    elif nStub == 4:
        st_spread = 1000*(s1Station) + 100*(s2Station) + 10*(s3Station) + 1*(s4Station)
    return st_spread
## generate ak arr
@nb.jit
def arr_st_spread(events, builder):
    n_events = len(events)
    for i_event in range(n_events):
        builder.begin_list()
        event = events[i_event]
        n_tracks = len(event.L1KBMTFSkimmed_nStub)
        for i_track in range(n_tracks):
            st_spread = track_st_spread(nStub=event.L1KBMTFSkimmed_nStub[i_track], s1Station=event.L1KBMTFSkimmed_s1Station[i_track], s2Station=event.L1KBMTFSkimmed_s2Station[i_track], s3Station=event.L1KBMTFSkimmed_s3Station[i_track], s4Station=event.L1KBMTFSkimmed_s4Station[i_track])
            builder.integer(st_spread)
        builder.end_list()
    return builder
## add field to arr
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Calculating \"stspread\" for all tracks")
builder = ak.ArrayBuilder()
arr_st_spread(events=arr, builder=builder)
arr["L1KBMTFSkimmed_stSpread"] = builder.snapshot()

### calculate track pt from curvature hwK for arr
## for single track
@nb.jit
def track_pt(hwK):
    hwK = hwK - 9.0
    abs_hwk = abs(hwK)
    if abs_hwk > 2047:
        abs_hwk = 2047
    #abs_hwk = abs_hwk * 1.25 / (1 << 13)
    abs_hwk = abs_hwk * 1.25 / 2**13
    abs_hwk = 0.8569 * abs_hwk / (1.0 + 0.1144 * abs_hwk)
    pt = 0
    if abs_hwk != 0:
        pt = 2.0 / abs_hwk
    if pt > 2000:
        pt = 2000
    if pt < 8:
        pt = 0
    pt = pt / 2.0
    return pt
## generate ak arr
@nb.jit
def arr_pt_from_hwk(events, builder):
    n_events = len(events)
    for i_event in range(n_events):
        builder.begin_list()
        event = events[i_event]
        n_tracks = len(event.L1KBMTFSkimmed_nStub)
        for i_track in range(n_tracks):
            pt = track_pt(hwK=event.L1KBMTFSkimmed_hwK[i_track])
            builder.real(pt)
        builder.end_list()
    return builder
## add field to arr
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Calculating \"ptoffline\" for all tracks")
builder = ak.ArrayBuilder()
arr_pt_from_hwk(events=arr, builder=builder)
arr["L1KBMTFSkimmed_ptOffline"] = builder.snapshot()

### create track 4-vectors for arr
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Creating \"fourVec\" for all tracks and l1 muons")
arr["L1KBMTFSkimmed_fourVec"] = ak.zip(
    {
        "pt": arr.L1KBMTFSkimmed_ptOffline,
        "eta": arr.L1KBMTFSkimmed_eta,
        "phi": arr.L1KBMTFSkimmed_phi,
        "m": analysis_params.muon_mass,
    },
    with_name="Momentum4D",
)
arr["SkimmedL1Mu_fourVec"] = ak.zip(
    {
        "pt": arr.SkimmedL1Mu_pt,
        "eta": arr.SkimmedL1Mu_eta,
        "phi": arr.SkimmedL1Mu_phi,
        "m": analysis_params.muon_mass,
    },
    with_name="Momentum4D",
)

### attempt to match l1 muon to kbmtf track for arr
## for all tracks of one event
# only select match track with l1muon if delta_r < threshold to primary track
@nb.jit
def track_find_l1muon_match(trackFourVec, l1muFourVecs):
    n_muons = len(l1muFourVecs)
    matched_i_muon = -1
    for i_muon in range(n_muons):
        if trackFourVec.deltaR(l1muFourVecs[i_muon]) < analysis_params.delta_r_max_for_track_l1mu_match:
            matched_i_muon = i_muon
            #break
    return matched_i_muon
## for ak arr
@nb.jit
def arr_find_l1muon_match(events, builder):
    n_events = len(events)
    for i_event in range(n_events):
        builder.begin_list()
        event = events[i_event]
        n_tracks = len(event.L1KBMTFSkimmed_fourVec)
        for i_track in range(n_tracks):
            matched_i_muon = track_find_l1muon_match(trackFourVec=event.L1KBMTFSkimmed_fourVec[i_track], l1muFourVecs=event.SkimmedL1Mu_fourVec)
            builder.integer(matched_i_muon)
        builder.end_list()
    return builder
## add field to arr
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Matching tracks and l1 muons")
builder = ak.ArrayBuilder()
builder = arr_find_l1muon_match(events=arr, builder=builder)
arr["L1KBMTFSkimmed_l1muMatchedIdx"] = builder.snapshot()

### add boolean field whether there was a l1 muon match
arr["L1KBMTFSkimmed_isL1muMatched"] = ak.where(arr.L1KBMTFSkimmed_l1muMatchedIdx > -1, True, False)

### select only primary and secondary track
# track selection order from collection:
# - largest bxspread,
# - if same, then largest nstub,
# - if same, then largest pt
# only select secondary track if delta_r > threshold to primary track
## for all tracks of one event
@nb.jit
def event_sel_tracks(nStubs, bxSpreads, fourVecs):
    n_tracks = len(nStubs)
    pts = fourVecs["pt"]
    sel_i_prim_track = -1
    sel_i_sec_track = -1
    if n_tracks == 1:
        sel_i_prim_track = 0
    elif n_tracks > 1:
        sel_i_prim_track = 0
        # select prim track
        for i_track in range(n_tracks):
            if (bxSpreads[i_track] > bxSpreads[sel_i_prim_track]) or ((bxSpreads[i_track] == bxSpreads[sel_i_prim_track]) and (nStubs[i_track] > nStubs[sel_i_prim_track])) or ((bxSpreads[i_track] == bxSpreads[sel_i_prim_track]) and (nStubs[i_track] == nStubs[sel_i_prim_track]) and (pts[i_track] > pts[sel_i_prim_track])):
                sel_i_prim_track = i_track
        # select sec track
        for i_track in range(n_tracks):
            if i_track == sel_i_prim_track:
                continue
            elif fourVecs[i_track].deltaR(fourVecs[sel_i_prim_track]) <= analysis_params.delta_r_min_distance_between_tracks:
                continue
            if sel_i_sec_track == -1:
                sel_i_sec_track = i_track
            elif (bxSpreads[i_track] > bxSpreads[sel_i_sec_track]) or ((bxSpreads[i_track] == bxSpreads[sel_i_sec_track]) and (nStubs[i_track] > nStubs[sel_i_sec_track])) or ((bxSpreads[i_track] == bxSpreads[sel_i_sec_track]) and (nStubs[i_track] == nStubs[sel_i_sec_track]) and (pts[i_track] > pts[sel_i_sec_track])):
                sel_i_sec_track = i_track
    return sel_i_prim_track, sel_i_sec_track
## for ak arr
@nb.jit
def arr_sel_tracks(events):
    n_events = len(events)
    arr_prim_selection = np.zeros(n_events, dtype=np.int8)
    arr_sec_selection = np.zeros(n_events, dtype=np.int8)
    for i_event in range(n_events):
        event = events[i_event]
        sel_i_prim_track, sel_i_sec_track = event_sel_tracks(nStubs=event.L1KBMTFSkimmed_nStub, bxSpreads=event.L1KBMTFSkimmed_bxSpread, fourVecs=event.L1KBMTFSkimmed_fourVec)
        arr_prim_selection[i_event] = sel_i_prim_track
        arr_sec_selection[i_event] = sel_i_sec_track
    return arr_prim_selection, arr_sec_selection
### obtain indexlist of selected primary and secondary tracks from each event in arr
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Selecting up to 2 tracks per event for output data")
i_arr_prim_selection, i_arr_sec_selection = arr_sel_tracks(events=arr)

### generate akindex for primary and secondary tracks to select from arr
aki_arr_prim_selection = analysis_utils.gen_akindex_from_indexlist(indexlist=i_arr_prim_selection)
aki_arr_sec_selection = analysis_utils.gen_akindex_from_indexlist(indexlist=i_arr_sec_selection)

### generate no of selected tracks for each event
n_sel_tracks = np.array((i_arr_prim_selection != -1), dtype=np.int8) + np.array((i_arr_sec_selection != -1), dtype=np.int8)

## determine arr indices of tracks to be selected
row_indices_arr = ak.local_index(arr, axis=0)

## generate new flat arr "arr_tracks" with selected prim and sec tracks info
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Preparing output data with information about the selected tracks")
arr_tracks = ak.Array({
    #--- basic info
    "treeidx":                  np.array(arr.treeidx[row_indices_arr], dtype=np.uintc),
    "arridx":                   np.array(row_indices_arr, dtype=np.uintc),
    "run":                      np.array(arr.run[row_indices_arr], dtype=np.uintc),
    "luminosityBlock":          np.array(arr.luminosityBlock[row_indices_arr], dtype=np.uintc),
    "orbitNumber":              np.array(arr.orbitNumber[row_indices_arr], dtype=np.uintc),
    "bunchCrossing":            np.array(arr.bunchCrossing[row_indices_arr], dtype=np.uintc),
    "nseltracks":               np.array(n_sel_tracks, dtype=np.short),
    #--- primary track
    "idx1":             i_arr_prim_selection,
    "nstub1":           analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_nStub, aki=aki_arr_prim_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.short),
    "bxspread1":        analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_bxSpread, aki=aki_arr_prim_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.intc),
    "stationspread1":   analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_stSpread, aki=aki_arr_prim_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.intc),
    "firstbx1":         analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_firstBx, aki=aki_arr_prim_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.intc),
    "pt1":              analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_ptOffline, aki=aki_arr_prim_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.single),
    "hwPt1":            analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_pt, aki=aki_arr_prim_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.single),
    "hwPtU1":           analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_ptUnconstrained, aki=aki_arr_prim_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.single),
    "eta1":             analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_eta, aki=aki_arr_prim_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.single),
    "phi1":             analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_phi, aki=aki_arr_prim_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.single),
    "dxy1":             analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_hwDXY, aki=aki_arr_prim_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.intc),
    "qual1":            analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_hwQual, aki=aki_arr_prim_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.short),
    "charge1":          analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_hwCharge, aki=aki_arr_prim_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.short),
    "isL1MuMatched1":   analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_isL1muMatched, aki=aki_arr_prim_selection, padlen=1, padval=False, firsts=True, to_numpy=True, numpy_dtype=np.bool),
    "l1MuMatchedIdx1":  analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_l1muMatchedIdx, aki=aki_arr_prim_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.short),
    #--- secondary track
    "idx2":             i_arr_sec_selection,
    "nstub2":           analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_nStub, aki=aki_arr_sec_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.short),
    "bxspread2":        analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_bxSpread, aki=aki_arr_sec_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.intc),
    "stationspread2":   analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_stSpread, aki=aki_arr_sec_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.intc),
    "firstbx2":         analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_firstBx, aki=aki_arr_sec_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.intc),
    "pt2":              analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_ptOffline, aki=aki_arr_sec_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.single),
    "hwPt2":            analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_pt, aki=aki_arr_sec_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.single),
    "hwPtU2":           analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_ptUnconstrained, aki=aki_arr_sec_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.single),
    "eta2":             analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_eta, aki=aki_arr_sec_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.single),
    "phi2":             analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_phi, aki=aki_arr_sec_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.single),
    "dxy2":             analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_hwDXY, aki=aki_arr_sec_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.intc),
    "qual2":            analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_hwQual, aki=aki_arr_sec_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.short),
    "charge2":          analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_hwCharge, aki=aki_arr_sec_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.short),
    "isL1MuMatched2":   analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_isL1muMatched, aki=aki_arr_sec_selection, padlen=1, padval=False, firsts=True, to_numpy=True, numpy_dtype=np.bool),
    "l1MuMatchedIdx2":  analysis_utils.apply_akindex(arr=arr.L1KBMTFSkimmed_l1muMatchedIdx, aki=aki_arr_sec_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.short),
    #--- met
    #"met_bx0"
    #"met_bxm1"
    #"met_bxm2"
    #"met_bxm3"
    #"met_bxm4"
    #"met_bxm5"
})

### generate akindex for prim and sec matched l1 muon to select from arr
aki_arr_l1mu_prim_selection = analysis_utils.gen_akindex_from_indexlist(indexlist=np.array(arr_tracks.l1MuMatchedIdx1))
aki_arr_l1mu_sec_selection = analysis_utils.gen_akindex_from_indexlist(indexlist=np.array(arr_tracks.l1MuMatchedIdx2))
## add matched prim and sec l1 muon info to flat arr "arr_tracks"
# prim matched l1 muon
arr_tracks["l1MuHwPt1"] = analysis_utils.apply_akindex(arr=arr.SkimmedL1Mu_pt, aki=aki_arr_l1mu_prim_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.single)
arr_tracks["l1MuHwPtU1"] = analysis_utils.apply_akindex(arr=arr.SkimmedL1Mu_ptUnconstrained, aki=aki_arr_l1mu_prim_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.single)
arr_tracks["l1MuEta1"] = analysis_utils.apply_akindex(arr=arr.SkimmedL1Mu_eta, aki=aki_arr_l1mu_prim_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.single)
arr_tracks["l1MuPhi1"] = analysis_utils.apply_akindex(arr=arr.SkimmedL1Mu_phi, aki=aki_arr_l1mu_prim_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.single)
arr_tracks["l1MuDxy1"] = analysis_utils.apply_akindex(arr=arr.SkimmedL1Mu_hwDXY, aki=aki_arr_l1mu_prim_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.intc)
arr_tracks["l1MuQual1"] = analysis_utils.apply_akindex(arr=arr.SkimmedL1Mu_hwQual, aki=aki_arr_l1mu_prim_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.intc)
arr_tracks["l1MuCharge1"] = analysis_utils.apply_akindex(arr=arr.SkimmedL1Mu_hwCharge, aki=aki_arr_l1mu_prim_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.intc)
# sec matched l1 muon
arr_tracks["l1MuHwPt2"] = analysis_utils.apply_akindex(arr=arr.SkimmedL1Mu_pt, aki=aki_arr_l1mu_sec_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.single)
arr_tracks["l1MuHwPtU2"] = analysis_utils.apply_akindex(arr=arr.SkimmedL1Mu_ptUnconstrained, aki=aki_arr_l1mu_sec_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.single)
arr_tracks["l1MuEta2"] = analysis_utils.apply_akindex(arr=arr.SkimmedL1Mu_eta, aki=aki_arr_l1mu_sec_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.single)
arr_tracks["l1MuPhi2"] = analysis_utils.apply_akindex(arr=arr.SkimmedL1Mu_phi, aki=aki_arr_l1mu_sec_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.single)
arr_tracks["l1MuDxy2"] = analysis_utils.apply_akindex(arr=arr.SkimmedL1Mu_hwDXY, aki=aki_arr_l1mu_sec_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.intc)
arr_tracks["l1MuQual2"] = analysis_utils.apply_akindex(arr=arr.SkimmedL1Mu_hwQual, aki=aki_arr_l1mu_sec_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.intc)
arr_tracks["l1MuCharge2"] = analysis_utils.apply_akindex(arr=arr.SkimmedL1Mu_hwCharge, aki=aki_arr_l1mu_sec_selection, padlen=1, padval=-1, firsts=True, to_numpy=True, numpy_dtype=np.intc)

### prepare map of colliding bunches
run_to_lhcscheme = analysis_params.nb_run_to_lhcscheme
lhcscheme_to_filledbx = analysis_params.nb_lhcscheme_to_filledbx

### determine whether current event is in colliding bunch
# take as reference bx not the event bx, but the firstbx1
## for single event
@nb.jit
def event_check_colliding(run, bx, run_to_lhcscheme, lhcscheme_to_filledbx):
    lhcscheme = run_to_lhcscheme[run]
    filledbx_list = lhcscheme_to_filledbx[lhcscheme]
    is_colliding = False
    if bx in filledbx_list:
        is_colliding = True
    return is_colliding
## for ak arr
@nb.jit
def arr_check_colliding(events, run_to_lhcscheme, lhcscheme_to_filledbx):
    n_events = len(events)
    arr_is_colliding = np.zeros(n_events, dtype=np.bool_)
    for i_event in range(n_events):
        event = events[i_event]
        is_colliding = event_check_colliding(run=event.run, bx=event.firstbx1, run_to_lhcscheme=run_to_lhcscheme, lhcscheme_to_filledbx=lhcscheme_to_filledbx)
        arr_is_colliding[i_event] = is_colliding
    return arr_is_colliding
### add boolean field if is colliding event
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Calculating \"is_colliding\" for output data")
arr_tracks["is_colliding"] = arr_check_colliding(events=arr_tracks, run_to_lhcscheme=run_to_lhcscheme, lhcscheme_to_filledbx=lhcscheme_to_filledbx)

### determine whether current event had colliding bunch within last collisions
# take as reference bx not the event bx, but the firstbx1
# mark as "earlier colliding" if [bx-bx_interval , bx] was colliding bunch
# mask as "earlier colliding", if is currently colliding
## for single event
@nb.jit
def event_check_earlier_colliding(run, bx, bx_interval, is_colliding, run_to_lhcscheme, lhcscheme_to_filledbx):
    lhcscheme = run_to_lhcscheme[run]
    filledbx_list = lhcscheme_to_filledbx[lhcscheme]
    is_earlier_colliding = False
    if is_colliding == True: # if colliding, also set earlier colliding
        is_earlier_colliding = True
    else:
        for bx_check in range(bx-bx_interval, bx+1): # include current bx, i.e. check [bx-1-bx_interval , bx]
            if bx_check in filledbx_list:
                is_earlier_colliding = True
    return is_earlier_colliding
## for ak arr
@nb.jit
def arr_check_earlier_colliding(events, bx_interval, run_to_lhcscheme, lhcscheme_to_filledbx):
    n_events = len(events)
    arr_is_earlier_colliding = np.zeros(n_events, dtype=np.bool_)
    for i_event in range(n_events):
        event = events[i_event]
        is_earlier_colliding = event_check_earlier_colliding(run=event.run, bx=event.firstbx1, bx_interval=bx_interval, is_colliding=event.is_colliding, run_to_lhcscheme=run_to_lhcscheme, lhcscheme_to_filledbx=lhcscheme_to_filledbx)
        arr_is_earlier_colliding[i_event] = is_earlier_colliding
    return arr_is_earlier_colliding
### add boolean field if is earlier colliding event
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Calculating \"is_earlier_colliding\" for output data")
arr_tracks["is_earlier_colliding"] = arr_check_earlier_colliding(events=arr_tracks, bx_interval=analysis_params.bx_interval_earlier_colliding, run_to_lhcscheme=run_to_lhcscheme, lhcscheme_to_filledbx=lhcscheme_to_filledbx)



### store no of events before all cuts
selection_n_initial = len(arr_tracks)
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Output data has \"{selection_n_initial}\" events before all cuts")

### select events with at least one kbmtf track
selection_info = f"(nseltracks > 0)"
selection_n_before = len(arr_tracks)
#--------------
arr_mask = (arr_tracks.nseltracks > 0)
#--------------
arr_tracks = arr_tracks[arr_mask]
selection_n_after = len(arr_tracks)
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Performing output data cut \"{selection_info}\". Cut flow: \"{selection_n_after} / {selection_n_before} = {(selection_n_after/selection_n_before if selection_n_before > 0 else 0)*100:.3f} %\". Total cut flow: \"{selection_n_after} / {selection_n_initial} = {(selection_n_after/selection_n_initial if selection_n_initial > 0 else 0)*100:.3f} %\"")

### select events with at >= 1 track over more than one bx
selection_info = f"(bxspread1 > 0) | (bxspread2 > 0)"
selection_n_before = len(arr_tracks)
#--------------
arr_mask = (arr_tracks.bxspread1 > 0) | (arr_tracks.bxspread2 > 0)
#--------------
arr_tracks = arr_tracks[arr_mask]
selection_n_after = len(arr_tracks)
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Performing output data cut \"{selection_info}\". Cut flow: \"{selection_n_after} / {selection_n_before} = {(selection_n_after/selection_n_before if selection_n_before > 0 else 0)*100:.3f} %\". Total cut flow: \"{selection_n_after} / {selection_n_initial} = {(selection_n_after/selection_n_initial if selection_n_initial > 0 else 0)*100:.3f} %\"")

# ### select events with two tracks
# selection_info = f"(nseltracks == 2)"
# selection_n_before = len(arr_tracks)
# #--------------
# arr_mask = (arr_tracks.nseltracks == 2)
# #--------------
# arr_tracks = arr_tracks[arr_mask]
# selection_n_after = len(arr_tracks)
# console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Performing output data cut \"{selection_info}\". Cut flow: \"{selection_n_after} / {selection_n_before} = {(selection_n_after/selection_n_before if selection_n_before > 0 else 0)*100:.3f} %\". Total cut flow: \"{selection_n_after} / {selection_n_initial} = {(selection_n_after/selection_n_initial if selection_n_initial > 0 else 0)*100:.3f} %\"")

# ### select events with matched l1mu
# selection_info = f"(isL1MuMatched1 == True) | (isL1MuMatched2 == True)"
# selection_n_before = len(arr_tracks)
# #--------------
# arr_mask = (arr_tracks.isL1MuMatched1 == True) | (arr_tracks.isL1MuMatched2 == True)
# #--------------
# arr_tracks = arr_tracks[arr_mask]
# selection_n_after = len(arr_tracks)
# console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Performing output data cut \"{selection_info}\". Cut flow: \"{selection_n_after} / {selection_n_before} = {(selection_n_after/selection_n_before if selection_n_before > 0 else 0)*100:.3f} %\". Total cut flow: \"{selection_n_after} / {selection_n_initial} = {(selection_n_after/selection_n_initial if selection_n_initial > 0 else 0)*100:.3f} %\"")

### store no of events before all cuts
selection_n_final = len(arr_tracks)
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Output data has \"{selection_n_final}\" events after all cuts. Total cut flow: \"{selection_n_final} / {selection_n_initial} = {(selection_n_final/selection_n_initial if selection_n_initial > 0 else 0)*100:.3f} %\"")



# ### print some entries of the processed arr
# n_to_print = 15
# ## general
# list_of_dict_per_row = []
# n_entries = len(arr_tracks)
# for i in range(0,min(n_entries,n_to_print)):
#     row_dict = {}
#     for rk in [
#         "treeidx", "arridx",
#         "run", "orbitNumber", "bunchCrossing",
#         "is_colliding", "is_earlier_colliding",
#         ]:
#         for k,v in arr_tracks[i].tolist().items():
#             if rk == k:
#                 row_dict[k] = v
#     list_of_dict_per_row.append(row_dict)
# print(tabulate(list_of_dict_per_row, headers="keys", tablefmt="grid", showindex=True))
# ## for first track
# list_of_dict_per_row = []
# n_entries = len(arr_tracks)
# for i in range(0,min(n_entries,n_to_print)):
#     row_dict = {}
#     for rk in [
#         "idx1",
#         "firstbx1",
#         #"bxspread1", "nstub1",
#         "pt1", "hwPt1", "hwPtU1",
#         "isL1MuMatched1", "l1MuMatchedIdx1", "l1MuHwPt1", "l1MuHwPtU1",
#         ]:
#         for k,v in arr_tracks[i].tolist().items():
#             if rk == k:
#                 row_dict[k] = v
#     list_of_dict_per_row.append(row_dict)
# print(tabulate(list_of_dict_per_row, headers="keys", tablefmt="grid", showindex=True))
# ## for second track
# list_of_dict_per_row = []
# n_entries = len(arr_tracks)
# for i in range(0,min(n_entries,n_to_print)):
#     row_dict = {}
#     for rk in [
#         "idx2",
#         "firstbx2",
#         #"bxspread2", "nstub2",
#         "pt2", "hwPt2", "hwPtU2",
#         "isL1MuMatched2", "l1MuMatchedIdx2", "l1MuHwPt2", "l1MuHwPtU2",
#         ]:
#         for k,v in arr_tracks[i].tolist().items():
#             if rk == k:
#                 row_dict[k] = v
#     list_of_dict_per_row.append(row_dict)
# print(tabulate(list_of_dict_per_row, headers="keys", tablefmt="grid", showindex=True))


### overview of output array
# as it should be / as it was generated by FinalSelection_SlowData.py:
"""
bunchCrossing UInt_t
bxspread1 int
bxspread2 int
charge1 short
charge2 short
dxy1 short
dxy2 short
eta1 float
eta2 float
firstbx1 int
firstbx2 int
hwPt1 float
hwPt2 float
hwPtU1 float
hwPtU2 float
idx1 int
idx2 int
isL1MuMatched1 bool
isL1MuMatched2 bool
is_colliding bool
is_earlier_colliding bool
l1MuCharge1 int
l1MuCharge2 int
l1MuDxy1 int
l1MuDxy2 int
l1MuEta1 float
l1MuEta2 float
l1MuHwPt1 float
l1MuHwPt2 float
l1MuHwPtU1 float
l1MuHwPtU2 float
l1MuMatchedIdx1 int
l1MuMatchedIdx2 int
l1MuPhi1 float
l1MuPhi2 float
l1MuQual1 int
l1MuQual2 int
luminosityBlock UInt_t
met_bx0 float
met_bxm1 float
met_bxm2 float
met_bxm3 float
met_bxm4 float
met_bxm5 float
nL1KBMTFSkimmed Int_t
nSkimmedL1Mu Int_t
nstub1 short
nstub2 short
orbitNumber UInt_t
phi1 float
phi2 float
pt1 float
pt2 float
qual1 short
qual2 short
run UInt_t
stationspread1 int
stationspread2 int
"""

### store output as root ttree
n_arr = len(arr_tracks)
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Attempting to write \"{n_arr}\" events into output ROOT file \"{outfile_path}\"")
# prepare output file
outfile = uproot.recreate(outfile_path)
# write ttree
outfile.mktree("Events", arr_tracks)
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Done writing output ROOT file")

#****************************
#############################

stop_time = time.time()
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The execution took \"{stop_time - start_time} seconds\"")
console_utils.print_console_footer()
