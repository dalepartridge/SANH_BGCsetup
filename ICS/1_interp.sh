

################
# WOA18
###############
cd woa18
ln -s $RAWDATA/ICS/woa18_nitrate_sanh.nc woa18_nitrate.nc
ln -s $RAWDATA/ICS/woa18_phosphate_sanh.nc woa18_phosphate.nc
ln -s $RAWDATA/ICS/woa18_silicate_sanh.nc woa18_silicate.nc
ln -s $DOMAINFILE domain_cfg.nc
ln -s $TOOLS/interp-files/interp_IC_*.sh .
python interp_woa.py $TOOLS/interp-files/namelist-templates/
cd ..

################
# WOA18-OXYGEN
###############
cd woa18-oxy
ln -s $RAWDATA/ICS/woa18_oxygen_sanh.nc woa18_oxygen.nc
ln -s $DOMAINFILE domain_cfg.nc
ln -s $TOOLS/interp-files/interp_IC_initial.sh .
python interp_woaoxy.py $TOOLS/interp-files/namelist-templates/
cd ..

################
# GLODAP
###############
cd glodap
ln -s $RAWDATA/ICS/GLODAP_TAlk_sanh.nc GLODAP_TAlk.nc 
ln -s $RAWDATA/ICS/GLODAP_TCO2_sanh.nc GLODAP_TCO2.nc
ln -s $DOMAINFILE domain_cfg.nc
ln -s $TOOLS/interp-files/interp_IC_*.sh .
python interp_glodap.py $TOOLS/interp-files/namelist-templates/
cd ..

################
# OCCCI
###############
cd occci
ln -s $RAWDATA/ICS/chlor_a_sanh.nc CCI-OC_chla.nc
ln -s $DOMAINFILE domain_cfg.nc
ln -s $TOOLS/interp-files/interp_IC_initial.sh .
python interp_occci.py $TOOLS/interp-files/namelist-templates/
cd ..

################
# ADY
###############
cd ady
ln -s $RAWDATA/ICS/ady_sanh.nc adyBroadBandClimatology.nc
ln -s $DOMAINFILE domain_cfg.nc
ln -s $TOOLS/interp-files/interp_IC_initial.sh .
python interp_ady.py $TOOLS/interp-files/namelist-templates/
cd ..

################
# iMarNet
###############
cd imarnet
ln -s $RAWDATA/ICS/iMarNet_data.nc .
ln -s $DOMAINFILE domain_cfg.nc
ln -s $TOOLS/interp-files/interp_IC_*.sh .
python interp_imarnet.py $TOOLS/interp-files/namelist-templates/
cd ..




