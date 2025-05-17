//---------------------------------------------------------------------------
#ifndef HiggsAnalysis_CombinedLimit_RooHistSplinePdf_h
#define HiggsAnalysis_CombinedLimit_RooHistSplinePdf_h
//---------------------------------------------------------------------------

#include "RooHistPdf.h"
#include "TSpline.h"

//---------------------------------------------------------------------------
class RooHistSplinePdf : public RooHistPdf
{
public:
  RooHistSplinePdf() {}
  RooHistSplinePdf(const char *name, const char *title, const RooArgSet& vars,
		   const RooDataHist& dhist, Int_t intOrder, const RooArgList &coefList, bool fixEndpoints=true);

  RooHistSplinePdf(const RooHistSplinePdf &other, const char *name = nullptr) :
    RooHistPdf(other, name),
    _coefList("coefList", this, other._coefList),
    _fixEndpoints(other._fixEndpoints)
  {
  }

  TObject *clone(const char *newname) const override { return new RooHistSplinePdf(*this, newname); }

  // all integrals need to be calculated numerically
  Int_t getAnalyticalIntegral(RooArgSet &allVars, RooArgSet &analVars, const char *rangeName = nullptr) const override { return 0; }
 
  RooArgList const &coefList() const { return _coefList; }

  TSpline3 getSpline(void) const;
  
protected:
 
  RooListProxy _coefList;
  bool _fixEndpoints;
  
  virtual double evaluate() const override;
  
  ClassDefOverride(RooHistSplinePdf, 1) // Histogram*spline PDF
};


//---------------------------------------------------------------------------
class RooHistBBPdf : public RooHistPdf
{
public:
  RooHistBBPdf() {}
  RooHistBBPdf(const char *name, const char *title, const RooArgSet& vars,
		   const RooDataHist& dhist, Int_t intOrder, const RooArgList &coefList);

  RooHistBBPdf(const RooHistBBPdf &other, const char *name = nullptr) :
    RooHistPdf(other, name),
    _coefList("coefList", this, other._coefList)
  {
  }

  TObject *clone(const char *newname) const override { return new RooHistBBPdf(*this, newname); }

  // all integrals need to be calculated numerically
  Int_t getAnalyticalIntegral(RooArgSet &allVars, RooArgSet &analVars, const char *rangeName = nullptr) const override { return 0; }
 
  RooArgList const &coefList() const { return _coefList; }

protected:
 
  RooListProxy _coefList;
  
  virtual double evaluate() const override;
  
  ClassDefOverride(RooHistBBPdf, 1) // Histogram with Barlow-Beeston PDF
};



//---------------------------------------------------------------------------
#endif
