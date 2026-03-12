import xarray as xr
import netCDF4
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
import xesmf

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

# Load Dataset
fdir = '/work/n01/n01/dapa/SANH/RAW_DATA/SBC/SANH-Ndep/ULLOW/'
ds = xr.open_dataset(fdir+'SANH_Ndep_nhx_1993-2020.nc',decode_times=False)
ds['N4_flux'] = ds.wet + ds.dry

ds_temp = xr.open_dataset(fdir+'SANH_Ndep_noy_1993-2020.nc',decode_times=False)
ds['N3_flux'] = ds_temp.wet + ds_temp.dry
ds = ds[['N3_flux','N4_flux']]

ds['time'] = np.array([datetime(1993,1,15) + relativedelta(months=i) for i in ds.time])

#Convert units
tar_units = 'mmol / m**2 / s'
ds['N3_flux'].values = convert_mass_to_mol(ds.N3_flux.values,'g / m**2 / month',get_molar_mass('N'),target_units=tar_units)

ds['N4_flux'].values = convert_mass_to_mol(ds.N4_flux.values,'g / m**2 / month',get_molar_mass('N'),target_units=tar_units)



#Interpolate to domain
grd = xr.open_dataset('domain_cfg.nc')
ds_regrid = xr.Dataset(coords={'time':ds.time,'lat':grd.nav_lat,'lon':grd.nav_lon})
regridder = xesmf.Regridder(ds,ds_regrid,method='bilinear',extrap_method='nearest_s2d')
ds = regridder(ds)


#Add attributes
ds.N3_flux.attrs['units']=tar_units
ds.N4_flux.attrs['units']=tar_units
ds.attrs['title'] = 'Nitrogen Deposition for SANH domain provided by CEH'

for year,idx in ds.groupby('time.year').groups.items():
    ofile=f'/work/n01/n01/dapa/SANH/INPUTS/SBC/BGC/BASELINE/Ndep_y%s.nc' %year
    ds.isel(time=idx).to_netcdf(ofile,unlimited_dims='time')


