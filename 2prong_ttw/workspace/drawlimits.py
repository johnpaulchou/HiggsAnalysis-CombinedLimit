import tdrstyle
import ROOT
import array as ar

tdrstyle.setTDRStyle()

x = [0.5, 0.75, 0.85, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0 ]
ex = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1 ]
obs = [0.106600, 0.338700, 0.492200, 0.778700, 5.727500, 3.461200, 3.998900, 1.373300, 4.034700]
e25 = [0.026200, 0.182100, 0.271200, 0.490100, 1.489700, 1.573200, 1.452600, 1.207800, 1.067500]
e16 = [0.039600, 0.254800, 0.381200, 0.674800, 1.942400, 2.051200, 1.922800, 1.624000, 1.453100]
e50 = [0.064500, 0.376000, 0.564500, 0.972700, 2.648400, 2.796900, 2.656200, 2.273400, 2.054700]
e84 = [0.106100, 0.561800, 0.841200, 1.406900, 3.661900, 3.856000, 3.693900, 3.179600, 2.931000]
e97 = [0.164400, 0.795800, 1.186500, 1.933900, 4.879900, 5.109000, 4.943800, 4.273500, 4.161900]

exp = [0, 0, 0, 0, 0, 0, 0, 0, 0]
eyl = [0, 0, 0, 0, 0, 0, 0, 0, 0]
eyh = [0, 0, 0, 0, 0, 0, 0, 0, 0]
eyl2 =[0, 0, 0, 0, 0, 0, 0, 0, 0]
eyh2 =[0, 0, 0, 0, 0, 0, 0, 0, 0]

br=0.2734126
for i in range(9):
    obs[i]=(obs[i]/br)**.5
    exp[i]=(e50[i]/br)**.5
    eyl[i]=exp[i]-(e16[i]/br)**.5
    eyh[i]=(e84[i]/br)**.5-exp[i]
    eyl2[i]=exp[i]-(e25[i]/br)**.5
    eyh2[i]=(e97[i]/br)**.5-exp[i]

    
g = ROOT.TGraphErrors(9, ar.array('d',x),  ar.array('d',obs))
gexp = ROOT.TGraphErrors(9, ar.array('d',x), ar.array('d',exp))
ge1 = ROOT.TGraphAsymmErrors(9, ar.array('d',x),  ar.array('d',exp), ar.array('d',ex), ar.array('d',ex), ar.array('d',eyl), ar.array('d',eyh))
ge2 = ROOT.TGraphAsymmErrors(9, ar.array('d',x),  ar.array('d',exp), ar.array('d',ex), ar.array('d',ex), ar.array('d',eyl2), ar.array('d',eyh2))

can = ROOT.TCanvas("limits","limits",500,500)
can.cd()
can.SetMargin(0.16,0.05,0.15,0.10)
ge2.SetFillColor(ROOT.TColor.GetColor("#F5BB54"))
ge2.SetFillStyle(1001)
ge2.Draw("a3")
ge2.SetMinimum(0)
ge2.SetMaximum(7.0)
ge2.GetXaxis().SetTitle("m_{#omega} [GeV]")
ge2.GetYaxis().SetTitle("95% C.L. Lower limit on g_{#psi}")
ge1.SetFillColor(ROOT.TColor.GetColor("#607641"))
ge1.SetFillStyle(1001)
ge1.Draw("Same3l")
gexp.SetLineStyle(2)
gexp.Draw("SAME L")
g.Draw("SAME LP")

leg = ROOT.TLegend(0.5,0.65,0.9,0.85)
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
lumitxt.DrawLatexNDC(0.65,0.91,"59 fb^{-1} (13 TeV)")

brtxt = ROOT.TLatex()
brtxt.SetTextFont(42)
brtxt.SetTextSize(0.04)
brtxt.DrawLatexNDC(0.65,0.20,"#eta BRs")

can.Update()
can.Draw()
can.Print("limits.pdf")
