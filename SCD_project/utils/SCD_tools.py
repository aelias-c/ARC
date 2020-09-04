## Author: Aleksandra Elias Chereque
## Created: July 8, 2020
## Last edited: Aug 6, 2020

import numpy as np
import xarray as xr 
import matplotlib.pylab as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib as mpl 
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import matplotlib.ticker as mticker   

from utils.IMS_tools import load_latlon

def plot_2(data1, data2, lat, lon, name):
   fig_crs = ccrs.LambertAzimuthalEqualArea(central_latitude=90, central_longitude=-80)
   data_crs = ccrs.PlateCarree()
   figsize = (15, 6.85)
   extent = [-6e6, 5e6, -5e6, 5e6]
   cbar_ticks = [-50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50]
   # copied the RGB values from Arc18_Snow_Fig2.png
   cmap = mpl.colors.LinearSegmentedColormap.from_list(
      name='fig2',
      colors=[
         (x[0]/255, x[1]/255, x[2]/255) for x in [(255,  47,  34), (255, 113,  57), (239, 162,   0), (255, 211,  66), (255, 255, 156), (255, 255, 255), (255, 255, 255), (255, 255, 255), (198, 255, 222), (140, 211, 255), ( 57, 195, 255), (  0, 150, 189), (  0,  95, 206)]],
      N=256 )

   cut_data1 = data1[158:1024-158+1,158:1024-158+1]
   cut_data2 = data2[158:1024-158+1,158:1024-158+1]
   cut_lat = lat[158:1024-158+1,158:1024-158+1]
   cut_lon = lon[158:1024-158+1,158:1024-158+1]

   #initialize canvas

   fig, (ax_a, ax_b) = plt.subplots(figsize=figsize, nrows=1, ncols=2, subplot_kw={'projection': fig_crs})

   # setting margins
   plt.subplots_adjust(top=0.999, bottom=0.001, left=0.001, right=0.999, wspace=0, hspace=0)

   mesh_a = ax_a.pcolormesh(cut_lon, cut_lat, cut_data1, transform = data_crs, cmap=cmap, vmin=-50, vmax=50)
   mesh_b = ax_b.pcolormesh(cut_lon, cut_lat, cut_data2, transform = data_crs, cmap=cmap, vmin=-50, vmax=50)
   ax_a.coastlines()
   ax_b.coastlines()
   ax_a.add_feature(cfeature.BORDERS, linestyle=':')
   ax_b.add_feature(cfeature.BORDERS, linestyle=':')
   
   gla = ax_a.gridlines(color='gray')
   gla.xlocator = mticker.FixedLocator([-180, -90, 0, 90, 180])
   gla.ylocator = mticker.FixedLocator([60])

   glb = ax_b.gridlines(color='gray')
   glb.xlocator = mticker.FixedLocator([-180, -90, 0, 90, 180])
   glb.ylocator = mticker.FixedLocator([60])

   # adding colorbars
   caxa = inset_axes(ax_a, width='5%', height='55%', loc=3, bbox_to_anchor=(0.015, 0.015, 1, 1), bbox_transform=ax_a.transAxes)
   cb_a = plt.colorbar(mesh_a, cax=caxa, ticks=cbar_ticks, orientation='vertical')
   ax_a.text(0.015, 0.61, 'days', fontsize=18, transform=ax_a.transAxes)
   cb_a.ax.tick_params(labelsize=14)

   caxb = inset_axes(ax_b, width='5%', height='55%', loc=3, bbox_to_anchor=(0.015, 0.015, 1, 1), bbox_transform=ax_b.transAxes)
   cb_b = plt.colorbar(mesh_b, cax=caxb, ticks=cbar_ticks, orientation='vertical')
   ax_b.text(0.015, 0.61, 'days', fontsize=18, transform=ax_b.transAxes)
   cb_b.ax.tick_params(labelsize=14)

   # axis text indicators
   ax_a.text(0.02, 0.94, 'a.', fontsize=30, transform=ax_a.transAxes)
   ax_b.text(0.02, 0.94, 'b.', fontsize=30, transform=ax_b.transAxes)

   # setting figure extents
   ax_a.set_extent(extent, crs=fig_crs)
   ax_a.outline_patch.set_linewidth(1)
   ax_b.set_extent(extent, crs=fig_crs)
   ax_b.outline_patch.set_linewidth(1)
   
   plt.savefig(name)
   plt.close()


