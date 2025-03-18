//---------------------------------------------------------------------------
#ifndef HiggsAnalysis_CombinedLimit_RooHistSplinePdf_h
#define HiggsAnalysis_CombinedLimit_RooHistSplinePdf_h
//---------------------------------------------------------------------------

#include "RooHistPdf.h"

//---------------------------------------------------------------------------
class RooHistSplinePdf : public RooHistPdf
{
public:
  RooHistSplinePdf(const char *name, const char *title, const RooArgSet& vars,
		   const RooDataHist& dhist, Int_t intOrder, const RooArgList &coefList);

  RooHistSplinePdf(const RooHistSplinePdf &other, const char *name = nullptr) :
    RooHistPdf(other, name),
    _coefList("coefList", this, other._coefList)
  {
  }

  TObject *clone(const char *newname) const override { return new RooHistSplinePdf(*this, newname); }

  // all integrals need to be calculated numerically
  Int_t getAnalyticalIntegral(RooArgSet &allVars, RooArgSet &analVars, const char *rangeName = nullptr) const override { return 0; }
 
  RooArgList const &coefList() const { return _coefList; }

  
protected:
 
  RooListProxy _coefList;
  
  virtual double evaluate() const override;
  
  ClassDefOverride(RooHistSplinePdf, 1) // Histogram*spline PDF
};


//---------------------------------------------------------------------------
#endif
