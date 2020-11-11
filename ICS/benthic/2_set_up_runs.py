import numpy as np
GY_cfg = f90nml.read('./gotmrun.nml')
import os
import coast
import pandas as pd
import datetime as dt
import yaml
import netCDF4

#Load indexes for runs
idx = np.genfromtxt('sample_points.csv', delimiter=',',skip_header=1)

#Load physics data
t = coast.NEMO('toce/*.nc','domain_cfg.nc', multiple=True)
z = coast.NEMO('ssh/*.nc','domain_cfg.nc', multiple=True)

h = coast.NEMO('bathy_meter.nc','domain_cfg.nc')

#Load met data
met = coast.NEMO('sbc/ERA5_MSDWSWRF*.nc',multiple=True)
met.dataset['time'] = met.dataset['time'].dt.round('T')
for v in ['SPH','T2M','U10','V10']:
    a = coast.NEMO('sbc/ERA5_'+v+'*.nc',multiple=True)
    a.dataset['time'] = a.dataset['time'].dt.round('T')
    met.dataset = met.dataset.assign(a.dataset)
met.set_dimension_names({'nLon':'x_dim','nLat':'y_dim', 'time':'t_dim'})
met.dataset = met.dataset.assign(longitude=met.dataset.lon.isel(t_dim=0),latitude=met.dataset.lat.isel(t_dim=0)) 

#Load BGC data
bgc = coast.NEMO('bgc/bgc_ini.nc','domain_cfg.nc')
relax_rate = 1.0 / (3*86400)
sdate = dt.datetime(2000,1,1)
plist = {'N3n':'TRNN3_n', 'N4n':'TRNN4_n', 'N1p':'TRNN1_p', 'N5s':'TRNN5_s', 'O2o':'TRNO2_o', 'O3c':'TRNO3_c'}
fabm_plist = {
    'N3':'n', 'N4':'n', 'N1':'p', 'N5':'s', 'O2':'o', 'O3':'c', \
    'P1':{'Chl','c','n','p','s'}, 'P2':{'Chl','c','n','p'}, \
    'P3':{'Chl','c','n','p'}, 'P4':{'Chl','c','n','p'}, \
    'Z4':'c', 'Z5':{'c','n','p'}, 'Z6':{'c','n','p'}, \
    'R1':{'c','n','p'}, 'R2':{'c'}, 'R3':{'c'}, \
    'R4':{'c','n','p'}, 'R6':{'c','n','p','s'}, \
    'R8':{'c','n','p','s'}, 'L2':'c', 'B1':{'c','n','p'}}
fabm_blist = {
    'Y2':'c', 'Y3':'c', 'Y4':'c', 'H1':'c', 'H2':'c', \
    'K3':'n', 'K4':'n', 'K1':'p', 'K5':'s', 'G2':'o', 'G3':'c', \
    'Q1':{'c','n','p'}, 'Q6':{'c','n','p','s', \
        'pen_depth_c','pen_depth_n','pen_depth_p','pen_depth_s'}, \
    'Q7':{'c','n','p', 'pen_depth_c','pen_depth_n','pen_depth_p'}, \
    'Q17':{'c','n','p'}, 'ben_col':{'D1m','D2m'}, 'bL2':'c'}
FY_cfg = yaml.load(open('./fabm.yaml','r'),Loader=yaml.FullLoader)

GY_cfg = f90nml.read('./gotmrun.nml')

for ix in range(len(idx)):
    i = int(idx[ix,0])
    j = int(idx[ix,1])

    odir = 'RUN_%03i' %(ix+1)
    #Create directory
    os.system('mkdir '+odir)
    rf = open(odir+'/README.txt','w')
    rf.write('GOTM simulation on SANH domain at point i=%i, j=%i' %(i,j))
    rf.close()   

    #Create ssh file
    zd = z.dataset.zos.isel(y_dim=j,x_dim=i)
    zd = zd.reset_coords(['longitude','latitude'],drop=True).to_dataframe()
    zd['time'] = zd['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    zd.to_csv(odir+'/zeta.dat',sep='\t',index=False,header=False)

    #Create temp/salt profiles
    td = t.dataset.isel(y_dim=j,x_dim=i)
    tf = open(odir+'/temp_profile','w')
    sf = open(odir+'/salt_profile','w')
    for k,time in enumerate(pd.to_datetime(td.time.values)):
        tf.write('%s %i 2\n' %(time, len(td.z_dim)))
        sf.write('%s %i 2\n' %(time, len(td.z_dim)))
        td_k = td.isel(t_dim=k)
        for n,dep in enumerate(td.depth_0.values):
            tf.write('%f %f\n' %(-dep,td_k.toce.isel(z_dim=n).values)) 
            sf.write('%f %f\n' %(-dep,td_k.soce.isel(z_dim=n).values))
    tf.close()
    sf.close()

    #Create met file
    m_idx = met.find_j_i(td.latitude.values, td.longitude.values)
    md = met.dataset.isel(y_dim=m_idx[0],x_dim=m_idx[1])
    md = md.assign(cloud=np.abs(0*md.U10),pres=0*md.U10+1013.25)
    md_m = md[['time','U10','V10','pres','T2M','SPH','cloud']].to_dataframe()
    md_m['time'] = md_m['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    md_m.to_csv(odir+'/meteo.dat',sep='\t',index=False,header=False)

    md_s = md.MSDWSWRF.to_dataframe()
    md_s['time'] = md_s['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    md_s.to_csv(odir+'/radsw.dat',sep='\t',index=False,header=False)
    
    #Create BGC profiles
    os.system('mkdir '+odir+'/profiles')
    bd = bgc.dataset.isel(t=0,y_dim=j,x_dim=i)
    for v in plist:
        # Target profile
        target=open('%s/profiles/%s_profile' %(odir,v),'w')
        for time in [sdate, sdate.replace(sdate.year+10)]:
            target.write('%s %i 2\n' %(time.strftime('%Y-%m-%d %H:%M:%S'), len(bd.z_dim)))
            for n,dep in enumerate(bd.nav_lev.values):
                target.write(f'%f %f\n' %(-dep,bd[plist[v]].isel(z=n).values))
        target.close()

        # Relaxation File
        relax=open('%s/profiles/%s_relax' %(odir,v),'w')
        for y in range(11):
            for time in [sdate.replace(sdate.year+y),sdate.replace(sdate.year+y,sdate.month,31)]:
                relax.write(time.strftime('%Y-%m-%d %H:%M:%S ')+'2 2\n')
                relax.write(f'0 %f\n' %relax_rate)
                relax.write(f'%f %f\n' %(-bd.nav_lev[-1].values,relax_rate))
            for time in [sdate.replace(sdate.year+y,2,1),sdate.replace(sdate.year+y,12,31)]:
                relax.write(time.strftime('%Y-%m-%d %H:%M:%S ')+'2 2\n')
                relax.write(f'0 0.0\n')
                relax.write(f'%f 0.0\n' %(-bd.nav_lev[-1].values))
        relax.close()

    #Update fabm.yaml
    for v in fabm_plist:
        for c in fabm_plist[v]:
            FY_cfg['instances'][v]['initialization'][c] = float(bd['TRN%s_%s' %(v,c)].isel(z=0).values)
    for v in fabm_blist:
        for c in fabm_blist[v]:
            FY_cfg['instances'][v]['initialization'][c] = float(bd['fabm_st2Dn%s_%s' %(v,c)].values)
    fyaml = open(odir+'/fabm.yaml','w')
    fyaml.write(yaml.dump(FY_cfg))
    fyaml.close()

    # Update gotm.yaml
    GY_cfg['title'] = f'GOTM-ERSEM at lon_idx %i, lat_idx %i' %(i,j)
    GY_cfg['grid']['nlev'] = len(td.z_dim) 
    GY_cfg['location']['name'] = f'Point i=%i,j=%i' %(i,j)
    GY_cfg['location']['latitude'] = float(td.latitude)
    GY_cfg['location']['longitude'] = float(td.longitude)
    GY_cfg['location']['depth'] = float(h.dataset.Bathymetry.isel(y_dim=j,x_dim=i))
    gyaml = open(odir+'/gotm.yaml','w')
    gyaml.write(yaml.dump(GY_cfg))
    gyaml.close()
