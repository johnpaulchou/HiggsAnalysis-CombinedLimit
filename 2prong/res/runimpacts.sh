#!/bin/bash

region=sideband
sigtype=eta
mass=10
param=3

./makebkgworkspace.py --region $region --sigtype $sigtype
./makesigworkspace.py --region $region --sigtype $sigtype --imass $mass
./makenewcard.py --region $region --sigtype $sigtype --cardname combine$param.txt
text2workspace.py newcard.txt

combineTool.py -M Impacts -d newcard.root -m 125 --robustFit 1 --cminDefaultMinimizerStrategy 1 --setParameterRanges r=-1.,1. --doInitialFit
combineTool.py -M Impacts -d newcard.root -m 125 --robustFit 1 --cminDefaultMinimizerStrategy 1 --setParameterRanges r=-1.,1. --doFits
combineTool.py -M Impacts -d newcard.root -m 125 --robustFit 1 --cminDefaultMinimizerStrategy 1 --setParameterRanges r=-1.,1. -o impacts_$param.json

plotImpacts.py -i impacts_$param.json -o impacts_$param --POI r
