'''
Script to add benthic initial conditions from GOTM runs to ACCORD domain
'''
import netCDF4
import numpy as np

##########################
# Create/Open File
##########################
ncbath = netCDF4.Dataset('bathy_meter.nc')
h = ncbath.variables['Bathymetry'][:][np.newaxis,:]
ncbath.close()

nc = netCDF4.Dataset('domain_cfg.nc')
bl = nc.variables['bottom_level'][:]
bl[bl==74] -= 1
nc.close()

outfile = 'restart_trc.nc'
nco = netCDF4.Dataset(outfile,'a')

pf = 'fabm_st2Dn'

##########################
# Set Zoobenthos
# Source - Yuri
##########################
print('Deposit Feeders')
nco.variables[pf+'Y2_c'][:] = np.ma.filled(8834.4 * h**(-0.1651), fill_value=0)

print('Filter Feeders')
dat = -1300 * np.log(h) + 8830.8
dat[dat<0] = 0
nco.variables[pf+'Y3_c'][:] = np.ma.filled(dat,fill_value=0)

print('Meiobenthos')
nco.variables[pf+'Y4_c'][:] = 0.1689 * h + 55.342

##########################
# Set Bacteria
# Source - Yuri
##########################

print('Aerobic Bacteria')
nco.variables[pf+'H1_c'][:] = 0.61 * h + 23.98

print('Anaerobic Bacteria')
dat = -156.98 * np.log(h) + 1139.8
dat[dat<0] = 0
nco.variables[pf+'H2_c'][:] = np.ma.filled(dat,fill_value=0)

##########################
# Set Inorganic Matter - 
# Nutrients, Oxygen, DIC and NO2
# Source - Approximate equilibrium concentration from lowest pelagic
#          including porosity and benthic thickness
##########################

p = 0.4 # From fabm.yaml
z = 0.3 # benthic thickness (m)

print('Nitrogen')
v = np.squeeze(nco.variables['TRNN3_n'][:])
nco.variables[pf+'K3_n'][:] = (1/p)*z*np.take_along_axis(v, bl, axis=0)

print('Ammonium')
v = np.squeeze(nco.variables['TRNN4_n'][:])
nco.variables[pf+'K4_n'][:] = (1/p)*z*np.take_along_axis(v, bl, axis=0)

print('Phosphate')
v = np.squeeze(nco.variables['TRNN1_p'][:])
nco.variables[pf+'K1_p'][:] = (1/p)*z*np.take_along_axis(v, bl, axis=0)

print('Silicate')
v = np.squeeze(nco.variables['TRNN5_s'][:])
nco.variables[pf+'K5_s'][:] = (1/p)*z*np.take_along_axis(v, bl, axis=0)

print('Oxygen')
v = np.squeeze(nco.variables['TRNO2_o'][:])
nco.variables[pf+'G2_o'][:] = (1/p)*z*np.take_along_axis(v, bl, axis=0)

nco.variables[pf+'G2_o_deep'][:] = 0*h

print('DIC')
v = np.squeeze(nco.variables['TRNO3_c'][:])
nco.variables[pf+'G3_c'][:] = (1/p)*z*np.take_along_axis(v, bl, axis=0)

print('NO2')
nco.variables[pf+'ben_nit_G4n'][:] = 0*h

##########################
# Set Organic Matter
# Source - Yuri
##########################

print('Dissolved Detrital')
nco.variables[pf+'Q1_c'][:] = np.ma.filled(828.74 * h**-0.6246, fill_value=0)
nco.variables[pf+'Q1_n'][:] = np.ma.filled(21.103 * h**-0.6882, fill_value=0)
nco.variables[pf+'Q1_p'][:] = np.ma.filled(1.60278 * h**-0.6725, fill_value=0)

print('Particulate')
nco.variables[pf+'Q6_c'][:] = 0.1 * np.ma.filled(-1069 * np.log(h) + 10900, fill_value=0)
nco.variables[pf+'Q6_n'][:] = 0.1 * np.ma.filled(-7.6368 * np.log(h) + 78.564, fill_value=0)
nco.variables[pf+'Q6_p'][:] = 0.1 * np.ma.filled(-0.545 * np.log(h) + 6.0114, fill_value=0)
nco.variables[pf+'Q6_s'][:] = 0.1 * np.ma.filled(-64.598 * np.log(h) + 391.61, fill_value=0)
nco.variables[pf+'Q6_pen_depth_c'][:] = 0.0486 * h**0.103
nco.variables[pf+'Q6_pen_depth_n'][:] = 0.0486 * h**0.104
nco.variables[pf+'Q6_pen_depth_p'][:] = 0.0484 * h**0.1042
nco.variables[pf+'Q6_pen_depth_s'][:] = 1e-5 * h + 0.0232

print('Refractory')
nco.variables[pf+'Q7_c'][:] = np.ma.filled(50 * nco.variables[pf+'Q6_c'][:], fill_value=0)
nco.variables[pf+'Q7_n'][:] = np.ma.filled(50 * nco.variables[pf+'Q6_n'][:], fill_value=0)
nco.variables[pf+'Q7_p'][:] = np.ma.filled(50 * nco.variables[pf+'Q6_p'][:], fill_value=0)
nco.variables[pf+'Q7_pen_depth_c'][:] = 1e-5 * h + 0.0155
nco.variables[pf+'Q7_pen_depth_n'][:] = 8e-6 * h + 0.0155
nco.variables[pf+'Q7_pen_depth_p'][:] = 0.0495 * h**0.0965

print('Buried')
nco.variables[pf+'Q17_c'][:] = 0 * h
nco.variables[pf+'Q17_n'][:] = 0 * h
nco.variables[pf+'Q17_p'][:] = 0 * h

print('Horizons')

D1 = 0.0026 * h**0.3286 
D1[D1<0.01] = 0.01 #Enforce minimum depth
nco.variables[pf+'ben_col_D1m'][:] = D1

D2 = 0.011 * h**0.4018
D2[D2<0.01] = 0.01 #Enforce minimum depth 1cm
tot = D1 + D2
D2[tot>0.3] = 0.3 - D1[tot>0.3] # Enforce total thickness less than 30cm
nco.variables[pf+'ben_col_D2m'][:] = D2

################################################################################
print('Calcite')
nco.variables[pf+'bL2_c'][:] = 0 * h + 0.1


#############################################################################

print('Filling Before Fields')
fields = list(filter(lambda x: x.startswith('fabm_st2Dn'), nco.variables.keys()))
for i in fields:
    nco.variables[i.replace('st2Dn','st2Db')][:] = nco.variables[i][:]
nco.sync()

print('Complete')
nco.close()
