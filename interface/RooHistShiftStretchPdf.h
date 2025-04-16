//---------------------------------------------------------------------------
#ifndef HiggsAnalysis_CombinedLimit_RooHistShiftStretchPdf_h
#define HiggsAnalysis_CombinedLimit_RooHistShiftStretchPdf_h
//---------------------------------------------------------------------------

#include "RooHistPdf.h"
#include "RooRealProxy.h"
#include "TSpline.h"

//---------------------------------------------------------------------------
class RooAbsReal;

//---------------------------------------------------------------------------

class RooHistShiftStretchPdf : public RooHistPdf
{
public:
  RooHistShiftStretchPdf() { _spline=nullptr; }
  RooHistShiftStretchPdf(const char *name, const char *title, const RooArgSet& vars,
			 const RooDataHist& dhist, Int_t intOrder, RooAbsReal& shift, RooAbsReal& stretch, RooAbsReal& fixedPoint);
  RooHistShiftStretchPdf(const RooHistShiftStretchPdf& other, const char* name= nullptr) :
  RooHistPdf(other, name),
  _shift("shift", this, other._shift),
  _stretch("stretch", this, other._stretch),
  _fixedPoint("fixedPoint", this, other._fixedPoint),
  _spline(nullptr)
    {
    }

  virtual TObject* clone(const char* newname) const override { return new RooHistShiftStretchPdf(*this,newname); }
    
  inline virtual ~RooHistShiftStretchPdf() { if(_spline) delete _spline; }

  // compute the integral analytically
  Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const override;

  //  Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const override;
  
protected:
  RooRealProxy _shift;      // parameter that controls shifting
  RooRealProxy _stretch;    // parameter that controls stretching
  RooRealProxy _fixedPoint; // parameter that controls the point about which to do the shifting and stretching

  virtual double evaluate() const override;

 private:
  // get/create the spline
  const TSpline5* getSpline(void) const;
  mutable TSpline5* _spline;
  
  ClassDefOverride(RooHistShiftStretchPdf,1) // Declare this for CINT
};


//---------------------------------------------------------------------------
#endif
