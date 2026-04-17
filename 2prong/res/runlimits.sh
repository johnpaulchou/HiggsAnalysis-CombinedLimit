#!/bin/bash

region=sideband
sigtype=eta

for mass in {102..102}
do
    echo "Processing mass $mass"
    ./makebkgworkspace.py --region $region --sigtype $sigtype
    ./makesigworkspace.py --region $region --sigtype $sigtype --imass $mass
    ./makenewcard.py --region $region --sigtype $sigtype
    text2workspace.py newcard.txt

    combine -M FitDiagnostics newcard.root -m $mass --X-rtd MINIMIZER_freezeDisassociatedParams --cminDefaultMinimizerStrategy 0 -v 2 --rMin 0 --rMax 200 --freezeParameters lumi

    combine -M AsymptoticLimits newcard.txt -m $mass --X-rtd MINIMIZER_freezeDisassociatedParams --cminDefaultMinimizerStrategy 0

done
