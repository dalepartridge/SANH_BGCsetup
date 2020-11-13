#Load modules
module load anaconda/python3

cd $WDIR/RIV/
ln -s $DOMAINFILE domain_cfg.nc
ln -s $RAWDATA/RIVERS/*.nc .
ln -s $WDIR/SBC/pCO2/pCO2_y*nc .
for f in /work/n01/n01/jenjar93/SANH_HINDCAST_CMEMS/SURFACE_FORCING/ERA5_T2M_y*.nc; do 
  ln -s $f surftemp_${f: -8}; 
done

conda create -n xarr python=3.6
source activate xarr
pip install xarray netcdf4

python add_river_nutrients.py $SYEAR $EYEAR

source deactivate
conda remove -n xarr --all

ln -s rivers*nc $INPUTS/RIVERS/

cd $WDIR

