module load cdo

mkdir cmems/
cd cmems/
ln -s $RAWDATA/OBC/cmems*.nc .
ln -s $RAWDATA/OBC/domain_bdy_depths.nc domain_cfg.nc
ln -s $RAWDATA/OBC/bdy_depth.nc bdy_gdept.nc
ln -s $TOOLS/interp-files/interp_OBC*.sh .
ln -s ../mesh_mask.nc .

python interp_cmems.py $TOOLS/interp-files/namelist-templates/
cd ..




