#!/bin/bash

rLo=0.3
rHi=2.5
shiftLo=-0.2
shiftHi=0.2
stretchLo=0.9
stretchHi=1.3

for year in 2016 2017 2018;
do
    ./makeworkspace.py $year
    ./makenewcard.py
    text2workspace.py newcard.txt
    combine -M MultiDimFit newcard.root --saveWorkspace --cminDefaultMinimizerStrategy 0 -v 0
    ./drawfits.py higgsCombineTest.MultiDimFit.mH120.root --year $year

    combine -M MultiDimFit newcard.root --algo grid --points 100 --cminDefaultMinimizerStrategy 0 -P r -P shiftPar --setParameterRanges r=$rLo,$rHi:shiftPar=$shiftLo,$shiftHi
    ./draw2Dscan.py higgsCombineTest.MultiDimFit.mH120.root --year $year --xvar r --yvar shiftPar
    combine -M MultiDimFit newcard.root --algo grid --points 100 --cminDefaultMinimizerStrategy 0 -P r -P stretchPar --setParameterRanges r=$rLo,$rHi:stretchPar=$stretchLo,$stretchHi
    ./draw2Dscan.py higgsCombineTest.MultiDimFit.mH120.root --year $year --xvar r --yvar stretchPar
    combine -M MultiDimFit newcard.root --algo grid --points 100 --cminDefaultMinimizerStrategy 0 -P shiftPar -P stretchPar --setParameterRanges shiftPar=$shiftLo,$shiftHi:stretchPar=$stretchLo,$stretchHi
    ./draw2Dscan.py higgsCombineTest.MultiDimFit.mH120.root --year $year --xvar shiftPar --yvar stretchPar

done
