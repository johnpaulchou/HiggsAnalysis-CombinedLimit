#!/bin/bash

rm -f bkgworkspace.root newcard.root sigworkspace.root

source setup_limits.sh
output="/dev/null"
#output="/dev/stdout"

for mass in ${masses[@]}; do
    echo ""
    date
    echo "Processing mass $mass"
    ./makebkgworkspace.py --region $region --sigtype $sigtype &> "$output"
    echo "."
    ./makesigworkspace_mod.py --region $region --sigtype $sigtype --raw --imass $mass > "$output"
    if [[ $? -ne 0 ]]; then
        echo "ERROR: signal workspace failed, skipping $mass."
        continue
    fi
    echo ".."
    ./makenewcard.py --region $region --sigtype $sigtype
    echo "..."
    #text2workspace.py newcard.txt
    #echo "...."

    #combine -M FitDiagnostics newcard.root -m $mass --X-rtd MINIMIZER_freezeDisassociatedParams --cminDefaultMinimizerStrategy 0 -v $debug --rMin 0 --rMax 200 --freezeParameters lumi &> "$output"
    #echo ""
    #date
    #echo "fit diagnostics mass $mass"

    rm higgsCombineTest.AsymptoticLimits.mH$mass.root
    combine -M AsymptoticLimits newcard.txt -m $mass --X-rtd MINIMIZER_freezeDisassociatedParams --cminDefaultMinimizerStrategy 0 -v $debug --rAbsAcc 0.02 --rRelAcc 0.05
    echo "....."
done

date
echo "Finished"
