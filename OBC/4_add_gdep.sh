
for i in bdyfiles/sanh*nc; do
  ncks -A bdy_depths.nc $i
done

