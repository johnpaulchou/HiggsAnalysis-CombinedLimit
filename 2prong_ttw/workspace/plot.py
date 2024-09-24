import ROOT
import CMS_lumi, tdrstyle
import makeworkspace as ttw

tdrstyle.setTDRStyle()

pttitles = ["=20-40", "=40-60", "=60-80", "=80-100", "=100-140", "=140-180", "=180-220", "=220-300", "=300-380", ">380" ]
btagtitles = ["1 b tag", "#kern[0.2]{#geq}#kern[-0.1]{2} b tags" ]
wtitles = ["Sym. iso.", "Asym. non-iso."]

CMS_lumi.lumi_13TeV = "59 fb^{-1}"
CMS_lumi.writeExtraText = 1

rootfile = ROOT.TFile(ttw.fileoutname, "READ")

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

doPullSig=False

# setup chi^2 probability histograms
hchi2probs = []
for wbin in ttw.wbins:
    hchi2prob = ROOT.TH1D("hchi2prob"+wbin,"hchi2prob"+wbin,10,0.,1.)
    hchi2probs.append(hchi2prob)


# loop over the w types and the b tags
for windex, wbin in enumerate(ttw.wbins):
    for btagindex, btagbin in enumerate(ttw.btagbins):

        # create two canvases for each w-type bin and b-tag bin, one for each set of pt bins
        canlist = []
        canlist.append(ROOT.TCanvas("c1_"+wbin+"_"+btagbin, "c1_"+wbin+"_"+btagbin, 1000, 300))
        canlist.append(ROOT.TCanvas("c2_"+wbin+"_"+btagbin, "c2_"+wbin+"_"+btagbin, 1000, 300))

        padlist = []
        plotlist = []
        pullpadlist = []
        pullerrs = []
        chitexts = []
        
        for ptindex, ptbin in enumerate(ttw.ptbins):
            # select canvas to work in
            can = canlist[int(ptindex/5)]
            can.cd()
            can.SetFillColor(0)
            can.SetBorderMode(0)
            can.SetFrameFillStyle(0)
            can.SetFrameBorderMode(0)
            can.SetTickx(0)
            can.SetTicky(0)

            # create pads for the pt bins
            pad = ROOT.TPad("pad"+ptbin,"pad"+ptbin,(ptindex%5)*0.2,0.25,(ptindex%5+1)*0.2,1.0)
            padlist.append(pad)
            if ptindex%5==0:
                pad.SetMargin(0.15,0.0,0.023,0.1) #left-most pad
            elif ptindex%5==4:
                pad.SetMargin(0.0,0.05,0.023,0.1) #right-most pad
            else:
                pad.SetMargin(0.0,0.0,0.023,0.1) # middle pads
            pad.SetFrameLineWidth(1)
            pad.Draw()

            # create pads for the pulls
            pullpad = ROOT.TPad("pullpad"+ptbin,"pullpad"+ptbin,(ptindex%5)*0.2,0,(ptindex%5+1)*0.2,0.25)
            pullpadlist.append(pullpad)
            if ptindex%5==0:
                pullpad.SetMargin(0.15,0.0,0.35,0.023) #left-most pad
            elif ptindex%5==4:
                pullpad.SetMargin(0.0,0.05,0.35,0.023) #right-most pad
            else:
                pullpad.SetMargin(0.0,0.0,0.35,0.023) # middle pads
            pullpad.SetFrameLineWidth(1)
            pullpad.SetTickx()
            pullpad.Draw()
            
            plot = ttw.m2p.frame()
            plotlist.append(plot)
            
            data = rootfile.Get("data_"+wbin+"_"+btagbin+"_"+ptbin)
            bkg0 = rootfile.Get("temp_"+wbin+"_"+btagbin+"_"+ptbin+"_pdf")
            bkg1 = rootfile.Get("temp_"+wbin+"_"+btagbin+"_"+ptbin+"_bkg1pdf")
            bkg2 = rootfile.Get("temp_"+wbin+"_"+btagbin+"_"+ptbin+"_bkg2pdf")
            bkg3 = rootfile.Get("temp_"+wbin+"_"+btagbin+"_"+ptbin+"_bkg3pdf")
            data.plotOn(plot,ROOT.RooFit.MarkerSize(0.5),ROOT.RooFit.Name("data"))
            if wbin=="asymnoniso":
                bkg0.plotOn(plot,ROOT.RooFit.LineColor(colors[0]),ROOT.RooFit.LineWidth(1),ROOT.RooFit.Name("bkg0"))
                bkg1.plotOn(plot,ROOT.RooFit.LineColor(colors[1]),ROOT.RooFit.LineWidth(1),ROOT.RooFit.Name("bkg1"))
                bkg2.plotOn(plot,ROOT.RooFit.LineColor(colors[2]),ROOT.RooFit.LineWidth(1),ROOT.RooFit.Name("bkg2"))
                bkg3.plotOn(plot,ROOT.RooFit.LineColor(colors[3]),ROOT.RooFit.LineWidth(1),ROOT.RooFit.Name("bkg3"))
            else:
                bkg3.plotOn(plot,ROOT.RooFit.LineColor(colors[3]),ROOT.RooFit.LineWidth(1),ROOT.RooFit.Name("bkg3"))
                if doPullSig:
                    fitresult = rootfile.Get("fitresult_temp_"+wbin+"_"+btagbin+"_"+ptbin+"_bkg3pdf_data_"+wbin+"_"+btagbin+"_"+ptbin)
                    bkg3.plotOn(plot,ROOT.RooFit.VisualizeError(fitresult,2),ROOT.RooFit.FillColor(0),ROOT.RooFit.LineWidth(0),ROOT.RooFit.Name("sigma2"))
                    bkg3.plotOn(plot,ROOT.RooFit.VisualizeError(fitresult,1),ROOT.RooFit.FillColor(0),ROOT.RooFit.LineWidth(0),ROOT.RooFit.Name("sigma1"))
                    # get the curves from the plot
                    sigma2=plot.findObject("sigma2")
                    sigma1=plot.findObject("sigma1")
                    central=plot.findObject("bkg3")
                    h=plot.findObject("data")
                    up1=ROOT.TGraph(central.GetN())
                    lo1=ROOT.TGraph(central.GetN())
                    up2=ROOT.TGraph(central.GetN())
                    lo2=ROOT.TGraph(central.GetN())
                    for j in range(sigma1.GetN()):
                        if j<central.GetN():
                            up1.SetPoint(j, sigma1.GetX()[j], sigma1.GetY()[j])
                            up2.SetPoint(j, sigma2.GetX()[j], sigma2.GetY()[j])
                        else:
                            lo1.SetPoint(j, sigma1.GetX()[j], sigma1.GetY()[j])
                            lo2.SetPoint(j, sigma2.GetX()[j], sigma2.GetY()[j])
                    pull1sig = ROOT.TGraphErrors(h.GetN())
                    pull2sig = ROOT.TGraphErrors(h.GetN())
                    pull1sig.SetFillColorAlpha(colors[3], 0.35)
                    pull1sig.SetLineColor(0)
                    pullerrs.append(pull1sig)
                    pullerrs.append(pull2sig)
                    for j in range(h.GetN()):
                        x = h.GetPointX(j)
                        err=h.GetErrorY(j)
                        pull1sig.SetPoint(j, x, 0)
                        pull1sig.SetPointError(j, h.GetErrorX(j), (up1.Eval(x)-lo1.Eval(x))/err)
                        pull2sig.SetPoint(j, x, 0)
                        pull2sig.SetPointError(j, h.GetErrorX(j), (up2.Eval(x)-lo2.Eval(x))/err)

            data.plotOn(plot,ROOT.RooFit.MarkerSize(0.5),ROOT.RooFit.Name("data"))
            pad.cd()
            plot.Draw()
            
            # write text
            txt = ROOT.TLatex()
            txt.SetTextFont(42)
            txt.SetTextSize(0.07)
            txt.DrawLatexNDC(0.45,0.83,"p_{T}"+pttitles[ptindex]+" GeV")

            if ptindex%5==4:
                txt = ROOT.TLatex()
                txt.SetTextFont(42)
                txt.SetTextSize(0.07)
                txt.DrawLatexNDC(0.45,0.76,wtitles[windex])
                txt = ROOT.TLatex()
                txt.SetTextFont(42)
                txt.SetTextSize(0.07)
                txt.DrawLatexNDC(0.45,0.68,btagtitles[btagindex])


            # calculate chi^2 and F-test
            print(pttitles[ptindex]+" "+btagtitles[btagindex]+" "+wtitles[windex])
            chi2dof1=plot.chiSquare("bkg0","data",1)
            chi2dof2=plot.chiSquare("bkg1","data",2)
            chi2dof3=plot.chiSquare("bkg2","data",3)
            chi2dof4=plot.chiSquare("bkg3","data",4)
            chi2prob = ROOT.TMath.Prob(chi2dof1*33,33)
            hchi2probs[windex].Fill(chi2prob)
            chi2dof4str="{0:0.2f}".format(chi2dof4)
            if wbin=="asymnoniso":
                F1=(chi2dof1*32)/(chi2dof2*31)
                F2=(chi2dof2*31)/(chi2dof3*30)
                F3=(chi2dof3*30)/(chi2dof4*29)
                ftest1=1-ROOT.TMath.FDistI(F1,32,31)
                ftest2=1-ROOT.TMath.FDistI(F2,31,30)
                ftest3=1-ROOT.TMath.FDistI(F3,30,29)
                pick=1
                if ftest1<0.05: pick=2
                if ftest2<0.05: pick=3
                if ftest3<0.05: pick=4
                print("picked order "+str(pick))
                print("F1="+str(F1)+"; ftest1="+str(ftest1))
                print("F2="+str(F2)+"; ftest2="+str(ftest2))
                print("F3="+str(F3)+"; ftest3="+str(ftest3))

                chi2dof1str="{0:0.2f}".format(chi2dof1)
                chi2dof2str="{0:0.2f}".format(chi2dof2)
                chi2dof3str="{0:0.2f}".format(chi2dof3)
                chi2dof4str="{0:0.2f}".format(chi2dof4)
                chi2dof1str='#tilde{#chi}^{2}(bkgd)='+chi2dof1str
                chi2dof2str='#tilde{#chi}^{2}(B_{1})='+chi2dof2str
                chi2dof3str='#tilde{#chi}^{2}(B_{2})='+chi2dof3str
                chi2dof4str='#tilde{#chi}^{2}(B_{3})='+chi2dof4str
                if pick==1: chi2dof1str="#bf{"+chi2dof1str+"}"
                elif pick==2: chi2dof2str="#bf{"+chi2dof2str+"}"
                elif pick==3: chi2dof3str="#bf{"+chi2dof3str+"}"
                elif pick==4: chi2dof4str="#bf{"+chi2dof4str+"}"
                if ptindex%5!=4: offset=0.
                else: offset=0.5
                chi1text=ROOT.TLatex()
                chi1text.SetTextFont(42)
                chi1text.SetTextSize(0.055)
                chi1text.DrawLatexNDC(0.60-offset,0.74,chi2dof1str)
                chi2text=ROOT.TLatex()
                chi2text.SetTextFont(42)
                chi2text.SetTextSize(0.055)
                chi2text.DrawLatexNDC(0.60-offset,0.68,chi2dof2str)
                chi3text=ROOT.TLatex()
                chi3text.SetTextFont(42)
                chi3text.SetTextSize(0.055)
                chi3text.DrawLatexNDC(0.60-offset,0.62,chi2dof3str)
                chi4text=ROOT.TLatex()
                chi4text.SetTextFont(42)
                chi4text.SetTextSize(0.055)
                chi4text.DrawLatexNDC(0.60-offset,0.56,chi2dof4str)
                chitexts.append(chi1text)
                chitexts.append(chi2text)
                chitexts.append(chi3text)
                chitexts.append(chi4text)
                
            # draw the legend
            if ptindex==4:
                leg1=ROOT.TLegend(0.45,0.30,0.90,0.65)
                leg1.SetBorderSize(0)
                leg1.SetFillColor(0)
                leg1.SetTextFont(42)
                leg1.SetTextSize(0.07)
                leg1.AddEntry(plot.findObject("data"), "data", "ep")
                if wbin=="asymnoniso":
                    leg1.AddEntry(plot.findObject("bkg0"), "bkgd", "l")
                    leg1.AddEntry(plot.findObject("bkg1"), "bkgd*Bern1", "l")
                    leg1.AddEntry(plot.findObject("bkg2"), "bkgd*Bern2", "l")
                leg1.AddEntry(plot.findObject("bkg3"), "bkgd*Bern3", "l")
                leg1.Draw()
            if ptindex==9:
                leg2=ROOT.TLegend(0.45,0.30,0.90,0.65)
                leg2.SetBorderSize(0)
                leg2.SetFillColor(0)
                leg2.SetTextFont(42)
                leg2.SetTextSize(0.065)
                leg2.AddEntry(plot.findObject("data"), "data", "ep")
                if wbin=="asymnoniso":
                    leg2.AddEntry(plot.findObject("bkg0"), "bkgd", "l")
                    leg2.AddEntry(plot.findObject("bkg1"), "bkgd*Bern1", "l")
                    leg2.AddEntry(plot.findObject("bkg2"), "bkgd*Bern2", "l")
                    leg2.AddEntry(plot.findObject("bkg3"), "bkgd*Bern3", "l")
                else:
                    leg2.AddEntry(plot.findObject("bkg3"), "bkgd*Bern3", "l")
                    if doPullSig:
                        leg2.AddEntry(pull1sig, "Fit uncertainty", "f")
                leg2.Draw()
                
            # calculate the pulls
            pullpad.cd()
            pullHist = plot.pullHist("data","bkg3")
            pullPlot = ttw.m2p.frame()
            pullHist.SetMarkerSize(0.5)
            pullPlot.addPlotable(pullHist, "P")
            pullPlot.Draw()
 #           if wbin=="symiso":
 #               pull2sig.Draw("2")
#                pull1sig.Draw("2")
            pullPlot.SetMinimum(-3)
            pullPlot.SetMaximum(3)
            if ptindex%5==4:
                pullPlot.GetXaxis().SetTitle("M(2p) [GeV]")
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

            line = ROOT.TLine()
            line.SetNDC(False)
            line.SetX1(0.25)
            line.SetX2(5.65)
            line.SetY1(0)
            line.SetY2(0)
            line.SetLineWidth(1)
            line.SetLineColor(colors[3])
            line.SetLineStyle(3)
            line.Draw()
            line.DrawClone()
            pullpad.Update()

            
        # set the plots to the same maximum value (need to split this in two)
        max1=0.
        max2=0.
        for ind, plot in enumerate(plotlist):
            if ind<5 and plot.GetMaximum()>max1:
                max1=plot.GetMaximum()
            if ind>=5 and plot.GetMaximum()>max2:
                max2=plot.GetMaximum()
        for ind, plot in enumerate(plotlist):
            if ind<5:
                plot.SetMaximum(max1)
            else:
                plot.SetMaximum(max2)

        for can in canlist:

            can.cd()
            # Write CMS stuff
            cmstxt = ROOT.TLatex()
            cmstxt.SetTextFont(61)
            cmstxt.SetTextSize(0.07)
            cmstxt.DrawLatexNDC(0.03,0.935,"CMS")
            extratxt = ROOT.TLatex()
            extratxt.SetTextFont(52)
            extratxt.SetTextSize(0.05)
            if wbin=="asymnoniso":
                extratxt.DrawLatexNDC(0.073,0.935,"Preliminary")
            else:
                extratxt.DrawLatexNDC(0.073,0.935,"Preliminary")
            lumitxt = ROOT.TLatex()
            lumitxt.SetTextFont(42)
            lumitxt.SetTextSize(0.05)
            lumitxt.DrawLatexNDC(0.9,0.935,"59 fb^{-1} (13 TeV)")

            can.Update()
            can.Draw()
            can.SaveAs("../plots/"+can.GetName()+".pdf")


# draw Chi^2 probability distributions
for windex, wbin in enumerate(ttw.wbins):
    can = ROOT.TCanvas("cprob"+wbin,"cprob"+wbin,500,500)
    can.cd()
    h=hchi2probs[windex]
    h.Draw()
    h.SetMinimum(0)
    h.GetXaxis().SetTitle("#chi^{2} probability")
    h.GetYaxis().SetTitle("frequency")
    h.SetTitle(wtitles[windex])
    can.SetTopMargin(0.1)
    can.Update()
    can.Draw()
    can.SaveAs("../plots/"+can.GetName()+".pdf")
