#!/bin/env python3

import ROOT
import argparse
import common.common as common
import sys

# where to write things out
fileoutname = "workspace.root"
workspacename = "w"

# create the observable and set the range
xlo=0.
xhi=3.0
x = ROOT.RooRealVar("x","x-axis parameter",xlo,xhi)

# QCD and non-QCD background uncertainties
QCDError=0.15
nonQCDError=0.20


# where to read things from
year = "2017"
filename = "./input/savefile_"+year+".root"

# list of non-QCD backgrounds
nonQCDbackgrounds = ["DYbkg_SIGNAL_TPM_TauCand_massPi0","WJETS_SIGNAL_TPM_TauCand_massPi0","TTJETS_SIGNAL_TPM_TauCand_massPi0"]

# list of signals
signals = ["DYsig_SIGNAL_TPM_TauCand_massPi0_0p8","DYsig_SIGNAL_TPM_TauCand_massPi0_0p9","DYsig_SIGNAL_TPM_TauCand_massPi0","DYsig_SIGNAL_TPM_TauCand_massPi0_1p1","DYsig_SIGNAL_TPM_TauCand_massPi0_1p2"]

minscalepar=0.8
maxscalepar=1.2
    

###############################################################
# start of the "main" function
###############################################################

if __name__ == "__main__":

    # setup the output file and workspace
    fileout = ROOT.TFile(fileoutname,"RECREATE")
    w = ROOT.RooWorkspace(workspacename,workspacename)

    rebinVal=2
    
    # create a RooDataHist from the data histogram
    dataTH1 = common.get_TH1_from_file(filename, "DATA_SIGNAL_TPM_TauCand_massPi0")
    dataTH1.Rebin(rebinVal)
    dataHist = ROOT.RooDataHist("data","data",ROOT.RooArgList(x),dataTH1)
    getattr(w,"import")(dataHist)

    # create a TH1 that contains all of the non-QCD backgrounds
    for bkgIndex,bkg in enumerate(nonQCDbackgrounds):
        if bkgIndex==0:
            nonQCDTH1 = common.get_TH1_from_file(filename, nonQCDbackgrounds[bkgIndex]).Clone("nonQCD")
        else:
            nonQCDTH1.Add(common.get_TH1_from_file(filename, bkg))
    nonQCDTH1.Rebin(rebinVal)

    # create the RooDataHist, RooHistPdf, normalization, and constraint of the non-QCD backgrounds
    nonQCDIntegral=nonQCDTH1.Integral(nonQCDTH1.FindBin(xlo),nonQCDTH1.FindBin(xhi))
    nonQCDDataHist = ROOT.RooDataHist("nonQCD_dh","nonQCD_dh",ROOT.RooArgList(x),nonQCDTH1)
    nonQCDPdf = ROOT.RooHistPdf("nonQCD_pdf","nonQCD_pdf",ROOT.RooArgList(x),nonQCDDataHist,2)
    nonQCDPdfNorm = ROOT.RooRealVar("nonQCD_pdf_norm", "normalization",nonQCDIntegral,0,nonQCDIntegral*3)
    nonQCDConstraint = ROOT.RooGaussian("nonQCDConstraint","nonQCDConstraint",nonQCDPdfNorm,nonQCDIntegral,nonQCDIntegral*nonQCDError)
    
    # create the TH1 for the QCD backgrounds
    QCDTH1 = common.get_TH1_from_file(filename, "QCD_SS_TPM_TauCand_massPi0")
    QCDTH1.Rebin(rebinVal)
    for bin in range(1,QCDTH1.GetNbinsX()+1):
        if QCDTH1.GetBinContent(bin)<0:
            QCDTH1.SetBinContent(bin,0.0)

    # create the RooDataHist, RooHistPdf, normalization, and constraint of the QCD background
    QCDIntegral=QCDTH1.Integral(QCDTH1.FindBin(xlo),QCDTH1.FindBin(xhi))
    print("QCDIntegral="+str(QCDIntegral))
    QCDDataHist = ROOT.RooDataHist("QCD_dh","QCD_dh",ROOT.RooArgList(x),QCDTH1)
    a1=ROOT.RooRealVar("a1","a1",0,-0.6,0.6)
    a2=ROOT.RooRealVar("a2","a2",0,-0.6,0.6)
    a3=ROOT.RooRealVar("a3","a3",0,-0.6,0.6)
    a4=ROOT.RooRealVar("a4","a4",0,-0.6,0.6)
    a5=ROOT.RooRealVar("a5","a5",0,-0.6,0.6)
    a6=ROOT.RooRealVar("a6","a6",0,-0.6,0.6)
    QCDPdf = ROOT.RooHistSplinePdf("QCD_pdf","QCD_pdf",ROOT.RooArgList(x),QCDDataHist,2,ROOT.RooArgList(a1,a2,a3,a4,a5,a6),False)
    QCDPdfNorm = ROOT.RooRealVar("QCD_pdf_norm", "normalization",QCDIntegral,0,QCDIntegral*3)
    QCDConstraint = ROOT.RooGaussian("QCDConstraint","QCDConstraint",QCDPdfNorm,QCDIntegral,QCDIntegral*QCDError)
    a1Constraint= ROOT.RooGaussian("a1Constraint","a1Constraint",a1,0.0,QCDError)
    a2Constraint= ROOT.RooGaussian("a2Constraint","a2Constraint",a2,0.0,QCDError)
    a3Constraint= ROOT.RooGaussian("a3Constraint","a3Constraint",a3,0.0,QCDError)
    a4Constraint= ROOT.RooGaussian("a4Constraint","a4Constraint",a4,0.0,QCDError)
    a5Constraint= ROOT.RooGaussian("a5Constraint","a5Constraint",a5,0.0,QCDError)
    a6Constraint= ROOT.RooGaussian("a6Constraint","a6Constraint",a6,0.0,QCDError)

    # create a TH2 for the signal
    tempSignalTH1 = common.get_TH1_from_file(filename,signals[0])
    tempSignalTH1.Rebin(rebinVal)
    signalTH2 = ROOT.TH2D("signalTH2","signal TH2",tempSignalTH1.GetNbinsX(),tempSignalTH1.GetXaxis().GetXmin(),tempSignalTH1.GetXaxis().GetXmax(),len(signals),minscalepar-0.05,maxscalepar+0.05)
    for ybin in range(1,signalTH2.GetNbinsY()+1):
        tempSignalTH1=common.get_TH1_from_file(filename,signals[ybin-1])
        tempSignalTH1.Rebin(rebinVal)
        for xbin in range(1,signalTH2.GetNbinsX()+1):
            signalTH2.SetBinContent(xbin,ybin,tempSignalTH1.GetBinContent(xbin))

    # create the RooHistMorphPdf and normalization of the signal
    scalePar = ROOT.RooRealVar("scalePar","scale Parameter",minscalepar,maxscalepar)
#    scalePar = ROOT.RooRealVar("scalePar","scale Parameter",1.0)
    tempSignalTH1 = common.get_TH1_from_file(filename,signals[2]) # base the normalization histogram off of the middle point
    tempSignalTH1.Rebin(rebinVal)
    signalIntegral=tempSignalTH1.Integral(tempSignalTH1.FindBin(xlo),tempSignalTH1.FindBin(xhi))
    signalPdf = ROOT.RooHistMorphPdf("signal_pdf","signal_pdf",x,scalePar,signalTH2)
    signalPdfNorm = ROOT.RooRealVar("signal_pdf_norm", "normalization",signalIntegral,0,signalIntegral*3)

    # create the model by first extending the PDFs and then including the constraints
    extNonQCD=ROOT.RooExtendPdf("extNonQCD","extended non-QCD background",nonQCDPdf,nonQCDPdfNorm)
    extQCD=ROOT.RooExtendPdf("extQCD","extended QCD background",QCDPdf,QCDPdfNorm)
    extSignal=ROOT.RooExtendPdf("extSignal","extended signal",signalPdf,signalPdfNorm)
    
    model = ROOT.RooAddPdf("model","model",ROOT.RooArgList(extSignal,extQCD,extNonQCD))
    modelc= ROOT.RooProdPdf("modelc","constrained model",ROOT.RooArgList(model,QCDConstraint,nonQCDConstraint,a1Constraint,a2Constraint,a3Constraint,a4Constraint,a5Constraint,a6Constraint))

    # fit and save the result
    r1=modelc.fitTo(dataHist,Save=True, Minimizer=("Minuit2","minimize"),PrintLevel=0,Minos=True)
    getattr(w,"import")(modelc)

    nonQCDSF=nonQCDPdfNorm.getVal()/nonQCDIntegral
    QCDSF=QCDPdfNorm.getVal()/QCDIntegral
    signalSF=signalPdfNorm.getVal()/signalIntegral
    signalErr=signalPdfNorm.getError()/signalIntegral
    print("non-QCD SF="+str(nonQCDSF))
    print("QCD normalization SF="+str(QCDSF))
    print("signal normalization SF="+str(signalSF)+" +/- "+str(signalErr))
    print("signal scale="+str(scalePar.getVal())+" +/- "+str(scalePar.getError()))
    sys.stdout.flush()
    
    fileout.cd()
    w.Write()
    fileout.Close()
        
