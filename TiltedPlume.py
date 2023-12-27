"""
UPDATE LOG
----------
NumberDensity is being replaced by NumberDensityList.
This allows us to specify the NumberDensity within each HeightPlumeRange interval

It would be more efficient to specify this within the individual dust files.
But that requires me to look into GenerateHDF5.generate_hdf5()
"""

import numpy as np
import os
import subprocess
import math
import signal
# from time import sleep
from hyperion.model import Model
from hyperion.util.constants import pi, lsun, rsun, tsun, au
from sys import exc_info
from HelperFunctions import *
from multiprocessing import Process, Value, Queue

# New Imports for multiprocessing debugging
import sys

# This is the specifics of the run
from current_config import *
##################################################################

# Initialize model
m = Model()


if WhichGrid != 'quick' and WhichGrid != 'slow':
    print("WhichGrid must either be 'quick' or 'slow'.")
    quit()
elif HeightPlumeRange[0] != 0.:
    print('PlumeHeightRange must start with 0.')
    quit()
elif HeightPlumeRange[-1] != HeightPlume / km:
    print('PlumeHeightRange must end with HeightPlume in KM.')
    quit()
elif len(DustFilesPlume) != 1 and (len(HeightPlumeRange) - 1) != len(DustFilesPlume):
    print('The size of HeightPlumeRange must be either exactly 1 or one more than DustFilesPlume.')
    quit()
elif HeightPlumeRange != sorted(HeightPlumeRange):
    print('HeightPlumeRange must be sorted in ascending order.')
    quit()

if len(NumberDensityList) != len(HeightPlumeRange) - 1:
    print('NumberDensityList must be len(HeightPlumeRange) - 1')
    quit()
##################################################################
# Set up walls (hstack is used to concatenate values/arrays)

PlumeTop = CenterDistanceCone + HeightPlume - Offset1Plume
if RnucleusMax > PlumeTop:
    rwFineGridMax = RnucleusMax + 0.2 * km
else:
    rwFineGridMax = PlumeTop + 0.2 * km


SunDistance = rwFineGridMax * 1.2  # 40.* km * scale
SunRadius = RnucleusMax

ObserverDistance = SunDistance * 0.8 - SunRadius

rw = np.hstack([0., RnucleusMin / 2.,
                np.linspace(RnucleusMin, rwFineGridMax, NumRadNucleusROI), (SunDistance + SunRadius) * 1.2], )

tw = np.hstack([np.linspace(0., 75., NumThetaNonROI),
                np.linspace(75., 90., math.floor((20. * NumThetaROI) / 105.)),
                np.linspace(90., 110., math.floor((17. * NumThetaROI) / 105.)),
                np.linspace(110., 135., math.floor((30. * NumThetaROI) / 105.)),
                np.linspace(135., 180., math.ceil((38. * NumThetaROI) / 105.))])

pw = np.hstack([np.linspace(0., 15., math.floor((7. * NumPhiROI) / 235.)),
                np.linspace(15., 25., math.floor((7. * NumPhiROI) / 235.)),
                np.linspace(25., 45., math.floor((17. * NumPhiROI) / 235.)),
                np.linspace(45., 60., math.floor((12. * NumPhiROI) / 235.)),
                np.linspace(60., 80., math.floor((12. * NumPhiROI) / 235.)),
                np.linspace(80., 205., NumPhiNonROI),
                np.linspace(205., 230., math.floor((53. * NumPhiROI) / 235.)),
                np.linspace(230., 250., math.floor((32. * NumPhiROI) / 235.)),
                np.linspace(250., 280., math.floor((42. * NumPhiROI) / 235.)),
                np.linspace(280., 315., math.floor((36. * NumPhiROI) / 235.)),
                np.linspace(315., 360., math.ceil((17. * NumPhiROI) / 235.))])

# Remove duplicates from the grids
rw = np.unique(rw)
tw = np.unique(tw)
pw = np.unique(pw)

# For radius grid, insert a point at the highest height of the plume
nearestIndex = np.argmin(np.abs(rw - PlumeTop))
if rw[nearestIndex] > PlumeTop:
    rw = np.insert(rw, nearestIndex, PlumeTop)
elif rw[nearestIndex] < PlumeTop:
    rw = np.insert(rw, nearestIndex + 1, PlumeTop)

# Sort, needed for use in Hyperion
tw.sort()
pw.sort()

# For phi grid, make certain 0 is first value and 360 last
if pw[-1] != 360.:
    pw = np.hstack([pw, 360.])
if pw[0] != 0.:
    pw = np.hstack([0, pw])
tw = tw * dtor
pw = pw * dtor
NumRad = len(rw) - 1
NumTheta = len(tw) - 1
NumPhi = len(pw) - 1
print("Grid radii (km): ", rw / km)
print("Grid theta angles: ", tw / dtor)
print("Grid phi angles: ", pw / dtor)

##################################################################

# Set up grid
print("Setting up the initial grid...")
m.set_spherical_polar_grid(rw, tw, pw)
print("Shape of grid (phi, theta, r): ", m.grid.shape)

##################################################################
# **Select array indices associated with plume
# 1) allow for a vertical gradient in dAnglePlume{Inner,Outer}
#
CoreIdx, = np.where(rw <= RnucleusMax)
print("Radial extent of nucleus (km): ", rw[CoreIdx] / km)

# Key information about the grid
PlumeRad_idx1, = np.where(rw <= (PlumeTop))
PlumeRad_idx2, = np.where(rw >= CenterDistanceCone)
PlumeRadIdx = np.intersect1d(PlumeRad_idx1, PlumeRad_idx2)
NumRadPlume = len(PlumeRadIdx)
print("Number of radial walls in plume: ", NumRadPlume)
print("Radial extent of plume (km): ", rw[PlumeRadIdx] / km)


# Create cell mid-point arrays
RadiusMid = (rw[1:NumRad] + rw[0:NumRad - 1]) / 2
ThetaMid = (tw[1:NumTheta] + tw[0:NumTheta - 1]) / 2
PhiMid = (pw[1:NumPhi] + pw[0:NumPhi - 1]) / 2

# Re-insert approximately zero points removed during creation of mid-point arrays
RadiusMid = np.insert(RadiusMid, 0, 0)
ThetaMid = np.insert(ThetaMid, 0, (ThetaMid[NumTheta - 2] +
                                   0.5 * (180. * dtor - ThetaMid[NumTheta - 2] + ThetaMid[0])) % (180. * dtor))
PhiMid = np.insert(PhiMid, 0, (PhiMid[NumPhi - 2] +
                               0.5 * (360. * dtor - PhiMid[NumPhi - 2] + PhiMid[0])) % (360. * dtor))

RadiusMid.sort()
ThetaMid.sort()
PhiMid.sort()

DensityCoreArray = np.zeros((NumPhi, NumTheta, NumRad))
DensityDiskArray = np.zeros((NumPhi, NumTheta, NumRad))
DensityPlumeArray = np.zeros((2, NumPhi, NumTheta, NumRad))
# DensityPlumeArray = np.zeros((len(HeightPlumeRange), NumPhi, NumTheta, NumRad))

# Cartesian vector of plume base
x0, y0, z0 = SphericalToCartesian(CenterDistanceCone, ThetaPlume, PhiPlume)
PlumeVector = np.array([x0, y0, z0])
print("Plume Vector (cartesian, km): ", PlumeVector / km)

# Derive rotation matrix which brings plume to z-axis or polar coordinates (r,0,0)
Zaxis = np.array([0, 0, 1])
Yaxis = np.array([0, 1, 0])
Xaxis = np.array([1, 0, 0])
RMz = RotationMatrix(Zaxis, PhiPlume)
RMy = RotationMatrix(Yaxis, ThetaPlume)
RM = np.dot(RMy, RMz)

# Derive rotation matrix for tilting of cone
RMyTilt = RotationMatrix(Yaxis, ThetaTilt)
RMzTilt = RotationMatrix(Zaxis, PhiTilt)
RMTilt = np.dot(RMyTilt, RMzTilt)

# Derive rotation matrix for tilting of disk/wedge
RMyTiltDisk = RotationMatrix(Yaxis, 25. * dtor)  # 25 is best, maybe 30
RMzTiltDisk = RotationMatrix(Zaxis, PhiTilt + 10. * dtor)  # 5 is so far best, maybe 10
# RMyTiltDisk = RotationMatrix(Yaxis, ThetaTilt)
# RMzTiltDisk = RotationMatrix(Zaxis, PhiTilt)
RMTiltDisk = np.dot(RMyTiltDisk, RMzTiltDisk)

# Build the plume grid by calling the parallelized function FillDensityPlumeArray
NumPythonProcesses = 6
print('Building plume grid (running ' + str(NumPythonProcesses) + ' parallel processes)...')
FirstZAboveZero = Value('d', -1)
Processes = []
ResultQueuesCone = []
ResultQueuesDisk = []

for i in range(1, NumPythonProcesses + 1):
    StartPhi = round(NumPhi / NumPythonProcesses) * (i - 1)
    if i != NumPythonProcesses:
        EndPhi = round(NumPhi / NumPythonProcesses) * i
    else:
        EndPhi = NumPhi

    ResultQueuesCone.append(Queue())
    ResultQueuesDisk.append(Queue())
    Processes.append(Process(target=FillDensityPlumeArray, args=(NumRad, NumTheta, StartPhi, EndPhi,
                                                                 RadiusMid, ThetaMid, PhiMid, DensityPlumeArray,
                                                                 DensityDiskArray, FirstZAboveZero, HeightPlume,
                                                                 OpeningAnglePlume, Offset1Plume, HeightPlumeRange,
                                                                 OpeningAngleHollowPlume, NumberDensityList,
                                                                 massPerParticle, RM, RMTilt, RMTiltDisk,
                                                                 CenterDistanceCone, ConeOffset, PlumeVector,
                                                                 ResultQueuesCone[i - 1], ResultQueuesDisk[i - 1])))

try:
    for Process in Processes: Process.start()
    for ResultQueueCone in ResultQueuesCone:
        DensityPlumeArraySubresult = ResultQueueCone.get()
        NonzeroIndicies = np.nonzero(DensityPlumeArraySubresult)
        DensityPlumeArray[NonzeroIndicies] = DensityPlumeArraySubresult[NonzeroIndicies]
    for ResultQueueDisk in ResultQueuesDisk:
        DensityDiskArraySubresult = ResultQueueDisk.get()
        NonzeroIndicies = np.nonzero(DensityDiskArraySubresult)
        DensityDiskArray[NonzeroIndicies] = DensityDiskArraySubresult[NonzeroIndicies]

except:
    for Process in Processes: Process.terminate()
    print(exc_info()[2])
    raise

# Output all theta and phi combinations
# (used further in code to determine where the asteroid nucleus should be in the grid)

file_socket = open(os.path.join('IDL', 'positions_file.txt'), 'w')
for it in range(0, NumTheta):
    tt = ThetaMid[it]
    for ip in range(0, NumPhi):
        pp = PhiMid[ip]
        file_socket.write(str(tt / dtor) + '\t' + str(pp / dtor) + '\n')
file_socket.close()

# Call IDL to determine which points are inside the asteroid
if WhichGrid == 'quick':
    OutputFilename = QuickGridShapeFile
else:
    OutputFilename = SlowGridShapeFile

### IDL Portion ###
NumIDLProcesses = 4
print('Running IDL to help build nucleus grid (running ' + str(NumIDLProcesses) + \
      ' parallel processes)...')
NumCalcs = NumTheta * NumPhi
IDLPath = os.path.join(os.getcwd(), 'IDL') + '/'
Processes = []
OutputFilenames = ''
print('Total points: ' + str(NumCalcs))

for i in range(1, NumIDLProcesses + 1):
    StartingPosition = round(NumCalcs / NumIDLProcesses) * (i - 1)
    if i != NumIDLProcesses:
        EndingPosition = round(NumCalcs / NumIDLProcesses) * i
    else:
        EndingPosition = NumCalcs

    CurOutputFilename = OutputFilename + str(i)
    IDLJob = subprocess.Popen("idl -quiet \"IDL/run_point_inside_routine.pro\" -args " + IDLPath +
                              ' ' + str(StartingPosition) + ' ' + str(EndingPosition) + ' ' + CurOutputFilename +
                              ' ' + str(NumIDLProcesses), shell=True, executable='/bin/tcsh', preexec_fn=os.setsid)
    Processes.append(IDLJob)
    OutputFilenames = OutputFilenames + CurOutputFilename + ' '

try:
    for Process in Processes:
        Process.wait()
except:
    for Process in Processes:
        os.killpg(Process.pid, signal.SIGTERM)
    print(exc_info()[2])
    raise

# Each subprocess stores its results in an individual file
# At the end, these need to be recombined
ConcatFiles = subprocess.Popen((f"cd IDL; cat " + OutputFilenames +
                                " > " + OutputFilename), shell=True)
ConcatFiles.wait()
DeleteFiles = subprocess.Popen((f"cd IDL; rm -rf " + OutputFilenames), shell=True)
DeleteFiles.wait()
print('IDL done.. continuing.')
### END OF IDL Portion ###

NucleusRadii = np.loadtxt(os.path.join('IDL', OutputFilename))

# Set indices for core radii to large optically thick value
print('Building nucleus grid...')
i = 0
rrDividedByKM = RadiusMid / km

for it in range(0, NumTheta):
    for ip in range(0, NumPhi):
        biggerIndices = (np.where(rrDividedByKM >= NucleusRadii[i]))[0]

        ir = biggerIndices[0]
        DensityCoreArray[ip, it, 0:ir] = 1e5
        i = i + 1


# Add density grids to physical grids
m.add_density_grid(DensityCoreArray, DustFileCore)

for i in range(0, 1):
# for i in range(0, len(HeightPlumeRange) - 1):
    if len(DustFilesPlume) == 1:
        m.add_density_grid(DensityPlumeArray[i], DustFilesPlume[0], None, False)
    else:
        m.add_density_grid(DensityPlumeArray[i], DustFilesPlume[i], None, False)

print('Done building all grids.')
print('Finishing up...')


# ThetaSource - Rotates downward from top (positive z-axis) (in frame of source)
ThetaSource = 94.01542  # Given here in asteroid's reference frame (converted into source's later)
# PhiSource - Rotates counterclockwise from positive x-axis (in frame of source)
PhiSource = 332.767  # Given here in asteroid's reference frame (converted into source's later)

# Calculate proper phi and theta angles in source's reference frame,
# and get x, y positions of the source

# SunDistance = 40. * km 
# SunDistance = 40.* km * scale
SourceX, SourceY, SourceZ, ThetaSource, PhiSource \
    = BodyCoordinatesToObjectCoordinates(SunDistance, ThetaSource, PhiSource)

source = m.add_plane_parallel_source()
source.radius = SunRadius
# source.radius = 15. * km
# TODO: replace the hardcoded radius in the equation fomula
source.luminosity = pi * (15 * km) ** 2 / (4 * pi * d_sun ** 2) * lsun
source.temperature = tsun

# Set position of source and direction of light from source (in the source's reference frame)
source.position = (SourceX, SourceY, SourceZ)
source.direction = (ThetaSource, PhiSource)

# Set to scattering only, no thermal emission
m.set_kill_on_absorb(True)

# Generate the viewing angles (viewing options in DS9)
ThetaObserver = [ThetaSC, 110, 100, 90, 80, 70, 100, 180, 70, 90, 130, 150, 170]
PhiObserver = [PhiSC, PhiSC, PhiSC, PhiSC, PhiSC, 350, 350, 350, 20, 50, 50, 50, 50]

# Calculate proper phi and theta angles in observer's reference frame, and get x, y positions of the observer
# ObserverDistance = 30. * km
ObserverX, ObserverY, ObserverZ, _, irr \
    = BodyCoordinatesToObjectCoordinates(ObserverDistance, ThetaObserver[0], PhiObserver[0])

# Set up the image
image = m.add_peeled_images()
image.set_image_size(CameraPixNx, CameraPixNy)
image.set_image_limits(-CameraHalfWidth, CameraHalfWidth, -CameraHalfWidth,
                       CameraHalfWidth)

# Only produce monochromatic images
m.set_monochromatic(True, wavelengths=[0.55])

# Set position of observer and direction that observer is looking in
image.set_viewing_angles(ThetaObserver, PhiObserver)  # (theta, phi)

# No temperature calculation
m.set_n_initial_iterations(0)

# Set number of photons
m.set_n_photons(imaging_sources=NumberOfPhotons, imaging_dust=0)

# Write out file
m.write(ModelInputFile)

print('Finished!')
quit()
