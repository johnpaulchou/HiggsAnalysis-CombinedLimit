import ROOT
from scipy.interpolate import interp1d

# set the omega mass and phi mass values here
wmass=0.55
pmass=451
tlabel=str(pmass)+"_"+str(wmass)

# interpolate the cross section
theory_xs = [(450., 585.983), (500., 353.898), (625., 117.508), (750., 45.9397), (875., 20.1308),
             (1000., 9.59447), (1125., 4.88278), (1250., 2.61745), (1375., 1.46371),
             (1500., 0.847454), (1625., 0.505322), (1750., 0.309008), (1875., 0.192939),
             (2000., 0.122826), (2125., 0.0795248), (2250., 0.0522742), (2375., 0.0348093),
             (2500., 0.0235639), (2625., 0.0161926), (2750., 0.0109283), (2875., 0.00759881)]
x=list(zip(*theory_xs))
interp=interp1d(x[0], x[1])
xsec=interp(pmass)
print("The interpolated cross section is "+str(xsec)+" fb.")

# compute the acceptance*efficiency
acceff = 1.0

# make sure that the signal shape is normalized to unity


# where to write things out
fileout = ROOT.TFile("sigworkspace_"+tlabel+".root", "RECREATE")
w = ROOT.RooWorkspace("w","w")


#w.Print()
#fileout.cd()
#w.Write()
#fileout.Close()
