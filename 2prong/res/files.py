#!/bin/env python3

import ROOT
import sys
import numpy
import array
import re
import os
from scipy.stats import norm

# signal types
sigtypes = ["eta","etaprime"]

# regions to consider
regions = ["sideband","signal"]
etabins = ["barrel","endcap"]

# toggle for extended phi range
crop_style = 1

# toggle for extra grid points
extra_points = 0

# omega mass bin boundaries
def get_m2pbin_boundaries(region, sigtype, etabin=''):
    if crop_style == 0:
        if sigtype==sigtypes[0]:
            return (1,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,27)
        elif sigtype==sigtypes[1]:
            return (8,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,27)
    else:
        if sigtype==sigtypes[0]:
            return (1,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,27)
        elif sigtype==sigtypes[1] and etabin==etabins[0]:
            return (6,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,27)
        elif sigtype==sigtypes[1] and etabin==etabins[1]:
            return (6,9,10,11,12,13,14,15,16,17,18,19,20,21,27)
        elif sigtype==sigtypes[1]:
            print('ERR: supply etabin to get_m2pbin_boundaries()!')
            return (0)

def get_num_m2pbins(region, sigtype, etabin=''):
    return len(get_m2pbin_boundaries(region, sigtype, etabin))-1

# setup observables
if crop_style == 0:
    m2pg = ROOT.RooRealVar("m2pg","Invariant mass of the 2-prong and photon",500,3998)
    m2pg_sig = m2pg
    m2p = ROOT.RooRealVar("m2p","Invariant mass of the 2-prong",0.4,5.33)
if crop_style == 1 or crop_style == 2:
    m2pg = ROOT.RooRealVar("m2pg","Invariant mass of the 2-prong and photon",520,3998)
    m2pg_sig = ROOT.RooRealVar("m2pg_sig","Invariant mass of the 2-prong and photon for the signal pdfs only",396,3998)
    m2p = ROOT.RooRealVar("m2p","Invariant mass of the 2-prong",0.4,5.33)
if crop_style == 3:
    m2pg = ROOT.RooRealVar("m2pg","Invariant mass of the 2-prong and photon",563,3998)
    m2pg_sig = ROOT.RooRealVar("m2pg_sig","Invariant mass of the 2-prong and photon for the signal pdfs only",396,3998)
    m2p = ROOT.RooRealVar("m2p","Invariant mass of the 2-prong",0.4,5.33)

# list of systematics
systs = [ "", "_shiftUp", "_shiftDown", "_stretchUp", "_stretchDown", "_scaleUp", "_scaleDown", "_resUp", "_resDown" ]
#systs = [ "" ]

# signal and background workspace filenames
sigworkspacefn="sigworkspace.root"
bkgworkspacefn="bkgworkspace.root"
workspacename="w"

# input path
input_top_level = './input'
signal_input = 'signal_10percent_lowerphimass_eta'
data_input = '.'
datafilename = "{}/{}/egamma2018full.root".format(input_top_level, data_input)

# luminosity for the dataset
luminosity=138

# set up the grid of generated points and their corresponding input files
gengridw = ( (0.5, "0p5"), (0.75, "0p750"), (0.85, "0p850"), (1.0, "1p0"), (2.0, "2p0"), (3.0, "3p0"), (4.0, "4p0") )
gengridp = ( (500, "500"), (750, "750"), (1000., "1000"), (1500, "1500"), (2500., "2500"), (3000., "3000"))
genfilenames = [ [""]*len(gengridw) for i in range(len(gengridp))]
for i in range(len(gengridw)):
    for j in range(len(gengridp)):
        genfilenames[j][i]="./input/signal_"+gengridp[j][1]+"_"+gengridw[i][1]+".root"

# omega and phi mass points to run over
wmasspoints = numpy.linspace(0.5, 3.95, 24)
pmasspoints = numpy.linspace(550, 2920, 80)
if extra_points == 1:
    add_w_points = [2.0, 3.0]
    add_p_points = [1000, 1500]
    for point in add_w_points:
        if not numpy.any(numpy.isclose(wmasspoints, point)):
            wmasspoints = numpy.insert(wmasspoints, numpy.searchsorted(wmasspoints, point), point)
            wmasspoints = numpy.sort(wmasspoints)  # safety net if wmasspoints isn't already sorted
    for point in add_p_points:
        if not numpy.any(numpy.isclose(pmasspoints, point)):
            pmasspoints = numpy.insert(pmasspoints, numpy.searchsorted(pmasspoints, point), point)
            pmasspoints = numpy.sort(pmasspoints)  # safety net if pmasspoints isn't already sorted
npoints = len(wmasspoints)*len(pmasspoints)

# convert a single index into a wmassindex and a pmassindex
def indexpair(index):
    assert(index>=0 and index<npoints)
    windex = index % len(wmasspoints)
    pindex = int(index / len(wmasspoints))
    return (windex, pindex)

# convert a single index into a wmass and a pmass
def indexmasses(index):
    assert(index>=0 and index<npoints)
    windex = index % len(wmasspoints)
    pindex = int(index / len(wmasspoints))
    return (wmasspoints[windex], pmasspoints[pindex])

# convert a wmassindex and pmassindex to a single index (inverse of the above)
def index(wmassindex, pmassindex):
    assert(wmassindex>=0 and wmassindex<len(wmasspoints))
    assert(pmassindex>=0 and pmassindex<len(pmasspoints))
    return wmassindex+pmassindex*len(wmasspoints)

def indexof(wmass, pmass):
    w_idx = numpy.where(numpy.isclose(wmasspoints, wmass))[0]
    p_idx = numpy.where(numpy.isclose(pmasspoints, pmass))[0]
    if len(w_idx) == 0 or len(p_idx) == 0:
        return None
    #return w_idx[0], p_idx[0]
    return index(w_idx[0], p_idx[0])

# x-section as a function of m_phi from an interpolation of the phi masses
def get_xsection(phimass):
    theory_xs = [(450., 585.983), (500., 353.898), (625., 117.508), (750., 45.9397), (875., 20.1308),
                 (1000., 9.59447), (1125., 4.88278), (1250., 2.61745), (1375., 1.46371),
                 (1500., 0.847454), (1625., 0.505322), (1750., 0.309008), (1875., 0.192939),
                 (2000., 0.122826), (2125., 0.0795248), (2250., 0.0522742), (2375., 0.0348093),
                 (2500., 0.0235639), (2625., 0.0161926), (2750., 0.0109283), (2875., 0.00759881),
                 (3000., 0.00531361)]
    assert(phimass>=theory_xs[0][0] and phimass<=theory_xs[len(theory_xs)-1][0])
    for i in range(len(theory_xs) - 1):
        x0, y0 = theory_xs[i]
        x1, y1 = theory_xs[i + 1]
        if x0 <= phimass <= x1:
            return y0 + (y1 - y0) * (phimass - x0) / (x1 - x0)

def modify_significance(sig, factor):
    p = 1 - norm.cdf(sig)
    p_modified = p * factor
    if p_modified >= 1: return 0
    sig_modified = norm.ppf(1 - p_modified)
    return sig_modified

def massage(histo, style=""):
    nx = histo.GetNbinsX()
    ny = histo.GetNbinsY()
    #for y in range(ny, 0, -1):  # last y-bin first
    for y in range(1, ny):
        for x in range(1, nx+1):
            old = histo.GetBinContent(histo.GetBin(x, y))
            if style == "sideband_eta":
                if (y <= 15 and old > 0) or \
                   (x == 18 and y == 18) or \
                   (x == 13 and (y == 19 or y == 20 or y == 21)) or \
                   (x == 12 and (y >= 20 and y <= 23)) \
                :
                    histo.SetBinContent(histo.GetBin(x, y), -0.2)

# set up the grid of generated points and their corresponding input files
import os
import re
signal_fullpath = "{}/{}".format(input_top_level, signal_input)
files = os.listdir(signal_fullpath)
pattern = re.compile(r"signal_(\d+)_(\d+p\d+)\.root")
wmasses = set()
pmasses = set()
#print(files)
for f in files:
    m = pattern.match(f)
    if m:
        pmasses.add(m.group(1))
        wmasses.add(m.group(2))
def parse_w(s):
    return float(s.replace("p", "."))
def parse_p(s):
    return float(s)
gengridw = list(sorted((parse_w(s), s) for s in wmasses))
gengridp = list(sorted((parse_p(s), s) for s in pmasses))
#print("################")
#print(gengridw)
#print(gengridp)
#genfilenames = [ [""]*len(gengridw) for i in range(len(gengridp))] # old
genfilenames = [ [""]*len(gengridp) for i in range(len(gengridw))]
remove_w = set()
remove_p = set()
for i in range(len(gengridw)):
    for j in range(len(gengridp)):
        sigfilename="signal_"+gengridp[j][1]+"_"+gengridw[i][1]+".root"
        if sigfilename not in files:
            remove_w.add(gengridw[i])
            remove_p.add(gengridp[j])
#print(remove_w)
#print(remove_p)
for item in remove_w:
    gengridw.remove(item)
for item in remove_p:
    gengridp.remove(item)
#print(gengridw)
#print(gengridp)
#print("################")
for i in range(len(gengridw)):
    for j in range(len(gengridp)):
        sigfilename="signal_"+gengridp[j][1]+"_"+gengridw[i][1]+".root"
        if sigfilename in files:
            genfilenames[i][j] = "{}/{}".format(signal_fullpath, sigfilename)
        else:
            genfilenames[i][j] = "error"

genfilenames_raw = ['',]*npoints
signal_fullpath = "{}/{}".format(input_top_level, signal_input)
for fi in os.listdir(signal_fullpath):
    result = re.search(r"signal_(.+?)\.root", fi)
    if not result: continue
    masspoint_string = result.group(1)
    pmass_string = re.search(r"(.+?)_(.*)", masspoint_string).group(1)
    wmass_string = (re.search(r"(.+?)_(.*)", masspoint_string).group(2)).replace('p','.')
    masspoint_index = indexof(float(wmass_string), float(pmass_string))
    #print(masspoint_string, masspoint_index)
    if not masspoint_index == None: genfilenames_raw[masspoint_index] ="{}/signal_{}.root".format(signal_fullpath, masspoint_string)

# crop histogram bins
def crop_first_bins_variable(h, n_remove):
    nbins = h.GetNbinsX()
    if n_remove >= nbins:
        raise ValueError("Cannot remove all bins (or more).")

    xaxis = h.GetXaxis()

    # Extract original bin edges
    edges = [xaxis.GetBinLowEdge(1)]
    for i in range(1, nbins + 1):
        edges.append(xaxis.GetBinUpEdge(i))

    # Remove first n_remove bins → keep edges from that point onward
    new_edges = edges[n_remove:]

    # Convert to C-style array for ROOT
    edges_array = array.array('d', new_edges)

    # Create new histogram with variable binning
    h_new = ROOT.TH1D(
        h.GetName() + "_cropped",
        h.GetTitle(),
        len(edges_array) - 1,
        edges_array
    )

    # Copy contents and errors
    for i in range(1, h_new.GetNbinsX() + 1):
        old_bin = i + n_remove
        h_new.SetBinContent(i, h.GetBinContent(old_bin))
        h_new.SetBinError(i, h.GetBinError(old_bin))

    return h_new

def main():
    print("npoints:", npoints)
    print("pmasspoints:", pmasspoints)
    print("wmasspoints:", wmasspoints)
    print('(w, p) indexes and associated gen file')
    count = 0
    for n in range(npoints):
        print(n, indexpair(n), indexmasses(n), genfilenames_raw[n])
        if genfilenames_raw[n] != '':
            #print(n)
            count += 1
    print('points with genfile: {}'.format(count))
    #print('full gen grid:')
    #for i in range(len(gengridw)):
    #    for j in range(len(gengridp)):
    #        print(i, j, genfilenames[i][j])
    
    #for sig in sigtypes:
    #    for reg in regions:
    #        for etabin in etabins:
    #            print("{} {} {}: {}".format(sig, reg, etabin, get_num_m2pbins(reg, sig, etabin)))

if __name__ == "__main__":
    main()
