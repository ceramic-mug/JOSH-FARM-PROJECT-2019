##########################################
##                                      ##
##     WRITTEN BY JOSHUA EASTMAN        ##
##            summer 2019               ##
##                                      ##
##########################################

#############################################
##                                         ##
##          RUNNING THE PROGRAM            ##
##                                         ##
##  python bugs.py [farm] [sensor_column]  ##
##                                         ##
#############################################

import os # for making directories and checking to see if they exist
import glob # for getting filenames and relative paths
import re # for getting text information and filtering
import datetime # for handling date and time data
import numpy as np # for handling arrays of numerical data
import pandas as pd # for building data structures
from skbio.diversity.alpha import shannon # for insect biodiversity quantification
import math # basically just to get euler's number "e"
import sys # to get command line arguments

# Main function. Takes raw bug spreadsheet and creates csv file with shannon index per date per sensor
def bugs():
    print('SHANNON INDICES for '+farm+'\n----------------------')
    bugs = pd.read_csv(os.path.join(my_path,'./in/'+farm+'_bugs.csv')) # read in the raw csv bug sheet for a farm
    bugs = bugs[pd.notnull(bugs['Total Count'])] # Let's drop all the rows that don't have counts
    bugs = bugs[pd.notnull(bugs.iloc[:,[sc]].values)] # Let's drop all the rows that don't have sensor numbers
    bugs['Date']=[datetime.datetime.strptime(x,'%m/%d/%y') for x in bugs['Date']] # Replace each date with a datetime.datetime object
    dates = [] # initialize empty list to store distinct dates
    trueDates = [] # initialize empty list to store list of dates for each shannon measurement
    sensors = [] # initialize empty list of sensors to store distinct sensors
    shannons = [] # initialize empty list of shannon values to store shannon values to be computed
    bug_finds = [] # initialize empty list of sensors to store sensor for each shannon measurement
    
    # Get the distinct dates and sensors
    for index, row in bugs.iterrows():
        if not row['Date'] in dates:
            dates.append(row['Date'])
        if not row[[sc]].values[0] in sensors:
            sensors.append(row[[sc]].values[0])

    # Go through each date and sensor and compute shannon for each, appending
    # date and sensor to trueDates and big_finds for each shannon computation 
    # so that all three lists will be the same length at the end
    for date in dates:
        print(date.strftime('%Y-%m-%d')+':')
        interval = bugs[bugs['Date']==date] # cut a dataframe that contains only the date we're looking for from the master bugs dataframe
        for sensor in sensors: 
            if [sensor] in interval.iloc[:,[sc]].values:
                sub_interval = interval[interval.iloc[:,[sc]].values==[sensor]] # cut a dataframe out of the date dataframe that contains only the sensor
                s = shannon(sub_interval['Total Count'].values,base=math.exp(1)) # compute shannon index
                shannons.append(s) # append index value to shannons list
                print('   '+str(sensor)+': '+str(s))
                bug_finds.append(sensor) # append sensor to sensor list
                trueDates.append(date) # append date to dates list

    # When we've done all the computations, we want to make a new dataframe
    # out of the three lists we've made
    bug_dict = {
        'date': [x.strftime('%Y-%m-%d') for x in trueDates],
        'sensor': [int(x) if type(x)==float else x for x in bug_finds],
        'bug_shannon': shannons
    }
    bug_df = pd.DataFrame.from_dict(bug_dict)

    # Create the output directory if it doesn't exist
    if not os.path.exists(os.path.join(my_path,'./out')):
        os.makedirs(os.path.join(my_path,'./out'))

    # Output csv to output directory
    bug_df.to_csv(os.path.join(my_path,'./out/'+farm+'_bugShannon.csv'),index=False)
    print('Results output to: '+'/out/'+farm+'_bugShannon.csv')
    return bug_df

#############################################
############### MAIN METHOD #################
#############################################

# Get the farm name
farm = sys.argv[1]

# Get my current path
my_path = os.path.abspath(os.path.dirname(__file__))

# sensor column number
sc = int(sys.argv[2])

bugs()