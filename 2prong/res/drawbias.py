#!/bin/env python3

import ROOT
import argparse
import re
import numpy
import sys
import common.tdrstyle as tdrstyle
import files

###############################################################
# start of the "main" function
###############################################################

def getfixindex(fix, test):
    if fix == 0 and test == 0: return 1
    if fix == 0 and test == 1: return 2
    if fix == 0 and test == 2: return 3
    if fix == 1 and test == 0: return 4
    if fix == 1 and test == 1: return 5
    if fix == 1 and test == 2: return 6
    if fix == 2 and test == 0: return 7
    if fix == 2 and test == 1: return 8
    if fix == 2 and test == 2: return 9

if __name__ == "__main__":


    # setup parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("files", nargs="+", help="A list of root files")
    args = parser.parse_args()

    # setup output for printing
    pdffilename="./plots/biasfits.pdf"
    pdfsummaryfilename="./plots/biasfits_summary.pdf"
    first=True

    # stuff to plot
    plotdata = {}
    
    # loop over the files that are passed to the command line
    for filename in args.files:

        print('DEBUG', filename)

        # Try to open the ROOT TFile
        rootfile = ROOT.TFile(filename, "READ")
        if not rootfile or rootfile.IsZombie():
            print("Error: Unable to open file "+filename+".")
            continue

        # parse the filename to get the parameters
        # NB that this assumes it takes the form, fitDiagnosticsTest_m${mass}_sig${strength}.root, which should come from runbias.sh
        # This code won't work if that formula is changed
        m = re.search('fitDiagnosticsTest_m(.+?)_sig(.+?)_gen(.+?)_test(.+?).root', filename)
        if m:
            try:
                imass=int(m.group(1))
                mu=float(m.group(2))
                fix=float(m.group(3))
                test=float(m.group(4))
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
        #hist = ROOT.TH1D(histname,"#mu="+str(mu)+"; "+ttw.sigmasses[imass],50,-5,5)


        title = "#mu="+str(mu)+", fix {:n} test {:n} ; ".format(fix, test) + str(imass)
        hist = ROOT.TH1D(histname,title,50,-5,5)

        #tree.Project(histname,"(r-"+str(mu)+")/(0.5*(rHiErr+rLoErr))","fit_status==0")
        tree.Project(histname,"(r-"+str(mu)+")/(0.5*(rHiErr+rLoErr))", "r>-49 && r<50 && fit_status!=-1")
        #tree.Draw("(r-"+str(mu)+")/(0.5*(rHiErr+rLoErr)) >> "+histname)

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

        #test = input()

        result=hist.Fit("gaus","sL")
        #mass=float(ttw.sigmasses[imass][1:])
        mass=int(imass)

        print(result.GetName())


        # a point has a mass, a function pair label, the mean, and the error on the mean
        #p = (mass, result.Parameters()[1], result.ParError(1))
        fixindex = getfixindex(fix, test)
        p = (mass, fixindex, result.Parameters()[1], result.ParError(1))

        # add the point to the data dictionary
        if mass in plotdata:
            if mu in plotdata[mass]: plotdata[mass][mu].append(p)
            else: plotdata[mass][mu] = [p] # mass present but new mu
        else: plotdata[mass] = {mu: [p]} # new mass and thus new mu

        #if mu in data: data[mu].append(p)
        #else: data[mu]=[p]
        
        # save it to a file
        if first:
            can.Print(pdffilename+"(",".pdf")
            first=False
        else:
            can.Print(pdffilename,".pdf")

    for mass in plotdata:
        print(mass)
        for mu in plotdata[mass]:
            print("  ", mu, " maps to ", len(plotdata[mass][mu]))

    can.Print(pdffilename+"]")

    # sort data from lowest to highest mu
    #datatemp = data
    #data = sorted(datatemp, key = lambda x: float(x))
    #print(datatemp)
    #print(data)

    print()


    
    can = ROOT.TCanvas("cBias","cBias",500,300)
    can.Print(pdfsummaryfilename+"[",".pdf")
    for mass in plotdata:
    
        print()
        data = plotdata[mass]
        
        for mu in data:
            print(mu)
            for entry in data[mu]:
                print("  ", entry)
        
        windex, pindex = files.indexpair(int(mass))
        pmass, wmass = files.pmasspoints[pindex], files.wmasspoints[windex]        
        Title = "(M_#Phi, M_#omega) = ({}, {}) GeV".format(pmass, wmass)
                
        # graph+mu value pairs
        graphandmus = []
        
        # now create a plot with the biases that we fit for
        for muindex, mu in enumerate(sorted(data.keys(), key = lambda x : float(x))):

            # for each mu value, get the data in a convenient format
            npoints = len(data[mu])
            x    = numpy.array([p[1] for p in data[mu]], dtype=numpy.float64)
            y    = numpy.array([p[2] for p in data[mu]], dtype=numpy.float64)
            xerr = numpy.zeros(npoints)
            yerr = numpy.array([p[3] for p in data[mu]], dtype=numpy.float64)

            # offset the x index slightly based on the muindex
            for i in range(len(x)):
                x[i]=x[i]+muindex*0.05
            
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
        #firstgr.GetXaxis().SetTitle("M_{#omega} [MeV]")
        firstgr.GetXaxis().SetTitle("Func pair (gen,test)")
        firstgr.GetYaxis().SetTitle("Bias")
        firstgr.SetTitle(Title)
        firstgr.GetYaxis().SetRangeUser(-2.5,2.5)
        #firstgr.GetXaxis().SetRangeUser(-1.,20.)
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
            gr.GetXaxis().SetLimits(0,10)

        # Change labels
        xaxis = firstgr.GetXaxis()
        
        labels = [' ', '(0,0)', '(0,1)', '(0,2)', '(1,0)', '(1,1)', '(1,2)', '(2,0)', '(2,1)', '(2,2)', ' ']
        for i, label in enumerate(labels, start=1):
            xaxis.ChangeLabel(i, -1, -1, -1, -1, -1, label) # (bin_number, angle, size, align, color, font, label_text)
        can.Modified()
        can.Update()

        # Draw Legend
        leg = ROOT.TLegend(0.83,0.13,0.98,0.36)
        leg.SetBorderSize(1)
        leg.SetFillColor(0)
        #leg.SetFillColorAlpha(0, 0.01);
        leg.SetTextFont(42)
        leg.SetTextSize(0.05)
        for graphmupair in graphandmus:
            leg.AddEntry(graphmupair[0], "#mu="+str(graphmupair[1]), "p")
        leg.Draw()

        # Draw Box
        box = ROOT.TBox(firstgr.GetXaxis().GetXmin(), -0.5, firstgr.GetXaxis().GetXmax(), 0.5)
        box.SetFillColorAlpha(ROOT.kBlack,0.1)
        box.Draw()
        
        can.Print(pdfsummaryfilename,".pdf")

    can.Print(pdfsummaryfilename+"]",".pdf")
