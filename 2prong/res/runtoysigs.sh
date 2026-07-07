#!/bin/bash

rm -f bkgworkspace.root newcard.root sigworkspace.root

source setup_sig.sh
#output="/dev/null"
output="/dev/stdout"

for mass in ${masses[@]}; do
    echo ""
    date
    echo "Processing mass $mass"
    ./makebkgworkspace.py --region $region --sigtype $sigtype #&> "$output"
    echo "."

    ./makesigworkspace.py --region $region --sigtype $sigtype --raw --imass $mass #&> "$output"
    if [[ $? -ne 0 ]]; then
        echo "MSG: signal workspace failed for $mass."
        continue
        #echo "MSG: signal workspace failed, dropendcap for $mass."
        #./makesigworkspace.py --region $region --sigtype $sigtype --raw --imass $mass --dropendcap &> "$output"
        #echo ".."
        #./makenewcard.py --region $region --sigtype $sigtype --dropendcap
    else
        echo ".."
        ./makenewcard.py --region $region --sigtype $sigtype --cardname combine1.txt
    fi
    echo "..."
    text2workspace.py newcard.txt
    echo "...."

    combine -M HybridNew newcard.txt --LHCmode LHC-significance --saveToys --fullBToys --saveHybridResult -T $toys -s -1 -m $mass

done

date
echo "Finished"
