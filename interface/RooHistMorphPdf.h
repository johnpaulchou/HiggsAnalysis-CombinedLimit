//---------------------------------------------------------------------------
#ifndef HiggsAnalysis_CombinedLimit_RooHistMorphPdf_h
#define HiggsAnalysis_CombinedLimit_RooHistMorphPdf_h
//---------------------------------------------------------------------------
#include "RooAbsPdf.h"
#include "RooRealProxy.h"
//---------------------------------------------------------------------------
class RooAbsReal;

#include <TH2.h>

//---------------------------------------------------------------------------
class RooHistMorphPdf : public RooAbsPdf
{
public:
  RooHistMorphPdf() { _hist=nullptr; }
  RooHistMorphPdf(const char *name, const char *title, RooAbsReal& x, RooAbsReal& p, TH2* hist);
  RooHistMorphPdf(const RooHistMorphPdf& other, const char* name=0);
  inline virtual ~RooHistMorphPdf() { if(_hist) delete _hist; }

  // all integrals need to be calculated numerically
  Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const override { return 0; }
   virtual TObject* clone(const char* newname) const override { return new RooHistMorphPdf(*this,newname); }
  TH2* getHist(void) { return _hist; }

protected:
  RooRealProxy _x;   // dependent variable
  RooRealProxy _p;   // parameter that controls morphing
  TH2* _hist;        // hist owned by this object

  virtual double evaluate() const override;
  ClassDefOverride(RooHistMorphPdf,1) // Declare this for CINT
};


//---------------------------------------------------------------------------
#endif
