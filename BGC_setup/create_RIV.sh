#!/bin/bash

source ./set_paths.sh

cd $WDIR/RIV/
ln -s $DOMAINFILE domain_cfg.nc
ln -s $RAWDATA/RIVERS-LTLS/ .
mkdir T2M
ln -s $INPUTDIR/SBC/ATM/ERA5_T2M_y*.nc T2M/
ln -s $RAWDATA/EEZ .

echo 'Creating River Files...'
python make_ltls_rivers.py $SYEAR $EYEAR
echo '...Complete'


ln -s $WDIR/RIV/rivers*nc $INPUTDIR/RIV/

cd $WDIR

