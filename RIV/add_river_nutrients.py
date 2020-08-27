'''
Script to calculate and fill river files with oxygen, DIC and total alkalinity

Oxygen - Values calculated at saturation as function of temperature based on 
         formula from https://www.waterontheweb.org/under/waterquality/oxygen.html
DIC - Values calculated using temperature, zero salinity, alkalinity and pCO2 
      based upon calculation in ERSEM carbonate module (ICALC=4)
TA - Set to a constant mmol / m3 value of 1500, based on GEMS/GLORI project
'''

import netCDF4
import numpy as np
import datetime as dt
import xarray

ncd = netCDF4.Dataset('domain_cfg.nc')
SA = ncd.variables['e1t'][:]*ncd.variables['e2t'][:] 
lon = ncd.variables['nav_lon'][:]
lat = ncd.variables['nav_lat'][:]
ncd.close()

# Define year to calculate for / begin loop over years
syear=1993
eyear=2010
for year in np.arange(syear,eyear+1): #Loop until end of script
    print('Adding river nutrients for {}'.format(year))
    #################### Load air temperature ##############################
    nct = xarray.open_dataset('/work/n01/n01/jenjar93/SANH_HINDCAST_CMEMS/SURFACE_FORCING/ERA5_T2M_y{}.nc'.format(year))
    Tlon = nct['lon']
    Tlat = nct['lat']
    Tavg = nct.resample(time='1MS').mean()
    
    #################### Load river runoff #############################
    ncr = netCDF4.Dataset('rivers_y{}.nc'.format(year),'a')
    r = ncr.variables['rorunoff'][:]

    # Create new variables
    rdim = ncr.variables['rorunoff'].dimensions
    ncr.createVariable('DIOrunoff','double',rdim)
    ncr.createVariable('DICrunoff','double',rdim)
    ncr.createVariable('TArunoff','double',rdim)

    #################### Dissolved Oxygen ##############################
    dat = np.zeros(r.shape)
    for j in range(r.shape[1]):
        for i in range(r.shape[2]):
            if r[0,j,i] > 0:
                c = np.maximum(np.abs(Tlon-lon[j,i]),np.abs(Tlat-lat[j,i]))
                ll_idx = np.where(c == np.min(c))
                Tr = Tavg['T2M'][:,ll_idx[0][0],ll_idx[1][0]]
                dat[:,j,i] = ((np.exp(7.7117-1.31403*np.log(Tr+45.93))) * (1-np.exp(11.8571-(3840.7/(Tr+273.15)) - \
                              (216961/((Tr+273.15)**2)))) * (1-(0.000975-(0.00001426*Tr)+0.00000006436*(Tr**2)))) / \
                              (1-np.exp(11.8571-(3840.7/(Tr+273.15))-(216961/((Tr+273.15)**2)))) / \
                              (1-(0.000975-(0.00001426*Tr)+(0.00000006436*(Tr**2)))) # Dissolved oxygen at saturation (mg/L)

    dat *= (1000/32) # Convert to mmol/m3
    dat *= (r/1000) * SA # Convert to mmol/s

    ncr.variables['DIOrunoff'][:] = dat


    ###################### DIC ########################################
    def K (T):
        '''
        Function to calculate carbonate equilibirum constants at surface with S=0
        '''
        K0 = np.exp(93.4517*(100/T) - 60.2409 + 23.3585*np.log(T/100))
        K1 = 10**(126.34048 - 6320.813*(1/T) - 19.568224*np.log(T))  
        K2 = 10**(90.18333 - 5143.692*(1/T) - 14.613358*np.log(T))
        return K0, K1, K2

    #Load pCO2
    ncp = netCDF4.Dataset('/work/n01/n01/dapa/SANH/INPUTS/SBC/pCO2_y{}.nc'.format(year))
    pco2 = np.squeeze(ncp.variables['pCO2a'][:])
    ncp.close()

    TA = 1500

    dat = np.zeros(r.shape)
    for j in range(r.shape[1]):
        for i in range(r.shape[2]):
            if r[0,j,i] > 0:
                c = np.maximum(np.abs(Tlon-lon[j,i]),np.abs(Tlat-lat[j,i]))
                ll_idx = np.where(c == np.min(c))
                Tr = Tavg['T2M'][:,ll_idx[0][0],ll_idx[1][0]]
                k0,k1,k2 = K(Tr)
                Pr = (k1/k2)*k0*pco2[j,i]
                x = np.sqrt((8*TA+Pr)*Pr)
                dat[:,j,i] = TA/2 - Pr/8 + x/8 + pco2[j,i]*k0 

    dat *= (r/1000) * SA # Convert to mmol/s
    ncr.variables['DICrunoff'][:] = dat

    ################ Total Alkalinity ##################################
    # Alkalinity set to constant value

    dat = TA # mmol/m3
    dat *= (r/1000) * SA # Convert to mmol/s
    ncr.variables['TArunoff'][:] = dat

    ncr.close()

