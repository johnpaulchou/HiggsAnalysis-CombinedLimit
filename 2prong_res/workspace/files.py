#!/bin/env python3

import ROOT
import os
import numpy
import sys

# input filenames
pathname = os.getcwd()
data2018filename = pathname+"/../input/egamma18.root"

# set up the grid of generated points and their corresponding input files
gengridw = ( (1.0, "1p0"), (2.0, "2p0") )
gengridp = ( (1000., "1000"), (2500., "2500") )
genfilenames = [ [""]*len(gengridw)]*len(gengridp)
for i in range(len(gengridw)):
    for j in range(len(gengridp)):
        genfilenames[i][j]=pathname+"/../input/signal_2x2box_"+gengridp[j][1]+"_"+gengridw[i][1]+"_200k_events.root"
        
# omega and phi mass points to run over
wmasspoints = numpy.arange(1.0, 2.0+0.1, 0.1)
pmasspoints = numpy.arange(1000, 2500+100, 100)
npoints = len(wmasspoints)*len(pmasspoints)

# list of systematics
systs = [ "" ]

# convert wmass to a string
def wmasstostr(wmass):
    return "{:.2f}".format(wmass)

# convert pmass to a string
def pmasstostr(pmass):
    return "{:.0f}".format(pmass)

# create signal workspace filename
def sigworkspacefn(wmass, pmass):
    return "sigworkspace_"+wmasstostr(wmass)+"_"+pmasstostr(pmass)+".root"


# function to get a TH1 from a ROOT file
def getTH1(filename,histname):
    rootfile = ROOT.TFile(filename, "READ")
    if not rootfile or rootfile.IsZombie():
        print("Error: Unable to open file '{file_name}'.")
        return None

    hist = rootfile.Get(histname)
    if not hist or not isinstance(hist, ROOT.TH1) or hist is None:
        print("Error: Histogram '"+histname+"' not found or is not a valid TH1 object in the file '"+filename+"'.")
        rootfile.Close()
        return None

    hist.SetDirectory(0)
    rootfile.Close()
    return hist

# basic function is to return the wmass and pmass from a "job ID" running from 1 to npoints
if __name__ == "__main__":
    if len(sys.argv)<2:
        print("files.py JobId")
        exit(1)
    jobid=int(sys.argv[1])-1
    windex = jobid % len(wmasspoints)
    pindex = int(jobid / len(wmasspoints))
    wmass = wmasspoints[windex]
    pmass = pmasspoints[pindex]
    print(wmasstostr(wmass)+" "+pmasstostr(pmass))
