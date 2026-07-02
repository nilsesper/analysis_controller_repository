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

from analysis_controller.src import path_utils
from analysis_controller.src import cosmetic_utils
from analysis_controller.src import file_utils
from analysis_controller.src import console_utils

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_PATH, _ANALYSIS_CONTROLLER_REPO_PATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)
cosmetic_utils.print_console_header(analysis_controller_filepath=_ANALYSIS_CONTROLLER_RELATIVE_FILEPATH)

start_time = time.time()
cosmetic_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_RELATIVE_FILEPATH}", string=f"Starting execution at time.time() value of {start_time} seconds")

vector.register_awkward()

#############################
#****************************
### MAIN PART

### import root file
#rootfile_path = os.path.join(_ANALYSIS_CONTROLLER_PATH, "dev", "rekbmtf_example_output.root")
rootfile_path = "~/promotion/test_analysis_hscp_l1/_localtest/1_reKBMTF/output.root"
cosmetic_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_RELATIVE_FILEPATH}", string=f"Opening ROOT file from \"{rootfile_path}\"")
rootfile = uproot.open(rootfile_path)

### extract "Events" root tree
roottree = rootfile["Events"]
roottree_branches = roottree.keys()
cosmetic_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_RELATIVE_FILEPATH}", string=f"ROOT tree \"Events\" contains branches {roottree_branches}")

### convert root tree to awkward array
arr = roottree.arrays(roottree_branches)
arr = ak.with_name(arr, name="Events")
cosmetic_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_RELATIVE_FILEPATH}", string=f"Converting ROOT tree \"Events\" to awkward array")

### add initial index to arr
row_indices = ak.local_index(arr, axis=0)
arr["treeidx"] = row_indices
n_entries = len(row_indices)
cosmetic_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_RELATIVE_FILEPATH}", string=f"The imported dataset has {n_entries} events")

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

### select events with at least one kbmtf track
selection_info = f"(nL1KBMTFSkimmed > 0)"
selection_n_before = len(arr)
#--------------
arr_mask = (arr.nL1KBMTFSkimmed > 0)
#--------------
arr = arr[arr_mask]
selection_n_after = len(arr)
cosmetic_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_RELATIVE_FILEPATH}", string=f"Performing selection step \"{selection_info}\". Cut flow: {selection_n_after} / {selection_n_before} = {(selection_n_after/selection_n_before if selection_n_before > 0 else 0)*100:.3f}%")

#class EventRecord(ak.Record):
#    def show_info(self):
#        #print(f"++++++++++++++++++++++")
#        #print(f"nL1KBMTFSkimmed:      {self.nL1KBMTFSkimmed},")
#        #print(f"L1KBMTFSkimmed_nStub: {self.L1KBMTFSkimmed_nStub},")
#        #print(f"L1KBMTFSkimmed_s1Bx:  {self.L1KBMTFSkimmed_s1Bx},")
#        #print(f"L1KBMTFSkimmed_s2Bx:  {self.L1KBMTFSkimmed_s2Bx},")
#        #print(f"L1KBMTFSkimmed_s3Bx:  {self.L1KBMTFSkimmed_s3Bx},")
#        #print(f"L1KBMTFSkimmed_s4Bx:  {self.L1KBMTFSkimmed_s4Bx},")
#        print(f"arr_min_bx():         {self.L1KBMTFSkimmed_firstBx},")
#        print(f"arr_bx_spread():      {self.L1KBMTFSkimmed_bxSpread},")
#        #print(f"L1KBMTFSkimmed_s1Bx:  {self.L1KBMTFSkimmed_s1Station},")
#        #print(f"L1KBMTFSkimmed_s2Bx:  {self.L1KBMTFSkimmed_s2Station},")
#        #print(f"L1KBMTFSkimmed_s3Bx:  {self.L1KBMTFSkimmed_s3Station},")
#        #print(f"L1KBMTFSkimmed_s4Bx:  {self.L1KBMTFSkimmed_s4Station},")
#        print(f"arr_st_spread():      {self.L1KBMTFSkimmed_stSpread},")
#        print(f"arr_pt_from_hwk():    {self.L1KBMTFSkimmed_pt},")
#        #print(f"++++++++++++++++++++++")
#ak.behavior.update({"Events": EventRecord})

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
builder = ak.ArrayBuilder()
arr_pt_from_hwk(events=arr, builder=builder)
arr["L1KBMTFSkimmed_pt"] = builder.snapshot()

### create track 4-vectors for arr
muon_mass = 0.10566 # PDG value in GeV
arr["L1KBMTFSkimmed_fourVec"] = ak.zip(
    {
        "pt": arr.L1KBMTFSkimmed_pt,
        "eta": arr.L1KBMTFSkimmed_eta,
        "phi": arr.L1KBMTFSkimmed_phi,
        "m": muon_mass,
    },
    with_name="Momentum4D",
)

### select only primary and secondary track
# track selection order from collection:
# - largest bxspread,
# - if same, then largest nstub,
# - if same, then largest pt
# only select secondary track if delta_r > 0.1 to primary track
### for all tracks of one event
delta_r_min = 0.1
@nb.jit
def sel_tracks_from_event(nStubs, bxSpreads, fourVecs):
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
            elif fourVecs[i_track].deltaR(fourVecs[sel_i_prim_track]) <= delta_r_min:
                continue
            if sel_i_sec_track == -1:
                sel_i_sec_track = i_track
            elif (bxSpreads[i_track] > bxSpreads[sel_i_sec_track]) or ((bxSpreads[i_track] == bxSpreads[sel_i_sec_track]) and (nStubs[i_track] > nStubs[sel_i_sec_track])) or ((bxSpreads[i_track] == bxSpreads[sel_i_sec_track]) and (nStubs[i_track] == nStubs[sel_i_sec_track]) and (pts[i_track] > pts[sel_i_sec_track])):
                sel_i_sec_track = i_track
    return sel_i_prim_track, sel_i_sec_track
## for ak arr
@nb.jit
def sel_tracks_from_arr(events):
    n_events = len(events)
    arr_prim_selection = np.zeros(n_events, dtype=np.int8)
    arr_sec_selection = np.zeros(n_events, dtype=np.int8)
    for i_event in range(n_events):
        event = events[i_event]
        sel_i_prim_track, sel_i_sec_track = sel_tracks_from_event(nStubs=event.L1KBMTFSkimmed_nStub, bxSpreads=event.L1KBMTFSkimmed_bxSpread, fourVecs=event.L1KBMTFSkimmed_fourVec)
        arr_prim_selection[i_event] = sel_i_prim_track
        arr_sec_selection[i_event] = sel_i_sec_track
    return arr_prim_selection, arr_sec_selection
### for ak arr
#delta_r_min = 0.1
#@nb.jit
#def sel_tracks_from_arr(events):
#    n_events = len(events)
#    arr_prim_selection = np.zeros(n_events, dtype=np.int8)
#    arr_sec_selection = np.zeros(n_events, dtype=np.int8)
#    for i_event in range(n_events):
#        event = events[i_event]
#        n_tracks = len(event.L1KBMTFSkimmed_nStub)
#        sel_i_prim_track = -1
#        sel_i_sec_track = -1
#        if n_tracks == 1:
#            sel_i_prim_track = 0
#        elif n_tracks > 1:
#            best_bxSpread_prim_track = 0
#            best_nStub_prim_track = 0
#            best_pt_prim_track = 0
#            for i_track in range(n_tracks):
#                if (event.L1KBMTFSkimmed_bxSpread[i_track] > best_bxSpread_prim_track) or ((event.L1KBMTFSkimmed_bxSpread[i_track] == best_bxSpread_prim_track) and (event.L1KBMTFSkimmed_nStub[i_track] > best_nStub_prim_track)) or ((event.L1KBMTFSkimmed_bxSpread[i_track] == best_bxSpread_prim_track) and (event.L1KBMTFSkimmed_nStub[i_track] == best_nStub_prim_track) and (event.L1KBMTFSkimmed_pt[i_track] > best_pt_prim_track)):
#                    sel_i_prim_track = i_track
#                    best_bxSpread_prim_track = event.L1KBMTFSkimmed_bxSpread[sel_i_prim_track]
#                    best_nStub_prim_track = event.L1KBMTFSkimmed_nStub[sel_i_prim_track]
#                    best_pt_prim_track = event.L1KBMTFSkimmed_pt[sel_i_prim_track]
#            if sel_i_prim_track != -1:
#                best_bxSpread_sec_track = 0
#                best_nStub_sec_track = 0
#                best_pt_sec_track = 0
#                for i_track in range(n_tracks):
#                    if i_track == sel_i_prim_track:
#                        continue
#                    elif event.L1KBMTFSkimmed_fourVec[i_track].deltaR(event.L1KBMTFSkimmed_fourVec[sel_i_prim_track]) <= delta_r_min:
#                        continue
#                    elif (event.L1KBMTFSkimmed_bxSpread[i_track] > best_bxSpread_sec_track) or ((event.L1KBMTFSkimmed_bxSpread[i_track] == best_bxSpread_sec_track) and (event.L1KBMTFSkimmed_nStub[i_track] > best_nStub_sec_track)) or ((event.L1KBMTFSkimmed_bxSpread[i_track] == best_bxSpread_sec_track) and (event.L1KBMTFSkimmed_nStub[i_track] == best_nStub_sec_track) and (event.L1KBMTFSkimmed_pt[i_track] > best_pt_sec_track)):
#                        sel_i_sec_track = i_track
#                        best_bxSpread_sec_track = event.L1KBMTFSkimmed_bxSpread[sel_i_sec_track]
#                        best_nStub_sec_track = event.L1KBMTFSkimmed_nStub[sel_i_sec_track]
#                        best_pt_sec_track = event.L1KBMTFSkimmed_pt[sel_i_sec_track]
#        arr_prim_selection[i_event] = sel_i_prim_track
#        arr_sec_selection[i_event] = sel_i_sec_track
#    return arr_prim_selection, arr_sec_selection
## determine arr indices of tracks to be selected
row_indices = ak.local_index(arr, axis=0)
prim_selection_indices, sec_selection_indices = sel_tracks_from_arr(events=arr)
prim_selection_indices_valid = (prim_selection_indices >= 0)
sec_selection_indices_valid = (sec_selection_indices >= 0)
n_sel_tracks = np.array(prim_selection_indices_valid, dtype=np.int8) + np.array(sec_selection_indices_valid, dtype=np.int8)

## apply selection and generate new flat arr_tracks
arr_tracks = ak.Array({
    #--- base info
    "treeidx":          arr.treeidx[row_indices],
    "run":              arr.run[row_indices],
    "luminosityBlock":  arr.luminosityBlock[row_indices],
    "orbitNumber":      arr.orbitNumber[row_indices],
    "bunchCrossing":    arr.bunchCrossing[row_indices],
    #"is_colliding"
    #"is_earlier_colliding"
    "nseltracks":       n_sel_tracks,
    #--- primary track
    "idx1":             ak.where(prim_selection_indices_valid, prim_selection_indices, -1),
    "nstub1":           ak.where(prim_selection_indices_valid, arr.L1KBMTFSkimmed_nStub[row_indices, prim_selection_indices], -1),
    "bxspread1":        ak.where(prim_selection_indices_valid, arr.L1KBMTFSkimmed_bxSpread[row_indices, prim_selection_indices], -1),
    "stationspread1":   ak.where(prim_selection_indices_valid, arr.L1KBMTFSkimmed_stSpread[row_indices, prim_selection_indices], -1),
    "firstbx1":         ak.where(prim_selection_indices_valid, arr.L1KBMTFSkimmed_firstBx[row_indices, prim_selection_indices], -1),
    "pt1":              ak.where(prim_selection_indices_valid, arr.L1KBMTFSkimmed_pt[row_indices, prim_selection_indices], -1),
    "eta1":             ak.where(prim_selection_indices_valid, arr.L1KBMTFSkimmed_eta[row_indices, prim_selection_indices], -1),
    "phi1":             ak.where(prim_selection_indices_valid, arr.L1KBMTFSkimmed_phi[row_indices, prim_selection_indices], -1),
    "dxy1":             ak.where(prim_selection_indices_valid, arr.L1KBMTFSkimmed_hwDXY[row_indices, prim_selection_indices], -1),
    "qual1":            ak.where(prim_selection_indices_valid, arr.L1KBMTFSkimmed_hwQual[row_indices, prim_selection_indices], -1),
    "charge1":          ak.where(prim_selection_indices_valid, arr.L1KBMTFSkimmed_hwCharge[row_indices, prim_selection_indices], -1),
    #"isL1MuMatched1"
    #--- secondary track
    "idx2":             ak.where(sec_selection_indices_valid, sec_selection_indices, -1),
    "nstub2":           ak.where(sec_selection_indices_valid, arr.L1KBMTFSkimmed_nStub[row_indices, sec_selection_indices], -1),
    "bxspread2":        ak.where(sec_selection_indices_valid, arr.L1KBMTFSkimmed_bxSpread[row_indices, sec_selection_indices], -1),
    "stationspread2":   ak.where(sec_selection_indices_valid, arr.L1KBMTFSkimmed_stSpread[row_indices, sec_selection_indices], -1),
    "firstbx2":         ak.where(sec_selection_indices_valid, arr.L1KBMTFSkimmed_firstBx[row_indices, sec_selection_indices], -1),
    "pt2":              ak.where(sec_selection_indices_valid, arr.L1KBMTFSkimmed_pt[row_indices, sec_selection_indices], -1),
    "eta2":             ak.where(sec_selection_indices_valid, arr.L1KBMTFSkimmed_eta[row_indices, sec_selection_indices], -1),
    "phi2":             ak.where(sec_selection_indices_valid, arr.L1KBMTFSkimmed_phi[row_indices, sec_selection_indices], -1),
    "dxy2":             ak.where(sec_selection_indices_valid, arr.L1KBMTFSkimmed_hwDXY[row_indices, sec_selection_indices], -1),
    "qual2":            ak.where(sec_selection_indices_valid, arr.L1KBMTFSkimmed_hwQual[row_indices, sec_selection_indices], -1),
    "charge2":          ak.where(sec_selection_indices_valid, arr.L1KBMTFSkimmed_hwCharge[row_indices, sec_selection_indices], -1),
    #"isL1MuMatched2"
    #--- met
    #"met_bx0"
    #"met_bxm1"
    #"met_bxm2"
    #"met_bxm3"
    #"met_bxm4"
    #"met_bxm5"
})

### select events with at least one track over more than one bx
selection_info = f"(bxspread1 > 0) | (bxspread2 > 0)"
selection_n_before = len(arr_tracks)
#--------------
arr_mask = (arr_tracks.bxspread1 > 0) | (arr_tracks.bxspread2 > 0)
#--------------
arr_tracks = arr_tracks[arr_mask]
selection_n_after = len(arr_tracks)
cosmetic_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_RELATIVE_FILEPATH}", string=f"Performing selection step \"{selection_info}\". Cut flow: {selection_n_after} / {selection_n_before} = {(selection_n_after/selection_n_before if selection_n_before > 0 else 0)*100:.3f}%")

### select events with two tracks
arr_tracks = arr_tracks[arr_tracks.idx2 != -1]

### print some entries of the processed arr
list_of_dict_per_row = []
for i in range(0,20):
    row_dict = {}
    for rk in ["idx1", "firstbx1", "bxspread1", "nstub1", "pt1", "idx2", "firstbx2", "bxspread2", "nstub2", "pt2"]:
        for k,v in arr_tracks[i].tolist().items():
            if rk == k:
                row_dict[k] = v
    list_of_dict_per_row.append(row_dict)
print(tabulate(list_of_dict_per_row, headers="keys", tablefmt="grid")) #, showindex=True

#****************************
#############################

stop_time = time.time()
cosmetic_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_RELATIVE_FILEPATH}", string=f"Finshing execution at time.time() value of {start_time} seconds")
cosmetic_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_RELATIVE_FILEPATH}", string=f"The execution took {stop_time - start_time} seconds")
cosmetic_utils.print_console_footer()
