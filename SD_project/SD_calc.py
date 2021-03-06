#!/space/hall3/sitestore/eccc/crd/ccrp/mib001/usr_conda/envs/py3-arc-SCD/bin/python

## Author: Aleksandra Elias Chereque
## Created: Sept 2, 2020
## Last edited: Sept 16, 2020

import xarray as xr
from pathlib import Path

from utils.constants import DOWNLOAD, RUN_SETUP, current_y, CMC_files_loc
from utils.fetch_data import download_monthly_CMC_year, download_CMC_latlon, download_CMC_lsmask, download_CMC_homogmask

from utils.group_CMC_year import raw_to_nc_CMC
from utils.special_group import currenty_raw_to_nc_CMC #this is for data that is for the current year and has different formatting
from utils.CMC_tools import read_lsmask, read_homog_mask

plot_root = Path(__file__).absolute().parent #absolute path to ARC directory
data_root = plot_root.parent / 'data' #directory for final versions of data, used to plot

#set these in utils/constants.py
if DOWNLOAD:
   for year in range(1998, current_y):
      download_monthly_CMC_year(year)
   download_CMC_latlon() 
   download_CMC_lsmask()
   download_CMC_homogmask()
 
if RUN_SETUP:
   for year in range(1998, current_y):
      raw_to_nc_CMC(year)
   currenty_raw_to_nc_CMC(6) #see README 

### Edit:
month_s_of_interest = [3, 4, 5, 6] #list of one or more months, 1=Jan
year_of_interest = 2020
clim_min = 1998
clim_max = 2017
### In this case, March, April, May, June of 2019 will be compared against data from Aug, 1998 to July, 2017

month_names = {'1':'Jan', '2':'Feb', '3':'March', '4':'April', '5':'May', '6': 'June', '7':'July','8':'Aug', '9':'Sept', '10': 'Oct', '11':'Nov', '12':'Dec'}

def load_years(year_min, year_max):
   '''
   Loads snow depth data that falls between Aug of year_min and July of year_max.

   Returns:
      xarray Dataset containing monthly snow depth data.
   '''
   
   years_fnames = [CMC_files_loc+'CMC_sdp_mly_'+str(year)+'.nc' for year in range(year_min, year_max + 1)]
   data = xr.open_mfdataset(years_fnames, combine='by_coords')
   
   condition_1 = (data.time.dt.year == year_min)&(data.time.dt.month > 7) # Selects July and earlier in year_min 
   condition_2 = (data.time.dt.year == year_max)&(data.time.dt.month < 8)
   # Selects August and later in year_max 
   condition_3 = (data.time.dt.year > year_min)&(data.time.dt.year < year_max)
   # Selects all months in intermediate years

   data = data.where(condition_1|condition_2|condition_3, drop=True)
   return data

def calc_mly_clim(data):
   '''
   Returns monthly climatology in xarray Dataset or DataArray (same as input), given data for a period of time. Can be applied to daily data or monthly data, and dates are converted to months. E.g. Coordinate time with value '01-01-2000' will be replaced with coordinate month and value '1'.
   '''

   data = data.groupby('time.month').mean(dim='time')
   return data

def clim_for_month_of_interest(data, month):
   '''
   Calculates monthly climatology using data and selects a particular month. No time coordinate will persist. Returns xarray Dataset or DataArray, same as input.
   '''

   data = calc_mly_clim(data)
   data = data.where(data.month == month, drop=True).isel(month=0)
   return data

def lsmask_data(data):
   mask = read_lsmask()
   return data.where(mask == 1)

def homog_mask_data(data):
   mask = read_homog_mask()
   return data.where(mask == 1)

# Functions with outputs

def calculate_clim(month, year_min, year_max, save = False):
   '''
   Calculates the climatological snow depth for month using the years given. E.g. calculate_clim(2008, 2019, 2) will return the climatological snow depth using Feb 2009, Feb 2008, ..., Feb 2019. E.g. calculate_clim(2008, 2019, 10) will return the climatological snow depth using Oct 2008, Oct 2009, ..., Oct 2018.

   Args:
      month (int): value between 1 and 12, indicating which month to calculate for. E.g. 1 is January.
      year_min (int): months after and including August of year_min will be used to calculate climatology.
      year_max (int): months before and including July of year_max will be used to calculate the climatology.
      save (bool): True if climatology should be saved to NetCDF file, default False

   '''

   data = load_years(year_min, year_max) #load (Aug, year_min)-(July, year_max)
   select_data = clim_for_month_of_interest(data, month)

   select_data = lsmask_data(select_data['sdp']) #apply CMC lsmask to exclude ocean, Greenland
   select_data = homog_mask_data(select_data) #apply homogeneity mask

   if save:
      print('saving climatology')
      select_data.to_netcdf(str(data_root) +'/'+ month_names[str(month)]+'_clim_'+str(year_min)+'_'+str(year_max)+'.nc')

def calculate_anom(month, year_of_interest, clim_years_min, clim_years_max, save = False):
   '''
   Calculate the snow depth anomaly for month in the year given. Climatology is calculated using data between (Aug, clim_years_min)-(July, clim_years_max). 

   Args:
      month (int): value between 1 and 12 to choose month of interest.
      year_of_interest (int): year of interest. E.g. if looking at Feb 2019 against climatology, use month = 2 and year = 2019.
      clim_years_min (int): months after and including August of year_min will be used to calculate climatology.
      clim_years_max (int): months before and including July of year_max will be used to calculate the climatology.
      save (bool): True if anomaly should be saved to NetCDF file, default False
   '''   

   data = load_years(clim_years_min, clim_years_max) #load (Aug, clim_year_min)-(July, clim_year_max)
   clim_for_month = clim_for_month_of_interest(data, month)
   clim_for_month = clim_for_month.where(clim_for_month > 1e-5) #mask out very small values to avoid dividing by zero later

   specific_data = xr.open_mfdataset(CMC_files_loc+'CMC_sdp_mly_'+str(year_of_interest)+'.nc', combine='by_coords')
   specific_data_mly = calc_mly_clim(specific_data)
   select = specific_data_mly.where(specific_data_mly.month == month, drop=True).isel(month=0)

   #key calculation
   percent_anom = ((select - clim_for_month) / clim_for_month) * 100 

   #masking
   masked_anom = lsmask_data(percent_anom['sdp']) #mask out ocean and Greenland
   masked_anom = homog_mask_data(masked_anom) #apply homogeneity mask
 
   if save:
      print('saving anomaly field')
      masked_anom.to_netcdf(str(data_root)+'/anom_SD_'+month_names[str(month)]+str(year_of_interest)+'_clim_'+str(clim_years_min)+'_'+str(clim_years_max)+'.nc')

for i in month_s_of_interest:
   print('Working on month: '+month_names[str(i)])
   calculate_clim(i, clim_min, clim_max, save=True)
   calculate_anom(i, year_of_interest, clim_min, clim_max, save=True)
