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

    ./makesigworkspace.py --region $region --sigtype $sigtype --raw --imass $mass &> "$output"
    if [[ $? -ne 0 ]]; then
        echo "MSG: signal workspace failed for $mass."
        continue
        #echo "MSG: signal workspace failed, dropendcap for $mass."
        #./makesigworkspace.py --region $region --sigtype $sigtype --raw --imass $mass --dropendcap &> "$output"
        #echo ".."
        #./makenewcard.py --region $region --sigtype $sigtype --dropendcap
    else
        echo ".."
        ./makenewcard.py --region $region --sigtype $sigtype
    fi
    echo "..."
    text2workspace.py newcard.txt
    echo "...."

    combine -M FitDiagnostics newcard.root -m $mass --X-rtd MINIMIZER_freezeDisassociatedParams --cminDefaultMinimizerStrategy 0 -v $debug --rMin 0 --rMax 200 --freezeParameters lumi
    echo "..... done fit"

    rm higgsCombineTest.AsymptoticLimits.mH$mass.root
    combine -M AsymptoticLimits newcard.txt -m $mass --X-rtd MINIMIZER_freezeDisassociatedParams --cminDefaultMinimizerStrategy 0 -v $debug 
    echo "...... done limit"

    combine -M Significance newcard.txt -m $mass --X-rtd MINIMIZER_freezeDisassociatedParams --cminDefaultMinimizerStrategy 0 -v $debug
    echo "....... done sig"
done

date
echo "Finished"
