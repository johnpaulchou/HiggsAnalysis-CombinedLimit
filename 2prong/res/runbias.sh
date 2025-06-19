#!/bin/bash

#set -x

niter="10"

./makebkgworkspace.py
./makenewcard.py
#for mass in 0 10 165 175; do
for mass in 0 175; do
    ./makesigworkspace.py --imass $mass
    echo "Processing mass point $mass"

    signal=1.0
    combine newcard.txt -M GenerateOnly --setParameters pdfindex_bin0barrel=0,pdfindex_bin1barrel=0,pdfindex_bin2barrel=0,pdfindex_bin3barrel=0,pdfindex_bin4barrel=0,pdfindex_bin5barrel=0,pdfindex_bin6barrel=0,pdfindex_bin7barrel=0,pdfindex_bin8barrel=0,pdfindex_bin9barrel=0,pdfindex_bin10barrel=0,pdfindex_bin11barrel=0,pdfindex_bin12barrel=0,pdfindex_bin13barrel=0,pdfindex_bin14barrel=0,pdfindex_bin15barrel=0,pdfindex_bin16barrel=0,pdfindex_bin17barrel=0,pdfindex_bin18barrel=0,pdfindex_bin19barrel=0,pdfindex_bin20barrel=0,pdfindex_bin0endcap=0,pdfindex_bin1endcap=0,pdfindex_bin2endcap=0,pdfindex_bin3endcap=0,pdfindex_bin4endcap=0,pdfindex_bin5endcap=0,pdfindex_bin6endcap=0,pdfindex_bin7endcap=0,pdfindex_bin8endcap=0,pdfindex_bin9endcap=0,pdfindex_bin10endcap=0,pdfindex_bin11endcap=0,pdfindex_bin12endcap=0,pdfindex_bin13endcap=0,pdfindex_bin14endcap=0,pdfindex_bin15endcap=0,pdfindex_bin16endcap=0,pdfindex_bin17endcap=0,pdfindex_bin18endcap=0,pdfindex_bin19endcap=0,pdfindex_bin20endcap=0 --toysFrequentist -t $niter --expectSignal $signal --saveToys -m 125 --freezeParameters pdfindex_bin0barrel,pdfindex_bin1barrel,pdfindex_bin2barrel,pdfindex_bin3barrel,pdfindex_bin4barrel,pdfindex_bin5barrel,pdfindex_bin6barrel,pdfindex_bin7barrel,pdfindex_bin8barrel,pdfindex_bin9barrel,pdfindex_bin10barrel,pdfindex_bin11barrel,pdfindex_bin12barrel,pdfindex_bin13barrel,pdfindex_bin14barrel,pdfindex_bin15barrel,pdfindex_bin16barrel,pdfindex_bin17barrel,pdfindex_bin18barrel,pdfindex_bin19barrel,pdfindex_bin20barrel,pdfindex_bin0endcap,pdfindex_bin1endcap,pdfindex_bin2endcap,pdfindex_bin3endcap,pdfindex_bin4endcap,pdfindex_bin5endcap,pdfindex_bin6endcap,pdfindex_bin7endcap,pdfindex_bin8endcap,pdfindex_bin9endcap,pdfindex_bin10endcap,pdfindex_bin11endcap,pdfindex_bin12endcap,pdfindex_bin13endcap,pdfindex_bin14endcap,pdfindex_bin15endcap,pdfindex_bin16endcap,pdfindex_bin17endcap,pdfindex_bin18endcap,pdfindex_bin19endcap,pdfindex_bin20endcap,pdfindex_bin21endcap,pdfindex_bin22endcap,pdfindex_bin23endcap

    combine newcard.txt -M FitDiagnostics --toysFile higgsCombineTest.GenerateOnly.mH125.123456.root -t $niter --rMin -10 --rMax 10 --cminDefaultMinimizerStrategy=0 --X-rtd MINIMIZER_freezeDisassociatedParams --setParameters pdfindex_bin0barrel=1,pdfindex_bin1barrel=1,pdfindex_bin2barrel=1,pdfindex_bin3barrel=1,pdfindex_bin4barrel=1,pdfindex_bin5barrel=1,pdfindex_bin6barrel=1,pdfindex_bin7barrel=1,pdfindex_bin8barrel=1,pdfindex_bin9barrel=1,pdfindex_bin10barrel=1,pdfindex_bin11barrel=1,pdfindex_bin12barrel=1,pdfindex_bin13barrel=1,pdfindex_bin14barrel=1,pdfindex_bin15barrel=1,pdfindex_bin16barrel=1,pdfindex_bin17barrel=1,pdfindex_bin18barrel=1,pdfindex_bin19barrel=1,pdfindex_bin20barrel=1,pdfindex_bin0endcap=1,pdfindex_bin1endcap=1,pdfindex_bin2endcap=1,pdfindex_bin3endcap=1,pdfindex_bin4endcap=1,pdfindex_bin5endcap=1,pdfindex_bin6endcap=1,pdfindex_bin7endcap=1,pdfindex_bin8endcap=1,pdfindex_bin9endcap=1,pdfindex_bin10endcap=1,pdfindex_bin11endcap=1,pdfindex_bin12endcap=1,pdfindex_bin13endcap=1,pdfindex_bin14endcap=1,pdfindex_bin15endcap=1,pdfindex_bin16endcap=1,pdfindex_bin17endcap=1,pdfindex_bin18endcap=1,pdfindex_bin19endcap=1,pdfindex_bin20endcap=1
    mv fitDiagnosticsTest.root fitDiagnosticsTest_m${mass}_sig1.root

    done
done

