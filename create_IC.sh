
#Load modules
cd $WDIR/ICS/
. 1_interp.sh

ln -s $DOMAINFILE domain_cfg.nc
python 2_create_IC_file.py

ln -s $RAWDATA/DOMAIN/SANH_density.nc density.nc
ln -s $RAWDATA/DOMAIN/bathy_meter.nc .
python 3_extract_pelagic.py

python 4_extract_benthic.py

cd $WDIR

