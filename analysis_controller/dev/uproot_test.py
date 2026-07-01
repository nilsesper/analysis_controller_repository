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

from analysis_controller.src import path_utils
from analysis_controller.src import cosmetic_utils
from analysis_controller.src import file_utils
from analysis_controller.src import console_utils

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_PATH, _ANALYSIS_CONTROLLER_REPO_PATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)
cosmetic_utils.print_console_header(analysis_controller_filepath=_ANALYSIS_CONTROLLER_RELATIVE_FILEPATH)

#############################
#****************************
### MAIN PART

### import root file
rootfile_path = os.path.join(_ANALYSIS_CONTROLLER_PATH, "dev", "rekbmtf_example_output.root")
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
#print(f"{arr.type.show()}")

### overview of input data array
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

### select events with at least one kbmtf track
selection_info = f"arr.nL1KBMTFSkimmed > 0"
selection_n_before = len(arr)
#--------------
arr = arr[arr.nL1KBMTFSkimmed > 0]
#--------------
selection_n_after = len(arr)
cosmetic_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_RELATIVE_FILEPATH}", string=f"Performing selection step \"{selection_info}\". Cut flow: {selection_n_after} / {selection_n_before} = {(selection_n_after/selection_n_before if selection_n_before > 0 else 0)*100:.3f}%")

class EventRecord(ak.Record):

    def show_info(self):
        print(f"++++++++++++++++++++++")
        #print(f"nL1KBMTFSkimmed:      {self.nL1KBMTFSkimmed},")
        #print(f"L1KBMTFSkimmed_nStub: {self.L1KBMTFSkimmed_nStub},")
        #print(f"L1KBMTFSkimmed_s1Bx:  {self.L1KBMTFSkimmed_s1Bx},")
        #print(f"L1KBMTFSkimmed_s2Bx:  {self.L1KBMTFSkimmed_s2Bx},")
        #print(f"L1KBMTFSkimmed_s3Bx:  {self.L1KBMTFSkimmed_s3Bx},")
        #print(f"L1KBMTFSkimmed_s4Bx:  {self.L1KBMTFSkimmed_s4Bx},")
        print(f"arr_min_bx():         {self.L1KBMTFSkimmed_firstBx},")
        print(f"arr_bx_spread():      {self.L1KBMTFSkimmed_bxSpread},")
        #print(f"L1KBMTFSkimmed_s1Bx:  {self.L1KBMTFSkimmed_s1Station},")
        #print(f"L1KBMTFSkimmed_s2Bx:  {self.L1KBMTFSkimmed_s2Station},")
        #print(f"L1KBMTFSkimmed_s3Bx:  {self.L1KBMTFSkimmed_s3Station},")
        #print(f"L1KBMTFSkimmed_s4Bx:  {self.L1KBMTFSkimmed_s4Station},")
        print(f"arr_st_spread():      {self.L1KBMTFSkimmed_stSpread},")
        print(f"arr_pt_from_hwk():    {self.L1KBMTFSkimmed_pt},")
        print(f"++++++++++++++++++++++")

ak.behavior.update({"Events": EventRecord})

### calculate min_bx for arr
@nb.jit
def arr_min_bx(events, builder):
    n_events = len(events)
    for i_event in range(n_events):
        builder.begin_list()
        n_tracks = len(events[i_event].L1KBMTFSkimmed_nStub)
        for i_track in range(n_tracks):
            track_min_bx = -1
            if events[i_event].L1KBMTFSkimmed_nStub[i_track] == 1:
                track_min_bx = min([events[i_event].L1KBMTFSkimmed_s1Bx[i_track]])
            elif events[i_event].L1KBMTFSkimmed_nStub[i_track] == 2:
                track_min_bx = min([events[i_event].L1KBMTFSkimmed_s1Bx[i_track], events[i_event].L1KBMTFSkimmed_s2Bx[i_track]])
            elif events[i_event].L1KBMTFSkimmed_nStub[i_track] == 3:
                track_min_bx = min([events[i_event].L1KBMTFSkimmed_s1Bx[i_track], events[i_event].L1KBMTFSkimmed_s2Bx[i_track], events[i_event].L1KBMTFSkimmed_s3Bx[i_track]])
            elif events[i_event].L1KBMTFSkimmed_nStub[i_track] == 4:
                track_min_bx = min([events[i_event].L1KBMTFSkimmed_s1Bx[i_track], events[i_event].L1KBMTFSkimmed_s2Bx[i_track], events[i_event].L1KBMTFSkimmed_s3Bx[i_track], events[i_event].L1KBMTFSkimmed_s4Bx[i_track]])
            builder.integer(track_min_bx)
        builder.end_list()
    return builder

builder = ak.ArrayBuilder()
arr_min_bx(events=arr, builder=builder)
arr["L1KBMTFSkimmed_firstBx"] = builder.snapshot()

### calculate bx_spread for arr
# because of inner order of kbmtf algo, the order is always outer station -> inner station
# therefore a good track coming from the interaction point has outer bx >= inner bx
@nb.jit
def arr_bx_spread(events, builder):
    n_events = len(events)
    for i_event in range(n_events):
        builder.begin_list()
        event_min_bx = events[i_event].L1KBMTFSkimmed_firstBx
        n_tracks = len(events[i_event].L1KBMTFSkimmed_nStub)
        for i_track in range(n_tracks):
            track_bx_spread = -1
            if events[i_event].L1KBMTFSkimmed_nStub[i_track] == 1:
                track_bx_spread = 1000*(events[i_event].L1KBMTFSkimmed_s1Bx[i_track] - event_min_bx[i_track])
            elif events[i_event].L1KBMTFSkimmed_nStub[i_track] == 2:
                track_bx_spread = 1000*(events[i_event].L1KBMTFSkimmed_s1Bx[i_track] - event_min_bx[i_track]) + 100*(events[i_event].L1KBMTFSkimmed_s2Bx[i_track] - event_min_bx[i_track])
            elif events[i_event].L1KBMTFSkimmed_nStub[i_track] == 3:
                track_bx_spread = 1000*(events[i_event].L1KBMTFSkimmed_s1Bx[i_track] - event_min_bx[i_track]) + 100*(events[i_event].L1KBMTFSkimmed_s2Bx[i_track] - event_min_bx[i_track]) + 10*(events[i_event].L1KBMTFSkimmed_s3Bx[i_track] - event_min_bx[i_track])
            elif events[i_event].L1KBMTFSkimmed_nStub[i_track] == 4:
                track_bx_spread = 1000*(events[i_event].L1KBMTFSkimmed_s1Bx[i_track] - event_min_bx[i_track]) + 100*(events[i_event].L1KBMTFSkimmed_s2Bx[i_track] - event_min_bx[i_track]) + 10*(events[i_event].L1KBMTFSkimmed_s3Bx[i_track] - event_min_bx[i_track]) + 1*(events[i_event].L1KBMTFSkimmed_s4Bx[i_track] - event_min_bx[i_track])
            builder.integer(track_bx_spread)
        builder.end_list()
    return builder

builder = ak.ArrayBuilder()
arr_bx_spread(events=arr, builder=builder)
arr["L1KBMTFSkimmed_bxSpread"] = builder.snapshot()

### calculate st_spread for arr
# because of inner order of kbmtf algo, the order is always outer station -> inner station
# therefore always st_spread monotnically decreasing
@nb.jit
def arr_st_spread(events, builder):
    n_events = len(events)
    for i_event in range(n_events):
        builder.begin_list()
        n_tracks = len(events[i_event].L1KBMTFSkimmed_nStub)
        for i_track in range(n_tracks):
            track_bx_spread = -1
            if events[i_event].L1KBMTFSkimmed_nStub[i_track] == 1:
                track_st_spread = 1000*(events[i_event].L1KBMTFSkimmed_s1Station[i_track])
            elif events[i_event].L1KBMTFSkimmed_nStub[i_track] == 2:
                track_st_spread = 1000*(events[i_event].L1KBMTFSkimmed_s1Station[i_track]) + 100*(events[i_event].L1KBMTFSkimmed_s2Station[i_track])
            elif events[i_event].L1KBMTFSkimmed_nStub[i_track] == 3:
                track_st_spread = 1000*(events[i_event].L1KBMTFSkimmed_s1Station[i_track]) + 100*(events[i_event].L1KBMTFSkimmed_s2Station[i_track]) + 10*(events[i_event].L1KBMTFSkimmed_s3Station[i_track])
            elif events[i_event].L1KBMTFSkimmed_nStub[i_track] == 4:
                track_st_spread = 1000*(events[i_event].L1KBMTFSkimmed_s1Station[i_track]) + 100*(events[i_event].L1KBMTFSkimmed_s2Station[i_track]) + 10*(events[i_event].L1KBMTFSkimmed_s3Station[i_track]) + 1*(events[i_event].L1KBMTFSkimmed_s4Station[i_track])
            builder.integer(track_st_spread)
        builder.end_list()
    return builder

builder = ak.ArrayBuilder()
arr_st_spread(events=arr, builder=builder)
arr["L1KBMTFSkimmed_stSpread"] = builder.snapshot()

### calculate track pt from curvature hwK for arr
@nb.jit
def arr_pt_from_hwk(events, builder):
    n_events = len(events)
    for i_event in range(n_events):
        builder.begin_list()
        n_tracks = len(events[i_event].L1KBMTFSkimmed_nStub)
        for i_track in range(n_tracks):
            track_hwk = events[i_event].L1KBMTFSkimmed_hwK[i_track]
            track_hwk = track_hwk - 9
            track_abs_hwk = abs(track_hwk)
            if track_abs_hwk > 2047:
                track_abs_hwk = 2047
            track_abs_hwk = track_abs_hwk * 1.25 / (1 << 13)
            track_abs_hwk = 0.8569 * track_abs_hwk / (1.0 + 0.1144 * track_abs_hwk)
            track_pt = 0
            if track_abs_hwk != 0:
                track_pt = 2 / track_abs_hwk
            if track_pt > 2000:
                track_pt = 2000
            if track_pt < 8:
                track_pt = 0
            track_pt = track_pt / 2
            builder.real(track_pt)
        builder.end_list()
    return builder

builder = ak.ArrayBuilder()
arr_pt_from_hwk(events=arr, builder=builder)
arr["L1KBMTFSkimmed_pt"] = builder.snapshot()

### select primary and secondary track
# track selection order from collection:
# - largest bxspread,
# - if same, then largest nstub,
# - if same, then largest pt






### make extra array for two tracks
arr2 = arr[arr.nL1KBMTFSkimmed == 2]




























### calculate bx spread for each track, from bx information of stubs
# bxspread = ABCD, integer number, where:
#   A = bx(first stub) - min(stub bxs)
#   B = bx(second stub) - min(stub bxs)
#   C = bx(third stub) - min(stub bxs), if nstub < 3: C = 0
#   D = bx(fourth stub) - min(stub bxs), if nstub < 4: D = 0
# else bxspread = -1
"""
df = df.Define(
    "bxspread1",
    "GetBxSpread(
        ncand = nL1KBMTFSkimmed,
        index = idx1,
        nstub = L1KBMTFSkimmed_nStub,
        bx1 = L1KBMTFSkimmed_s1Bx,
        bx2 = L1KBMTFSkimmed_s2Bx, 
        bx3 = L1KBMTFSkimmed_s3Bx, 
        bx4 = L1KBMTFSkimmed_s4Bx
    )"
)

int GetBxSpread(
    int ncand,
    int index,
    ROOT::VecOps::RVec<Short_t> &nstub,
    ROOT::VecOps::RVec<Short_t> &bx1, 
    ROOT::VecOps::RVec<Short_t> &bx2, 
    ROOT::VecOps::RVec<Short_t> &bx3, 
    ROOT::VecOps::RVec<Short_t> &bx4
    )
{
    int spread = 0;
    if (index<ncand)
    {
        int minbx = bx1[index];
        if (bx2[index]<minbx)
            minbx = bx2[index];
        if (nstub[index]>2 and bx3[index]<minbx)
            minbx = bx3[index];
        if (nstub[index]>3 and bx4[index]<minbx)
            minbx = bx4[index];
        
        spread = spread + 1000*(bx1[index]-minbx);
        spread = spread + 100*(bx2[index]-minbx);
        if (nstub[index]>2)
            spread = spread + 10*(bx3[index]-minbx);
        if (nstub[index]>3)
            spread = spread + 1*(bx4[index]-minbx);
    }
    else
        spread=-1;
    return spread;
}
"""

#arr["L1KBMTFSkimmed_sBx"] = ak.concatenate(
#    arrays=[
#        arr.L1KBMTFSkimmed_s1Bx[arr.L1KBMTFSkimmed_nStub > 0],
#        arr.L1KBMTFSkimmed_s2Bx[arr.L1KBMTFSkimmed_nStub > 1],
#        arr.L1KBMTFSkimmed_s3Bx[arr.L1KBMTFSkimmed_nStub > 2],
#        arr.L1KBMTFSkimmed_s4Bx[arr.L1KBMTFSkimmed_nStub > 3],
#    ],
#    axis=1
#)
#arr["L1KBMTFSkimmed_sMinBx"] = ak.min(arr.L1KBMTFSkimmed_sBx, axis=1)
#arr["L1KBMTFSkimmed_s1DeltaMinBx"] = arr.L1KBMTFSkimmed_s1Bx[arr.L1KBMTFSkimmed_nStub > 0] - arr.L1KBMTFSkimmed_sMinBx
#arr["L1KBMTFSkimmed_s2DeltaMinBx"] = arr.L1KBMTFSkimmed_s2Bx[arr.L1KBMTFSkimmed_nStub > 1] - arr.L1KBMTFSkimmed_sMinBx
#arr["L1KBMTFSkimmed_s3DeltaMinBx"] = arr.L1KBMTFSkimmed_s3Bx[arr.L1KBMTFSkimmed_nStub > 2] - arr.L1KBMTFSkimmed_sMinBx
#arr["L1KBMTFSkimmed_s4DeltaMinBx"] = arr.L1KBMTFSkimmed_s4Bx[arr.L1KBMTFSkimmed_nStub > 3] - arr.L1KBMTFSkimmed_sMinBx

### replace undefined stub bx information
# all elements with mask=True become None
#arr["L1KBMTFSkimmed_s1Bx"] = ak.where(arr.L1KBMTFSkimmed_nStub < 1, -1, arr.L1KBMTFSkimmed_s1Bx)
#arr["L1KBMTFSkimmed_s2Bx"] = ak.where(arr.L1KBMTFSkimmed_nStub < 2, -1, arr.L1KBMTFSkimmed_s2Bx)
#arr["L1KBMTFSkimmed_s3Bx"] = ak.where(arr.L1KBMTFSkimmed_nStub < 3, -1, arr.L1KBMTFSkimmed_s3Bx)
#arr["L1KBMTFSkimmed_s4Bx"] = ak.where(arr.L1KBMTFSkimmed_nStub < 4, -1, arr.L1KBMTFSkimmed_s4Bx)

### calculate station spread for each track, from station information of stubs
# stationspread = ABCD, integer number, where:
#   A = station(first stub)
#   B = station(second stub)
#   C = station(third stub), if nstub < 3: C = 0
#   D = station(fourth stub), if nstub < 4: D = 0
# else stationspread = -1
"""
df = df.Define(
    "stationspread1",
    "GetStationSpread(
        ncand = nL1KBMTFSkimmed,
        index = idx1, 
        nstub = L1KBMTFSkimmed_nStub, 
        st1 = L1KBMTFSkimmed_s1Station, 
        st2 = L1KBMTFSkimmed_s2Station, 
        st3 = L1KBMTFSkimmed_s3Station, 
        st4 = L1KBMTFSkimmed_s4Station
    )"
)

int GetStationSpread(
    int ncand, 
    int index, 
    ROOT::VecOps::RVec<Short_t> &nstub, 
    ROOT::VecOps::RVec<Short_t> &st1, 
    ROOT::VecOps::RVec<Short_t> &st2, 
    ROOT::VecOps::RVec<Short_t> &st3, 
    ROOT::VecOps::RVec<Short_t> &st4
    )
{
    int spread = 0;
    if (index<ncand)
    {
        spread = spread + 1000*st1[index];
        spread = spread + 100*st2[index];
        if (nstub[index]>2)
            spread = spread + 10*st3[index];
        if (nstub[index]>3)
            spread = spread + 1*st4[index];
    }
    else
        spread=-1;
    return spread;
}
"""

### calculate track pt for each track, from kbmtf curvature value
"""
float Get_newpt(int oldK){
  float K = oldK-9;
  if (K==0) K=1;
  float lsb = 1.25 / float(1 << 13);
  float FK = abs(K);

  if (FK > 2047)
    FK = 2047.;

  FK = FK * lsb;

  //step 1 -material and B-field
  FK = .8569 * FK / (1.0 + 0.1144 * FK);

  float pt = 0;
  if (FK != 0)
    pt = float(2.0 / FK);

  if (pt > 2000)
    pt = 2000;

  if (pt < 8)
    pt = 8;

  return pt/2;
}
"""

### select primary and secondary track
# track selection order from collection:
# - largest bxspread,
# - if same, then largest nstub,
# - if same, then largest pt
"""
df = df.Define(
    "idx1",
    "GetIndex(
        rank = 1, 
        ncand = nL1KBMTFSkimmed, 
        LepCand_pt = L1KBMTFSkimmed_pt, 
        LepCand_eta = L1KBMTFSkimmed_eta, 
        LepCand_phi = L1KBMTFSkimmed_phi, 
        nstub = L1KBMTFSkimmed_nStub, 
        bx1 = L1KBMTFSkimmed_s1Bx, 
        bx2 = L1KBMTFSkimmed_s2Bx, 
        bx3 = L1KBMTFSkimmed_s3Bx, 
        bx4 = L1KBMTFSkimmed_s4Bx, 
        LepCand_hwK = L1KBMTFSkimmed_hwK
    )"
)

int GetIndex(
    int rank,
    int ncand,
    ROOT::VecOps::RVec<Float_t> &LepCand_pt,
    ROOT::VecOps::RVec<Float_t> &LepCand_eta,
    ROOT::VecOps::RVec<Float_t> &LepCand_phi,
    ROOT::VecOps::RVec<Short_t> &nstub,
    ROOT::VecOps::RVec<Short_t> &bx1,
    ROOT::VecOps::RVec<Short_t> &bx2,
    ROOT::VecOps::RVec<Short_t> &bx3,
    ROOT::VecOps::RVec<Short_t> &bx4,
    ROOT::VecOps::RVec<Short_t> &LepCand_hwK
    )
{

	int idxK1=99; int idxK2=99;
	int best_bxspread=0;
	int best_nstubs=0;
	float best_pt=0;

    if (ncand==1)
        idxK1=0;
    else if (ncand>1){
	    for (int k=0; k<ncand; ++k)
        {
            int tmp_bxspread=GetBxSpread(ncand, k, nstub, bx1, bx2, bx3, bx4);
            int tmp_nstubs=nstub[k];
            int tmp_pt=Get_newpt(LepCand_hwK[k]);
            if (tmp_bxspread>best_bxspread or (tmp_bxspread==best_bxspread and tmp_nstubs>best_nstubs) or (tmp_bxspread==best_bxspread and tmp_nstubs==best_nstubs and tmp_pt>best_pt)) // prefer slowest
            {
                idxK1=k;
                best_bxspread=tmp_bxspread;
                best_nstubs=tmp_nstubs;
                best_pt=tmp_pt;
            }
        }
        
        TLorentzVector my_mu1; my_mu1.SetPtEtaPhiM(Get_newpt(LepCand_hwK[idxK1]), LepCand_eta[idxK1], LepCand_phi[idxK1],0.105);
        best_bxspread=0;
        best_nstubs=0;
        best_pt=0;
        TLorentzVector tmp_mu;
        for (int k=0; k<ncand; ++k)
        {
            tmp_mu.SetPtEtaPhiM(Get_newpt(LepCand_hwK[k]), LepCand_eta[k], LepCand_phi[k],0.105);
            if (tmp_mu.DeltaR(my_mu1)>0.10)
            {
                int tmp_bxspread=GetBxSpread(ncand, k, nstub, bx1, bx2, bx3, bx4);
                int tmp_nstubs=nstub[k];
                int tmp_pt=Get_newpt(LepCand_hwK[k]);
                if (tmp_bxspread>best_bxspread or (tmp_bxspread==best_bxspread and tmp_nstubs>best_nstubs) or (tmp_bxspread==best_bxspread and tmp_nstubs==best_nstubs and tmp_pt>best_pt)) // prefer slowest
                {
                    idxK2=k;
                    best_bxspread=tmp_bxspread;
                    best_nstubs=tmp_nstubs;
                    best_pt=tmp_pt;
                }
            }
        }
	}

	if (rank==1)
        return idxK1;
    else if (rank==2)
        return idxK2;
    else
        return 0;
}
"""


#****************************
#############################

cosmetic_utils.print_console_footer()
