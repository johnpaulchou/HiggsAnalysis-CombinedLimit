#!/bin/bash

region=sideband
sigtype=eta

for mass in {50..50}
do
    echo "Processing mass $mass"
    ./makebkgworkspace.py --region $region --sigtype $sigtype
    ./makesigworkspace.py --region $region --sigtype $sigtype --imass $mass
    ./makenewcard.py --region $region --sigtype $sigtype
    text2workspace.py newcard.txt
#    combine -M FitDiagnostics newcard.root -m $mass --X-rtd MINIMIZER_freezeDisassociatedParams --cminDefaultMinimizerStrategy 1 -v 2 --rMin -10 --rMax 10 --setParameters pdfindex_bin0barrel=0,pdfindex_bin1barrel=0,pdfindex_bin2barrel=0,pdfindex_bin3barrel=0,pdfindex_bin4barrel=0,pdfindex_bin5barrel=0,pdfindex_bin6barrel=0,pdfindex_bin7barrel=0,pdfindex_bin8barrel=0,pdfindex_bin9barrel=0,pdfindex_bin10barrel=0,pdfindex_bin11barrel=0,pdfindex_bin12barrel=0,pdfindex_bin13barrel=0,pdfindex_bin14barrel=0,pdfindex_bin15barrel=0,pdfindex_bin16barrel=0,pdfindex_bin17barrel=0,pdfindex_bin18barrel=0,pdfindex_bin19barrel=0,pdfindex_bin20barrel=0,pdfindex_bin0endcap=0,pdfindex_bin1endcap=0,pdfindex_bin2endcap=0,pdfindex_bin3endcap=0,pdfindex_bin4endcap=0,pdfindex_bin5endcap=0,pdfindex_bin6endcap=0,pdfindex_bin7endcap=0,pdfindex_bin8endcap=0,pdfindex_bin9endcap=0,pdfindex_bin10endcap=0,pdfindex_bin11endcap=0,pdfindex_bin12endcap=0,pdfindex_bin13endcap=0,pdfindex_bin14endcap=0,pdfindex_bin15endcap=0,pdfindex_bin16endcap=0,pdfindex_bin17endcap=0,pdfindex_bin18endcap=0,pdfindex_bin19endcap=0,pdfindex_bin20endcap=0 --freezeParameters pdfindex_bin0barrel,pdfindex_bin1barrel,pdfindex_bin2barrel,pdfindex_bin3barrel,pdfindex_bin4barrel,pdfindex_bin5barrel,pdfindex_bin6barrel,pdfindex_bin7barrel,pdfindex_bin8barrel,pdfindex_bin9barrel,pdfindex_bin10barrel,pdfindex_bin11barrel,pdfindex_bin12barrel,pdfindex_bin13barrel,pdfindex_bin14barrel,pdfindex_bin15barrel,pdfindex_bin16barrel,pdfindex_bin17barrel,pdfindex_bin18barrel,pdfindex_bin19barrel,pdfindex_bin20barrel,pdfindex_bin0endcap,pdfindex_bin1endcap,pdfindex_bin2endcap,pdfindex_bin3endcap,pdfindex_bin4endcap,pdfindex_bin5endcap,pdfindex_bin6endcap,pdfindex_bin7endcap,pdfindex_bin8endcap,pdfindex_bin9endcap,pdfindex_bin10endcap,pdfindex_bin11endcap,pdfindex_bin12endcap,pdfindex_bin13endcap,pdfindex_bin14endcap,pdfindex_bin15endcap,pdfindex_bin16endcap,pdfindex_bin17endcap,pdfindex_bin18endcap,pdfindex_bin19endcap,pdfindex_bin20endcap,p3_bin0barrel,p3_bin0endcap,p4_bin0barrel,p4_bin0endcap,p5_bin0barrel,p5_bin0endcap,p6_bin0barrel,p6_bin0endcap,p3_bin1barrel,p3_bin1endcap,p4_bin1barrel,p4_bin1endcap,p5_bin1barrel,p5_bin1endcap,p6_bin1barrel,p6_bin1endcap,p3_bin2barrel,p3_bin2endcap,p4_bin2barrel,p4_bin2endcap,p5_bin2barrel,p5_bin2endcap,p6_bin2barrel,p6_bin2endcap,p3_bin3barrel,p3_bin3endcap,p4_bin3barrel,p4_bin3endcap,p5_bin3barrel,p5_bin3endcap,p6_bin3barrel,p6_bin3endcap,p3_bin4barrel,p3_bin4endcap,p4_bin4barrel,p4_bin4endcap,p5_bin4barrel,p5_bin4endcap,p6_bin4barrel,p6_bin4endcap,p3_bin5barrel,p3_bin5endcap,p4_bin5barrel,p4_bin5endcap,p5_bin5barrel,p5_bin5endcap,p6_bin5barrel,p6_bin5endcap,lumi
    combine -M FitDiagnostics newcard.root -m $mass --X-rtd MINIMIZER_freezeDisassociatedParams --cminDefaultMinimizerStrategy 1 -v 2 --rMin -10 --rMax 10 --freezeParameters lumi

    combine -M AsymptoticLimits newcard.txt -m $mass --X-rtd MINIMIZER_freezeDisassociatedParams --cminDefaultMinimizerStrategy 0

done
