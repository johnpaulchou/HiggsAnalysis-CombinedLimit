//---------------------------------------------------------------------------
#include "RooFit.h"
#include <cassert>
#include "TSpline.h"

#include "../interface/RooHistMorphPdf.h"

using namespace std;
using namespace RooFit;

ClassImp(RooHistMorphPdf)

RooHistMorphPdf::RooHistMorphPdf(const char *name, const char *title, RooAbsReal& x, RooAbsReal& p, TH2* hist) : RooAbsPdf(name, title), _x("x", "Dependent variable", this, x), _p("p","p", this, p) {
  // clone the histogram that is passed
  assert(hist);
  TString newname(name);
  newname += "_RooHistMorphPdf";
  _hist=dynamic_cast<TH2*>(hist->Clone(newname));
}

RooHistMorphPdf::RooHistMorphPdf(const RooHistMorphPdf& other, const char* name) : RooAbsPdf(other, name), _x("x", this, other._x), _p("p", this, other._p) {
  // clone the histogram that is passed
  TString newname(name);
  newname += "_hist";
  _hist=dynamic_cast<TH2*>(other._hist->Clone(newname));
}

double RooHistMorphPdf::evaluate() const
{
  /*
  double bincenter=_hist->GetYaxis()->GetBinCenter(biny);
  if(_p<bincenter) { // if we're on the low side of things...
    double z0=_hist->GetBinContent(binx, biny-1);
    double y0=_hist->GetYaxis()->GetBinCenter(biny-1);
    double z1=_hist->GetBinContent(binx, biny);
    double y1=bincenter;
    return (z1-z0)*(_p-y0)/(y1-y0)+z0;
    
  } else if(_p<bincenter) { // if we're on the high side of things...
    double z0=_hist->GetBinContent(binx, biny);
    double y0=bincenter;
    double z1=_hist->GetBinContent(binx, biny+1);
    double y1=_hist->GetYaxis()->GetBinCenter(biny+1);
    return (z1-z0)*(_p-y0)/(y1-y0)+z0;

  } else { // if we're smack dab in the middle...
    return _hist->GetBinContent(binx, biny);
    } */

  
  int binx=_hist->GetXaxis()->FindBin(_x);

  // create the spline
  int n= _hist->GetNbinsY();
  Double_t *x=new Double_t[n];
  Double_t *y=new Double_t[n];
  for(int i=1; i<=n; i++) {
    x[i-1]=_hist->GetYaxis()->GetBinCenter(i);
    y[i-1]=_hist->GetBinContent(binx, i);
  }
  TSpline3 spline("spline",x,y,n);
  double val=spline.Eval(_p);
  delete x;
  delete y;
  return val;
}


//---------------------------------------------------------------------------
