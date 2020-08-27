
for i in bdyfiles/sanh*nc; do
  ncks -A bdy_gdept.nc $i
done

