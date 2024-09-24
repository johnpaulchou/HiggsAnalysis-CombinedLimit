import ROOT

# where to write things out
fileout = ROOT.TFile("ttpworkspace.root","RECREATE")
w = ROOT.RooWorkspace("w","w")

ptbins = [20, 40, 60, 80, 100, 140, 180, 220, 300, 380 ]
btags = "1b"
# btags = "mb"
datalabel = "singlemuon_symiso"
#datalabel = "singlemuon_asymnoniso"
