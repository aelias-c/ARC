## Credit: "Python 101: Downloading a File with ftplib" page on 
### blog.pythonlibrary.org, page public as of July 19, 2012

## Adapted: Aleksandra Elias Chereque
## Created: July 13, 2020
## Last edited: Aug 11, 2020

import os
from ftplib import FTP

from utils.constants import CMC_DIR

def download(ftp, download_dir, fname):
   '''
   Retrieve file in binary transfer mode, write to file locally.

   Args:
      ftp: relevant instance of FTP class, pointing to correct directory
      download_dir (str): path to directory to save these files locally
      fname: filename accessed via FTP, used to name file locally
   '''

   if not os.path.exists(download_dir):
      os.makedirs(download_dir)

   local_filename = download_dir+str(fname)
   lf = open(local_filename, 'wb')
   ftp.retrbinary('retr ' + fname, lf.write)
   lf.close()

def download_monthly_CMC_year(year):
   '''
   Given relevant year, downloads zipped CMC snow depth file for year, contains monthly data.

   Args:
      year (int): relevant year, must be from 1998-present.
   '''
   
   ftp = FTP('sidads.colorado.edu')
   ftp.login()
   ftp.cwd('DATASETS/nsidc0447_CMC_snow_depth_v01/Snow_Depth/Snow_Depth_Monthly_Averages/')

   listing = []
   ftp.retrlines('LIST', listing.append)
   list_year = [name for name in listing if str(year) in name]
   if len(list_year) == 1: #only '..' exists in directory, no file
      print('No file for this year exists')
   else:
      words = list_year[0].split(None, 8)
      filename = words[-1].lstrip()
      print('Downloading =>', filename)
      download(ftp, CMC_DIR, filename)

def download_CMC_latlon():
   '''
   Downloads latitude and longitude grids for CMC data to CMC_DIR.
   '''

   ftp = FTP('sidads.colorado.edu')
   ftp.login()
   ftp.cwd('DATASETS/nsidc0447_CMC_snow_depth_v01/')
   download(ftp, CMC_DIR, 'cmc_analysis_ps_lat_lon_v01.2.zip')

def download_CMC_lsmask():
   '''
   Downloads land-sea mask for CMC data to CMC_DIR.
   '''

   ftp = FTP('sidads.colorado.edu')
   ftp.login()
   ftp.cwd('DATASETS/nsidc0447_CMC_snow_depth_v01/')
   download(ftp, CMC_DIR, 'cmc_analysis_lsmask_binary_nogl_v01.2.txt')

def download_CMC_homogmask():
   '''
   Downloads homogeneity mask for CMC data to CMC_DIR.
   '''

   ftp = FTP('sidads.colorado.edu')
   ftp.login()
   ftp.cwd('DATASETS/nsidc0447_CMC_snow_depth_v01/')
   download(ftp, CMC_DIR, 'cmc_homog_mask_points_v01.2.csv')

