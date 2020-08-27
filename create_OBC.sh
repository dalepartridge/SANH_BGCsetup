
#Load modules
module unload cray-netcdf-hdf5parallel cray-hdf5-parallel
module load cray-netcdf cray-hdf5
module load nco/4.5.0
module load anaconda/python3

cd $WDIR/OBC/
ln -s $DOMAINFILE domain_cfg.nc
python 0_make_mask.py
. 1_interp.sh

mkdir bdyfiles
ln -s $RAWDATA/OBC/coordinates.bdy.nc .
python 2_create_OBC_file.py

ln -s $RAWDATA/OBC/bdy_depth.nc bdy_gdept.nc
python 3_extract_OBC.py

. 4_add_gdep.sh

cd bdyfiles
cp sanh_bdytrc_y1993m01.nc sanh_bdytrc_y1992m12.nc
cp sanh_bdytrc_y2010m12.nc sanh_bdytrc_y2011m01.nc
cd $WDIR

