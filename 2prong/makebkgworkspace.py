import ROOT


# where to write things out
fileout = ROOT.TFile("bkgworkspace.root", "RECREATE")
w = ROOT.RooWorkspace("w","w")

# get the 2D histogram from the file
rootfile = ROOT.TFile("egamma2018-partial_signalreigon_phi_by_omega.root","READ")
datahist2d = rootfile.Get("plots/recomass_2d_variable")

# loop over the 2-prong mass slices
for bin in range(4,25):
    label = "bin"+str(bin)
    datahist1d = datahist2d.ProjectionY("_py"+label,bin,bin)

    # convert histogram into a RooDataHist
    m2pg = ROOT.RooRealVar("m2pg","Invariant mass of the 2-prong and photon",499.23,4150.4400)
    #m2pg = ROOT.RooRealVar("m2pg","Invariant mass of the 2-prong and photon",499.23,1500)
    dataHist = ROOT.RooDataHist("dataHist_"+label, "dataHist", m2pg, datahist1d)

    # set up the three background function models
    p1 = ROOT.RooRealVar("p1_"+label,"p1",-5,-100,0)
    p2 = ROOT.RooRealVar("p2_"+label,"p2",-5,-100,0)
    sqrts = ROOT.RooRealVar("sqrts","sqrts",13000.)
    f1 = ROOT.RooDijet1Pdf("model_bkg_f1_"+label,"f1",m2pg,p1,p2,sqrts)
    f1.fitTo(dataHist, ROOT.RooFit.Minimizer("Minuit2","minimize"), ROOT.RooFit.SumW2Error(True), ROOT.RooFit.PrintLevel(-1))

    p3 = ROOT.RooRealVar("p3_"+label,"p3",-5,-100,0)
    p4 = ROOT.RooRealVar("p4_"+label,"p4",-5,-100,0)
    f2 = ROOT.RooDijet2Pdf("model_bkg_f2_"+label,"f2",m2pg,p3,p4,sqrts)
    f2.fitTo(dataHist, ROOT.RooFit.Minimizer("Minuit2","minimize"), ROOT.RooFit.SumW2Error(True), ROOT.RooFit.PrintLevel(-1))

    p5 = ROOT.RooRealVar("p5_"+label,"p5",5,0,100)
    p6 = ROOT.RooRealVar("p6_"+label,"p6",-5,-100,100)
    f3 = ROOT.RooDijet3Pdf("model_bkg_f3_"+label,"f3",m2pg,p5,p6,sqrts)
    f3.fitTo(dataHist, ROOT.RooFit.Minimizer("Minuit2","minimize"), ROOT.RooFit.SumW2Error(True), ROOT.RooFit.PrintLevel(-1))

    # create multiPDF
    cat = ROOT.RooCategory("pdfindex_"+label,
                           "Index of Pdf which is active"
    )
    models = ROOT.RooArgList()
    models.add(f1)
    models.add(f2)
    models.add(f3)
    multipdf = ROOT.RooMultiPdf("multipdf_"+label, "MultiPdf", cat, models)
    # naming convention of the normalization is specific to Combine and needs to be used this way for an extended likelihood. Bleh.
    norm = ROOT.RooRealVar("multipdf_"+label+"_norm", "Number of background events", dataHist.numEntries(),0,3*dataHist.numEntries())

    # write to workspace
    getattr(w, "import")(dataHist)
    getattr(w, "import")(cat)
    getattr(w, "import")(norm)
    getattr(w, "import")(multipdf)

    # plot fits for inspection later
    can = ROOT.TCanvas()
    can.Divide(2,1)
    plot = m2pg.frame()
    lo=hist2d.GetXaxis().GetBinLowEdge(bin)
    up=hist2d.GetXaxis().GetBinUpEdge(bin)
    plot.SetTitle("2-prong mass ["+str(lo)+", "+str(up)+"]")
    dataHist.plotOn(plot)
    f1.plotOn(plot,ROOT.RooFit.LineColor(4))
    f2.plotOn(plot,ROOT.RooFit.LineColor(2))
    f3.plotOn(plot,ROOT.RooFit.LineColor(3))
    can.cd(1)
    plot.Draw()
    can.cd(2)
    can.SetLogy(True)
    plot.Draw()
    can.Update()
    can.Draw()
    can.SaveAs("bkgplot_"+label+".pdf")


w.Print()
fileout.cd()
w.Write()
fileout.Close()
