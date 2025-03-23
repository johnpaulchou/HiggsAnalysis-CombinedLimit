#!/bin/env python3

import ROOT
import sys
import argparse
import numpy

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

# luminosity for the dataset
luminosity=59.

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

# x-section as a function of m_phi from an interpolation of the phi masses
def get_xsection(phimass):
    theory_xs = [(450., 585.983), (500., 353.898), (625., 117.508), (750., 45.9397), (875., 20.1308),
                 (1000., 9.59447), (1125., 4.88278), (1250., 2.61745), (1375., 1.46371),
                 (1500., 0.847454), (1625., 0.505322), (1750., 0.309008), (1875., 0.192939),
                 (2000., 0.122826), (2125., 0.0795248), (2250., 0.0522742), (2375., 0.0348093),
                 (2500., 0.0235639), (2625., 0.0161926), (2750., 0.0109283), (2875., 0.00759881)]
    assert(phimass>=theory_xs[0][0] and phimass<=theory_xs[len(theory_xs)-1][0])
    for i in range(len(theory_xs) - 1):
        x0, y0 = theory_xs[i]
        x1, y1 = theory_xs[i + 1]
        if x0 <= phimass <= x1:
            return y0 + (y1 - y0) * (phimass - x0) / (x1 - x0)
