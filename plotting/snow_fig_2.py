#!/space/hall3/sitestore/eccc/crd/ccrp/mib001/usr_conda/envs/py3-arc-SCD/bin/python

from pathlib import Path
import cartopy.crs as ccrs
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import xarray as xr
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from xc_yc_to_x_y import convert_xc_yc_to_meters_IMS

#### FLAG TO ASSIGN OUTPUT FIGURE FORMAT
FIG_FMT = 'PNG' # or 'PNG' or 'TIF'

#### file name for year of interest
data_file='anom_SCD_2019_to_2020.nc'

plt.rcParams['font.weight'] = 'bold'
plt.rcParams['font.family'] = 'Arial'

fig_crs = ccrs.LambertAzimuthalEqualArea(central_latitude=90, central_longitude=-80)
data_crs = ccrs.Stereographic(true_scale_latitude=60, central_longitude=-80, central_latitude=90, globe=ccrs.Globe(semimajor_axis=6371200, semiminor_axis=6371200))
figsize = (15, 6.85)
dpi = 100
extent = [-6e6, 5e6, -5e6, 5e6]
cbar_ticks = [-50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50]

plot_root=Path(__file__).absolute().parent
data_root=plot_root.parent / 'data' 

cmap = mpl.colors.LinearSegmentedColormap.from_list(
    name='fig2',
    colors=[
        (x[0]/255, x[1]/255, x[2]/255) for x in [
            (140,  20,  10), (255, 255, 255), (10,  20, 122)
        ]
    ],
    N=11
)
### so that the colorbar extensions aren't the same colour as the cmap max/min
# very slightly darker blue
cmap.set_over((5/255, 12/255, 102/255))
# very slightly darker red
cmap.set_under((115/255, 25/255, 15/255))
# note the -1.6/1.6 - Mike noticed the greenland values were in the range of -1.5999999999 to 0.8 
levels = [-50,-40,-30,-20,-10,-1.6,1.6,10,20,30,40,50]

# note that I add the x/y in meters
with xr.open_dataset(data_root / data_file) as ds:
    data_a = convert_xc_yc_to_meters_IMS(ds.sel(season='SON')['snowc'])
    data_b = convert_xc_yc_to_meters_IMS(ds.sel(season='MAM')['snowc'])

land = gpd.read_file(plot_root / 'vector' / 'land.gpkg').to_crs(fig_crs.proj4_init)
lakes = gpd.read_file(plot_root / 'vector' / 'lakes.gpkg').to_crs(fig_crs.proj4_init)
ac = gpd.read_file(plot_root / 'vector' / 'arcticcircle.gpkg').to_crs(fig_crs.proj4_init)
rivers = gpd.read_file(plot_root / 'vector' / 'rivers.gpkg').to_crs(fig_crs.proj4_init)

fig, (ax_a, ax_b) = plt.subplots(
    figsize=figsize,
    nrows=1,
    ncols=2,
    subplot_kw={'projection': fig_crs}
)

plt.subplots_adjust(top=0.999, bottom=0.001, left=0.001, right=0.999, wspace=0, hspace=0)
contour_a = data_a.plot.contourf(
    ax=ax_a, x='xc', y='yc', add_colorbar=False, transform=data_crs,
    cmap=cmap, levels=levels, vmin=-50, vmax=50
)

contour_b = data_b.plot.contourf(
    ax=ax_b, x='xc', y='yc', add_colorbar=False, transform=data_crs,
    cmap=cmap, levels=levels, vmin=-50, vmax=50
)

for ax in [ax_a, ax_b]:
   ax.set_extent(extent, crs=fig_crs)
   ax.outline_patch.set_linewidth(1)
   ax.add_geometries(land['geometry'], facecolor='None', edgecolor='black', linewidth=0.4, crs=fig_crs)
   ax.add_geometries(lakes['geometry'], facecolor='white', edgecolor='black', linewidth=0.4, zorder=2, crs=fig_crs)
   ax.add_geometries(ac['geometry'], facecolor='None', edgecolor='black', linestyle='dashed', linewidth=1.5, alpha=0.4, zorder=3, crs=fig_crs)
   ax.add_geometries(rivers['geometry'], facecolor='None', edgecolor='black', linewidth=0.3, crs=fig_crs)

caxa = inset_axes(ax_a, width='5%', height='55%', loc=3, bbox_to_anchor=(0.015, 0.015, 1, 1), bbox_transform=ax_a.transAxes)
cb_a = plt.colorbar(contour_a, cax=caxa, ticks=cbar_ticks, orientation='vertical', extend='neither')
ax_a.text(0.015, 0.61, 'days', fontsize=18, transform=ax_a.transAxes)
cb_a.ax.tick_params(labelsize=14)
caxb = inset_axes(ax_b, width='5%', height='55%', loc=3, bbox_to_anchor=(0.015, 0.015, 1, 1), bbox_transform=ax_b.transAxes)
cb_b = plt.colorbar(contour_b, cax=caxb, ticks=cbar_ticks, orientation='vertical', extend='neither')
ax_b.text(0.015, 0.61, 'days', fontsize=18, transform=ax_b.transAxes)
cb_b.ax.tick_params(labelsize=14)
ax_a.text(0.02, 0.94, 'a.', fontsize=30, transform=ax_a.transAxes)
ax_b.text(0.02, 0.94, 'b.', fontsize=30, transform=ax_b.transAxes)

# save
if FIG_FMT.upper() == 'PDF':
    plt.savefig(plot_root.parent / 'figures' / 'ARC_Snow_Fig2-aleksdata.pdf', dpi=dpi)
elif FIG_FMT.upper() == 'PNG':
    plt.savefig(plot_root.parent / 'figures' / 'ARC_Snow_Fig2-aleksdata.png', dpi=dpi)
elif FIG_FMT.upper() == 'TIF':
    plt.savefig(plot_root.parent / 'figures' / 'ARC_Snow_Fig2-aleksdata.tif', dpi=dpi)
else:
    print('Unrecognized figure format: "%s" (must be PNG or PDF)' % FIG_FMT)
