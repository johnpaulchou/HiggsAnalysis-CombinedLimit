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
    parser.add_argument("--suppressPoints", type=int, nargs="*", help="Observed points to suppress (set them to the expected)")
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

    hObs = ROOT.TH2D("hObs","Observed",xbinsn,xbinslo,xbinshi,ybinsn,ybinslo,ybinshi)
    hExp = ROOT.TH2D("hExp","Expected",xbinsn,xbinslo,xbinshi,ybinsn,ybinslo,ybinshi)
    hExpLo = ROOT.TH2D("hExpLo","Expected -1 sigma",xbinsn,xbinslo,xbinshi,ybinsn,ybinslo,ybinshi)
    hExpHi = ROOT.TH2D("hExpHi","Expected +1 sigma",xbinsn,xbinslo,xbinshi,ybinsn,ybinslo,ybinshi)
    hObsXs = ROOT.TH2D("hObsXs","Observed XS",xbinsn,xbinslo,xbinshi,ybinsn,ybinslo,ybinshi)
    
    # loop over all of the arguments
    for file in args.filenames:
        dict=common.parse_HC_limit_tree(file)
        imass=int(dict["mass"])
        windex,pindex=files.indexpair(imass)
        pmass=files.pmasspoints[pindex]
        obs=dict["obs"]
        exp=dict["exp-med"]
        for skip in args.suppressPoints:
            if skip==imass:
                obs=exp
#        print("windex="+str(windex)+" pindex="+str(pindex)+" obs="+str(dict["obs"]))
        hObs.SetBinContent(windex+1,pindex+1,math.log10(obs))
        hExp.SetBinContent(windex+1,pindex+1,math.log10(exp))
        hExpLo.SetBinContent(windex+1,pindex+1,math.log10(dict["exp-1"]))
        hExpHi.SetBinContent(windex+1,pindex+1,math.log10(dict["exp+1"]))
        hObsXs.SetBinContent(windex+1,pindex+1,obs*files.get_xsection(pmass))

    nbins=200
    if args.drawSmooth:
        hObs=common.interpolate_th2d(hObs, nbins, nbins)
        hExp=common.interpolate_th2d(hExp, nbins, nbins)
        hExpLo=common.interpolate_th2d(hExpLo, nbins, nbins)
        hExpHi=common.interpolate_th2d(hExpHi, nbins, nbins)
        hObsXs=common.interpolate_th2d(hObsXs, nbins, nbins)

    # Draw observed limits
    can1 = ROOT.TCanvas()
    can1.SetFillColor(0)
    can1.SetBorderMode(0)
    can1.SetFrameFillStyle(0)
    can1.SetFrameBorderMode(0)
    can1.SetTickx(0)
    can1.SetTicky(0)
    can1.SetMargin(0.15,0.20,0.15,0.15)
    can1.cd()
    hObs.Draw("colz")
    hObs.GetXaxis().SetTitle("m_{#omega} [GeV]")
    hObs.GetYaxis().SetTitle("m_{#phi} [GeV]")
    hObs.GetZaxis().SetTitle("Observed log_{10}r_{95}")
    hObs.SetMinimum(-1.0)
    hObs.SetMaximum(2.0)

    obsCont=hObs.Clone("obsCont")
    obsCont.SetContour(2)
    obsCont.SetContourLevel(1,.0)
    obsCont.SetLineWidth(3)
    obsCont.SetLineColorAlpha(ROOT.kBlack,0.7)
    obsCont.SetLineStyle(ROOT.kDotted)
    obsCont.Draw("cont3same")

    # store the observed contour
    contours = ROOT.gROOT.GetListOfSpecials().FindObject("contours")
    obsGraphs = []
    if contours:
        for i in range(contours.GetSize()):
            level_list = contours.At(i)
            for j in range(level_list.GetSize()):
                gr = level_list.At(j)
                cloned = gr.Clone()
                cloned.SetLineColor(ROOT.kRed)  # Optional: set color/style
                cloned.SetLineWidth(2)
                obsGraphs.append(cloned)

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
    
    can1.Update()
    can1.Draw()
    can1.SaveAs("resobs.pdf")


    # Draw Expected limits
    
    can2 = ROOT.TCanvas()
    can2.SetFillColor(0)
    can2.SetBorderMode(0)
    can2.SetFrameFillStyle(0)
    can2.SetFrameBorderMode(0)
    can2.SetTickx(0)
    can2.SetTicky(0)
    can2.SetMargin(0.15,0.20,0.15,0.15)
    can2.cd()
    hExp.Draw("colz")
    hExp.GetXaxis().SetTitle("m_{#omega} [GeV]")
    hExp.GetYaxis().SetTitle("m_{#phi} [GeV]")
    hExp.GetZaxis().SetTitle("Expected log_{10}r_{95}")
    hExp.SetMinimum(-1.0)
    hExp.SetMaximum(2.0)

    expCont=hExp.Clone("expCont")
    expCont.SetContour(2)
    expCont.SetContourLevel(1,.0)
    expCont.SetLineWidth(3)
    expCont.SetLineColorAlpha(ROOT.kBlack,0.7)
    expCont.SetLineStyle(ROOT.kDashed)
    expCont.Draw("cont3same")

    # store the expected contour
    contours = ROOT.gROOT.GetListOfSpecials().FindObject("contours")
    expGraphs = []
    if contours:
        for i in range(contours.GetSize()):
            level_list = contours.At(i)
            for j in range(level_list.GetSize()):
                gr = level_list.At(j)
                cloned = gr.Clone()
                cloned.SetLineColor(ROOT.kRed)  # Optional: set color/style
                cloned.SetLineWidth(2)
                expGraphs.append(cloned)

    cmstxt.DrawLatexNDC(0.15,0.87,"CMS")
    extratxt.DrawLatexNDC(0.26,0.87,"Preliminary")
    lumitxt.DrawLatexNDC(0.63,0.87,"138 fb^{-1} (13 TeV)")
    
    can2.Update()
    can2.Draw()
    can2.SaveAs("resexp.pdf")

    # Draw xs limits
    can3 = ROOT.TCanvas()
    can3.SetFillColor(0)
    can3.SetFrameBorderMode(0)
    can3.SetTickx(0)
    can3.SetTicky(0)
    can3.SetMargin(0.15,0.20,0.15,0.15)
    can3.cd()
    can3.SetLogz(True)
    hObsXs.Draw("colz")
    hObsXs.GetXaxis().SetTitle("m_{#omega} [GeV]")
    hObsXs.GetYaxis().SetTitle("m_{#phi} [GeV]")
    hObsXs.GetZaxis().SetTitle("95% CL Excluded #sigma#timesBR [pb]")
    hObsXs.SetMinimum(-100)
    hObsXs.SetMaximum(20)

    for gr in expGraphs:
        gr.Draw("L same")
    for gr in obsGraphs:
        gr.Draw("L same")

#    hExpLo.SetContour(2)
 #   hExpLo.SetContourLevel(1,.0)
  #  hExpLo.SetLineWidth(3)
   # hExpLo.SetLineColorAlpha(ROOT.kBlack,0.7)
    #hExpLo.Draw("cont3same")
   # hExpHi.SetContour(2)
   # hExpHi.SetContourLevel(1,.0)
  #  hExpHi.SetLineWidth(3)
  #  hExpHi.SetLineColorAlpha(ROOT.kBlack,0.7)
  #  hExpHi.Draw("cont3same")

    cmstxt.DrawLatexNDC(0.15,0.87,"CMS")
    extratxt.DrawLatexNDC(0.26,0.87,"Preliminary")
    lumitxt.DrawLatexNDC(0.63,0.87,"138 fb^{-1} (13 TeV)")

    can3.Update()
    can3.Draw()
    can3.SaveAs("resobsxs.pdf")

    
"""
    # Draw Significance
    
    can3 = ROOT.TCanvas()
    can3.SetFillColor(0)
    can3.SetBorderMode(0)
    can3.SetFrameFillStyle(0)
    can3.SetFrameBorderMode(0)
    can3.SetTickx(0)
    can3.SetTicky(0)
    can3.SetMargin(0.15,0.20,0.15,0.15)
    can3.cd()
    hSig.Draw("colz")
    hSig.GetXaxis().SetTitle("m_{#omega} [GeV]")
    hSig.GetYaxis().SetTitle("m_{#phi} [GeV]")
    hSig.GetZaxis().SetTitle("Significance (z-score)")
    hSig.SetMinimum(-0.1)
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
    
    can3.Update()
    can3.Draw()
    can3.SaveAs("ressig.pdf")
"""
