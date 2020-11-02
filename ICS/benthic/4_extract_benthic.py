import netCDF4
import numpy as np
import pandas as pd
import glob
from scipy.interpolate import Rbf

import matplotlib.pyplot as plt

fabm_blist = {
    'Y2':'c', 'Y3':'c', 'Y4':'c', 'H1':'c', 'H2':'c', \
    'K3':'n', 'K4':'n', 'K1':'p', 'K5':'s', 'G2':'o', 'G3':'c', \
    'Q1':{'c','n','p'}, 'Q6':{'c','n','p','s', \
        'pen_depth_c','pen_depth_n','pen_depth_p','pen_depth_s'}, \
    'Q7':{'c','n','p', 'pen_depth_c','pen_depth_n','pen_depth_p'}, \
    'Q17':{'c','n','p'}, 'bL2':'c'}
cols = ['lon','lat']
for v in sorted(fabm_blist):
    for c in fabm_blist[v]:
        cols.append('%s_%s' %(v,c))

t_idx = 469

df = pd.DataFrame(columns = cols)

flist = sorted(glob.glob('**/output/SANH_7d_mean.nc'))

for f in flist:
    print(f)
    dat = np.zeros(len(cols))
    nc = netCDF4.Dataset(f)
    dat[0] = nc.variables['lon'][:]
    dat[1] = nc.variables['lat'][:]
    for i,v in enumerate(cols[2:]):
        dat[i+2] = nc.variables[v][t_idx]
    df = df.append(pd.Series(dat, index=df.columns),ignore_index=True)
    nc.close()

nc = netCDF4.Dataset('/work/n01/n01/dapa/SANH/BGCsetup/ICS/bgc_ini.nc')
lon = nc.variables['nav_lon'][:]
lat = nc.variables['nav_lat'][:]


ncd = netCDF4.Dataset('/work/n01/n01/dapa/SANH/BGCsetup/ICS/domain_cfg.nc')
h = ncd.variables['bottom_level'][:]
h = np.ma.masked_where(h==0,h)

for v in cols[2:]:
    rbf = Rbf(df['lon'].values,df['lat'].values,df[v].values,function='gaussian')
    dat = rbf(lon,lat)
    dat[dat<0] = 0
    dat = np.ma.masked_array(dat,mask=h.mask)
    plt.figure()
    plt.pcolormesh(lon,lat,dat)
    plt.colorbar()
    plt.title(v+', prior constant value = '+str(nc.variables['fabm_st2Dn'+v][0,50,50]))
    plt.savefig(v+'.png')
    plt.close()


bd['fabm_st2Dn%s_%s' %(v,c)
