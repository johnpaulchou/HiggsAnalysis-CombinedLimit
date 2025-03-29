import ROOT
import array
import ctypes
import numpy as np


"""
Retrieve a TH1 object from a ROOT file

Parameters:
    - histname: name of the TH1 object
    - filename: name of the ROOT file to read

Returns:
    - TH1 object
"""
def get_TH1_from_file(filename,histname):
    rootfile = ROOT.TFile(filename, "READ")
    if not rootfile or rootfile.IsZombie():
        print("Error: Unable to open file '{filename}'.")
        return None
    
    hist = rootfile.Get(histname)
    if not hist or not isinstance(hist, ROOT.TH1) or hist is None:
        print("Error: Histogram '", histname, "' not found or is not a valid TH1 object in the file '", filename ,"'.")
        exit(1)
        rootfile.Close()
        return None
    hist.SetDirectory(0)
    rootfile.Close()
    return hist



"""
Retrieve the title of a TNamed object from a ROOT file

Parameters:
    - file_path: Path to the ROOT file containing the TNamed object
    - tnamed_name: name of the TNamed object

Returns:
    - string
"""
def get_tnamed_title_from_file(file_path, tnamed_name):
    # Open the ROOT file
    root_file = ROOT.TFile.Open(file_path, "READ")
    if not root_file or root_file.IsZombie():
        raise RuntimeError(f"Cannot open file: {file_path}")

    # Get the TNamed object
    tnamed = root_file.Get(tnamed_name)
    if not tnamed:
        root_file.Close()
        raise RuntimeError(f"Cannot find TNamed '{tnamed_name}' in file: {file_path}")

    # get the title before closing the file
    title = tnamed.GetTitle()
    root_file.Close()

    return title



"""
Retrieve a RooWorkspace from a ROOT file

Parameters:
    - file_path: Path to the ROOT file containing the workspace
    - workspace_name: Name of the RooWorkspace in the file

Returns:
    - RooWorkspace object
"""
def get_workspace_from_file(file_path, workspace_name):
    # Open the ROOT file
    root_file = ROOT.TFile.Open(file_path, "READ")
    if not root_file or root_file.IsZombie():
        raise RuntimeError(f"Cannot open file: {file_path}")
    
    # Get the workspace
    workspace = root_file.Get(workspace_name)
    if not workspace:
        root_file.Close()
        raise RuntimeError(f"Cannot find workspace '{workspace_name}' in file: {file_path}")

    # Clone to avoid dependence on file
    ws_clone = workspace.Clone()

    # Close the file
    root_file.Close()

    return ws_clone


"""
Retrieve a TGraphAsymmErrors from a RooDataHist inside a RooWorkspace
    
Parameters:
    - workspace: RooWorkspace to retrieve RooAbsPdf
    - datahist_name: Name of the specific RooDataHist to retrieve
    
Returns:
    - TGraphAsymmErrors object and associated RooRealVar
"""
def get_datagraph_from_workspace(workspace, datahist_name):
    # get the datahist
    datahist = workspace.data(datahist_name)
    if not datahist:
        raise RuntimeError(f"Cannot find RooDataHist '{datahist_name}' in workspace '{workspace.GetName()}'")
    
    # Get the variable(s) associated with the RooDataHist
    var_set = datahist.get()
    variable = var_set.first()
    if not variable:
        raise RuntimeError("Cannot find associated variable for the RooDataHist")

    # get binning
    binning = variable.getBinning()
    
    # create a TH1D first
    hist = datahist.createHistogram(datahist_name+"_temporary_hist",variable)

    # create the TGraphAsymmErrors
    gr=ROOT.TGraphAsymmErrors(hist)

    # compute the Poisson uncertainties and divide out by the bin width
    alpha = 1 - 0.6827
    for i in range(gr.GetN()):
        N = gr.GetPointY(i)
        width = binning.binWidth(i)
        L = 0
        if N>0: L=ROOT.Math.gamma_quantile(alpha/2,N,1.)
        U =  ROOT.Math.gamma_quantile_c(alpha/2,N+1,1)
        gr.SetPointEYlow(i, (N-L)/width)
        gr.SetPointEYhigh(i, (U-N)/width)
        gr.SetPointY(i, N/width)

    # set the x-axis range
    gr.GetXaxis().SetRangeUser(binning.binLow(0),binning.binHigh(binning.numBins()-1))
    return gr, variable


"""
Create a set of bin boundaries based off a RooBinning

Parameters:
    - binning: RooBinning that you want to use

Returns:
    - c_array_type with the proper bin edges
"""
def get_carray_from_binning(binning):
     # get the variable's binning
    nbins = binning.numBins()
    bin_edges = [binning.binLow(i) for i in range(nbins)]
    bin_edges.append(binning.binHigh(nbins-1)) #append last bin high edge
    c_array_type = ctypes.c_float * len(bin_edges)
    c_array = c_array_type(*bin_edges)
    return c_array





"""
Convert a RooAbsPdf to a TH1D histogram with given normalization.
    
Parameters:
    - pdf: RooAbsPdf object to convert
    - binning: RooBinning that you want to use
    - hist_name: Name of the output histogram
    - normalization: Desired integral of the histogram (default: 1.0)

Returns:
    - TH1D histogram object
"""
def pdf_to_histogram(pdf, binning, hist_name, normalization=1.0):

    # Create histogram
    hist = ROOT.TH1D(hist_name, hist_name, binning.numBins(), get_carray_from_binning(binning))

    # Get the RooRealVar
    obs = pdf.getVariables().first()

    # Fill histogram by evaluating PDF at bin centers
    for i in range(1, binning.numBins() + 1):
        x = hist.GetBinCenter(i)
        obs.setVal(x)
        pdf_value = pdf.getVal(ROOT.RooArgSet(obs))
        hist_val = pdf_value * normalization
        hist.SetBinContent(i, hist_val)
    
    return hist



"""
Estimate the 1-sigma uncertainty envelope of a function using Monte Carlo sampling.

Parameters:
    - pdf: RooAbsPdf. The pdf to evaluate, which accepts parameters and x as inputs.
    - fitresult: RooFitResult of the fit which we want to get the envelope for.
    - binning: RooBinning that you want to use
    - num_samples: Number of Monte Carlo samples to generate.

Returns:
    - list of uncertainties evaluated at the central value of the bins

"""

def monte_carlo_uncertainty_envelope(pdf, normalization, fitresult, binning, num_samples=1000):

    # first thing is to copy the pdf so that we don't mess with the parameters
    # then, get the variables and observable for the pdf, and create a argument set for the observable
    pdf_copy = pdf.Clone(pdf.GetName()+"_copy")
    variables = pdf_copy.getVariables()
    observable = variables.first()
    argset = ROOT.RooArgSet(observable)
    
    # get the parameters from the fit and then put their values into the means
    params = fitresult.floatParsFinal()
    param_means = [params[i].getVal() for i in range(params.getSize())]

    # get the covariance matrix for the fit
    cov=fitresult.covarianceMatrix()
    size=cov.GetNrows()
    param_cov=np.zeros((size, size))
    for i in range(size):
        for j in range(size):
            param_cov[i, j] = cov[i][j]  # Access matrix elements

    # get the central values of the bins we are evaluating the pdf at
    x_values = [binning.binCenter(i) for i in range(binning.numBins())]

    # Generate random samples of parameters
    param_samples = np.random.multivariate_normal(param_means, param_cov, num_samples)
    
    # Initialize array to store function evaluations
    func_evals = np.zeros((num_samples, len(x_values)))

    # Evaluate the function for each parameter sample
    for i, params in enumerate(param_samples):

        # set the parameters
        for j,parameter in enumerate(params):
            variables[j+1].setVal(parameter)

        # set the x value and evaluate
        for k,x in enumerate(x_values):
            variables[0].setVal(x)
            func_evals[i, k] = pdf_copy.getVal(argset)*normalization

    # Compute mean and standard deviation at each x
    # mean_values = np.mean(func_evals, axis=0)
    std_devs = np.std(func_evals, axis=0)
    return std_devs

