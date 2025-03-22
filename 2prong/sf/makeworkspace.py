#!/bin/env python3

import ROOT
import argparse

# function to get a TH1 from a root file
def getTH1(histname,filename):
    rootfile = ROOT.TFile(filename, "READ")
    if not rootfile or rootfile.IsZombie():
        print("Error: Unable to open file '{filename}'.")
        return None

    hist = rootfile.Get(histname)
    if not hist or not isinstance(hist, ROOT.TH1) or hist is None:
        print("Error: Histogram '", histname, "' not found or is not a valid TH1 object in the file '", filename ,"'.")
        exit(1)
        rootfile.Close()
        return None
    hist.SetDirectory(0)
    rootfile.Close()
    return hist

# where to write things out
fileoutname = "workspace.root"
workspacename = "w"

# create the observable
x = ROOT.RooRealVar("x","x-axis parameter",5.,20.)

# where to read things from
filename="hists.root"

###############################################################
# start of the "main" function
###############################################################

if __name__ == "__main__":

    # setup the output file and workspace
    fileout = ROOT.TFile(fileoutname,"RECREATE")
    w = ROOT.RooWorkspace(workspacename,workspacename)

    

