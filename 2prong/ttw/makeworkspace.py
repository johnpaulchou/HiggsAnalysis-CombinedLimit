#!/bin/env python3

import ROOT
import argparse
import common.common as common

# where to write things out
fileoutname = "workspace.root"
workspacename = "w"

# binning labels
#ptbins = ["20_40", "40_60", "60_80", "80_100", "100_140", "140_180", "180_220", "220_300", "300_380", "380on" ]
ptbins = ["20_40", "40_60", "60_80", "80_100", "100_140", "140_180", "180_300", "300on" ]
btagbins = ["1b", "mb"]

# create the observable
m2p = ROOT.RooRealVar("m2p","Invariant mass of the 2-prong",0.25,5.53)

# need to specify which signal we're considering
sigmasses = ["M500", "M750", "M850", "M1000", "M1500", "M2000", "M2500", "M3000", "M4000" ]

# systematic uncertainties
systs = ["", "_MuonRecoUp", "_MuonRecoDown", "_MuonIdUp", "_MuonIdDown", "_MuonIsoUp", "_MuonIsoDown", "_MuonHltUp", "_MuonHltDown",
         "_BtagLightCorrelatedUp", "_BtagLightCorrelatedDown", "_BtagBCCorrelatedUp", "_BtagBCCorrelatedDown", "_BtagLightUncorrelatedUp", "_BtagLightUncorrelatedDown",
         "_BtagBCUncorrelatedUp", "_BtagBCUncorrelatedDown", "_JECUp", "_JECDown", "_JERUp", "_JERDown", "_MuonRocUp", "_MuonRocDown", "_MuonResoUp", "_MuonResoDown",
         "_PileupUp", "_PileupDown", "_TwoProngMassResoUp", "_TwoProngMassResoDown", "_TwoProngMassScaleUp", "_TwoProngMassScaleDown", "_TwoProngPtResoUp", "_TwoProngPtResoDown",
         "_TwoProngPtScaleUp", "_TwoProngPtScaleDown"]

# regions to evalute
regions = ["symiso","asymnoniso","asymnoniso_unscaled"]

# signal types
sigtypes = ["eta","etaprime"]

# where to read things from
filenames = ["./input/summed_hists_eta_11-08-25_rebin2.root", "./input/summed_hists_etaprime_18-08-25_rebin2.root"]
#filenames =  ["./input/summed_hists_eta_11-08-25.root", "./input/summed_hists_etaprime_18-08-25.root"]
#filenames =  ["./input/summed_hists_TEST_eta_18-08-25.root", "./input/summed_hists_etaprime_18-08-25.root"]
#filenames =  ["./input/summed_hists_COARSEBINS_eta_23-08-25.root", "./input/summed_hists_COARSEBINS_etaprime_23-08-25.root"]


###############################################################
# start of the "main" function
###############################################################

if __name__ == "__main__":

    # setup and use the parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--imass",help="signal mass index (0-"+str(len(sigmasses)-1)+")", choices=range(len(sigmasses)), type=int)
    parser.add_argument("--region",help="region that we're working in",choices=regions, default=regions[1])
    parser.add_argument("--sigtype",help="signal type that we're using",choices=sigtypes,default=sigtypes[0])
    args=parser.parse_args()
    sigmass = sigmasses[args.imass]
    sigtype = args.sigtype
    region = args.region
    
    # setup the output file and workspace
    fileout = ROOT.TFile(fileoutname,"RECREATE")
    w = ROOT.RooWorkspace(workspacename,workspacename)

    if sigtype==sigtypes[0]: filename=filenames[0]
    if sigtype==sigtypes[1]: filename=filenames[1]
    
    # write the parser parameters to the rootfile
    fileout.cd()
    (ROOT.TNamed("sigmass",sigmass)).Write()
    (ROOT.TNamed("sigtype",sigtype)).Write()
    (ROOT.TNamed("region",region)).Write()
    
    # loop over the bins
    for ptbin in ptbins:
        for btagbin in btagbins:

            if sigtype=="eta" and region=="asymnoniso" and (args.imass==5 or args.imass==6 or args.imass==7): rebin=2
            elif sigtype=="eta" and region=="symiso" and (args.imass==4 or args.imass==7): rebin=2
            elif sigtype=="etaprime" and region=="asymnoniso" and (args.imass==6 or args.imass==7): rebin=2
            else: rebin=1
            
            # get the data
            if region==regions[0]:
                dataName = "singlemuon_symiso_"+btagbin+"_"+ptbin+"_tight"
            elif region==regions[1]:
                dataName = "singlemuon_asymnoniso_"+btagbin+"_"+ptbin+"_tightscaledtosymiso"
            elif region==regions[2]:
                dataName = "singlemuon_asymnoniso_"+btagbin+"_"+ptbin+"_tight"

            # create a RooDataHist from the data histogram
            newName = "data_"+btagbin+"_"+ptbin
            dataTH1 = common.get_TH1_from_file(filename, dataName)
            dataTH1.Rebin(rebin)
            dataHist = ROOT.RooDataHist(newName,newName,ROOT.RooArgList(m2p),dataTH1)
            getattr(w,"import")(dataHist)

            # get the template TH1
            if region==regions[0]:
                templateTH1 = common.get_TH1_from_file(filename, "singlemuon_symiso_0b_"+ptbin+"_loose")
            elif region==regions[1] or region==regions[2]:
                templateTH1 = common.get_TH1_from_file(filename, "singlemuon_asymnoniso_0b_"+ptbin+"_loose")
            templateTH1.Rebin(rebin)
                
            # find any non-0 bins in the data that are 0 in the template
            # set it to 1.0 if it happens and print a warning
            for i in range(1, dataTH1.GetNbinsX()+1):
                if templateTH1.GetBinContent(i)==0 and dataTH1.GetBinContent(i)!=0:
                    print("************************************************************************************")
                    print("found a 0 bin in the template",templateTH1.GetName(),dataTH1.GetName(),str(i),str(dataTH1.GetBinContent(i)),sep=" ; ")
                    print("************************************************************************************")
                    templateTH1.SetBinContent(i, 1.0)

            # construct the PDF of the template
            newName = "temp_"+btagbin+"_"+ptbin
            templateDataHist = ROOT.RooDataHist(newName+"_dh",newName+"_dh",ROOT.RooArgList(m2p),templateTH1)
            a1=ROOT.RooRealVar(newName+"_a1",newName+"_a1",0,-0.6,0.6)
            a2=ROOT.RooRealVar(newName+"_a2",newName+"_a2",0,-0.6,0.6)
            a3=ROOT.RooRealVar(newName+"_a3",newName+"_a3",0,-0.6,0.6)
            a4=ROOT.RooRealVar(newName+"_a4",newName+"_a4",0,-0.6,0.6)
            a5=ROOT.RooRealVar(newName+"_a5",newName+"_a5",0,-0.6,0.6)
            a6=ROOT.RooRealVar(newName+"_a6",newName+"_a6",0,-0.6,0.6)
            bkg0pdf=ROOT.RooHistPdf(newName+"_pdf0",newName+"_pdf0",ROOT.RooArgList(m2p),templateDataHist,2)
            bkg1pdf=ROOT.RooHistSplinePdf(newName+"_pdf1",newName+"_pdf1",ROOT.RooArgList(m2p),templateDataHist,2,ROOT.RooArgList(a1,a2,a3,a4,a5,a6))

            # compute the normalizations
            # (note that the naming convention for the normalization parameter is assumed to be "*_norm" by HiggsCombine)
            datanorm = dataTH1.Integral(1,dataTH1.GetNbinsX())
            print(dataTH1.GetName()+" norm = "+str(datanorm))
            normf0 = ROOT.RooRealVar(newName+"_pdf0_norm", "Number of background events", datanorm, 0, 3*datanorm)
            normf1 = ROOT.RooRealVar(newName+"_pdf1_norm", "Number of background events", datanorm, 0, 3*datanorm)

            # do a preliminary fit and save them for inspection later
            r1=bkg1pdf.fitTo(dataHist, Save=True, Minimizer=("Minuit2","minimize"), SumW2Error=True, Strategy=2, PrintLevel=-1)

            getattr(w,"import")(bkg0pdf)
            getattr(w,"import")(normf0)
            getattr(w,"import")(r1)
            getattr(w,"import")(bkg1pdf)
            getattr(w,"import")(normf1)
            
            # get the signal and its normalization (with systematics)
            for syst in systs:
                sigName = sigtype+"_"+str(sigmass)+"_symiso_"+btagbin+"_"+ptbin+"_tight"+syst
                sigTH1 = common.get_TH1_from_file(filename,sigName)
                sigTH1.Rebin(rebin)
                newName = "sig_"+btagbin+"_"+ptbin
                sigDataHist = ROOT.RooDataHist(newName+"_hist"+syst,newName+"hist"+syst,ROOT.RooArgSet(m2p),sigTH1)
                sigPdf = ROOT.RooHistPdf(newName+"_pdf"+syst,newName+"_pdf"+syst,ROOT.RooArgSet(m2p),sigDataHist,2)
                norm = sigTH1.Integral(1,sigTH1.GetNbinsX())
                normVar = ROOT.RooRealVar(newName+"_pdf"+syst+"_norm","Norm of signal",norm)
                getattr(w,"import")(sigPdf)
                getattr(w,"import")(normVar)
            
    fileout.cd()
    w.Print()
    w.Write()
    fileout.Close()
    
### end main
