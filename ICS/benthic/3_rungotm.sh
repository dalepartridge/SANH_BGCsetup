
Nens=99 #Number of ensembles
Ns=1 # start number - DO NOT START FROM ZERO
bs=32 #batch size (max on ARCHER=32)


while [ $Ns -le $Nens ]; do
    Ne=$(($Ns + $bs - 1)) # Set range for bash submission
    if [ $Ne -gt $Nens ]; then # Check if we go past the final ensemble
        Ne=$Nens
    fi
    if [ $Ns -eq $Ne ]; then # Check if we are submitting a single job
        qsub -v "idx=$Ne" 3_rungotm.pbs
    else
        qsub -r y -J $Ns-$Ne 3_rungotm.pbs
    fi 
    Ns=$(($Ns + $bs))
done

