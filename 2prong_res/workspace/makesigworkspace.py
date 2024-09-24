import ROOT
from scipy.interpolate import interp1d

def get2DHist(newname,filename, histname,x,y):
    rootfile = ROOT.TFile(filename, "READ")
    if not rootfile or rootfile.IsZombie():
        print("Error: Unable to open file '{file_name}'.")
        return None

    sighist = rootfile.Get(histname)
    if not sighist or not isinstance(sighist, ROOT.TH1) or sighist is None:
        print("Error: Histogram '{histname}' not found or is not a valid TH2 object in the file '{filename}'.")
        rootfile.Close()
        return None
    #    sighist.Scale(sighist2d.GetEntries()/sighist2d.Integral(0,sighist2d.GetXaxis().GetNbins()+1,0,sighist2d.GetYaxis().GetNbins()))
    #    sighist.Sumw2(False)
    sighist.SetDirectory(0)
    rootfile.Close()

    datahist=ROOT.RooDataHist(newname,"2D signal histogram",ROOT.RooArgList(x,y),sighist)
    return datahist
#    histpdf=ROOT.RooHistPdf(newname,"2d signal histogram PDF",ROOT.RooArgSet(x,y),datahist)
#    print(histpdf)
#    return histpdf

# set the omega mass and phi mass values here
pmass=1050.
wmass=0.50
tlabel=str(pmass)+"_"+str(wmass)

# set the signal interpolation parameters here
txmin=0.5; txmax=2.1; tymin=450.; tymax=1050.
tx=ROOT.RooRealVar("tx","tx",txmin,txmax)
ty=ROOT.RooRealVar("ty","ty",tymin,tymax)
tx.setVal(wmass)
ty.setVal(pmass)
fnA="input/mass2D_Phi_450_omega_0p5.root"
fnB="input/mass2D_Phi_450_omega_2p1.root"
fnC="input/mass2D_Phi_1050_omega_0p5.root"
fnD="input/mass2D_Phi_1050_omega_2p1.root"

# create the observables (do this based on the data's histogram boundaries)
rootfile = ROOT.TFile("input/egamma2018-full-newbinning_signalreigon_phi_by_omega.root","READ")
datahist2d = rootfile.Get("plots/recomass_2d_variable")
m2p = ROOT.RooRealVar("m2p","Invariant mass of the 2-prong",datahist2d.GetXaxis().GetBinLowEdge(1),datahist2d.GetXaxis().GetBinUpEdge(datahist2d.GetXaxis().GetNbins()))
m2pg = ROOT.RooRealVar("m2pg","Invariant mass of the 2-prong and photon",datahist2d.GetYaxis().GetBinLowEdge(1),datahist2d.GetYaxis().GetBinUpEdge(datahist2d.GetYaxis().GetNbins()))


# where to write things out
fileout = ROOT.TFile("sigworkspace_"+tlabel+".root", "RECREATE")
w = ROOT.RooWorkspace("w","w")

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
# this is a dummy value for now
acceff=ROOT.RooRealVar("acceff","interpolated acceptance*efficiency",0.0001)
acceff.setConstant(True)
print("The interpolated acc*eff is "+str(acceff.getValV()))

# interpolate the signal PDF
bintx = ROOT.RooBinning(1,txmin,txmax)
binty = ROOT.RooBinning(1,tymin,tymax)
grid = ROOT.RooMomentMorphFuncNDCorr.Grid2(bintx,binty)
histA = get2DHist("histA",fnA,"hist_sum_1",m2p,m2pg)
histB = get2DHist("histB",fnB,"hist_sum_1",m2p,m2pg)
histC = get2DHist("histC",fnC,"hist_sum_1",m2p,m2pg)
histD = get2DHist("histD",fnD,"hist_sum_1",m2p,m2pg)
histpdfA=ROOT.RooHistPdf("histpdfA","histpdfA",ROOT.RooArgSet(m2p,m2pg),histA)
histpdfB=ROOT.RooHistPdf("histpdfB","histpdfA",ROOT.RooArgSet(m2p,m2pg),histB)
histpdfC=ROOT.RooHistPdf("histpdfC","histpdfA",ROOT.RooArgSet(m2p,m2pg),histC)
histpdfD=ROOT.RooHistPdf("histpdfD","histpdfA",ROOT.RooArgSet(m2p,m2pg),histD)
grid.addPdf(histpdfA,0,0)
grid.addPdf(histpdfB,0,1)
grid.addPdf(histpdfC,1,0)
grid.addPdf(histpdfD,1,1)
morph = ROOT.RooMomentMorphFuncNDCorr("morph","morph", ROOT.RooArgList(tx,ty), ROOT.RooArgList(m2p, m2pg), grid, ROOT.RooMomentMorphFuncNDCorr.Linear)
morph.setPdfMode()
sighist = morph.createHistogram("m2p:m2pg")
fileout.cd()
sighist.Write()
#getattr(w,"import")(sighist)

#sigpdf = ROOT.RooWrapperPdf("sigpdf","sigpdf",morph)
#print(sigpdf)

#sigpdf1d = sigpdf.createProjection(ROOT.RooArgSet(m2p))
#can = ROOT.TCanvas()
#plot = m2pg.frame()
#sigpdf1d.plotOn(plot)
#plot.Draw()
#can.Update()
#can.Draw()
#can.SaveAs("asdf.pdf")

# create PDFs for different 2-prong mass slices
#for bin in range(1,datahist2d.GetXaxis().GetNbins()+1):
#    label = "bin"+str(bin)
#    m2p.setRange("range_"+label,datahist2d.GetXaxis().GetBinLowEdge(bin),datahist2d.GetXaxis().GetBinUpEdge(bin))
#    sigpdf1d = sigpdf.createProjection(ROOT.RooArgSet(m2p),ROOT.ProjectionRange("range_"+label))
#    sigpdf1d = sigpdf.createProjection(ROOT.RooArgSet(m2p))
#    sigpdf1d.SetName("signal_"+label)
#    accnum = sigpdf.createIntegral(ROOT.RooArgSet(m2p,m2pg))
#    dennum = sigpdf.createIntegral(ROOT.RooArgSet(m2p,m2pg))
#    sliceacc = ROOT.RooRealVar("sliceacc_"+label,"acceptance in the given slice",accnum.getVal()/accden.getVal())
#    sliceacc.setConstant(True)
#    print("The slice acceptance for "+label+" is "+str(sliceacc.getValV()))
#    norm = ROOT.RooProduct("signal_"+label+"_norm", "Normalisation of signal", ROOT.RooArgList(xsec,acceff,sliceacc))

    # write to workspace
    #getattr(w,"import")(norm)
#    getattr(w,"import")(sigpdf1d)



    # plot for inspection later
#    can = ROOT.TCanvas()
#    can.Divide(2,1)
#    can.cd(1)
#    plot1 = m2pg.frame()
#    lo=sighist2d.GetXaxis().GetBinLowEdge(bin)
#    up=sighist2d.GetXaxis().GetBinUpEdge(bin)
#    plot1.SetTitle("2-prong mass ["+str(lo)+", "+str(up)+"]")
#    sigHist.plotOn(plot1)
#    plot1.Draw()
#    can.cd(2)
#    plot2 = m2pg.frame()
#    plot2.SetTitle("2-prong mass ["+str(lo)+", "+str(up)+"]")
#    sigHistPdf.plotOn(plot2)
#    plot2.Draw()
#    can.Update()
#    can.Draw()
#    can.SaveAs("sigplot_"+tlabel+"_"+label+".pdf")

w.Print()
fileout.cd()
w.Write()
fileout.Close()



