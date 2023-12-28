# Library to run system commands
import os

# Library for plotting
import matplotlib as mpl
mpl.use('Agg')  # this enforces non-interactive plotting
				# (so no window will pop up)
import matplotlib.pyplot as plt

# Library for FITS files
# pyfits is depreciated. It is now a part of the astropy package as astropy.io.fits
from astropy.io import fits as pyfits
# import pyfits

from hyperion.model import ModelOutput
from hyperion.util.constants import pc
km = 1.e5

# get object for model results
m = ModelOutput('model_result_file.rtout')

# Retrieve the image
wav, nufnu = m.get_image(group=0, distance=8000*km, units='MJy/sr')

# We can reverse the wavelength order:
wav = wav[::-1]
nufnu = nufnu[:, :, :, ::-1]

# To export cube for all wavelengths viewable in ds9, need to re-order dimensions
nufnu = nufnu.swapaxes(3, 2)
nufnu = nufnu.swapaxes(2, 1)

# Print out the index and wavelengths of the images (just for info)
for i in range(len(wav)):
	print("Wavelength: " + str(wav[i]) + " microns")

# Write out the image cube as a FITS cube
pyfits.writeto('images.fits', nufnu, clobber=True)
# Compress the FITS cube because it's pretty big otherwise
os.system('gzip --best --force images.fits')

print("Finished extracting.")
