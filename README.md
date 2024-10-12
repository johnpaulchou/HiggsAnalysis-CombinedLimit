HiggsAnalysis-CombinedLimit
===========================

### This Branch is for the ɸ->ωω, ω->πππ analysis, and the ttω, ω->πππ analysis
This was forked from the v9.2.1 tag of the master

# Official documentation

All documentation, including installation instructions, is hosted at
http://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/latest

The source code of this documentation can be found in the `docs/` folder in this repository.

# Instructions
```
cmsrel CMSSW_14_1_0_pre4
cd CMSSW_14_1_0_pre4/src
cmsenv
git clone https://github.com/johnpaulchou/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git checkout Brandon
scramv1 b clean; scramv1 b # always make a clean build
```
=======
### Publication 

The `Combine` tool publication can be found [here](https://arxiv.org/abs/2404.06614). Please consider citing this reference if you use the `Combine` tool. 
