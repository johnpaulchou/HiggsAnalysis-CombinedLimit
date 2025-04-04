#!/bin/env python3

import makeworkspace as sf
import common.common as common
import common.tdrstyle as tdrstyle
import ROOT

###############################################################
# start of the "main" function
###############################################################

if __name__ == "__main__":


    # get the workspace
    ws = common.get_workspace_from_file(sf.fileoutname, sf.workspacename)
    
    ROOT.gStyle.SetErrorX(0)
    ROOT.gStyle.SetTitleFont(42)
    ROOT.gStyle.SetTitleFont(42, "XYZ")
    ROOT.gStyle.SetHistLineWidth(2)

    can=ROOT.TCanvas("c","c",300,300)
    can.cd()

    # get the observable from the workspace
    obs=ws.var("x")
    
    # get the data and corresponding variable
    datagraph,var=common.get_datagraph_from_workspace(ws, "data")

    # get the pdfs and their respective normalizations
    qcdPdf=ws.pdf("QCD_pdf")
    qcdNorm=ws.var("QCD_pdf_norm").getVal()
    nonQcdPdf=ws.pdf("nonQCD_pdf")
    nonQcdNorm=ws.var("nonQCD_pdf_norm").getVal()
    signalPdf=ws.pdf("signal_pdf")
    signalNorm=ws.var("signal_pdf_norm").getVal()

    print("qcdNorm="+str(qcdNorm))
    print("nonQcdNorm="+str(nonQcdNorm))
    print("signalNorm="+str(signalNorm))

    # turn the PDFs into histograms
    pdfhists = []
    pdfhisttitles = []
    pdfhists.append(common.pdf_to_histogram(qcdPdf, obs, var.getBinning(), "qcdPdfHist", qcdNorm))
    pdfhists.append(common.pdf_to_histogram(nonQcdPdf, obs, var.getBinning(), "nonQcdPdfHist", nonQcdNorm))
    pdfhists.append(common.pdf_to_histogram(signalPdf, obs, var.getBinning(), "signalPdfHist", signalNorm))
    pdfhisttitles.append("QCD")
    pdfhisttitles.append("W/Z+jets,non-#tau DY")
    pdfhisttitles.append("Z#rightarrow#tau#tau")

    
    stack=ROOT.THStack("stack","")
    for index,pdfhist in enumerate(pdfhists):
        pdfhist.SetFillColor(tdrstyle.colors[index])
        pdfhist.SetLineColor(ROOT.kBlack)
        pdfhist.SetLineWidth(1)
        stack.Add(pdfhist)

    can.SetFillColor(0)
    can.SetBorderMode(0)
    can.SetFrameFillStyle(0)
    can.SetFrameBorderMode(0)
    can.SetTickx(0)
    can.SetTicky(0)
    
    datagraph.GetXaxis().SetLabelSize(0.03)
    datagraph.SetMarkerSize(0.3)
    datagraph.SetMarkerStyle(20)
    datagraph.SetLineWidth(2)
    datagraph.GetXaxis().SetTitle("M(2p) [GeV]")
    datagraph.SetStats(0)
    datagraph.SetTitle("")
    datagraph.GetYaxis().SetTitle("Events/GeV")
    datagraph.GetYaxis().SetTitleSize(0.05)
    datagraph.SetMarkerColor(ROOT.kBlack)
    datagraph.SetLineColor(ROOT.kBlack)
    datagraph.SetMinimum(0)
    datagraph.Draw("APZ")
    
    stack.Draw("hist same")
    datagraph.Draw("PZ")
    can.RedrawAxis()

    leg=ROOT.TLegend(0.55,0.60,0.88,0.88)
    leg.SetBorderSize(0)
    leg.SetFillColor(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.035)
    leg.AddEntry(datagraph, "data", "ep")
    for index,pdfhist in enumerate(pdfhists):
        leg.AddEntry(pdfhist, pdfhisttitles[index], "f")
    leg.Draw()

    
    can.Modified()
    can.Update()            
    can.SaveAs("postfit.pdf")
    

