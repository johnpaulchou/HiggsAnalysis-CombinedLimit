import ROOT

f = ROOT.TFile("higgsCombine.bestfit.MultiDimFit.mH120.root")
w = f.Get("w")
w.Print("v")
m2pg = w.var("m2pg")
can = ROOT.TCanvas()
plot = m2pg.frame()
w.data("sigHist_bin13").plotOn(plot)
sb_model = w.pdf("model_s").getPdf("bin13")

# Prefit
sb_model.plotOn( plot, ROOT.RooFit.LineColor(2), ROOT.RooFit.Name("prefit") )

# Postfit
r = w.var("r")
w.loadSnapshot("MultiDimFit")
r.setVal(15.)
sb_model.plotOn( plot, ROOT.RooFit.LineColor(4), ROOT.RooFit.Name("postfit") )

plot.Draw()
can.Update()
can.SaveAs("part2_sb_model.png")


