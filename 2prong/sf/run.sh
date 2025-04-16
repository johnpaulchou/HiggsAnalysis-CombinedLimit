#!/bin/bash

./makeworkspace.py 2018
./makenewcard.py
text2workspace.py newcard.txt
combine -M MultiDimFit newcard.root --saveWorkspace -v 0
./drawfits.py higgsCombineTest.MultiDimFit.mH120.root --year 2018
#combine -M MultiDimFit newcard.root --algo singles -P r -P scalePar --setParameterRanges r=0.3,1.5:scalePar=0.8,1.2


rLo=0.3
rHi=2.0
shiftLo=-0.2
shiftHi=0.2
stretchLo=0.9
stretchHi=1.3

combine -M MultiDimFit newcard.root --algo grid --points 200 --cminDefaultMinimizerStrategy 0 -P r -P shiftPar --setParameterRanges r=$rLo,$rHi:shiftPar=$shiftLo,$shiftHi
./draw2Dscan.py higgsCombineTest.MultiDimFit.mH120.root --year 2018 --xrange r $rLo $rHi --yrange shiftPar $shiftLo $shiftHi
combine -M MultiDimFit newcard.root --algo grid --points 200 --cminDefaultMinimizerStrategy 0 -P r -P stretchPar --setParameterRanges r=$rLo,$rHi:stretchPar=$stretchLo,$stretchHi
./draw2Dscan.py higgsCombineTest.MultiDimFit.mH120.root --year 2018 --xrange r $rLo $rHi --yrange stretchPar $stretchLo $stretchHi
combine -M MultiDimFit newcard.root --algo grid --points 200 --cminDefaultMinimizerStrategy 0 -P shiftPar -P stretchPar --setParameterRanges shiftPar=$shiftLo,$shiftHi:stretchPar=$stretchLo,$stretchHi
./draw2Dscan.py higgsCombineTest.MultiDimFit.mH120.root --year 2018 --xrange shiftPar $shiftLo $shiftHi --yrange stretchPar $stretchLo $stretchHi
