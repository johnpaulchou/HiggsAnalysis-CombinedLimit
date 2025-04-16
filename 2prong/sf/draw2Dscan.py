#!/bin/env python3

import ROOT
from scipy.interpolate import griddata
import numpy as np
import argparse




###############################################################
# start of the "main" function
###############################################################

if __name__ == "__main__":
    # setup and use the parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("workspacefn", help="root file containing the workspace to draw")
    parser.add_argument("--year", help="data year the file comes from")
    parser.add_argument('--xrange', nargs=3, metavar=('PARAM', 'LOW', 'HIGH'),
                        help='Specify x-axis parameter name with low and high values')
    parser.add_argument('--yrange', nargs=3, metavar=('PARAM', 'LOW', 'HIGH'),
                        help='Specify y-axis parameter name with low and high values')

    args=parser.parse_args()
    xname, xlo, xhi= args.xrange
    yname, ylo, yhi= args.yrange
    xlo=float(xlo)
    xhi=float(xhi)
    ylo=float(ylo)
    yhi=float(yhi)

    axisdict = { "r" : ["efficiency scale factor", 1.0], "shiftPar" : ["mass scale shift [GeV]", 0.0], "stretchPar" : ["mass resolution",1.0] }
    xtitle=axisdict[xname][0]
    ytitle=axisdict[yname][0]
    SMx=axisdict[xname][1]
    SMy=axisdict[yname][1]
    
    
    ROOT.gROOT.SetBatch(True)
    ROOT.gStyle.SetOptStat(0)

    f = ROOT.TFile(args.workspacefn)
    t = f.Get("limit")

    # Number of points in interpolation
    n_points = 1000
    x_range = [xlo, xhi]
    y_range = [ylo, yhi]

    # Number of bins in plot
    n_bins = 60

    x, y, deltaNLL = [], [], []
    for ev in t:
        x.append(getattr(ev, xname))
        y.append(getattr(ev, yname))
        deltaNLL.append(getattr(ev, "deltaNLL"))

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Do interpolation
    # Convert to numpy arrays as required for interpolation
    dnll = np.asarray(deltaNLL)
    points = np.array([x, y]).transpose()
    # Set up grid
    grid_x, grid_y = np.mgrid[x_range[0] : x_range[1] : n_points * 1j, y_range[0] : y_range[1] : n_points * 1j]
    grid_vals = griddata(points, dnll, (grid_x, grid_y), "cubic")

    # Remove NANS
    grid_x = grid_x[grid_vals == grid_vals]
    grid_y = grid_y[grid_vals == grid_vals]
    grid_vals = grid_vals[grid_vals == grid_vals]
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    # Define Profile2D histogram
    h2D = ROOT.TProfile2D("h", "h", n_bins, x_range[0], x_range[1], n_bins, y_range[0], y_range[1])

    bbxvals=[]
    bbyvals=[]
    for i in range(len(grid_vals)):
        # Factor of 2 comes from 2*NLL
        h2D.Fill(grid_x[i], grid_y[i], 2 * grid_vals[i])
        if abs(2*grid_vals[i]-2.3)<5e-2:
            bbxvals.append(grid_x[i])
            bbyvals.append(grid_y[i])

    # get bounding-box min/max
    bb =(min(bbxvals), min(bbyvals), max(bbxvals), max(bbyvals))
    parx = round((bb[2]+bb[0])/2,3)
    parxerr = round((bb[2]-bb[0])/2,3)
    pary = round((bb[3]+bb[1])/2,3)
    paryerr = round((bb[3]-bb[1])/2,3)
    print(xname+" = "+str(parx)+" +/- "+str(parxerr))
    print(yname+" = "+str(pary)+" +/- "+str(paryerr))
    
    # Loop over bins: if content = 0 then set 999
    for ibin in range(1, h2D.GetNbinsX() + 1):
        for jbin in range(1, h2D.GetNbinsY() + 1):
            if h2D.GetBinContent(ibin, jbin) == 0:
                xc = h2D.GetXaxis().GetBinCenter(ibin)
                yc = h2D.GetYaxis().GetBinCenter(jbin)
        h2D.Fill(xc, yc, 999)

    # Set up canvas
    canv = ROOT.TCanvas("canv", "canv", 600, 600)
    canv.SetTickx()
    canv.SetTicky()
    canv.SetRightMargin(0.14)
    canv.SetLeftMargin(0.115)
    canv.SetBottomMargin(0.115)
    # Extract binwidth
    xw = (x_range[1] - x_range[0]) / n_bins
    yw = (y_range[1] - y_range[0]) / n_bins

    # Set histogram properties
    h2D.SetContour(999)
    h2D.SetTitle("")
    h2D.GetXaxis().SetTitle(xtitle)
    h2D.GetXaxis().SetTitleSize(0.05)
    h2D.GetXaxis().SetTitleOffset(0.9)
    h2D.GetXaxis().SetRangeUser(x_range[0], x_range[1] - xw)

    h2D.GetYaxis().SetTitle(ytitle)
    h2D.GetYaxis().SetTitleSize(0.05)
    h2D.GetYaxis().SetTitleOffset(1.05)
    h2D.GetYaxis().SetRangeUser(y_range[0], y_range[1] - yw)
    
    h2D.GetZaxis().SetTitle("-2 #Delta ln L")
    h2D.GetZaxis().SetTitleSize(0.05)
    h2D.GetZaxis().SetTitleOffset(0.8)

    h2D.SetMaximum(25)

    # Make confidence interval contours
    c68, c95 = h2D.Clone(), h2D.Clone()
    c68.SetContour(2)
    c68.SetContourLevel(1, 2.3)
    c68.SetLineWidth(3)
    c68.SetLineColor(ROOT.kBlack)
    c95.SetContour(2)
    c95.SetContourLevel(1, 5.99)
    c95.SetLineWidth(3)
    c95.SetLineStyle(2)
    c95.SetLineColor(ROOT.kBlack)

    # Draw histogram and contours
    xlo=xlo
    xhi=xhi
    ylo=ylo
    yhi=yhi
    h2D.GetXaxis().SetRangeUser(xlo,xhi)
    h2D.GetYaxis().SetRangeUser(ylo,yhi)
    h2D.Draw("COLZ")
    
    # Draw lines for SM point
    vline = ROOT.TLine(SMx, ylo, SMx, yhi)
    vline.SetLineColorAlpha(ROOT.kGray, 0.5)
    vline.Draw("Same")
    hline = ROOT.TLine(xlo, SMy, xhi, SMy)
    hline.SetLineColorAlpha(ROOT.kGray, 0.5)
    hline.Draw("Same")

    # Draw ontours
    c68.Draw("cont3same")
    c95.Draw("cont3same")

    # Draw bounding box
    box = ROOT.TBox(bb[0], bb[1], bb[2], bb[3])
    box.SetLineColorAlpha(ROOT.kGray,0.5)
    box.SetLineWidth(1)
    box.SetFillStyle(0)
    box.Draw("same")
    
    
    # Make best fit and sm points
    gBF = ROOT.TGraph()
    gBF.SetPoint(0, grid_x[np.argmin(grid_vals)], grid_y[np.argmin(grid_vals)])
    gBF.SetMarkerStyle(34)
    gBF.SetMarkerSize(2)
    gBF.SetMarkerColor(ROOT.kBlack)
    gBF.Draw("P")

    gSM = ROOT.TGraph()
    gSM.SetPoint(0, SMx, SMy)
    gSM.SetMarkerStyle(33)
    gSM.SetMarkerSize(2)
    gSM.SetMarkerColor(ROOT.kRed)
    gSM.Draw("P")
    

    # Add legend
    leg = ROOT.TLegend(0.6, 0.67, 0.8, 0.87)
    leg.SetBorderSize(0)
    leg.SetFillColor(0)
    leg.AddEntry(gBF, "Best fit", "P")
    leg.AddEntry(c68, "1#sigma CL", "L")
    leg.AddEntry(c95, "2#sigma CL", "L")
    leg.AddEntry(gSM, "MC expectation", "P")
    leg.Draw()

    # Draw Text
    cmstxt = ROOT.TLatex()
    cmstxt.SetTextFont(61)
    cmstxt.SetTextSize(0.07)
    cmstxt.DrawLatexNDC(0.12,0.915,"CMS")
    extratxt = ROOT.TLatex()
    extratxt.SetTextFont(52)
    extratxt.SetTextSize(0.05)
    extratxt.DrawLatexNDC(0.27,0.915,"Preliminary")
    lumitxt = ROOT.TLatex()
    lumitxt.SetTextFont(42)
    lumitxt.SetTextSize(0.05)
    if args.year=="2018":
        lumitxt.DrawLatexNDC(0.58,0.915,"59 fb^{-1} (13 TeV)")

    canv.Update()
    canv.SaveAs("./plots/"+xname+"_"+yname+"_"+args.year+".pdf")
