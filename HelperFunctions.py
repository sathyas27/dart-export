
import numpy as np
import sys
import os
from hyperion.util.constants import pi
from math import cos, sin, sqrt, acos, atan2, tan, fabs
dtor = pi / 180.
km = 1.e5

def InsideBody(x, y, z, AxisA, AxisB, AxisC):
    XCalc = (x/AxisA)**2.
    YCalc = (y/AxisB)**2.
    ZCalc = (z/AxisC)**2.

    if (XCalc+YCalc+ZCalc) <= 1.:
        return 1
    else:
        return 0


def SphericalToCartesian(r, t, p):
    x = r*sin(t)*cos(p)
    y = r*sin(t)*sin(p)
    z = r*cos(t)
    return x, y, z


def CartesianToSpherical(x, y, z):
    r = sqrt(x*x + y*y + z*z)
    theta = acos(z/r)
    phi = atan2(y, x)
    if phi < 0:
        phi = phi + (2*pi)
    return r, theta, phi


def InsideCone(x, y, z, PlumeHeight, PlumeOpeningAngle, ZShift):
    f = (x*x + y*y) - ((z+ZShift)*tan(PlumeOpeningAngle/2.))**2
    if (f <= 0) and (z >= 0.) and (z <= (PlumeHeight + ZShift)):
        return True
    else:
        return False


def InsideDisk(x, y, z, PlumeVector):
        f = (x*x + y*y) - (1.0*km)**2  # previously 2.5 km worked if radmax set to 4.5km
        if f <= 0 and 0. <= z <= (0.1 * km):
            return 1
        else:
            return 0


def RotationMatrix(axis, theta):
    axis = axis/np.sqrt(np.dot(axis,axis))
    a = np.cos(theta/2)
    b,c,d = -axis*np.sin(theta/2)
    return np.array([[a*a+b*b-c*c-d*d, 2*(b*c-a*d), 2*(b*d+a*c)],
                     [2*(b*c+a*d), a*a+c*c-b*b-d*d, 2*(c*d-a*b)],
                     [2*(b*d-a*c), 2*(c*d+a*b), a*a+d*d-b*b-c*c]])


def BodyCoordinatesToObjectCoordinates(RadialDistance, theta, phi):
    """Converts body-centric coordinates and angles into angles and coordinates in a
        given object's reference frame."""

    Z = RadialDistance * cos(theta * dtor)
    XYSourceLength = RadialDistance * fabs(sin(theta * dtor))
    theta = 180.-theta

    # Calculate proper phi angle in object's reference frame, and get x, y positions of the object
    if phi <= 90 or phi > 270:
        X = 1
    else:
        X = -1
    if phi <= 180:
        Y = 1
    else:
        Y = -1

    phi = (phi + 180) % 360
    X *= XYSourceLength * fabs(cos(phi * dtor))
    Y *= XYSourceLength * fabs(sin(phi * dtor))

    return [X, Y, Z, theta, phi]


def PlumeDensityFunction(x, y, z, InitialZHeight, NumberDensity, MassPerParticle):
    """Calculates density in the coordinate system of the cone"""

    NormalizedZ = z / InitialZHeight
    n0 = NumberDensity*MassPerParticle

    if 0.51*km <= z <= 0.52*km:
        f = n0*5 / (NormalizedZ**2)
    elif 0.5*km <= z <= 0.6*km:
        f = n0*5 / (NormalizedZ**2)
    else:
        f = n0 / (NormalizedZ**2)
    return f

# TODO: Replace NumberDensity with NumberDensityList
# Each element corresponds to the density of an interval specified by HeightPlumeRange
def FillDensityPlumeArray(NumRad, NumTheta, StartPhi, EndPhi, RadiusMid, ThetaMid, PhiMid,
        DensityPlumeArray, DensityDiskArray, FirstZAboveZero, HeightPlume,
        OpeningAnglePlume, Offset1Plume, HeightPlumeRange, OpeningAngleHollowPlume,
        NumberDensityList, MassPerParticle, RM, RMTilt, RMTiltDisk, CenterDistanceCone,
        ConeOffset, PlumeVector, ResultQueuePlume, ResultQueueDisk):

    sys.stdout = open(str(os.getpid()) + ".out", "w")
    print('testing')
    """Saves the plume's density grid for points inside the shape model to ResultQueue"""

    counter_i = 0
    InitialZHeight = (3./(pi * tan(OpeningAnglePlume/2.)**2.))**(1./3.)

    for ir in range(0, NumRad):
        print('new ir: ', ir, 'Percent: ', round(ir/NumRad, 2), flush=True)
        rr = RadiusMid[ir]
        for it in range(0, NumTheta):
            tt = ThetaMid[it]
            for ip in range(StartPhi, EndPhi):
                pp = PhiMid[ip]

                # Rotate Cone to z-axis
                x, y, z = SphericalToCartesian(rr, tt, pp)
                v = np.array([x, y, z])
                xp, yp, zp = np.dot(RM, v)
                zp = zp - CenterDistanceCone  # shift z coordinate down so that plume is plane

                # Tilt Cone
                vp = np.array([xp, yp, zp])
                xp, yp, zp = np.dot(RMTilt, vp)
                xp2, yp2, zp2 = np.dot(RMTiltDisk, vp)

                # Now, in cone-centric coordinates, see if point is inside cone(s)
                # only allow positive z solution (Cone is quadratic function)
                if 0. <= zp <= HeightPlume:
                    if InsideCone(xp, yp, zp, HeightPlume, OpeningAnglePlume, Offset1Plume):
                        CurrentHeight = zp/km - Offset1Plume/km
                        if CurrentHeight < 0.:
                            continue

                        # TODO: Since the input to next() is reinstated with each call,
                        # determine if this is equivalent to:
                        # the index of the largest element to be less than CurrentHeight
                        PlumeHeightIndex = next(x[0] for x in enumerate(HeightPlumeRange)
                                                if x[1] > CurrentHeight) - 1

                        DensityPlumeArray[min(1, PlumeHeightIndex), ip, it, ir] = \
                            PlumeDensityFunction(xp, yp, zp, InitialZHeight, NumberDensityList[PlumeHeightIndex], MassPerParticle)

                        # Check to see point is in the hollow portion
                        # If it is, set the density to 0
                        zp2 = zp - ConeOffset
                        if (zp2 >= 0.) and (ConeOffset > 0.):
                            if InsideCone(xp, yp, zp2, HeightPlume, OpeningAngleHollowPlume, Offset1Plume):
                                DensityPlumeArray[min(1, PlumeHeightIndex), ip, it, ir] = 0.

    print('After loop', flush=True)
    ResultQueuePlume.put(DensityPlumeArray)
    ResultQueueDisk.put(DensityDiskArray)
    print('Done', flush=True)
