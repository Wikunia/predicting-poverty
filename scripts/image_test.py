import os
import pandas as pd
from skimage import io
import glob

country = "malawi"

for filepath in glob.glob('../data/output/Daylights/'+country+'/split_complete/**/*.png', recursive=True):
    print(filepath)
    full_image = io.imread(filepath)