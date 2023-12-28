from hyperion.util.constants import pi
import loadDustFiles
# import calc_height
import os

from buildNumberDensityList import file, buildLayeredPlume

dtor = pi / 180.
km = 1.e5
massPerParticle = 9.09e-9

version = 'source-testing-smaller-centerDistanceCone'

##################################################################
# TODO: Write method to generate NumberDensityList
# This example should create bands of density
# NumberDensityList = [3.1e1, 3.2e2,  3.1e12, 3.2e2]
# NumberDensity = 4.023e12
# Previous was 1.e8
NumberOfPhotons = 1.e7


### Plume Geometry (in spherical coordinates) ###
time = 167
approximate_HeightPlume = 0.076 * km


ThetaPlume = 102.656 * dtor  # Given in asteroid's reference frame. Ranges from 0 to 180.
# Rotates downward from top (positive z-axis)
PhiPlume = (108.29 - 180) * dtor  # Given in asteroid's reference frame. Ranges from 0 to 360.
# Rotates counterclockwise from positive x-axis.
OpeningAnglePlume = 90. * dtor  # was 64 # opening angle of cone
Offset1Plume = 0.01 * km  # making this positive shifts the cone "downward" by Offset1Plume
OpeningAngleHollowPlume = 44. * dtor  # opening angle of inner, hollow, cone
ConeOffset = 0. * km  # set to 0 or large number to skip the hollow cone
PhiTilt = 0 * dtor  # 1st tilt rotation, about z-axis.   Rotates x-axis CCW about z-axis to setup
# the Theta rotation. (Bigger number rotates toward right of image.)
ThetaTilt = 0 * dtor  # 2nd tilt rotation, about y-axis.  if PhiTilt=0, positive is southward.

### Core Geometry ###
RnucleusMin = 0.0665 * km  # Minimal extent of the asteroid's nucleus
RnucleusMax = 0.104 * km  # Maximal extent of the asteroid's nucleus
CenterDistanceCone = 0.005 * km  # Distance from center coordinate system to the edge of nucleus
# at the cone's location

### Optical Properties ###
# Plume heights in the cone-centric coordinates (use as many divisions as you'd like)
# Plume dust properties in same order as plume height (one for each height divison)

_, NumberDensityList, HeightPlumeRange = buildLayeredPlume(file, time, approximate_HeightPlume, OpeningAnglePlume, OpeningAngleHollowPlume, massPerParticle)
HeightPlume = HeightPlumeRange[-1] * km

# TODO: Update code to only expect a single DustPlume File
DustPlume = [{"albedo0": 0.55, "chi0": 0.517, "g0": 0.9367, "pmax0": 0}]
DustFilesPlume = [os.path.join(loadDustFiles.DustFolder, DustFile) for DustFile in loadDustFiles.load_plume(DustPlume)]

DustCore = {"albedo0": 0.25, "chi0": 1, "g0": -0.49, "pmax0": 0}
DustFileCore = os.path.join(loadDustFiles.DustFolder, loadDustFiles.load_core(DustCore))

### General Grid Properties ###
WhichGrid = 'slow'  # Options are quick, or slow
if WhichGrid == 'quick':
    NumRadNucleusROI = 71
    NumThetaROI = 131
    NumPhiROI = 221
    NumThetaNonROI = 31
    NumPhiNonROI = 31
else:
    NumRadNucleusROI = 451
    NumThetaROI = 321
    NumPhiROI = 741
    NumThetaNonROI = 31
    NumPhiNonROI = 31

### Viewing Angle ###
ThetaSC = 90 + 11.69170539  # Theta angle of Sub-Spacecraft point (in asteroid's above-described coordinate system)
PhiSC = 98.50032253  # Phi angle of Sub-Spacecraft point (in asteroid's above-described coordinate system)

### Camera Properties ###
scale = 0.075
CameraHalfWidth = 4.441855 * km * scale

# pixels * platescale = CHW

platescale = 1735.1 * scale  # Centimeters per pixel

ModelInputFile = 'model_input_file.rtin'
QuickGridShapeFile = 'quick_grid.txt'
SlowGridShapeFile = 'slow_grid.txt'
d_sun = 156479687.3 * km  # target-solar distance in cm


CameraPixNx = CameraPixNy = round((2 * CameraHalfWidth) / platescale)

runIDL = True
