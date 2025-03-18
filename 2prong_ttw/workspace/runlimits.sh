#!/bin/bash

for mass in {0..8}
#for mass in {0..0}
do
    ./makeworkspace.py --imass $mass --region asymnoniso
    ./makenewcard.py --imass $mass
    echo "Processing mass $mass"
    combine -M AsymptoticLimits newcard.txt
done
