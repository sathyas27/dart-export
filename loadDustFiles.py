import os
from GenerateHDF5 import generate_hdf5
DustFolder = 'dust-files'

"""
DESCRIPTION
-----------
The underlying code expects the dust files to follow a particular naming convention.

With the given dictionary of input parameters, this script attempts to locate the associated file to be used in the 
modeling. 
If that file does not exist, GenerateHDF5 is called to generate it. 
"""

def generate_file_name(parameters):
    label_dict = {"albedo0": ["A", 100],
                  "chi0": ["C", 1000],
                  "g0": ["G", 100],
                  "pmax0": ["P", 100]}

    if parameters["g0"] < 0:
        parameters["g0"] *= -1
        label_dict["g0"][0] = "Gm"
    arg_list = [val[0] + str(round(parameters[key] * val[1])).zfill(3) for key, val in label_dict.items()]

    output_file = '_'.join(arg_list)
    return output_file + ".hdf5"


def generate_parameters(file_name):
    parameter_list = file_name.replace('.hdf5', '').split('_')
    parameters = {
        "albedo0": float(parameter_list[0].replace('A', '')) / 100,
        "chi0": float(parameter_list[1].replace('C', '')) / 1000,
        "pmax0": float(parameter_list[3].replace('P', '')) / 100,
    }
    if parameter_list[2][0:2] == "Gm":
        parameters["g0"] = - float(parameter_list[2].replace('Gm', '')) / 100
    else:
        parameters["g0"] = float(parameter_list[2].replace('G', '')) / 100

    return parameters


def from_param_dict(parameters):
    file_name = generate_file_name(parameters)

    if not os.path.isfile(os.path.join(DustFolder, file_name)):
        generate_hdf5(parameters, file_name)

    return file_name


def from_file_str(file_name):
    if not os.path.isfile(os.path.join(DustFolder, file_name)):
        parameters = generate_parameters(file_name)
        generate_hdf5(parameters, file_name)

    return file_name


def load_single_dust_file(dust_input):
    if type(dust_input) == str:
        return from_file_str(dust_input)
    elif type(dust_input) == dict:
        return from_param_dict(dust_input)
    else:
        raise ValueError("Dust files can either be loaded by providing a parameter dictionary or file name.")


def load_core(core_input):
    return load_single_dust_file(core_input)


def load_plume(plume_input):
    assert type(plume_input) == list, "Please ensure your plume is a list"
    plume_list = []
    for dust_input in plume_input:
        plume_list.append(load_single_dust_file(dust_input))

    return plume_list
