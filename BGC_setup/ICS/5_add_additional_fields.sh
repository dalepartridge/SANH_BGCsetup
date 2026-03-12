#!/usr/bin/env bash
ncap2 -O -s TRBN6_h=0*TRNN3_n+1e-8 restart_trc.nc restart_trc.nc
ncap2 -O -s TRNN6_h=0*TRBN3_n+1e-8 restart_trc.nc restart_trc.nc

ncap2 -O -s TRBDIN_ban_n=0*TRNN3_n restart_trc.nc restart_trc.nc
ncap2 -O -s TRNDIN_ban_n=0*TRNN3_n restart_trc.nc restart_trc.nc
ncap2 -O -s TRBDON_ban_n=0*TRNN3_n restart_trc.nc restart_trc.nc
ncap2 -O -s TRNDON_ban_n=0*TRNN3_n restart_trc.nc restart_trc.nc

ncap2 -O -s TRBDIN_ind_n=0*TRNN3_n restart_trc.nc restart_trc.nc
ncap2 -O -s TRNDIN_ind_n=0*TRNN3_n restart_trc.nc restart_trc.nc
ncap2 -O -s TRBDON_ind_n=0*TRNN3_n restart_trc.nc restart_trc.nc
ncap2 -O -s TRNDON_ind_n=0*TRNN3_n restart_trc.nc restart_trc.nc

ncap2 -O -s TRBDIN_mya_n=0*TRNN3_n restart_trc.nc restart_trc.nc
ncap2 -O -s TRNDIN_mya_n=0*TRNN3_n restart_trc.nc restart_trc.nc
ncap2 -O -s TRBDON_mya_n=0*TRNN3_n restart_trc.nc restart_trc.nc
ncap2 -O -s TRNDON_mya_n=0*TRNN3_n restart_trc.nc restart_trc.nc

ncap2 -O -s TRBDIN_pak_n=0*TRNN3_n restart_trc.nc restart_trc.nc
ncap2 -O -s TRNDIN_pak_n=0*TRNN3_n restart_trc.nc restart_trc.nc
ncap2 -O -s TRBDON_pak_n=0*TRNN3_n restart_trc.nc restart_trc.nc
ncap2 -O -s TRNDON_pak_n=0*TRNN3_n restart_trc.nc restart_trc.nc

ncap2 -O -s TRBDIN_sri_n=0*TRNN3_n restart_trc.nc restart_trc.nc
ncap2 -O -s TRNDIN_sri_n=0*TRNN3_n restart_trc.nc restart_trc.nc
ncap2 -O -s TRBDON_sri_n=0*TRNN3_n restart_trc.nc restart_trc.nc
ncap2 -O -s TRNDON_sri_n=0*TRNN3_n restart_trc.nc restart_trc.nc

