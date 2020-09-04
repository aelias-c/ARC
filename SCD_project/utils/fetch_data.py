## Credit: "Python 101: Downloading a File with ftplib" page on 
### blog.pythonlibrary.org, page public as of July 19, 2012

## Adapted: Aleksandra Elias Chereque
## Created: July 13, 2020
## Last edited: Aug 6, 2020

import os
from ftplib import FTP

from utils.constants import RUN_SETUP, IMS_DIR

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

def download_full_IMS_year(year):
   '''
   Given relevant year, downloads all IMS files for the year to IMS_DIR.

   Args:
      year (int): relevant year, must be from 1998-present.
   '''
   
   ftp = FTP('sidads.colorado.edu')
   ftp.login()
   ftp.cwd('DATASETS/NOAA/G02156/24km/'+str(year)+'/')

   listing = []
   ftp.retrlines('LIST', listing.append)

   for i in range(2, len(listing)): #start from 2 to skip the '.' and '..' directories, listed first
      words = listing[i].split(None, 8)
      filename = words[-1].lstrip()
      print('Downloading =>', filename)
      download(ftp, IMS_DIR+str(year)+'/', filename)
      
def update_current_y_IMS(current_year):
   '''
   Downloads IMS Data to bring current year up to date.
   '''
   
   ftp = FTP('sidads.colorado.edu')
   ftp.login()
   ftp.cwd('DATASETS/NOAA/G02156/24km/'+str(current_y)+'/')

   listing = []
   ftp.retrlines('LIST', listing.append)
   
   for i in range(1, len(listing)):
      words = listing[-i].split(None, 8)
      filename = words[-1].lstrip()
      if os.path.exists(IMS_DIR+str(current_year)+'/'+filename):
         print('Directory is up to date, downloaded '+str(i)+' new days.')
         break
      else:
         print('Downloading =>', filename)
         download(ftp, current_y, filename)

def download_IMS_latlon():
   '''
   Downloads latitude and longitude grids for IMS data to IMS_DIR.
   '''

   ftp = FTP('sidads.colorado.edu')
   ftp.login()
   ftp.cwd('DATASETS/NOAA/G02156/metadata/')

   download(ftp, IMS_DIR, 'imslat_24km.bin.gz')
   download(ftp, IMS_DIR, 'imslon_24km.bin.gz')

