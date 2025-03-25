#!/bin/env python3

import ROOT
import files
import argparse
import common.tdrstyle as tdrstyle
import common.common as common

###############################################################
# start of the "main" function
###############################################################

if __name__ == "__main__":

    # setup and use the parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--drawSignal",help="Draw the signal on top of the background. If so, make sure to specify which background index to drop on top of.",action=argparse.BooleanOptionalAction,default=True)
    parser.add_argument("--sigScale",help="How to scale the signal, if drawn.",type=float,default=1.0)
    parser.add_argument("--bkgIndex",help="Which background to compute the pull and chi^2 with respect to and/or plot the signal on top of.",type=int,choices=[0,1,2],default=0)
    parser.add_argument("--drawBkgUncertainty",help="Draw the uncertainty on the background fit. This can be slow.",action=argparse.BooleanOptionalAction,default=False)
    args=parser.parse_args()
    
    # get the workspace and parameters
    bkgws = common.get_workspace_from_file(files.bkgworkspacefn, files.workspacename)
    sigws = common.get_workspace_from_file(files.sigworkspacefn, files.workspacename)
    region  = common.get_tnamed_title_from_file(files.bkgworkspacefn, "region")
    imass = common.get_tnamed_title_from_file(files.sigworkspacefn, "imass")
    wmass = common.get_tnamed_title_from_file(files.sigworkspacefn, "wmass")
    pmass = common.get_tnamed_title_from_file(files.sigworkspacefn, "pmass")
    
    ROOT.gStyle.SetErrorX(0)
    ROOT.gStyle.SetTitleFont(42)
    ROOT.gStyle.SetTitleFont(42, "XYZ")
    ROOT.gStyle.SetHistLineWidth(2)
    
    # loop over etabins
    for etabin in files.etabins:
        
        # loop over the m2pbins
        for m2pbin in files.m2pbins:

            # create the canvas and subdivide into a top and bottom pad
            can=ROOT.TCanvas("fits_"+region+"_"+etabin+"_"+str(m2pbin), "c",300,300)
            can.cd()
            pad = ROOT.TPad("pad"+etabin+str(m2pbin),"pad",0,0.25,1,1)
            pad.SetMargin(0.15,0.08,0.02,0.1) #L, R, B, T
            pad.Draw()
            pullpad = ROOT.TPad("pullpad"+etabin+str(m2pbin),"pullpad",0,0,1,0.25)
            pullpad.SetMargin(0.15,0.08,0.3,0.02) #L, R, B, T
            pullpad.SetTickx()
            pullpad.Draw()

            # get the roodatahist and corresponding variable, then create a TH1 from it
            datagraph,var=common.get_datagraph_from_workspace(bkgws, "dataHist_bin"+str(m2pbin)+etabin)
            # get the pdfs and their respective normalizations, and turn them into histograms
            sigpdf=sigws.pdf("sigpdf_bin"+str(m2pbin)+etabin)
            sigpdfnorm=sigws.obj("sigpdf_bin"+str(m2pbin)+etabin+"_norm")
            sighist=common.pdf_to_histogram(sigpdf, var.getBinning(), "hsig_"+str(m2pbin)+etabin, sigpdfnorm.getVal()*args.sigScale*files.luminosity)
            pdfs = []
            pdfnorms = []
            pdfhists = []
            pdfhisttitles = []
            pdfs.append(bkgws.pdf("model_bkg_f1_bin"+str(m2pbin)+etabin))
            pdfs.append(bkgws.pdf("model_bkg_f2_bin"+str(m2pbin)+etabin))
            pdfs.append(bkgws.pdf("model_bkg_f3_bin"+str(m2pbin)+etabin))
            pdfnorms.append(bkgws.var("model_bkg_f1_bin"+str(m2pbin)+etabin+"_norm"))
            pdfnorms.append(bkgws.var("model_bkg_f2_bin"+str(m2pbin)+etabin+"_norm"))
            pdfnorms.append(bkgws.var("model_bkg_f3_bin"+str(m2pbin)+etabin+"_norm"))
            pdfhists.append(common.pdf_to_histogram(pdfs[0], var.getBinning(), "hpdf1_"+str(m2pbin)+etabin, pdfnorms[0].getVal()))
            pdfhists.append(common.pdf_to_histogram(pdfs[1], var.getBinning(), "hpdf2_"+str(m2pbin)+etabin, pdfnorms[1].getVal()))
            pdfhists.append(common.pdf_to_histogram(pdfs[2], var.getBinning(), "hpdf3_"+str(m2pbin)+etabin, pdfnorms[2].getVal()))
            pdfhisttitles.append("f1")
            pdfhisttitles.append("f2")
            pdfhisttitles.append("f3")

            # compute the uncertainty on the background fit
            if args.drawBkgUncertainty:
                fitresult=bkgws.obj("fitresult_"+pdfs[args.bkgIndex].GetName()+"_dataHist_bin"+str(m2pbin)+etabin)
                if not fitresult: raise RuntimeError(f"Cannot get fitresult")
                bkg_uncertainties=common.monte_carlo_uncertainty_envelope(pdfs[args.bkgIndex], pdfnorms[args.bkgIndex].getVal(), fitresult, var.getBinning())
            

            
            # compute the pull graph and chi^2
            pull=datagraph.Clone(datagraph.GetName()+"_pull")
            sigpullhist = sighist.Clone(sighist.GetName()+"_pull")
            bkguncertaintypull=ROOT.TGraphErrors(var.getBinning().numBins())
            
            chisq=0
            ndof=-3
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

            

            # Draw the data
            pad.cd()
            pad.SetLogy(1)
            datagraph.SetMaximum(1e1)
            datagraph.SetMinimum(1e-3)
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
            datagraph.Draw("APZ")

            # draw the signal
            if args.drawSignal:
                sighist.SetLineColor(tdrstyle.colors[len(pdfhists)+1])
                sighist.SetFillColor(0)
                sighist.SetLineWidth(2)
                stack=ROOT.THStack("stack","")
                stack.Add(pdfhists[args.bkgIndex])
                stack.Add(sighist)
                stack.Draw("C same")
                datagraph.Draw("PZ") # draw the data again on _top_ of the signal
                
            # draw the background pdfs
            for pdfhistindex, pdfhist in enumerate(pdfhists):
                pdfhists[pdfhistindex].SetLineColor(tdrstyle.colors[pdfhistindex])
                pdfhists[pdfhistindex].SetLineWidth(2)
                pdfhists[pdfhistindex].SetFillColor(0)
                pdfhist.Draw("C same")
            pad.RedrawAxis() # redraw the tick marks
            
            # Draw legend
            leg=ROOT.TLegend(0.6,0.40,0.90,0.70)
            leg.SetBorderSize(0)
            leg.SetFillColor(0)
            leg.SetTextFont(42)
            leg.SetTextSize(0.04)
            leg.AddEntry(datagraph, "data", "ep")
            for pdfhistindex, pdfhist in enumerate(pdfhists):
                leg.AddEntry(pdfhist, pdfhisttitles[pdfhistindex], "l")
            if args.drawBkgUncertainty:
                leg.AddEntry(bkguncertaintypull, "bkg. uncertainty","f")
            if args.drawSignal:
                leg.AddEntry(sighist, "signal (x"+str(args.sigScale)+")", "f")
            leg.Draw()

                
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
            lumitxt.DrawLatexNDC(0.68,0.915,str(files.luminosity)+" fb^{-1} (13 TeV)")

            # need to get a 2D histogram with the right binning
            hist2d=common.get_TH1_from_file(files.sigworkspacefn,"recomass_barrelm")
            m2plo = hist2d.GetXaxis().GetBinLowEdge(m2pbin)
            m2phi = hist2d.GetXaxis().GetBinUpEdge(m2pbin)
            m2ptext=ROOT.TLatex()
            m2ptext.SetTextFont(42)
            m2ptext.SetTextSize(0.045)
            m2ptext.DrawLatexNDC(0.6,0.83,"{0:0.2f}".format(m2plo)+"<M(2p)<"+"{0:0.2f}".format(m2phi)+" GeV")
            moretext=ROOT.TLatex()
            moretext.SetTextFont(42)
            moretext.SetTextSize(0.045)
            moretext.DrawLatexNDC(0.6,0.78,"("+etabin+"; "+region+")")
            
            # Draw pulls
            pullpad.cd()
            pull.SetMarkerSize(0.3)
            pull.SetMarkerStyle(20)
            pull.SetLineWidth(2)
            pull.GetXaxis().SetTitle("M(2p+#gamma) [GeV]")
            pull.GetXaxis().SetLabelSize(0.13)
            pull.GetXaxis().SetTitleSize(0.13)
            pull.GetXaxis().SetTitleOffset(0.8)
            pull.SetStats(0)
            pull.SetTitle("")
            pull.GetYaxis().SetTitle("#frac{data-pred.}{error}")
            pull.GetYaxis().SetTitleSize(0.13)
            pull.GetYaxis().SetLabelSize(0.15)
            pull.GetYaxis().SetTitleOffset(0.33)
            pull.GetYaxis().SetNdivisions(5, 5, 0)
            pull.GetYaxis().CenterTitle(True)
            pull.SetMarkerColor(ROOT.kBlack)
            pull.SetLineColor(ROOT.kBlack)
            pull.GetXaxis().SetRangeUser(var.getBinning().binLow(0),var.getBinning().binHigh(var.getBinning().numBins()-1))
            pull.Draw("APZ")
            if args.drawSignal:
                sigpullhist.SetLineColor(tdrstyle.colors[len(pdfhists)+1])
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

            if args.drawBkgUncertainty:
                bkguncertaintypull.SetFillColorAlpha(ROOT.kBlack,0.5)
                bkguncertaintypull.SetFillStyle(1001)
                bkguncertaintypull.SetLineColor(0)
                bkguncertaintypull.Draw("3")

            chisqstr="#chi^{2}/d.o.f.="+"{0:0.2f}".format(chisq/ndof)
            chisqtxt=ROOT.TLatex()
            chisqtxt.SetTextFont(42)
            chisqtxt.SetTextSize(0.10)
            chisqtxt.DrawLatexNDC(0.75,0.85,chisqstr)
            
            can.Modified()
            can.Update()
            can.SaveAs("./plots/"+can.GetName()+".pdf")
