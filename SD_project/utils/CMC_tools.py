## Author: Aleksandra Elias Chereque
## Created: July 14, 2020
## Last edited: Sept 2, 2020

import os
import zipfile
import numpy as np

from utils.constants import CMC_DIR

def read_lsmask():
   '''
   Returns a lsmask with 1 on land and 0 on water for CMC snow depth data. 
   '''

   fname = CMC_DIR+'cmc_analysis_lsmask_binary_nogl_v01.2.txt'
   with open(fname, 'rt') as f:
      file_content = f.read().splitlines()
      mask = np.zeros((706, 706))
      for line_num in range(706):
         line = file_content[line_num]
         mask[line_num,:] = [i for i in line]
   return mask   

def read_homog_mask(return_latlon=False):
   '''
   Returns a mask with value 0 on every grid square that needs to be excluded. On square lat/lon grids provided by CMC, coordiates are given for squares to be excluded, and zeros fill all the allowed squares. 
   '''

   fname = CMC_DIR + 'cmc_homog_mask_points_v01.2.csv'

   homog_mask_points = np.loadtxt(fname, skiprows=1, delimiter=',')
   lat = np.zeros((706, 706))
   lon = np.zeros((706, 706))

   for row in range(np.shape(homog_mask_points)[0]):
      i, j, latitude, longitude = homog_mask_points[row]
      j = j-1 #Python convention
      i = i-1 #Python convention
      lat[int(i),int(j)] = latitude
      lon[int(i), int(j)] = longitude

   mask = np.where(lat == 0, 1., 0.) 
   if return_latlon:
      return lat, lon, mask
   else:
      return mask

def read_mly_data(dir, zipname, months = 12):
   '''
   Returns monthly snow depth data from a file containing data for a full year. 

   Args:
      dir (str): full path to the directory where the file has been downloaded
      zipname (str): the filename ending in .zip
      months (int): default 12 for 12 months of data, but 1998 has only 5 months and the current year may also be incomplete.
   '''

   with zipfile.ZipFile(dir+zipname) as z:
      fname = z.namelist()[0] #there is only one file in these .zip files
      data = np.zeros((months, 706, 706))
      with z.open(fname, 'r') as f:
         file_content = f.read().splitlines()
         for month in range(months):
            first = month * (706 + 1) #file formatted as 'YYYY MM \n (706,706) data, so skip the first line, and then every 706th after that
            for row in range(1, 707):
               content = file_content[first + row].split()
               data[month, row-1, :] = [float(i) for i in content]
   return data

def load_latlon():
   path = CMC_DIR + 'cmc_analysis_ps_lat_lon_v01.2.zip'
   
   if not os.path.exists(CMC_DIR+'cmc_analysis_ps_lat_lon_v01.2.txt'):
      with zipfile.ZipFile(CMC_DIR+'cmc_analysis_ps_lat_lon_v01.2.zip','r') as zip_ref:
         zip_ref.extractall(CMC_DIR)

   i, j, lat, lon = np.loadtxt(CMC_DIR+'cmc_analysis_ps_lat_lon_v01.2.txt', skiprows=9, unpack=True)

   lats = np.zeros((706, 706))
   lons = np.zeros((706, 706))

   for idx in range(len(i)):
      i_idx = int(i[idx]) - 1 #Python convention
      j_idx = int(j[idx]) - 1 #Python convention
      lats[i_idx, j_idx] = lat[idx]
      lons[i_idx, j_idx] = lon[idx]

   return lats, lons
   

   