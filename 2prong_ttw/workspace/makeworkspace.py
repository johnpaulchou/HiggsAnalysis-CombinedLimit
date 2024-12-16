#!/bin/env python3

import ROOT

# function to get a TH1 from a root file
def getTH1(histname,filename):
    rootfile = ROOT.TFile(filename, "READ")
    if not rootfile or rootfile.IsZombie():
        print("Error: Unable to open file '{file_name}'.")
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

# binning labels
ptbins = ["20_40", "40_60", "60_80", "80_100", "100_140", "140_180", "180_220", "220_300", "300_380", "380on" ]
btagbins = ["1b", "mb"]

# create the observable
m2p = ROOT.RooRealVar("m2p","Invariant mass of the 2-prong",0.25,5.53)

# need to specify whether we are using the asymnoniso SB or the symiso SR
wbin = "asymnoniso"
#wbins = ["symiso", "asymnoniso"]

# need to specify the order of the pdf we're sending to the workspace
order=0

# need to specify which signal we're considering
sigtype = "eta"
sigmass = "M500"
xs = 504.
#sigmass = "M2000"
#xs = 534.
#sigmass = "M4000"
#xs = 529.

#systematic uncertainties
systs = ["", "_MuonRecoUp", "_MuonRecoDown", "_MuonIdUp", "_MuonIdDown", "_MuonIsoUp", "_MuonIsoDown", "_MuonHltUp", "_MuonHltDown",
         "_BtagLightCorrelatedUp", "_BtagLightCorrelatedDown", "_BtagBCCorrelatedUp", "_BtagBCCorrelatedDown", "_BtagLightUncorrelatedUp", "_BtagLightUncorrelatedDown",
         "_BtagBCUncorrelatedUp", "_BtagBCUncorrelatedDown"]

# where to read things from
filename="../input/hists_for_jp_16-12-24.root"
#filename="../input/hists_for_jp_15-10-24.root"
#filename="../input/hists_for_jp.root"

###############################################################
# start of the "main" function
###############################################################

if __name__ == "__main__":

    # setup the output file and workspace
    fileout = ROOT.TFile(fileoutname,"RECREATE")
    w = ROOT.RooWorkspace("w","w")

    # loop over the bins
    for ptbin in ptbins:
        for btagbin in btagbins:

            # get the data
            dataName = "singlemuon_"+wbin+"_"+btagbin+"_"+ptbin+"_tight"
            if wbin=="asymnoniso":
                dataName += "scaledtosymiso"
            newName = "data_"+btagbin+"_"+ptbin
            dataTH1 = getTH1(dataName, filename)
            dataHist = ROOT.RooDataHist(newName,newName,ROOT.RooArgList(m2p),dataTH1)
            getattr(w,"import")(dataHist)
            fileout.cd()
            dataHist.Write()

            # get the template TH1
            templateTH1 = getTH1("singlemuon_"+wbin+"_0b_"+ptbin+"_loose", filename)

            # find any non-0 bins in the data that are 0 in the template
            # set it to 0.01 if it happens and print a warning
            for i in range(1, dataTH1.GetNbinsX()+1):
                if templateTH1.GetBinContent(i)==0 and dataTH1.GetBinContent(i)!=0:
                    print("************************************************************************************")
                    print("found a 0 bin in the template",templateTH1.GetName(),dataTH1.GetName(),str(i),str(dataTH1.GetBinContent(i)),sep=" ; ")
                    print("************************************************************************************")
                    templateTH1.SetBinContent(i, 0.01)

            # construct the PDF of the template
            newName = "temp_"+btagbin+"_"+ptbin
            templateDataHist = ROOT.RooDataHist(newName+"_dh",newName+"_dh",ROOT.RooArgList(m2p),templateTH1)
            templatePdf=ROOT.RooHistPdf(newName+"_pdf0",newName+"_pdf0",ROOT.RooArgSet(m2p),templateDataHist,2)
            a1=ROOT.RooRealVar(newName+"_a1",newName+"_a1",0.1,0,100)
            a2=ROOT.RooRealVar(newName+"_a2",newName+"_a2",0.1,0,100)
            bern1=ROOT.RooBernstein(newName+"_bern1",newName+"_bern1",m2p,ROOT.RooArgList(a1,a2))
            bkg1pdf=ROOT.RooProdPdf(newName+"_pdf1",newName+"_pdf1",ROOT.RooArgSet(templatePdf,bern1))
            b1=ROOT.RooRealVar(newName+"_b1",newName+"_b1",0.1,0,100)
            b2=ROOT.RooRealVar(newName+"_b2",newName+"_b2",0.1,0,100)
            b3=ROOT.RooRealVar(newName+"_b3",newName+"_b3",0.1,0,100)
            bern2=ROOT.RooBernstein(newName+"_bern2",newName+"_bern2",m2p,ROOT.RooArgList(b1,b2,b3))
            bkg2pdf=ROOT.RooProdPdf(newName+"_pdf2",newName+"_pdf2",ROOT.RooArgSet(templatePdf,bern2))
            c1=ROOT.RooRealVar(newName+"_c1",newName+"_c1",0.1,0,100)
            c2=ROOT.RooRealVar(newName+"_c2",newName+"_c2",0.1,0,100)
            c3=ROOT.RooRealVar(newName+"_c3",newName+"_c3",0.1,0,100)
            c4=ROOT.RooRealVar(newName+"_c4",newName+"_c4",0.1,0,100)
            bern3=ROOT.RooBernstein(newName+"_bern3",newName+"_bern3",m2p,ROOT.RooArgList(c1,c2,c3,c4))
            bkg3pdf=ROOT.RooProdPdf(newName+"_pdf3",newName+"_pdf3",ROOT.RooArgSet(templatePdf,bern3))

            # compute the normalizations
            datanorm = dataTH1.Integral(1,dataTH1.GetNbinsX())
            normtemp = ROOT.RooRealVar(newName+"_pdf0_norm", "Number of background events", datanorm, 0, 3*datanorm)
            normf1 = ROOT.RooRealVar(newName+"_pdf1_norm", "Number of background events", datanorm, 0, 3*datanorm)
            normf2 = ROOT.RooRealVar(newName+"_pdf2_norm", "Number of background events", datanorm, 0, 3*datanorm)
            normf3 = ROOT.RooRealVar(newName+"_pdf3_norm", "Number of background events", datanorm, 0, 3*datanorm)
                
            if order==0:
                getattr(w,"import")(templatePdf)
                getattr(w,"import")(normtemp)
            elif order==1:
                getattr(w,"import")(bkg1pdf)
                getattr(w,"import")(normf1)
            elif order==2:
                getattr(w,"import")(bkg2pdf)
                getattr(w,"import")(normf2)
            elif order==3:
                getattr(w,"import")(bkg3pdf)
                getattr(w,"import")(normf3)
                

            # do a preliminary fit and save them for inspection later
            fileout.cd()
            r1=bkg1pdf.fitTo(dataHist, Save=True, Minimizer=("Minuit2","minimize"), SumW2Error=True, Strategy=2, PrintLevel=-1)
            r2=bkg2pdf.fitTo(dataHist, Save=True, Minimizer=("Minuit2","minimize"), SumW2Error=True, Strategy=2, PrintLevel=-1)
            r3=bkg3pdf.fitTo(dataHist, Save=True, Minimizer=("Minuit2","minimize"), SumW2Error=True, Strategy=2, PrintLevel=-1)
            r1.Write()
            r2.Write()
            r3.Write()
            templateDataHist.Write()
            templatePdf.Write()
            bkg1pdf.Write()
            bkg2pdf.Write()
            bkg3pdf.Write()
            
            
            # get the signal
            for syst in systs:
                sigName = sigtype+"_"+str(sigmass)+"_symiso_"+btagbin+"_"+ptbin+"_tight"+syst
                sigTH1 = getTH1(sigName, filename)
                normTH1 = getTH1(sigtype+"_"+str(sigmass)+"_totalentries", filename)
                newName = sigtype+"_"+btagbin+"_"+ptbin
                sigDataHist = ROOT.RooDataHist(newName+"_hist"+syst,newName+"hist"+syst,ROOT.RooArgSet(m2p),sigTH1)
                sigPdf = ROOT.RooHistPdf(newName+"_pdf"+syst,newName+"_pdf"+syst,ROOT.RooArgSet(m2p),sigDataHist,2)
                norm = sigTH1.Integral(1,sigTH1.GetNbinsX())/normTH1.GetBinContent(1)*xs
                normVar = ROOT.RooRealVar(newName+"_pdf"+syst+"_norm","Norm of signal",norm)
                print(sigName+" norm = "+str(normVar))
                fileout.cd()
                getattr(w,"import")(sigPdf)
                getattr(w,"import")(normVar)
#                sigTH1.SetName(newName)
#                sigTH1.Scale(xs/normTH1.GetBinContent(1))
#                fileout.cd()
#                sigTH1.Write()
            
    fileout.cd()
    w.Print()
    w.Write()
    fileout.Close()
    
### end main
