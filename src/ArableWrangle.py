# Script for wrangling all of the arable data csv files
# -*- coding: utf-8 -*-

# For handling columns of data numerically
# and performing computations or resizing.
# All-around very handy scientific module
import numpy as np

# Handle the data in tables
# like a spreadsheet
import pandas as pd

# Getting and filtering textual information
import re

# Working with the operating system to do absolute-path direcotory structures
import os

# Get the current absolute path
my_path = os.path.abspath(os.path.dirname(__file__))
output_folder = os.path.join(my_path, "../arable_data/")

# Folder containing all downloaded Arable Data
arable_data = os.path.join(my_path, "../arable_data/")

# Folder containing image outputs of graphs
results_folder = os.path.join(my_path, "../visualization/")

# Necessary Regular Expressions
dayParse = re.compile('(....)-(..)-(..)T(..):(..):(..)Z') # format 'YYYY-MM-DDTHH:MM:SSZ'
fileParse = re.compile('(\w*)\s([\w\s]*)(\s#)?(\d)?_(.*).csv') # (1, farm) (2, crop) (3, space and hashtag) (4, number) (5, data)

# Hash all the sensor names to full farm names for print-handling
# TODO: UPDATE THESE DICTIONARIES AS FARMS/CROPS/ARABLE DATA CHANGES
farms = {'OO': 'Organic Orchards', 'KK': 'Kerr\'s Kornstand', 'BRF': 'Big Red Farm', 'CG': 'Cherry Grove', 'PU': 'Princeton'}
crops = ['Cherry Tomato', 'Corn', 'Standard Tomato', 'Swiss Chard', 'Zucchini']
data_dictHourly = {
    'B1dw': ('W/m$^2$', 'Downwelling Spectrometer Band 1'),
    'B2dw': ('W/m$^2$', 'Downwelling Spectrometer Band 2'),
    'B3dw': ('W/m$^2$', 'Downwelling Spectrometer Band 3'),
    'B4dw': ('W/m$^2$', 'Downwelling Spectrometer Band 4'),
    'B5dw': ('W/m$^2$', 'Downwelling Spectrometer Band 5'),
    'B6dw': ('W/m$^2$', 'Downwelling Spectrometer Band 6'),
    'B7dw': ('W/m$^2$', 'Downwelling Spectrometer Band 7'),
    'B1uw': ('W/m$^2$', 'Upwelling Spectrometer Band 1'),
    'B2uw': ('W/m$^2$', 'Upwelling Spectrometer Band 2'),
    'B3uw': ('W/m$^2$', 'Upwelling Spectrometer Band 3'),
    'B4uw': ('W/m$^2$', 'Upwelling Spectrometer Band 4'),
    'B5uw': ('W/m$^2$', 'Upwelling Spectrometer Band 5'),
    'B6uw': ('W/m$^2$', 'Upwelling Spectrometer Band 6'),
    'B7uw': ('W/m$^2$', 'Upwelling Spectrometer Band 7'),
    'LWdw': ('W/m$^2$', 'Long Wave Downwelling Radiation'),
    'LWuw': ('W/m$^2$', 'Long Wave Upwelling Radiation'),
    'LfW': ('unitless', 'Leaf Wetness'),
    'P': ('kPa', 'Pressure'),
    'SLP': ('kPa', 'Sea Level Pressure'),
    'PARuw': (u'\u03bc'+'Em$^{-2}$s$^{-1}$', 'Upwelling Photosynthetically Active Radiation'),
    'PARdw': (u'\u03bc'+'Em$^{-2}$s$^{-1}$', 'Downwelling Photosynthetically Active Radiation'),
    'RH': ('unitless','Relative Humidity'),
    'SWdw': ('W/m$^2$', 'Downwelling Shortwave Radiation'),
    'SWuw': ('W/m$^2$', 'Upwelling Shortwave Radiation'),
    'Tabove': (u'\N{DEGREE SIGN}'+'C', 'Sky Temperature'),
    'Tair': (u'\N{DEGREE SIGN}'+'C', 'Air Temperature'),
    'Tbelow': (u'\N{DEGREE SIGN}'+'C','Leaf/Ground Temperature'),
    'Tdew': (u'\N{DEGREE SIGN}'+'C', 'Dew Temperature'),
    'prate': ('mm/hr', 'Precipitation Rate'),
    'precip': ('mm', 'Precipitation')
}
data_dictDaily = {
    'CGDD': (u'\N{DEGREE SIGN}'+'C-days', 'Cumulative Growing Degree Days'),
    'Cl': ('unitless', 'Chlorophyll index'),
    'ET': ('mm','Evapotranspiration (ET$_0$)'),
    'GDD': (u'\N{DEGREE SIGN}'+'C-days', 'Growing Degree Days for the Day'),
    'LfAirDelta': (u'\N{DEGREE SIGN}'+'C', 'Leaf to Air temperature difference'),
    'NDVI': ('unitless','Normalized Difference Vegetation Index'),
    'SWdw': ('MJ/m$^2$', 'Downwelling Shortwave Radiation'),
    'maxT': (u'\N{DEGREE SIGN}'+'C', 'Daily maximum temperature'),
    'meanT': (u'\N{DEGREE SIGN}'+'C', 'Daily mean temperature'),
    'minT': (u'\N{DEGREE SIGN}'+'C', 'Daily minimum temperature'),
    'prate': ('mm/day', 'Precipitation rate'),
    'precip': ('mm', 'Precipitation'),
    'SLP': ('kPa', 'Sea Level Pressure'),
    'Kc': ('unitless', 'Crop coefficient K$_c$'),
    'ETc': ('mm', 'Crop Evapotranspiration'),
    'mean_tbelow': ('tbd', 'mean_tbelow'),
    'lfw': ('tbd', 'lfw'),
    'crop_water_demand': ('tbd', 'crop_water_demand'),
    'sunshine_duration': ('tbd', 'sunshine_duration')
}



### Days in each month of 2019 for time conversion
# TODO: THIS IS A POOR IMPLEMENTATION. I did this to compute Julian Date. Turns out,
# the python datetime.timetuple() class has a variable .tm_yday which gives you the Julian
# date. Usage would look like:

# date = datetime.datetime(2019,7,5) <--- datetime object mapping to July 5 2019
# julian_date = date.timetuple().tm_yday <--- integer Julian date of the above

# I highly recommend this ^^^^^^ implementation over my crappy month by month implementation

Jan = 31 # days
Feb = 28 # days
Mar = 31 # days
Apr = 30 # days
May = 31 # days
Jun = 30 # days
Jul = 31 # days
Aug = 31 # days
Sep = 30 # days
Oct = 31 # days
Nov = 30 # days
Dec = 31 # days

# Put it together and what do you get?
days = [Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec]

# Function for outputting a csv containing latitude and longitude
# references for all of the sensors
def latLong():

    latlongs = {'name': [], 'lat': [], 'long': []}
    sensorparse = re.compile('(.*)_(.*)')

    for datafile in os.listdir(arable_data): # look through all the files
        file = fileParse.match(datafile) # match object for group referencing
        if file:
            if file.group(5) == 'daily':
                # For bad cherry tomato naming convention
                df = pd.read_csv(arable_data+datafile)
                lat, long = df['lat'].iloc[-1], df['long'].iloc[-1]
                sensor = sensorparse.match(datafile)
                latlongs['name'].append(sensor.group(1))
                latlongs['lat'].append(lat)
                latlongs['long'].append(long)
                del df

    dfLL = pd.DataFrame(latlongs)
    path = arable_data
    dfLL.to_csv(path_or_buf=path+'latlongs.csv')

# return the list of all the kinds of crops we're studying
def crop_names():
    return crops

# return a Dictionary mapping farm names to colors for consistent styling on visualizations
def farm_styles():
    # for plotting by farm
    farm_clr = {'Organic Orchards': 'green', 'Kerr\'s Kornstand': 'orange', 'Big Red Farm': 'red', 'Cherry Grove': 'violet'}
    return farm_clr

# Return a sorted list of farms in study
# TODO: REMEMBER TO UPDATE THE LIST "farms" AT THE TOP OF THIS PROGRAM FOR FUTURE YEARS
def farm_names():
    return sorted(farms.Values.ToList());

# Return a dictionary containing all the daily data for all farms mapped to specific crops and a sorted list of keys
def allCrop_daily():
    # daily dict looks like ['crop']: ('farm', 'data', datafile)

    daily = {}
    for datafile in os.listdir(arable_data): # look through all the files
        file = fileParse.match(datafile) # match object for group referencing
        if file:
            if file.group(5) == 'daily':
                # For bad cherry tomato naming convention
                if file.group(2) == 'Cherry Tomatoes':
                    daily.setdefault('Cherry Tomato',[]).append((farms[file.group(1)], pd.read_csv(arable_data + datafile)))
                # For PU corn crops
                elif file.group(4) != None:
                    daily.setdefault(file.group(2),[]).append((farms[file.group(1)]+' #'+file.group(4), pd.read_csv(arable_data + datafile)))
                # For everything else
                else:
                    daily.setdefault(file.group(2),[]).append((farms[file.group(1)], pd.read_csv(arable_data + datafile)))

        # daily dict looks like ['crop']: ('farm', 'data', datafile)

    # Get an alphabetically sorted list of keys to return for printing purposes
    keys = list(daily.keys())
    keys = sorted(keys)
    return keys, daily

# Return a dictionary containing all the hourly data for all farms mapped to specific crops and a sorted list of keys
def allCrop_hourly():

    # hourly dict looks like ['crop']: ('farm', 'data', datafile)

    hourly = {}

    for datafile in os.listdir(arable_data): # look through all the files
        file = fileParse.match(datafile) # match object for group referencing
        if file:
            if file.group(5) == 'hourly':
                # For bad cherry tomato naming convention
                if file.group(2) == 'Cherry Tomatoes':
                    hourly.setdefault('Cherry Tomato',[]).append((farms[file.group(1)], pd.read_csv(arable_data + datafile)))
                # For PU corn crops
                elif file.group(4) != None:
                    hourly.setdefault(file.group(2),[]).append((farms[file.group(1)]+' #'+file.group(4), pd.read_csv(arable_data + datafile)))
                # For everything else
                else:
                    hourly.setdefault(file.group(2),[]).append((farms[file.group(1)], pd.read_csv(arable_data + datafile)))

        # hourly dict looks like ['crop']: ('farm', datafile)

    keys = list(hourly.keys())
    keys = sorted(keys)

    return keys, hourly

# Return a dictionary {'sensor': dataframe} for all daily files
# of a specific crop and a sorted list of sensor names (keys)
def byCrop_daily(crop):

    daily = {}
    for datafile in os.listdir(arable_data): # look through all the files
        file = fileParse.match(datafile) # match object for group referencing
        if file:
            if file.group(5) == 'daily':
                if crop == 'Cherry Tomato':
                    # For bad cherry tomato naming convention
                    if file.group(2) == 'Cherry Tomatoes':
                        # Add a key for the sensor if there is none,
                        # and plug the daily datafile in for that sensor
                        daily[farms[file.group(1)]] = pd.read_csv(arable_data + datafile)
                    elif file.group(2) == crop:
                        # Add a key for the sensor if there is none,
                        # and plug the daily datafile in for that sensor
                        daily[farms[file.group(1)]] = pd.read_csv(arable_data + datafile)
                elif crop == 'Corn':
                        # If there's a space hashtag and the crop is 'Corn'
                    if file.group(4) != None and file.group(2) == 'Corn':
                        # Add a key for the sensor if there is none,
                        # and plug the daily datafile in for that sensor
                        daily[farms[file.group(1)] + ' #' + file.group(4)] = pd.read_csv(arable_data + datafile)
                else:
                    # For all other, systematically named crops
                    if file.group(2) == crop:
                        daily[farms[file.group(1)]] = pd.read_csv(arable_data + datafile)

    # The structure of the daily dict looks like:
    # {'sensor': pd.dataframe}

    keys = list(daily.keys())
    keys = sorted(keys)
    return keys, daily


# Return a dictionary {'sensor': dataframe} for all hourly files
# of a specific crop and a sorted list of sensor names (keys)
def byCrop_hourly(crop):

    hourly = {}
    for datafile in os.listdir(arable_data): # look through all the files
        file = fileParse.match(datafile) # match object for group referencing
        if file:
            if file.group(5) == 'hourly':
                if crop == 'Cherry Tomato':
                    # For bad cherry tomato naming convention
                    if file.group(2) == 'Cherry Tomatoes':
                        # Add a key for the sensor if there is none,
                        # and plug the hourly datafile in for that sensor
                        hourly[farms[file.group(1)]] = pd.read_csv(arable_data + datafile)
                    elif file.group(2) == crop:
                        # Add a key for the sensor if there is none,
                        # and plug the hourly datafile in for that sensor
                        hourly[farms[file.group(1)]] = pd.read_csv(arable_data + datafile)
                elif crop == 'Corn':
                        # If there's a space hashtag and the crop is 'Corn'
                    if file.group(4) != None and file.group(2) == 'Corn':
                        # Add a key for the sensor if there is none,
                        # and plug the hourly datafile in for that sensor
                        hourly[farms[file.group(1)] + ' #' + file.group(4)] = pd.read_csv(arable_data + datafile)
                else:
                    # For all other, systematically named crops
                    if file.group(2) == crop:
                        hourly[farms[file.group(1)]] = pd.read_csv(arable_data + datafile)

    # The structure of the hourly dict looks like:
    # {'sensor': pd.dataframe}

    keys = list(hourly.keys())
    keys = sorted(keys)
    return hourly


# Again, sucky implementation. Use datetime.timetuple().tm_yday instead
def daily_to_float(list):

    # Return the nummber of days since January 1 for all
    # date-time values in time column of arable dataFrame

    # list to store row-specific days since jan 1
    dayList = []

    # Do the thing
    for val in list:
        matcher = dayParse.match(val)
        month = int(matcher.group(2))
        day = int(matcher.group(3))

        since = 0
        for i in range(month-1):
            since += days[i]
        since+=day
        dayList.append(since)

    return dayList

# This is kinda cool. Pass in a column of date and time values straight from the arable date column and
# output a float corresponding to the julian date (fractional values for hourly resolution)
def hourly_to_float(list):

    # Where list is a list of timestamps

    timeList = []

    for val in list:
        matcher = dayParse.match(val)
        month = float(matcher.group(2))
        day = float(matcher.group(3))
        hour = float(matcher.group(4))

        since = 0
        for i in range(int(month)-1):
            since += days[i]
        since+=day
        since+= hour/24.0

        timeList.append(since)

    return timeList

# Return the dictionaries mapping the Arable raw column names to descriptive names and units ^^^^ See top of this program
def dictHourly():
    return data_dictHourly

def dictDaily():
    return data_dictDaily
