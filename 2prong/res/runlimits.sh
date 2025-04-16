#!/bin/bash

for mass in {2..2}
do
    echo "Processing mass $mass"
    ./makebkgworkspace.py
    ./makesigworkspace.py --imass $mass
    ./makenewcard.py
    text2workspace.py newcard.txt
    combine -M FitDiagnostics newcard.root -m $mass --X-rtd MINIMIZER_freezeDisassociatedParams --cminDefaultMinimizerStrategy 0 -v 2
    combine -M AsymptoticLimits newcard.txt -m $mass --X-rtd MINIMIZER_freezeDisassociatedParams --cminDefaultMinimizerStrategy 0

done
