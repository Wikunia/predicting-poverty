import numpy as np 
from osgeo import gdal
import pandas as pd
import os
import random

import geopy
import geopy.distance as distance

nightlight_fname = "south_middle"
out_dir = '../data/output/LSMS/'
country = 'malawi'

driver = gdal.GetDriverByName('GTiff')
filename = "../data/input/Nightlights/2016/"+nightlight_fname+".tif" #path to raster
dataset = gdal.Open(filename)
band = dataset.GetRasterBand(1)

cols = dataset.RasterXSize
rows = dataset.RasterYSize

transform = dataset.GetGeoTransform()

xOrigin = transform[0]
yOrigin = transform[3]
pixelWidth = transform[1]
pixelHeight = -transform[5]

print("xOr: ", xOrigin)
print("yOr: ", yOrigin)
print("pW: ", pixelWidth)
print("pH: ", pixelHeight)
data = band.ReadAsArray(0, 0, cols, rows)

clustering = np.load("../data/output/LSMS/malawi/clustering.npy")
nlats = np.load("../data/output/LSMS/malawi/nlats.npy")
nlons = np.load("../data/output/LSMS/malawi/nlons.npy")

nlats_min = np.min(nlats)
nlats_max = np.max(nlats)
nlons_min = np.min(nlons)
nlons_max = np.max(nlons)

print("nlats_min: ", nlats_min)
print("nlats_max: ", nlats_max)

print("nlons_min: ", nlons_min)
print("nlons_max: ", nlons_max)

lats_dif = nlats_max - nlats_min
lons_dif = nlons_max - nlons_min
mid_point = geopy.Point(((nlats_max + nlats_min)/2), ((nlons_max + nlons_min)/2))

d = geopy.distance.great_circle(kilometers = 1)
onek_lats = mid_point.latitude-d.destination(point=mid_point, bearing=180).latitude 
onek_lons = mid_point.longitude-d.destination(point=mid_point, bearing=270).longitude

c = 70000

size_y, size_x, depth = clustering.shape
with open(os.path.join(out_dir, country, 'extra_locs_2.csv'), 'w') as f:
    f.write("name,latitude,longitude\n")
    for y in range(1000):
        lat = -1-5*y*onek_lats # going south and onek_lats is positive
        if lat > nlats_min and lat < nlats_max:
            continue
        for x in range(1000):
            lon = 5+5*x*onek_lons # going east
            if lon > nlons_min and lon < nlons_max:
                continue

            col = int(round((lon-pixelWidth/2 - xOrigin) / pixelWidth))
            row = int(round((yOrigin - lat+pixelHeight/2 ) / pixelHeight))

            assert col >= 0
            assert row >= 0

            if data[row][col] > 0 or random.randint(0,30) == 0:
                f.write("%s,%f,%f\n" % (country+"_"+str(c),lat,lon))
                c += 1
                if c % 10 == 0:
                    print(c)