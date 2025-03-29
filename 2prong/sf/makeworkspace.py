#!/bin/env python3

import ROOT
import argparse
import common.common as common

# where to write things out
fileoutname = "workspace.root"
workspacename = "w"

# create the observable and set the range
xlo=0.
xhi=4.
x = ROOT.RooRealVar("x","x-axis parameter",xlo,xhi)

# QCD and non-QCD background uncertainties
QCDError=0.1
nonQCDError=0.1

# where to read things from
filename="./input/histos.root"

###############################################################
# start of the "main" function
###############################################################

if __name__ == "__main__":

    # list of non-QCD backgrounds
    nonQCDbackgrounds = ["dybkg_TwoProng_massPi0","wjets_TwoProng_massPi0","ttjets_TwoProng_massPi0"]

    # list of signals
    signals = ["dy_TwoProng_massPi0_scale_0p8","dy_TwoProng_massPi0_scale_0p9","dy_TwoProng_massPi0","dy_TwoProng_massPi0_scale_1p1","dy_TwoProng_massPi0_scale_1p2"]
    minscalepar=0.8
    maxscalepar=1.2
    
    # setup the output file and workspace
    fileout = ROOT.TFile(fileoutname,"RECREATE")
    w = ROOT.RooWorkspace(workspacename,workspacename)

    # create a RooDataHist from the data histogram
    dataTH1 = common.get_TH1_from_file(filename, "data_TwoProng_massPi0")
    dataHist = ROOT.RooDataHist("data","data",ROOT.RooArgList(x),dataTH1)
    getattr(w,"import")(dataHist)

    # create a TH1 that contains all of the non-QCD backgrounds
    for bkgIndex,bkg in enumerate(nonQCDbackgrounds):
        if bkgIndex==0:
            nonQCDTH1 = common.get_TH1_from_file(filename, nonQCDbackgrounds[bkgIndex]).Clone("nonQCD")
        else:
            nonQCDTH1.Add(common.get_TH1_from_file(filename, bkg))

    # create the RooDataHist, RooHistPdf, normalization, and constraint of the non-QCD backgrounds
    nonQCDIntegral=nonQCDTH1.Integral(nonQCDTH1.FindBin(xlo),nonQCDTH1.FindBin(xhi))
    nonQCDDataHist = ROOT.RooDataHist("nonQCD_dh","nonQCD_dh",ROOT.RooArgList(x),nonQCDTH1)
    nonQCDPdf = ROOT.RooHistPdf("nonQCD_pdf","nonQCD_pdf",ROOT.RooArgList(x),nonQCDDataHist,2)
    nonQCDPdfNorm = ROOT.RooRealVar("nonQCD_pdf_norm", "normalization",nonQCDIntegral,0,nonQCDIntegral*3)
    nonQCDConstraint = ROOT.RooGaussian("nonQCDConstraint","nonQCDConstraint",nonQCDPdfNorm,nonQCDIntegral,nonQCDIntegral*nonQCDError)
    
    # create the TH1 for the QCD backgrounds
    QCDTH1 = common.get_TH1_from_file(filename, "data_TwoProng_massPi0")
    for bin in range(1,QCDTH1.GetNbinsX()+1):
        if QCDTH1.GetBinContent(bin)<0:
            QCDTH1.SetBinContent(bin,0.0)

    # create the RooDataHist, RooHistPdf, normalization, and constraint of the QCD background
    QCDIntegral=QCDTH1.Integral(QCDTH1.FindBin(xlo),QCDTH1.FindBin(xhi))
    QCDDataHist = ROOT.RooDataHist("QCD_dh","QCD_dh",ROOT.RooArgList(x),QCDTH1)
    QCDPdf = ROOT.RooHistPdf("QCD_pdf","QCD_pdf",ROOT.RooArgList(x),QCDDataHist,2)
    QCDPdfNorm = ROOT.RooRealVar("QCD_pdf_norm", "normalization",QCDIntegral,0,QCDIntegral*3)
    QCDConstraint = ROOT.RooGaussian("QCDConstraint","QCDConstraint",QCDPdfNorm,QCDIntegral,QCDIntegral*QCDError)

    # create a TH2 for the signal
    tempSignalTH1 = common.get_TH1_from_file(filename,signals[0])
    signalTH2 = ROOT.TH2D("signalTH2","signal TH2",tempSignalTH1.GetNbinsX(),tempSignalTH1.GetXaxis().GetXmin(),tempSignalTH1.GetXaxis().GetXmax(),len(signals),minscalepar,maxscalepar)
    for ybin in range(1,signalTH2.GetNbinsY()+1):
        tempSignalTH1=common.get_TH1_from_file(filename,signals[ybin-1])
        for xbin in range(1,signalTH2.GetNbinsX()+1):
            signalTH2.SetBinContent(xbin,ybin,tempSignalTH1.GetBinContent(xbin))

    # create the RooHistMorphPdf and normalization of the signal
    scalePar = ROOT.RooRealVar("scalePar","scale Parameter",minscalepar,maxscalepar)
    tempSignalTH1 = common.get_TH1_from_file(filename,signals[2]) # base the normalization histogram off of the middle point
    signalIntegral=tempSignalTH1.Integral(tempSignalTH1.FindBin(xlo),tempSignalTH1.FindBin(xhi))
    signalPdf = ROOT.RooHistMorphPdf("signal_pdf","signal_pdf",x,scalePar,signalTH2)
    signalPdfNorm = ROOT.RooRealVar("signal_pdf_norm", "normalization",signalIntegral,0,signalIntegral*3)

    # create the model by first extending the PDFs and then including the constraints
    extNonQCD=ROOT.RooExtendPdf("extNonQCD","extended non-QCD background",nonQCDPdf,nonQCDPdfNorm)
    extQCD=ROOT.RooExtendPdf("extQCD","extended QCD background",QCDPdf,QCDPdfNorm)
    extSignal=ROOT.RooExtendPdf("extSignal","extended signal",signalPdf,signalPdfNorm)
    
    model = ROOT.RooAddPdf("model","model",ROOT.RooArgList(extSignal,extQCD,extNonQCD))
    modelc= ROOT.RooProdPdf("modelc","constrained model",ROOT.RooArgList(model,QCDConstraint,nonQCDConstraint))
    getattr(w,"import")(modelc)


    r=model.fitTo(dataHist,Save=True, Minimizer=("Minuit2","minimize"),PrintLevel=2)
    print("non-QCD normalization="+str(nonQCDIntegral))
    print("QCD normalization="+str(QCDIntegral))
    print("signal normalization="+str(signalIntegral))

    
    fileout.cd()
    w.Write()
    fileout.Close()
        
