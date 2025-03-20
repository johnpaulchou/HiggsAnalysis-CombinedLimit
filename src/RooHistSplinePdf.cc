//---------------------------------------------------------------------------
#include "RooFit.h"
#include "RooRealVar.h"
#include "RooAbsReal.h"

#include "Riostream.h"

#include "../interface/RooHistSplinePdf.h"

using namespace std;
using namespace RooFit;

ClassImp(RooHistSplinePdf)

RooHistSplinePdf::RooHistSplinePdf(const char *name, const char *title, const RooArgSet& vars,
				   const RooDataHist& dhist, Int_t intOrder, const RooArgList &coefList)
: RooHistPdf(name, title, vars, dhist, intOrder),
  _coefList("coefList", "List of coefficients", this) {

  if(_histObsList.size()!=1 || _pdfObsList.size()!=1) {
    coutE(InputArguments) << "RooHistSplinePdf::ctor(" << GetName()
           << ") Can only run with 1D histogram for now." << std::endl ;
    assert(0) ;
  }

  _coefList.add(coefList);
}

TSpline3 RooHistSplinePdf::getSpline(void) const
{
  // get the position to evaluate at
  RooRealVar *param=dynamic_cast<RooRealVar*>(_histObsList[0]);
  double min=param->getMin();
  double max=param->getMax();

  // get the number of coefficients and create the values
  int n= _coefList.size();
  Double_t *x=new Double_t[n+2];
  Double_t *y=new Double_t[n+2];

  // create the spline points
  y[0]=y[n+1]=0.0;
  x[0]=min;
  x[n+1]=max;
  for(int i=1; i<=n; i++) {
    x[i]=i*(max-min)/(n+1)+min;
    y[i]=static_cast<RooAbsReal &>(_coefList[i-1]).getVal();
  }

  // create the spline, evaluate it, and multiply
  TSpline3 spline("spline",x,y,n+2);

  delete x;
  delete y;
  
  return spline;
}

double RooHistSplinePdf::evaluate() const
{
  // evaluate the histogram first
  double histeval=RooHistPdf::evaluate();

  // get the position to evaluate at
  RooRealVar *param=dynamic_cast<RooRealVar*>(_histObsList[0]);
  double val=param->getVal();

  // create the spline, evaluate it, and multiply
  double scale=getSpline().Eval(val)+1.0;
  if(scale<0.0) scale=0.0;
  
  return scale*histeval;
}
