/*****************************************************************************
 * Project: RooFit                                                           *
 *                                                                           *
  * This code was autogenerated by RooClassFactory                            * 
 *****************************************************************************/

#ifndef HZZ4L_ROOSPINZEROPDF
#define HZZ4L_ROOSPINZEROPDF

#include "RooAbsPdf.h"
#include "RooRealProxy.h"
#include "RooRealVar.h"
#include "RooCategoryProxy.h"
#include "RooAbsReal.h"
#include "RooAbsCategory.h"
#include "TH3F.h"
#include "TH1.h"
#include "RooDataHist.h"
#include "RooHistFunc.h"
#include "RooListProxy.h"
using namespace RooFit;
class HZZ4L_RooSpinZeroPdf : public RooAbsPdf {
protected:

  RooRealProxy kd ;
  RooRealProxy kdint ;
  RooRealProxy ksmd ;
  RooRealProxy fai ;
  RooListProxy _coefList ;  //  List of funcficients
//  TIterator* _coefIter ;    //! Iterator over funcficient lis
  Double_t evaluate() const override ;
public:
  HZZ4L_RooSpinZeroPdf() {} ; 
  HZZ4L_RooSpinZeroPdf(const char *name, const char *title,
		       RooAbsReal& _kd,
		       RooAbsReal& _kdint,
					 RooAbsReal& _ksmd,
		       RooAbsReal& _fai,
			const RooArgList& inCoefList);
		    
  HZZ4L_RooSpinZeroPdf(const HZZ4L_RooSpinZeroPdf& other, const char* name=0) ;
  TObject* clone(const char* newname) const override { return new HZZ4L_RooSpinZeroPdf(*this,newname); }
  inline ~HZZ4L_RooSpinZeroPdf() override {}
  
  Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const override ;
  Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const override ;
  const RooArgList& coefList() const { return _coefList ; }

  double Integral_T1;
  double Integral_T2;
  double Integral_T4;

private:

	ClassDefOverride(HZZ4L_RooSpinZeroPdf,1) // Your description goes here...

};
 
#endif
