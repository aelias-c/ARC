## Author: Aleksandra Elias Chereque
## Created: July 3, 2020
## Last edited: Aug 13, 2020

import numpy as np
import os 
from datetime import datetime, timedelta
import gzip
import re 

from utils.constants import IMS_DIR, EMPTY_PATH
#EMPTY_PATH is to a zipped txt file created by saving a 1024x1024 array of zeros to file

#missing days come from G02156_missing_files.txt provided with IMS data
missing = {'1997': [46, 238], '1998': [51, 291], '1999': [], 
            '2000': [21, 226, 291], '2001': [221, 254, 275, 350], 
            '2002': [], '2003': [342], '2004': [], 
            '2005': [155, 185, 284, 321], '2006': [62, 185, 186, 187, 188],
            '2007': [72, 73], '2008': [71], '2009': [85], '2010': [],
            '2011': [], '2012': [137], '2013': [], '2014': [293, 294, 295], 
            '2015': [109], '2016': [], '2017': [308, 309], '2018': [], 
            '2019': [], '2020': []}

#unpacked days come from unpacked_files.txt provided with IMS data      
unpacked = {'1997': [[38, 45], [47, 137], [139, 154], [156, 160], 
            [162, 162], [165, 165], [168, 168], [170, 170], [174, 175], 
            [177, 177], [179, 179], [182, 185], [188], [192, 192], 
            [195, 197], [199, 200], [202, 202], [206, 207], [209, 210], 
            [212, 214], [219, 219], [221, 222], [226, 226], [228, 232], 
            [235, 237], [251, 251], [254, 268], [272, 278], [280, 281], 
            [285, 286], [288, 289], [291, 291], [293, 365]], 
            '1998': [[1, 144], [146, 148], [151, 157], [159, 253], 
            [271, 271], [274, 290]], '1999': [], '2000': [], '2001': [],
            '2002': [], '2003': [], '2004': [], '2005': [], '2006': [],
            '2007': [], '2008': [], '2009': [], '2010': [], '2011': [], 
            '2012': [], '2013': [], '2014': [], '2015': [], '2016': [],
            '2017': [], '2018': [], '2019': [], '2020': []} 

def year_len(year):
   if year % 4 == 0:
      return 366
   else:
      return 365
   
def list_unpacked_days(year):
   days = []
   for i in range(len(unpacked[str(year)])):
      group = np.arange(unpacked[str(year)][i][0], unpacked[str(year)][i][1]+1)
      for d in group:
         days.append(d)
   print('Unpacked days in '+str(year)+':', days)
   return days

def load_latlon():
   '''
   Loads auxiliary coordinate data from IMS dataset into 2D arrays (latitude
   and longitude). For 24 km data, these are provided in flat binary 4-byte,
   floating point values in little-endian byte order -> dtype = '<f4'. 
   
   Arrays are reflected vertically to match the ASCII text data files 
   entry-by-entry.
   '''

   lon_data = np.fromfile(IMS_DIR+'imslon_24km.bin', dtype='<f4', count=-1, sep='')
   lon_data = np.reshape(lon_data, (1024,1024))
   lon_data = np.flip(lon_data, axis=0)

   lat_data = np.fromfile(IMS_DIR+'imslat_24km.bin', dtype='<f4', count=-1, sep='')
   lat_data = np.reshape(lat_data, (1024,1024))
   lat_data = np.flip(lat_data, axis=0)

   return lat_data, lon_data

def file_and_date(true_dayofyear, year):
   '''
   Returns appropriate IMS file path and the correct date associated with inputs.

   Args:
      true_dayofyear (int): The day of the year of interest, counting from 1 on January 1, XXXX.
      year (int): The year of interest.
   
   Returns:
      pathname for the file associated with true_dayofyear of year, taking into 
      account IMS dataset naming conventions.
   '''
   
   date = datetime(year, 1, 1)+timedelta(true_dayofyear-1)
   nextday = date+timedelta(1)
   
   #define v1.3 path using the next day's day of year - does it exist?
   path_next_1_3 = IMS_DIR+str(nextday.year)+'/'+'ims'+str(nextday.year)+str(nextday.strftime('%j'))+'_24km_v1.3.asc.gz'
   nextday_not_missing = np.isin(int(nextday.strftime('%j')), missing[str(nextday.year)], invert=True)
   if nextday_not_missing and os.path.exists(path_next_1_3):
      #yes, so this is the right path for the date given
      return path_next_1_3, date
   else:
      #no, so try looking for a file that is NOT v1.3 with the true day of year - does it exist?
      path_1_3 = IMS_DIR+str(year)+'/'+'ims'+str(year)+str('%03d' % true_dayofyear)+'_24km_v1.3.asc.gz'
      day_not_missing = np.isin(true_dayofyear, missing[str(year)], invert=True)
      v1_3_not_exist = not os.path.exists(path_1_3)
      if day_not_missing and v1_3_not_exist:
         #yes, so return the path to this file
         true_path = [IMS_DIR+str(year)+'/'+fn for fn in os.listdir(IMS_DIR+str(year)+'/') if str('%03d' % true_dayofyear)+'_' in fn][0]
         return true_path, date
      else:
         #no, so the file does not exist for this day, return empty array
         return EMPTY_PATH, date

def read_packed(fname):
   '''
   Reads IMS file that has been packaged in packed form to numpy array.

   Args:
      fname (str): full path to file in question.
    
   Returns:
      data (array): IMS data for day of year associated with this file.
   '''
   with gzip.open(fname, 'rt') as f:
      file_content = f.read().splitlines()
      data = np.zeros((1024,1024))
      counter = 0
      for line_num in range(len(file_content)):
         line = file_content[line_num]
         if line.startswith('00'):
            data[counter, :] = [i for i in line]
            counter += 1           
         else: 
            continue
      return data
         
def read_unpacked(fname):
   '''
   Reads IMS file in unpacked form to numpy array. Based on https://nsidc.org/sites/nsidc.org/files/IMS_24km_Unpacked_to_Packed_0.txt script.

   Args:
      fname (str): full path to file in question.
    
   Returns:
      data (array): IMS data for day of year associated with this file.
   '''

   with gzip.open(fname, 'rt') as f:
      if("empty_file" in fname):
         DataArray = np.zeros((1024,1024))
      else:
         # Skip 1200 bytes within the header.
         f.seek(1280)
         # Take all lines after the header, strip the end-line character and join all in one string.
         Lines = " ".join(line.strip('\n') for line in f)
         # Remove all white space from Lines with Lines.split.
         # If characters (s) in string are digits, convert to integers, then convert to a NumPy Array.
         # Lastly, reshape to 1024 x 1024 24 km resolution.
         DataArray = np.reshape(np.asarray([int(s) for s in Lines.split() if s.isdigit()]), [1024,1024])

         # From the documentation (Table 3):
         # For unpacked data, integer value of 164 is sea ice, while 165 is snow-covered land.
         # Convert 164 to 3 (sea ice) and 165 to 4 (snow covered land) to align with packed data.
         DataArray = np.where(DataArray == 164, 3, DataArray)
         DataArray = np.where(DataArray == 165, 4, DataArray)
      return DataArray

         
   
