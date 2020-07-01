
# Quick script to clean directories


declare -a dirs=("ady" "glodap" "imarnet" "occci" "woa18" "woa18-oxy" )

for d in ${dirs[@]}; do
cd $d
rm -rf *.namelist *.nc *.drwn *.sh
cd ..
done


