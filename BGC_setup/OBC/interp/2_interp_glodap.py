### The script applies seasonality to annual climatology of DIC and Alkalinity retrieved from GLODAPv2 based on monthly mean climatology values of nitrate from WOA18. This assumes DIC/Alkalinity seasonality driven by biogeochemical processes only. Script originally created by Gennadi Lessin, modified by Helen Powley

import yaml
import xesmf
import xarray as xr
import numpy as np
from tqdm import tqdm

def dim_remap(ds,vconf):
    remap = {v:k for k,v in vconf['dim_map'].items()}
    return ds.rename_dims(remap)

def var_remap(ds,vconf):
    remap = {v:k for k,v in vconf['var_map'].items()}
    return ds.rename(remap)

# Open yaml file with configuration
with open('2_interp.yaml','r') as yamlfile:
    yconf = yaml.safe_load(yamlfile)

# Load nemo domain file, rename variables and create a mask
ds_dom = xr.open_dataset(yconf['domainfile']).rename(
                        {'nav_lon':'lon','nav_lat':'lat','nav_lev':'depth'}).isel(t=0)
ds_dom = ds_dom.assign_coords(lon=ds_dom.lon,lat=ds_dom.lat,depth=ds_dom.depth)
ds_dom['mask'] = xr.where(ds_dom.bottom_level!=0,1,0)

ds_dep = xr.open_dataset(yconf['bdydepthfile']).gdept.isel(yb=0,xb=0)

# Create empty dataset to hold interpolated values
ds_int = xr.Dataset(coords={'depth':ds_dep,'lon':ds_dom.lon,'lat':ds_dom.lat})

for v,vconf in yconf['variables'].items():
    print('Interpolating: ' + v)
    # Load dataset and remap name
    ds = xr.open_dataset(vconf['input_file'],decode_times=False)
    ds = dim_remap(ds,vconf) if 'dim_map' in vconf else ds
    ds = var_remap(ds,vconf) if 'var_map' in vconf else ds
    ds = ds.assign_coords(lon=ds.lon,lat=ds.lat)
    ds = ds.assign_coords(depth=ds.depth) if 'depth' in ds else ds

    ds_3Dint = xr.Dataset(coords={'depth':ds.depth,'lon':ds_dom.lon,'lat':ds_dom.lat})
    ds_3Dint[v] = (('z','y','x'),np.zeros((ds_3Dint.z.size,ds_3Dint.y.size,ds_3Dint.x.size)))
    for z in tqdm(range(ds.z.size)):
        ds['mask'] = xr.where(~np.isnan(ds[vconf['varname']].isel(z=z)),1,0)
        regridder = xesmf.Regridder(ds.isel(z=z),ds_dom,method='bilinear',extrap_method='nearest_s2d')
        ds_3Dint[v][z,:,:] = regridder(ds[vconf['varname']].isel(z=z)).values

    #Vertical interpolation
    ds_int[v] = ds_3Dint[v].swap_dims({'z':'depth'}).interp(depth=ds_dep.values,
                                        method='linear',kwargs={"fill_value": "extrapolate"})

#######################################
# Seasonalise GLODAP

# Calculate seasonal nitrate anomaly
ds_nit = xr.open_dataset('woa_OBCs.nc',decode_times=False)
nit_anom=ds_nit.N3_n - ds_nit.N3_n.mean('t')

# Apply seasonality
ds_int=ds_int.expand_dims({'t':12}).assign_coords({'time':ds_nit.time}) 
ds_int['O3_c'] = ds_int['O3_c'] + nit_anom*106./16.
ds_int['O3_TA'] = ds_int['O3_TA'] - nit_anom
    
# Save out
ds_int.to_netcdf(yconf['outfile'])
