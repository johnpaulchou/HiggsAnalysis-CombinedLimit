#!/bin/env python3

import ROOT
import files
import argparse
import common.tdrstyle as tdrstyle
import common.common as common
import makesigworkspace as ws
import shlex

def getExtrema(hists, projx=True):

    if projx:
        hmax=hists[0].ProjectionX().Clone("hmax")
        hmin=hists[0].ProjectionX().Clone("hmin")
        hextre=hists[0].ProjectionX().Clone("hextre")
    else:
        hmax=hists[0].ProjectionY().Clone("hmax")
        hmin=hists[0].ProjectionY().Clone("hmin")
        hextre=hists[0].ProjectionY().Clone("hextre")

    for bin in range(hmax.GetNbinsX()+1):
        hmax.SetBinContent(bin, -999.)
        hmin.SetBinContent(bin, 999.)

    for hist in hists:
        if projx: h=hist.ProjectionX()
        else:     h=hist.ProjectionY()

        h.Scale(1.0 / h.Integral())

        for bin in range(h.GetNbinsX()+1):
            val=h.GetBinContent(bin)
            if val>hmax.GetBinContent(bin):
                hmax.SetBinContent(bin, val)
            if val<hmin.GetBinContent(bin):
                hmin.SetBinContent(bin, val)

    for bin in range(hmin.GetNbinsX()+1):
        minval=hmin.GetBinContent(bin)
        maxval=hmax.GetBinContent(bin)
        hextre.SetBinContent(bin, 0.5*(minval+maxval))
        hextre.SetBinError(bin, 0.5*(maxval-minval))

    return hextre


###### main function ######
if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--doBarrel', help="whether or not to run over the barrel or endcap", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument('--projectX', help="do the x-axis projection (or do the y-axis projection)", action=argparse.BooleanOptionalAction, default=True)
    args=parser.parse_args()

    # run the makesigworkspace script for a wmass=1.5 GeV and omass=1500 GeV to compare against the other file
    ws.main(shlex.split('--fixmasses 1.5 1500. --sigtype eta'))

    if args.doBarrel: region="barrel"
    else:             region="endcap"
    
    sigws = common.get_workspace_from_file(files.sigworkspacefn, files.workspacename)
    sigtype = common.get_tnamed_title_from_file(files.sigworkspacefn, "sigtype")

    ROOT.gStyle.SetTitleFont(42)
    ROOT.gStyle.SetTitleFont(42, "XYZ")
    ROOT.gStyle.SetHistLineWidth(2)
    
    h2dOrig=common.get_TH1_from_file("input/signal_2x2boxextra_1500_1p5_10k_events.root", "plots/recomass_"+region)

    h2dMorph=[]

    for syst in files.systs:
        h2dMorph.append(common.get_TH1_from_file(files.sigworkspacefn, "recomass_"+region+syst+"m"))

    if args.projectX:
        bcan=ROOT.TCanvas("sig_m2p_"+region+"_"+sigtype,"signal",300,300)
    else:
        bcan=ROOT.TCanvas("sig_m2pg_"+region+"_"+sigtype,"signal",300,300)
    bcan.cd()

    if args.projectX:
        h1d=h2dOrig.ProjectionX('h1d')
        h1d.GetXaxis().SetTitle("M(2p) GeV")
    else:
        h1d=h2dOrig.ProjectionY('h1d')
        h1d.GetXaxis().SetTitle("M(2p#gamma) GeV")
    h1d.SetLineColor(ROOT.kBlack)
    h1d.SetLineWidth(2)
    h1d.SetTitle('')
    h1d.SetStats(0)
    h1d.DrawNormalized('E0')

    if args.projectX: hinter=h2dMorph[0].ProjectionX('hinter')
    else:             hinter=h2dMorph[0].ProjectionY('hinter')
    hinter.SetLineColor(ROOT.kBlue)
    hinter.SetLineWidth(2)
    hinter.Scale(1.0 / hinter.Integral())
    hinter.Draw('HIST same')

    hextre=getExtrema(h2dMorph, args.projectX)
    hextre.SetLineColor(ROOT.kBlue)
    hextre.SetLineWidth(2)
    hextre.SetFillColorAlpha(ROOT.kBlue, 0.3)  # transparent gray shading
    hextre.SetStats(0)
    hextre.Draw("E2 same")

    leg = ROOT.TLegend(0.65, 0.75, 0.88, 0.88)
    leg.SetBorderSize(0)
    leg.SetFillColor(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.04)
    leg.AddEntry(h1d, "Generated", "l")
    leg.AddEntry(hextre, "Interpolated", "lf")
    leg.Draw()

    bcan.Update()
    bcan.SaveAs("./plots/"+bcan.GetName()+".pdf")


