#Load modules
module load anaconda/python3

cd $WDIR/RIV/
ln -s $DOMAINFILE domain_cfg.nc
ln -s $RAWDATA/RIVERS/*.nc .
ln -s $WDIR/SBC/pCO2/pCO2_y*nc .
for f in /work/n01/n01/jenjar93/SANH_HINDCAST_CMEMS/SURFACE_FORCING/ERA5_T2M_y*.nc; do 
  ln -s $f surftemp_${f: -8}; 
done

python add_river_nutrients.py $SYEAR $EYEAR

ln -s rivers*nc $INPUTS/RIVERS/

cd $WDIR

