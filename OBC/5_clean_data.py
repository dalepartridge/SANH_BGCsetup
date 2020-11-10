import netCDF4
import glob
import numpy as np

files = glob.glob('bdyfiles/sanh_bdytrc*.nc')

for f in files:
    nc = netCDF4.Dataset(f,'a')
    v = nc.variables['nitrate'][:]
    for i in range(50):
        x = np.percentile(v[0,i,0,:],5)
        v[0,i,0,:][v[0,i,0,:]<x] = x
    nc.variables['nitrate'][:] = v
    v = nc.variables['silicate'][:]
    for i in range(50):
        x = np.percentile(v[0,i,0,:],5)
        v[0,i,0,:][v[0,i,0,:]<x] = x
    nc.variables['silicate'][:] = v
    v = nc.variables['phosphate'][:]
    for i in range(50):
        x = np.percentile(v[0,i,0,:],5)
        v[0,i,0,:][v[0,i,0,:]<x] = x
    nc.variables['phosphate'][:] = v
    v = nc.variables['oxygen'][:]
    for i in range(50):
        x = np.percentile(v[0,i,0,:],5)
        v[0,i,0,:][v[0,i,0,:]<x] = x
    nc.variables['oxygen'][:] = v
    nc.close()

