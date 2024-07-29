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
class RooDijetAbsPdf : public RooAbsPdf
{
public:
   RooDijetAbsPdf() {}

  RooDijetAbsPdf(const char *name, const char *title,
	       RooAbsReal& x, RooAbsReal& p1, RooAbsReal& p2, RooAbsReal& sqrts) :
     RooAbsPdf(name, title), _x("x", "Dependent variable", this, x),
       _p1("p1", "p1", this, p1), _p2("p2", "p2", this, p2), _sqrts("sqrts","sqrts",this,sqrts) {}

  RooDijetAbsPdf(const RooDijetAbsPdf& other, const char* name=0) :
     RooAbsPdf(other, name), _x("x", this, other._x), _p1("p1", this, other._p1), _p2("p2", this, other._p2), _sqrts("sqrts", this, other._sqrts) {}

   inline virtual ~RooDijetAbsPdf() { }

  // all integrals need to be calculated numerically
  Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const { return 0; }
  //   Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;

protected:   
  
  RooRealProxy _x;        // dependent variable
  RooRealProxy _p1;       // p1
  RooRealProxy _p2;       // p2
  RooRealProxy _sqrts;    // sqrts
  
  virtual Double_t evaluate() const=0;
  ClassDef(RooDijetAbsPdf,1) // Declare this for CINT
  
private:
};

class RooDijet1Pdf : public RooDijetAbsPdf
{
 public:
  using RooDijetAbsPdf::RooDijetAbsPdf;

   virtual TObject* clone(const char* newname) const { return new RooDijet1Pdf(*this,newname); }
 protected:
  Double_t evaluate() const;
  ClassDef(RooDijet1Pdf,1) // Declare this for CINT
};

class RooDijet2Pdf : public RooDijetAbsPdf
{
 public:
  using RooDijetAbsPdf::RooDijetAbsPdf;

   virtual TObject* clone(const char* newname) const { return new RooDijet2Pdf(*this,newname); }
 protected:
  Double_t evaluate() const;
  ClassDef(RooDijet2Pdf,1) // Declare this for CINT
};

class RooDijet3Pdf : public RooDijetAbsPdf
{
 public:
  using RooDijetAbsPdf::RooDijetAbsPdf;

   virtual TObject* clone(const char* newname) const { return new RooDijet3Pdf(*this,newname); }
 protected:
  Double_t evaluate() const;
  ClassDef(RooDijet3Pdf,1) // Declare this for CINT
};


//---------------------------------------------------------------------------
#endif
