#Load modules

cd $WDIR/OBC/
. 1_interp.sh

mkdir bdyfiles
ln -s $DOMAINFILE domain_cfg.nc
ln -s $RAWDATA/OBC/bdy_depths.nc .
ln -s $RAWDATA/OBC/coordinates.bdy.nc .
python 2_create_OBC_file.py

python 3_extract_OBC.py

. 4_add_gdep.sh

cd bdyfiles
cp sanh_bdytrc_y1993m01.nc sanh_bdytrc_y1992m12.nc
cp sanh_bdytrc_y2015m12.nc sanh_bdytrc_y2016m01.nc
cd $WDIR

