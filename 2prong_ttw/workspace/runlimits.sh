#!/bin/bash

for mass in {0..8}
#for mass in {0..0}
do
    ./makeworkspace.py --imass $mass --region asymnoniso
    ./makenewcard.py --imass $mass
    echo "Processing mass $mass"
    combine -M AsymptoticLimits newcard.txt
    combine -M Significance newcard.txt
    mv higgsCombineTest.AsymptoticLimits.mH120.root higgsCombineTest.AsymptoticLimits.m${mass}.root
    mv higgsCombineTest.Significance.mH120.root higgsCombineTest.Significance.m${mass}.root
done
