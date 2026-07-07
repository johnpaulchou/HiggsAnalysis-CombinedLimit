#!/bin/env python3

import ROOT
import common.tdrstyle as tdrstyle
import common.common as common
import files
import math
import re
import argparse
import sys

tdrstyle.setTDRStyle()

#PLOT_SIG_MIN = -0.2
PLOT_SIG_MIN = -3.0
PLOT_SIG_MAX = 4.5

###############################################################
# start of the "main" function
###############################################################

if __name__ == "__main__":

    # setup parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("filenames", nargs="+", help="A list of root files containing the limit info")
    parser.add_argument("--drawSmooth",help="Draw a smoothed version of the limit plot",action=argparse.BooleanOptionalAction,default=False)
    parser.add_argument("--sigtype",help="signal type that we're using",choices=files.sigtypes, default=files.sigtypes[0])
    parser.add_argument("--fixedgrid",action='store_true', default=False)
    parser.add_argument("-t", "--toybasedsig",action='store_true', default=False)

    args = parser.parse_args()

    #ROOT.gROOT.SetBatch(True)

    # create histograms
    if args.fixedgrid:
        xbinsw = (files.wmasspoints[1]-files.wmasspoints[0])
        ybinsw = (files.pmasspoints[1]-files.pmasspoints[0])
        xbinslo, xbinshi = 0.85, 4
        ybinslo, ybinshi = 550, 2925
        xbinslo = xbinslo - 0.5*xbinsw
        xbinshi = xbinshi + 0.5*xbinsw
        ybinslo = ybinslo - 0.5*ybinsw
        ybinshi = ybinshi + 0.5*ybinsw
        xbinsn = int((xbinshi - xbinslo)/xbinsw)
        ybinsn = int((ybinshi - ybinslo)/ybinsw)
    else:
        xbinsw = (files.wmasspoints[1]-files.wmasspoints[0])
        ybinsw = (files.pmasspoints[1]-files.pmasspoints[0])
        xbinsn = len(files.wmasspoints)
        ybinsn = len(files.pmasspoints)
        xbinslo = files.wmasspoints[0]-xbinsw*0.5
        xbinshi = files.wmasspoints[xbinsn-1]+xbinsw*0.5
        ybinslo = files.pmasspoints[0]-ybinsw*0.5
        ybinshi = files.pmasspoints[ybinsn-1]+ybinsw*0.5

    hSig = ROOT.TH2D("hSig","Significance",xbinsn,xbinslo,xbinshi,ybinsn,ybinslo,ybinshi)

    # setup hGen
    def getdrawbin(imass):
        wmass, pmass = files.indexmasses(imass)
        xbin = hGen.GetXaxis().FindBin(wmass)
        ybin = hGen.GetYaxis().FindBin(pmass)
        return xbin, ybin

    hGen = ROOT.TH2D("hGen","Generated Masspoints",xbinsn,xbinslo,xbinshi,ybinsn,ybinslo,ybinshi)
    for imass, entry in enumerate(files.genfilenames_raw):
        if not entry=='':
            xindex, yindex = getdrawbin(imass)
            hGen.SetBinContent(xindex,yindex,0.1)

    # loop over all of the arguments
    for count, file in enumerate(args.filenames):

        if not args.toybasedsig:
            dict=common.parse_HC_limit_tree(file,hasExpected=False)
            imass=int(dict["mass"]) 
            windex,pindex=files.indexpair(imass)
            pmass=files.pmasspoints[pindex]
            sig=dict["obs"]
            hSig.SetBinContent(windex+1,pindex+1,sig)
        if args.toybasedsig:
            #higgsCombineTest.HybridNew.mH71
            #higgsCombineTest.HybridNew.mH71.-1783651521.root
            # parse the filename to get the parameters
            # NB that this assumes it takes the form, fitDiagnosticsTest_m${mass}_sig${strength}.root, which should come from runbias.sh
            # This code won't work if that formula is changed
            m = re.search('higgsCombineTest_HybridNew_mH(.+?)_(.+?)_root', file.replace(".","_"))
            if m:
                try:
                    imass=int(m.group(1))
                    seed=str(m.group(2))
                except ValueError:
                    print("Could not convert "+m.group(1)+" and "+m.group(2)+"")
                    continue
            else:
                print("Could not parse the file "+file+" according to the regex.")
                continue
            #print(imass, seed)
            f = ROOT.TFile.Open(file)
            toy_dir = f.Get("toys")
            #print(toy_dir)
            res = None
            for key in toy_dir.GetListOfKeys():
                #print(key)
                obj = key.ReadObj()
                if isinstance(obj, ROOT.RooStats.HypoTestResult):
                    res = obj
                    #print(res)
                    #print(res.Significance())
                    break
            if not res:
                print(file)
                continue
            sig = res.Significance()
            #dict=common.parse_toybased_sig_tree(file)
            #imass=int(dict["mass"]) 

            #imass=count
            windex,pindex=files.indexpair(imass)
            #if sig < 0:
            #    sig = 0
            if math.isinf(sig) or math.isnan(sig):
                print(file)
                print(imass)
                print(sig, "nan")
                sig = -100
            hSig.SetBinContent(windex+1,pindex+1,sig)
            #print("hi", imass, sig)


    nbins=200
    if args.drawSmooth:
        hSig=common.interpolate_th2d(hSig, nbins, nbins)

    # Draw significance
    can = ROOT.TCanvas()
    can.SetFillColor(0)
    can.SetBorderMode(0)
    can.SetFrameFillStyle(0)
    can.SetFrameBorderMode(0)
    can.SetTickx(0)
    can.SetTicky(0)
    can.SetMargin(0.15,0.20,0.15,0.15)
    can.cd()
    hSig.Draw("colz")
    hSig.GetXaxis().SetTitle("m_{#omega} [GeV]")
    hSig.GetYaxis().SetTitle("m_{#phi} [GeV]")
    hSig.GetZaxis().SetTitle("Significance (z-score)")
    hSig.SetMinimum(PLOT_SIG_MIN) # -0.2
    hSig.SetMaximum(PLOT_SIG_MAX) # 4.0

    cmstxt = ROOT.TLatex()
    cmstxt.SetTextFont(61)
    cmstxt.SetTextSize(0.07)
    cmstxt.DrawLatexNDC(0.15,0.87,"CMS")
    extratxt = ROOT.TLatex()
    extratxt.SetTextFont(52)
    extratxt.SetTextSize(0.05)
    extratxt.DrawLatexNDC(0.26,0.87,"Preliminary")
    lumitxt = ROOT.TLatex()
    lumitxt.SetTextFont(42)
    lumitxt.SetTextSize(0.05)
    lumitxt.DrawLatexNDC(0.63,0.87,"138 fb^{-1} (13 TeV)")
    sigtxt = ROOT.TLatex()
    sigtxt.SetTextFont(42)
    sigtxt.SetTextSize(0.03)
    if args.sigtype==files.sigtypes[0]:
        sigtxt.DrawLatexNDC(0.18,0.75,"#eta BR hypothesis")
    else:
        sigtxt.DrawLatexNDC(0.18,0.75,"#eta' BR hypothesis")
    
    hGen.SetMarkerStyle(5)
    hGen.SetMarkerColor(7)
    hGen.SetFillColor(7)
    #hGen.SetLineWidth(1)
    #hGen.SetLineStyle(1)
    #hGen.SetMarkerSize(5)
    hGen.Draw("box same")

    can.Update()
    can.Draw()
    can.SaveAs("ressig_"+args.sigtype+".pdf")

    print('DUMP Significance')
    nx = hSig.GetNbinsX()
    ny = hSig.GetNbinsY()
    for y in range(ny, 0, -1):  # last y-bin first
        row = [f"{hSig.GetBinContent(hSig.GetBin(x, y)):.3f}" for x in range(1, nx + 1)]
        print(" ".join(row))
