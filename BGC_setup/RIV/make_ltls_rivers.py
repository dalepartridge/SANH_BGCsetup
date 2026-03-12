'''
Script to interpolate river data output from the LTLS model to the coastline
of the SANG domain. 

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
import scipy
import scipy.spatial as spatial
import tqdm
import geopandas as gpd
import xesmf
from shapely.geometry import Polygon
from shapely.vectorized import contains as scontains
from shapely.affinity import translate
import datetime
from pathlib import Path

def calc_DIC (T, pCO2, TA=1500):
    '''
    Function to calculate DIC using carbonate equilibirum constants at surface with S=0
    '''
    K0 = np.exp(93.4517*(100/T) - 60.2409 + 23.3585*np.log(T/100))
    K1 = 10**(126.34048 - 6320.813*(1/T) - 19.568224*np.log(T))
    K2 = 10**(90.18333 - 5143.692*(1/T) - 14.613358*np.log(T))
    Pr = (K1/K2)*K0*pCO2
    x = np.sqrt((8*TA+Pr)*Pr)
    DIC = TA/2 - Pr/8 + x/8 + pCO2*K0
    return DIC

def match_base_on_distance(source_df,target_df):
    "Based on https://stackoverflow.com/q/43020919/190597"
    "this match every river in the original dataset (IMAGE) to the location of the NEMO runoff locations (JRA)"
    #    source_df: Dataframa with Lat, Lon
    #    target_df: Dataframa with Lat, Lon
    R=6367
    phi = np.deg2rad(source_df['Latitude'])
    theta = np.deg2rad(source_df['Longitude'])
    source_df['x'] = R * np.cos(phi) * np.cos(theta)
    source_df['y'] = R * np.cos(phi) * np.sin(theta)
    source_df['z'] = R * np.sin(phi)
    phi = np.deg2rad(target_df['Latitude'])
    theta = np.deg2rad(target_df['Longitude'])
    target_df['x'] = R * np.cos(phi) * np.cos(theta)
    target_df['y'] = R * np.cos(phi) * np.sin(theta)
    target_df['z'] = R * np.sin(phi)
    
    #build the KDtree on the final grid, (i.e. JRA)
    tree = spatial.KDTree(target_df[['x', 'y','z']])
    
    # query the tree with the original dataset, i.e. IMAGE
    '''
    d, ix = tree.query(source_df[['x', 'y','z']], k=10)
    distance = d[:,0]
    index = ix[:,0]
    ks = np.zeros(len(ix))
    for i in tqdm.tqdm(np.arange(len(ix))):
        for k in np.arange(10):
            i_tar = int(target_df.iloc[[ix[i,k]]].loc[:,'x_idx'].values)
            j_tar = int(target_df.iloc[[ix[i,k]]].loc[:,'y_idx'].values)
            if (grd[j_tar,i_tar] == 1):
                index[i]=ix[i,k]
                distance[i]=d[i,k]
                ks[i]=k
                break
    '''
    distance, index = tree.query(source_df[['x', 'y','z']], k=1)

    return distance,index

def compress_to_dataframe(da):
    [x_idx,y_idx] = np.meshgrid(da.x,da.y)
    da['x_idx'] = (da.dims,x_idx)
    da['y_idx'] = (da.dims,y_idx)
    da = da.stack(dim_0=da.dims).reset_index('dim_0').drop_vars(da.dims)
    da = da.where(np.isfinite(da),drop=True) 
    return da.to_dataframe(name='coastline')

##############################################
scenario = 'BASELINE'
#scenario = 'CL'
fdir = 'RIVERS-LTLS-'+scenario
odir = '/work/n01/n01/dapa/SANH/INPUTS/RIV/'+scenario
Path(odir).mkdir(exist_ok=True)

ds_src = xr.open_mfdataset(fdir+'/mm*nc',combine='nested')
    
# Load SANH domain info and find coastline
grd = xr.open_dataset('domain_cfg.nc')
SA = (grd.e1t * grd.e2t).isel(t=0) # Cell area
grd = grd['bottom_level'].isel(t=0).assign_coords({'Latitude':grd.nav_lat,'Longitude':grd.nav_lon})
grd = xr.where(grd>0,1,-1)
#edges = grd - scipy.ndimage.binary_dilation(grd) #detect coastline in 2D array
#edges = edges.where(edges<0)
#target_df = compress_to_dataframe(edges)
edges = np.where(scipy.ndimage.sobel(grd)!=0,1,0)
a = xr.where((edges - grd) == 0,1,np.nan)

grd['edges'] = (('y','x'),a.values)
target_df = compress_to_dataframe(grd.edges)

# Load LTLS coastline mask
mask = xr.open_dataset('RIVERS-LTLS-BASELINE/sea_outflow_cells.nc')
mask['sea_outflow'][:,390:] = 0 #Mask Gulf of Thailand
mask = mask.fillna(0).rename_dims({'Longitude':'x','Latitude':'y'}).rename({'Longitude':'lon','Latitude':'lat'})
[Lon,Lat] = np.meshgrid(ds_src.Longitude,ds_src.Latitude)
mask = mask['sea_outflow'].assign_coords({'Latitude':(('y','x'),Lat),'Longitude':(('y','x'),Lon)}).drop(['lat','lon'])
mask = xr.where(mask.Longitude>grd.Longitude.min(),mask,0)
mask = xr.where(mask.Longitude<grd.Longitude.max(),mask,0)
mask = xr.where(mask.Latitude>grd.Latitude.min(),mask,0)
mask = xr.where(mask.Latitude<grd.Latitude.max(),mask,0)
source_df = compress_to_dataframe(mask.where(mask==1))

# Create mapping from LTLS to SANH 
distance,index = match_base_on_distance(source_df,target_df)
np.save('indexes.npy', index)
###########################

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
grd = xr.open_dataset('domain_cfg.nc')
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

ds_temp = xr.open_mfdataset('./T2M/ERA5_T2M_y*nc')
if scenario == 'BASELINE':
    ds_temp = ds_temp.resample(time='1MS').mean().isel(time=slice(12,None))
else:
    ds_temp = ds_temp.resample(time='1MS').mean().isel(time=slice(12*12,None))
ds_temp = ds_temp.rename_dims({'nLat':'y','nLon':'x'})
ds_temp = ds_temp.assign_coords({'lon': (('y','x'),ds_temp.lon.isel(time=0).values),
                           'lat': (('y','x'),ds_temp.lat.isel(time=0).values)})
regridder = xesmf.Regridder(ds_temp[['T2M']],ds.rename({'Latitude':'lat','Longitude':'lon'}),method='bilinear',extrap_method='nearest_s2d')
ds_T = xr.Dataset({'T2M':(('time','y','x'),regridder(ds_temp.T2M.values))},coords=ds.coords)
#Regrid ds_T

DIO = ((np.exp(7.7117-1.31403*np.log(ds_T.T2M+45.93))) * (1-np.exp(11.8571-(3840.7/(ds_T.T2M+273.15)) - \
         (216961/((ds_T.T2M+273.15)**2)))) * (1-(0.000975-(0.00001426*ds_T.T2M)+0.00000006436*(ds_T.T2M**2)))) / \
         (1-np.exp(11.8571-(3840.7/(ds_T.T2M+273.15))-(216961/((ds_T.T2M+273.15)**2)))) / \
         (1-(0.000975-(0.00001426*ds_T.T2M)+(0.00000006436*(ds_T.T2M**2)))) # Dissolved oxygen at saturation (mg/L)
DIO.to_netcdf('dio.nc')
ds['DIOrunoff'] = xr.where(ds.rorunoff>0, DIO * (1000/32) * (ds.rorunoff/1000) * SA, 0) # Convert from mg/L to mmol/s

# Add DIC
#Load pCO2
if scenario == 'BASELINE':
    ds_p = xr.open_mfdataset('../SBC/pCO2/pCO2_y*.nc').isel(t=slice(3,33)).rename({'t':'time'})
else:
    ds_p = xr.open_mfdataset('../SBC/pCO2/pCO2_y*.nc').isel(t=slice(14,33)).rename({'t':'time'})
ds_p_int = ds_p.interp(time=ds_T.time)

DIC = calc_DIC(ds_T.T2M, ds_p_int.pCO2a)
DIC.to_netcdf('dic.nc')
ds['DICrunoff'] = xr.where(ds.rorunoff>0,DIC * (ds.rorunoff/1000) * SA, 0)

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







