import xarray as xr
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import glob
import cmocean as cm
import cartopy.crs as ccrs
from cartopy.feature import NaturalEarthFeature

coastline = NaturalEarthFeature(category="physical", facecolor=[0.9, 0.9, 0.9], name="coastline", scale="50m")
def plot_data_map(axes,data,bath,vmin,vmax,cmap,title):
    data.plot(ax=axes,x='nav_lon',y='nav_lat', \
              robust=True, vmin=vmin,vmax=vmax, \
              cmap=cmap,add_colorbar=True)
    axes.add_feature(coastline, edgecolor="gray")
    gl = axes.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0.5, color="gray", linestyle="-")
    gl.top_labels = False
    gl.bottom_labels = True
    gl.right_labels = False
    gl.left_labels = True
    axes.set_aspect("auto")
    #bath.plot.contour(ax=axes,x='nav_lon',y='nav_lat',levels=[40,500],linestyles=['dashed','solid'],colors='k',alpha=0.8,linewidths=1)
    axes.set_title(title,x=0.98,y=0.93,fontsize=10,horizontalalignment='right')

################################################################################
### PROCESS DATA
################################################################################

ds = xr.open_dataset('SANH_5d_riv_nit.nc')
ds = ds.isel(deptht=0,time_counter=-1)

grd = xr.open_dataset('/work/n01/n01/dapa/SANH/INPUTS/DOM/domain_cfg.nc')
bath = xr.open_dataset('/work/n01/n01/dapa/SANH/RAW_DATA/DOMAIN/bathy_meter.nc')
ds['nav_lon'] = grd.nav_lon
ds['nav_lat'] = grd.nav_lat
ds['bath'] = bath.Bathymetry

######################################################################3
# Spatial plot

cmap = cm.cm.matter

vmax=1
f = plt.figure(figsize=(24,12))
matplotlib.gridspec.GridSpec(2,3)

ax1 = plt.subplot2grid((2,3),(0,0),projection=ccrs.PlateCarree())
plot_data_map(ax1,ds['DON_ind_n'],ds.bath,0,vmax,cmap,'DON India Rivers')

ax2 = plt.subplot2grid((2,3),(0,1),projection=ccrs.PlateCarree())
plot_data_map(ax2,ds['DON_ban_n'],ds.bath,0,vmax,cmap,'DON Bangladesh Rivers')

ax3 = plt.subplot2grid((2,3),(0,2),projection=ccrs.PlateCarree())
plot_data_map(ax3,ds['DON_sri_n'],ds.bath,0,vmax,cmap,'DON Sri Lanka Rivers')

ax4 = plt.subplot2grid((2,3),(1,0),projection=ccrs.PlateCarree())
plot_data_map(ax4,ds['DON_pak_n'],ds.bath,0,vmax,cmap,'DON Pakistan Rivers')

ax5 = plt.subplot2grid((2,3),(1,1),projection=ccrs.PlateCarree())
plot_data_map(ax5,ds['DON_mya_n'],ds.bath,0,vmax,cmap,'DON Myanmar Rivers')

plt.savefig('SANH_country_DON.png')

vmax=6
f = plt.figure(figsize=(24,12))
matplotlib.gridspec.GridSpec(2,3)

ax1 = plt.subplot2grid((2,3),(0,0),projection=ccrs.PlateCarree())
plot_data_map(ax1,ds['DIN_ind_n'],ds.bath,0,vmax,cmap,'DIN India Rivers')

ax2 = plt.subplot2grid((2,3),(0,1),projection=ccrs.PlateCarree())
plot_data_map(ax2,ds['DIN_ban_n'],ds.bath,0,vmax,cmap,'DIN Bangladesh Rivers')

ax3 = plt.subplot2grid((2,3),(0,2),projection=ccrs.PlateCarree())
plot_data_map(ax3,ds['DIN_sri_n'],ds.bath,0,vmax,cmap,'DIN Sri Lanka Rivers')

ax4 = plt.subplot2grid((2,3),(1,0),projection=ccrs.PlateCarree())
plot_data_map(ax4,ds['DIN_pak_n'],ds.bath,0,vmax,cmap,'DIN Pakistan Rivers')

ax5 = plt.subplot2grid((2,3),(1,1),projection=ccrs.PlateCarree())
plot_data_map(ax5,ds['DIN_mya_n'],ds.bath,0,vmax,cmap,'DIN Myanmar Rivers')

plt.savefig('SANH_country_DIN.png')
plt.show()







