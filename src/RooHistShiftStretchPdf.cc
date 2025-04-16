//---------------------------------------------------------------------------
#include "RooFit.h"
#include "RooRealVar.h"
#include "RooAbsReal.h"
#include "TSpline.h"
#include "RooBinning.h"

#include "Riostream.h"

#include "../interface/RooHistShiftStretchPdf.h"

using namespace std;
using namespace RooFit;

ClassImp(RooHistShiftStretchPdf)

RooHistShiftStretchPdf::RooHistShiftStretchPdf(const char *name, const char *title, const RooArgSet& vars,
			 const RooDataHist& dhist, Int_t intOrder, RooAbsReal& shift, RooAbsReal& stretch, RooAbsReal& fixedPoint)
: RooHistPdf(name, title, vars, dhist, intOrder),
  _shift("shift", "shift", this, shift),
  _stretch("stretch", "stretch", this, stretch),
  _fixedPoint("fixedPoint", "fixedPoint", this, fixedPoint) {
  if(_histObsList.size()!=1 || _pdfObsList.size()!=1) {
    coutE(InputArguments) << "RooHistShiftStretchPdf::ctor(" << GetName()
           << ") Can only run with 1D histogram for now." << std::endl ;
    assert(0) ;
  }
  _spline=nullptr;
}

const TSpline5* RooHistShiftStretchPdf::getSpline(void) const
{
  if(_spline) return _spline;

  std::vector<double> xVals;
  std::vector<double> yVals;

  // Get the variable(s) associated with the RooDataHist
  auto var_set = _dataHist->get();
  const RooRealVar* variable = dynamic_cast<const RooRealVar*>(var_set->first());
  const RooAbsBinning* binning = &variable->getBinning();

  
  // Loop over all bins in the RooDataHist and integrate to compute the CDF
  xVals.push_back(binning->binLow(0));
  yVals.push_back(0.0);
  for(int i = 0; i < _dataHist->numEntries(); ++i) {
    double xval=binning->binHigh(i);
    xVals.push_back(xval);
    double sum=0.0;
    for(int j=0; j<= i; ++j)
      sum += _dataHist->weight(j)*binning->binWidth(j);
    yVals.push_back(sum);
  }

  // Create a TGraph from the collected points
  TGraph graph(xVals.size(), xVals.data(), yVals.data());

  // Create and return the TSpline5
  _spline = new TSpline5("spline", &graph);
  return _spline;
}


double RooHistShiftStretchPdf::evaluate() const
{
  // evaluate the histogram first (this is necessary for some unknown reason)
  RooHistPdf::evaluate();
  
  // get the position to evaluate at
  RooRealVar *param=dynamic_cast<RooRealVar*>(_histObsList[0]);
  
  double val=param->getVal();
  double valprime = (val-_fixedPoint-_shift)/_stretch+_fixedPoint;
  
  // get the spline of the CDF and it's derivative at the point
  const TSpline5* spline=getSpline();
  double deriv=spline->Derivative(valprime);
  if(deriv<0.0) deriv=0.0;

  return deriv;
}

Int_t RooHistShiftStretchPdf::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName) const
{
  //  if(matchArgs(allVars,analVars,_histObsList)) return 1;
  return 0;
}

/*
Double_t RooHistShiftStretchPdf::analyticalIntegral(Int_t code, const char* rangeName) const
{
  // evaluate the histogram first (this is necessary for some unknown reason)
   RooHistPdf::evaluate();

  const TSpline5* spline=getSpline();

  // get the position to evaluate at
  RooRealVar *param=dynamic_cast<RooRealVar*>(_histObsList[0]);
  double maxVal=param->getMax();
  return spline->Eval(maxVal);
}

*/
