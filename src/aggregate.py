##########################################
##                                      ##
##     WRITTEN BY JOSHUA EASTMAN        ##
##            summer 2019               ##
##                                      ##
##########################################

#################################################
##                                             ##
##             RUNNING THE PROGRAM             ##
##                                             ##
##   python aggregate.py [farm] [conditions]   ##
##                                             ##
##      where [conditions] is a list of        ## 
##      any of the following seperated by      ##
##      spaces:                                ##
##         - "nutrients"                       ##
##         - "bugs"                            ##
##         - "deer"                            ##
##         - "arable"                          ##
##         - "NDVI"                            ##
##                                             ##
##                                             ##
##                  EXAMPLE                    ##
##                                             ##
##    python aggregate.py PU deer NDVI         ##
##                                             ##
##       Outputs csv with those data-types     ##
##       aggregated                            ##
##                                             ##
##                                             ##
#################################################

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
import sys # for command line arguments


def get_farm_name():
    # Grab the pure farm name from the name we pass in
    farm_name_getter = re.compile('(.*)_?.*')
    farm_name = farm_name_getter.match(farm)
    farm_name = farm_name.group(1)

    return farm_name

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

# Return a list of all flight dates pertaining to
# a specific farm
def flight_dates():

    # regular expression for getting dates
    parser = re.compile('.*_(.*)_(.*)_(.*).tif')

    # set path to farm specific drone data
    drone_data = os.path.join(my_path,'../drone/'+farm+'/')

    # quit this program if there is no drone data
    if not os.path.exists(drone_data):
        raise Exception('No drone flight information. Cannot build date list')
    
    # get a list of NDVI flight files to get the flight dates
    flights = glob.glob(drone_data+farm+'_NDVI_*.tif')

    # build a list of flight date objects

    dates = []
    for flight in flights:
        d = parser.match(flight)
        date = datetime.datetime(int(d.group(1)),int(d.group(2)),int(d.group(3)))
        if not date in dates:
            dates.append(date)

    dates.sort()
    return dates

# get a list of sensors from the bug processing output and
def sensors():

    print('Gathering sensor names')

    bugFile = os.path.join(my_path,'../bugs/out/'+farm+'_bugShannon.csv')
    df = pd.read_csv(bugFile)
    sensors = []
    for sensor in df['sensor'].values:
        if not sensor in sensors:
            sensors.append(sensor)
    return sensors

# hard-coded conversion of plot number to camera trap
# and vice-versus for PU 2019 deer observation
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

# another hard-coded dictionary for Princeton 2019
# corn field experiment
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

# Take the first sensor and use that as a proxy for all atmospheric conditions for the farm
def arable():

    print('Gathering Arable data')

    farm_name = get_farm_name()

    # read in the first DAILY arable data file for that farm
    try:
        a = pd.read_csv(glob.glob(os.path.join(my_path,'../arable_data/out/'+farm+'*_daily.csv'))[0])
    except:
        raise Exception('No daily arable data for '+farm+'. Please remove arable from your conditions inputs or download Arable data first.')
    
    # convert time column
    a['time'] = [datetime.datetime.strptime(x,'%Y-%m-%dT00:00:00Z') for x in a['time']]
    
    # prep new dataframe
    intervals = pd.DataFrame()
    flights = flight_dates()
    for column in a:
        if column in ['Unnamed: 0','time','device','location','lat','long']:
            continue
        intervals['{}_mean'.format(column)] = np.full(len(flights)-1,np.nan)
        for i in range(len(flights)-1):
            interval = a[(flights[i] <= a['time']) & (a['time'] < flights[i+1])]
            intervals['{}_mean'.format(column)][i] = np.mean(interval[column])
    
    # set to intervals
    intervals['date']=flights[1::]

    # return interval dataframe
    return intervals

# Get the mean NDVI for each flight for the farm
def NDVI_treatments():

    print('Gathering NDVI data')

    n_stats = pd.read_csv(os.path.join(my_path,'../drone/OUTPUTS/mean_NDVI/'+farm+'_mean_ndvi.csv'))
    n = n_stats[['aoi','id','date','mean_ndvi']]
    n['date'] = [datetime.datetime.strptime(x,'%Y-%m-%d') for x in n['date']]
    n['julian'] = [x.timetuple().tm_yday for x in n['date']]
    n = n.reset_index()
    return n

# return a dataframe with the 2019-07-16 soil sample data
# TODO: CHANGE THE FILE PATH IF YOU WANT TO USE NEW SOIL SAMPLE DATA
def nutrient():

    print('Gathering UniBest AgManager data')

    farm_name = get_farm_name()
    try:
        soil = pd.read_csv(os.path.join(my_path,'../nutrients/soil-2019-07-17.csv'))
        farm_soil = soil[soil['Farm']==farm_name]
        farm_soil = farm_soil.drop(columns=['Farm','Crop','Sample Depth (inches)'])
        return farm_soil
    except:
        print('No data for '+farm_name+' in the given soil nutrient file.')
        return

# return count of deer in plot per time interval
# TODO: Remove conditions if you do sensors at other farms in the future
def deer():

    print('Gathering deer data')

    if farm == 'PU':
        return pd.read_csv(os.path.join(my_path,'../deer/out/PUdeerCounts.csv'))
    print('Deer counts only pertain to PU')
    return

# convert integer plot numbers to the naming convention of bugfile
def bugPlot(i):
    if farm=='PU':
        return str(i)+'C'
    else:
        return i

# bug biodiversity indices calculated using Shannon Entropy:
# http://scikit-bio.org/docs/0.4.2/generated/generated/skbio.diversity.alpha.shannon.html
# https://en.wikipedia.org/wiki/Diversity_index#Shannon_index
def bugs():

    print('Gathering bug data')

    try:
        bug_df = pd.read_csv(os.path.join(my_path,'../bugs/out/'+farm+'_bugShannon.csv'))
        return bug_df
    except:
        print('No bug Shannon dataframe for '+farm+'. Please run bugs.py in the bugs directory to create the dataframe.')

# create a master matrix with the given command line conditions
def masterConditional():
    
    # build a list of all the data types we want to aggregate
    frames = {}
    cases = {}
        # 'nutrients': nutrient(),
        # 'bugs':bugs(),
        # 'arable':arable(),
        # 'deer':deer(),
        # 'NDVI': NDVI_treatments()
    for condition in conditions:
        if condition == 'nutrients':
            cases['nutrients'] = nutrient()
        if condition == 'bugs':
            cases['bugs'] = bugs()
        if condition == 'arable':
            cases['arable'] = arable()
        if condition == 'deer':
            cases['deer'] = deer()
        if condition == 'NDVI':
            cases['NDVI'] = NDVI_treatments()
        if condition in cases.keys():
            df = cases[condition]
            frames[condition] = df
            continue
        print('No data matching condition '+condition+'. Possible conditions are '+cases.keys())
    

    flights = flight_dates()
    dates = []
    real_date = []
    plotList = []
    numIntervals = len(flights)-1
    ps = sensors()

    for flight in flights[1::]:
        reps = [flight]*len(ps)
        for rep in reps:
            # convert date to Julian date
            dates.append(rep.timetuple().tm_yday)
            real_date.append(rep)
    for i in range(numIntervals):
        for p in ps:
            plotList.append(p) 

    master = pd.DataFrame()
    master['julian'] = dates
    master['date'] = real_date
    master['sensor'] = plotList
    
    if 'nutrients' in conditions:
        frames['nutrients'] = pd.concat([frames['nutrients']]*len(flights[1::]), ignore_index=True)
        frames['nutrients']['date']=dates
        for col in frames['nutrients'].columns:
            if not col in ['date','plot','index']:
                master[col] = frames['nutrients'][col]
    if 'bugs' in conditions:
        b = frames['bugs']
        b['julian'] = [datetime.datetime.strptime(x,'%Y-%m-%d').timetuple().tm_yday for x in b['date']]
        shannons = []
        for index, row in master.iterrows():
            shannon = b[(b['julian']==row['julian']) & (b['sensor']==row['sensor'])]
            try:
                shannons.append(shannon['bug_shannon'].values[0])
            except:
                shannons.append(None)
        master['bugs'] = shannons
    if 'arable' in conditions:
        a = frames['arable']
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
        for col in a.columns:
            if not col in ['date','plot','index']:
                master[col] = a[col]
    if 'deer' in conditions:
        master['deer'] = frames['deer']['deer_count'] # The deer dataframe should be built to just stick in
    if 'NDVI' in conditions:
        n = frames['NDVI']
        if farm == 'PU':
            n['sensei'] = [str(x) + 'C' for x in n['id']]
        nd = []
        for index, row in master.iterrows():
            try:
                if farm == 'PU':
                    ap = n[(n['sensei']==row['sensor']) & (n['julian']==row['julian'])]
                    nd.append(ap['mean_ndvi'].values[0])
                else:
                    ap = nd.append(n[(n['id']==row['sensor']) & (n['julian']==row['julian'])])
                    nd.append(ap['mean_ndvi'].values[0])
            except:
                nd.append(np.nan)
        master['NDVI'] = nd
     
    outname = ''
    conditions.sort()
    for condition in conditions:
        outname = outname + '_' + condition

    outpath = os.path.join(my_path, './out/')
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    output = outpath + farm+'_master'+outname + '.csv'

    master.to_csv(output, index=False)


# Get the farm name
farm = sys.argv[1]

# Get my current path
my_path = os.path.abspath(os.path.dirname(__file__))

# Get the desired outputs to frame
conditions = sys.argv[2::]

masterConditional()