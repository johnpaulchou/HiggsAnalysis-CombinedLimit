#!/bin/env python3

import ROOT
import argparse
import common.common as common

# where to write things out
fileoutname = "workspace.root"
workspacename = "w"

# binning labels
ptbins = ["pt20", "pt40", "pt60", "pt80"]

# shift labels
shifts = [ "_0p8", "_0p9", "", "_1p1", "_1p2" ]

# set the observable range
minm2p = 0.5
maxm2p = 3.5

# signal scale (from Brandon)
sigScale=1.8433

# where to read things from
def getDataFilename(year):
    return "./input/data_newptbins_"+str(year)+".root"
def getSignalFilename(year):
    return "./input/dysig_newptbins_"+str(year)+".root"


# create out of a collection of TH1D's a TH2D that contains the shifts along the y-axis
minscalepar=0.8
maxscalepar=1.2
def createTH2(name, TH1s):
    newTH2 = ROOT.TH2D(name, name, TH1s[0].GetNbinsX(),TH1s[0].GetXaxis().GetXmin(),TH1s[0].GetXaxis().GetXmax(),len(shifts),minscalepar-0.05,maxscalepar+0.05)
    for ybin in range(1,newTH2.GetNbinsY()+1):
        for xbin in range(1,newTH2.GetNbinsX()+1):
            newTH2.SetBinContent(xbin,ybin,TH1s[ybin-1].GetBinContent(xbin))
    return newTH2


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
    scalePar = ROOT.RooRealVar("scalePar","scale Parameter",minscalepar,maxscalepar)
    m2p = ROOT.RooRealVar("m2p","Invariant mass of the 2-prong",minm2p,maxm2p)

    # loop over the bins
    for ptbin in ptbins:

        # get the data
        newName = "data_"+ptbin
        dataTH1 = common.get_TH1_from_file(datafilename, "plots/SIGNAL_TPM_TauCand_massPi0_"+ptbin+"_ZWIN")
        dataHist = ROOT.RooDataHist(newName,newName,ROOT.RooArgList(m2p),dataTH1)

        # get the template
        templateTH1 = common.get_TH1_from_file(datafilename, "plots/ANTI_TPM_TauCand_massPi0_"+ptbin+"_ZWIN")
        newName = "temp_"+ptbin
        templateDataHist = ROOT.RooDataHist(newName+"_dh",newName+"_dh",ROOT.RooArgList(m2p),templateTH1)
        a1=ROOT.RooRealVar(newName+"_a1",newName+"_a1",0,-0.6,0.6)
        a2=ROOT.RooRealVar(newName+"_a2",newName+"_a2",0,-0.6,0.6)
        a3=ROOT.RooRealVar(newName+"_a3",newName+"_a3",0,-0.6,0.6)
        a4=ROOT.RooRealVar(newName+"_a4",newName+"_a4",0,-0.6,0.6)
        bkgpdf=ROOT.RooHistSplinePdf(newName+"_pdf",newName+"_pdf",ROOT.RooArgList(m2p),templateDataHist,2,ROOT.RooArgList(a1,a2,a3,a4),False)

        datanorm = dataTH1.Integral(dataTH1.GetXaxis().FindBin(minm2p),dataTH1.GetXaxis().FindBin(maxm2p))
        bkgpdfnorm = ROOT.RooRealVar(newName+"_pdf_norm", "Number of background events", datanorm, 0, 3*datanorm)

        # get the signal
        histos=[]
        for shift in shifts:
            histo=common.get_TH1_from_file(signalfilename,"plots/SIGNAL_TPM_TauCand_massPi0"+shift+"_"+ptbin+"_ZWIN")
            histo.Scale(sigScale)
            histos.append(histo)
        newName = "signal_"+ptbin
        signalTH2=createTH2(newName+"_2D",histos)
        signalIntegral=signalTH2.ProjectionX(newName+"px",int(len(shifts)/2),int(len(shifts)/2)).Integral()
        signalpdf = ROOT.RooHistMorphPdf(newName+"_pdf","signal_pdf",m2p,scalePar,signalTH2)
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

