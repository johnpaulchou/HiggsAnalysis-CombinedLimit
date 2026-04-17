#!/bin/bash

source setup_bias.sh
./makeconstants.py
source constants.sh
if [ "$debug" = "-2" ]; then
    output="/dev/null"
else
    #output="/dev/fd/1"
    output="/dev/stdout"
fi

./makebkgworkspace.py --region $region --sigtype $sigtype
./makenewcard.py --region $region --sigtype $sigtype

for mass in ${masses[@]}; do
    for sigstr in ${sigstrs[@]}; do
        for genfix in ${genfixes[@]}; do
            for testfix in ${testfixes[@]}; do
    
                #if [[ $genfix -eq $testfix ]]; then
                #    continue
                #fi
                echo "Processing $mass $sigstr $genfix $testfix" `date`
                ./makesigworkspace.py --imass $mass --region $region --sigtype $sigtype
                text2workspace.py newcard.txt
                genfixtemp="fix$genfix"
                genfixstr="${!genfixtemp}"
                testfixtemp="fix$testfix"
                testfixstr="${!testfixtemp}"
                freeze_params0="lumi,$list_params,$freezeparams0"
                freeze_params1="lumi,$list_params,$freezeparams1"
                freeze_params2="lumi,$list_params,$freezeparams2"
                freeze_paramstmp="freeze_params$testfix"
                freeze_paramsstr="${!freeze_paramstmp}"
                
                combine newcard.txt -M GenerateOnly --setParameters lumi=0,$genfixstr --toysNoSystematics -t $niter --expectSignal $sigstr --saveToys -m 125 --freezeParameters lumi,$list_params -v $debug > "$output"
                combine -M FitDiagnostics newcard.root --toysFile higgsCombineTest.GenerateOnly.mH125.123456.root -t $niter --rMin -$rrange --rMax $rrange --cminDefaultMinimizerStrategy=1  --X-rtd MINIMIZER_freezeDisassociatedParams --setParameters $testfixstr --freezeParameters $freeze_paramsstr -v $debug > "$output"

                mv fitDiagnosticsTest.root fitDiagnosticsTest_m${mass}_sig${sigstr}_gen${genfix}_test${testfix}.root
            done
        done
    done
done
