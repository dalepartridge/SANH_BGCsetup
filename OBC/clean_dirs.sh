
# Quick script to clean directories


declare -a dirs=("hadgem" )

for d in ${dirs[@]}; do
cd $d
rm -rf *.namelist *.nc *.drwn *.sh
cd ..
done


