######################
### ANALYSIS UTILS ###
######################

############################
### IMPORTS

import os
import awkward as ak
import numpy as np
import numba as nb

from analysis_controller.src import path_utils

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_PATH, _ANALYSIS_CONTROLLER_REPO_PATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)

############################
### HELPER FUNCTIONS & CLASSES (with prefix "_")



############################
### MAIN FUNCTIONS & CLASSES

#*******************************
#*** AWKWARD ARRAY UTILITIES ***
#*******************************

### generate awkward index, to slice an ak array
# ak array to slice: structure [ [x1, x2], [x1], [], [x1], ]
# indexlist: [ index of one inner entry that should be selected, or -1 if none should/can be selected ]
# returns: ak index array [ [ index of inner entry or empty list if none should be selected ] ]
# usage: gen_idx = gen_akindex_from_indexlist(indexlist=got_idx)
@nb.jit
def _build_gen_akindex_from_indexlist(indexlist, builder):
    n_indices = len(indexlist)
    for i_index in range(n_indices):
        builder.begin_list()
        if indexlist[i_index] != -1:
            builder.integer(indexlist[i_index])
        builder.end_list()
    return builder
## actual function to call
def gen_akindex_from_indexlist(*, indexlist):
    builder = ak.ArrayBuilder()
    builder = _build_gen_akindex_from_indexlist(indexlist=indexlist, builder=builder)
    gen_ak_idx = builder.snapshot()
    return gen_ak_idx

### apply awkward index to an ak array
# arr: ak array to be sliced
# aki: ak index array
# padlen: if > 0, pad defaultvalue to each row until there are at least padlen entries in each row
# padval: value to be padded
# firsts: it True, collapse inner list and select first element of it
def apply_akindex(*, arr, aki, padlen=0, padval=None, firsts=True):
    # apply ak index to arr
    arr = arr[aki]
    # pad values if desired
    if padlen > 0:
        arr = ak.pad_none(arr, padlen, clip=False)
        arr = ak.fill_none(arr, padval)
    if firsts == True:
        arr = ak.firsts(arr)
    return arr
