'''
Script to interpolate variables from multiple sources onto a nemo domain

Reads configuration file interp.yaml from the same directory containing the fields:

domainfile : path to domain netcdf file
outfile : name (+path) of file to save interpolated output
variables : set of variables named by desired output varname with following fields:
        input_file : path to source file
        varname : name of variable to interpolate in input_file
        has_depth (optional) : booleon, field is 3D (True) or 2D (False), (default: True) 
        timeidx (optional) : index of time record to interpolate (default: 0)  
        dim_map (optional) :
            x : lon dimension
            y : lat dimension
            t : time dimenion
            z : depth dimension
        var_map (optional) :
            lon : lon variable
            lat : lat variable
            depth : depth variable
        
'''
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
with open('interp.yaml','r') as yamlfile:
    yconf = yaml.safe_load(yamlfile)

# Load nemo domain file, rename variables and create a mask
ds_dom = xr.open_dataset(yconf['domainfile']).rename(
                        {'nav_lon':'lon','nav_lat':'lat','nav_lev':'depth'}).isel(t=0)
ds_dom = ds_dom.assign_coords(lon=ds_dom.lon,lat=ds_dom.lat,depth=ds_dom.depth)                        
ds_dom['mask'] = xr.where(ds_dom.bottom_level!=0,1,0)

# Create empty dataset to hold interpolated values
ds_int = xr.Dataset(coords={'depth':ds_dom.depth,'lon':ds_dom.lon,'lat':ds_dom.lat})

for v,vconf in yconf['variables'].items():
    print('Interpolating: ' + v)
    # Load dataset and remap name
    ds = xr.open_dataset(vconf['input_file'],decode_times=False)
    ds = dim_remap(ds,vconf) if 'dim_map' in vconf else ds
    ds = var_remap(ds,vconf) if 'var_map' in vconf else ds
    ds = ds.assign_coords(lon=ds.lon,lat=ds.lat)
    ds = ds.assign_coords(depth=ds.depth) if 'depth' in ds else ds

    # If time is present, select correct time record
    timerec = int(vconf['timeidx']) if 'timeidx' in vconf else 0 
    ds = ds.isel(t=timerec) if 't' in list(ds.dims.keys()) else ds

    # Check if depth variables are to be processed
    has_depth = False if 'has_depth' in vconf else True
    # 2D interpolation for each depth level, followed by interpolation in depth
    if has_depth:
        ds_3Dint = xr.Dataset(coords={'depth':ds.depth,'lon':ds_dom.lon,'lat':ds_dom.lat})
        ds_3Dint[v] = (('z','y','x'),np.zeros((ds_3Dint.z.size,ds_3Dint.y.size,ds_3Dint.x.size)))
        for z in tqdm(range(ds.z.size)):
            ds['mask'] = xr.where(~np.isnan(ds[vconf['varname']].isel(z=z)),1,0)
            regridder = xesmf.Regridder(ds.isel(z=z),ds_dom,method='bilinear',extrap_method='nearest_s2d')
            ds_3Dint[v][z,:,:] = regridder(ds[vconf['varname']].isel(z=z)).values

        #Vertical interpolation
        ds_int[v] = ds_3Dint[v].swap_dims({'z':'depth'}).interp(depth=ds_dom.depth.values,
                                        method='linear',kwargs={"fill_value": "extrapolate"})

    else:     
        ds['mask'] = xr.where(~np.isnan(ds[vconf['varname']]),1,0)
        regridder = xesmf.Regridder(ds,ds_dom,method='bilinear',extrap_method='nearest_s2d')
        ds_int[v] = (('y','x'),regridder(ds[vconf['varname']]).values)

ds_int.to_netcdf(yconf['outfile'])
