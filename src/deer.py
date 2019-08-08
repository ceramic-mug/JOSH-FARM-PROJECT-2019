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
##            python deer.py               ##
##                                         ##
#############################################

import pandas as pd # tabular data
import numpy as np # computations
import sys # get path
import os # create directories and paths
import datetime # date objects


# Dictionary that maps treatment area to camera id and camera id to treatment areas
def trap_plot():
    tp = {
        1: ['PUC_CT_W','PUC_CT_N'],
        2: ['PUC_CT_W','PUC_CT_N'],
        3: ['PUC_CT_WF','PUC_CT_NF'],
        4: ['PUC_CT_WF','PUC_CT_NF'],
        5: ['PUC_CT_EF','PUC_CT_SF'],
        6: ['PUC_CT_EF','PUC_CT_SF'],
        7: ['PUC_CT_E','PUC_CT_S'],
        8: ['PUC_CT_E','PUC_CT_S'],
        'PUC_CT_W': [1,2],
        'PUC_CT_WF': [3,4],
        'PUC_CT_N': [1,2],
        'PUC_CT_NF': [3,4],
        'PUC_CT_E': [7,8],
        'PUC_CT_EF': [5,6],
        'PUC_CT_S': [7,8],
        'PUC_CT_SF': [5,6]
    }
    return tp

# handler for flight dates
def flight_dates():
    flight_dates = [
        datetime.datetime(2019,6,20),
        datetime.datetime(2019,6,24),
        datetime.datetime(2019,7,1),
        datetime.datetime(2019,7,8),
        datetime.datetime(2019,7,16),
        datetime.datetime(2019,7,22)
    ]
    return flight_dates

# handler for treatment areas
def plots():
    p = [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8
    ]
    return p

# return count of deer in plot per time interval
def deer():

    tp = trap_plot()
    deer = pd.read_csv(os.path.join(my_path,'./in/PU_camTraps.csv'))
    deer = deer[pd.notnull(deer['DATE'])] # Let's drop all the rows that don't have dates
    deer = deer[deer['ANIMAL']=='deer'] # Make sure we only count deer
    deer['DATE'] = [datetime.datetime.strptime(x,'%B %d, %Y') for x in deer['DATE']]
    flights = flight_dates()
    ps = plots()
    date_col = ['']*40
    plot_col = ['']*40
    count_col = ['']*40
    for j in range(len(ps)):
        for i in range(len(flights)-1):
            interval = deer[(flights[i] <= deer['DATE']) & (deer['DATE'] < flights[i+1])]
            index = 8*i+j
            date_col[index]=flights[i+1]
            plot_col[index]=int(ps[j])
            for idd in tp[ps[j]]:
                if isinstance(count_col[index],str):
                    count_col[index]=np.sum(interval[interval['CT_ID']==idd]['QUANTITY'].values)
                    continue
                count_col[index]=count_col[index]+np.sum(interval[interval['CT_ID']==idd]['QUANTITY'].values)
    deer_counts_dict = {
        'date': date_col,
        'plot': plot_col,
        'deer_count': count_col
    }

    # Create the output directory if it doesn't exist
    if not os.path.exists(os.path.join(my_path,'./out')):
        os.makedirs(os.path.join(my_path,'./out'))

    deer_counts = pd.DataFrame.from_dict(deer_counts_dict)
    deer_counts.to_csv(os.path.join(my_path,'./out/PUdeerCounts.csv'),index=False)
    return deer_counts

#############################################
############### MAIN METHOD #################
#############################################

# Get my current path
my_path = os.path.abspath(os.path.dirname(__file__))

deer()