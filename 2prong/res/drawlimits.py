#!/bin/env python3

import ROOT
import common.tdrstyle as tdrstyle
import re
import files
import sys
import math
import files
import os

tdrstyle.setTDRStyle()


def parsefile(filename, hSig, hObs, hExp):
    sig = -1
    obs = -1
    exp = -1
    result=re.findall(r'\d+', os.path.basename(filename))
    jobid=int(result[1])
    windex,pindex=files.indexpair(jobid)
    wmass=files.wmasspoints[windex]
    pmass=files.pmasspoints[pindex]
    with open(filename, 'r') as file:
        for line in file:
            split = line.strip().split(' ')
            if split[0]=="Significance:":
                sig = float(split[1])
            elif split[0]=="Observed" and split[1]=="Limit:":
                obs = float(split[4])
            elif split[0]=="Expected" and split[1]=="50.0%:":
                exp = float(split[4])
    if sig>-1: hSig.Fill(wmass,pmass,sig)
    if obs>-1: hObs.Fill(wmass,pmass,math.log10(obs))
    if exp>-1: hExp.Fill(wmass,pmass,math.log10(exp))

# start by collecting the data from the files listed
if __name__ == "__main__":
    if len(sys.argv)<2:
        print("plotlimits.py logfiles")
        exit(1)

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
    hObs = ROOT.TH2D("hObs","Observed",xbinsn,xbinslo,xbinshi,ybinsn,ybinslo,ybinshi)
    hExp = ROOT.TH2D("hExp","Expected",xbinsn,xbinslo,xbinshi,ybinsn,ybinslo,ybinshi)
       
    # loop over all of the arguments
    for arg in sys.argv:

        # skip the first argument
        if arg==sys.argv[0]: continue

        # fill the histograms with the info
        parsefile(arg, hSig, hObs, hExp)


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
    
    can2.Update()
    can2.Draw()
    can2.SaveAs("resexp.pdf")


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
