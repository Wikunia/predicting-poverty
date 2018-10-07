# Combining satellite imagery and machine learning to predict poverty

Part of this repository is based on [predicting-poverty](https://github.com/nealjean/predicting-poverty).

The data and code in this repository allows users to fully reproduce the results appearing in the main text of the paper **Predicting poverty using daylight satelliteimagery** 

The code works on Python 3.7 and R 3.5.1


## Description of folders

- **data**: Input and output data stored here
- **figures**: Notebooks used to generate Figs. 3-5
- **scripts**: Scripts used to process data
- **model**: Store parameters for trained convolutional neural network

## Packages required

**R**
- R.utils
- magrittr
- foreign
- raster
- readstata13
- plyr
- RColorBrewer
- sp
- lattice
- ggplot2
- grid
- gridExtra

The user can run the following command to automatically install the R packages
```
install.packages(c('R.utils', 'magrittr', 'foreign', 'raster', 'readstata13', 'plyr', 'RColorBrewer', 'sp', 'lattice', 'ggplot2', 'grid', 'gridExtra'), dependencies = T)
```

**Python**
- NumPy
- Pandas
- SciPy
- scikit-learn
- Seaborn
- Geospatial Data Abstraction Library (GDAL)

## Instructions for processing survey data

Due to data access agreements, users need to independently download data files from the World Bank's Living Standards Measurement Surveys websites. These data source requires the user to fill in a Data User Agreement form.

For all data processing scripts, the user needs to set the working directory to the repository `scripts` folder.

1. Download LSMS data
	1. Visit the [host website for the World Bank's LSMS-ISA data](http://microdata.worldbank.org/index.php/catalog/2936):
	2. Download into **data/input/LSMS** the files corresponding to the following country-years:
		- Malawi 2016
		
2. Run the following files in the script folder
	1. DowndloadPublicData.R (run from root folder)
	2. ProcessSurveyData.R  (run from root folder)
	3. save_survey_data.py

## Instructions for extracting satellite image features

1. Download the parameters of the trained CNN model [here](https://www.dropbox.com/s/4cmfgay9gm2fyj6/predicting_poverty_trained.caffemodel?dl=0) and save in the **model** directory.

2. Generate candidate locations to download using `get_image_download_locations.py`. This will generate locations meant to download 1x1 km RGB satellite images of size 400x400 pixels. Locations for 121 images in a 10x10 km area around the cluster is generated. The result of running this is a file for each country, for each dataset named `candidate_download_locs.txt`, in the following format for every line:
    ```
    [image_lat] [image_long] [cluster_lat] [cluster_long]
    ```
    For example, a line in this file may be 
    ```
    4.163456 6.083456 4.123456 6.123456
    ```
    Note that this requires GDAL and previously running `DownloadPublicData.R`.

3. Download all images generated in `candidate_download_locs.csv` using
	[Satellite-Downloader](https://github.com/Wikunia/satellite-downloader). The images should be stored in `data/input/Daylights/COUNTRY/
	**Attention:** A google clould platform registration is needed!

4. Download high resolution nightlight data [here](https://ngdc.noaa.gov/eog/viirs/download_dnb_composites.html) from 2016 (yearly) (ony tile 5 is needed) and save the `vcm-orm-ntl` version in `data/input/Nightlights/2016/south_middle.tif`

5. Run `process_sat_images.py`. This splits the square kilometer images to 500m x 500m images to fit the resolution of the nightlight data and then saves the images in `../data/output/Daylights/malawi/split_complete`. This includes the folders `train`, `test` & `val` with subfolders `NO_LIGHT`, `LOW_LIGHT` & `HIGH_LIGHT` which are the three classes for the first step in our neural network. This set is highley unbalanced but is fully needed for 6. For learning purposes most of the `NO_LIGHT` imagery was removed.

6. Run `sat2poverty.py` to generate a similar data structure for below poverty line and above poverty line.

7. Training and evaluation can be done by using the jupyter notebooks `vgg_nightlights.ipynb` and `vgg_poverty.ipynb`.
    - There is also a copy available for training on Google Colab.