# May be changed often

DOWNLOAD_DATA = False 
#False if data has been downloaded 

RUN_SETUP = False
#False if all data has been reformatted to netCDF 

current_y = 2020 
#set current year

max_day_downloaded = 213 
#set how many days exist in the IMS record for current year. If latest download is 2020152, set max_day_downloaded to 151 to be safe.

max_day_change = False 
#if max_day_downloaded is changed, set to True - otherwise, should be False

# Set once

IMS_DIR = '/data/kushner_group/IMS/'
#set path to directory where IMS data should be downloaded
IMS_files_loc = '/users/jk/19/achereque/ARC/SCD_project/IMS_nc_output/'
#set path to directory where reformatted IMS data should be saved

EMPTY_PATH = '/data/kushner_group/IMS/EMPTY_GZ/empty_file.gz'
#EMPTY_PATH is a txt file created by saving a 1024x1024 array of zeros to file
#if file doesn't exist yet, use create_empty_IMS.py



