#! /bin/sh
echo ">>> Starting job on" `date`
echo ">>> Running on: `uname -a`"
echo ">>> System software: `cat /etc/redhat-release`"
echo ""
echo "&&& Here there are all the input arguments &&&"
echo $@
export INITIAL_DIR=$(pwd)
export HOME=$INITIAL_DIR
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch

source $VO_CMS_SW_DIR/cmsset_default.sh
tar -xvf combine.tgz
ls -alh .
cd CMSSW_14_1_0_pre4/src/HiggsAnalysis/CombinedLimit/2prong_res/workspace
eval `scramv1 runtime -sh`
scramv1 b ProjectRename  

echo '&&& CMSSW_BASE: &&&'
echo $CMSSW_BASE
echo '&&& ROOTSYS: &&&'
echo $ROOTSYS

echo '&&& ROOT version &&&'
export DISPLAY=localhost:0.0
root -l -q -e "gROOT->GetVersion()"
unset DISPLAY

python3 makebkgworkspace.py
./makesigworkspace.py `./files.py $1`
./makenewcard.py `./files.py $1`
cat newcard.txt
text2workspace.py newcard.txt
combine -M MultiDimFit newcard.root --saveWorkspace -n .bestfit
combine -M AsymptoticLimits newcard.txt
combine -M Significance newcard.txt
