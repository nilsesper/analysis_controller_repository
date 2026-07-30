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
infile = uproot.open(infile_path)
### extract "Events" root tree
roottree = infile["Events"]
roottree_branches = roottree.keys()
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"ROOT tree \"Events\" contains branches {roottree_branches}")
### convert root tree to awkward array
arr = roottree.arrays(roottree_branches)
arr = ak.with_name(arr, name="Events")
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"Converting ROOT tree \"Events\" to awkward array")
row_indices = ak.local_index(arr, axis=0)
n_entries = len(row_indices)
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The imported dataset has \"{n_entries:,}\" events")

#############################
### ANALYZE DATA

# mask = (arr['nseltracks'] > 0)
mask = (arr['nseltracks'] > 1)
arr = arr[mask]

i_last_track = None
last_track = None
n_found = 0

n_tracks = len(arr)
for i_track in range(n_tracks):
    if n_found > 1000: break

    track = arr[i_track]

    if i_last_track is not None:
        if (last_track['orbitNumber'] == last_track['orbitNumber']) and (track['bunchCrossing'] - last_track['bunchCrossing'] <= 5) and (track['bunchCrossing'] - last_track['bunchCrossing'] > 0):
            n_found += 1

            print(f"================")
            print(f"track_{i_last_track:04d} : run_{last_track['run']:06d} lumi_{last_track['luminosityBlock']:04d} orbit_{last_track['orbitNumber']:09d} bx_{last_track['bunchCrossing']:04d} : nstub1_{last_track['nstub1']:01d} firstbx1_{track['firstbx1']:04d} bxsp1_{last_track['bxspread1']:04d} stsp1_{last_track['stationspread1']:04d} : eta1_{last_track['eta1']:+04f} phi1_{last_track['phi1']:+04f} pt1_{last_track['pt1']:06f} : isL1MuMatched1_{last_track['isL1MuMatched1']:01d}")
            print(f"track_{i_track:04d} : run_{track['run']:06d} lumi_{track['luminosityBlock']:04d} orbit_{track['orbitNumber']:09d} bx_{track['bunchCrossing']:04d} : nstub1_{track['nstub1']:01d} firstbx1_{track['firstbx1']:04d} bxsp1_{track['bxspread1']:04d} stsp1_{track['stationspread1']:04d} : eta1_{track['eta1']:+04f} phi1_{track['phi1']:+04f} pt1_{track['pt1']:06f} : isL1MuMatched1_{track['isL1MuMatched1']:01d}")
            print(f"----------------")
            print(f"track_{i_last_track:04d} : run_{last_track['run']:06d} lumi_{last_track['luminosityBlock']:04d} orbit_{last_track['orbitNumber']:09d} bx_{last_track['bunchCrossing']:04d} : nstub2_{last_track['nstub2']:01d} firstbx2_{track['firstbx2']:04d} bxsp2_{last_track['bxspread2']:04d} stsp2_{last_track['stationspread2']:04d} : eta2_{last_track['eta2']:+04f} phi2_{last_track['phi2']:+04f} pt2_{last_track['pt2']:06f} : isL1MuMatched2_{last_track['isL1MuMatched2']:01d}")
            print(f"track_{i_track:04d} : run_{track['run']:06d} lumi_{track['luminosityBlock']:04d} orbit_{track['orbitNumber']:09d} bx_{track['bunchCrossing']:04d} : nstub2_{track['nstub2']:01d} firstbx2_{track['firstbx2']:04d} bxsp2_{track['bxspread2']:04d} stsp2_{track['stationspread2']:04d} : eta2_{track['eta2']:+04f} phi2_{track['phi2']:+04f} pt2_{track['pt2']:06f} : isL1MuMatched2_{track['isL1MuMatched2']:01d}")

    last_track = track
    i_last_track = i_track

#****************************
#############################

stop_time = time.time()
console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH}", string=f"The execution took \"{(stop_time - start_time):03f} seconds\"")
console_utils.print_console_footer()

input("Press [Enter] to exit")
