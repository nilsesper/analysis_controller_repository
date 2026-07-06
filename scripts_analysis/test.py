
import awkward as ak
import numpy as np
import numba as nb
import subprocess
import sys
import os

from analysis_controller.src import analysis_utils

###############################################################

# arr = ak.Array([
#     [ 0,  1],
#     [10, 11, 12],
#     [],
#     [30, 31],
#     [40, 41, 42, 43],
# ])
# want_idx = ak.Array([
#     [0],
#     [1],
#     [],
#     [0],
#     [],
# ])
# print(f"arr           = {arr}")
# print(f"want_idx      = {want_idx}")
# print(f"arr[want_idx] = {arr[want_idx]}")

# got_idx = [
#     0,
#     1,
#     -1,
#     0,
#     -1,
# ]
# print(f"++++++++++")
# print(f"got_idx       = {got_idx}")

# ### generate awkward index, to slice an ak array
# # ak array to slice: structure [ [x1, x2], [x1], [], [x1], ]
# # indexlist: [ index of one inner entry that should be selected, or -1 if none should/can be selected ]
# # returns: ak index array [ [ index of inner entry or empty list if none should be selected ] ]
# # usage: gen_idx = gen_akindex_from_indexlist(indexlist=got_idx)
# @nb.jit
# def build_gen_akindex_from_indexlist(indexlist, builder):
#     n_indices = len(indexlist)
#     for i_index in range(n_indices):
#         builder.begin_list()
#         if indexlist[i_index] != -1:
#             builder.integer(indexlist[i_index])
#         builder.end_list()
#     return builder
# # actual function to call
# def gen_akindex_from_indexlist(indexlist):
#     builder = ak.ArrayBuilder()
#     builder = build_gen_akindex_from_indexlist(indexlist=got_idx, builder=builder)
#     gen_ak_idx = builder.snapshot()
#     return gen_ak_idx

# gen_idx = analysis_utils.gen_akindex_from_indexlist(indexlist=got_idx)

# print(f"gen_idx       = {gen_idx}")
# print(f"arr[gen_idx]  = {arr[gen_idx]}")


###############################################################

# mapping = {
#     0: 0,
#     1: 10,
#     2: 20,
# }
# print(f"mapping     = {mapping}")

# nb_mapping = nb.typed.Dict.empty(key_type=nb.types.int32, value_type=nb.types.int32)
# for key, value in mapping.items():
#     nb_mapping[key] = value
# print(f"nb_mapping   = {nb_mapping}")

# @nb.jit
# def numba_dict(list_keys, nb_mapping):
#     list_values = []
#     for key in list_keys:
#         value = nb_mapping[key]
#         list_values.append(value)
#     return list_values

# list_keys = [0, 1, 2]
# print(f"list_keys    = {list_keys}")

# list_values = numba_dict(list_keys=list_keys, nb_mapping=nb_mapping)
# print(f"list_values  = {list_values}")

###############################################################





###############################################################


