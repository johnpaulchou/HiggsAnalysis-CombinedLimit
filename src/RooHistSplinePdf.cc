//---------------------------------------------------------------------------
#include "RooFit.h"

#include "Riostream.h"

#include "../interface/RooHistSplinePdf.h"

using namespace std;
using namespace RooFit;

ClassImp(RooHistSplinePdf)

RooHistSplinePdf::RooHistSplinePdf(const char *name, const char *title, const RooArgSet& vars,
				   const RooDataHist& dhist, Int_t intOrder, const RooArgList &coefList)
: RooHistPdf(name, title, vars, dhist, intOrder),
  _coefList("coefficients", "List of coefficients", this) {

  if(_histObsList.size()!=1 || _pdfObsList.size()!=1) {
    coutE(InputArguments) << "RooHistSplinePdf::ctor(" << GetName()
           << ") Can only run with 1D histogram for now." << std::endl ;
    assert(0) ;
  }
}


double RooHistSplinePdf::evaluate() const
{
  double eval=RooHistPdf::evaluate();
  return eval;
}
