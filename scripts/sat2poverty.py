import pickle, os, glob, shutil, random
import pandas as pd
import numpy as np
import geopy
import geopy.distance as distance   
import math

out_dir = '../data/output/LSMS/'
country = 'malawi'

clustering = np.load(os.path.join(out_dir, country, 'clustering.npy'))
counting = np.load(os.path.join(out_dir, country, 'counting.npy'))

nlats = np.load("../data/output/LSMS/malawi/nlats.npy")
nlons = np.load("../data/output/LSMS/malawi/nlons.npy")

nlats_min = np.min(nlats)
nlats_max = np.max(nlats)
nlons_min = np.min(nlons)
nlons_max = np.max(nlons)

lats_dif = nlats_max - nlats_min
lons_dif = nlons_max - nlons_min
mid_point = geopy.Point(((nlats_max + nlats_min)/2), ((nlons_max + nlons_min)/2))

d = geopy.distance.great_circle(kilometers = 1)
onek_lats = mid_point.latitude-d.destination(point=mid_point, bearing=180).latitude 
onek_lons = mid_point.longitude-d.destination(point=mid_point, bearing=270).longitude

size_y = math.ceil(lats_dif/onek_lats)
size_x = math.ceil(lons_dif/onek_lons)

df = pd.read_csv(os.path.join(out_dir, country, 'data.csv'), index_col='id')
cdl = pd.read_csv(os.path.join(out_dir, country, 'candidate_download_locs.csv'), index_col='name')

image_dir_out_final = '../data/output/Daylights/'+country+'/split_poverty/'
for cat in ["train", "val", "test"]:
    for intensity_cat in ["NO_POV", "POV"]:
        if not os.path.exists(os.path.join(image_dir_out_final, cat, intensity_cat)):
            os.makedirs(os.path.join(image_dir_out_final, cat, intensity_cat))

counter = 0
med_expenses = np.zeros((size_y, size_x))
for filepath in glob.glob('../data/output/Daylights/'+country+'/split_complete/**/*.png', recursive=True):
    parts = filepath.split('/')
    if counter % 1000 == 0:
        print("Counter: ", counter)
    tvt = parts[-3]
    cat = parts[-2]
    filename = parts[-1]
    _,img_id,img_part = filename[:-4].split("_") # remove png and get parts
    img_id, img_part = int(img_id), int(img_part)
    if img_id >= 60000:
        continue
    row = cdl.loc[country+"_"+str(img_id)]
    lat, lon = row['latitude'], row['longitude']
    y = int((nlats_max-lat)/onek_lats)
    x = int((lon-nlons_min)/onek_lons)
    nhh = counting[y,x]
    hids = list(clustering[y,x,:nhh])
    rows = df.loc[hids]
    med_expense = rows['expagg'].median()
    med_expenses[y,x] = med_expense
    """
    if med_expense < 504200:
        shutil.copy(filepath, '../data/output/Daylights/'+country+'/split_poverty/'+tvt+'/POV/'+filename)
    else:
        shutil.copy(filepath, '../data/output/Daylights/'+country+'/split_poverty/'+tvt+'/NO_POV/'+filename)
    """
    counter += 1

np.save("../data/output/LSMS/malawi/med_expenses", med_expenses)