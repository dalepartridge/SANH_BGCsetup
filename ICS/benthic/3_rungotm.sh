
Nens=99 #Number of ensembles
Ns=1 # start number
bs=32 #batch size


while [ $Ns -le $Nens ]; do
    Ne=$(($Ns + $bs - 1))
    if [ $Ne -gt $Nens ]; then
        Ne=$Nens
    fi
    qsub -J $Ns-$Ne 3_rungotm.pbs
    Ns=$(($Ns + $bs))
done

