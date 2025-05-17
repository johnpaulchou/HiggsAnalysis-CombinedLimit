#!/bin/env python3

import ROOT
import common.tdrstyle as tdrstyle
import common.common as common
import files
import math
import argparse

tdrstyle.setTDRStyle()


###############################################################
# start of the "main" function
###############################################################

if __name__ == "__main__":

    # setup parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("filenames", nargs="+", help="A list of root files containing the limit info")
    parser.add_argument("--drawSmooth",help="Draw a smoothed version of the limit plot",action=argparse.BooleanOptionalAction,default=False)
    args = parser.parse_args()

    # create histograms
    xbinsn = len(files.wmasspoints)
    xbinsw = (files.wmasspoints[1]-files.wmasspoints[0])
    ybinsn = len(files.pmasspoints)
    ybinsw = (files.pmasspoints[1]-files.pmasspoints[0])
    xbinslo = files.wmasspoints[0]-xbinsw*0.5
    xbinshi = files.wmasspoints[xbinsn-1]+xbinsw*0.5
    ybinslo = files.pmasspoints[0]-ybinsw*0.5
    ybinshi = files.pmasspoints[ybinsn-1]+ybinsw*0.5

    hSig = ROOT.TH2D("hSig","Significance",xbinsn,xbinslo,xbinshi,ybinsn,ybinslo,ybinshi)

    # loop over all of the arguments
    for file in args.filenames:
        dict=common.parse_HC_limit_tree(file,hasExpected=False)
        imass=int(dict["mass"])
        windex,pindex=files.indexpair(imass)
        pmass=files.pmasspoints[pindex]
        sig=dict["obs"]
        hSig.SetBinContent(windex+1,pindex+1,sig)

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
    hSig.SetMinimum(-0.2)
    hSig.SetMaximum(5.0)

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
    
    can.Update()
    can.Draw()
    can.SaveAs("ressig.pdf")
