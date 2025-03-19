#!/bin/bash

#set -x

niter="100"

for mass in {0..8}; do
    ./makeworkspace.py --imass $mass
    ./makenewcard.py --imass $mass
    echo "Processing mass $mass"

    for strength in $(seq 0.0 0.5 1.0); do
    
	if [ "$mass" == "0" ]; then
	    range="1.0"
	elif [ "$mass" == "1" ]; then
	    range="2.0"
	elif [ "$mass" == "2" ]; then
	    range="5.0"
	else
	    range="10."
	fi

	lo=`echo "$strength-$range" | bc`
	hi=`echo "$strength+$range" | bc`
    
	combine newcard.txt -M GenerateOnly --toysFrequentist -t $niter --expectSignal $strength --saveToys -m 125
	combine newcard.txt -M FitDiagnostics --toysFile higgsCombineTest.GenerateOnly.mH125.123456.root  -t $niter --rMin $lo --rMax $hi --cminDefaultMinimizerStrategy=0
	mv fitDiagnosticsTest.root fitDiagnosticsTest_m${mass}_sig${strength}.root

    done
done

