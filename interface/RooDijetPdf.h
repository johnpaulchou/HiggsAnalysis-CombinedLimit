//---------------------------------------------------------------------------
#ifndef HiggsAnalysis_CombinedLimit_RooDijet3ParamBinPdf_h
#define HiggsAnalysis_CombinedLimit_RooDijet3ParamBinPdf_h
//---------------------------------------------------------------------------
#include "RooAbsPdf.h"
#include "RooConstVar.h"
#include "RooRealProxy.h"
//---------------------------------------------------------------------------
class RooRealVar;
class RooAbsReal;

#include "Riostream.h"
#include "TMath.h"
#include <TH1.h>
#include "Math/SpecFuncMathCore.h"
#include "Math/SpecFuncMathMore.h"
#include "Math/Functor.h"
#include "Math/WrappedFunction.h"
#include "Math/IFunction.h"
#include "Math/Integrator.h"

#include "Math/IFunction.h"
#include "Math/IParamFunction.h"

//---------------------------------------------------------------------------
class RooDijetPdf : public RooAbsPdf
{
public:
   RooDijetPdf() {} ;

  RooDijetPdf(const char *name, const char *title,
	       RooAbsReal& x, RooAbsReal& p1, RooAbsReal& p2, Double_t sqrts, Int_t funcid) :
     RooAbsPdf(name, title), _x("x", "Dependent variable", this, x),
     _p1("p1", "p1", this, p1), _p2("p2", "p2", this, p2), _sqrts(sqrts), _funcid(funcid) {}

  RooDijetPdf(const RooDijetPdf& other, const char* name=0) :
    RooAbsPdf(other, name), _x("x", this, other._x), _p1("p1", this, other._p1), _p2("p2", this, other._p2), _sqrts(other._sqrts), _funcid(other._funcid) {}

   virtual TObject* clone(const char* newname) const { return new RooDijetPdf(*this,newname); }
   inline virtual ~RooDijetPdf() { }

  // all integrals need to be calculated numerically
  Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const { return 0; }
  //   Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;

protected:   
  
  RooRealProxy _x;        // dependent variable
  RooRealProxy _p1;       // p1
  RooRealProxy _p2;        // p2
  Double_t _sqrts;        // sqrts
  Int_t _funcid;          // which function we want to evaluate
  
  Double_t evaluate() const;
  
private:
   ClassDef(RooDijetPdf,1) // Declare this for CINT
};


//---------------------------------------------------------------------------
#endif
