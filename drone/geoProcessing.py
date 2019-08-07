##########################################
##                                      ##
##     WRITTEN BY JOSHUA EASTMAN        ##
##            summer 2019               ##
##                                      ##
##########################################

##########################################
##                                      ##
##          RUNNING THE PROGRAM         ##
##                                      ##
##    python geoProcessing.py [farm]    ##
##                                      ##
##########################################
##                                      ##
##                                      ##
##      NECESSARY FOLDER STRUCTURE      ##
##       and FILE NAME CONVENTIONS      ##
##                                      ##
##     parent                           ##
##       |- geoProcessing.py            ##
##       |- farm1_NDVI_YYYY_MM_DD.tif   ##
##       |- farm1_RGB_YYYY_MM_DD.tif    ##        
##       |- farm2_NDVI_YYYY_MM_DD.tif   ##
##       |- farm2_RGB_YYYY_MM_DD.tif    ##    
##       |- AOI                         ##
##           |- farm1.shp               ##
##           |- farm2.shp               ##
##       etc                            ##
##                                      ##
##########################################

####### MODULES #########

# For handling command-line arguments
import sys

# For going through files and getting all those with a certain specification
import glob

# For handling the GeoTIFF files
import rasterio

# For visualizing our GeoTIFFs
from rasterio.plot import show

# For building spreadsheet-like dataframes
import pandas as pd

# For performing computations and such
import numpy as np

# For handlish shapefile AOI layers
import geopandas as gpd

# For text processing to get what we want out of Strings
import re

# For date and time handling and computing
import datetime

# For data visualization
import matplotlib.pyplot as plt

# For tuning input GeoTIFFs to AOI layers
from shapely.geometry import mapping
from rasterio.plot import plotting_extent
from rasterio.mask import mask

# For traversing and interacting with folder structure
import os

# For more data visualization
import seaborn as sns
sns.set(rc={'figure.figsize':(6,6)})

#######################################################################
############## Lasciate ogne speranza, voi ch'intrate #################
#######################################################################



# Take in a filename with the correct naming convention and
# return a datetime object of the corresponding date
def dayParse(filename):
    parser = re.compile('.*_(.*)_(.*)_(.*).tif')

    try:
        date = parser.match(filename)
    except:
        raise Exception('Filename not properly formatted. Please conclude NDVI and RGB filenames with _YYYY_MM_DD.tif')

    return datetime.datetime(int(date.group(1)),int(date.group(2)),int(date.group(3)))

def getAOIs():
    try:
        aois = gpd.read_file(os.path.join(my_path,'./AOI/'+farm+'_AOI.shp'))
    except:
        raise Exception('No shapefile for '+farm+' in AOI folder')

    return aois

def getFields():
    # Check to see if defining shapefile layer exists
    fields_shapes = glob.glob('./FIELD/'+farm+'_field.shp')

    # If none exist, exit
    if len(fields_shapes) < 1:
        print('No field-defining shapefiles found. Continuing other processes')
        return

    return gpd.read_file(fields_shapes[0])

# Go through all the FieldAgent NDVI GeoTIFFs for this farm and output new TIFFs with pure NDVI pixel data [-1, 1]
def makeNDVI():

    # outside NDVI range
    nodataval = 2

    # List to hold all flight dates for this farm
    dates = []

    # Run through the all the ndvi mosaics for this farm
    for tif in ndvi_r:
        with rasterio.open(tif) as src:

            # record the date
            date = dayParse(tif)
            dates.append(date)

            # compute NDVI
            print('Computing NDVI for '+farm+': '+date.strftime('%Y-%m-%d'))
            intensity = src.read(1,masked=True).astype(np.float)
            NDVI = -(((intensity-255/2)/255)*2) # because each of the three channels is equal since this is a grayscale

            # fix metadata
            NDVI = np.ma.filled(NDVI,fill_value=nodataval)
            NDVI_meta = src.meta.copy()
            NDVI_meta.update({'nodata':nodataval})
            NDVI_meta.update({'count':1})
            NDVI_meta.update({'dtype':'float64'})

            # output file
            filename = farm+'_trueNDVI_{}.tif'.format(date.strftime('%Y_%m_%d'))
            out_path = output_dict['wholefield_ndvi']+filename

            print('Writing whole field: '+out_path)
            with rasterio.open(out_path, 'w', **NDVI_meta) as out:
                out.write(NDVI, 1)
    
    print('Finished converting Sentera exports to true NDVI raster GeoTIFFs')

    # Return the list of dates to know how many files we are dealing with and 
    # to have handles for each of them based on their output names
    return dates

# Input a list of dates and create aoi-specific ndvi csv files
# and ndvi cropped GeoTIFFs for each
def aoiNDVI(dates):

    nodataval = 2

    bigPapaNDVI = farm + '_bigPapa.csv'
    bigPout = output_dict['ndvi_csv']+bigPapaNDVI
    with open(bigPout,'w') as DUDE:
        DUDE.write('aoi,date,val')

    aois = getAOIs()

    # Go through all of the time steps
    for date in dates:

        # Input filename, produced using makeNDVI()
        NDVI_in = output_dict['wholefield_ndvi']+farm+'_trueNDVI_{}.tif'.format(date.strftime('%Y_%m_%d'))

        # get NDVI for each aoi seprately
        with rasterio.open(NDVI_in) as NDVI_true:

            # crop by aoi
            for index, row in aois.iterrows():

                # Make the polygon definition into something we can use
                poly = mapping(row['geometry'])
                ndvi_mask, ndvi_affine = mask(NDVI_true,[poly],crop=True)

                output = output_dict['ndvi_csv']+farm+'_aoi_ndvi_'+row['Kind']+'_'+date.strftime('%Y-%m-%d')+'.csv'

                # Output to individual files
                print('Writing NDVI pixel data to csv:\n    '+output)

                vals = ndvi_mask.flatten('F')
                vals = vals[vals != 2.]
                np.savetxt(output,vals,delimiter=",")

                print('Appending to ' + farm + ' Bigpapa: '+bigPout)
                
                # Append to by-farm Bigpapa
                with open(bigPout,'a') as bigBoy:
                    for val in vals:
                        newline ='\n'+row['Kind']+','+date.strftime('%Y-%m-%d')+','+str(val)
                        bigBoy.write(newline)

                # Append mean to mean_csv
                print('Appending mean to mean NDVI master csv')
                meanNDVI(vals,row,date)

                del(vals)

                # fix metadata
                ndvi_mask = np.ma.filled(ndvi_mask,fill_value=nodataval)
                ndvi_mask_meta = NDVI_true.meta.copy()
                ndvi_mask_meta.update({'nodata':nodataval,
                                    'transform': ndvi_affine,
                                    'height':ndvi_mask.shape[1], # ndarray rows
                                    'width':ndvi_mask.shape[2]}) # ndarray cols

                mask_out = farm+'_trueNDVI_{}_{}.tif'.format(row['Kind'],date.strftime('%Y-%m-%d'))
                out_path = output_dict['treatment_ndvi']+mask_out

                print('Building tiff for '+farm+' '+row['Kind']+': '+out_path)

                with rasterio.open(out_path, 'w', **ndvi_mask_meta) as out:
                    out.write(ndvi_mask)

                del(ndvi_mask,ndvi_affine,ndvi_mask_meta)

# Take the true NDVI output that's the size of the Sentera FieldAgent output
# and crop it to defined "field" sections
def field_ndviCROP(dates):

    # Get the field shapefiles
    fields_shapes = getFields()

    nodataval = 2

    for date in dates:
        # Input filename, produced using makeNDVI()
        NDVI_in = output_dict['wholefield_ndvi']+farm+'_trueNDVI_{}.tif'.format(date.strftime('%Y_%m_%d'))
        with rasterio.open(NDVI_in) as NDVI_true:
            for i in range(len(fields_shapes)):

                field_mask, field_affine = mask(NDVI_true,[fields_shapes['geometry'][i]],crop=True)
                field_mask = np.ma.filled(field_mask,fill_value=nodataval)
                field_mask_meta = NDVI_true.meta.copy()
                field_mask_meta.update({'nodata':nodataval,
                                        'transform': field_affine,
                                        'height':field_mask.shape[1], # ndarray rows
                                        'width':field_mask.shape[2]}) # ndarray cols

                mask_out = farm+str(i)+'_trueNDVI_field_{}.tif'.format(date.strftime('%Y-%m-%d'))
                field_out = output_dict['field_ndvi']+mask_out

                print('Writing field true NDVI tif: ' + field_out)

                with rasterio.open(field_out, 'w', **field_mask_meta) as out:
                    out.write(field_mask)


# Take Senetera output RGB mosaic and crop it to defined "field" sections
def field_rgbCrop(dates):

    # Get the field shapefiles
    fields_shapes = getFields()

    for date in dates:
        with rasterio.open(os.path.join(my_path,farm+'/'+farm+'_RGB_'+date.strftime('%Y_%m_%d')+'.tif')) as rgb:
            for i in range(len(fields_shapes)):

                rgb_mask, rgb_affine = mask(rgb,[fields_shapes['geometry'][i]],crop=True)

                rgb_mask = np.ma.filled(rgb_mask)
                rgb_mask_meta = rgb.meta.copy()
                rgb_mask_meta.update({'transform': rgb_affine,
                                        'height':rgb_mask.shape[1], # ndarray rows
                                        'width':rgb_mask.shape[2]}) # ndarray cols

                rgb_out = farm+str(i)+'_rgb_field_{}.tif'.format(date.strftime('%Y-%m-%d'))
                field_out = output_dict['field_rgb']+rgb_out

                print('Writing field rgb tif: ' + field_out)

                with rasterio.open(field_out, 'w', **rgb_mask_meta) as out:
                    out.write(rgb_mask)


# crop and output aoi NDVI GeoTIFFs for graphics production
def aoi_ndviCROP(dates):

    aois = getAOIs()

    for date in dates:
        print('Cropping ndvi by kind : '+date.strftime('%Y-%m-%d'))
        with rasterio.open(os.path.join(my_path,farm+'/'+farm+'_NDVI_'+date.strftime('%Y_%m_%d')+'.tif')) as src_n:
            for index, row in aois.iterrows():
                nd_mask, nd_affine = mask(src_n,[row['geometry']],crop=True)
                nd_mask_meta = src_n.meta.copy()

                nd_mask_meta.update({'transform': nd_affine,
                                    'height':nd_mask.shape[1], # ndarray rows
                                    'width':nd_mask.shape[2]}) # ndarray cols

                nd_out = farm+'_NDVI_'+row['Kind']+'_cropped_{}.tif'.format(date.strftime('%Y-%m-%d'))

                nd_out_path = output_dict['treatment_ndvi']+nd_out

                with rasterio.open(nd_out_path, 'w', **nd_mask_meta) as out:
                    out.write(nd_mask)
                    print('Outputting ndvi: ' + nd_out_path)

# crop and output aoi RGB GeoTIFFs for graphics production
def aoi_rgbCROP(dates):

    aois = getAOIs()

    for i in range(len(dates)):
        print('Cropping rgb by kind : '+dates[i].strftime('%Y-%m-%d'))
        with rasterio.open(rgb_r[i]) as src_r:
            for index, row in aois.iterrows():
                rgb_mask, rgb_affine = mask(src_r,[row['geometry']],crop=True)
                rgb_mask_meta = src_r.meta.copy()
                rgb_mask_meta.update({'transform': rgb_affine,
                                    'height':rgb_mask.shape[1], # ndarray rows
                                    'width':rgb_mask.shape[2]}) # ndarray cols

                rgb_out = farm+'_RGB_'+row['Kind']+'_cropped_{}.tif'.format(dates[i].strftime('%Y-%m-%d'))

                rgb_out_path = output_dict['treatment_rgb']+rgb_out

                with rasterio.open(rgb_out_path, 'w', **rgb_mask_meta) as out:
                    out.write(rgb_mask)
                    print('Outputting rgb: ' + rgb_out_path)

# Creates one master csv that contains the average NDVI 
# value for each aoi at each time step
def meanNDVI(vals,row,date):

    # Append to by-farm mean
    with open(mNDVI,'a') as YES:
        newline ='\n'+row['Kind']+','+date.strftime('%Y-%m-%d')+','+str(np.mean(vals))
        YES.write(newline)
    
    return

# Function to call all the above functions in proper order
def allTheThings():
    dates = makeNDVI()
    field_ndviCROP(dates)
    field_rgbCrop(dates)
    aoi_ndviCROP(dates)
    aoi_rgbCROP(dates)
    aoiNDVI(dates)

#############################################
############### MAIN METHOD #################
#############################################

# Get the farm name
farm = sys.argv[1]

# Get my current path
my_path = os.path.abspath(os.path.dirname(__file__))

# handle ndvi mosaic GeoTIFFs
ndvi_r = glob.glob(os.path.join(my_path,'./'+farm+'/'+farm+'_NDVI*.tif'))

# kill the program if we don't have what we need
if len(ndvi_r) < 1:
    raise Exception('No NDVI GeoTIFFs corresponding to ' + farm + ' can be found. Is your file structure correct?')

# handle rgb mosaic GeoTIFFs
rgb_r = glob.glob(os.path.join(my_path,'./'+farm+'/'+farm+'_RGB*.tif'))

if len(rgb_r) < 1:
    raise Exception('No RGB GeoTIFFs corresponding to ' + farm + ' can be found. Is your file structure correct?')

# List directories for storing outputs
output_dict = {
    'field_ndvi': os.path.join(my_path, './OUTPUTS/NDVI_Field_tiffs/'+farm+'/'),
    'field_rgb': os.path.join(my_path, './OUTPUTS/RGB_Field_tiffs/'+farm+'/'),
    'wholefield_ndvi': os.path.join(my_path, './OUTPUTS/NDVI_WholeField_tiffs/'+farm+'/'),
    'treatment_ndvi': os.path.join(my_path, './OUTPUTS/NDVI_AOI_tiffs/'+farm+'/'),
    'treatment_rgb': os.path.join(my_path, './OUTPUTS/RGB_AOI_tiffs/'+farm+'/'),
    'ndvi_csv': os.path.join(my_path, './OUTPUTS/NDVI_csv/'+farm+'/'),
    'mean_csv': os.path.join(my_path, './OUTPUTS/mean_NDVI/')
}

# Create output parent folder
if not os.path.exists(os.path.join(my_path,'./OUTPUTS/')):
    os.makedirs(os.path.join(my_path,'./OUTPUTS/'))

# Create output paths above if they dont exist
for key in output_dict.keys():
    path = output_dict[key]
    if not os.path.exists(path):
        os.makedirs(path)

mNDVI = output_dict['mean_csv']+farm+'_mean_ndvi.csv'
with open(mNDVI,'w') as DUDE:
    DUDE.write('aoi,date,mean_ndvi')

# do the things!
allTheThings()