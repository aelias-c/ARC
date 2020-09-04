## Author: Aleksandra Elias Chereque
## Created: July 20, 2020
## Last edited: Sept 2, 2020

import numpy as np
from netCDF4 import Dataset, date2num
import time as t
from datetime import datetime, timedelta

from utils.constants import CMC_DIR, CMC_files_loc
from utils.CMC_tools import load_latlon, read_mly_data

def raw_to_nc_CMC(year):
   rootgrp = Dataset(CMC_files_loc+'CMC_sdp_mly_'+str(year)+'.nc', 'w', format='NETCDF4')

   if year == 1998:
      time = rootgrp.createDimension('time', 5) #only data for Aug-Dec available for 1998
   else:
      time = rootgrp.createDimension('time', 12)

   xc = rootgrp.createDimension('xc', 706) #x cartesian coordinate
   yc = rootgrp.createDimension('yc', 706) #y cartesian coordinate

   times = rootgrp.createVariable('time', 'f8', ('time',))
   lats = rootgrp.createVariable('latitude', 'f4', ('yc', 'xc',))
   lons = rootgrp.createVariable('longitude', 'f4', ('yc','xc',))

   #create variable that is not a dimension
   latlon = rootgrp.createVariable('latitude_longitude', 'i4')
   sdp = rootgrp.createVariable('sdp', 'f4', ('time', 'yc', 'xc',))

   #Set global and variable attributes 

   rootgrp.Conventions = 'CF-1.6'
   rootgrp.description = 'Aggregated monthly NH CMC snow depth for one calendar year'
   rootgrp.history = 'Created ' + t.ctime(t.time())

   lats.units = 'degrees_north'
   lats.standard_name = 'latitude'

   lons.units = 'degrees_east'
   lons.standard_name = 'longitude'

   latlon.grid_mapping_name = 'latitude_longitude'
   latlon.longitude_of_prime_meridian = 0.
   latlon.earth_radius = 6371229.

   sdp.units = 'cm'
   sdp.valid_min = 0.
   sdp.short_name = 'sdp'
   sdp.standard_name = 'surface_snow_thickness'
   sdp.coordinates = 'latitude longitude'
   sdp.grid_mapping = 'latitude_longitude'

   times.units = 'hours since 0001-01-01 00:00:00.0'
   times.calendar = 'gregorian'
   times.standard_name = 'time'

   #passing data to Variable instances, as one would for an array

   lat_vals, lon_vals = load_latlon()

   lats[:] = lat_vals
   lons[:] = lon_vals

   path = 'cmc_sdepth_mly_'+str(year)+'_v01.2.zip'
   sdp[:,:,:] = read_mly_data(CMC_DIR, path, months = len(times))
   
   for i in range(1, len(times)+1):
      if year == 1998:
         date = datetime(year, i+7, 1) #only last 5 months of 1998 are available
      else: 
         date = datetime(year, i, 1)

      #date2num converts datetime objects to numeric values of time in the specified units and calendar
      times[i-1] = date2num(date, units=times.units, calendar=times.calendar)

   rootgrp.close()
   print('done year: '+str(year))
