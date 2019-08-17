# Import arable client handler. 
# The "arable" module is what allows you
# to connect to the arable server.
from arable.client import *

# Write data from devices to csv file
# from Arable API
from io import StringIO

# Handle the data in tables
# like a spreadsheet
import pandas as pd

# Handle the dates and times as
# objects so that we can do
# additions and subtractions of dates
import datetime

# Work with the computer operating system
# to make files and directories as needed
import os

# Build regular expressions that extract
# information from date values and
# allows us to build csv files named
# according to farm and data type
import re

# Read and write csvs to output
# data
import csv

# Get command line arguments
import sys

# Build a regular expression for getting the date and time information
# from the format that arable gives us for date and time
dayParse = re.compile('(....)-(..)-(..)T(..):(..):(..)Z') # format 'YYYY-MM-DDTHH:MM:SSZ'

# Initialize an Arable Client Object to
# interact with the arable server
a = ArableClient()

# Connect to the arable server with Credentials
# (username, password, tenant) #TODO: Describe this in wiki, how to
# do it with command-line arguments
print('Attempting connection to Arable')
try:
    a.connect(sys.argv[1],sys.argv[2],sys.argv[3])
    print('Connected to arable server, user: '+sys.argv[1])
except:
    print('Cannot connect.\nWhen running Arble grep, enter [username] [password] [tenant]')

# Gather a list of all the arable devices connected to our account
sensors = a.devices()

# For outputting csvs in a subdirectory
my_path = os.path.abspath(os.path.dirname(__file__))
output_folder = os.path.join(my_path, "./out/")
# create the folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)


# FUNCTION for appending new data to old csv if the csv already exists
def appendNew(val, filename,i):

    print(filename + ' already exists. Appending data.')

    # print("Appending "+val+" Data to "+filename)

    f = open(output_folder+filename, 'r') # open the csv for reading
    ltString = list(csv.reader(f))[-1][1] # get the last recorded time
    f = open(output_folder+filename, 'r') # open the csv for reading
    ltNum = int(list(csv.reader(f))[-1][0]) # get last row number
    del(f) # close it up

    lt = dayParse.match(ltString) # get values from the last recorded time using the regular expression above ^^^
    start = datetime.datetime(int(lt.group(1)),int(lt.group(2)),int(lt.group(3)),int(lt.group(4))) #Make a datetime object using the last grepped time
    start = start + datetime.timedelta(hours=1) # add an hour
    start = start.strftime("%Y-%m-%d %H:%M:%S") # format for Arable grepping

    now = datetime.datetime.now() # get right now to compute a deltatime
    end = now.strftime("%Y-%m-%d %H:%M:%S") # put now in the right format for Arable

    # Query the Arable server and get all the data from the last time it synced until now
    values = a.query(select='all',
                format='list',
                devices=[a.devices()[i]['name']],
                measure=val,
                order='time',
                end=end,
                start=start)

    # Append new values row by row
    for i in range(len(values['values'])):
        newRow = values['values'][i]
        newRow.insert(0,i+1+ltNum)
        newRowString = ','.join(['' if x == None else str(x) for x in newRow])
        f = open(output_folder+filename,'a')
        f.write('\n'+newRowString)
        f.close()
        del(f)

# FUNCTION for getting hourly data
# appends to present CSV file if exists
# creates new CSV file if doesn't exist
def hourly():

    print('Gathering hourly data:')

    # For all the sensors
    for i in range(len(sensors)):
        # Check to see if a CSV exists:
        ####################################################
        filename = '{}_hourly.csv'.format(a.devices()[i]['location']['name'])
        if os.path.isfile(output_folder + filename):
            appendNew('hourly',filename,i) # run the append function ^^^^
        ####################################################
        else:
            try:
                print("creating new CSVs for:" + a.devices()[i]['location']['name'])

                # how many days worth of data do you want?
                # this is all described in the Arable API: https://pro-soap.cloudvent.net/
                DD = datetime.timedelta(days=90)

                now = datetime.datetime.now()
                sta = now-DD

                #Formatting the date inputs as yyyy-mm-dd hh:mm:ss
                end = now.strftime("%Y-%m-%d %H:%M:%S")
                sta = sta.strftime("%Y-%m-%d %H:%M:%S")

                hourly = a.query(select='all',
                            format='csv',
                            devices=[a.devices()[i]['name']],
                            measure='hourly',
                            order='time',
                            end=end,
                            start=sta)

                hourly = StringIO(hourly)
                hourly = pd.read_csv(hourly, sep=',', error_bad_lines=False)

                # Output to csv file in subdirectory "arable_data"
                hourly.to_csv(output_folder+'{}_hourly.csv'.format(a.devices()[i]['location']['name']))
            # Catch empty data (non-functional devices)
            except:
                pass

def daily():

    print("\nGathering daily data:")

    for i in range(len(sensors)):
        # Getting the daily data
        # Check to see if a CSV exists:
        ####################################################
        filename = '{}_daily.csv'.format(a.devices()[i]['location']['name'])
        if os.path.isfile(output_folder + filename):
            appendNew('daily',filename,i)
        ####################################################
        else:
            try:

                print("creating new CSVs for:" + a.devices()[i]['location']['name'])

                # how many days worth of data do you want?
                DD = datetime.timedelta(days=90)

                now = datetime.datetime.now()
                sta = now-DD

                #Formatting the date inputs as yyyy-mm-dd hh:mm:ss
                end = now.strftime("%Y-%m-%d %H:%M:%S")
                sta = sta.strftime("%Y-%m-%d %H:%M:%S")

                daily = a.query(select='all',
                            format='csv',
                            devices=[a.devices()[i]['name']],
                            measure='daily',
                            order='time',
                            end=end,
                            start=sta)

                daily = StringIO(daily)
                daily = pd.read_csv(daily, sep=',', error_bad_lines=False)

                # Output to csv file in subdirectory "arable_data"
                daily.to_csv(output_folder+'{}_daily.csv'.format(a.devices()[i]['location']['name']))
            # Catch empty data (non-functional devices)
            except:
                pass


def health():
    print("\nGathering health data from:")
    for i in range(len(sensors)):
        # Getting the health data
        # Check to see if a CSV exists:
        ####################################################
        filename = '{}_health.csv'.format(a.devices()[i]['location']['name'])
        if os.path.isfile(output_folder + filename):
            appendNew('health',filename,i)
        ####################################################
        else:
            try:

                print("creating new CSVs for:" + a.devices()[i]['location']['name'])

                # how many days worth of data do you want?
                DD = datetime.timedelta(days=90)

                now = datetime.datetime.now()
                sta = now-DD

                #Formatting the date inputs as yyyy-mm-dd hh:mm:ss
                end = now.strftime("%Y-%m-%d %H:%M:%S")
                sta = sta.strftime("%Y-%m-%d %H:%M:%S")

                health = a.query(select='all',
                            format='csv',
                            devices=[a.devices()[i]['name']],
                            measure='health',
                            order='time',
                            end=end,
                            start=sta)

                health = StringIO(health)
                health = pd.read_csv(health, sep=',', error_bad_lines=False)

                # Output to csv file in subdirectory "arable_data"
                health.to_csv(os.path.join(output_folder,'{}_health.csv'.format(a.devices()[i]['location']['name'])))
            # Catch empty data (non-functional devices)
            except:
                pass

hourly()
daily()
health()

# DEBUG: for some reason, blank name _hourly and _daily csv files
# are being generated on runs. I think these refer to sensors that
# were online but are now offline, where data is associated but not
# accessible by sensor name. There is no documentaion on this within the
# ARABLE API, so let's just not worry about this. If you can
# figure out how to fix this issue, be my guest
