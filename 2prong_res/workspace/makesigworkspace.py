import ROOT
import sys
from scipy.interpolate import interp1d

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

# function to get acceptance from a file
def getAcc(filename, histnames, normhistname):
    integral=0.0
    for histname in histnames:
        h=getTH1(filename, histname)
        integral += h.Integral(1,h.GetXaxis().GetNbins(),1,h.GetYaxis().GetNbins())

    hn=getTH1(filename, normhistname)
    norm=hn.GetBinContent(1)
    return integral/norm

###### main function ######
def main(wmass, pmass):

    # list of systematics
    systs = [ "" ]

    # set up the grid of generated points
    gridx = ( (1.0, "1p0"), (2.0, "2p0") )
    gridy = ( (1000., "1000"), (2500., "2500") )

    # find the grid points to match up to the chosen omega and phi masses
    txmin=txmax=tymin=tymax=-999.
    for i in range(len(gridx)-1):
        for j in range(len(gridy)-1):
            if gridx[i][0]<=wmass and gridx[i+1][0]>=wmass and gridy[j][0]<=pmass and gridy[j+1][0]>=pmass:
                txmin=gridx[i][0]
                txmax=gridx[i+1][0]
                tymin=gridy[j][0]
                tymax=gridy[j+1][0]
                fnA="../input/signal_2x2box_"+gridy[j][1]+"_"+gridx[i][1]+"_200k_events.root"
                fnB="../input/signal_2x2box_"+gridy[j][1]+"_"+gridx[i+1][1]+"_200k_events.root"
                fnC="../input/signal_2x2box_"+gridy[j+1][1]+"_"+gridx[i][1]+"_200k_events.root"
                fnD="../input/signal_2x2box_"+gridy[j+1][1]+"_"+gridx[i+1][1]+"_200k_events.root"

    if txmin<0 or txmax<0 or tymin<0 or tymax<0:
        print("Outside the theory bounds")
        exit(1)
    print("txmin="+str(txmin)+"; txmax="+str(txmax)+"; tymin="+str(tymin)+"; tymax="+str(tymax))

    # set the signal interpolation parameters here
    tx=ROOT.RooRealVar("tx","tx",txmin,txmax)
    ty=ROOT.RooRealVar("ty","ty",tymin,tymax)
    tx.setVal(wmass)
    ty.setVal(pmass)

    # list of barrel and endcap histnames
    histnames=('plots/recomass_barrel','plots/recomass_endcap')

    # interpolate the cross section
    theory_xs = [(450., 585.983), (500., 353.898), (625., 117.508), (750., 45.9397), (875., 20.1308),
                 (1000., 9.59447), (1125., 4.88278), (1250., 2.61745), (1375., 1.46371),
                 (1500., 0.847454), (1625., 0.505322), (1750., 0.309008), (1875., 0.192939),
                 (2000., 0.122826), (2125., 0.0795248), (2250., 0.0522742), (2375., 0.0348093),
                 (2500., 0.0235639), (2625., 0.0161926), (2750., 0.0109283), (2875., 0.00759881)]
    x=list(zip(*theory_xs))
    interp=interp1d(x[0], x[1])
    xsec=ROOT.RooRealVar("xsec","Interpolated theory x-section",interp(pmass))
    xsec.setConstant(True)
    print("The interpolated cross section is "+str(xsec.getValV())+" fb.")

    # interpolate the acceptance*efficiency
    accA=getAcc(fnA, histnames, "plots/cutflow")
    accB=getAcc(fnB, histnames, "plots/cutflow")
    accC=getAcc(fnC, histnames, "plots/cutflow")
    accD=getAcc(fnD, histnames, "plots/cutflow")
    z5=(accC-accA)/(tymax-tymin)*pmass+(accA*tymax-accC*tymin)/(tymax-tymin)
    z6=(accD-accB)/(tymax-tymin)*pmass+(accB*tymax-accD*tymin)/(tymax-tymin)
    acc=(z6-z5)/(txmax-txmin)*wmass+(z5*txmax-z6*txmin)/(txmax-txmin)
    acceff=ROOT.RooRealVar("acceff","interpolated acceptance*efficiency",acc)
    acceff.setConstant(True)
    print("The interpolated acc*eff is "+str(acceff.getValV()))
    
    # create label for output workspace
    tlabel=str(pmass)+"_"+str(wmass)
    fileout = ROOT.TFile("sigworkspace_"+tlabel+".root", "RECREATE")
    w = ROOT.RooWorkspace("w","w")

    # loop over systematic sources
    for syst in systs:

        # loop over barrel/endcap histograms
        for histindex,histname in enumerate(histnames):

            # get the 2D histograms
            hA=getTH1(fnA, histname+syst)
            hB=getTH1(fnB, histname+syst)
            hC=getTH1(fnC, histname+syst)
            hD=getTH1(fnD, histname+syst)

            # create the observables (do this based on the data's histogram boundaries)
            m2p = ROOT.RooRealVar("m2p","Invariant mass of the 2-prong",hA.GetXaxis().GetBinLowEdge(1),hA.GetXaxis().GetBinUpEdge(hA.GetXaxis().GetNbins()))
            m2pg = ROOT.RooRealVar("m2pg","Invariant mass of the 2-prong and photon",hA.GetYaxis().GetBinLowEdge(1),hA.GetYaxis().GetBinUpEdge(hA.GetYaxis().GetNbins()))

            # create RooDataHists
            dhA=ROOT.RooDataHist(hA.GetName()+"A_dh","2D signal RooDataHist",ROOT.RooArgList(m2p,m2pg),hA)
            dhB=ROOT.RooDataHist(hB.GetName()+"B_dh","2D signal RooDataHist",ROOT.RooArgList(m2p,m2pg),hB)
            dhC=ROOT.RooDataHist(hC.GetName()+"C_dh","2D signal RooDataHist",ROOT.RooArgList(m2p,m2pg),hC)
            dhD=ROOT.RooDataHist(hD.GetName()+"D_dh","2D signal RooDataHist",ROOT.RooArgList(m2p,m2pg),hD)

            # create RooAbsPdfs out of datahists
            pdfA=ROOT.RooHistPdf(hA.GetName()+"A_pdf","2D signal pdf",ROOT.RooArgSet(m2p,m2pg), dhA)
            pdfB=ROOT.RooHistPdf(hB.GetName()+"B_pdf","2D signal pdf",ROOT.RooArgSet(m2p,m2pg), dhB)
            pdfC=ROOT.RooHistPdf(hC.GetName()+"C_pdf","2D signal pdf",ROOT.RooArgSet(m2p,m2pg), dhC)
            pdfD=ROOT.RooHistPdf(hD.GetName()+"D_pdf","2D signal pdf",ROOT.RooArgSet(m2p,m2pg), dhD)

            # create a grid with each pdf at a corner
            bintx=ROOT.RooBinning(1,txmin,txmax)
            binty=ROOT.RooBinning(1,tymin,tymax)
            grid=ROOT.RooMomentMorphFuncNDFix.Grid2(bintx,binty);
            grid.addPdf(pdfA,0,0)
            grid.addPdf(pdfB,1,0)
            grid.addPdf(pdfC,0,1)
            grid.addPdf(pdfD,1,1)

            # morph and create a new 2D histogram in its place
            morph=ROOT.RooMomentMorphFuncNDFix("morph","morph",ROOT.RooArgList(tx,ty),ROOT.RooArgList(m2p,m2pg),grid,ROOT.RooMomentMorphFuncNDFix.Linear);
            morph.setPdfMode()
            tx.setVal(wmass)
            ty.setVal(pmass)
            morphhist=hA.Clone(hA.GetName()+"m")
            morphhist.Reset()
            morphhist=morph.fillHistogram(morphhist,ROOT.RooArgList(m2p,m2pg))
        
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

            # write the rest to the file
            fileout.cd()
            morphhist.Write()
            hA.Write(hA.GetName()+"A")
            hB.Write(hB.GetName()+"B")
            hC.Write(hC.GetName()+"C")
            hD.Write(hD.GetName()+"D")

    w.Print()
    w.Write()
    fileout.Close()
###### main function ######

if __name__ == "__main__":
    if len(sys.argv)<3:
        print("makesigworkspace.py wmass pmass")
        exit(1)
    
    main(float(sys.argv[1]), float(sys.argv[2]))
