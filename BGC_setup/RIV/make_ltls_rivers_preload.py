'''
Script to interpolate river data output from the LTLS model to the coastline
of the SANH domain. 

Additional functions calculate and fill river files with oxygen, DIC and total alkalinity

Oxygen - Values calculated at saturation as function of temperature based on 
         formula from https://www.waterontheweb.org/under/waterquality/oxygen.html
DIC - Values calculated using temperature, zero salinity, alkalinity and pCO2 
      based upon calculation in ERSEM carbonate module (ICALC=4)
TA - Set to a constant mmol / m3 value of 1500, based on GEMS/GLORI project
'''
import xarray as xr
import pandas as pd
import numpy as np # import arange,meshgrid, cos, sin,deg2rad,isfinite, zeros, logical_or, array
import geopandas as gpd
import tqdm
from shapely.geometry import Polygon
from shapely.vectorized import contains as scontains
from shapely.affinity import translate
import datetime
from pathlib import Path

##############################################
#scenario = 'BASELINE'
#scenario = 'CL'
scenario = 'MTFRPLUS'
fdir = 'RIVERS-LTLS-'+scenario
odir = '/work/n01/n01/dapa/SANH/INPUTS/RIV/'+scenario
Path(odir).mkdir(exist_ok=True)
    
# Load SANH domain info
grd = xr.open_dataset('domain_cfg.nc')
SA = (grd.e1t * grd.e2t).isel(t=0) # Cell area

# Load mapping from LTLS to SANH 
index = np.load('indexes.npy')
source_df = pd.read_csv('source_df.csv')
target_df = pd.read_csv('target_df.csv')

###########################

ds_src = xr.open_mfdataset(fdir+'/mm*nc',combine='nested')
if scenario == 'BASELINE':
    ds_src = ds_src.isel(Time=slice(9*12,None)).fillna(0) #Select 1993-2015 data and fill missing
else:
    ds_src = ds_src.fillna(0) #fill missing

time = np.array([datetime.datetime.strptime(str(int(x)),'%Y%m') for x in ds_src.Time.values])

vars = {'rorunoff':'mmflow',
        'NO3runoff':'mmflux_NO3_N',
        'NH4runoff':'mmflux_NH4_N',
        'DONrunoff':'mmflux_DON',
        'DOPrunoff':'mmflux_TDP'}
ds = xr.Dataset(coords={'time':time,'Latitude':grd.nav_lat,'Longitude':grd.nav_lon})
for v in vars:
    ds[v] = (('time','y','x'),np.zeros((len(time),len(ds.y),len(ds.x))))

for i,idx in enumerate(tqdm.tqdm(index)):
    i_src = int(source_df.iloc[[i]].loc[:,'x_idx'].values)
    j_src = int(source_df.iloc[[i]].loc[:,'y_idx'].values)
    i_tar = int(target_df.iloc[[idx]].loc[:,'x_idx'].values)
    j_tar = int(target_df.iloc[[idx]].loc[:,'y_idx'].values)
    for v in vars:
        ds[v][:,j_tar,i_tar] += ds_src[vars[v]][:,j_src,i_src].values


# Convert runoff from m3/s to kg/m2/s
ds['rorunoff'] = ds['rorunoff'] * 1000 / SA

# Note - split total dissolved phosphorus into DIP / DOP based upon globalnews ratio
ds['DOPrunoff'] = ds.DOPrunoff / 13.46
ds['DIPrunoff'] = 12.46*ds.DOPrunoff

# Note - create silicate field from the globalnews Si:N ratio
ds['DSirunoff'] = 10.97*ds.NO3runoff

######################################
# Add Oxygen
DIO = xr.open_dataset('dio.nc')
if scenario != 'BASELINE':
    DIO = DIO.isel(time=slice(12*11,None))

ds['DIOrunoff'] = xr.where(ds.rorunoff>0, DIO.DIO * (1000/32) * (ds.rorunoff/1000) * SA, 0) # Convert from mg/L to mmol/s

# Add DIC
DIC = xr.open_dataset('dic.nc')

if scenario != 'BASELINE':
    DIC = DIC.isel(time=slice(12*11,None))


ds['DICrunoff'] = xr.where(ds.rorunoff>0,DIC.DIC * (ds.rorunoff/1000) * SA, 0)

# Add Total Alkalinity in mmol/s
ds['TArunoff'] = 1500 * (ds.rorunoff/1000) * SA

#####################################
#Create regional rivers
# Define location of shapefiles
shapefile_dir = './EEZ/'
dom = ['india','bangladesh','myanmar','pakistan','sri-lanka']
off = 2*1.0/12.0
xoff = [1, 1, -1, -1]
yoff = [1, -1, 1, -1]
lon = grd.nav_lon.values
lat = grd.nav_lat.values

for d in dom:
    sf = gpd.read_file(shapefile_dir+d+'/eez.shp')
    poly = sf['geometry'][0]

    mask = scontains(poly, lon, lat)
    for x,y in zip(xoff,yoff):
        mask = np.logical_or(mask, scontains(translate(poly,yoff=y*off,xoff=x*off),lon,lat))
    ds['DIN_'+d[:3]] = mask*(ds.NO3runoff + ds.NH4runoff)
    ds['DON_'+d[:3]] = mask*ds.DONrunoff

# Set boundary region to zero
vars = [ 'rorunoff','NO3runoff','NH4runoff','DONrunoff','DOPrunoff','DIPrunoff','DSirunoff','DIOrunoff','DICrunoff','TArunoff','DIN_ind','DON_ind','DIN_ban','DON_ban','DIN_mya','DON_mya','DIN_pak','DON_pak','DIN_sri','DON_sri']
for v in vars:
    ds[v][:,:,:12] = 0
    ds[v][:,:,-12:] = 0
    ds[v][:,:12,:] = 0
    ds[v][:,-12:,:] = 0


#######################################
for year,idx in ds.groupby('time.year').groups.items():
    ofile=f'%s/rivers_y%s.nc' %(odir,year)
    ds.isel(time=idx).to_netcdf(ofile,unlimited_dims='time')







