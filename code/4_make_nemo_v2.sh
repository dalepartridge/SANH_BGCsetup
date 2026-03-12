#!/bin/bash

############# COMPILE NEMO ##########################
cd $NEMO_DIR

module restore
module swap craype-network-ofi craype-network-ucx
module swap cray-mpich cray-mpich-ucx
module load cray-hdf5-parallel/1.12.2.1
module load cray-netcdf-hdf5parallel/4.9.0.1

if [ "$ARCHER2" = true ] ; then
yes | cp $CODE_DIR/archer2-files/nemo/Config_cray.pm $NEMO_DIR/ext/FCM/lib/Fcm/Config.pm
fi

printf 'y\nn\nn\ny\nn\nn\nn\nn\n' |./makenemo -r $NEMO_REF -m $NEMO_ARCH -n $NEMO_CFG -j 0

yes | cp $CODE_DIR/extra-files/nemo/cpp_SANH_FABM.fcm $NEMO_DIR/cfgs/$NEMO_CFG/cpp_$NEMO_CFG.fcm
cp -r $CODE_DIR/extra-files/nemo/MY_SRC/ $NEMO_DIR/cfgs/$NEMO_CFG/

./makenemo -r $NEMO_REF -m $NEMO_ARCH -n $NEMO_CFG -j 4 clean
./makenemo -m $NEMO_ARCH -r $NEMO_REF -n $NEMO_CFG -j 8

cp $NEMO_DIR/cfgs/$NEMO_CFG/EXP00/nemo $CODE_DIR/executable/nemo

#cp $CODE_DIR/0_set_enviroment.sh $EXECUTABLE_DIR/build_env
