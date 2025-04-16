#!/bin/env python3

import common.tdrstyle as tdrstyle
import ROOT
import array as ar
import argparse
import makeworkspace as ttw
import math

tdrstyle.setTDRStyle()


def cross(x1, y1, x2, y2):
    return x1-(x2-x1)/math.log(y2/y1)*math.log(y1)


###############################################################
# start of the "main" function
###############################################################

if __name__ == "__main__":
    
    # setup parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("files", nargs="+", help="A list of root files")
    args = parser.parse_args()

    # setup output for printing
    pdffilename="./plots/limits.pdf"

    # setup data
    x = []
    ex = []
    obs = []
    e25 = []
    e16 = []
    e50 = []
    e84 = []
    e97 = []
    
    # loop over the files that are passed to the command line
    for filename in args.files:

        dict = parse_HC_limit_tree(filename)

        # convert mass into an integer
        imass=int(dict["mass"])
        
        # skip the 850 MeV mass point
        if imass==2: continue
        
        # start filling in data
        x.append(float(ttw.sigmasses[imass][1:])/1000.)
        ex.append(0.1)
        e25.append(dict["exp-2"])
        e16.append(dict["exp-1"])
        e50.append(dict["exp-med"])
        e84.append(dict["exp+1"])
        e97.append(dict["exp+2"])
        obs.append(dict["obs"])

    # edit the contents for plotting
    for i in range(len(x)):
        e25[i]=e50[i]-e25[i]
        e16[i]=e50[i]-e16[i]
        e84[i]=e84[i]-e50[i]
        e97[i]=e97[i]-e50[i]

    # determine the point where the observed and expected crosses mu=1
    for i in range(len(x)-1):
        if obs[i]<1. and obs[i+1]>1.:
            print("observed crosses mu=1.0 at "+str(cross(x[i],obs[i],x[i+1],obs[i+1])))
        if e50[i]<1. and e50[i+1]>1.:
            print("expected crosses mu=1.0 at "+str(cross(x[i],e50[i],x[i+1],e50[i+1])))
    
        
    # draw the plots
    g = ROOT.TGraphErrors(len(x), ar.array('d',x),  ar.array('d',obs))
    gexp = ROOT.TGraphErrors(len(x), ar.array('d',x), ar.array('d',e50))
    ge1 = ROOT.TGraphAsymmErrors(len(x), ar.array('d',x),  ar.array('d',e50), ar.array('d',ex), ar.array('d',ex), ar.array('d',e16), ar.array('d',e84))
    ge2 = ROOT.TGraphAsymmErrors(len(x), ar.array('d',x),  ar.array('d',e50), ar.array('d',ex), ar.array('d',ex), ar.array('d',e25), ar.array('d',e97))

    can = ROOT.TCanvas("limits","limits",500,500)
    can.cd()
    can.SetMargin(0.16,0.05,0.15,0.10)
    ge2.SetFillColor(ROOT.TColor.GetColor("#F5BB54"))
    ge2.SetFillStyle(1001)
    ge2.Draw("a3")
    ge2.SetMinimum(0.01)
    ge2.SetMaximum(8.0)
    ge2.GetXaxis().SetTitle("m_{#omega} [GeV]")
    ge2.GetXaxis().SetRangeUser(x[0],x[len(x)-1])
    ge2.GetYaxis().SetTitle("95% C.L. Lower limit on #mu")
    ge1.SetFillColor(ROOT.TColor.GetColor("#607641"))
    ge1.SetFillStyle(1001)
    ge1.Draw("Same3l")
    gexp.SetLineStyle(2)
    gexp.Draw("SAME L")
    g.Draw("SAME LP")
    ROOT.gPad.SetLogy()

    leg = ROOT.TLegend(0.5,0.20,0.9,0.38)
    leg.SetBorderSize(0)
    leg.SetFillColor(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.04)
    leg.AddEntry(g, "Observed", "LP")
    leg.AddEntry(gexp, "Median Expected", "L")
    leg.AddEntry(ge1, "68% Expected", "F")
    leg.AddEntry(ge2, "95% Expected", "F")
    leg.Draw()

    # Write CMS stuff
    cmstxt = ROOT.TLatex()
    cmstxt.SetTextFont(61)
    cmstxt.SetTextSize(0.07)
    cmstxt.DrawLatexNDC(0.16,0.91,"CMS")
    extratxt = ROOT.TLatex()
    extratxt.SetTextFont(52)
    extratxt.SetTextSize(0.05)
    extratxt.DrawLatexNDC(0.31,0.91,"Preliminary")
    lumitxt = ROOT.TLatex()
    lumitxt.SetTextFont(42)
    lumitxt.SetTextSize(0.05)
    lumitxt.DrawLatexNDC(0.65,0.91,"138 fb^{-1} (13 TeV)")
    
    brtxt = ROOT.TLatex()
    brtxt.SetTextFont(42)
    brtxt.SetTextSize(0.04)
    brtxt.DrawLatexNDC(0.25,0.20,"#eta BRs")

    # Draw horizontal line
    line=ROOT.TLine(x[0],1.0,x[len(x)-1],1.0)
    line.SetLineWidth(2)
    line.SetLineStyle(3)
    line.Draw()
    
    can.Update()
    can.Draw()
    can.Print(pdffilename)


