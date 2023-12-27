from astropy.io import fits
import numpy as np

from hyperion.util.constants import pi

km = 1.e5
m = 1.e3
dtor = pi / 180.


file = '/home/sselvam/dart-export/ejecta_distance_time_leia.fits'


def getMassData(file, time, HeightPlume, massPerParticle=None):
    with fits.open(file) as f:
        allMassData = f[0].data
        allDistanceData = f[1].data
        allTimeData = f[2].data

        timeIndexes = np.where(allTimeData <= time)
        distanceIndexes = np.where(allDistanceData <= HeightPlume)

        timeIndex = timeIndexes[-1][-1]

        heightIndex = distanceIndexes[-1][-1]

        heightData = allDistanceData[0:heightIndex]
        heightData = np.insert(heightData, 0, 0)

        massData = allMassData[timeIndex][0:heightIndex]
        nParticlesList = massData / massPerParticle

        return list(nParticlesList), [item / km for item in list(heightData)]

def getNumberDensity(slice_nParticles, OpeningAnglePlume, OpeningAngleHollowPlume, sliceMinHeight, sliceMaxHeight):
    def volumeCone(height, angle):
        radius = height * np.tan(angle * dtor)
        volume = 1/3 * pi * radius**2 * height
        return volume

    volumeFilledCone = volumeCone(sliceMaxHeight, OpeningAnglePlume) - volumeCone(sliceMinHeight, OpeningAnglePlume)
    volumeHollowCone = volumeCone(sliceMaxHeight, OpeningAngleHollowPlume) - volumeCone(sliceMinHeight, OpeningAngleHollowPlume)
    
    volumeHollowSlice = volumeFilledCone - volumeHollowCone

    NumberDensity = slice_nParticles / volumeHollowSlice

    return NumberDensity

def buildLayeredPlume(file, time, HeightPlume, OpeningAnglePlume, OpeningAngleHollowPlume, massPerParticle):
    nParticlesList, HeightPlumeRange = getMassData(file, time, HeightPlume, massPerParticle)

    NumberDensityList = []
    for idx, nParticles in enumerate(nParticlesList):
        NumberDensityList.append(getNumberDensity(nParticles, OpeningAnglePlume, OpeningAngleHollowPlume, HeightPlumeRange[idx], HeightPlumeRange[idx+1]))

    print(NumberDensityList[0:10], HeightPlumeRange[0:10])

    return nParticlesList, NumberDensityList, HeightPlumeRange


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    time = 167  # s
    HeightPlume = 0.076 * km
    OpeningAnglePlume = 90. * dtor  # was 64 # opening angle of cone
    OpeningAngleHollowPlume = 44. * dtor  # opening angle of inner, hollow, cone


    rho = 2170  # kg/m3
    R = 1e-4 # m
    massPerParticle = 4/3 * np.pi * R**3 * rho  # 9.09e-9

    nParticlesList, NumberDensityList, HeightPlumeRange = buildLayeredPlume(file, time, HeightPlume, OpeningAnglePlume, OpeningAngleHollowPlume, massPerParticle)
    
    HeightPlumeRange = [item * m for item in HeightPlumeRange]
    NumberDensityList.insert(0, NumberDensityList[0])
    nParticlesList.insert(0, nParticlesList[0])


    print('PlumeHeight', HeightPlumeRange[-1])
    print('Maximum Number Density', "{:e}".format(max(NumberDensityList)))

    plt.plot(HeightPlumeRange, NumberDensityList)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Plume Height (m)')
    plt.ylabel('Number Density')
    plt.title(' '.join(['Number Density vs Plume Height After', str(time), 'Seconds']))
    plt.show()

    print(len(nParticlesList), len(NumberDensityList))
    plt.plot(HeightPlumeRange, nParticlesList)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Plume Height (m)')
    plt.ylabel('Number of Particles')
    plt.title(' '.join(['Number of Particles vs Plume Height After', str(time), 'Seconds']))
    plt.show()
