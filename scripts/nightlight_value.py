from osgeo import gdal
import pandas as pd
import os

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

df = pd.read_csv(os.path.join(out_dir, country, 'extra_locs.csv'), sep=',')

points_list = []
for index, row in df.iterrows():
    # if index == 121:
        # break
    center_lat = row['latitude']
    center_lon = row['longitude']

    start = geopy.Point(center_lat, center_lon)
    d = geopy.distance.great_circle(kilometers = 0.353553) # sqrt(0.25^2+0.25^2)
    for r in range(4):
        point = d.destination(point=start, bearing=45+r*90)
        points_list.append((point.longitude,point.latitude))

non_zero_counter = 0
c = 60000
p = 1 
with open(os.path.join(out_dir, country, 'extra_nightlights.csv'), 'w') as f:
    f.write("image,part,lat,lon,intensity\n")
    for point in points_list:
        col = round((point[0]-pixelWidth/2 - xOrigin) / pixelWidth)
        row = round((yOrigin - point[1]+pixelHeight/2 ) / pixelHeight)

        assert col >= 0
        assert row >= 0

        if data[row][col] > 0:
            non_zero_counter += 1
            # print(c,p, row,col, data[row][col])
        
        f.write("%d,%d,%f,%f,%f\n" % (c, p, point[1], point[0], data[row][col]))

        if p == 4:
            p = 0
            c += 1
        p += 1

print("Non zero: ", non_zero_counter)