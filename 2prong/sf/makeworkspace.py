#!/bin/env python3

import ROOT
import argparse
import common.common as common

# where to write things out
fileoutname = "workspace.root"
workspacename = "w"

# binning labels (these are inconsistent with the cuts, as per Brandon's advice)
ptbins = ["pt20", "pt40", "pt60", "pt80"]

# set the observable range
minm2p = 0.0
maxm2p = 3.5

# signal scale (from Brandon)
def getSigScale(year):
    if year=="2018":
        return 1.8433
    elif year=="2017":
        return 1.2761
    elif year=="2016":
        return 1.1189

# where to read things from
def getDataFilename(year):
    if year=="2018":
        return "./input/data_wsmear_2018.root"
    elif year=="2017":
        return "./input/data_2017_apr21.root"
    elif year=="2016":
        return "./input/data_2016hadd_apr22.root"
        
def getSignalFilename(year):
    if year=="2018":
        return "./input/dysig_wsmear_2018.root"
    elif year=="2017":
        return "./input/dy_2017_apr21.root"
    elif year=="2016":
        return "./input/dy_2016hadd_apr22.root"


###############################################################
# start of the "main" function
###############################################################

if __name__ == "__main__":

    # setup and use the parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("year", help="year to run over")
    args=parser.parse_args()

    # setup the output file and workspace
    fileout = ROOT.TFile(fileoutname,"RECREATE")
    fileout.cd()
    w = ROOT.RooWorkspace(workspacename,workspacename)
    (ROOT.TNamed("year",args.year)).Write()
    datafilename=getDataFilename(args.year)
    signalfilename=getSignalFilename(args.year)
    
    # create the scale parameter and observable
    m2p = ROOT.RooRealVar("m2p","Invariant mass of the 2-prong",minm2p,maxm2p)

    # loop over the bins
    for ptbin in ptbins:

        # get the data
        newName = "data_"+ptbin
        dataTH1 = common.get_TH1_from_file(datafilename, "plots/SIGNAL_TPM_TauCand_massPi0_"+ptbin+"_ZWIN")
        dataHist = ROOT.RooDataHist(newName,newName,ROOT.RooArgList(m2p),dataTH1)

        # get the background template
        templateTH1 = common.get_TH1_from_file(datafilename, "plots/ANTI_TPM_TauCand_massPi0_"+ptbin+"_ZWIN")
        if templateTH1.GetBinContent(1)==0: templateTH1.SetBinContent(1,1.0)
        if templateTH1.GetBinContent(2)==0: templateTH1.SetBinContent(2,1.0)
        if templateTH1.GetBinContent(13)==0: templateTH1.SetBinContent(13,1.0)
        if templateTH1.GetBinContent(14)==0: templateTH1.SetBinContent(14,1.0)
        newName = "temp_"+ptbin
        templateDataHist = ROOT.RooDataHist(newName+"_dh",newName+"_dh",ROOT.RooArgList(m2p),templateTH1)
        a1=ROOT.RooRealVar(newName+"_a1",newName+"_a1",0,-0.6,0.6)
        a2=ROOT.RooRealVar(newName+"_a2",newName+"_a2",0,-0.6,0.6)
        a3=ROOT.RooRealVar(newName+"_a3",newName+"_a3",0,-0.6,0.6)
        a4=ROOT.RooRealVar(newName+"_a4",newName+"_a4",0,-0.6,0.6)
        bkgpdf=ROOT.RooHistSplinePdf(newName+"_pdf",newName+"_pdf",ROOT.RooArgList(m2p),templateDataHist,2,ROOT.RooArgList(a1,a2,a3,a4),False)

        datanorm = dataTH1.Integral(dataTH1.GetXaxis().FindBin(minm2p),dataTH1.GetXaxis().FindBin(maxm2p))
        bkgpdfnorm = ROOT.RooRealVar(newName+"_pdf_norm", "Number of background events", datanorm, 0, 3*datanorm)

        shiftPar = ROOT.RooRealVar("shiftPar","scale Parameter",-0.2,0.2)
        stretchPar = ROOT.RooRealVar("stretchPar","resolution Parameter",0.9,1.3)
        fixedPar = ROOT.RooRealVar("fixedPar","Fixed point",1.4)

        # get the signal histogram and "trim" the edges (as per Steffie's suggestion)
        signalTH1=common.get_TH1_from_file(signalfilename,"plots/SIGNAL_TPM_TauCand_massPi0_"+ptbin+"_ZWIN")
        signalTH1.SetBinContent(1,0.0)
        signalTH1.SetBinContent(2,0.0)
        signalTH1.SetBinContent(13,0.0)
        signalTH1.SetBinContent(14,0.0)


        signalTH1.Scale(getSigScale(args.year))
        newName = "signal_"+ptbin
        signalIntegral=signalTH1.Integral()
        signalDataHist = ROOT.RooDataHist(newName+"_dh",newName+"_dh",ROOT.RooArgList(m2p),signalTH1)
        signalpdf = ROOT.RooHistShiftStretchPdf(newName+"_pdf","signal_pdf",ROOT.RooArgList(m2p),signalDataHist, 2, shiftPar, stretchPar, fixedPar)
        signalpdfnorm = ROOT.RooRealVar(newName+"_pdf_norm", "normalization",signalIntegral)

        getattr(w,"import")(dataHist)
        getattr(w,"import")(signalpdf)
        getattr(w,"import")(signalpdfnorm)
        getattr(w,"import")(bkgpdf)
        getattr(w,"import")(bkgpdfnorm)
    
    fileout.cd()
    w.Print()
    w.Write()
    fileout.Close()

### end main

