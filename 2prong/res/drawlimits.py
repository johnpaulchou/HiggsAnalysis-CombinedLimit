#!/bin/env python3

import ROOT
import common.tdrstyle as tdrstyle
import common.common as common
import files
import math
import argparse
import sys

tdrstyle.setTDRStyle()

PLOT_R_LOW = -2.0
PLOT_R_HIGH = 2.5
PLOT_XSBR_LOW = 0
PLOT_XSBR_HIGH = 15

###############################################################
# start of the "main" function
###############################################################

if __name__ == "__main__":

    # setup parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("filenames", nargs="+", help="A list of root files containing the limit info")
    parser.add_argument("--drawSmooth",help="Draw a smoothed version of the limit plot",action=argparse.BooleanOptionalAction,default=False)
    parser.add_argument("--suppressPoints", type=int, nargs="*", help="Observed points to suppress (set them to the expected)")
    parser.add_argument("--sigtype",help="signal type that we're using",choices=files.sigtypes, default=files.sigtypes[0])
    parser.add_argument("--fixedgrid",action='store_true', default=False)
    args = parser.parse_args()

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

    print(xbinsw)
    print(ybinsw)
    print(xbinslo, xbinshi, xbinsn)
    print(ybinslo, ybinshi, ybinsn)

    hGen = ROOT.TH2D("hGen","Generated Masspoints",xbinsn,xbinslo,xbinshi,ybinsn,ybinslo,ybinshi)
    hObs = ROOT.TH2D("hObs","Observed",xbinsn,xbinslo,xbinshi,ybinsn,ybinslo,ybinshi)
    hExp = ROOT.TH2D("hExp","Expected",xbinsn,xbinslo,xbinshi,ybinsn,ybinslo,ybinshi)
    hExpLo = ROOT.TH2D("hExpLo","Expected -1 sigma",xbinsn,xbinslo,xbinshi,ybinsn,ybinslo,ybinshi)
    hExpHi = ROOT.TH2D("hExpHi","Expected +1 sigma",xbinsn,xbinslo,xbinshi,ybinsn,ybinslo,ybinshi)
    hObsXs = ROOT.TH2D("hObsXs","Observed XS",xbinsn,xbinslo,xbinshi,ybinsn,ybinslo,ybinshi)
    
    def getdrawbin(imass):
        wmass, pmass = files.indexmasses(imass)
        xbin = hObs.GetXaxis().FindBin(wmass)
        ybin = hObs.GetYaxis().FindBin(pmass)
        return xbin, ybin

    # setup hGen
    print(files.genfilenames_raw)
    for imass, entry in enumerate(files.genfilenames_raw):
        if not entry=='':
            xindex, yindex = getdrawbin(imass)
            hGen.SetBinContent(xindex,yindex,0.1)
   
    # loop over all of the arguments
    for file in args.filenames:
        print(file)
        dict=common.parse_HC_limit_tree(file)
        imass=int(dict["mass"])

        windex,pindex=files.indexpair(imass)
        pmass=files.pmasspoints[pindex]

        obs=dict["obs"]
        exp=dict["exp-med"]
        if args.suppressPoints is not None:
            for skip in args.suppressPoints:
                if skip==imass:
                    obs=exp
        print("imass="+str(imass)+" windex="+str(windex)+" pindex="+str(pindex)+" obs="+str(dict["obs"]) + " exp="+str(dict["exp-med"]))
        try:
            math.log10(dict["exp-1"]) + math.log10(dict["exp+1"])
        except ValueError:
            print("skipping imass "+str(imass))
            continue
       
        if args.fixedgrid:
            xindex, yindex = getdrawbin(imass)
            hObs.SetBinContent(xindex,yindex,math.log10(obs))
            hExp.SetBinContent(xindex,yindex,math.log10(exp))
            hExpLo.SetBinContent(xindex,yindex,math.log10(dict["exp-1"]))
            hExpHi.SetBinContent(xindex,yindex,math.log10(dict["exp+1"]))
            hObsXs.SetBinContent(xindex,yindex,obs*files.get_xsection(pmass))
        else:
            hObs.SetBinContent(windex+1,pindex+1,math.log10(obs))
            hExp.SetBinContent(windex+1,pindex+1,math.log10(exp))
            hExpLo.SetBinContent(windex+1,pindex+1,math.log10(dict["exp-1"]))
            hExpHi.SetBinContent(windex+1,pindex+1,math.log10(dict["exp+1"]))
            hObsXs.SetBinContent(windex+1,pindex+1,obs*files.get_xsection(pmass))

    nbins=50
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
    hObs.SetMinimum(PLOT_R_LOW)
    hObs.SetMaximum(PLOT_R_HIGH)

    obsCont=hObs.Clone("obsCont")
    obsCont.SetContour(2)
    obsCont.SetContourLevel(1,.0)
    obsCont.SetLineWidth(3)
    obsCont.SetLineColorAlpha(ROOT.kBlack,0.7)
    obsCont.SetLineStyle(ROOT.kDotted)
    obsCont.Draw("cont3same")
    ROOT.gPad.Update()
    
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
    
    can1.Update()
    can1.Draw()
    can1.SaveAs("resobs_"+args.sigtype+".pdf")

    print('DUMP Observed')
    nx = hObs.GetNbinsX()
    ny = hObs.GetNbinsY()
    for y in range(ny, 0, -1):  # last y-bin first
        row = [f"{hObs.GetBinContent(hObs.GetBin(x, y)):.3f}" for x in range(1, nx + 1)]
        print(" ".join(row))

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
    hExp.SetMinimum(PLOT_R_LOW)
    hExp.SetMaximum(PLOT_R_HIGH)

    expCont=hExp.Clone("expCont")
    expCont.SetContour(2)
    expCont.SetContourLevel(1,.0)
    expCont.SetLineWidth(3)
    expCont.SetLineColorAlpha(ROOT.kBlack,0.7)
    expCont.SetLineStyle(2)
    expCont.Draw("cont3same")
    ROOT.gPad.Update()

    hExpLo.SetContour(2)
    hExpLo.SetContourLevel(1,.0)
    hExpLo.SetLineWidth(2)
    hExpLo.SetLineColorAlpha(ROOT.kBlack,0.7)
    hExpLo.Draw("cont3same")
    hExpHi.SetContour(2)
    hExpHi.SetContourLevel(1,.0)
    hExpHi.SetLineWidth(2)
    hExpHi.SetLineColorAlpha(ROOT.kBlack,0.7)
    hExpHi.Draw("cont3same")


    cmstxt.DrawLatexNDC(0.15,0.87,"CMS")
    extratxt.DrawLatexNDC(0.26,0.87,"Preliminary")
    lumitxt.DrawLatexNDC(0.63,0.87,"138 fb^{-1} (13 TeV)")
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

    can2.Update()
    can2.Draw()
    can2.SaveAs("resexp_"+args.sigtype+".pdf")

    print('DUMP Expected')
    nx = hExp.GetNbinsX()
    ny = hExp.GetNbinsY()
    for y in range(ny, 0, -1):  # last y-bin first
        row = [f"{hExp.GetBinContent(hExp.GetBin(x, y)):.3f}" for x in range(1, nx + 1)]
        print(" ".join(row))

    # Draw xs limits
    can3 = ROOT.TCanvas()
    can3.SetFillColor(0)
    can3.SetFrameBorderMode(0)
    can3.SetTickx(0)
    can3.SetTicky(0)
    can3.SetMargin(0.15,0.20,0.15,0.15)
    can3.cd()
#    can3.SetLogz(True)
    hObsXs.Draw("colz")
    hObsXs.GetXaxis().SetTitle("m_{#omega} [GeV]")
    hObsXs.GetYaxis().SetTitle("m_{#phi} [GeV]")
    hObsXs.GetZaxis().SetTitle("95% CL Excluded #sigma#timesBR [pb]")
    hObsXs.SetMinimum(PLOT_XSBR_LOW)
    hObsXs.SetMaximum(PLOT_XSBR_HIGH)


    expCont.Draw("cont3same")
    obsCont.Draw("cont3same")
    hExpLo.Draw("cont3same")
    hExpHi.Draw("cont3same")

    cmstxt.DrawLatexNDC(0.15,0.87,"CMS")
    extratxt.DrawLatexNDC(0.26,0.87,"Preliminary")
    lumitxt.DrawLatexNDC(0.63,0.87,"138 fb^{-1} (13 TeV)")
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

    can3.Update()
    can3.Draw()
    can3.SaveAs("resobsxs_"+args.sigtype+".pdf")

    print('DUMP Observed xsec')
    nx = hObsXs.GetNbinsX()
    ny = hObsXs.GetNbinsY()
    for y in range(ny, 0, -1):  # last y-bin first
        row = [f"{hObsXs.GetBinContent(hObsXs.GetBin(x, y)):.3f}" for x in range(1, nx + 1)]
        print(" ".join(row))
