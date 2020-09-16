#!/space/hall3/sitestore/eccc/crd/ccrp/mib001/usr_conda/envs/py3-arc-SCD/bin/python

from pathlib import Path
import cartopy.crs as ccrs
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np

from xc_yc_to_x_y import convert_xc_yc_to_meters_CMC

#### 
clim_min = 1998
clim_max = 2017
year_interest = 2019

#### FLAG TO ASSIGN OUTPUT FIGURE FORMAT
FIG_FMT = 'PNG' # or 'PDF' or 'TIF'

plt.rcParams['font.weight'] = 'bold'
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.labelsize'] = 16
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['xtick.labelsize'] = 14
plt.rcParams['ytick.labelsize'] = 14

fig_crs = ccrs.LambertAzimuthalEqualArea(central_latitude=90, central_longitude=-80)
data_crs = ccrs.Stereographic(true_scale_latitude=60, central_longitude=-80, central_latitude = 90, globe=ccrs.Globe(semimajor_axis=6371200, semiminor_axis=6371200))

figsize = (11, 10)
dpi = 100
extent = [-6e6, 6e6, -6e6, 6e6]
cbar_ticks = [-100, -80, -60, -40, -20, 0, 20, 40, 60, 80, 100]
# copied the RGB values from Arc18_Snow_Fig2.png
cmap = mpl.colors.LinearSegmentedColormap.from_list(
    name='fig3',
    colors=[
        (x[0]/255, x[1]/255, x[2]/255) for x in [
            (188,  15,   1), (255,  70,  53), (255, 142,  67),
            (252, 192,  34), (255, 247, 111), (255, 255, 255),
            (255, 255, 255), (255, 255, 255), (176, 255, 114),
            (152, 246, 227), (104, 187, 255), ( 39, 140, 254),
            (  0,  70, 199), (  9,  16, 158)]
    ],
    N=256
)

plot_root = Path(__file__).absolute().parent
data_root = plot_root.parent / 'data'

filename_end = str(year_interest)+'_clim_'+str(clim_min)+'_'+str(clim_max)+'.nc'

# load netcdf data (snow depth?, orig type = float)
with xr.open_dataset(data_root / ('anom_SD_March' + filename_end)) as ds:
    data_a = ds['sdp']
    data_a = convert_xc_yc_to_meters_CMC(data_a)
with xr.open_dataset(data_root / ('anom_SD_April' + filename_end)) as ds:
    data_b = ds['sdp']
    data_b = convert_xc_yc_to_meters_CMC(data_b)
with xr.open_dataset(data_root / ('anom_SD_May' + filename_end)) as ds:
    data_c = ds['sdp']
    data_c = convert_xc_yc_to_meters_CMC(data_c)
with xr.open_dataset(data_root / ('anom_SD_June' + filename_end)) as ds:
    data_d = ds['sdp']
    data_d = convert_xc_yc_to_meters_CMC(data_d)


# load clim data
clim_end = 'clim_'+str(clim_min)+'_'+str(clim_max)+'.nc'
with xr.open_dataset(data_root / ('March_' + clim_end)) as ds:
    mask_a = np.where(ds['sdp'] >= 1, 1., np.nan)
    data_a = data_a * mask_a
with xr.open_dataset(data_root / ('April_' + clim_end)) as ds:
    mask_b = np.where(ds['sdp'].values>=1, 1., np.nan)
    data_b = data_b * mask_b
with xr.open_dataset(data_root / ('May_' + clim_end)) as ds:
    mask_c = np.where(ds['sdp'].values>=1, 1., np.nan)
    data_c = data_c * mask_c
with xr.open_dataset(data_root / ('June_' + clim_end)) as ds:
    mask_d = np.where(ds['sdp'].values>=1, 1., np.nan)
    data_d = data_d * mask_d

for i,data in enumerate([data_a, data_b, data_c, data_d]):
    data = data.where(data != 0) #put nans on 0 values

# load vector data
land = gpd.read_file(plot_root / 'vector' / 'land.gpkg').to_crs(fig_crs.proj4_init)
lakes = gpd.read_file(plot_root / 'vector' / 'lakes.gpkg').to_crs(fig_crs.proj4_init)
ac = gpd.read_file(plot_root / 'vector' / 'arcticcircle.gpkg').to_crs(fig_crs.proj4_init)
rivers = gpd.read_file(plot_root / 'vector' / 'rivers.gpkg').to_crs(fig_crs.proj4_init)


# initialize canvas
fig, axs = plt.subplots(
    figsize=figsize,
    nrows=2,
    ncols=2,
    sharex=True,
    sharey=True,
    subplot_kw={'projection': fig_crs},
    gridspec_kw={'hspace': 0, 'wspace': 0}
)
((ax_a, ax_b), (ax_c, ax_d)) = axs

# setting margins
plt.subplots_adjust(top=0.999, bottom=0.001, left=0.001, right=0.999)

contour_a = data_a.plot.contourf(
    ax=ax_a, x='xc', y='yc', add_colorbar=False, transform=data_crs, 
    cmap=cmap, levels=cbar_ticks, extend='both', add_labels=False
)
contour_b = data_b.plot.contourf(
    ax=ax_b, x='xc', y='yc', add_colorbar=False, transform=data_crs, 
    cmap=cmap, levels=cbar_ticks, extend='both', add_labels=False
)
contour_c = data_c.plot.contourf(
    ax=ax_c, x='xc', y='yc', add_colorbar=False, transform=data_crs, 
    cmap=cmap, levels=cbar_ticks, extend='both', add_labels=False
)
contour_d = data_d.plot.contourf(
    ax=ax_d, x='xc', y='yc', add_colorbar=False, transform=data_crs, 
    cmap=cmap, levels=cbar_ticks, extend='both', add_labels=False
)

# setting figure extents
# adding vector data to map
for ax in [ax_a, ax_b, ax_c, ax_d]:
    ax.set_extent(extent, crs=fig_crs)
    ax.outline_patch.set_linewidth(1)
    ax.add_geometries(land['geometry'], facecolor='None', edgecolor='black', linewidth=0.4, crs=fig_crs)
    ax.add_geometries(lakes['geometry'], facecolor='white', edgecolor='black', linewidth=0.4, zorder=2, crs=fig_crs)
    ax.add_geometries(ac['geometry'], facecolor='None', edgecolor='black', linestyle='dashed', linewidth=1.5, alpha=0.4, zorder=3, crs=fig_crs)
    ax.add_geometries(rivers['geometry'], facecolor='None', edgecolor='black', linewidth=0.3, crs=fig_crs)

# colorbar
cb_ax = fig.add_axes([0.92, 0.25, 0.02, 0.5])
cbar = fig.colorbar(contour_a, ax=axs[:, 1], cax=cb_ax, ticks=cbar_ticks, extend='both')

# reset axes positions (pain!)
ax_a.set_position(pos=[0.001, 0.500, 0.45, 0.5])
ax_b.set_position(pos=[0.451, 0.500, 0.45, 0.5])
ax_c.set_position(pos=[0.001, 0.005, 0.45, 0.5])
ax_d.set_position(pos=[0.451, 0.005, 0.45, 0.5])

# axis text indicators
ax_a.text(0.02, 0.94, 'a.', fontsize=24, transform=ax_a.transAxes)
ax_b.text(0.02, 0.94, 'b.', fontsize=24, transform=ax_b.transAxes)
ax_c.text(0.02, 0.94, 'c.', fontsize=24, transform=ax_c.transAxes)
ax_d.text(0.02, 0.94, 'd.', fontsize=24, transform=ax_d.transAxes)

# save
if FIG_FMT.upper() == 'PDF':
    plt.savefig(data_root.parent / 'figures' / 'ARC_Snow_Fig3-python.pdf', dpi=dpi)
elif FIG_FMT.upper() == 'PNG':
    plt.savefig(data_root.parent / 'figures' / 'ARC_Snow_Fig3-python.png', dpi=dpi)
elif FIG_FMT.upper() == 'TIF':
    plt.savefig(data_root.parent / 'figures' / 'ARC_Snow_Fig3-python.tif', dpi=dpi)
else:
    print('Unrecognized figure format: "%s" (must be PNG or PDF)' % FIG_FMT)
