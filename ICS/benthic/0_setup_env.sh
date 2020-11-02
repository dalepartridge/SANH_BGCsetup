#Load modules
module unload cray-netcdf-hdf5parallel cray-hdf5-parallel
module load cray-netcdf cray-hdf5
module load nco/4.5.0
module load anaconda/python3
module load cdo

export PATH=/home/n01/n01/dapa/miniconda3/bin:$PATH
conda create -n coast python=3.8
source activate coast
conda install --file /work/n01/n01/dapa/SANH/code/COAsT/conda_requirements.txt
export PYTHONPATH=$PYTHONPATH:/work/n01/n01/dapa/SANH/code/COAsT/

#Link domain files
ln -s $RAWDATA/DOMAIN/bathy_meter.nc .
ln -s $DOMAINFILE .

# Link to physics output files
PO_DIR=/work/n01/n01/jenjar93/SANH_HINDCAST_CMEMS/RUN_DIRECTORY
ln -s $PO_DIR/2000/SANH_1m_20000101_20010101_gridT.nc monthly_temperature.nc
mkdir ssh toce
ln -s $PO_DIR/**/SANH_5d_200*gridT.nc toce/
ncks -d time_counter,-1, $PO_DIR/1999/SANH_5d_1999*gridT.nc toce/SANH_5d_19991226_19991231.nc
ln -s $PO_DIR/**/SANH_1h_200*SSH.nc ssh/
ncks -d time_counter,-1, $PO_DIR/1999/SANH_1h_1999*SSH.nc ssh/SANH_1h_19991231_19991231.nc

# Link to met forcing files
M_DIR=/work/n01/n01/jenjar93/SANH_HINDCAST_CMEMS/SURFACE_FORCING
mkdir sbc
for i in {SPH,T2M,U10,V10,MTPR,MSDWSWRF}; do
ln -s $M_DIR/ERA5_${i}_y200*.nc sbc/
ncks -d time,-1, $M_DIR/ERA5_${i}_y1999.nc sbc/ERA5_${i}_y19991231.nc
done

cp /work/n01/n01/dapa/SANH/code/gotm/gotm gotm-base-files/
