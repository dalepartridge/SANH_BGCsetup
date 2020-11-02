import netCDF4
import numpy as np
from sklearn.cluster import KMeans
import coast
import csv

# Read in bathymetry, lat, lon
nc = netCDF4.Dataset('bathy_meter.nc')
h = nc.variables['Bathymetry'][:]
lon = nc.variables['nav_lon'][:]
lat = nc.variables['nav_lat'][:]
nc.close()

h = np.ma.masked_where(h==0,h)
hc = h.compressed()
lonc = lon[~h.mask].compressed()
latc = lat[~h.mask].compressed()
X = np.vstack([lonc,latc]).T

# Calculate weights based on depth
hci = 1/hc
w_d = (hci - np.min(hci)) * 1 / (np.max(hci) - np.min(hci))

# Read in Bottom level
nc = netCDF4.Dataset('domain_cfg.nc')
h_idx = np.squeeze(nc.variables['bottom_level'][:]-1)
nc.close()

# Read in bottom temp
nc = netCDF4.Dataset('monthly_temperature.nc')
temp = np.mean(nc.variables['toce'][:],axis=0)
T = 0*h
for i in range(T.shape[0]):
    for j in range(T.shape[1]):
        if ~T.mask[i,j]:
            T[i,j] = temp[h_idx[i,j],i,j]
tc = T.compressed()

# Calculate weights based on bottom temperature
w_t = (tc - np.min(tc)) * 1 / (np.max(tc) - np.min(tc))

#Perform weighted KMeans sampling
KM = KMeans(n_clusters=100)
KM.fit(X,sample_weight=w_d+w_t)
c_dt = KM.cluster_centers_

# Convert back to indices
d = coast.NEMO(None,'domain_cfg.nc')

mp = 0
with open('sample_points.csv', 'w', newline='') as csvfile:
    samp_writer = csv.writer(csvfile, delimiter=',')
    samp_writer.writerow(['LON_IDX','LAT_IDX'])
    for sp in c_dt:
        j,i = d.find_j_i(sp[1],sp[0])
        if np.ma.is_masked(h[j,i]):
            mp += 1
        else:
            samp_writer.writerow([i,j])
print('Sample points saved to file sample_points.csv, with '+str(mp)+' point(s) ignored for lying on land')
