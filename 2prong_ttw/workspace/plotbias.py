import makeworkspace as ttw
import ROOT
import argparse
import re
import numpy
import tdrstyle

###############################################################
# start of the "main" function
###############################################################

if __name__ == "__main__":

    # setup parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("files", nargs="+", help="A list of root files")
    args = parser.parse_args()

    # setup output for printing
    pdffilename="../plots/biasfits.pdf"
    first=True

    # stuff to plot
    data = {}
    
    # loop over the files that are passed to the command line
    for filename in args.files:

        # Try to open the ROOT TFile
        rootfile = ROOT.TFile(filename, "READ")
        if not rootfile or rootfile.IsZombie():
            print("Error: Unable to open file "+filename+".")
            continue

        # parse the filename to get the parameters
        # NB that this assumes it takes the form, fitDiagnosticsTest_m${mass}_sig${strength}.root, which should come from runbias.sh
        # This code won't work if that formula is changed
        m = re.search('fitDiagnosticsTest_m(.+?)_sig(.+?).root', filename)
        if m:
            try:
                imass=int(m.group(1))
                mu=float(m.group(2))
            except ValueError:
                print("Could not convert "+m.group(1)+" and "+m.group(2)+" into numbers")
                continue
        else:
            print("Could not parse the file "+filename+" according to the regex.")
            continue

        # Try to get the tree
        treename="tree_fit_sb"
        tree = rootfile.Get(treename)
        if not tree or not isinstance(tree, ROOT.TTree) or tree is None:
            print("Error: Tree '", treename, "' not found or is not a valid TTree object in the file '", filename ,"'.")
            continue

        # now create a histogram to be filled
        histname="hist_"+str(imass)+"_"+str(mu)
        hist = ROOT.TH1D(histname,"#mu="+str(mu)+"; "+ttw.sigmasses[imass],50,-5,5)
        tree.Project(histname,"(r-"+str(mu)+")/(0.5*(rHiErr+rLoErr))","fit_status==0")

        # create the canvas to draw on and format it
        can=ROOT.TCanvas("c_"+str(imass)+"_"+str(mu),"can",400,400)
        can.SetFillColor(0)
        can.SetBorderMode(0)
        can.SetFrameFillStyle(0)
        can.SetFrameBorderMode(0)
        can.SetTickx(0)
        can.SetTicky(0)

        # draw the histogram and extract the fit info
        can.cd()
        hist.Draw()
        result=hist.Fit("gaus","s")
        mass=float(ttw.sigmasses[imass][1:])

        # a point has a mass, the mean, and the error on the mean
        p = (mass, result.Parameters()[1], result.ParError(1))

        # add the point to the data dictionary
        if mu in data: data[mu].append(p)
        else: data[mu]=[p]
        
        # save it to a file
        if first:
            can.Print(pdffilename+"(",".pdf")
            first=False
        else:
            can.Print(pdffilename,".pdf")

    # graph+mu value pairs
    graphandmus = []
    
    # now create a plot with the biases that we fit for
    for muindex, mu in enumerate(data):

        # for each mu value, get the data in a convenient format
        npoints = len(data[mu])
        x    = numpy.array([p[0] for p in data[mu]], dtype=numpy.float64)
        y    = numpy.array([p[1] for p in data[mu]], dtype=numpy.float64)
        xerr = numpy.zeros(npoints)
        yerr = numpy.array([p[2] for p in data[mu]], dtype=numpy.float64)

        # offset the x index slightly based on the muindex
        for i in range(len(x)):
            x[i]=x[i]+muindex*20.
        
        # create a new graph
        graph = ROOT.TGraphErrors(npoints,x,y,xerr,yerr)
        graphandmus.append((graph,mu))

    # Create a canvas to draw the graphs
    can = ROOT.TCanvas("cBias","cBias",500,300)
    can.cd()
    can.SetFillColor(0)
    can.SetBorderMode(0)
    can.SetFrameFillStyle(0)
    can.SetFrameBorderMode(0)
    can.SetTickx(0)
    can.SetTicky(0)

    # Format the graphs by getting the first graph
    firstgr=graphandmus[0][0]
    firstgr.GetXaxis().SetTitle("M_{#omega} [MeV]")
    firstgr.GetYaxis().SetTitle("Bias")
    firstgr.SetTitle("")
    for grindex, graphmupair in enumerate(graphandmus):
        gr=graphmupair[0]
        gr.SetMarkerStyle(20+grindex)
        gr.SetMarkerColor(tdrstyle.colors[grindex])
        gr.SetLineColor(tdrstyle.colors[grindex])
        gr.SetLineWidth(2)
        if grindex==0:
            gr.Draw("AP")
        else:
            gr.Draw("P")

    # Draw Legend
    leg = ROOT.TLegend(0.7,0.15,0.85,0.35)
    leg.SetBorderSize(0)
    leg.SetFillColor(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.05)
    for graphmupair in graphandmus:
        leg.AddEntry(graphmupair[0], "#mu="+str(graphmupair[1]), "p")
    leg.Draw()

    # Draw Box
    box = ROOT.TBox(firstgr.GetXaxis().GetXmin(), -0.1, firstgr.GetXaxis().GetXmax(), 0.1)
    box.SetFillColorAlpha(ROOT.kBlack,0.1)
    box.Draw()
    
    can.Print(pdffilename+")",".pdf")
