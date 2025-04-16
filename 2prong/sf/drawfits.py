#!/bin/env python3

import argparse
import makeworkspace as sf
import common.common as common
import common.tdrstyle as tdrstyle
import ROOT

channels = ["ch1", "ch2", "ch3", "ch4"]
channelTitles = ["p_{T}=20-30 GeV","p_{T}=30-40 GeV","p_{T}=40-50 GeV","p_{T}=50-60 GeV"]

###############################################################
# start of the "main" function
###############################################################

if __name__ == "__main__":

    # setup and use the parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("workspacefn", help="root file containing the workspace to draw")
    parser.add_argument("--year", help="data year the file comes from")
    args=parser.parse_args()

    # get the workspace
    ws = common.get_workspace_from_file(args.workspacefn, "w")

    # load snapshot
    ws.loadSnapshot("MultiDimFit")
    
    ROOT.gStyle.SetErrorX(0)
    ROOT.gStyle.SetTitleFont(42)
    ROOT.gStyle.SetTitleFont(42, "XYZ")
    ROOT.gStyle.SetHistLineWidth(2)

    # get the observable from the workspace
    obs=ws.var("m2p")

    for channelIndex,channel in enumerate(channels):

        # get the data and corresponding variable
        datagraph,var=common.get_datagraph_from_workspace(ws, "data_obs","CMS_channel==CMS_channel::"+channel)

        # get the background and signal pdfs
        bpdf=ws.pdf("shapeBkg_bkg_"+channel)
        spdf=ws.pdf("shapeSig_sig_"+channel)
        bpdfnorm=ws.var("shapeBkg_bkg_"+channel+"__norm").getVal()
        spdfnorm=ws.var("shapeSig_sig_"+channel+"__norm").getVal()

        # turn the PDFs into histograms
        bkghist=common.pdf_to_histogram(bpdf, obs, var.getBinning(), "bkghist"+channel, bpdfnorm)
        sighist=common.pdf_to_histogram(spdf, obs, var.getBinning(), "sighist"+channel, spdfnorm)

        # calculate the pulls
        pull=datagraph.Clone(datagraph.GetName()+"_pull")
        sigpullhist = sighist.Clone(sighist.GetName()+"_pull")
            
        for i in range(pull.GetN()):
            N = datagraph.GetPointY(i)
            errup=datagraph.GetErrorYhigh(i)
            errlo=datagraph.GetErrorYlow(i)
            pred=bkghist.GetBinContent(i+1) # needs to be offset by one here
            # compute central point
            if N<pred:   pullval=(N-pred)/errup
            elif N>pred: pullval=(N-pred)/errlo
            else:        pullval=0
            pull.SetPointY(i, pullval)
            pull.SetPointEYhigh(i,1)
            pull.SetPointEYlow(i,1)

            # compute sigpullhist stuff
            sig=sigpullhist.GetBinContent(i+1) # needs to be offset by one here
            if N<pred:         sigpullhist.SetBinContent(i+1,sig/errup)
            elif N>(pred+sig): sigpullhist.SetBinContent(i+1,sig/errlo)
            elif errlo>0:      sigpullhist.SetBinContent(i+1, (N-pred)/errlo+(sig+pred-N)/errup)
            else:              sigpullhist.SetBinContent(i+1, (sig+pred-N)/errup)

        
        # create the canvas
        can=ROOT.TCanvas(channel,"c",300,300)
        can.cd()
        pad = ROOT.TPad("pad"+channel,"pad"+channel,0,0.25,1,1)
        pad.SetMargin(0.15,0.08,0.02,0.1) #L, R, B, T
        pad.Draw()
        pullpad = ROOT.TPad("pullpad"+channel,"pullpad"+channel,0,0,1,0.25)
        pullpad.SetMargin(0.15,0.08,0.3,0.02) #L, R, B, T
        pullpad.SetTickx()
        pullpad.Draw()
        
        can.SetFillColor(0)
        can.SetBorderMode(0)
        can.SetFrameFillStyle(0)
        can.SetFrameBorderMode(0)
        can.SetTickx(0)
        can.SetTicky(0)

        datagraph.GetXaxis().SetLabelSize(0)
        datagraph.SetMarkerSize(0.3)
        datagraph.SetMarkerStyle(20)
        datagraph.SetLineWidth(2)
        datagraph.GetXaxis().SetTitle("")
        datagraph.SetStats(0)
        datagraph.SetTitle("")
        datagraph.GetYaxis().SetTitle("Events/GeV")
        datagraph.GetYaxis().SetTitleSize(0.05)
        datagraph.SetMarkerColor(ROOT.kBlack)
        datagraph.SetLineColor(ROOT.kBlack)
        

        pull.SetMarkerSize(0.3)
        pull.SetMarkerStyle(20)
        pull.SetLineWidth(2)
        pull.GetXaxis().SetTitle("M(2p) [GeV]")
        pull.GetXaxis().SetLabelSize(0.13)
        pull.GetXaxis().SetTitleSize(0.13)
        pull.GetXaxis().SetTitleOffset(0.75)
        pull.SetStats(0)
        pull.SetTitle("")
        pull.GetYaxis().SetTitle("#frac{data-pred.}{error}")
        pull.GetYaxis().SetTitleSize(0.13)
        pull.GetYaxis().SetLabelSize(0.13)
        pull.GetYaxis().SetTitleOffset(0.33)
        pull.GetYaxis().SetNdivisions(5, 5, 0)
        pull.GetYaxis().CenterTitle(True)
        pull.SetMarkerColor(ROOT.kBlack)
        pull.SetLineColor(ROOT.kBlack)
        pull.GetXaxis().SetRangeUser(var.getBinning().binLow(0),var.getBinning().binHigh(var.getBinning().numBins()-1))

        # Draw things
        pad.cd()
        datagraph.Draw("APZ")
        stack=ROOT.THStack("stack","")
        stack.Add(bkghist)
        stack.Add(sighist)
        sighist.SetFillColor(tdrstyle.colors[2])
        sighist.SetLineColor(ROOT.kBlack)
        bkghist.SetFillColor(tdrstyle.colors[1])
        bkghist.SetLineColor(ROOT.kBlack)
        stack.Draw("hist same")
        datagraph.Draw("PZ") # draw a 2nd time on top
        pad.RedrawAxis() # redraw the tick marks

        # Write text
        cmstxt = ROOT.TLatex()
        cmstxt.SetTextFont(61)
        cmstxt.SetTextSize(0.07)
        cmstxt.DrawLatexNDC(0.15,0.915,"CMS")
        extratxt = ROOT.TLatex()
        extratxt.SetTextFont(52)
        extratxt.SetTextSize(0.05)
        extratxt.DrawLatexNDC(0.25,0.915,"Preliminary")
        lumitxt = ROOT.TLatex()
        lumitxt.SetTextFont(42)
        lumitxt.SetTextSize(0.05)
        if args.year=="2018":
            lumitxt.DrawLatexNDC(0.68,0.915,"59 fb^{-1} (13 TeV)")
        txt = ROOT.TLatex()
        txt.SetTextFont(42)
        txt.SetTextSize(0.05)
        txt.DrawLatexNDC(0.70,0.80,channelTitles[channelIndex])
        
        # Draw legend
        leg=ROOT.TLegend(0.65,0.40,0.90,0.70)
        leg.SetBorderSize(0)
        leg.SetFillColor(0)
        leg.SetTextFont(42)
        leg.SetTextSize(0.04)
        leg.AddEntry(datagraph, "data", "ep")
        leg.AddEntry(sighist, "Z#rightarrow#mu#tau_{h}","lf")
        leg.AddEntry(bkghist, "backgrounds", "lf")
        leg.Draw()

        # Draw pulls
        pullpad.cd()
        pull.Draw("APZ")
        sigpullhist.SetLineColor(tdrstyle.colors[2])
        sigpullhist.Draw("same")
        line = ROOT.TLine()
        line.SetNDC(False)
        line.SetX1(var.getBinning().binLow(0))
        line.SetX2(var.getBinning().binHigh(var.getBinning().numBins()-1))
        line.SetY1(0)
        line.SetY2(0)
        line.SetLineWidth(1)
        line.SetLineColor(tdrstyle.colors[3])
        line.SetLineStyle(3)
        line.Draw()

        can.Modified()
        can.Update()
        can.SaveAs("./plots/"+channel+"_"+args.year+".pdf")

