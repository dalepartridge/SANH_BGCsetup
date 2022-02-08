#!/sr/bin/env python3
'''
Script to download, process and interpolate light attenuation from CCI

ady - Broadband light attenuation from detritus and yellow substance

'''
import xarray as xr
import datetime as dt
import getpass
import fnmatch
import numpy as np
import nctoolkit as nc
import os
from tqdm import tqdm

######## User parameters ########################

# Define grid file and rename lon/lat fields
gridname = 'SANH'
gridfile = 'domain_cfg.nc'
var_map = {'nav_lon':'lon','nav_lat':'lat','bottom_level':'mask'}
grid_ds = xr.open_dataset(gridfile).rename(var_map).isel(t=0,z=0)
grid_ds['mask'] = xr.where(grid_ds.mask >0,1,0)

# Define Time Period
ystart=1998
yend=2020
time_res='8DAY' # monthly, 8DAY, 5DAY, DAILY 

## CCI file parameters
# As of Oct-2021, files have the format:
model='v5.0'
url = f'https://rsg.pml.ac.uk/thredds/dodsC/CCI_ALL-%s-%s' %(model,time_res.upper())

#################################################

# Load dataset
ds_full = xr.open_dataset(url)
wl_vars = list(ds_full[fnmatch.filter(ds_full,'adg_???')])[:-1] #Ignore highest wavelength as data is not reliable

# Create array of wavelengths and 'extend' by 5nm each side
wavelengths = np.array([float(s[-3:]) for s in wl_vars])
wavelengths[0] -= 5
wavelengths[-1] += 5

for y in tqdm(range(ystart,yend)):
    ds = ds_full[wl_vars].sel(time=slice(f'%s-10-01' %str(y-1), f'%s-03-31' %str(y+1)))

    #Interpolate to grid
    ds = ds.interp(lon=grid_ds.lon,lat=grid_ds.lat,method="linear")

    # Trapezoidal integration across wavelengths bands / wavelength range
    ds['adg_all'] = xr.concat([ds[v] for v in wl_vars],dim='wl')
    ds = ds[['adg_all']].assign_coords(wl=('wl',wavelengths))
    ds['ady'] = 2 * ds.adg_all.integrate('wl') / (wavelengths[-1]-wavelengths[0])

    # Fill missing data (cloud covered pixels)
    # Step 1 - Interpolation in time
    ds_filled = ds.ady.interpolate_na('time')
    ds_filled = ds_filled.bfill('time')
    ds_filled = ds_filled.ffill('time')
    
    # Step 2 - Interpolation in space
    ds_filled['lon'] = ds_filled.lon.assign_attrs({'units':'degrees_east'})
    ds_filled['lat'] = ds_filled.lat.assign_attrs({'units':'degrees_north'})
    ds_nc = nc.from_xarray(ds_filled)
    ds_nc.fill_na(n=12)
    ds = ds_nc.to_xarray()
    ds['ady'] = ds.ady.where(grid_ds.mask == 1)
    
    # Assign Attributes
    ds['ady'] = ds.ady.assign_attrs({
                    'standard_name':"volume_absorption_coefficient_of_radiative_flux_in_sea_water_due_to_detrirus_and_yellow_substances",
                    'long_name':"absorption due to detritus & yellow substances",
                    'coordinates': 'times lat lon',
                    'units': '1/m'})
    ds.attrs = {'title':f'Light Attenuation from detritus and yellow substance from CCI on %s grid at %s resolution' % (gridname, time_res),
                          'institution':'Plymouth Marine Laboratory, UK',
                          'date_created': dt.date.today().strftime('%d/%m/%Y'),
                          'created_by': getpass.getuser(),
                          'model_version': model,
                          'original_data_source':url}

    ofile=f'%s-CCI-ady-%s-broadband_y%s.nc' %(gridname,time_res.lower(),y)
    ds.isel(time=ds.groupby('time.year').groups[y]).to_netcdf(ofile)



