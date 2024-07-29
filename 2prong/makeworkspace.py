import ROOT


#where to write things out
fileout = ROOT.TFile("workspace.root", "RECREATE")
w = ROOT.RooWorkspace("w","w")

#get the 2D histogram from the file
rootfile = ROOT.TFile("egamma2018-partial_signalreigon_phi_by_omega.root","READ")
hist2d = rootfile.Get("plots/recomass_2d_variable")

for bin in range(4,25):
    hist1d = hist2d.ProjectionY("_py"+str(bin),bin,bin)
    lo=hist2d.GetXaxis().GetBinLowEdge(bin)
    up=hist2d.GetXaxis().GetBinUpEdge(bin)

    # convert histogram into a RooDataHist
    m2pg = ROOT.RooRealVar("m2pg","Invariant mass of the 2-prong and photon",499.23,4150.4400)
    #m2pg = ROOT.RooRealVar("m2pg","Invariant mass of the 2-prong and photon",499.23,1500)
    dataHist = ROOT.RooDataHist("dataHist_"+str(bin), "dataHist", m2pg, hist1d)


    p1 = ROOT.RooRealVar("p1_"+str(bin),"p1",-5,-100,0)
    p2 = ROOT.RooRealVar("p2_"+str(bin),"p2",-5,-100,0)
    sqrts = ROOT.RooRealVar("sqrts","sqrts",13000.)
    f0 = ROOT.RooDijet1Pdf("model_bkg_f0_"+str(bin),"f0",m2pg,p1,p2,sqrts)
    p3 = ROOT.RooRealVar("p3_"+str(bin),"p3",-5,-100,0)
    p4 = ROOT.RooRealVar("p4_"+str(bin),"p4",-5,-100,0)
    f1 = ROOT.RooDijet2Pdf("model_bkg_f1_"+str(bin),"f1",m2pg,p3,p4,sqrts)
    p5 = ROOT.RooRealVar("p5_"+str(bin),"p5",5,0,100)
    p6 = ROOT.RooRealVar("p6_"+str(bin),"p6",-5,-100,100)
    f2 = ROOT.RooDijet3Pdf("model_bkg_f2_"+str(bin),"f2",m2pg,p5,p6,sqrts)

    # naming convention is used for an extended likelihood
    norm0 = ROOT.RooRealVar("model_bkg_f0_"+str(bin)+"_norm","norm",dataHist.numEntries(),0,3*dataHist.numEntries())
    norm1 = ROOT.RooRealVar("model_bkg_f1_"+str(bin)+"_norm","norm",dataHist.numEntries(),0,3*dataHist.numEntries())
    norm2 = ROOT.RooRealVar("model_bkg_f2_"+str(bin)+"_norm","norm",dataHist.numEntries(),0,3*dataHist.numEntries())

    #plot fits
    f0.fitTo(dataHist)
    f1.fitTo(dataHist)
    f2.fitTo(dataHist)
    can = ROOT.TCanvas()
    plot = m2pg.frame()
    dataHist.plotOn(plot)
    f0.plotOn(plot,ROOT.RooFit.LineColor(4))
    f1.plotOn(plot,ROOT.RooFit.LineColor(2))
    f2.plotOn(plot,ROOT.RooFit.LineColor(3))
    plot.Draw()
    plot.SetTitle("2-prong mass ["+str(lo)+", "+str(up)+"]")
    can.Update()
    can.Draw()
    can.SaveAs("plot_"+str(bin)+".png")

    #write to workspace
    getattr(w, "import")(dataHist)
    getattr(w, "import")(norm0)
    getattr(w, "import")(norm1)
    getattr(w, "import")(norm2)
    getattr(w, "import")(f0)
    getattr(w, "import")(f1)
    getattr(w, "import")(f2)

w.Print()
fileout.cd()
w.Write()
fileout.Close()
