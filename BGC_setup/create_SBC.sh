#!/bin/bash

source ./set_paths.sh

#####################
# NITROGEN DEPOSITION
#####################

#Process Nitrogen Deposition
cd $WDIR/SBC/Ndep/
ln -s $DOMAINFILE domain_cfg.nc
ln -s $RAWDATA/SBC/NDEP-CEH/*.nc .
python process_Ndep.py

ln -s $WDIR/SBC/Ndep/Ndep_y*nc $INPUTDIR/SBC/BGC/

#####################
# LIGHT ABSORPTION
#####################
'''
cd $WDIR/SBC/ady/
ln -s $RAWDATA/SBC/ady/ady_sanh.nc .
ln -s $DOMAINFILE domain_cfg.nc
ln -s $TOOLS/interp-files/interp_SBC_initial.sh .
python interp_ady.py $TOOLS/interp-files/namelist-templates/
ln -s $WDIR/SBC/ady/SANH-CCI*nc $INPUTDIR/SBC/BGC/

####################
# Surface CO2
####################

cd $WDIR/SBC/pCO2
ln -s $RAWDATA/SBC/pCO2/RCP85_MIDYR_CONC.DAT .
python process_pCO2.py
cdo -splitsel,1 pCO2a.nc pCO2_y
year=1989
for f in pCO2_y*; do
  mv $f ${f::6}${year}.nc
  year=$((year+1))
done

ln -s $WDIR/SBC/pCO2/pCO2*nc $INPUTDIR/SBC/BGC/
'''