# get elevations
from libs.wgs84_gcj02 import *
import numpy as np

def swap(tp):
    f, l = tp
    return (l, f)

def request_elevation(gmaps, lng, lat, maxnum=512):
    """
    get elevations
    """
    
    xmin, xmax, xinc = lng
    ymin, ymax, yinc = lat
    
    xlist = np.arange(xmin, xmax, xinc)
    ylist = np.arange(ymin, ymax, yinc)
    points = [swap(wgs84_to_gcj02(x, y)) for y in ylist for x in xlist]

    requestnum = int(np.floor(len(points) / maxnum) + 1)
    npoints = np.array_split(points, requestnum)
    
    i = input("{} points and {} requests in total, continue?[y/n]".format(len(points), requestnum))
    if not (i == "y" or i == "Y"):
        raise("Cancelled.")
    
    if requestnum > 2500:
        raise("Error: Request number exceed! Change grid or region.")

    return [gmaps.elevation(locations=loc.tolist()) for loc in npoints]


