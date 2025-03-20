#!/bin/env python3

import ctypes
import array
import ROOT
import tdrstyle
import argparse
import makeworkspace as ttw


"""
Retrieve the title of a TNamed object from a ROOT file

Parameters:
    - file_path: Path to the ROOT file containing the TNamed object
    - tnamed_name: name of the TNamed object

Returns:
    - string
"""
def get_tnamed_title_from_file(file_path, tnamed_name):
    # Open the ROOT file
    root_file = ROOT.TFile.Open(file_path, "READ")
    if not root_file or root_file.IsZombie():
        raise RuntimeError(f"Cannot open file: {file_path}")

    # Get the TNamed object
    tnamed = root_file.Get(tnamed_name)
    if not tnamed:
        root_file.Close()
        raise RuntimeError(f"Cannot find TNamed '{tnamed_name}' in file: {file_path}")

    # get the title before closing the file
    title = tnamed.GetTitle()
    root_file.Close()

    return title



"""
Retrieve a RooWorkspace from a ROOT file

Parameters:
    - file_path: Path to the ROOT file containing the workspace
    - workspace_name: Name of the RooWorkspace in the file

Returns:
    - RooWorkspace object
"""
def get_workspace_from_file(file_path, workspace_name):
    # Open the ROOT file
    root_file = ROOT.TFile.Open(file_path, "READ")
    if not root_file or root_file.IsZombie():
        raise RuntimeError(f"Cannot open file: {file_path}")
    
    # Get the workspace
    workspace = root_file.Get(workspace_name)
    if not workspace:
        root_file.Close()
        raise RuntimeError(f"Cannot find workspace '{workspace_name}' in file: {file_path}")

    # Clone to avoid dependence on file
    ws_clone = workspace.Clone()

    # Close the file
    root_file.Close()

    return ws_clone


"""
Retrieve a TGraphAsymmErrors from a RooDataHist inside a RooWorkspace
    
Parameters:
    - workspace: RooWorkspace to retrieve RooAbsPdf
    - datahist_name: Name of the specific RooDataHist to retrieve
    
Returns:
    - TGraphAsymmErrors object and associated RooRealVar
"""
def get_datagraph_from_workspace(workspace, datahist_name):
    # get the datahist
    datahist = workspace.data(datahist_name)
    if not datahist:
        root_file.Close()
        raise RuntimeError(f"Cannot find RooDataHist '{datahist_name}' in workspace '{workspace_name}'")
    
    # Get the variable(s) associated with the RooDataHist
    var_set = datahist.get()
    variable = var_set.first()
    if not variable:
        root_file.Close()
        raise RuntimeError("Cannot find associated variable for the RooDataHist")

    # get binning
    binning = variable.getBinning()
    
    # create a TH1D first
    hist = datahist.createHistogram("hist_"+btagbin+"_"+ptbin,variable)

    # create the TGraphAsymmErrors
    gr=ROOT.TGraphAsymmErrors(hist)

    # compute the Poisson uncertainties and divide out by the bin width
    alpha = 1 - 0.6827
    for i in range(gr.GetN()):
        N = gr.GetPointY(i)
        width = binning.binWidth(i)
        L = 0
        if N>0: L=ROOT.Math.gamma_quantile(alpha/2,N,1.)
        U =  ROOT.Math.gamma_quantile_c(alpha/2,N+1,1)
        gr.SetPointEYlow(i, (N-L)/width)
        gr.SetPointEYhigh(i, (U-N)/width)
        gr.SetPointY(i, N/width)

    # set the x-axis range
    gr.GetXaxis().SetRangeUser(binning.binLow(0),binning.binHigh(binning.numBins()-1))
    return gr, variable



"""
Convert a RooAbsPdf to a TH1D histogram with given normalization.
    
Parameters:
    - pdf: RooAbsPdf object to convert
    - binning: RooBinning that you want to use
    - hist_name: Name of the output histogram
    - normalization: Desired integral of the histogram (default: 1.0)

Returns:
    - TH1D histogram object
"""
def pdf_to_histogram(pdf, binning, hist_name, normalization=1.0):

    # get the variable's binning
    nbins = binning.numBins()
    bin_edges = [binning.binLow(i) for i in range(nbins)]
    bin_edges.append(binning.binHigh(nbins-1)) #append last bin high edge
    c_array_type = ctypes.c_float * len(bin_edges)
    c_array = c_array_type(*bin_edges)

    # Create histogram
    hist = ROOT.TH1D(hist_name, hist_name, nbins, c_array)

    # Get the RooRealVar
    obs = pdf.getVariables().first()

    # Fill histogram by evaluating PDF at bin centers
    for i in range(1, nbins + 1):
        x = hist.GetBinCenter(i)
        obs.setVal(x)
        pdf_value = pdf.getVal(ROOT.RooArgSet(obs))
        hist_val = pdf_value * normalization
        hist.SetBinContent(i, hist_val)
    
    return hist



###############################################################
# start of the "main" function
###############################################################

if __name__ == "__main__":

    # setup and use the parser
    # either draw the signal or draw all of the background fits
    # if you are drawing the signal, pick the background index to draw on top of
    # the bkgIndex also specifies what is drawn in the pull plot
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--drawSignal",help="Draw the signal on top of the background. If not, it draws all background fits instead.",action=argparse.BooleanOptionalAction,default=True)
    parser.add_argument("--drawSpline",help="Draw the spline in the pull area.",action=argparse.BooleanOptionalAction,default=False)
    parser.add_argument("--drawChisq",help="Print the chi^2 on the plots and create the chi^2 probability histogram.",action=argparse.BooleanOptionalAction,default=True)
    parser.add_argument("--sigScale",help="How to scale the signal, if drawn.",type=float,default=1.0)
    parser.add_argument("--bkgIndex",help="Which background to compute the pull and chi^2 with respect to and/or plot the signal on top of.",type=int,choices=[0,1],default=1)
    
    args=parser.parse_args()
    drawSignal = args.drawSignal
    sigScale = args.sigScale
    bkgIndex = args.bkgIndex
    drawSpline=args.drawSpline
    drawChisq=args.drawChisq

    # setup bin titles
    pttitles = ["=20-40", "=40-60", "=60-80", "=80-100", "=100-140", "=140-180", "=180-220", "=220-300", "=300-380", ">380" ]
    btagtitles = ["=1 b tag", "#kern[0.2]{#geq}#kern[-0.1]{2} b tags" ]
    assert len(pttitles)==len(ttw.ptbins), "pttitles and ptbins lengths don't match"
    assert len(btagtitles)==len(ttw.btagbins), "btagtitles and btagbins lengths don't match"

    # get the workspace
    ws = get_workspace_from_file(ttw.fileoutname, ttw.workspacename)

    # get the parameters
    sigmass = get_tnamed_title_from_file(ttw.fileoutname, "sigmass")
    sigtype = get_tnamed_title_from_file(ttw.fileoutname, "sigtype")
    region  = get_tnamed_title_from_file(ttw.fileoutname, "region")
    
    # global style settings
    colors = [ROOT.TColor.GetColor("#3f90da"),
              ROOT.TColor.GetColor("#ffa90e"),
              ROOT.TColor.GetColor("#bd1f01"),
              ROOT.TColor.GetColor("#94a4a2"),
              ROOT.TColor.GetColor("#832db6"),
              ROOT.TColor.GetColor("#a96b59"),
              ROOT.TColor.GetColor("#e76300"),
              ROOT.TColor.GetColor("#b9ac70"),
              ROOT.TColor.GetColor("#717581"),
              ROOT.TColor.GetColor("#92dadd"),
              ROOT.TColor.GetColor("#607641"),
              ROOT.TColor.GetColor("#F5BB54")]
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
            can=ROOT.TCanvas("c_"+btagbin+"_"+ptbin, "c_"+btagbin+"_"+ptbin,300,300)
            can.cd()
            pad = ROOT.TPad("pad"+ptbin,"pad"+ptbin,0,0.25,1,1)
            pad.SetMargin(0.15,0.08,0.02,0.1) #L, R, B, T
            pad.Draw()
            pullpad = ROOT.TPad("pullpad"+ptbin,"pullpad"+ptbin,0,0,1,0.25)
            pullpad.SetMargin(0.15,0.08,0.3,0.02) #L, R, B, T
            pullpad.SetTickx()
            pullpad.Draw()

            # get the roodatahist and corresponding variable, then create a TH1 from it
            graph,var=get_datagraph_from_workspace(ws, "data_"+btagbin+"_"+ptbin)
            
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
            pdfhists.append(pdf_to_histogram(pdf0, var.getBinning(), "temp_"+btagbin+"_"+ptbin+"_pdf0hist", pdf0norm.getVal()))
            pdfhists.append(pdf_to_histogram(pdf1, var.getBinning(), "temp_"+btagbin+"_"+ptbin+"_pdf1hist", pdf1norm.getVal()))
            pdfhisttitles.append("background")
            pdfhisttitles.append("post-fit bkg.")
            sighist = pdf_to_histogram(sig, var.getBinning(), "sig_"+btagbin+"_"+ptbin+"_pdfhist", signorm.getVal()*sigScale) # scale signal to an arbitrary value

            # compute the pull graph and chi^2
            pull=graph.Clone(graph.GetName()+"_pull")
            sigpullhist = sighist.Clone(sighist.GetName()+"_pull")
            chisq=0
            ndof=0
            for i in range(pull.GetN()):
                N = graph.GetPointY(i)
                errup=graph.GetErrorYhigh(i)
                errlo=graph.GetErrorYlow(i)
                pred=pdfhists[bkgIndex].GetBinContent(i+1) # needs to be offset by one here

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

            chisqprob=ROOT.TMath.Prob(chisq,ndof)
            hChisqProb.Fill(chisqprob)

            # format things
            can.SetFillColor(0)
            can.SetBorderMode(0)
            can.SetFrameFillStyle(0)
            can.SetFrameBorderMode(0)
            can.SetTickx(0)
            can.SetTicky(0)
            
            graph.GetXaxis().SetLabelSize(0)
            graph.SetMarkerSize(0.3)
            graph.SetMarkerStyle(20)
            graph.SetLineWidth(2)
            graph.GetXaxis().SetTitle("")
            graph.SetStats(0)
            graph.SetTitle("")
            graph.GetYaxis().SetTitle("Events/GeV")
            graph.GetYaxis().SetTitleSize(0.05)
            graph.SetMarkerColor(ROOT.kBlack)
            graph.SetLineColor(ROOT.kBlack)

            pull.SetMarkerSize(0.3)
            pull.SetMarkerStyle(20)
            pull.SetLineWidth(2)
            pull.GetXaxis().SetTitle("M(2p) [GeV]")
            pull.GetXaxis().SetLabelSize(0.13)
            pull.GetXaxis().SetTitleSize(0.13)
            pull.GetXaxis().SetTitleOffset(0.73)
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
                pdfhists[pdfhistindex].SetLineColor(colors[pdfhistindex])
                pdfhists[pdfhistindex].SetFillColor(0)
            sighist.SetLineColor(colors[sigcolorindex])
            sighist.SetFillColor(colors[sigcolorindex])

            # Draw things
            pad.cd()
            graph.Draw("APZ")
            if drawSignal:
                stack=ROOT.THStack("stack","")
                stack.Add(pdfhists[bkgIndex])
                stack.Add(sighist)
                stack.Draw("hist same")
            else:
                for pdfhist in pdfhists:
                    pdfhist.Draw("same")
            graph.Draw("PZ") # draw a 2nd time on top

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
            leg.AddEntry(graph, "data", "ep")
            if drawSignal:
                if sigtype=="eta":
                    leg.AddEntry(sighist, "m_{#eta}="+sigmass[1:]+" MeV (x"+str(sigScale)+")", "f")
                elif sigtype=="etaprime":
                    leg.AddEntry(sighist, "m_{#eta'}="+sigmass[1:]+" MeV (x"+str(sigScale)+")", "f")
                leg.AddEntry(pdfhists[bkgIndex],pdfhisttitles[bkgIndex],"l")
            else:
                for pdfhistindex, pdfhist in enumerate(pdfhists):
                    leg.AddEntry(pdfhist, pdfhisttitles[pdfhistindex], "l")
            leg.Draw()

            # draw chisq
            if drawChisq:
                chisqstr="#chi^{2}/d.o.f.="+"{0:0.0f}/".format(chisq)+str(ndof)+"={0:0.2f}".format(chisq/ndof)
                chisqtxt=ROOT.TLatex()
                chisqtxt.SetTextFont(42)
                chisqtxt.SetTextSize(0.04)
                chisqtxt.DrawLatexNDC(0.65,0.2,chisqstr)
            
            # Draw pulls
            pullpad.cd()
            pull.Draw("APZ")
            if drawSignal:
                sigpullhist.SetLineColor(colors[sigcolorindex])
                sigpullhist.Draw("same")
            line = ROOT.TLine()
            line.SetNDC(False)
            line.SetX1(var.getBinning().binLow(0))
            line.SetX2(var.getBinning().binHigh(var.getBinning().numBins()-1))
            line.SetY1(0)
            line.SetY2(0)
            line.SetLineWidth(1)
            line.SetLineColor(colors[3])
            line.SetLineStyle(3)
            line.Draw()
            if drawSpline:
                spline=pdf1.getSpline()
                spline.SetLineWidth(2)
                spline.SetLineColor(colors[4])
                spline.Draw("same")
            
            can.SaveAs("../plots/"+can.GetName()+".pdf")

    # Draw chisq probability histogram
    if drawChisq:
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
        can.SaveAs("../plots/"+can.GetName()+".pdf")
