#!/bin/bash

############# COMPILE NEMO ##########################
cd $NEMO_DIR

if [ "$ARCHER2" = true ] ; then
yes | cp $CODE_DIR/archer2-files/nemo/Config_cray.pm $NEMO_DIR/ext/FCM/lib/Fcm/Config.pm
fi

printf 'y\nn\nn\ny\nn\nn\nn\nn\n' |./makenemo -r $NEMO_REF -m $NEMO_ARCH -n $NEMO_CFG -j 0

NEMO_CFG=SANH_FABM_DEBUG
NEMO_ARCH=X86_ARCHER2-Cray_FABM_DEBUG
NEMO_REF=AMM7_FABM

yes | cp $CODE_DIR/extra-files/nemo/cpp_SANH_FABM.fcm $NEMO_DIR/cfgs/$NEMO_CFG/cpp_$NEMO_CFG.fcm
cp -r $CODE_DIR/extra-files/nemo/MY_SRC/* $NEMO_DIR/cfgs/$NEMO_CFG/MY_SRC/

./makenemo -r $NEMO_REF -m $NEMO_ARCH -n $NEMO_CFG -j 4 clean
./makenemo -m $NEMO_ARCH -r $NEMO_REF -n $NEMO_CFG -j 8

cp $NEMO_DIR/cfgs/$NEMO_CFG/EXP00/nemo $CODE_DIR/executable/nemo-debug

cp $CODE_DIR/0_set_enviroment.sh $EXECUTABLE_DIR/build_env

