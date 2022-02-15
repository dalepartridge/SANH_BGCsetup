#!/bin/bash

# Build NEMO with Cray compiler
module load cray-hdf5-parallel/1.12.0.7
module load cray-netcdf-hdf5parallel/4.7.4.7
module load cmake

export FABM_HOME=$CODE_DIR/fabm-build
export XIOS_HOME=$CODE_DIR/xios-build
NEMO_DIR=$CODE_DIR/nemo
cd $NEMO_DIR

cp $CODE_DIR/extra-files/nemo/Config_cray.pm $NEMO_DIR/ext/FCM/lib/Fcm/Config.pm

# AMM7 FABM
CFG=$CONFIG
ARCH=X86_ARCHER2-Cray_FABM
REF=AMM7_FABM
printf 'y\nn\nn\ny\nn\nn\nn\nn\n' |./makenemo -n $CFG -r $REF -m $ARCH -j 0

cp $CODE_DIR/extra-files/nemo/cpp_SANH_FABM.fcm $NEMO_DIR/cfgs/$CONFIG/cpp_$CONFIG.fcm
cp -r $CODE_DIR/extra-files/nemo/MY_SRC/ $NEMO_DIR/cfgs/$CONFIG/

./makenemo -n $CFG -r $REF -m $ARCH -j 4 clean
./makenemo -n $CFG -r $REF -m $ARCH -j 4 

cd $WORK
