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
nco.variables[pf+'Y2_c'][:] = 8834.4 * h**(-0.1651)

print('Filter Feeders')
nco.variables[pf+'Y3_c'][:] = -1300 * np.log(h) + 8830.8

print('Meiobenthos')
nco.variables[pf+'Y4_c'][:] = 0.1689 * h + 55.342

##########################
# Set Bacteria
# Source - Yuri
##########################

print('Aerobic Bacteria')
nco.variables[pf+'H1_c'][:] = 0.61 * h + 23.98

print('Anaerobic Bacteria')
nco.variables[pf+'H2_c'][:] = -156.98 * np.log(h) + 1139.8

##########################
# Set Inorganic Matter - 
# Nutrients, Oxygen, DIC and NO2
# Source - Approximate equilibrium concentration from lowest pelagic
#          including porosity and benthic thickness
##########################

p = 20 # From fabm.yaml
z = 0.3 # benthic thickness (m)

print('Nitrogen')
v = np.squeeze(nco.variables['TRNN3_n'][:])
nco.variables[pf+'K3_n'][:] = p*z*np.take_along_axis(v, bl, axis=0)

print('Ammonium')
v = np.squeeze(nco.variables['TRNN4_n'][:])
nco.variables[pf+'K4_n'][:] = p*z*np.take_along_axis(v, bl, axis=0)

print('Phosphate')
v = np.squeeze(nco.variables['TRNN1_p'][:])
nco.variables[pf+'K1_p'][:] = p*z*np.take_along_axis(v, bl, axis=0)

print('Silicate')
v = np.squeeze(nco.variables['TRNN5_s'][:])
nco.variables[pf+'K5_s'][:] = p*z*np.take_along_axis(v, bl, axis=0)

print('Oxygen')
v = np.squeeze(nco.variables['TRNO2_o'][:])
nco.variables[pf+'G2_o'][:] = p*z*np.take_along_axis(v, bl, axis=0)

nco.variables[pf+'G2_o_deep'][:] = 0*h

print('DIC')
v = np.squeeze(nco.variables['TRNO3_c'][:])
nco.variables[pf+'G3_c'][:] = p*z*np.take_along_axis(v, bl, axis=0)

print('NO2')
nco.variables[pf+'ben_nit_G4n'][:] = 0*h

##########################
# Set Organic Matter
# Source - Yuri
##########################

print('Dissolved Detrital')
nco.variables[pf+'Q1_c'][:] = 828.74 * h**-0.6246
nco.variables[pf+'Q1_n'][:] = 21.103 * h**-0.6882
nco.variables[pf+'Q1_p'][:] = 1.60278 * h**-0.6725

print('Particulate')
nco.variables[pf+'Q6_c'][:] = -1069 * np.log(h) + 10900
nco.variables[pf+'Q6_n'][:] = -7.6368 * np.log(h) + 78.564
nco.variables[pf+'Q6_p'][:] = -0.545 * np.log(h) + 6.0114
nco.variables[pf+'Q6_s'][:] = -64.598 * np.log(h) + 391.61
nco.variables[pf+'Q6_pen_depth_c'][:] = 0.0486 * h**0.103
nco.variables[pf+'Q6_pen_depth_n'][:] = 0.0486 * h**0.104
nco.variables[pf+'Q6_pen_depth_p'][:] = 0.0484 * h**0.1042
nco.variables[pf+'Q6_pen_depth_s'][:] = 1e-5 * h + 0.0232

print('Refractory')
nco.variables[pf+'Q7_c'][:] = 50 * nco.variables[pf+'Q6_c'][:]
nco.variables[pf+'Q7_n'][:] = 50 * nco.variables[pf+'Q6_n'][:]
nco.variables[pf+'Q7_p'][:] = 50 * nco.variables[pf+'Q6_p'][:]
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
