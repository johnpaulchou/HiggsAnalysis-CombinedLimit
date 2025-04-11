#!/bin/bash

./makeworkspace.py 2018
./makenewcard.py
text2workspace.py newcard.txt
combine -M MultiDimFit newcard.root --saveWorkspace -v 0
./drawfits.py higgsCombineTest.MultiDimFit.mH120.root 2018
combine -M MultiDimFit newcard.root --algo grid --points 200 --cminDefaultMinimizerStrategy 0 -P r -P scalePar --setParameterRanges r=0.3,1.5:scalePar=0.8,1.2
./draw2Dscan.py

