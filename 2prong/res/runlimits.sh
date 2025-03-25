#!/bin/bash

for mass in {0..0}
do
    echo "Processing mass $mass"
    ./makebkgworkspace.py
    ./makesigworkspace.py --imass $mass
    ./makenewcard.py
    text2workspace.py newcard.txt
    combine -M FitDiagnostics newcard.root --X-rtd MINIMIZER_freezeDisassociatedParams --cminDefaultMinimizerStrategy=0 -v 2
    combine -M AsymptoticLimits newcard.txt --X-rtd MINIMIZER_freezeDisassociatedParams

    mv higgsCombineTest.AsymptoticLimits.mH120.root higgsCombineTest.AsymptoticLimits.m${mass}.root
    mv higgsCombineTest.FitDiagnostics.mH120.root higgsCombineTest.FitDiagnostics.m${mass}.root
done
