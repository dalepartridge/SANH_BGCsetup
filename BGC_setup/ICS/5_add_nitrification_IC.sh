#!/usr/bin/env bash
module load cray-hdf5-parallel/1.12.0.7
module load cray-netcdf-hdf5parallel/4.7.4.7

ncap2 -O -s TRBN6_h=0*TRNN3_n+1e-8 restart_trc.nc restart_trc.nc
ncap2 -O -s TRNN6_h=0*TRBN3_n+1e-8 restart_trc.nc restart_trc.nc
