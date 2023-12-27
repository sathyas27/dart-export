from hyperion.dust import HenyeyGreensteinDust, SphericalDust
from hyperion.util.constants import c
import numpy as np
import os
DustFolder = 'dust-files'
DataFolder = 'data'

"""
DESCRIPTION
-----------
This script generates the HDF5 dust files usedt to construct models.

We have been relying on the Henyey Greenstein model for BOTH the plume and core.
"""

def generate_hdf5(parameters, output_file, dustType='HG'):
    # print(parameters)
    # # print(parameters.keys())
    # if dustType in parameters.values():
    #     dustType = parameters['dustType']

    output_file = os.path.join(DustFolder, output_file)

        # specify wavelength and frequency (monotonically increasing in frequency)
    wave = np.hstack([1e7, 5.5e-1, 1e-3])  # microns
    nu = c / wave
    nu = c / (wave * 1e-4)  # Hz
    NumWave = len(wave)

    if dustType == 'HG':
        print("Generating new Henyey-Greenstein dust file with rootname: ", output_file)

        # specify albedo and chi (cm^2/g of dust)
        albedo = np.ones(NumWave) * parameters["albedo0"]
        g = np.ones(NumWave) * parameters["g0"]
        chi = np.ones(NumWave) * parameters["chi0"]
        pmax = np.ones(NumWave) * parameters["pmax0"]

        # create dust object
        d = HenyeyGreensteinDust(nu, albedo, chi, g, pmax)
    
    # Create a fully customized 4-element dust 
    else:
        print("Generating new fully customized dust file with rootname: ", output_file)

        # file = 'data/Munoz.txt'
        file = os.path.join(DataFolder, parameters["dustFile"])
        with open(file, "r", encoding='utf-8-sig') as f:
            lines = f.readlines()

            # header = [line.strip() for line in lines[0].split(' ') if line != '']

            mu = []
            S11 = []
            S12 = []
            for line in lines[1::]:
                data = [float(value) for value in line.split(' ') if value != '']
                # mu.append(np.cos(data[0])) # Munoz
                # BUG: mu should be monotonically increasing
                mu.append(np.cos((180 - data[0])*np.pi/180))

                S11.append(data[1]) # Munoz: S11 = data[2]
                S12.append(data[2]) 

        d = SphericalDust()

        # Optical Dust Properties
        d.optical_properties.nu = nu
        d.optical_properties.albedo = np.ones(NumWave) * parameters["albedo0"]
        d.optical_properties.chi = np.ones(NumWave) * parameters["chi0"]

        # Scattering Properties
        # mu is the cosine of the scattering angleS
        d.optical_properties.mu = mu

        # P1 (equivalent to S11), P2 (equivalent to S12), P3 (equivalent to S44),
        # and P4 (equivalent to -S34). 

        # Each of these variables should be specified as a 2-d array with dimensions 
        # (n_nu, n_mu), where n_nu is the number of frequencies, 
        # and n_mu is the number of values of the cosine of the scattering angle:
        d.optical_properties.initialize_scattering_matrix()
        
        d.optical_properties.P1 =  np.ones((NumWave, len(S11))) * np.array(S11)
        # d.optical_properties.P2[:, :] = 0.  # for initial testing
        d.optical_properties.P2 =  np.ones((NumWave, len(S12))) * np.array(S12)
        d.optical_properties.P3[:, :] = 0.
        d.optical_properties.P4[:, :] = 0.
    
    d.write(output_file)

