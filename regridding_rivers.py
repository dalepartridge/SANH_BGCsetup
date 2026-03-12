import pandas as pd
from numpy import where,arange,meshgrid, cos, sin,deg2rad,sqrt,cumsum,zeros,array
from netCDF4 import Dataset as DS
from netCDF4 import default_fillvals
from numpy.ma import masked_where as MW
from scipy.interpolate import griddata as GD
import scipy.spatial as spatial
from matplotlib.pyplot import figure, scatter,text,clim,colorbar, plot,title
import os
import sys

def find_original_matchup (lat0,lat1,lon0,lon1,original_coords_DF,final_coords_DF,tmask_coords_DF,river_indices,tmask_indices):
    for i in range(len(original_coords_DF)):
       if (lon0<original_coords_DF['Longitude'][i]<lon1)&(lat0<original_coords_DF['Latitude'][i]<lat1):
          print (i,
          original_coords_DF['Longitude'][i],original_coords_DF['Latitude'][i], final_coords_DF['Longitude'][river_indices[i]], final_coords_DF['Latitude'][river_indices[i]], tmask_coords_DF['Longitude'][tmask_indices[i]], tmask_coords_DF['Latitude'][tmask_indices[i]])
    return

def find_river_mouth(lat0,lat1,lon0,lon1,final_coords_DF,river_indices,rnf):
    for i in range(len(final_coords_DF)):
       if (lon0<final_coords_DF['Longitude'][i]<lon1)&(lat0<final_coords_DF['Latitude'][i]<lat1):
          print (i,final_coords_DF['Longitude'][i], final_coords_DF['Latitude'][i],rnf[i])
    return

def create_output_file(namefile,gridfile,varlist=('rorunoff','rono3','ronh4','rodip','rodoxy','rodic','rotalk','rosio2','rodepth')):


   units={'rorunoff':'Kg/m2/s',
           'rono3':'gN/s',
           'ronh4':'gN/s',
           'rodip':'gP/s',
           'rodoxy':'gO/s',
           'rodic':'gC/s',
           'rotalk':'mmol/s',
           'rosio2':'gSi/s',
           'rodepth':'m'}
   long_names={'rorunoff':'freshwater_discharge',
           'rono3':'nitrate_discharge',
           'ronh4':'ammonium_discharge',
           'rodip':'phosphate_discharge',
           'rodoxy':'oxygen_discharge',
           'rodic':'DIC_discharge',
           'rotalk':'Total_alkalinity_discharge',
           'rosio2':'silicate_discharge',
           'rodepth':'depth of river mouth'}

   try:
       ncout=DS(namefile,'w')
   except PermissionError: 
       check_deletion= input("the file {} exists, do you want to delete it? y/N ".format(namefile))
       if check_deletion in ('y','Y'):
           os.remove(namefile)
           ncout=DS(namefile,'w')
       else:
           print ("file not removed, exiting")
           sys.exit()
           
   ncgrid=DS(gridfile)
   lat=ncgrid.variables['nav_lat'][:]
   lon=ncgrid.variables['nav_lon'][:]
   dA=ncgrid.variables['e1t'][:]*ncgrid.variables['e2t'][:]
   ncgrid.close()

   ncout.createDimension('y',lat.shape[0])
   ncout.createDimension('x',lon.shape[1])
   ncout.createDimension('time',None)
   ncout.createVariable('time',float,'time')
   ncout.variables['time'].units='days since 1970-01-01'
   ncout.variables['time'].calendar='gregorian'
   ncout.variables['time'].long_name='time'

   ncout.createVariable('nav_lat',float,('y','x'))
   ncout.variables['nav_lat'].units='degrees_north'
   ncout.variables['nav_lat'].long_name='latitude'

   ncout.createVariable('nav_lon',float,('y','x'))
   ncout.variables['nav_lon'].units='degrees_east'
   ncout.variables['nav_lon'].long_name='longitude'
   
   ncout.createVariable('dA',float,('y','x'))
   ncout.variables['dA'].units='m2'
   ncout.variables['dA'].long_name='cell surface area'
   ncout.variables['dA'][:]=dA

   ncout.createVariable('socoefr',float,('y','x'))
   ncout.variables['socoefr'].units='-'
   ncout.variables['socoefr'].long_name='river mouth'

   for var in varlist:
      ncout.createVariable(var,float,('time','y','x'),complevel=6,fill_value=0.)
      ncout.variables[var].units=units[var]
      ncout.variables[var].long_name=long_names[var]

   ncout.close()
   return
#######################################################

def spread_load(load,da):

   spread_mapping={'Amazon':[[684,952],[685,952],[685,951],[685,950],[686,950],[686,949],[686,948],[687,948]], #Amazon
                   'Uruguay':[[538,917],[538,916],[537,916],[537,917]], #Buenos Aires
                   'Congo':[[659,1198],[658,1198],[660,1198]], #Congo
                   'Orinoco':[[719,907],[719,906],[719,906],[719,906],[719,906],[719,906]], #Orinoco
                   'Gange':[[777,74],[777,75],[777,74],[776,74],[776,73],[776,72],[775,72],[774,72],[774,71],[773,72],[773,70]], #Gange
                   'ChiangJang':[[817,196],[818,196],[818,195],[819,195],[819,194],[819,193],[820,193],[820,192],[821,192],[821,191]], #ChiangJang
                   'Columbia':[[904,651],[903,651]], # Columbia
                   'StLawrence':[[911,875],[912,875],[911,876],[912,876]], # St Lawrence
                   'Nelson':[[1005,791],[1005,790],[1006,790]], #Nelson
                   'Jena':[[1082,293],[1082,294],[1082,295],[1083,295],[1083,296],[1084,296],[1085,296],[1085,297],[1086,297],[1086,298],[1087,298],[1088,298],[1089,298],[1090,298],[1091,298],[1092,298],[1093,298],[1093,297],[1094,297],[1094,296],[1095,296],[1095,295],[1096,286],[1096,285]], #Jena
                   'Yukon':[[1085,541],[1085,542],[1085,543],[1086,543],[1086,544],[1086,545],[1087,545],
[1087,544],[1087,543],[1088,543],[1088,542],[1089,542],[1090,542],[1091,542],[1091,543],[1095,547],[1096,547],[1097,547]], #Yukon
                   'Yenisei':[[1175,222],[1175,221],[1176,222],[1176,221],[1177,222],[1177,221],[1177,223],[1178,222],[1178,221],[1178,223],[1178,224],[1178,225]], # Yenisei
                   'Taz':[[1187,191],[1186,188],[1186,189],[1187,190],[1187,189],[1187,188],[1187,187]], #Taz
                   'Ob':[[1194,1272],[1194,1271],[1195,1272],[1195,1271],[1196,1272],[1196,1271],[1197,1272],[1197,1271],[1197,1270],[1198,1272],[1198,1271],[1198,1270],[1199,1268],[1199,1269],[1199,1270],[1199,1271],[1199,1272],[1199,1273]], #Ob
                   }
   before=(load*da).sum()
   if (load.mask.any()):   # clean the mask for checking purposes
       load.mask=False
   for riv in spread_mapping.keys():
       ncells=len(spread_mapping[riv])   # total number of cells
       original_load=load[:,spread_mapping[riv][0][0],spread_mapping[riv][0][1]].copy()  # saving the original load for the river (1D - time)
       load[:,spread_mapping[riv][0][0],spread_mapping[riv][0][1]]=0.             # removing the original load from the array
       area_tot=0.    # new area recieving the input
       for cell in spread_mapping[riv]:
           area_tot+=da[cell[0],cell[1]]
       for cell in spread_mapping[riv]:
            load[:,cell[0],cell[1]]+=original_load*da[cell[0],cell[1]]/area_tot   # adding the load to the existing one
   after=(load*da).sum()
   print (before/after)
   return load
       
####################################################################################


def fill_new_file(namefile,year,indices,flowfile,N_file,P_file,gridfile,Rlat,Rlon,Tlat,Tlon,marine_climatology_file,spread=True):
    # fill the existing output file with the data
    # the set of variable is pre-defined

    # open the NEMO grid file and upload river runoff
    #ncgrid=DS(gridfile)
    #grid_lat=ncgrid.variables['nav_lat'][:]
    #grid_lon=ncgrid.variables['nav_lon'][:]
    #ncgrid.close()

    ncout=DS(namefile,'a')
    da=ncout.variables['dA'][:]
    if flowfile[-2:]=='nc':
       rnffile=DS(flowfile,'r')
       runoff=rnffile.variables['rorunoff'][:].squeeze()
       try:
           river_mask=runoff.mask
       except:
           river_mask=where((runoff==0)|(runoff>1e20),True,False)
    else:
       print('flowfile needs to be a netCDF file')
       return
    
    # ulpoad N and P loads
    if N_file[-3:]=='csv':
       Nloads=pd.read_csv(N_file,delimiter=',',usecols=arange(63))
       if year==0:
           Nloads=Nloads[['1970','1971', '1972', '1973', '1974', '1975', '1976', '1977', '1978', '1979','1980', '1981','1982', '1983', '1984', '1985','1986', '1987', '1988','1989', '1990', '1991', '1992', '1993', '1994', '1995', '1996', '1997','1998', '1999', '2000', '2001', '2002', '2003', '2004', '2005', '2006','2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015']].mean(axis=1)
       elif year>2015:
           Nloads=Nloads['{:4d}'.format(2015)].values
       else:
           Nloads=Nloads['{:4d}'.format(year)].values
    else:
       print('Nfile needs to be a csv file from IMAGE')
       return
    if P_file[-3:]=='csv':
       Ploads=pd.read_csv(P_file,delimiter=',',usecols=arange(63))
       if year==0:
           Ploads=Ploads[['1970','1971', '1972', '1973', '1974', '1975', '1976', '1977', '1978', '1979','1980', '1981','1982', '1983', '1984', '1985','1986', '1987', '1988','1989', '1990', '1991', '1992', '1993', '1994', '1995', '1996', '1997','1998', '1999', '2000', '2001', '2002', '2003', '2004', '2005', '2006','2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015']].mean(axis=1)
       elif year>2015:
           Ploads=Ploads['{:4d}'.format(2015)].values
       else:
           Ploads=Ploads['{:4d}'.format(year)].values
       
    else:
       print('Pfile needs to be a csv file from IMAGE')
       return
    # copy the runoff in the new file
    if spread:
        spread_load(runoff,da)
    ncout['rorunoff'][:]=runoff
    
    print ('calculating N & P...')
    # calculate the total load on each grid cell
    Ntmp=zeros(da.shape)
    Ptmp=zeros(da.shape)
    for n,index in enumerate(indices):
        if index>0:
            Ntmp[Rlat[index],Rlon[index]]+=Nloads[n]
            Ptmp[Rlat[index],Rlon[index]]+=Ploads[n]
        else:
            Ntmp[Tlat[-index],Tlon[-index]]+=Nloads[n]
            Ptmp[Tlat[-index],Tlon[-index]]+=Ploads[n]
        
    # calculate average concentration [g/m3] from total nutrient load [kg/y] and total flow [kg/m2/s]
    # 
    kg2g=1000.
    sec2day=1/86400.
    L2m3=.001 
    Nconc=Ntmp*kg2g/(runoff.sum(0)*da/sec2day*L2m3)
    
    # calculate daily load [g/s] from daily runoff [kg/m2/s] and concentration [g/m3]
    N_daily_load=runoff*da*L2m3*Nconc
    if spread:  # spread biggest rivers on multiple cells
       N_daily_load=spread_load(N_daily_load,da)
    
    # n2=where((Ntmp[newaxis,:,:].repeat(runoff.shape[0],axis=0)>0)&(runoff.data==0),Ntmp[newaxis,:,:].repeat(runoff.shape[0],axis=0)/float(runoff.shape[0]),N_daily_load)
    ncout['rono3'][:]=0.9*N_daily_load
    ncout['ronh4'][:]=0.1*N_daily_load
    del(N_daily_load)
    
    # this emopty memory
    Pconc=Ptmp*kg2g/(runoff.sum(0)*da/sec2day*L2m3)
    P_daily_load=runoff*da*L2m3*Pconc
    if spread:  # spread biggest rivers on multiple cells
       P_daily_load=spread_load(P_daily_load,da)

    ncout['rodip'][:]=P_daily_load
    del(P_daily_load)
    
    print ('calculating DO...')
    # oxygen concentration is assumed to be 10mg/l=10g/m3
    DO=10.
    DO_daily_load=runoff*da*L2m3*DO
    if spread:  # spread biggest rivers on multiple cells
       DO_daily_load=spread_load(DO_daily_load,da)

    ncout['rodoxy'][:]=DO_daily_load
    del(DO_daily_load)
    
    # Silicate, DIC and TA concentrations are assumed identical to a marine climatology passed trough marine_climatology_file
    # concentration in the marine climatology is in mmol/m3 and need to be converted in g/m3 to have a load in g/s, excpet TA that stays in mmol/s
    # TODO: we could keep Si DIC in original units as well and change fabm_input and units above
    print ('calculating Si...')
    fclimatology=DS(marine_climatology_file)
    Siconc=fclimatology.variables['N5_s'][0,0]
    Si_mmoles2mg=28.0855
    mg2g=0.001
    Si_daily_load=runoff*da*L2m3*Siconc*Si_mmoles2mg*mg2g
    if spread:  # spread biggest rivers on multiple cells
       Si_daily_load=spread_load(Si_daily_load,da)
    ncout['rosio2'][:]=Si_daily_load
    del(Si_daily_load)
    print ('calculating DIC...')
    DICconc=fclimatology.variables['O3_c'][0,0]
    DIC_mmoles2mg=12.
    DIC_daily_load=runoff*da*L2m3*DICconc*DIC_mmoles2mg*mg2g
    if spread:  # spread biggest rivers on multiple cells
       DIC_daily_load=spread_load(DIC_daily_load,da)
    ncout['rodic'][:]=DIC_daily_load
    del(DIC_daily_load)
    print ('calculating TA...')
    TAconc=fclimatology.variables['O3_TA'][0,0]
    TA_daily_load=runoff*da*L2m3*TAconc
    if spread:  # spread biggest rivers on multiple cells
       TA_daily_load=spread_load(TA_daily_load,da)
    ncout['rotalk'][:]=TA_daily_load
    del(TA_daily_load)
    
    socoefr=where(rnf[0]>0,0.5,0)
    ncout['socoefr'][:]=socoefr
    
    ncout['rodepth'][:]=10.
    #del(depthvar)
    ncout.close()
    
    return

def check_big_loads(final_coords_DF,indices,rnf,nutrient,sorted_load, cutoff=0.5):
    top_rivers=(cumsum(sorted_load['av_PD'].values)/sorted_load['av_PD'].sum()<cutoff).argmin()
    fig=figure(figsize=(18,18))
    rnf=MW(rnf==0,rnf)
    scatter(final_coords_DF['Longitude'].values,final_coords_DF['Latitude'].values,c=rnf,s=20)
    for i in range(top_rivers):
          if indices[sorted_load.index[i]]>0:
              plot([sorted_load['lon'][sorted_load.index[i]],final_coords_DF['Longitude'][indices[sorted_load.index[i]]]],[sorted_load['lat'][sorted_load.index[i]],final_coords_DF['Latitude'][indices[sorted_load.index[i]]]],'r',lw=1)
          else:
              plot([sorted_load['lon'][sorted_load.index[i]],tmask_coords_DF['Longitude'][-indices[sorted_load.index[i]]]],[sorted_load['lat'][_sorted_load.index[i]],tmask_coords_DF['Latitude'][-indices[sorted_load.index[i]]]],'m',lw=1)
          text(sorted_load['lon'][sorted_load.index[i]],sorted_load['lat'][sorted_load.index[i]],'{}'.format(i),size=12,c='g')
    colorbar()
    clim(0,500)
    title('Check for river with big nutrients loads')
    fig.savefig('check{}loads.png'.format(nutrient))
    return



def initial_match(coord_file,original_location_file,freshwater_file):
    '''this function extracts the coordinates of the tmask points, of the original river locations and of the the NEMO runoff locations
    coord_file: full path to the file containing the coordinates of the model grid
    original_location_file: full path to the file containing the coordinates of the river mouths that need to be regridded (e.g. IMAGE)
    freshwater_file: full path to the file containing the coordinates of the river mouths that will be used in the model (e.g. JRA)
    '''
    
    print('reading model grid file...')
    fmesh=DS(coord_file)
    da=(fmesh.variables['e1t'][:]*fmesh.variables['e2t'][:]).squeeze()
    lat=fmesh.variables['nav_lat'][:]
    lon=fmesh.variables['nav_lon'][:]
    nlat=arange(lat[:,0].size)
    nlon=arange(lon[0,:].size)
    nlon,nlat=meshgrid(nlon,nlat)
    tmask=where(fmesh.variables['bathy_metry'][0]>0,1,0)
    Tlat=MW(tmask==0,lat).compressed()
    Tlon=MW(tmask==0,lon).compressed()
    fmesh.close()
    tmask_coords_DF=pd.DataFrame({'Latitude':Tlat.ravel(),'Longitude':Tlon.ravel()})
    
    print('reading original locations...')
    original_DF=pd.read_csv(original_location_file,delimiter=',',usecols=arange(63))
    original_lat=original_DF['lat'].values
    original_lon=original_DF['lon'].values
    basin_ID=original_DF['Basin ID'].values
    original_coords_DF=pd.DataFrame({'Latitude':original_lat,'Longitude':original_lon})
   
    print('reading final locations...')
    final_file=DS(freshwater_file)
    rnf=(final_file.variables['rorunoff'][:]*da).mean(0).squeeze()/1000.
    final_riv_lat=MW(rnf.mask,lat).compressed()
    final_riv_lon=MW(rnf.mask,lon).compressed()
    final_coords_DF=pd.DataFrame({'Latitude':final_riv_lat,'Longitude':final_riv_lon})
    
    # these are the packed coordinated of the locations of the river in the NEMO file, or the Tmask  
    Rlat=MW(rnf.mask,nlat).compressed()
    Rlon=MW(rnf.mask,nlon).compressed()
    Tlat=MW(tmask==0,nlat).compressed()
    Tlon=MW(tmask==0,nlon).compressed()
    
    #pack the runoff data
    rnf=MW(rnf.mask,rnf).compressed()
    
    return lat,lon,original_coords_DF,final_coords_DF,tmask_coords_DF,basin_ID,rnf,Rlat,Rlon,Tlat,Tlon
    

def match_base_on_distance(IMAGE_DF,JRA_DF):
    "Based on https://stackoverflow.com/q/43020919/190597"
    "this match every river in the original dataset (IMAGE) to the location of the NEMO runoff locations (JRA)"
    #    IMAGE_DF: Dataframa with Lat, Lon
    #    JRA_DF: Dataframa with Lat, Lon
    R=6367
    phi = deg2rad(IMAGE_DF['Latitude'])
    theta = deg2rad(IMAGE_DF['Longitude'])
    IMAGE_DF['x'] = R * cos(phi) * cos(theta)
    IMAGE_DF['y'] = R * cos(phi) * sin(theta)
    IMAGE_DF['z'] = R * sin(phi)
    phi = deg2rad(JRA_DF['Latitude'])
    theta = deg2rad(JRA_DF['Longitude'])
    JRA_DF['x'] = R * cos(phi) * cos(theta)
    JRA_DF['y'] = R * cos(phi) * sin(theta)
    JRA_DF['z'] = R * sin(phi)
    
    #build the KDtree on the final grid, (i.e. JRA)
    tree = spatial.KDTree(JRA_DF[['x', 'y','z']])
    
    # query the tree with the original dataset, i.e. IMAGE
    distance, index = tree.query(IMAGE_DF[['x', 'y','z']], k=1)
    return distance,index

def calculate_distance(lat0,lon0,lat1,lon1):
    R=6367
    phi = deg2rad(lat0)
    theta = deg2rad(lon0)
    x0=R * cos(phi) * cos(theta)
    y0=R * cos(phi) * sin(theta)
    z0=R * sin(phi)
    phi = deg2rad(lat1)
    theta = deg2rad(lon1)
    x1=R * cos(phi) * cos(theta)
    y1=R * cos(phi) * sin(theta)
    z1=R * sin(phi)
    chord=sqrt((x0-x1)**2+(y0-y1)**2+(z0-z1)**2)
    return chord
    

def apply_cutoff(river_distance,river_indices,tmask_distance,tmask_indices, cutoff=100):
    # if the distance between the original coordinates and the new one is more than cutoff then set the coordinates to the closest grid point on the T grid
    # the index is stored with a negative value to highlight the fact that comes from the tmask and not the runoff dataset
    
    distance=where(river_distance>cutoff,-tmask_distance,river_distance)
    indices=where(river_distance>cutoff,-tmask_indices,river_indices)
    
    return distance, indices

def adjust_cutoff_100():
    # this function contains a series of manual adjustments following a cutoff at 100Km
    
    # list of indices to reset to the river_coordinates
    reset_rivers=(7731,7732,7774,7775,      # Colombia
                  5273,5274,                # Seattle
                  8205,8237,8300,8301,8342,  # Galapagos
                  3350,3351,3427,           # Hudson bay
                  )
    # this dictionary contains manual coupling
    manual_adjust={             # 9913:'nul', 9925: 'nul',  # salt lakes in Argentina
            9667:169233, # Lagoa dos Patos
            6126:173881,  # Pamlico river
            5275:175080,
            5276:175080,
            5300:175080,
            5301:175080,
            3114:180382,3115:180382,   # Kara Bay
            2309:179985, 2310:179985, 2311:179985, 2312:179985, # Yenisei River
            2462:179985, 2463:179985, 2464: 179985,   # Yenisei River
            6450:173507,            # Nile
            6481:173273,6482:173273,  # gulf of Suez
            5725:174524,5770:174524,5771:174524,  # Sea of Marmara 
            5769:174385,               # Sea of Marmara
            }
    
    return reset_rivers, manual_adjust

def adjust_big_loads():
    # this function moves the locations of the biggest nutrient loads discharge into the largest rivers in the JRA grid
    
    big_Nloads={7815:171528,    #Orinoco
                8239:170977,    # Amazon
                5300:175080,    # St Lawrence
                5335:175001,    # Columbia
                5135: 175133,    # Seine
                4953: 175432,    # Rhine
                4830: 175674,    # Elbe
                5541: 174629,    # Rhone
                5443: 174840,    # Po
                4779:175887,     #Vistula
                5320:175108 ,    # Dnipro
                5413: 174968,    # Danube
                6849:172823,     # Meghna
                7303:172241,     # Godavari
                7344: 172172,    # irrawady
                7309:172243,     # Thanlyin
                6790: 172930,    # Indus
                7710: 171606,    # Mekong
                6851:172756,     # Modaomen/Tan Jiang
                6378: 173461,    # Yangtze
                5879: 174225,    # haihe
                5966:174113     # Hangang
                }
    big_Ploads={5148:175352,     # Fraser
                8134: 171134,    # PAtia
                9772: 169084,    # Parana
                5664:174352,     # Douro
                4993:175377,     # Thames
                4824:175545,     # Humber
                5639:174521,     # Lumi mat
                6376:173506,     # Nile
                7340:172141,     # Krishna
                8603:170644,     # Sepik
                }
    return big_Nloads,big_Ploads

def extract_and_sort(load_file):
    loads=pd.read_csv(load_file,delimiter=',',usecols=arange(63))
    loads['av_PD']=loads[['1970','1971', '1972', '1973', '1974', '1975', '1976', '1977', '1978', '1979','1980', '1981','1982', '1983', '1984', '1985','1986', '1987', '1988','1989', '1990', '1991', '1992', '1993', '1994', '1995', '1996', '1997','1998', '1999', '2000', '2001', '2002', '2003', '2004', '2005', '2006','2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015']].mean(axis=1)
    loads=loads.sort_values('av_PD',axis=0,ascending=False)
    return loads
    
if __name__=='__main__':
    
    years=arange(1979,2016)   # range of years to analyse
    years=arange(2016,2021)   # range of years to analyse
    #years=arange(0,1)        # an array of 1 value = 0 means climatological input
    R = 6367                  # Earth Radius in Km
    cutoff=100                # cutoff distance in Km

    spread=True               # spread biggest rivers over multiple cells
    
    # grid of eORC2A25
    coord_file = '/data/sthenno1/scratch/yuti/MA_MissionAtlantic/domcfg_eORCA025_v2.nc'

    # text file with original river location (e.g. IMAGE)
    original_location_file='/data/sthenno1/scratch/yuti/MA_MissionAtlantic/rivers/Global_basins_TN_TP_data/global_basins_TP_export_SSP4_oct2020_.csv'
    
    # text files with N and P loads
    P_file='/data/sthenno1/scratch/yuti/MA_MissionAtlantic/rivers/Global_basins_TN_TP_data/global_basins_TP_export_SSP4_oct2020_.csv'
    N_file='/data/sthenno1/scratch/yuti/MA_MissionAtlantic/rivers/Global_basins_TN_TP_data/global_basins_TN_export_SSP4_oct2020_.csv'

    
    # netCDF file with model river location (e.g. JRA)
    freshwater_file='/data/sthenno1/scratch/yuti/MA_MissionAtlantic/rivers/JRA_RIVERS/ORCA025_rivers_Antar_Green_y2000.nc'
    if len(years)==0: 
        freshwater_file='/data/sthenno1/scratch/yuti/MA_MissionAtlantic/rivers/eORCA025_climatology_025/eORCA_R025_runoff_v1.0.nc'
    
    marine_climatology_file='/users/modellers/gig/Documents/MissionAtantic/eORCA025_Stuff/GLODAP_to_EORCA025/glodap_to_eORCA025.nc'
    
    #extract coords and basin IDs
    lat,lon,original_coords_DF,final_coords_DF,tmask_coords_DF,basin_ID,rnf,Rlat,Rlon,Tlat,Tlon=initial_match(coord_file,original_location_file,freshwater_file)
    
    # find  the river in the final dataset closest to the original location of river mouths 
    # river_indices[i] contains the index of the river location in the NEMO runoff dataset of the IMAGE river in list position i
    river_distance,river_indices=match_base_on_distance(original_coords_DF,final_coords_DF)
    
    # find  the grid point closest to the original location of river mouths 
    tmask_distance,tmask_indices=match_base_on_distance(original_coords_DF,tmask_coords_DF)

    #reset the river mouths that have been moved more than "cutoff" Km back to it osiginal position
    #on the assumption that this is due to (mostly) islands that are not considered in the model
    distance,indices=apply_cutoff(river_distance,river_indices,tmask_distance,tmask_indices, cutoff=cutoff)
    
    # when a cutoff of 100 Km is applied some adjustment is needed
    # reset_rivers contains id of rivers where the original regridding based on distance was preferable
    # manual_adjust contains ID of rivers that neither the closest river mouth or the closest tmask point are a good regridding point
    reset_rivers,manual_adjust=adjust_cutoff_100()
    
    # here the manual adjustments for the biggest rivers is set
    # biggest rivers are those who contribute to 50% of the cumulative load
    reset_bigN, reset_bigP=adjust_big_loads()
    
    # apply series of adjsutments
    for i in reset_rivers:
        distance[i]=river_distance[i]
        indices[i]=river_indices[i]
        
    for i in manual_adjust.keys():
        indices[i]=manual_adjust[i]
        distance[i]=calculate_distance(original_coords_DF['Latitude'][i], original_coords_DF['Longitude'][i],final_coords_DF['Latitude'][indices[i]], final_coords_DF['Longitude'][indices[i]])

    for i in reset_bigN.keys():
        indices[i]=reset_bigN[i]
        distance[i]=calculate_distance(original_coords_DF['Latitude'][i], original_coords_DF['Longitude'][i],final_coords_DF['Latitude'][indices[i]], final_coords_DF['Longitude'][indices[i]])
    
    for i in reset_bigP.keys():
        indices[i]=reset_bigP[i]
        distance[i]=calculate_distance(original_coords_DF['Latitude'][i], original_coords_DF['Longitude'][i],final_coords_DF['Latitude'][indices[i]], final_coords_DF['Longitude'][indices[i]])
    
    
    # here the source river loads are extracted and sorted
    sorted_TN=extract_and_sort(N_file)
    sorted_TP=extract_and_sort(P_file)
    
    # plot figures to check that the main rivers have been correctly allocated
    check_big_loads(final_coords_DF,indices,rnf,'N',sorted_TN)
    check_big_loads(final_coords_DF,indices,rnf,'P',sorted_TP)
    
    
    output_folder='/data/proteus2/scratch/yuti/MA_MissionAtlantic/rivers/JRA_RIVERS_BGC/'
    output_rootname='ORCA025_rivers_AG_BGC_dep_spread_'
    if (years.size==1)&(years[0]==0):
        # input and output are single climatological file
        output_folder='/data/sthenno1/scratch/yuti/MA_MissionAtlantic/rivers/eORCA025_climatology_025/'
        output_rootname='eORCA025_bfr2d_v0.2_BGC'
    
    for y in years:
        print ('Creating river file for year {:4d}...'.format(y))
        # create the new outputfile
        output_file=output_folder+output_rootname+'y{:4d}.nc'.format(y)
        freshwater_file='/data/sthenno1/scratch/yuti/MA_MissionAtlantic/rivers/JRA_RIVERS/ORCA025_rivers_Antar_Green_y{:4d}.nc'.format(y)
        if y==0:
            output_file=output_folder+output_rootname+'.nc'
            freshwater_file='/data/sthenno1/scratch/yuti/MA_MissionAtlantic/rivers/eORCA025_climatology_025/eORCA_R025_runoff_v1.0.nc'
        create_output_file(output_file,coord_file)
        # fill the new file
        fill_new_file(output_file, y, indices, freshwater_file, N_file, P_file, coord_file, Rlat, Rlon, Tlat, Tlon, marine_climatology_file,spread)
    
