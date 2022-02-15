#!/bin/bash

# Build FABM with cray compiler

module load cray-hdf5-parallel/1.12.0.7
module load cray-netcdf-hdf5parallel/4.7.4.7
module load cmake

ERSEM_DIR=$CODE_DIR/ersem
FABM_DIR=$CODE_DIR/fabm
FABM_INSTALL=$CODE_DIR/fabm-build

mkdir $FABM_INSTALL
cd $FABM_INSTALL
cmake $FABM_DIR/src -DFABM_HOST=nemo -DFABM_ERSEM_BASE=$ERSEM_DIR -DFABM_EMBED_VERSION=ON -DCMAKE_INSTALL_PREFIX=$FABM_INSTALL -DCMAKE_Fortran_COMPILER=ftn #-DCMAKE_BUILD_TYPE=debug
make
make install -j4

cd $WORK


