#################################################
# Script to compile XIOS2.5
# Tested on revision 2022, following instructions provided https://docs.archer2.ac.uk/research-software/nemo/nemo/#compiling-xios-and-nemo
#
# Note that a precompiled version of XIOS2.5 is available for use here:
# /work/n01/shared/acc/xios-2.5
#################################################

if [ "$ARCHER2" = true ] ; then
yes | cp $CODE_DIR/archer2-files/xios/arch-X86_ARCHER2-Cray* $XIOS_CLONE/arch/
yes | cp $CODE_DIR/archer2-files/xios/Config_cray.pm $XIOS_CLONE/tools/FCM/lib/Fcm/Config.pm
fi

cd $XIOS_CLONE && ./make_xios --prod --arch $XIOS_ARCH --netcdf_lib netcdf4_par --job 16 --full
rsync -a $XIOS_CLONE/bin $XIOS_CLONE/inc $XIOS_CLONE/lib $XIOS_HOME

cp $XIOS_HOME/bin/xios_server.exe $CODE_DIR/excutable/xios

cd $WORK
