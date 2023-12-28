from astropy.io import fits

import matplotlib.pyplot as plt
from numpy import squeeze


file = '/home/sselvam/dart-export/sfa-c7-167.fits'
with fits.open(file) as f:
    print(f.info())
    data = f[0].data
    print(f'Shape of data0: {data.shape}')

    for perspective in data:
        plt.imshow(squeeze(perspective, axis=0), cmap='gray')
        plt.show()

