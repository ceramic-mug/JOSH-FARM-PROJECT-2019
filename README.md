# FARM PROJECT 2019 ~ Joshua Eastman

This repository holds an annotated copy of the scripts and workflows that I put together for the PEI 2019 Farm Project. This README file will give you a detailed overview of the work. All files and folders referenced here are within this repository. To access and use the code, simply download this repository as a zip file and follow the steps below for installing python and necessary python modules.

I wish you well!

## Project Arms
1. [Drone Data](##DRONE)
2. [Arable Sensor Data](##ARABLE)
3. Other Data
    - Bugs
    - Soil Nutrients
    - Camera Traps
4. General Processing

Each of these project arms were approached somewhat differently due to differences in the data structures. The Arable Sensor and Drone Imagery data wrangling applications presented in this repository are built around the Arable and FieldAgent specifications, respectively. Bug, soil nutrient, and camera trap data are all held in spreadsheets and so are handled much more simply. We will begin our overview with a detailed description of Arable data handling.

## DRONE
**Drone image processing and data extraction** is the big ticket item. This section describes how to use a GIS application to define areas of interest (AOI) and then use these areas with Sentera FieldAgent NDVI exports to extract matrices of NDVI values. Once you have an extracted NDVI value matrix, you can perform all the numerical analysis you want, such as distribution fitting and differentials over time. Ok, let's get started:

*What you need:*
1. [QGIS](https://qgis.org/en/site/)
2. [Sentera FieldAgent Desktop](https://sentera.com/fieldagent-platform/)
3. The following Python modules:
    - [Rasterio](https://rasterio.readthedocs.io/en/stable/)
    - [Geopandas](http://geopandas.org/)
    - [Numpy](https://numpy.org/)

### FieldAgent Desktop Drone Image Import <a href="https://www.codecogs.com/eqnedit.php?latex=\rightarrow" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\rightarrow" title="\rightarrow" /></a> NDVI Mosaic Output
![FieldAgent](./assets/ClickFieldAgent.png)

## ARABLE
The arable sensors are stationary UFO-shaped things on poles that stick up above crop canopies. They gather atmospheric and spectrometric data and report the data in two resolutions: daily and hourly.

- Link to the Arable website: [https://www.arable.com/](https://www.arable.com/)
- Link to our Arable portal: [https://princeton.arable.com/](https://princeton.arable.com/auth/(auth_view:login))
- Link to the Arable API documentation: [https://pro-soap.cloudvent.net/](https://pro-soap.cloudvent.net/)

I know that last link looks sketchy, and you'll be directed to a really sketchy-looking page that says "FREE PLAN," but that's actually the documentation page. Go ahead and click through the scary blue button and you'll land on the true Arable API documentation site. I used it to build my program, so I know it's the right stuff.

### Getting the Data
- File: [./src/ArableGrep.py](./src/ArableGrep.py)
- Function: Downloads all the hourly, daily, and health data from currently operational Arable sensors and outputs all data to csv files in the [arable_data](./arable_data) directory, labeled by sensor name and data type.

To run this program, navigate to the folder containing this repository using your terminal and run the following command:
```bash
python ./src/ArableGrep.py
```
This will create an "arable_data" directory within the parent directory (same level as "src") and create csv files containing hourly, daily, and health data for all of the sensors within that folder. If any of these csv files already exists, the program will intelligently download all of the most recent data (between the last sync and the present) and append it to the existing csv file.

After running this program, your "arable_data" directory should look something like this: 
<!-- TODO:  add folder output -->
```bash
.
├── arable_data
│   ├── BRF\ Standard\ Tomato_daily.csv
│   ├── BRF\ Standard\ Tomato_health.csv
│   ├── BRF\ Standard\ Tomato_hourly.csv
│   ├── BRF\ Swiss\ Chard_daily.csv
│   ├── BRF\ Swiss\ Chard_health.csv
│   ├── BRF\ Swiss\ Chard_hourly.csv
│   ├── CG\ Cherry\ Tomato_daily.csv
│   ├── CG\ Cherry\ Tomato_health.csv
│   ├── CG\ Cherry\ Tomato_hourly.csv
│   ├── CG\ Standard\ Tomato_daily.csv
│   ├── ... (as many as you have)
└── src
    └── ArableGrep.py
```

**Limitations**
Three known bugs exist in this program:
- **THIS METHOD FOR GETTING THE DATA WORKS AS LONG AS THE SENSOR IS ON AND ACTIVELY REPORTING.** If the sensor is turned off or nonfunctional, THIS METHOD WILL NOT WORK because the sensor will not be in the list of active sensors accessed by this program. But as long as all sensors are on and active, this program will work great.
- When the program appends new data to old csv files, it sometimes adds a blank row between the old and new data.
- The program sometimes creates odd "_hourly", "_daily", and "_health" csv files with no sensor name labels. I believe these correspond to sensors that were operational but which for whatever reason are off or down. Disregard these files. If you can figure out a way to get sensor names for those sensors that are not currently operational, that would be ideal, because then the program could keep writing to those specific files.

### Handling the Data
Downloading the data into an accessible (csv) format is the biggest hurdle. Once it's in the csv format, you can do whatever you want with it. When I did my pretty basic analysis of the Princeton cornfield sensor data, I only used the "*_daily.csv" data and averaged data per drone flight week. I'll discuss that in more detail later.

However, early on in the summer I built a wrangling program with some handy functions that take arable csv files as inputs and output handy data objects. You're welcome to use these functions and dictionaries for your own programs.

- General Wrangling Program: [./src/ArableWrangle.py](./src/ArableWrangle.py)

Not all of the functions in [ArableWrangle](./src/ArableWrangle.py) may be useful to you. I would look through this script and identify things that are helpful, implementing only those aspects that are benificial. This program wasn't cleanly finished and packaged because my work shifted to Princeton cornfield only at the end of the 2019 Farm Project, which meant that handling *all* the Arable data was no longer important to me. Development of this program therefore ground to a halt.

