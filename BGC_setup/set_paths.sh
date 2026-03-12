#!/bin/bash

module load cray-hdf5-parallel/1.12.2.1
module load cray-parallel-netcdf/1.12.3.1
module load cray-netcdf-hdf5parallel/4.9.0.1
module load nco
module load cdo
module load cray-python

source ~/.bashrc # Load mamba paths

# Create mamba environment if it doesn't exist
if { mamba env list | grep 'model_setup'; } >/dev/null 2>&1; 
then 
echo 'Activating conda environment model_setup'
mamba activate model_setup
else 
echo 'Creating conda env model_setup'
mamba env create --name model_setup -f conda_env.yml
mamba activate model_setup
fi

export ROOTDIR=/work/n01/n01/dapa/SANH
export RAWDATA=$ROOTDIR/RAW_DATA
export WDIR=$ROOTDIR/BGC_setup
export TOOLS=$WDIR/TOOLS
export DOMAINFILE=$RAWDATA/DOMAIN/domain_cfg.nc
export INPUTDIR=/work/n01/n01/dapa/SANH/INPUTS
export SYEAR=1993
export EYEAR=2015
