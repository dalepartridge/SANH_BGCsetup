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
CFG=SANH_FABM
ARCH=X86_ARCHER2-Cray_FABM
REF=AMM7_FABM
printf 'y\nn\nn\ny\nn\nn\nn\nn\n' |./makenemo -n $CFG -r $REF -m $ARCH -j 0

cp $CODE_DIR/extra-files/nemo/cpp_SANH_FABM.fcm $NEMO_DIR/cfgs/$CFG/cpp_$CFG.fcm
cp -r $CODE_DIR/extra-files/nemo/MY_SRC/ $NEMO_DIR/cfgs/$CFG/

./makenemo -n $CFG -r $REF -m $ARCH -j 4 clean
./makenemo -n $CFG -r $REF -m $ARCH -j 4 


############## DEBUG #######################
CFG=SANH_FABM_DEBUG
ARCH=X86_ARCHER2-Cray_FABM_DEBUG
export FABM_HOME=$CODE_DIR/fabm-debug
cp $CODE_DIR/extra-files/nemo/cpp_SANH_FABM.fcm $NEMO_DIR/cfgs/$CFG/cpp_$CFG.fcm
cp -r $CODE_DIR/extra-files/nemo/MY_SRC/ $NEMO_DIR/cfgs/$CFG/
./makenemo -n $CFG -r $REF -m $ARCH -j 4 clean
./makenemo -n $CFG -r $REF -m $ARCH -j 4 


cd $WORK
