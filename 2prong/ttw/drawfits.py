#!/bin/env python3

import argparse
import makeworkspace as ttw
import common.common as common
import common.tdrstyle as tdrstyle
import ROOT

###############################################################
# start of the "main" function
###############################################################

if __name__ == "__main__":

    # setup and use the parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--drawSignal",help="Draw the signal on top of the background. If so, make sure to specify which background index to drop on top of. If not, it draws all background fits instead.",action=argparse.BooleanOptionalAction,default=True)
    parser.add_argument("--drawSpline",help="Draw the spline in the pull area.",action=argparse.BooleanOptionalAction,default=False)
    parser.add_argument("--drawChisq",help="Print the chi^2 on the plots and create the chi^2 probability histogram.",action=argparse.BooleanOptionalAction,default=True)
    parser.add_argument("--sigScale",help="How to scale the signal, if drawn.",type=float,default=1.0)
    parser.add_argument("--bkgIndex",help="Which background to compute the pull and chi^2 with respect to and/or plot the signal on top of.",type=int,choices=[0,1],default=1)
    parser.add_argument("--drawBkgUncertainty",help="Draw the uncertainty on the background fit. Note this takes can be slow and only works when bkgIndex=1",action=argparse.BooleanOptionalAction,default=False)
    args=parser.parse_args()

    # setup bin titles
    pttitles = ["=20-40", "=40-60", "=60-80", "=80-100", "=100-140", "=140-180", "=180-220", "=220-300", "=300-380", ">380" ]
    btagtitles = ["=1 b tag", "#kern[0.2]{#geq}#kern[-0.1]{2} b tags" ]
    assert len(pttitles)==len(ttw.ptbins), "pttitles and ptbins lengths don't match"
    assert len(btagtitles)==len(ttw.btagbins), "btagtitles and btagbins lengths don't match"

    # get the workspace
    ws = common.get_workspace_from_file(ttw.fileoutname, ttw.workspacename)

    # get the parameters
    sigmass = common.get_tnamed_title_from_file(ttw.fileoutname, "sigmass")
    sigtype = common.get_tnamed_title_from_file(ttw.fileoutname, "sigtype")
    region  = common.get_tnamed_title_from_file(ttw.fileoutname, "region")
    
    ROOT.gStyle.SetErrorX(0)
    ROOT.gStyle.SetTitleFont(42)
    ROOT.gStyle.SetTitleFont(42, "XYZ")
    ROOT.gStyle.SetHistLineWidth(2)
    sigcolorindex=5

    # create the chi^2 prob histogram
    hChisqProb=ROOT.TH1D("hChisqProb","#chi^{2} Probability",8,0,1)    
    
    # loop over the b tags
    for btagindex, btagbin in enumerate(ttw.btagbins):

        # loop over pt bins
        for ptindex, ptbin in enumerate(ttw.ptbins):
            
            # create the canvas and subdivide into a top and bottom pad
            can=ROOT.TCanvas("fits_"+region+"_"+btagbin+"_"+ptbin, "c_"+btagbin+"_"+ptbin,300,300)
            can.cd()
            pad = ROOT.TPad("pad"+ptbin,"pad"+ptbin,0,0.25,1,1)
            pad.SetMargin(0.15,0.08,0.02,0.1) #L, R, B, T
            pad.Draw()
            pullpad = ROOT.TPad("pullpad"+ptbin,"pullpad"+ptbin,0,0,1,0.25)
            pullpad.SetMargin(0.15,0.08,0.3,0.02) #L, R, B, T
            pullpad.SetTickx()
            pullpad.Draw()

            # get the roodatahist and corresponding variable, then create a TH1 from it
            datagraph,var=common.get_datagraph_from_workspace(ws, "data_"+btagbin+"_"+ptbin)
            
            # get the template and signal pdfs and their respective normalizations
            pdf0=ws.pdf("temp_"+btagbin+"_"+ptbin+"_pdf0")
            pdf1=ws.pdf("temp_"+btagbin+"_"+ptbin+"_pdf1")
            sig=ws.pdf("sig_"+btagbin+"_"+ptbin+"_pdf")
            pdf0norm=ws.var("temp_"+btagbin+"_"+ptbin+"_pdf0_norm")
            pdf1norm=ws.var("temp_"+btagbin+"_"+ptbin+"_pdf1_norm")
            signorm=ws.var("sig_"+btagbin+"_"+ptbin+"_pdf_norm")
            
            # turn the PDFs into histograms
            pdfhists = []
            pdfhisttitles = []
            pdfhists.append(common.pdf_to_histogram(pdf0, var.getBinning(), "temp_"+btagbin+"_"+ptbin+"_pdf0hist", pdf0norm.getVal()))
            pdfhists.append(common.pdf_to_histogram(pdf1, var.getBinning(), "temp_"+btagbin+"_"+ptbin+"_pdf1hist", pdf1norm.getVal()))
            pdfhisttitles.append("background")
            pdfhisttitles.append("post-fit bkg.")
            sighist = common.pdf_to_histogram(sig, var.getBinning(), "sig_"+btagbin+"_"+ptbin+"_pdfhist", signorm.getVal()*args.sigScale) # scale signal to an arbitrary value

            # compute the uncertainty on the background fit (right now, this hard-coded for pdf1)
            if args.drawBkgUncertainty:
                fitresult=ws.obj("fitresult_temp_"+btagbin+"_"+ptbin+"_pdf1_data_"+btagbin+"_"+ptbin)
                if not fitresult: raise RuntimeError(f"Cannot get fitresult")
                bkg_uncertainties=common.monte_carlo_uncertainty_envelope(pdf1, pdf1norm.getVal(), fitresult, var.getBinning())
            
            # compute the pull graph and chi^2
            pull=datagraph.Clone(datagraph.GetName()+"_pull")
            sigpullhist = sighist.Clone(sighist.GetName()+"_pull")
            bkguncertaintypull=ROOT.TGraphErrors(var.getBinning().numBins())
            
            chisq=0
            ndof=0
            for i in range(pull.GetN()):
                N = datagraph.GetPointY(i)
                errup=datagraph.GetErrorYhigh(i)
                errlo=datagraph.GetErrorYlow(i)
                pred=pdfhists[args.bkgIndex].GetBinContent(i+1) # needs to be offset by one here

                # compute central point
                if N<pred:   pullval=(N-pred)/errup
                elif N>pred: pullval=(N-pred)/errlo
                else:        pullval=0
                pull.SetPointY(i, pullval)
                pull.SetPointEYhigh(i,1)
                pull.SetPointEYlow(i,1)
                if N>0:
                    chisq = chisq+pullval**2
                    ndof = ndof+1

                # compute sigpullhist stuff
                sig=sigpullhist.GetBinContent(i+1) # needs to be offset by one here
                if N>(sig+pred):  sigpullhist.SetBinContent(i+1,sig/errlo)
                else:             sigpullhist.SetBinContent(i+1,sig/errup)

                # compute the background error pull
                if args.drawBkgUncertainty:
                    bkguncertaintypull.SetPoint(i,var.getBinning().binCenter(i),0.0)
                    if N>(pred+bkg_uncertainties[i]):
                        bkguncertaintypull.SetPointError(i,var.getBinning().binWidth(i)/2,bkg_uncertainties[i]/errlo)
                    else:
                        bkguncertaintypull.SetPointError(i,var.getBinning().binWidth(i)/2,bkg_uncertainties[i]/errup)

            chisqprob=ROOT.TMath.Prob(chisq,ndof)
            hChisqProb.Fill(chisqprob)

            # format things
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
            
            for pdfhistindex, pdfhist in enumerate(pdfhists):
                pdfhists[pdfhistindex].SetLineColor(tdrstyle.colors[pdfhistindex])
                pdfhists[pdfhistindex].SetFillColor(0)
            sighist.SetLineColor(tdrstyle.colors[sigcolorindex])
            sighist.SetFillColor(tdrstyle.colors[sigcolorindex])

            # Draw things
            pad.cd()
            datagraph.Draw("APZ")
            if args.drawSignal:
                stack=ROOT.THStack("stack","")
                stack.Add(pdfhists[args.bkgIndex])
                stack.Add(sighist)
                stack.Draw("hist same")
            else:
                for pdfhist in pdfhists:
                    pdfhist.Draw("same")
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
            lumitxt.DrawLatexNDC(0.68,0.915,"138 fb^{-1} (13 TeV)")
            txt = ROOT.TLatex()
            txt.SetTextFont(42)
            txt.SetTextSize(0.04)
            if region=="symiso":
                regiontxt="sym. iso."
            elif region=="asymnoniso":
                regiontxt="asym. non-iso. (scaled)"
            elif region=="asymnoniso_unscaled":
                regiontxt="asym. non-iso."
            txt.DrawLatexNDC(0.55,0.80,"#splitline{"+btagtitles[btagindex]+", p_{T}"+pttitles[ptindex]+" GeV}{"+regiontxt+"}")
            
            
            # Draw legend
            leg=ROOT.TLegend(0.6,0.40,0.90,0.70)
            leg.SetBorderSize(0)
            leg.SetFillColor(0)
            leg.SetTextFont(42)
            leg.SetTextSize(0.04)
            leg.AddEntry(datagraph, "data", "ep")
            if args.drawSignal:
                if sigtype=="eta":
                    leg.AddEntry(sighist, "m_{#eta}="+sigmass[1:]+" MeV (x"+str(args.sigScale)+")", "f")
                elif sigtype=="etaprime":
                    leg.AddEntry(sighist, "m_{#eta'}="+sigmass[1:]+" MeV (x"+str(args.sigScale)+")", "f")
                leg.AddEntry(pdfhists[args.bkgIndex],pdfhisttitles[args.bkgIndex],"l")
            else:
                for pdfhistindex, pdfhist in enumerate(pdfhists):
                    leg.AddEntry(pdfhist, pdfhisttitles[pdfhistindex], "l")
            if args.drawBkgUncertainty:
                leg.AddEntry(bkguncertaintypull, "bkg. uncertainty","f")
            leg.Draw()

            # draw chisq
            if args.drawChisq:
                chisqstr="#chi^{2}/d.o.f.="+"{0:0.2f}".format(chisq/ndof)
                chisqtxt=ROOT.TLatex()
                chisqtxt.SetTextFont(42)
                chisqtxt.SetTextSize(0.04)
                chisqtxt.DrawLatexNDC(0.65,0.2,chisqstr)
            
            # Draw pulls
            pullpad.cd()
            pull.Draw("APZ")
            if args.drawSignal:
                sigpullhist.SetLineColor(tdrstyle.colors[sigcolorindex])
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
            if args.drawSpline:
                spline=pdf1.getSpline()
                spline.SetLineWidth(2)
                spline.SetLineColor(tdrstyle.colors[4])
                spline.Draw("same")

            if args.drawBkgUncertainty:
                bkguncertaintypull.SetFillColorAlpha(ROOT.kBlack,0.5)
                bkguncertaintypull.SetFillStyle(1001)
                bkguncertaintypull.SetLineColor(0)
                bkguncertaintypull.Draw("3")

            can.Modified()
            can.Update()
            
            can.SaveAs("./plots/"+can.GetName()+".pdf")

    # Draw chisq probability histogram
    if args.drawChisq:
        can=ROOT.TCanvas("chisqprob","chisqprob",300,300)
        can.SetFillColor(0)
        can.SetBorderMode(0)
        can.SetFrameFillStyle(0)
        can.SetFrameBorderMode(0)
        can.SetTickx(0)
        can.SetTicky(0)
        hChisqProb.SetMarkerSize(0.3)
        hChisqProb.SetMarkerStyle(20)
        hChisqProb.SetBinErrorOption(ROOT.TH1.kPoisson)
        hChisqProb.Draw("E0")
        can.SaveAs("./plots/"+can.GetName()+".pdf")
