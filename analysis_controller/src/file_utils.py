#############################
### CONFIG FILE UTILITIES ###
#############################

############################
### IMPORTS

import os
import sys
import yaml
import ROOT

from analysis_controller.src import path_utils
from analysis_controller.src import console_utils 
from analysis_controller.src import hist_utils

_FILEPATH = os.path.abspath( __file__ ) # absolute path of this file (including the file itself)
_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH, _ANALYSIS_CONTROLLER_PATH, _ANALYSIS_CONTROLLER_REPO_PATH = path_utils.relative_path_analysis_controller(filepath=_FILEPATH)

############################
### HELPER FUNCTIONS & CLASSES (with prefix "_")

### determination of file type (file, directory) with first char of permissions (from ls -lH output)
_perm_to_type = {
    "-": "file",
    "d": "directory",
    "l": "symlink",
    "b": "block",
    "c": "char",
    "s": "socket",
    "p": "fifo",
}

### recursive scan for files in subdirs
def _recursive_file_scan(*, cur_basepath, ls_command="ls -l", file_suffix="", maxdepth=9999, verbose=1, cur_found_files=[], cur_depth=0):
    # check whether depth is not too high, else immediately exit
    if cur_depth > maxdepth:
        return cur_found_files
    # run ls command
    returnvalue, cmdout = console_utils.run_command(bash_command=f'{ls_command} {cur_basepath}', verbose=verbose)
    # analyze output of ls command
    subdir_basepaths = []
    for ls_line in cmdout.split("\n"):
        # make sure line is not empty
        if ls_line.lower().startswith("total"):
            continue
        if len(ls_line) == 0:
            continue
        # extract information from ls output
        ls_line_parts = ls_line.split(maxsplit=8) # maxsplit=8 ensures that spaces in last column (filename) are not misinterpreted
        ls_line_parts = [console_utils.remove_console_characters(input_str=ls_item) for ls_item in ls_line_parts]
        perms, links, owner, group, size, month, day, time_or_year, name = ls_line_parts
        # determine type from permission string
        perms_firstchar = perms[0]
        dtype = _perm_to_type[perms_firstchar]
        # remove trailing spaces from name
        name = name.rstrip()
        # determine rel filepath / objpath
        rel_objath = os.path.join(cur_basepath, name)
        # check if directory: call recursively (later)
        if dtype == "directory":
            subdir_basepaths.append(rel_objath)
        # skip if not file
        if dtype != "file":
            continue
        # check file suffix (if desired)
        if file_suffix != None:
            if not name.endswith(file_suffix):
                continue
        # add found file to list, use rel filepath as key
        cur_found_files.append({
            "path": rel_objath,
            "size": int(size),
        })
    # recusively analyze subdirs, if depth not too high
    next_depth = cur_depth+1
    for subdir_basepath in subdir_basepaths:
        cur_found_files = _recursive_file_scan(cur_basepath=subdir_basepath, ls_command=ls_command, file_suffix=file_suffix, maxdepth=maxdepth, verbose=verbose, cur_found_files=cur_found_files, cur_depth=next_depth)
    return cur_found_files

### recursively write nested dict into rootfile, using TDirectories
# allowed input_dictionary value types:
# - pyroot TObject derived objects
# - RootHist objects
def _recursive_rootfile_write(input_dictionary, rootdirectory):
    for name, item in input_dictionary.items():
        # dictionary -> further recursive looping
        if isinstance(item, dict):
            # Reuse existing directory if present
            subdir = rootdirectory.GetDirectory(name)
            if not subdir:
                subdir = rootdirectory.mkdir(name)
            _recursive_rootfile_write(item, subdir)
        # root object
        elif isinstance(item, ROOT.TObject):
            rootdirectory.cd()
            item.Write(name, ROOT.TObject.kOverwrite)
        # RootHist object -> store as roothist
        elif isinstance(item, hist_utils.StructRootHist):
            rootdirectory.cd()
            rootitem = item.roothist
            rootitem.Write(name, ROOT.TObject.kOverwrite)
        # plain number (int/float) -> store as double
        elif isinstance(item, float) or isinstance(item, int):
            rootdirectory.cd()
            rootitem = ROOT.TParameter("double")(name, float(item))
            rootitem.Write(name, ROOT.TObject.kOverwrite)
        # other objects
        else:
            raise TypeError(f"Unsupported object at '{name}': {type(item).__name__}")

### recursively read nested rootfile into nested dict, using TDirectories
def _recursive_rootfile_read(rootdirectory):
    output_dictionary = {}
    for key in rootdirectory.GetListOfKeys():
        name = key.GetName()
        obj = key.ReadObj()
        # directory -> further recursive looping
        if obj.InheritsFrom(ROOT.TDirectory.Class()):
            output_dictionary[name] = _recursive_rootfile_read(obj)
        else:
            # roothist object -> convert to RootHist object
            if isinstance(obj, ROOT.TH1):
                out_obj = hist_utils.create_RootHist_from_rootobj(roothist=obj)
                output_dictionary[name] = out_obj
            # tparameter double object -> convert to float
            elif isinstance(obj, ROOT.TParameter("double")):
                out_obj = float(obj.GetVal())
                output_dictionary[name] = out_obj
            # other objects
            else:
                output_dictionary[name] = obj
    return output_dictionary

############################
### MAIN FUNCTIONS & CLASSES

### convert file size in bytes to human readable file size
# human readable format: "1.3 GiB"
def byte_size_to_human_readable_size(*, bytesize, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(bytesize) < 1024.0:
            return f"{bytesize:3.1f} {unit}B"
        bytesize /= 1024.0
    return f"{bytesize:.1f} YiB"

### convert human readable file size to byte file size
# human readable format: "1.3 GiB"
def human_readable_size_to_byte_size(*, humanreadablesize):
    units = {"":1, "Ki":1024, "Mi":1024**2, "Gi":1024**3,
             "Ti":1024**4, "Pi":1024**5, "Ei":1024**6,
             "Zi":1024**7, "Yi":1024**8}
    import re
    m = re.match(r'^\s*([0-9.]+)\s*([KMGTPEZY]?i?)?\s*B?\s*$', humanreadablesize, re.I)
    if not m: raise ValueError
    num = float(m.group(1))
    unit = (m.group(2) or "").title()
    return int(round(num * units[unit]))

### load local file
def load_local_file(*, filepath):
    if not os.path.isfile(filepath):
        console_utils.raise_exception(string=f"Could not find the file \"{filepath}\"")
    with open(filepath, "r") as file:
        content = str(file.read())
    return content

### store local file
def store_local_file(*, filepath, new_content):
    with open(filepath, "w") as file:
        file.write(new_content)

### replace wildcards in file if possible
# content: one large string as file content
# wildcards: {wildcard: meaning}
def replace_wildcards_if_possible(*, content, wildcards):
    new_content = content
    for wildcard, wildcard_replacement in wildcards.items():
        new_content = new_content.replace(wildcard, wildcard_replacement)
    return new_content

### load local yaml file
def load_local_yaml_file(*, filepath):
    if not os.path.isfile(filepath):
        console_utils.raise_exception(string=f"Could not find the file \"{filepath}\"")
    with open(filepath, "r") as file:
        yaml_content = yaml.safe_load(file)
    return yaml_content

### store local yaml file
def store_local_yaml_file(*, filepath, yaml_content):
    content = yaml.safe_dump(yaml_content)
    with open(filepath, "w") as file:
        file.write(content)

### recursively scan for files
# basepath: path from where to start the recursive scan
# ls_command: "ls -h"-like command that produces the following output format, e.g. "ls -h" or "gfal-ls -h":
#   "drwxrwxrwx  0 0     0        0.0    Jun 27 00:43 260626_075212" for directory
#   "-rw-------. 1 esper inst3a   205275 Jun 17 12:07 output.root" for file
# file_suffix: optional file suffix to filter on, e.g. ".root"
# maxdepth: max directory depth of recursive search
# verbose: change print statement behavior
## returns:
# found_files: [{path (wrt basepath), size (in bytes)}]
# total_size: total size of found files in bytes (int)
def recursive_file_scan(*, basepath, ls_command="ls -l", file_suffix="", maxdepth=9999, verbose=1):
    # print
    if verbose >= 1:
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"Attempting to recursively find files with the command \"{ls_command}\" starting from path \"{basepath}\"")
    # recursive scan, starting at basepath
    found_files = _recursive_file_scan(cur_basepath=basepath, ls_command=ls_command, file_suffix=file_suffix, maxdepth=maxdepth, verbose=max(0,verbose-1), cur_depth=0, cur_found_files=[])
    # calculate file no
    n_files = len(found_files)
    # calculate file size
    total_size = 0
    for file in found_files:
        total_size += file["size"]
    total_size_str = byte_size_to_human_readable_size(bytesize=total_size)
    # print
    if verbose >= 1:
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"Found \"{n_files}\" files with a total size of \"{total_size_str}\"")
    return found_files, total_size

### replace substring in file path
# file_list: [{path, size (in bytes)}]
# subs_from: substring to be replaced
# subs_with: substring that is inserted instead
def replace_substring_filepath(*, file_list, subs_from=" ", subs_with=" "):
    for i in range(len(file_list)):
        file_list[i]["path"] = file_list[i]["path"].replace(subs_from, subs_with)
    return file_list

### get file size
# file_path: path to file
# ls_command: custom ls -l command (e.g. when on grid)
def get_file_size(*, file_path, ls_command="ls -l", verbose=1):
    # run ls command
    returnvalue, cmdout = console_utils.run_command(bash_command=f'{ls_command} {file_path}', verbose=verbose)
    # analyze output of ls command
    ls_lines = cmdout.split("\n")
    # check if only one line output
    if len(ls_lines) != 2:
        console_utils.raise_exception(string="Unexpected behavior of ls command when trying to get the file size")
    ls_line = ls_lines[0]
    # extract information from ls output
    ls_line_parts = ls_line.split(maxsplit=8) # maxsplit=8 ensures that spaces in last column (filename) are not misinterpreted
    ls_line_parts = [console_utils.remove_console_characters(input_str=ls_item) for ls_item in ls_line_parts]
    perms, links, owner, group, size, month, day, time_or_year, name = ls_line_parts
    return int(size)

### combine files into groups which should be hadd-ed together, respecting the file sizes
# file_list: [files = {path (wrt basepath), perms, links, owner, group, size (in bytes), month, day, time_or_year, dtype}]
# target_group_size: target size of group of files (if group >= this size, a new group is begun), in human readable form
## returns:
# file_group_list: [{size (sum of all file sizes in group), files: [file dict for all files in group]}]
def group_files(*, file_list, target_group_size="1 GiB", verbose=1):
        n_files = len(file_list)
        # print
        if verbose >= 1:
            console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"Attempting to build file groups of target size \"{target_group_size}\" from \"{n_files}\" input files")
        # parse target size
        target_file_group_size = human_readable_size_to_byte_size(humanreadablesize=target_group_size)
        # build groups
        file_group_list = []
        file_group = {"size": 0, "files": []}
        for i_file, file in enumerate(file_list):
            # continue to fill current group
            file_group["size"] += file["size"]
            file_group["files"].append(file)
            # if too large or last file, stop current group and start new group
            if file_group["size"] > target_file_group_size or i_file == n_files-1:
                file_group_list.append(file_group)
                file_group = {"size": 0, "files": []}
        n_file_groups = len(file_group_list)
        # print
        if verbose >= 1:
            console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"Built \"{n_file_groups}\" file groups")
        return file_group_list

### generate hadd file paths from file groups
# file_group_list: [{size (sum of all file sizes in group), files: [file dict for all files in group]}]
# hadd_basepath: base dir where hadd file names should be
# hadd_name_prefix: prefix of hadd file name. will be "{prefix}{index}.root"
## returns:
# hadd_file_list: [{input_files, input_size, path}]
def hadd_names_from_file_groups(*, file_group_list, hadd_basepath, hadd_name_prefix="output_", verbose=1):
    hadd_file_list = []
    for i in range(len(file_group_list)):
        hadd_file_name = f"{hadd_name_prefix}{i}.root"
        hadd_file_path = os.path.join(hadd_basepath, hadd_file_name)
        hadd_file_list.append({
            "input_files": file_group_list[i]["files"],
            "input_size": file_group_list[i]["size"],
            "path": hadd_file_path,
        })
    return hadd_file_list

### actually hadd the files together
# hadd_file_list: [{input_files, input_size, path}]
# hadd_command: string of hadd command to be executed, e.g. if you like special arguments
# check_exists: if True, ask user whether to overwrite file
# also measure size of output file
## returns:
# hadd_output_file_list: [{input_files, input_size, path, size}]
def run_hadd_commands(*, hadd_file_list, hadd_command="hadd -ff -f", check_exists=True, delete_source_files=False, rm_command="rm -f", ls_command="ls -l", check_hadd_file_size=True, file_size_rel_diff_thres=0.05, verbose=1):
    hadd_output_file_list = []
    n_hadd_files = len(hadd_file_list)
    # check any hadd file with same name already exists
    if check_exists:
        if verbose >= 1:
            console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"Checking whether any of the target hadd files already exists")
        already_exists = False
        for i in range(n_hadd_files):
            hadd_file_path = hadd_file_list[i]["path"]
            if os.path.isfile(hadd_file_path):
                already_exists = True
        # ask user whether he wants to continue
        if already_exists:
            console_utils.raise_exception(string="Aborted because any of the target hadd files already exists")
        if verbose >= 1:
            console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"None of the target hadd files already exist")
    # perform actual hadd-ing
    for i in range(n_hadd_files):
        hadd_file_path = hadd_file_list[i]["path"]
        if verbose >= 1:
            console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"Running \"{hadd_command}\" command for file group \"{i+1} / {n_hadd_files} ({(i+1)/n_hadd_files*100:03f} %)\"")
        # prepare string of input files
        input_str = ""
        for file in hadd_file_list[i]["input_files"]:
            input_file_path = file["path"]
            input_str += f"{input_file_path} "
        # run hadd command
        bash_command = f'{hadd_command} {hadd_file_path} {input_str}'
        returnvalue, cmdout = console_utils.run_command(bash_command=bash_command, verbose=max(0,verbose-1))
        # check if hadd file was actually created
        if not os.path.isfile(hadd_file_path):
            console_utils.raise_exception(string="The hadd command was executed but the output file could not be found")
        # measure size of created hadd file
        hadd_file_size = get_file_size(file_path=hadd_file_path, ls_command=ls_command, verbose=max(0,verbose-1))
        # if desired: make sure file size is roughly the same
        if check_hadd_file_size:
            file_size_abs_diff = abs(hadd_file_size - hadd_file_list[i]["input_size"])
            file_size_rel_diff = file_size_abs_diff / hadd_file_size
            if file_size_rel_diff > file_size_rel_diff_thres:
                console_utils.raise_exception(string=f"The created hadd file does not match in total size with the input files within \"{file_size_rel_diff_thres*100:03f} %\"")
            if verbose >= 1:
                console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"The created hadd file does match in total size with the input files within \"{file_size_rel_diff_thres*100:03f} %\"")
        # if desired: delete source files
        if delete_source_files:
            if verbose >= 1:
                console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"Deleting the source files of the successfully executed hadd command")
            bash_command = f'{rm_command} {input_str}'
            returnvalue, cmdout = console_utils.run_command(bash_command=bash_command, verbose=max(0,verbose-1))
        # create output entry
        hadd_output_file_list.append({
            "input_files": hadd_file_list[i]["input_files"],
            "input_size": hadd_file_list[i]["input_size"],
            "path": hadd_file_path,
            "size": hadd_file_size,
        })
    return hadd_output_file_list

### store (nested) dict with items (histograms, numbers) into root file (with internal directory structure)
def store_dict_as_rootfile(*, input_dictionary, rootfile_path, check_exists=True, verbose=1):
    if verbose >= 1:
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"Attempting to store data in root file \"{rootfile_path}\"")
    # if desired: check if file exists
    if check_exists:
        if os.path.isfile(rootfile_path):
            console_utils.raise_exception(string=f"Aborted because the target root file \"{rootfile_path}\" already exists")
    # open rootfile
    rootfile = ROOT.TFile(rootfile_path, "RECREATE")
    # write rootfile contents
    _recursive_rootfile_write(input_dictionary=input_dictionary, rootdirectory=rootfile)
    # close rootfile
    rootfile.Close()

### read (nested) dict with items (histograms, numbers) from root file (with internal directory structure)
def read_dict_from_rootfile(*, rootfile_path, verbose=1):
    if verbose >= 1:
        console_utils.print_topic_string(topic=f"{_ANALYSIS_CONTROLLER_REPO_RELATIVE_FILEPATH} : {sys._getframe().f_code.co_name}()", string=f"Attempting to read data from root file \"{rootfile_path}\"")
    # open rootfile
    rootfile = ROOT.TFile.Open(rootfile_path)
    # read rootfile contents
    output_dictionary = _recursive_rootfile_read(rootdirectory=rootfile)
    # close rootfile
    rootfile.Close() 
    return output_dictionary