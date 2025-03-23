#!/bin/bash

for mass in {0..0}
do
    echo "Processing mass $mass"
    ./makebkgworkspace.py
    ./makesigworkspace.py --imass $mass
    ./makenewcard.py
    text2workspace.py newcard.txt
    combine -M FitDiagnostics newcard.root --X-rtd MINIMIZER_freezeDisassociatedParams
    combine -M AsymptoticLimits newcard.txt --X-rtd MINIMIZER_freezeDisassociatedParams

    mv higgsCombineTest.AsymptoticLimits.mH120.root higgsCombineTest.AsymptoticLimits.m${mass}.root
    mv higgsCombineTest.Significance.mH120.root higgsCombineTest.Significance.m${mass}.root
done
