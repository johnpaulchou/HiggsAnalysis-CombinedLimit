#!/bin/bash

for mass in {0..8}
#for mass in {4..4}
do
    ./makeworkspace.py --imass $mass
    ./makenewcard.py --imass $mass
    echo "Processing mass $mass"
    combine -M AsymptoticLimits newcard.txt
#    combine -M HybridNew --LHCmode LHC-limits newcard.txt
#    combine -M HybridNew --LHCmode LHC-limits newcard.txt --expectedFromGrid=0.5
#    combine -M HybridNew --LHCmode LHC-limits newcard.txt --expectedFromGrid=0.84
#    combine -M HybridNew --LHCmode LHC-limits newcard.txt --expectedFromGrid=0.16
done
