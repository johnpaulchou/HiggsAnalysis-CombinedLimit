import ROOT
import sys

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

# list of systematics
systs = [ "" ]

# determine the w and p masses from the arguments
wmass=float(sys.argv[1])
pmass=float(sys.argv[2])
tlabel=str(pmass)+"_"+str(wmass)


###### main function ######
if __name__ == "__main__":

    # loop over systematic sources
    for syst in systs:

        morphhist=getTH1("sigshapes_"+tlabel+".root", )
    
            # create PDFs for different m2p slices
            fileout.cd()
            for bin in range(1,morphhist.GetXaxis().GetNbins()+1):
                label = "bin"+str(bin)
                if histindex==0: label = label+"B"
                else: label = label+"E"
                projy=morphhist.ProjectionY("_py"+label,bin,bin)
                accnum = projy.Integral(1,projy.GetXaxis().GetNbins())
                accden = morphhist.Integral(1,morphhist.GetXaxis().GetNbins(),1,morphhist.GetYaxis().GetNbins())
                dh=ROOT.RooDataHist("dh"+label,"dh"+label,m2pg,projy)
                sigpdf1d = ROOT.RooHistPdf("sigpdf_"+label,"signal PDF for a slice in m2p",m2pg,dh)
                sliceacc = ROOT.RooRealVar("sliceacc_"+label,"acceptance in a given slice",accnum/accden)
                sliceacc.setConstant(True)
                print("The slice acceptance for "+label+" is "+str(sliceacc.getValV()))
                norm = ROOT.RooProduct("signal_"+label+"_norm", "Normalisation of signal", ROOT.RooArgList(xsec,acceff,sliceacc))
                getattr(w,"import")(sigpdf1d)
                getattr(w,"import")(norm)

            morphhist.Write()
            hA.Write(hA.GetName()+"A")
            hB.Write(hB.GetName()+"B")
            hC.Write(hC.GetName()+"C")
            hD.Write(hD.GetName()+"D")

    w.Print()
    w.Write()
    fileout.Close()
###### main function ######
