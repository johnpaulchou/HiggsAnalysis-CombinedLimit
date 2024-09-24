import ROOT


# where to write things out
fileout = ROOT.TFile("../output/bkgworkspace.root", "RECREATE")
w = ROOT.RooWorkspace("w","w")

# get the 2D histogram from the file
rootfile = ROOT.TFile("../input/egamma2018-full-newbinning_signalreigon_phi_by_omega.root","READ")
datahist2d = rootfile.Get("plots/recomass_2d_variable")
m2pg = ROOT.RooRealVar("m2pg","Invariant mass of the 2-prong and photon",datahist2d.GetYaxis().GetBinLowEdge(1),datahist2d.GetYaxis().GetBinUpEdge(datahist2d.GetYaxis().GetNbins()))

# loop over the 2-prong mass slices
for bin in range(1,datahist2d.GetXaxis().GetNbins()+1):
    label = "bin"+str(bin)
    datahist1d = datahist2d.ProjectionY("_py"+label,bin,bin)

    # convert histogram into a RooDataHist
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
#    norm = ROOT.RooRealVar("model_bkg_f1_"+label+"_norm", "Number of background events", dataHist.numEntries(),0,3*dataHist.numEntries())

    # write to workspace
    getattr(w, "import")(dataHist)
    getattr(w, "import")(cat)
    getattr(w, "import")(norm)
    getattr(w, "import")(multipdf)

    # plot fits for inspection later
    fileout.cd()
    datahist2d.Write()
    f1.Write()
    f2.Write()
    f3.Write()

w.Print()
fileout.cd()
w.Write()
fileout.Close()
