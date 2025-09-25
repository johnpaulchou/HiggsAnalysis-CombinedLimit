#!/bin/env python3

import ROOT
import files
import argparse
import common.common as common

###############################################################
# start of the "main" function
###############################################################

if __name__ == "__main__":
    # setup and use the parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--region',help='region to run over',choices=files.regions,default=files.regions[0])
    parser.add_argument("--sigtype",help="signal type that we're using",choices=files.sigtypes, default=files.sigtypes[0])
    args=parser.parse_args()
    
    # open the file and create the workspace
    fileout = ROOT.TFile(files.bkgworkspacefn, "RECREATE")
    w = ROOT.RooWorkspace(files.workspacename,files.workspacename)

    # loop over eta bins
    for etabin in files.etabins:

        # get the 2d data histogram
        if args.sigtype==files.sigtypes[0]:   tempname="plots/recomass"
        elif args.sigtype==files.sigtypes[1]: tempname="plots/recomassprime"
        boundaries=files.get_m2pbin_boundaries(args.region, args.sigtype)
        nboundaries=files.get_num_m2pbins(args.region, args.sigtype)

        if args.region==files.regions[0]: datahist2d=common.get_TH1_from_file(files.datafilename, tempname+"_sideband_"+etabin)
        elif args.region==files.regions[1]: datahist2d=common.get_TH1_from_file(files.datafilename, tempname+"_"+etabin)
        
        # loop over the 2-prong mass slices
        for binindex in range(nboundaries):
            label = "bin"+str(binindex)+etabin
            datahist1d = datahist2d.ProjectionY("_py"+label,boundaries[binindex],boundaries[binindex+1]-1)
            datanorm=datahist1d.Integral(1,datahist1d.GetNbinsX())

            # convert histogram into a RooDataHist
            dataHist = ROOT.RooDataHist("dataHist_"+label, "dataHist", files.m2pg, datahist1d)

            strategy=2
            # set up the three background function models
            p1 = ROOT.RooRealVar("p1_"+label,"p1",-10,-25,-5)
            p2 = ROOT.RooRealVar("p2_"+label,"p2",-1,-3,-.1)
            sqrts = ROOT.RooRealVar("sqrts","sqrts",13000.)
            f1 = ROOT.RooDijet1Pdf("model_bkg_f1_"+label,"f1",files.m2pg,p1,p2,sqrts)
            p3 = ROOT.RooRealVar("p3_"+label,"p3",-5,-200,0)
            p4 = ROOT.RooRealVar("p4_"+label,"p4",-1,-20,0)
            f2 = ROOT.RooDijet2Pdf("model_bkg_f2_"+label,"f2",files.m2pg,p3,p4,sqrts)
            p5 = ROOT.RooRealVar("p5_"+label,"p5",5,0,100)
            p6 = ROOT.RooRealVar("p6_"+label,"p6",-20,-200,0)
            f3 = ROOT.RooDijet3Pdf("model_bkg_f3_"+label,"f3",files.m2pg,p5,p6,sqrts)

            # perform some initial fits
            r1=f1.fitTo(dataHist, ROOT.RooFit.Save(True),ROOT.RooFit.Minimizer("Minuit2","minimize"), ROOT.RooFit.Strategy(strategy),ROOT.RooFit.SumW2Error(True), ROOT.RooFit.PrintLevel(-1))
            r2=f2.fitTo(dataHist, ROOT.RooFit.Save(True),ROOT.RooFit.Minimizer("Minuit2","minimize"), ROOT.RooFit.Strategy(strategy),ROOT.RooFit.SumW2Error(True), ROOT.RooFit.PrintLevel(-1))
            r3=f3.fitTo(dataHist, ROOT.RooFit.Save(True),ROOT.RooFit.Minimizer("Minuit2","minimize"), ROOT.RooFit.Strategy(strategy),ROOT.RooFit.SumW2Error(True), ROOT.RooFit.PrintLevel(-1))

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
            normlo=0.
            normhi=2.
            normf1 = ROOT.RooRealVar("model_bkg_f1_"+label+"_norm", "Number of background events", datanorm, datanorm*normlo, datanorm*normhi)
            normf2 = ROOT.RooRealVar("model_bkg_f2_"+label+"_norm", "Number of background events", datanorm, datanorm*normlo, datanorm*normhi)
            normf3 = ROOT.RooRealVar("model_bkg_f3_"+label+"_norm", "Number of background events", datanorm, datanorm*normlo, datanorm*normhi)
            normmulti = ROOT.RooRealVar("multipdf_"+label+"_norm", "Number of background events", datanorm, datanorm*normlo, datanorm*normhi)

            # write to workspace
            getattr(w, "import")(dataHist)
            getattr(w, "import")(cat)
            getattr(w, "import")(normmulti)
            getattr(w, "import")(multipdf)
            getattr(w, "import")(normf1)
            getattr(w, "import")(normf2)
            getattr(w, "import")(normf3)
            getattr(w, "import")(r1)
            getattr(w, "import")(r2)
            getattr(w, "import")(r3)

    # write the workspace and region to the file
    fileout.cd()
    w.Write()
    (ROOT.TNamed("region",args.region)).Write()
    (ROOT.TNamed("sigtype",args.sigtype)).Write()
    fileout.Close()
