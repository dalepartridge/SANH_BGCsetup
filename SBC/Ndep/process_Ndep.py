import xarray as xr
import netCDF4
import numpy as np
import pandas as pd

def get_molar_mass(element):
    from molmass import Formula
    f = Formula(element)
    return f.mass


def convert_mass_to_mol(x,units,mw,target_units=None):
    '''
    Function to convert mass component of a value with pint units into the molar mass. 

    Inputs
    ------
    x: float, including a mass component,
    units: string, units of x,
    mw: float, molar mass in g/mol, 
    target_units: string, required units

    Outputs
    -------
    y - float with pint units, Returns x with mass converted to mols. 
                            If target_units != None, returns value with full converted units. 
    
    Example
    -------

    y = convert_mass_to_mol(12.0, 'kilogram / kilometer**2 / year', 12.0) 
            >> 1000.0 <Unit('mole / kilometer ** 2 / year')>    
    y = convert_mass_to_mol(5000.0, 'kilogram / kilometer**2 / year', 14.0, \
                            target_units='mmol / m**2 / s') 
            >> 1.132e-05 <Unit('millimole / meter ** 2 / second')>    

    '''
    import pint
    ureg = pint.UnitRegistry()
    x *= ureg(units)

    y = 1
    for k,v in x._units.items():
        if ureg('[%s]'%k).dimensionality == '[mass]':
            y *= (x.magnitude * ureg(k)).to('mol','chemistry',mw=mw*ureg('g/mol'))**v
        else:
            y *= ureg('%s**%i'%(k,v))
    return y.magnitude if target_units is None else y.to(target_units).magnitude

def trend_coef(x):
    '''
    Function to calculate linear trend coefficients in time for 2D (lat/lon) array. Returns

    Inputs
    ------
    x: array, dimensions time x lat x lon

    Outputs
    --------
    c - array, Intercept coefficient dimensions lat x lon
    m - array, Slope coefficient dimensions lat x lon
    '''
    from scipy.signal import detrend
    dt = detrend(x, axis=0, type='linear')
    t = x - dt
    return t[0,:,:], t[1,:,:] - t[0,:,:]


# Load Dataset
ds = xr.open_dataset('SANH_Ndep_1985_2015.nc').rename({'lat':'y','lon':'x','NHx':'N4_flux','NOy':'N3_flux'}).drop('crs')
Nyears = len(ds.time)

#Convert units
tar_units = 'mmol / m**2 / s'
ds['N3_flux'].values = convert_mass_to_mol(ds.N3_flux.values,'g / m**2 / year',get_molar_mass('N'),target_units=tar_units)
ds.N3_flux.attrs['units']=tar_units

ds['N4_flux'].values = convert_mass_to_mol(ds.N4_flux.values,'g / m**2 / year',get_molar_mass('N'),target_units=tar_units)
ds.N4_flux.attrs['units']=tar_units
#Interpolate to domain
nc = netCDF4.Dataset('domain_cfg.nc')
lon = np.mean(nc.variables['nav_lon'][:],axis=0)
lat = np.mean(nc.variables['nav_lat'][:],axis=1)
nc.close()
ds = ds.interp(y=lat,x=lon)

#Calculate trends and extrapolate to 2020
ds = ds.reindex({'time':np.arange(1985,2021)})
Nyears_ext = len(ds.time)
for v in ['N3_flux','N4_flux']:
    c,m = trend_coef(ds[v].isel(time=slice(0,Nyears)).values)
    for i in range(Nyears,Nyears_ext):
        ds[v][i,:,:] = c + m*i



#Add global attributes
ds.attrs['title'] = 'Nitrogen Deposition for SANH domain provided by ISIMP'
ds = ds.assign_coords({'time':pd.date_range(str(ds.time.values[0]),str(ds.time.values[-1]),freq='YS')})

#Save Out
ds.to_netcdf('Ndep.nc')

for year,idx in ds.groupby('time.year').groups.items():
    ofile=f'Ndep_y%s.nc' %year
    print('Saving '+ofile)
    ds.isel(time=idx).to_netcdf(ofile)


