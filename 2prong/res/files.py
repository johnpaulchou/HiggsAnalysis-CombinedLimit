#!/bin/env python3

import ROOT
import numpy
import sys
import argparse

# regions to consider
regions = ["sideband","signal"]
etabins = ["barrel","endcap"]
m2pbins = range(3,26)

# setup observables
m2pg = ROOT.RooRealVar("m2pg","Invariant mass of the 2-prong and photon",500,4020)
m2p = ROOT.RooRealVar("m2p","Invariant mass of the 2-prong",0.4,5.33)

# list of systematics
systs = [ "" ]

# signal and background workspace filenames
sigworkspacefn="sigworkspace.root"
bkgworkspacefn="bkgworkspace.root"
workspacename="w"

# data file names
#datafilename = "./input/egamma18.root"
#datafilename = "./input/HISTO_photon2017.root"
#datafilename = "./input/HISTO_photon2016pre.root"
datafilename = "./input/HISTO_photon2016post.root"

# set up the grid of generated points and their corresponding input files
gengridw = ( (1.0, "1p0"), (2.0, "2p0") )
gengridp = ( (1000., "1000"), (2500., "2500") )
genfilenames = [ [""]*len(gengridw) for i in range(len(gengridp))]
for i in range(len(gengridw)):
    for j in range(len(gengridp)):
        genfilenames[i][j]="./input/signal_2x2box_"+gengridp[j][1]+"_"+gengridw[i][1]+"_200k_events.root"

# omega and phi mass points to run over
wmasspoints = numpy.arange(1.0, 2.0+0.1, 0.1)
pmasspoints = numpy.arange(1000, 2500+100, 100)
npoints = len(wmasspoints)*len(pmasspoints)

# convert a single index into a wmassindex and a pmassindex
def indexpair(index):
    assert(index>=0 and index<npoints)
    windex = index % len(wmasspoints)
    pindex = int(index / len(wmasspoints))
    return (windex, pindex)

# convert a wmassindex and pmassindex to a single index (inverse of the above)
def index(wmassindex, pmassindex):
    assert(wmassindex>=0 and wmassindex<len(wmasspoints))
    assert(pmassindex>=0 and pmassindex<len(pmasspoints))
    return wmassindex+pmassindex*len(wmasspoints)


"""
###############################################################
# start of the "main" function
# basic function is to return the wmass and pmass from a "job ID" running from 0 to npoints-1
###############################################################

if __name__ == "__main__":

    # setup and use the parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('jobid', help="index of the job to run (0-"+str(npoints-1)+")", type=int)
    args=parser.parse_args()
    jobid=args.jobid
    (windex,pindex)=indexpair(jobid)
    wmass = wmasspoints[windex]
    pmass = pmasspoints[pindex]
    print(wmasstostr(wmass)+" "+pmasstostr(pmass))

"""
