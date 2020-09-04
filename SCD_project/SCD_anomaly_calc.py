#!/space/hall3/sitestore/eccc/crd/ccrp/mib001/usr_conda/envs/py3-arc-SCD/bin/python

## Author: Aleksandra Elias Chereque
## Created: July 16, 2020
## Last edited: Aug 13, 2020

import numpy as np
import xarray as xr 
import matplotlib.pylab as plt
import time
from pathlib import Path
from utils.constants import RUN_SETUP, DOWNLOAD_DATA, max_day_change, IMS_DIR, IMS_files_loc, max_day_downloaded, current_y

from utils.fetch_data import download_full_IMS_year, download_IMS_latlon
from utils.group_IMS_year import raw_to_nc_IMS

plot_root = Path(__file__).absolute().parent
data_root = plot_root.parent / 'data'

# Edit: 

## Set the years to be used when calculating the climatology

CLIM_MIN = 1998 #implies beginning from August of this year
CLIM_MAX = 2018 #implies ending in July of this year

## Set the year for which to calculate the SCD anomaly

year_of_interest = [2019, 2020] #implies snow season August 2019-July 2020

# Setup, as set in utils/constants.py:

if DOWNLOAD_DATA:
   print('Setting up IMS data in directory '+str(IMS_DIR))
   for i in range(1998, current_y+1):
      download_full_IMS_year(i)
   download_IMS_latlon()

if RUN_SETUP:
#   for i in range(1998, current_y+1):
   for i in [1998]:
      raw_to_nc_IMS(i)
      print('Raw IMS data has been grouped by year in NetCDF format in directory '+str(IMS_files_loc))

if max_day_change:
   download_full_IMS_year(current_y)
   raw_to_nc_IMS(current_y)

   
# Script:

def load_years(year_min, year_max):
   '''
   Returns IMS snow cover data from (August, year_min)-(July, year_max)

   Args:
      year_min (int): loaded data will be after August of this year. Must be 1998 or later for this dataset.
      year_max (int): loaded data will be before July of this year. 

   Returns: 
      xarray Dataset containing daily snow cover data. 
   '''

   years = [IMS_files_loc+'IMS_snowc_'+str(year)+'.nc' for year in range(year_min, year_max + 1)]

   data = xr.open_mfdataset(years, combine='by_coords')

   condition_1 = (data.time.dt.year == year_min)&(data.time.dt.month > 7)
   condition_2 = (data.time.dt.year == year_max)&(data.time.dt.month < 8)
   condition_3 = (data.time.dt.year > year_min)&(data.time.dt.year < year_max)

   data = data.where(condition_1|condition_2|condition_3, drop=True)

   return data

def calc_seasonal_SCD(data):

   data = data.where(data.snowc == 4)
   data = data.resample(time='6MS', loffset='3M').count() 
   data = data.groupby('time.season').mean() #autumn snowfall is labelled by season = 'SON', spring SCD by 'MAM'

   return data

def clim_to_netcdf(clim_year_min, clim_year_max):
   '''
   Calculates climatologial SCD for two seasons and writes to NetCDF.

   Args: 
      clim_year_min (int): data after August of clim_year_min will be used to calculate the climatology
      clim_year_max (int): data up to July of clim_year_max will be used to calculate the climatology
   '''

   data = load_years(clim_year_min, clim_year_max)
   clim_SCD = calc_seasonal_SCD(data)

   cut_data = clim_SCD.snowc[:, 158:1024-158+1, 158:1024-158+1]
   file_name = 'clim_SCD_'+str(clim_year_min)+'_'+str(clim_year_max)+'.nc'
   cut_data.to_netcdf(data_root / file_name)

   
def anom_to_netcdf(year, clim_year_min, clim_year_max):
   ''' 
   Saves xarray Dataarray as netcdf containing count of days with snow cover in "year" of interest. 

   Args:
      year (tuple of int): year of interest, e.g. [2017, 2018] for Aug 2017-July 2018 snow season.
      clim_year_min (int): data after August of clim_year_min will be used to calculate the climatology
      clim_year_max (int): data up to July of clim_year_max will be used to calculate the climatology
   '''
   clim_data = load_years(clim_year_min, clim_year_max) 
   clim_seasonal_SCD = calc_seasonal_SCD(clim_data)

   data = load_years(year[0], year[1])
   current_SCD = calc_seasonal_SCD(data)

   anom = current_SCD - clim_seasonal_SCD
   #cut out area that does not have masked lat/lon values

   cut_data = anom.snowc[:, 158:1024-158+1, 158:1024-158+1]
   file_name = 'anom_SCD_'+str(year[0])+'_to_'+str(year[1])+'.nc'
   cut_data.to_netcdf(data_root / file_name)

clim_to_netcdf(CLIM_MIN, CLIM_MAX)
anom_to_netcdf(year_of_interest, CLIM_MIN, CLIM_MAX)
