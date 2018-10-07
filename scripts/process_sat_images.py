import numpy as np 
import glob
import shutil
import os
import pandas as pd
from skimage import io
import random

np.random.seed(7)

country = "malawi"
out_dir = '../data/output/LSMS/'
image_dir  = '../data/output/Daylights/malawi'
image_dir_in  = '../data/output/Daylights/malawi/single'
image_dir_out = '../data/output/Daylights/malawi/split'
image_dir_out_final = '../data/output/Daylights/malawi/split_complete'

for top_folders in ["single", "split", "split_complete"]:
    if not os.path.exists(os.path.join(image_dir, top_folders)):
        os.makedirs(os.path.join(image_dir, top_folders))

for intensity_cat in ["NO_LIGHT", "LOW_LIGHT", "HIGH_LIGHT"]:
    if not os.path.exists(os.path.join(image_dir_out, intensity_cat)):
        os.makedirs(os.path.join(image_dir_out, intensity_cat))

for cat in ["train", "val", "test"]:
    for intensity_cat in ["NO_LIGHT", "LOW_LIGHT", "HIGH_LIGHT"]:
        if not os.path.exists(os.path.join(image_dir_out_final, cat, intensity_cat)):
            os.makedirs(os.path.join(image_dir_out_final, cat, intensity_cat))

ci = 0
for filepath in glob.glob('../data/input/Daylights/'+country+'/*.png'):
    path_parts = filepath.split('/') 
    filename = path_parts[-1][:-4]

    # split into 4 parts
    if not os.path.exists('../data/output/Daylights/'+country+'/single/'+filename+'_4.png'):
        print(filepath)
        full_image = io.imread(filepath)
       
        # cut 25 pixel from top and bottom
        processed = full_image[25:-25]
        # io.imsave('../data/output/Daylights/'+country+'/'+filename, processed)


        io.imsave('../data/output/Daylights/'+country+'/single/'+filename+'_1.png', processed[:200,200:])
        io.imsave('../data/output/Daylights/'+country+'/single/'+filename+'_2.png', processed[200:,200:])
        io.imsave('../data/output/Daylights/'+country+'/single/'+filename+'_3.png', processed[200:,:200])
        io.imsave('../data/output/Daylights/'+country+'/single/'+filename+'_4.png', processed[:200,:200])
    ci += 1
    if ci % 1000 == 0:
        print("ci: ", ci)
print("All in output")

df = pd.read_csv(os.path.join(out_dir, country, 'comb_nightlights.csv'), sep=',')

no_counter   = 0
low_counter  = 0
high_counter = 0
for index, row in df.iterrows():
    iid, part, lat, lon, intensity = int(row['image']),int(row['part']),row['lat'],row['lon'],row['intensity']

    if iid % 1000 == 0 and part == 1:
        print("iid: ", iid)

    image_file_in = os.path.join(image_dir_in, country+'_'+str(iid)+"_"+str(part)+".png")
    if intensity == 0:
        intensity_cat = "NO_LIGHT"
        # if random.randint(0,20) != 0:
            # continue
            
        no_counter += 1
    elif intensity <= 0.26:
        intensity_cat = "LOW_LIGHT"
        low_counter += 1
    else:
        intensity_cat = "HIGH_LIGHT"
        high_counter += 1


    image_file_out = os.path.join(image_dir_out, intensity_cat, country+'_'+str(iid)+"_"+str(part)+".png")
    shutil.copy(image_file_in, image_file_out)

print("#No: ", no_counter)
print("#Low: ", low_counter)
print("#High: ", high_counter)
print("Split all in no, low, high")

for intensity_cat in ["NO_LIGHT", "LOW_LIGHT", "HIGH_LIGHT"]:
    files = np.array(glob.glob(os.path.join(image_dir_out, intensity_cat, "*.png")))
    size = len(files)
    indices = np.random.permutation(size)
    training_idx, test_idx = indices[:int(0.7*size)], indices[int(0.7*size):]
    size_test = len(test_idx)
    test_idx, val_idx = test_idx[:int(0.7*size_test)], test_idx[int(0.7*size_test):]
    train_files = files[training_idx]
    val_files = files[val_idx]
    test_files = files[test_idx]


    for fp in train_files:
        fn = fp.split("/")
        fn = fn[-1]
        shutil.move(fp, os.path.join(image_dir_out_final, "train", intensity_cat, fn))

    for fp in val_files:
        fn = fp.split("/")
        fn = fn[-1]
        shutil.move(fp, os.path.join(image_dir_out_final, "val", intensity_cat, fn))

    for fp in test_files:
        fn = fp.split("/")
        fn = fn[-1]
        shutil.move(fp, os.path.join(image_dir_out_final, "test", intensity_cat, fn))