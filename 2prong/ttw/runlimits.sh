#!/bin/bash

for mass in {0..8}
do
    ./makeworkspace.py --imass $mass --region symiso --sigtype eta
    ./makenewcard.py
    combine -M AsymptoticLimits newcard.txt -m $mass
    combine -M Significance newcard.txt -m $mass
done
