import ROOT
import makebkgworkspace as ws
import tdrstyle

tdrstyle.setTDRStyle()

rootfile = ROOT.TFile(ws.fileoutname, 'READ')

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

# loop over etabins
for etabin in ws.etabins:

    # split bins into chunks of at most chunksize elements
    chunksize=5
    splitbins = [ws.bins[i:i+chunksize] for i in range(0, len(ws.bins), chunksize)]

    # get the 2d histogram
    datahist2d=ws.get2dHist(etabin)

    # loop over chunks of bins
    for chunkindex, chunk in enumerate(splitbins):

        # create a new Canvas for each chunk
        if etabin==ws.etabins[0]: etalabel="B"
        else: etalabel="E"

        canname = "bkgfit"+etalabel+str(chunkindex)
        can = ROOT.TCanvas(canname, canname, 230*chunksize, 300)
        can.cd()
        can.SetFillColor(0)
        can.SetBorderMode(0)
        can.SetFrameFillStyle(0)
        can.SetFrameBorderMode(0)
        can.SetTickx(0)
        can.SetTicky(0)

        plotlist = []
        padlist = []
        # loop over the bins in the chunk
        for binindex, bin in enumerate(chunk):

            # create pads for each of the bins
            can.cd()
            pad = ROOT.TPad("pad"+str(bin),"pad"+str(bin),(1.*binindex)/chunksize,0.25,(binindex+1.)/chunksize,1.0)
            padlist.append(pad)
            leftmargin=rightmargin=0.0
            if binindex==0: leftmargin=0.15
            if binindex==chunksize-1: rightmargin=0.05
            pad.SetMargin(leftmargin,rightmargin,0.023,0.1)
            pad.SetFrameLineWidth(1)
            pad.SetLogy(1)
            pad.Draw()

            # create pads for the pulls
            pullpad = ROOT.TPad("pullpad"+str(bin),"pullpad"+str(bin),(1.*binindex)/chunksize,0,(binindex+1.)/chunksize,0.25)
            pullpad.SetMargin(leftmargin,rightmargin,0.35,0.023)
            pullpad.SetFrameLineWidth(1)
            pullpad.SetTickx()
            pullpad.Draw()
        
            # get the data and fits
            data = rootfile.Get("dataHist_bin"+str(bin)+etalabel)
            f1 = rootfile.Get("model_bkg_f1_bin"+str(bin)+etalabel)
            f2 = rootfile.Get("model_bkg_f2_bin"+str(bin)+etalabel)
            f3 = rootfile.Get("model_bkg_f3_bin"+str(bin)+etalabel)

            # draw the data
            pad.cd()
            plot = ws.m2pg.frame()
            plotlist.append(plot)
            data.plotOn(plot,ROOT.RooFit.MarkerSize(0.5),ROOT.RooFit.Name("data"))
            f1.plotOn(plot,ROOT.RooFit.LineColor(colors[0]),ROOT.RooFit.LineWidth(1),ROOT.RooFit.Name("f1"))
            f2.plotOn(plot,ROOT.RooFit.LineColor(colors[1]),ROOT.RooFit.LineWidth(1),ROOT.RooFit.Name("f2"))
            f3.plotOn(plot,ROOT.RooFit.LineColor(colors[2]),ROOT.RooFit.LineWidth(1),ROOT.RooFit.Name("f3"))
            plot.GetXaxis().SetLabelSize(0)
            plot.Draw()
            plot.SetMinimum(.001)
            pad.Update()

            # draw the pulls
            pullpad.cd()
            pullHist = plot.pullHist("data","f1")
            pullPlot = ws.m2pg.frame()
            pullPlot.addPlotable(pullHist,"P")
            #        for i in range(pullHist.GetN()):
            #            pullHist.SetPointEYlow(i, 0.0)
            #           pullHist.SetPointEYhigh(i, 0.0)
            #            print(pullHist.GetPointY(i))

            pullHist.SetMarkerSize(0.5)
            if binindex==len(chunk)-1:
                pullPlot.GetXaxis().SetTitle("M(2p+#gamma) [GeV]")
            else:
                pullPlot.GetXaxis().SetTitle("")
            pullPlot.GetXaxis().SetTitleOffset(0.85)
            pullPlot.GetXaxis().SetTitleSize(0.18)
            pullPlot.GetXaxis().SetLabelSize(0.15)
            pullPlot.GetXaxis().SetTickSize(0.10)
            pullPlot.GetYaxis().SetTitle("Pull")
            pullPlot.GetYaxis().SetTitleOffset(0.3)
            pullPlot.GetYaxis().SetTitleSize(0.18)
            pullPlot.GetYaxis().SetNdivisions(5)
            pullPlot.GetYaxis().SetLabelSize(0.15)
            pullPlot.SetMinimum(-3)
            pullPlot.SetMaximum(3)
            if binindex !=0:
                pullPlot.GetXaxis().ChangeLabel(1,-1,-1,-1,-1,-1," ")
            pullPlot.Draw("P")
        
            line = ROOT.TLine()
            line.SetNDC(False)
            line.SetX1(500.)
            line.SetX2(3992.)
            line.SetY1(0)
            line.SetY2(0)
            line.SetLineWidth(1)
            line.SetLineColor(colors[3])
            line.SetLineStyle(3)
            #        line.Draw()
            #        line.DrawClone()
            pullpad.Update()
            
            # calculate and draw the chi^2
            pad.cd()
            if binindex==len(chunk)-1: m2ptextx=0.25
            else: m2ptextx=0.40
            chi2dof=plot.chiSquare("f1","data",3)
            #        for i in range(pullHist.GetN()):
            #            val=pullHist.GetPointY(i)
            #            print(str(i)+": "+str(val))
            chi2dofstr="{0:0.2f}".format(chi2dof)
            chitext=ROOT.TLatex()
            chitext.SetTextFont(42)
            chitext.SetTextSize(0.055)
            chitext.DrawLatexNDC(m2ptextx,0.71,"#chi^{2}/dof="+chi2dofstr)

            # write the 2p mass range
            m2plo = datahist2d.GetXaxis().GetBinLowEdge(bin)
            m2phi = datahist2d.GetXaxis().GetBinUpEdge(bin)
            m2ptext=ROOT.TLatex()
            m2ptext.SetTextFont(42)
            m2ptext.SetTextSize(0.055)
            m2ptext.DrawLatexNDC(m2ptextx,0.83,str(m2plo)+"<M(2p)<"+str(m2phi)+" GeV")

            # write the 2p eta range
            etatext=ROOT.TLatex()
            etatext.SetTextFont(42)
            etatext.SetTextSize(0.055)
            if etabin==ws.etabins[0]:
                etatext.DrawLatexNDC(m2ptextx,0.77,"|#eta(2p)|<1.44")
            else:
                etatext.DrawLatexNDC(m2ptextx,0.77,"1.44<|#eta(2p)|<2.50")
        
            # draw the legend
            if binindex==len(chunk)-1:
                leg=ROOT.TLegend(0.7,0.55,0.93,0.85)
                leg.SetBorderSize(0)
                leg.SetFillColor(0)
                leg.SetTextFont(42)
                leg.SetTextSize(0.07)
                leg.AddEntry(plot.findObject("data"),"data","ep")
                leg.AddEntry(plot.findObject("f1"), "f1", "l")
                leg.AddEntry(plot.findObject("f2"), "f2", "l")
                leg.AddEntry(plot.findObject("f3"), "f3", "l")
                leg.Draw()
        
            
            #
            # end loop over bins in chunk
            #
        
        # set the plots to the same maximum value
        max=0.;
        for plot in plotlist:
            if plot.GetMaximum()>max:
                max=plot.GetMaximum()
        for plot in plotlist:
            plot.SetMaximum(max*1.1)
        
        # Write CMS stuff
        can.cd()
        cmstxt = ROOT.TLatex()
        cmstxt.SetTextFont(61)
        cmstxt.SetTextSize(0.07)
        cmstxt.DrawLatexNDC(0.03,0.935,"CMS")
        extratxt = ROOT.TLatex()
        extratxt.SetTextFont(52)
        extratxt.SetTextSize(0.05)
        extratxt.DrawLatexNDC(0.068,0.935,"Preliminary")
        lumitxt = ROOT.TLatex()
        lumitxt.SetTextFont(42)
        lumitxt.SetTextSize(0.05)
        lumix=0.91
        if len(chunk)==1:
            lumix=0.13
        lumitxt.DrawLatexNDC(lumix,0.935,"59 fb^{-1} (13 TeV)")

        # note if sideband
        if ws.doSideband:
            sbtxt = ROOT.TLatex()
            sbtxt.SetTextFont(42)
            sbtxt.SetTextSize(0.05)
            sbtxt.DrawLatexNDC(0.5,0.935,"Sideband Region")
        
        can.Update()
        can.Draw()
        can.SaveAs("../plots/"+can.GetName()+".pdf")

