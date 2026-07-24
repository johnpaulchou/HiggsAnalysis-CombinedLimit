#!/bin/env python3

import ROOT
import common.tdrstyle as tdrstyle
import common.common as common
import files
import math
import argparse
import sys

tdrstyle.setTDRStyle()

###############################################################
# start of the "main" function
###############################################################

if __name__ == "__main__":

    # setup parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("filenames", nargs="+", help="A list of root files containing the limit info")
    parser.add_argument("--drawSmooth",help="Draw a smoothed version of the limit plot",action=argparse.BooleanOptionalAction,default=False)
    parser.add_argument("--coarse",help="Draw a smoothed version of the contours",action=argparse.BooleanOptionalAction,default=False)
    parser.add_argument("--suppressPoints", type=int, nargs="*", help="Observed points to suppress (set them to the expected)")
    parser.add_argument("--sigtype",help="signal type that we're using",choices=files.sigtypes, default=files.sigtypes[0])
    parser.add_argument("--fixedgrid",action='store_true', default=False)
    parser.add_argument("--massage",action='store_true', default=False)
    parser.add_argument("--Obs",action='store_true', default=False)
    parser.add_argument("--Obsxs",action='store_true', default=False)
    parser.add_argument("--Exp",action='store_true', default=False)
    parser.add_argument("--showGen",action='store_true', default=False)
    parser.add_argument("-s", "--save",action='store_true', default=True)
    args = parser.parse_args()
    if not args.Obs and not args.Obsxs and not args.Exp: args.Obs, args.Obsxs, args.Exp = True, True, True

    # constants
    PLOT_R_LOW = -2.05
    PLOT_R_HIGH = 2.5
    PLOT_XSBR_LOW = 0
    PLOT_XSBR_HIGH = 20
    fixedxlo_eta, fixedxhi_eta = 0.5, 3.95
    fixedxlo_etaprime, fixedxhi_etaprime = 0.95, 3.95
    fixedylo, fixedyhi = 550, 2920
    points = [
    (2, 30),
    (14, 21),
    (14, 18),
    (19, 19),
    (17, 17),
    ]
    massage = args.massage
    if args.sigtype == files.sigtypes[0]: # eta
        nbinsx_smooth=12
        nbinsy_smooth=40
    if args.sigtype == files.sigtypes[1]: # etaprime
        nbinsx_smooth=16
        nbinsy_smooth=45

    # create histograms
    if args.fixedgrid:
        xbinsw = (files.wmasspoints[1]-files.wmasspoints[0])
        ybinsw = (files.pmasspoints[1]-files.pmasspoints[0])
        if args.sigtype == files.sigtypes[0]: xbinslo, xbinshi = fixedxlo_eta, fixedxhi_eta
        if args.sigtype == files.sigtypes[1]: xbinslo, xbinshi = fixedxlo_etaprime, fixedxhi_etaprime
        ybinslo, ybinshi = fixedylo, fixedyhi
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

    hGen = ROOT.TH2D("hGen","Generated Masspoints",xbinsn,xbinslo,xbinshi,ybinsn,ybinslo,ybinshi)
    hObs = ROOT.TH2D("hObs","Observed",xbinsn,xbinslo,xbinshi,ybinsn,ybinslo,ybinshi)
    hExp = ROOT.TH2D("hExp","Expected",xbinsn,xbinslo,xbinshi,ybinsn,ybinslo,ybinshi)
    hExpLo = ROOT.TH2D("hExpLo","Expected -1 sigma",xbinsn,xbinslo,xbinshi,ybinsn,ybinslo,ybinshi)
    hExpHi = ROOT.TH2D("hExpHi","Expected +1 sigma",xbinsn,xbinslo,xbinshi,ybinsn,ybinslo,ybinshi)
    hObsXs = ROOT.TH2D("hObsXs","Observed XS",xbinsn,xbinslo,xbinshi,ybinsn,ybinslo,ybinshi)
    if args.showGen:
        for imass, entry in enumerate(files.genfilenames_raw):
            if not entry=='':
                xindex, yindex = getdrawbin(imass)
                hGen.SetBinContent(xindex,yindex,0.1)
   
    # process files
    print(f"X Binning: {xbinsw} wide from {xbinslo} to {xbinshi}, {xbinsn} total")
    print(f"Y Binning: {ybinsw} wide from {ybinslo} to {ybinshi}, {ybinsn} total")
    def getdrawbin(imass):
        wmass, pmass = files.indexmasses(imass)
        xbin = hObs.GetXaxis().FindBin(wmass)
        ybin = hObs.GetYaxis().FindBin(pmass)
        return xbin, ybin
    for file in args.filenames:
        #print(file)
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

    # Drawing Prep
    if args.drawSmooth:
        hObs=common.interpolate_th2d(hObs, nbinsx_smooth, nbinsy_smooth)
        hExp=common.interpolate_th2d(hExp, nbinsx_smooth, nbinsy_smooth)
        hExpLo=common.interpolate_th2d(hExpLo, nbinsx_smooth, nbinsy_smooth)
        hExpHi=common.interpolate_th2d(hExpHi, nbinsx_smooth, nbinsy_smooth)
        hObsXs=common.interpolate_th2d(hObsXs, nbinsx_smooth, nbinsy_smooth)

    hObs_draw=hObs.Clone("hObs_draw")
    if massage:
        files.massage(hObs_draw, "sideband_eta")
        '''
        for point in points:
            xcor, ycor = point
            neighbor = hObs_draw.GetBinContent(xcor,ycor+1)
            current = hObs_draw.GetBinContent(xcor,ycor)
            print(f"replace {current} with {neighbor}")
            hObs_draw.SetBinContent(xcor,ycor,neighbor)
        '''
    if args.coarse:
        obsCont=common.interpolate_th2d(hObs_draw, nbinsx_smooth, nbinsy_smooth)
    else:
        obsCont=hObs_draw.Clone("obsCont")
    obsCont.SetContour(2)
    obsCont.SetContourLevel(1,.0)
    obsCont.SetLineWidth(3)
    obsCont.SetLineColorAlpha(ROOT.kBlack,0.7)
    obsCont.SetLineStyle(ROOT.kDotted)

    if args.coarse:
        expCont=common.interpolate_th2d(hExp, nbinsx_smooth, nbinsy_smooth)
        expContLo=common.interpolate_th2d(hExpLo, nbinsx_smooth, nbinsy_smooth)
        expContHi=common.interpolate_th2d(hExpHi, nbinsx_smooth, nbinsy_smooth)
    else:
        expCont=hExp.Clone("expCont")
        expContLo=hExpLo.Clone("expCont")
        expContHi=hExpHi.Clone("expCont")
    expCont.SetContour(2)
    expCont.SetContourLevel(1,.0)
    expCont.SetLineWidth(3)
    expCont.SetLineColorAlpha(ROOT.kBlack,0.7)
    expCont.SetLineStyle(2)
    expContLo.SetContour(2)
    expContLo.SetContourLevel(1,.0)
    expContLo.SetLineWidth(2)
    expContLo.SetLineColorAlpha(ROOT.kBlack,0.7)
    expContHi.SetContour(2)
    expContHi.SetContourLevel(1,.0)
    expContHi.SetLineWidth(2)
    expContHi.SetLineColorAlpha(ROOT.kBlack,0.7)

    cmstxt = ROOT.TLatex()
    cmstxt.SetTextFont(61)
    cmstxt.SetTextSize(0.07)
    extratxt = ROOT.TLatex()
    extratxt.SetTextFont(52)
    extratxt.SetTextSize(0.05)
    lumitxt = ROOT.TLatex()
    lumitxt.SetTextFont(42)
    lumitxt.SetTextSize(0.05)
    sigtxt = ROOT.TLatex()
    sigtxt.SetTextFont(42)
    sigtxt.SetTextSize(0.03)

    # Draw observed limits
    if args.Obs:
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

        obsCont.Draw("cont3same")
        ROOT.gPad.Update()
        
        cmstxt.DrawLatexNDC(0.15,0.87,"CMS")
        extratxt.DrawLatexNDC(0.26,0.87,"Preliminary")
        lumitxt.DrawLatexNDC(0.63,0.87,"138 fb^{-1} (13 TeV)")
        if args.sigtype==files.sigtypes[0]:
            sigtxt.DrawLatexNDC(0.18,0.75,"#eta BR hypothesis")
        else:
            sigtxt.DrawLatexNDC(0.18,0.75,"#eta' BR hypothesis")

        if args.showGen:
            hGen.SetMarkerStyle(5)
            hGen.SetMarkerColor(7)
            hGen.SetFillColor(7)
            hGen.Draw("box same")
        
        can1.Update()
        can1.Draw()
        print('DUMP Observed')
        nx = hObs.GetNbinsX()
        ny = hObs.GetNbinsY()
        for y in range(ny, 0, -1):  # last y-bin first
            row = [f"{hObs.GetBinContent(hObs.GetBin(x, y)):.3f}" for x in range(1, nx + 1)]
            print(" ".join(row))
        if args.save: can1.SaveAs("resobs_"+args.sigtype+".pdf")

    # Draw Expected limits
    if args.Exp:
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

        expCont.Draw("cont3same")
        expContLo.Draw("cont3same")
        expContHi.Draw("cont3same")
        ROOT.gPad.Update()

        cmstxt.DrawLatexNDC(0.15,0.87,"CMS")
        extratxt.DrawLatexNDC(0.26,0.87,"Preliminary")
        lumitxt.DrawLatexNDC(0.63,0.87,"138 fb^{-1} (13 TeV)")
        if args.sigtype==files.sigtypes[0]:
            sigtxt.DrawLatexNDC(0.18,0.75,"#eta BR hypothesis")
        else:
            sigtxt.DrawLatexNDC(0.18,0.75,"#eta' BR hypothesis")
        
        if args.showGen:
            hGen.SetMarkerStyle(5)
            hGen.SetMarkerColor(7)
            hGen.SetFillColor(7)
            hGen.Draw("box same")

        can2.Update()
        can2.Draw()
        print('DUMP Expected')
        nx = hExp.GetNbinsX()
        ny = hExp.GetNbinsY()
        for y in range(ny, 0, -1):  # last y-bin first
            row = [f"{hExp.GetBinContent(hExp.GetBin(x, y)):.3f}" for x in range(1, nx + 1)]
            print(" ".join(row))
        can2.SaveAs("resexp_"+args.sigtype+".pdf")

    # Draw xs limits
    if args.Obsxs:
        can3 = ROOT.TCanvas()
        can3.SetFillColor(0)
        can3.SetFrameBorderMode(0)
        can3.SetTickx(0)
        can3.SetTicky(0)
        can3.SetMargin(0.15,0.20,0.15,0.15)
        can3.cd()
        # can3.SetLogz(True)
        hObsXs.Draw("colz")
        hObsXs.GetXaxis().SetTitle("m_{#omega} [GeV]")
        hObsXs.GetYaxis().SetTitle("m_{#phi} [GeV]")
        hObsXs.GetZaxis().SetTitle("95% CL Excluded #sigma#timesBR [pb]")
        hObsXs.SetMinimum(PLOT_XSBR_LOW)
        hObsXs.SetMaximum(PLOT_XSBR_HIGH)

        expCont.Draw("cont3same")
        obsCont.Draw("cont3same")
        expContLo.Draw("cont3same")
        expContHi.Draw("cont3same")

        cmstxt.DrawLatexNDC(0.15,0.87,"CMS")
        extratxt.DrawLatexNDC(0.26,0.87,"Preliminary")
        lumitxt.DrawLatexNDC(0.63,0.87,"138 fb^{-1} (13 TeV)")
        if args.sigtype==files.sigtypes[0]:
            sigtxt.DrawLatexNDC(0.18,0.75,"#eta BR hypothesis")
        else:
            sigtxt.DrawLatexNDC(0.18,0.75,"#eta' BR hypothesis")
        
        if args.showGen:
            hGen.SetMarkerStyle(5)
            hGen.SetMarkerColor(7)
            hGen.SetFillColor(7)
            hGen.Draw("box same")

        can3.Update()
        can3.Draw()
        print('DUMP Observed xsec')
        nx = hObsXs.GetNbinsX()
        ny = hObsXs.GetNbinsY()
        for y in range(ny, 0, -1):  # last y-bin first
            row = [f"{hObsXs.GetBinContent(hObsXs.GetBin(x, y)):.3f}" for x in range(1, nx + 1)]
            print(" ".join(row))
        can3.SaveAs("resobsxs_"+args.sigtype+".pdf")
