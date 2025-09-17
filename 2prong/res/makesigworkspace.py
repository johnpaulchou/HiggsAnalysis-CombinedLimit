#!/bin/env python3

import ROOT
import sys
import files
import common.common as common
import argparse

# function to get acceptance from a file
def getAcc(filename, histnames, normhistname):
    integral=0.0
    for histname in histnames:
        h=common.get_TH1_from_file(filename, histname)
        integral += h.Integral(1,h.GetXaxis().GetNbins(),1,h.GetYaxis().GetNbins())

    hn=common.get_TH1_from_file(filename, normhistname)
    norm=hn.GetBinContent(1)
    return integral/norm


###### main function ######
if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--imass', help="index of the job to run (0-"+str(files.npoints-1)+")", type=int)
    parser.add_argument("--sigtype",help="signal type that we're using",choices=files.sigtypes,default=files.sigtypes[0])
    args=parser.parse_args()

    (windex,pindex)=files.indexpair(args.imass)
    wmass = files.wmasspoints[windex]
    pmass = files.pmasspoints[pindex]
    print("Creating workspace for m_w="+str(wmass)+" GeV and m_phi="+str(pmass)+" GeV")
    # find the grid points to match up to the chosen omega and phi masses
    txmin=txmax=tymin=tymax=-999.
    for i in range(len(files.gengridw)-1):
        for j in range(len(files.gengridp)-1):
            if files.gengridw[i][0]<=wmass and files.gengridw[i+1][0]>=wmass and files.gengridp[j][0]<=pmass and files.gengridp[j+1][0]>=pmass:
                txmin=files.gengridw[i][0]
                txmax=files.gengridw[i+1][0]
                tymin=files.gengridp[j][0]
                tymax=files.gengridp[j+1][0]
                fnA=files.genfilenames[i][j]
                fnB=files.genfilenames[i+1][j]
                fnC=files.genfilenames[i][j+1]
                fnD=files.genfilenames[i+1][j+1]

    if txmin<0 or txmax<0 or tymin<0 or tymax<0:
        print("Outside the theory bounds")
        exit(1)
    print("txmin="+str(txmin)+"; txmax="+str(txmax)+"; tymin="+str(tymin)+"; tymax="+str(tymax))

    # set the signal interpolation parameters here
    tx=ROOT.RooRealVar("tx","tx",txmin,txmax)
    ty=ROOT.RooRealVar("ty","ty",tymin,tymax)
    tx.setVal(wmass)
    ty.setVal(pmass)

    # get the cross section
    xsec=ROOT.RooRealVar("xsec","Interpolated theory x-section",files.get_xsection(pmass))
    xsec.setConstant(True)
    print("The interpolated cross section is "+str(xsec.getValV())+" fb.")

    if args.sigtype==files.sigtypes[0]:
        tempname="plots/recomass"
        boundaries=files.eta_m2pbin_boundaries
        nboundaries=files.eta_num_m2pbins
    elif args.sigtype==files.sigtypes[1]:
        tempname="plots/recomassprime"
        boundaries=files.etaprime_m2pbin_boundaries
        nboundaries=files.etaprime_num_m2pbins
    
    # interpolate the acceptance*efficiency
    accA=getAcc(fnA, (tempname+'_barrel',tempname+'_endcap'), "plots/cutflow")
    accB=getAcc(fnB, (tempname+'_barrel',tempname+'_endcap'), "plots/cutflow")
    accC=getAcc(fnC, (tempname+'_barrel',tempname+'_endcap'), "plots/cutflow")
    accD=getAcc(fnD, (tempname+'_barrel',tempname+'_endcap'), "plots/cutflow")
    z5=(accC-accA)/(tymax-tymin)*pmass+(accA*tymax-accC*tymin)/(tymax-tymin)
    z6=(accD-accB)/(tymax-tymin)*pmass+(accB*tymax-accD*tymin)/(tymax-tymin)
    acc=(z6-z5)/(txmax-txmin)*wmass+(z5*txmax-z6*txmin)/(txmax-txmin)
    acceff=ROOT.RooRealVar("acceff","interpolated acceptance*efficiency",acc)
    acceff.setConstant(True)
    print("The interpolated acc*eff is "+str(acceff.getValV()))
    
    # create label for output workspace
    fileout = ROOT.TFile(files.sigworkspacefn,"RECREATE")
    w = ROOT.RooWorkspace("w","w")

    # loop over systematic sources
    for syst in files.systs:

        # loop over eta regions
        for etabin in files.etabins:

            # get the 2D histograms
            hA=common.get_TH1_from_file(fnA, tempname+"_"+etabin+syst)
            hB=common.get_TH1_from_file(fnB, tempname+"_"+etabin+syst)
            hC=common.get_TH1_from_file(fnC, tempname+"_"+etabin+syst)
            hD=common.get_TH1_from_file(fnD, tempname+"_"+etabin+syst)

            # create RooDataHists
            dhA=ROOT.RooDataHist(hA.GetName()+"A_dh","2D signal RooDataHist",ROOT.RooArgList(files.m2p,files.m2pg),hA)
            dhB=ROOT.RooDataHist(hB.GetName()+"B_dh","2D signal RooDataHist",ROOT.RooArgList(files.m2p,files.m2pg),hB)
            dhC=ROOT.RooDataHist(hC.GetName()+"C_dh","2D signal RooDataHist",ROOT.RooArgList(files.m2p,files.m2pg),hC)
            dhD=ROOT.RooDataHist(hD.GetName()+"D_dh","2D signal RooDataHist",ROOT.RooArgList(files.m2p,files.m2pg),hD)

            # create RooAbsPdfs out of datahists
            pdfA=ROOT.RooHistPdf(hA.GetName()+"A_pdf","2D signal pdf",ROOT.RooArgSet(files.m2p,files.m2pg), dhA)
            pdfB=ROOT.RooHistPdf(hB.GetName()+"B_pdf","2D signal pdf",ROOT.RooArgSet(files.m2p,files.m2pg), dhB)
            pdfC=ROOT.RooHistPdf(hC.GetName()+"C_pdf","2D signal pdf",ROOT.RooArgSet(files.m2p,files.m2pg), dhC)
            pdfD=ROOT.RooHistPdf(hD.GetName()+"D_pdf","2D signal pdf",ROOT.RooArgSet(files.m2p,files.m2pg), dhD)

            # create a grid with each pdf at a corner
            bintx=ROOT.RooBinning(1,txmin,txmax)
            binty=ROOT.RooBinning(1,tymin,tymax)
            grid=ROOT.RooMomentMorphFuncNDFix.Grid2(bintx,binty);
            grid.addPdf(pdfA,0,0)
            grid.addPdf(pdfB,1,0)
            grid.addPdf(pdfC,0,1)
            grid.addPdf(pdfD,1,1)

            # morph and create a new 2D histogram in its place
            morph=ROOT.RooMomentMorphFuncNDFix("morph","morph",ROOT.RooArgList(tx,ty),ROOT.RooArgList(files.m2p,files.m2pg),grid,ROOT.RooMomentMorphFuncNDFix.Linear);
            morph.setPdfMode()
            tx.setVal(wmass)
            ty.setVal(pmass)
            morphhist=hA.Clone(hA.GetName()+"m")
            morphhist.Reset()
            morphhist=morph.fillHistogram(morphhist,ROOT.RooArgList(files.m2p,files.m2pg))
        
            # create PDFs for different m2p slices
            fileout.cd()
            for binindex in range(nboundaries):
                label = "bin"+str(binindex)+etabin+syst
                projy=morphhist.ProjectionY("_py"+label,boundaries[binindex],boundaries[binindex+1]-1)
                accnum = projy.Integral(1,projy.GetXaxis().GetNbins())
                accden = morphhist.Integral(1,morphhist.GetXaxis().GetNbins(),1,morphhist.GetYaxis().GetNbins())
                dh=ROOT.RooDataHist("dh"+label,"dh"+label,files.m2pg,projy)
                sigpdf1d = ROOT.RooHistPdf("sigpdf_"+label,"signal PDF for a slice in files.m2p",files.m2pg,dh)
                sliceacc = ROOT.RooRealVar("sliceacc_"+label,"acceptance in a given slice",accnum/accden)
                sliceacc.setConstant(True)
                print("The slice acceptance for "+label+" is "+str(sliceacc.getValV()))
                norm = ROOT.RooProduct("sigpdf_"+label+"_norm", "Normalisation of signal", ROOT.RooArgList(xsec,acceff,sliceacc))
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
    (ROOT.TNamed("imass",str(args.imass))).Write()
    (ROOT.TNamed("wmass",str(wmass))).Write()
    (ROOT.TNamed("pmass",str(pmass))).Write()
    (ROOT.TNamed("sigtype",args.sigtype)).Write()
    fileout.Close()

    
