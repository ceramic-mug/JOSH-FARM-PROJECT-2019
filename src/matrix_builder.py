##########################################
##                                      ##
##     WRITTEN BY JOSHUA EASTMAN        ##
##            summer 2019               ##
##                                      ##
##########################################

import os # for making directories and checking to see if they exist
import glob # for getting filenames and relative paths
import re # for getting text information and filtering
import datetime # for handling date and time data
import numpy as np # for handling arrays of numerical data
import pandas as pd # for building data structures
from skbio.diversity.alpha import shannon # for insect biodiversity quantification
import math # basically just to get euler's number "e"
import seaborn as sns # for visualization
import matplotlib.pyplot as plt # for visualization


# Fill this list with columns of data that you're not
# interested in analyzing

# When I built this program, my lab supervisor
# decided that these Arable sensor measurements
# were not immediately important for analysis:
def dropCols():
    a_colstoDrop = [
        'CGDD_mean',
        'GDD_mean',
        'maxT_mean',
        'minT_mean',
        'Cl_mean',
        'ET_mean',
        'NDVI_mean',
        'precip_mean',
        'mean_tbelow_mean',
        'lfw_mean',
        'crop_water_demand_mean',
        'SLP_mean',
        'Kc_mean',
        'ETc_mean',
        'sunshine_duration_mean'
    ]
    return a_colstoDrop

# This is where you put the dates of your
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

def treatment_dict():
    td = {
        'fence': {
            'yes': 1,
            'no': 0
        },
        'weed': {
            'H': 1,
            'C': 0
        },
        'soil': {
            'S': 1,
            'O': 0
        }
    }

    return td

def arable():
    # I'm going to use arable sensor number 8 as a proxy for the whole field, 
    # since that sensor never went out on us and was never covered by the crop. No plot-by
    # -plot analysis

    # read in 8
    a = pd.read_csv(glob.glob('./dat/PU CORN*8_daily.csv')[0])
    # convert time column
    a['time'] = [datetime.datetime.strptime(x,'%Y-%m-%dT00:00:00Z') for x in a['time']]
    # prep new dataframe
    intervals = pd.DataFrame()
    flights = flight_dates()
    for column in a:
        if column in ['Unnamed: 0','time','device','location','lat','long']:
            continue
        intervals['{}_mean'.format(column)] = np.full(len(flights)-1,np.nan)
        # intervals['{}_var'.format(column)] = np.full(len(flights)-1,np.nan)
        for i in range(len(flights)-1):
            interval = a[(flights[i] <= a['time']) & (a['time'] < flights[i+1])]
            intervals['{}_mean'.format(column)][i] = np.mean(interval[column])
            # intervals['{}_var'.format(column)][i] = np.var(interval[column])
    
    intervals['date']=flights[1::]

    return intervals

def NDVI_treatments():
    n_stats = pd.read_csv('./dat/drone_stats.csv')
    n = n_stats[['date','plot','weed','soil','fence']]
    n['ndvi_mean'] = n_stats['mean']
    td = treatment_dict()
    for column in n:
        if column in ['weed','soil','fence']:
            n[column] = [td[column][x] for x in n[column]]
    n['date'] = [datetime.datetime.strptime(x,'%Y-%m-%d') for x in n['date']]
    n = n[n.date > datetime.datetime(2019,6,21)]
    n = n.reset_index()
    return n

# return a dataframe with the PU soil sample info, broken by plot
def nutrient():
    soil = pd.read_csv('./dat/soil.csv')
    pu_soil = soil[soil['Farm']=='PU']
    pu_soil = pu_soil.drop(columns=['Farm','Crop','Sample Depth (inches)'])
    return pu_soil

# return count of deer in plot per time interval
def deer():

    tp = trap_plot()
    deer = pd.read_csv('./dat/ct.csv')
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
    deer_counts = pd.DataFrame.from_dict(deer_counts_dict)
    return deer_counts

# convert integer plot numbers to the naming convention of bugfile
def bugPlot(i):
    return str(i)+'C'

# bug biodiversity indices calculated using Shannon Entropy:
# http://scikit-bio.org/docs/0.4.2/generated/generated/skbio.diversity.alpha.shannon.html
# https://en.wikipedia.org/wiki/Diversity_index#Shannon_index
def bugs():
    bugs = pd.read_csv('./dat/bugs.csv')
    bugs = bugs[pd.notnull(bugs['Total Count'])] # Let's drop all the rows that don't have counts
    bugs = bugs[pd.notnull(bugs['Sensor Number'])] # Let's drop all the rows that don't have sensor numbers
    bugs['Date']=[datetime.datetime.strptime(x,'%m/%d/%Y') for x in bugs['Date']]
    flights = flight_dates()
    ps = plots()
    dates = []
    big_plots = []
    shannons = []
    for flight in flights:
        interval = bugs[bugs['Date']==flight]
        for p in ps:
            if bugPlot(p) in interval['Sensor Number'].values:
                sub_interval = interval[interval['Sensor Number']==bugPlot(p)]
                big_plots.append(p)
                dates.append(flight)
                shannons.append(shannon(sub_interval['Total Count'].values,base=math.exp(1)))
    bug_dict = {
        'date': dates,
        'plot': big_plots,
        'bug_shannon': shannons
    }
    bug_df = pd.DataFrame.from_dict(bug_dict)
    bug_df.to_csv('./dat/bugFrame.csv',index=False)
    return bug_df

# "a" row needs to be duplicated for every plot for each date
# "s" row needs to be duplicated for every date for each plot
# "b" and "d" rows need to be slotted in where appropriate
def masterFrame():
    n = NDVI_treatments()
    d = deer()
    b = bugs()
    s = nutrient()
    a = arable()
    ps = plots()
    flights = flight_dates()
    dates = []
    plotList = []
    numIntervals = len(flights)-1
    for flight in flights[1::]:
        reps = [flight]*len(ps)
        for rep in reps:
            dates.append(rep.timetuple().tm_yday)
    for i in range(numIntervals):
        for p in ps:
            plotList.append(p) 
    s = pd.concat([s]*5, ignore_index=True)
    a_dict = a.to_dict()
    for key in a_dict.keys():
        tmp = []
        for i in range(numIntervals):
            for _j in range(len(ps)):
                tmp.append(a_dict[key][i])
        a_dict[key] = tmp
    a = pd.DataFrame.from_dict(a_dict)
    a_colstoDrop = dropCols()
    a = a.drop(columns=a_colstoDrop)
    a['plot']=plotList
    s['date']=dates
    master = pd.DataFrame()
    master['date'] = dates
    dfs = [d,b,s,a,n]
    for df in dfs:
        for col in df.columns:
            if not col in ['date','plot','index']:
                master[col] = df[col]
    return master

def masterFrame_minusArable():
    n = NDVI_treatments()
    d = deer()
    b = bugs()
    s = nutrient()
    ps = plots()
    flights = flight_dates()
    dates = []
    plotList = []
    numIntervals = len(flights)-1
    for flight in flights[1::]:
        reps = [flight]*len(ps)
        for rep in reps:
            dates.append(rep.timetuple().tm_yday)
    for i in range(numIntervals):
        for p in ps:
            plotList.append(p) 
    s = pd.concat([s]*5, ignore_index=True)
    s['date']=dates
    master = pd.DataFrame()
    master['date'] = dates
    dfs = [d,b,s,n]
    for df in dfs:
        for col in df.columns:
            if not col in ['date','plot','index']:
                master[col] = df[col]
    return master

def masterFrame_minusSoil():
    n = NDVI_treatments()
    d = deer()
    b = bugs()
    a = arable()
    ps = plots()
    flights = flight_dates()
    dates = []
    plotList = []
    numIntervals = len(flights)-1
    for flight in flights[1::]:
        reps = [flight]*len(ps)
        for rep in reps:
            dates.append(rep.timetuple().tm_yday)
    for i in range(numIntervals):
        for p in ps:
            plotList.append(p) 
    a_dict = a.to_dict()
    for key in a_dict.keys():
        tmp = []
        for i in range(numIntervals):
            for _j in range(len(ps)):
                tmp.append(a_dict[key][i])
        a_dict[key] = tmp
    a = pd.DataFrame.from_dict(a_dict)
    a_colstoDrop = dropCols()
    a = a.drop(columns=a_colstoDrop)
    a['plot']=plotList
    master = pd.DataFrame()
    master['date'] = dates
    dfs = [d,b,a,n]
    for df in dfs:
        for col in df.columns:
            if not col in ['date','plot','index']:
                master[col] = df[col]
    return master

def NDVItreatment_animals_Frame():
    n = NDVI_treatments()
    d = deer()
    b = bugs()
    ps = plots()
    flights = flight_dates()
    dates = []
    plotList = []
    numIntervals = len(flights)-1
    for flight in flights[1::]:
        reps = [flight]*len(ps)
        for rep in reps:
            dates.append(rep.timetuple().tm_yday)
    for i in range(numIntervals):
        for p in ps:
            plotList.append(p)
    master = pd.DataFrame()
    master['date'] = dates
    dfs = [d,b,n]
    for df in dfs:
        for col in df.columns:
            if not col in ['date','plot','index']:
                master[col] = df[col]

    master.to_csv('./dat/ndvi_animals_traetments_frame.csv')
    return master

def inFence():
    n = NDVI_treatments()
    d = deer()
    b = bugs()
    a = arable()
    ps = plots()
    flights = flight_dates()
    dates = []
    plotList = []
    numIntervals = len(flights)-1
    for flight in flights[1::]:
        reps = [flight]*len(ps)
        for rep in reps:
            dates.append(rep.timetuple().tm_yday)
    for i in range(numIntervals):
        for p in ps:
            plotList.append(p) 
    a_dict = a.to_dict()
    for key in a_dict.keys():
        tmp = []
        for i in range(numIntervals):
            for _j in range(len(ps)):
                tmp.append(a_dict[key][i])
        a_dict[key] = tmp
    a = pd.DataFrame.from_dict(a_dict)
    a_colstoDrop = dropCols()
    a = a.drop(columns=a_colstoDrop)
    a['plot']=plotList
    master = pd.DataFrame()
    master['date'] = dates
    master['plot'] = plotList
    dfs = [d,b,a,n]
    for df in dfs:
        for col in df.columns:
            if not col in ['date','plot','index']:
                master[col] = df[col]
    master = master[(master['plot'] >= 3) & (master['plot'] <=6)]
    master = master.drop(columns='plot')
    master.to_csv('./dat/infence_nosoil.csv')
    return master

def synth():
    n = NDVI_treatments()
    d = deer()
    b = bugs()
    a = arable()
    ps = plots()
    flights = flight_dates()
    dates = []
    plotList = []
    numIntervals = len(flights)-1
    for flight in flights[1::]:
        reps = [flight]*len(ps)
        for rep in reps:
            dates.append(rep.timetuple().tm_yday)
    for i in range(numIntervals):
        for p in ps:
            plotList.append(p) 
    a_dict = a.to_dict()
    for key in a_dict.keys():
        tmp = []
        for i in range(numIntervals):
            for _j in range(len(ps)):
                tmp.append(a_dict[key][i])
        a_dict[key] = tmp
    a = pd.DataFrame.from_dict(a_dict)
    a_colstoDrop = dropCols()
    a = a.drop(columns=a_colstoDrop)
    a['plot']=plotList
    master = pd.DataFrame()
    master['date'] = dates
    master['plot'] = plotList
    dfs = [d,b,a,n]
    for df in dfs:
        for col in df.columns:
            if not col in ['date','plot','index']:
                master[col] = df[col]
    master = master[master['plot'] <= 4]
    master = master.drop(columns='plot')
    master.to_csv('./dat/synth.csv')
    return master

# master_frame = masterFrame()
# print('outputting masterframe to ./dat/masterFrame.csv')
# master_frame.to_csv('./dat/masterFrame.csv')

# master_nonArable = masterFrame_minusArable()
# print('outputting Non_arable masterframe to ./dat/masterFrame_nonArable.csv')
# master_nonArable.to_csv('./dat/masterFrame_nonArable.csv')

# master_nonSoil = masterFrame_minusSoil()
# print('outputting Non_soil masterframe to ./dat/masterFrame_nonSoil.csv')
# master_nonSoil.to_csv('./dat/masterFrame_nonSoil.csv')

# NDVItreatment_animals_Frame()

# synth()