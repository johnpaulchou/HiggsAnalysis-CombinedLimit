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

ClassImp(RooDijetPdf)

//---------------------------------------------------------------------------
Double_t RooDijetPdf::evaluate() const
{
  using namespace std;
  Double_t x=_x/_sqrts;
  if(_funcid==0)
    return pow(x,_p1+_p2*log(x));
  if(_funcid==1)
    return exp(_p1*x)*pow(x,_p2);
  if(_funcid==2)
    return pow(1.0+x*_p1,_p2);
  return 0.0;
}


// //---------------------------------------------------------------------------

