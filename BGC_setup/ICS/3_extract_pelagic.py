'''
Script to compile pelagic initial conditions from variety of sources into a single file, with some quality checks, for the ACCORD domain
'''

import netCDF4
import numpy as np

#Load Density
nc = netCDF4.Dataset('density.nc')
dens = np.squeeze(nc.variables['rhop'][:])
nc.close()

outfile = 'restart_trc.nc'
nco = netCDF4.Dataset(outfile,'a')

##########################
# Set Nutrients + Oxygen
# Source - WOA18
##########################
print('Compiling pelagic variables into '+outfile)

# Nitrate
print('Nitrate')
nci = netCDF4.Dataset('pelagic/pelagic_ICs.nc')
dat = np.ma.filled(nci.variables['N3_n'][:][np.newaxis,:],fill_value=0)
nco.variables['TRNN3_n'][:] = dat

t,z,y,x = dat.shape
unit = np.ones((dat.shape))

# Phosphate
print('Phosphate')
nco.variables['TRNN1_p'][:] = np.ma.filled(nci.variables['N1_p'][:][np.newaxis,:],fill_value=0)

# Silicate
print('Silicate')
nco.variables['TRNN5_s'][:] = np.ma.filled(nci.variables['N5_s'][:][np.newaxis,:],fill_value=0)

# Oxygen
print('Dissolved Oxygen')
nco.variables['TRNO2_o'][:] = np.ma.filled(nci.variables['O2_o'][:][np.newaxis,:],fill_value=0)

nco.sync()
################################################
# Set Alkalinity and Dissolved inorganic carbon
# Source - GLODAP
################################################

# Total Alkalinity
print('Total Alkalinity')
nco.variables['TRNO3_TA'][:] = np.ma.filled(nci.variables['O3_TA'][:][np.newaxis,:],fill_value=0)

print('DIC')
nco.variables['TRNO3_c'][:] = np.ma.filled(nci.variables['O3_c'][:][np.newaxis,:],fill_value=0)

##########################
# Set Light Attenuation
# Source - PML
##########################
print('ADY') 
dat = nci.variables['light_ADY'][:]
nco.variables['TRNlight_ADY'][:] = np.ma.filled(np.tile(dat,(z,1,1))[np.newaxis,:,:,:],fill_value=0)

nco.sync()
##########################################################
# Set homogeneous fields - Ammonium & DOC
# Source - Yuri Artioli
########################################################


print('Ammonium')
nco.variables['TRNN4_n'][:] = 0.25 * np.ma.filled(nco.variables['TRNN3_n'][:],fill_value=0) 

print('Dissolved Organic Carbon')
nco.variables['TRNR1_c'][:] = 12 * unit
nco.variables['TRNR1_n'][:] = 0.151 * unit
nco.variables['TRNR1_p'][:] = 0.0094 * unit
print('Semi-labile Organic Carbon')
nco.variables['TRNR2_c'][:] = 60 * unit
print('Semi-refractory Organic Carbon')
nco.variables['TRNR3_c'][:] = 60 * unit

print('Calcite')
nco.variables['TRNL2_c'][:] = 0.1 * unit

print('Bacteria')
nco.variables['TRNB1_c'][:] =  3.7523 * unit # Check with Luca if this is a sensible value
nco.variables['TRNB1_n'][:] =  0.0167 * nco.variables['TRNB1_c'][:] # B1: qnc in fabm.yaml
nco.variables['TRNB1_p'][:] =  0.0019 * nco.variables['TRNB1_c'][:] # B1: qpc in fabm.yaml

nco.sync()

########################################################
# Set phytoplankton values
# Source - OC-CCI monthly image for Chloraphyll
#          Chloraphyll conversion from NEMO-ERSEM 
#          Redfield ratio for nitrogen, phosphate, silicate
########################################################

dat = nci.variables['Chl_Tot'][:][np.newaxis,:]
# Set uniform down to pycnocline, exponentially step down below
Chl_tot = np.tile(dat,(z,1,1))
pycno = np.argmax(np.diff(dens,axis=0),axis=0)
for i in np.arange(x):
    for j in np.arange(y):
        k = pycno[j,i]
        p1 = Chl_tot[k,j,i]
        p2 = 0.0001
        Chl_tot[pycno[j,i]:,j,i] = p1*np.exp((np.log(p2/p1)/(z-k))*np.arange(1,z-k+1)) 
Chl_tot = np.ma.filled(Chl_tot[np.newaxis,:,:,:],fill_value=0)

# Split Chl using Brewin2010 Eq13-16, parameterised using Brewin2012 Table 1
Chl_pn = 0.937*(1-np.exp(-1.033*Chl_tot))
Chl_dia = 2.0/3.0 * (Chl_tot - Chl_pn) #Split micro 2:1 into diatom and micro
Chl_mic = 1.0/3.0 * (Chl_tot - Chl_pn)
Chl_pic = 0.170*(1-np.exp(-4.804*Chl_tot))
Chl_nan = Chl_pn - Chl_pic 

print('Diatom Phytoplankton')
nco.variables['TRNP1_Chl'][:] = Chl_dia
carbon = 25*Chl_dia # Chl:C = 0.04
nco.variables['TRNP1_c'][:] = carbon
nco.variables['TRNP1_n'][:] = (carbon/12.0)*(16.0/106.0)
nco.variables['TRNP1_p'][:] = (carbon/12.0)*(1.0/106.0)
nco.variables['TRNP1_s'][:] = (carbon/12.0)*(15.0/106.0)

print('Nano Phytoplankton')
nco.variables['TRNP2_Chl'][:] = Chl_nan
carbon = 50*Chl_nan # Chl:C = 0.02
nco.variables['TRNP2_c'][:] = carbon
nco.variables['TRNP2_n'][:] = (carbon/12.0)*(16.0/106.0)
nco.variables['TRNP2_p'][:] = (carbon/12.0)*(1.0/106.0)

print('Pico Phytoplankton')
nco.variables['TRNP3_Chl'][:] = Chl_pic
carbon = 80*Chl_pic # Chl:C = 0.0125
nco.variables['TRNP3_c'][:] = carbon
nco.variables['TRNP3_n'][:] = (carbon/12.0)*(16.0/106.0)
nco.variables['TRNP3_p'][:] = (carbon/12.0)*(1.0/106.0)

print('Micro Phytoplankton')
nco.variables['TRNP4_Chl'][:] = Chl_mic
carbon = 30*Chl_mic # Chl:C = 0.03'
nco.variables['TRNP4_c'][:] = carbon
nco.variables['TRNP4_n'][:] = (carbon/12.0)*(16.0/106.0)
nco.variables['TRNP4_p'][:] = (carbon/12.0)*(1.0/106.0)

nco.sync()

########################################################
# Set zooplankton and POM values
# Source - iMarNet Model (Provided by LEDM)
########################################################

meso_zoo = ['TRNZ4_c']
micro_zoo = ['TRNZ5_c','TRNZ5_n','TRNZ5_p']
heteroflagellates = ['TRNZ6_c','TRNZ6_n','TRNZ6_p']
small_pom = ['TRNR4_c','TRNR4_n','TRNR4_p']
med_pom = ['TRNR6_c','TRNR6_n','TRNR6_p','TRNR6_s']
large_pom = ['TRNR8_c','TRNR8_n','TRNR8_p','TRNR8_s']
vars = meso_zoo + micro_zoo + heteroflagellates + \
        small_pom + med_pom + large_pom

print('Zooplankton and POM')
for var in vars:
    nco.variables[var][:] = np.ma.filled(nci.variables[var[3:]][:][np.newaxis,:],fill_value=0)
nco.sync()

##########################################################

print('Filling Before Fields')
fields = list(filter(lambda x: x.startswith('TRN'), nco.variables.keys()))
for i in fields:
    nco.variables[i.replace('TRN','TRB')][:] = nco.variables[i][:]
nco.sync()

print('Complete')
nco.close()
