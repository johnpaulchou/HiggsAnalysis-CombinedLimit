#!/bin/bash

region=asymnoniso
sigtype=eta
mass=3

./makeworkspace.py --imass $mass --region $region --sigtype $sigtype
./makenewcard.py
text2workspace.py newcard.txt

combineTool.py -M Impacts -d newcard.root -m 125 --robustFit 1 --cminDefaultMinimizerStrategy 1 --setParameterRanges r=-5.,5. --doInitialFit
combineTool.py -M Impacts -d newcard.root -m 125 --robustFit 1 --cminDefaultMinimizerStrategy 1 --setParameterRanges r=-5.,5. --doFits
combineTool.py -M Impacts -d newcard.root -m 125 --robustFit 1 --cminDefaultMinimizerStrategy 1 --setParameterRanges r=-5.,5. -o impacts.json

plotImpacts.py -i impacts.json -o impacts --POI r
