import numpy as np
import pandas as pd
import os
import math
import matplotlib.pyplot as plt
import pickle

import geopy
import geopy.distance as distance


def retrieve_and_save(countries, fns, out_dir, keys, sample=True):
  for idx, country in enumerate(countries):
    df = pd.read_csv(fns[idx], sep=' ')

    df = df[(df.lat!=0) & (df.lon!=0)]
    df.to_csv(out_dir+country+'/data.csv')

    # download locs
    loc_around = []
    loc_cluster = [] 
    for index, row in df.iterrows():
        center_lat = row['lat']
        center_lon = row['lon']
        
        start = geopy.Point(center_lat, center_lon)
        d = geopy.distance.great_circle(kilometers = 5)
        end_north = d.destination(point=start, bearing=0)
        end_east = d.destination(point=start, bearing=90)
        end_south = d.destination(point=start, bearing=180)
        end_west = d.destination(point=start, bearing=270)
        top_left = geopy.Point(end_north.latitude,end_west.longitude)
        top_right = geopy.Point(end_north.latitude,end_east.longitude)
        bottom_left = geopy.Point(end_south.latitude,end_west.longitude)
        bottom_right = geopy.Point(end_south.latitude,end_east.longitude)

        step_down = (bottom_left.latitude-top_left.latitude)/10
        step_right = (top_right.longitude-top_left.longitude)/10

        for yi in range(11):
            y = top_left.latitude+yi*step_down
            for xi in range(11):
                x = top_left.longitude+xi*step_right
                loc_around.append((y,x))
                loc_cluster.append((row['lat'],row['lon']))

    with open(os.path.join(out_dir, country, 'candidate_download_locs.txt'), 'w') as f:
      for loc, cluster_loc in zip(loc_around, loc_cluster):
        f.write("%f %f %f %f\n" % (loc[0], loc[1], cluster_loc[0], cluster_loc[1]))

    lats = []
    lons = []
    with open(os.path.join(out_dir, country, 'candidate_download_locs.csv'), 'w') as f:
      c = 0
      
      f.write("name,latitude,longitude\n")
      for loc, cluster_loc in zip(loc_around, loc_cluster):
        f.write("%s,%f,%f\n" % (country+"_"+str(c),loc[0],loc[1]))
        c += 1
        lats.append(loc[0])
        lons.append(loc[1])

  # clustering
  # create an array of the size of malawi with a 1km x 1km grid. All households (including the 10km x 10km) are stored
  # then the corresponding coordinates are stored
  nlats = np.array(lats)
  nlons = np.array(lons)
  nlats_min = np.min(nlats)
  nlats_max = np.max(nlats)
  nlons_min = np.min(nlons)
  nlons_max = np.max(nlons)
  np.save(os.path.join(out_dir, country, 'nlats'), nlats)
  np.save(os.path.join(out_dir, country, 'nlons'), nlons)

  print("Lats: %f - %f" % (nlats_min, nlats_max))
  print("Lons: %f - %f" % (nlons_min, nlons_max))
 
  # size of array 
  lats_dif = nlats_max - nlats_min
  lons_dif = nlons_max - nlons_min
  mid_point = geopy.Point(((nlats_max + nlats_min)/2), ((nlons_max + nlons_min)/2))

  d = geopy.distance.great_circle(kilometers = 1)
  onek_lats = mid_point.latitude-d.destination(point=mid_point, bearing=180).latitude 
  onek_lons = mid_point.longitude-d.destination(point=mid_point, bearing=270).longitude
  print("onek_lats: ", onek_lats)
  print("onek_lats: ", onek_lons)

  size_y = math.ceil(lats_dif/onek_lats)
  size_x = math.ceil(lons_dif/onek_lons)
   
  print("size_y: ", size_y)
  print("size_x: ", size_x)

  # get depth
  # how many households can be in a 1km area
  np_counting = np.zeros((size_y, size_x), dtype=np.int)

  for lat,lon in zip(lats, lons):
    y_pos = int((nlats_max-lat)/onek_lats)
    x_pos = int((lon-nlons_min)/onek_lons)
    np_counting[y_pos, x_pos] += 1

  depth = np.max(np_counting)

  np_clustering = -np.ones((size_y, size_x, depth), dtype=np.int)
  print("Depth: ", depth)

  i = 0
  for lat,lon in zip(lats, lons):
    y_pos = int((nlats_max-lat)/onek_lats)
    x_pos = int((lon-nlons_min)/onek_lons)
    d = 0
    while np_clustering[y_pos, x_pos, d] != -1:
      d += 1
    np_clustering[y_pos, x_pos, d] = i//121 # get the household id
    i += 1
    
  np.save(os.path.join(out_dir, country, 'clustering'), np_clustering)
  np.save(os.path.join(out_dir, country, 'counting'), np_counting)

  iid2hh = []
  with open(os.path.join(out_dir, country, 'candidate_download_locs.csv'), 'w') as f:
    f.write("name,latitude,longitude\n")
    c = 0
    for y in range(size_y):
        lat = nlats_max-y*onek_lats # going south and onek_lats is positive
        for x in range(size_x):
            lon = nlons_min+x*onek_lons # going east
            if np_counting[y,x] > 0:
                f.write("%s,%f,%f\n" % (country+"_"+str(c),lat,lon))
                # number of households
                nhh = np_counting[y,x]
                iid2hh.append(list(np_clustering[y,x,:nhh]))
                c += 1
  
  with open(os.path.join(out_dir, country, 'cluster_list'), 'wb') as filehandle:  
    # store the data as binary data stream
    pickle.dump(iid2hh, filehandle)

if __name__ == '__main__':
  ############################
  ############ LSMS ##########
  ############################

  countries = ['malawi']
  fns = ['../data/output/LSMS/Malawi 2016 LSMS (Household).txt']
  out_dir = '../data/output/LSMS/'
  keys = ['lats', 'lons', 'expagg']
  retrieve_and_save(countries, fns, out_dir, keys)
