import xesmf
import xarray as xr
import numpy as np

sfile = ''
svar = 'n_an'
s_remap = {}

dfile = 'mesh_mask.nc'
d_remap = {'nav_lon':'lon','nav_lat':'lat'}

ofile = ''
ovar = 'nitrate'

ds = xr.open_dataset(sfile,decode_times=False).rename(s_remap)

ds_dom = xr.open_dataset(dfile).rename(d_remap)
ds_dom['mask'] = xr.where(ds_dom.bottom_level.isel(t=0)!=0,1,0)

ds_int = xr.Dataset(coords={'depth':ds.depth,'lon':ds_dom.lon,'lat':ds_dom.lat})
ds_int[ovar] = (('depth','y','x'),np.zeros((ds.depth.size,ds_dom.y.size,ds_dom.x.size)))

for z in range(ds_int.depth.size):
    ds['mask'] = xr.where(~np.isnan(ds[svar].isel(time=0,depth=z)),1,0)
    regridder = xesmf.Regridder(ds.isel(time=0,depth=z),ds_dom.isel(t=0),method='bilinear',extrap_method='nearest_s2d')
    ds_int[ovar][z,:,:] = regridder(ds[svar].isel(time=0,depth=z)).values

ds_int.to_netcdf(ofile)
