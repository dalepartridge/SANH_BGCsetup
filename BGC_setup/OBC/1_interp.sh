#!/usr/bin/env bash

cd interp
ln -s $RAWDATA/global/woa*.nc .
ln -s $RAWDATA/global/GLODAP*.nc .
ln -s $DOMAINFILE .
ln -s $RAWDATA/OBC/bdy_depths.nc .
python 1_interp_woa.py
python 2_interp_glodap.py
cd ..
