## Author: Aleksandra Elias Chereque
## Created: July 6, 2020
## Last edited: Aug 13, 2020

import numpy as np
from netCDF4 import Dataset, num2date, date2num
import time as t

from utils.constants import current_y, max_day_downloaded, IMS_files_loc
from utils.IMS_tools import load_latlon, year_len, file_and_date, list_unpacked_days, read_packed, read_unpacked

def raw_to_nc_IMS(year):
   print('starting year '+str(year))
   #open new dataset
   rootgrp = Dataset(IMS_files_loc+'IMS_snowc_'+str(year)+'.nc', 'w', format='NETCDF4')

   #create the dimensions the variables will use using createDimension
   #method of Dataset. Name dimension with str, set size with int.

   if year == current_y:
      time = rootgrp.createDimension('time', max_day_downloaded)
   else:
      time = rootgrp.createDimension('time', year_len(year))

   xc = rootgrp.createDimension('xc', 1024) #x cartesian coordinate
   yc = rootgrp.createDimension('yc', 1024) #y cartesian coordinate

   #use the createVariable method of Dataset, which has two mandatory
   #arguments, variable name and variable datatype. Variable dimensions 
   #are given by a tuple containing the dimension names. Returns an 
   #instance of the Variable class.

   #first define coordinate variables, dimensions which are defined as
   #variables

   times = rootgrp.createVariable('time', 'f8', ('time',))
   lats = rootgrp.createVariable('latitude', 'f4', ('yc', 'xc',))
   lons = rootgrp.createVariable('longitude', 'f4', ('yc','xc',))

   #create variable that is not a dimension
   latlon = rootgrp.createVariable('latitude_longitude', 'i4')
   snowc = rootgrp.createVariable('snowc', 'f4', ('time', 'yc', 'xc',))

   #Set global and variable attributes 

   lats.units = 'degrees_north'
   lats.standard_name = 'latitude'

   lons.units = 'degrees_east'
   lons.standard_name = 'longitude'

   latlon.grid_mapping_name = 'latitude_longitude'
   latlon.longitude_of_prime_meridian = 0.
   latlon.earth_radius = 6371229.

   snowc.short_name = 'snowc'
   snowc.standard_name = 'snow_cover_type'
   snowc.coordinates = 'latitude longitude'
   snowc.grid_mapping = 'latitude_longitude'

   times.units = 'hours since 0001-01-01 00:00:00.0'
   times.calendar = 'gregorian'
   times.standard_name = 'time'

   rootgrp.Conventions = 'CF-1.6'
   rootgrp.description = 'Aggregated IMS snow cover and sea ice for one calendar year'
   rootgrp.history = 'Created ' + t.ctime(t.time())

   times.units = 'hours since 0001-01-01 00:00:00.0'
   times.calendar = 'gregorian'

   #passing data to Variable instances, as one would for an array

   lat_vals, lon_vals = load_latlon()

   lats[:] = lat_vals
   lons[:] = lon_vals

   unpacked_days = list_unpacked_days(year)

   for i in range(1, len(times)+1):
      print(i)
      path, date = file_and_date(i, year)
      if (year == 1997) or (year == 1998):
         if np.isin(i, unpacked_days):
            snowc_vals = read_unpacked(path)
         else:
            snowc_vals = read_packed(path)
      else:
         snowc_vals = read_packed(path)

      snowc[i-1,:,:] = snowc_vals

      #date2num converts datetime objects to numeric values of time in the specified units and calendar

      times[i-1] = date2num(date, units=times.units, calendar=times.calendar)
      
   rootgrp.close()
   print('done year: '+str(year))
