import tdrstyle
import ROOT
import array as ar

tdrstyle.setTDRStyle()

'''
500
Observed Limit: r < 0.0139
Expected  2.5%: r < 0.0061
Expected 16.0%: r < 0.0092
Expected 50.0%: r < 0.0151
Expected 84.0%: r < 0.0253
Expected 97.5%: r < 0.0386

2000
Observed Limit: r < 0.4484
Expected  2.5%: r < 0.2791
Expected 16.0%: r < 0.3738
Expected 50.0%: r < 0.5215
Expected 84.0%: r < 0.7335
Expected 97.5%: r < 0.9865

4000
Observed Limit: r < 0.2223
Expected  2.5%: r < 0.1761
Expected 16.0%: r < 0.2378
Expected 50.0%: r < 0.3340
Expected 84.0%: r < 0.4738
Expected 97.5%: r < 0.6452
'''

x = [0.5, 2., 4. ]
ex = [0.1, 0.1, 0.1 ]
obs = [0.118, 0.670, 0.471 ]
exp = [0.123, 0.725, 0.578 ]
eyl = [0.027, 0.111, 0.090 ]
eyh = [0.036, 0.134, 0.110 ]
eyl2 =[0.045, 0.194, 0.158 ]
eyh2 =[0.074, 0.271, 0.225 ]

g = ROOT.TGraphErrors(3, ar.array('d',x),  ar.array('d',obs))
gexp = ROOT.TGraphErrors(3, ar.array('d',x), ar.array('d',exp))
ge1 = ROOT.TGraphAsymmErrors(3, ar.array('d',x),  ar.array('d',exp), ar.array('d',ex), ar.array('d',ex), ar.array('d',eyl), ar.array('d',eyh))
ge2 = ROOT.TGraphAsymmErrors(3, ar.array('d',x),  ar.array('d',exp), ar.array('d',ex), ar.array('d',ex), ar.array('d',eyl2), ar.array('d',eyh2))

can = ROOT.TCanvas("limits","limits",500,500)
can.cd()
can.SetMargin(0.16,0.05,0.15,0.10)
ge2.SetFillColor(ROOT.TColor.GetColor("#F5BB54"))
ge2.SetFillStyle(1001)
ge2.Draw("a3")
ge2.SetMinimum(0)
ge2.SetMaximum(1.2)
ge2.GetXaxis().SetTitle("m_{#omega} [GeV]")
ge2.GetYaxis().SetTitle("95% C.L. Lower limit on g_{#psi}")
ge1.SetFillColor(ROOT.TColor.GetColor("#607641"))
ge1.SetFillStyle(1001)
ge1.Draw("Same3l")
gexp.SetLineStyle(2)
gexp.Draw("SAME L")
g.Draw("SAME LP")

leg = ROOT.TLegend(0.5,0.2,0.9,0.4)
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

can.Update()
can.Draw()
can.Print("limits.pdf")
