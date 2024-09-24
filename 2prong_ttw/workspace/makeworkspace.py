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
        rootfile.Close()
        return None
    hist.SetDirectory(0)
    rootfile.Close()
    return hist


# where to write things out
fileoutname = "../output/ws.root"

# binning labels
ptbins = ["20_40", "40_60", "60_80", "80_100", "100_140", "140_180", "180_220", "220_300", "300_380", "380on" ]
btagbins = ["1b", "mb"]
wbins = ["symiso", "asymnoniso"]

# where to read things from
filename="../input/hists_for_JP.root"

# create the observable
m2p = ROOT.RooRealVar("m2p","Invariant mass of the 2-prong",0.25,5.65)


###############################################################
# start of the "main" function
###############################################################

if __name__ == "__main__":

    # setup the output file and workspace
    fileout = ROOT.TFile(fileoutname,"RECREATE")
    w = ROOT.RooWorkspace("w","w")

    # loop over the bins
    for ptbin in ptbins:
        for wbin in wbins:
            for btagbin in btagbins:

                # get the template and construct a PDF
                templateName = "singlemuon_"+wbin+"_0b_"+ptbin+"_loosefittemplate"
                newName = "temp_"+wbin+"_"+btagbin+"_"+ptbin
                templateTH1 = getTH1(templateName, filename)
                templateDataHist = ROOT.RooDataHist(newName,newName,ROOT.RooArgList(m2p),templateTH1)
                templatePdf=ROOT.RooHistPdf(newName+"_pdf",newName+"_pdf",ROOT.RooArgSet(m2p),templateDataHist,2)
                a1=ROOT.RooRealVar(newName+"_a1",newName+"_a1",0.1,0,100)
                a2=ROOT.RooRealVar(newName+"_a2",newName+"_a2",0.1,0,100)
                bern1=ROOT.RooBernstein(newName+"_bern1",newName+"_bern1",m2p,ROOT.RooArgList(a1,a2))
                bkg1pdf=ROOT.RooProdPdf(newName+"_bkg1pdf",newName+"_bkg1pdf",ROOT.RooArgSet(templatePdf,bern1))
                b1=ROOT.RooRealVar(newName+"_b1",newName+"_b1",0.1,0,100)
                b2=ROOT.RooRealVar(newName+"_b2",newName+"_b2",0.1,0,100)
                b3=ROOT.RooRealVar(newName+"_b3",newName+"_b3",0.1,0,100)
                bern2=ROOT.RooBernstein(newName+"_bern2",newName+"_bern2",m2p,ROOT.RooArgList(b1,b2,b3))
                bkg2pdf=ROOT.RooProdPdf(newName+"_bkg2pdf",newName+"_bkg2pdf",ROOT.RooArgSet(templatePdf,bern2))
                c1=ROOT.RooRealVar(newName+"_c1",newName+"_c1",0.1,0,100)
                c2=ROOT.RooRealVar(newName+"_c2",newName+"_c2",0.1,0,100)
                c3=ROOT.RooRealVar(newName+"_c3",newName+"_c3",0.1,0,100)
                c4=ROOT.RooRealVar(newName+"_c4",newName+"_c4",0.1,0,100)
                bern3=ROOT.RooBernstein(newName+"_bern3",newName+"_bern3",m2p,ROOT.RooArgList(c1,c2,c3,c4))
                bkg3pdf=ROOT.RooProdPdf(newName+"_bkg3pdf",newName+"_bkg3pdf",ROOT.RooArgSet(templatePdf,bern3))
                
                # get the data
                dataName = "singlemuon_"+wbin+"_"+btagbin+"_"+ptbin+"_tight"
                if wbin=="asymnoniso":
                    dataName += "scaledtosymiso"
                newName = "data_"+wbin+"_"+btagbin+"_"+ptbin
                dataTH1 = getTH1(dataName, filename)
                dataHist = ROOT.RooDataHist(newName,newName,ROOT.RooArgList(m2p),dataTH1)
                getattr(w,"import")(dataHist)
                fileout.cd()
                dataHist.Write()
            
                # do a preliminary fit and save them for inspection later
                # r0=templatePdf.fitTo(dataHist, Save=True, Minimizer=("Minuit2","minimize"), SumW2Error=True, Strategy=2, PrintLevel=-1)
                r1=bkg1pdf.fitTo(dataHist, Save=True, Minimizer=("Minuit2","minimize"), SumW2Error=True, Strategy=2, PrintLevel=1)
                r2=bkg2pdf.fitTo(dataHist, Save=True, Minimizer=("Minuit2","minimize"), SumW2Error=True, Strategy=2, PrintLevel=1)
                r3=bkg3pdf.fitTo(dataHist, Save=True, Minimizer=("Minuit2","minimize"), SumW2Error=True, Strategy=2, PrintLevel=1)
                r1.Write()
                r2.Write()
                r3.Write()
                templatePdf.Write()
                bkg1pdf.Write()
                bkg2pdf.Write()
                bkg3pdf.Write()
            
            
                # get the signal

    fileout.cd()
    w.Print()
    w.Write()
    fileout.Close()
    
### end main
