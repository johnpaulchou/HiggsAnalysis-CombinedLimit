//---------------------------------------------------------------------------
#include "RooFit.h"

#include "Riostream.h"
#include <TMath.h>
#include <cassert>
#include <cmath>
#include <math.h>

#include "RooRealVar.h"
#include "RooConstVar.h"
#include "Math/Functor.h"
#include "Math/WrappedFunction.h"
#include "Math/IFunction.h"
#include "Math/Integrator.h"
#include "Math/GSLIntegrator.h"

#include "../interface/RooDijetPdf.h"

using namespace std;
using namespace RooFit;

ClassImp(RooDijetAbsPdf)
ClassImp(RooDijet1Pdf)
ClassImp(RooDijet2Pdf)
ClassImp(RooDijet3Pdf)

//---------------------------------------------------------------------------
Double_t RooDijet1Pdf::evaluate() const
{
  using namespace std;
  Double_t x=_x/_sqrts;
    return pow(x,_p1+_p2*log(x));
}

Double_t RooDijet2Pdf::evaluate() const
{
  using namespace std;
  Double_t x=_x/_sqrts;
  return exp(_p1*x)*pow(x,_p2);
}

Double_t RooDijet3Pdf::evaluate() const
{
  using namespace std;
  Double_t x=_x/_sqrts;
  return pow(1.0+x*_p1,_p2);
}


// //---------------------------------------------------------------------------

