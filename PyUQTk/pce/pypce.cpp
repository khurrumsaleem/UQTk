#include <pybind11/pybind11.h>

#include "PCBasis.h"
#include "PCSet.h"

namespace py = pybind11;

PYBIND11_MODULE(_pce, m) {
    py::class_<PCBasis>(m,"PCBasis")
      .def(py::init<const string, const double, const double, const int>())
      .def("Init1dQuadPoints",&PCBasis::Init1dQuadPoints)
      .def("Eval1dBasisAtQuadPoints",&PCBasis::Eval1dBasisAtQuadPoints)
      .def("Eval1dBasisAtCustPoints",&PCBasis::Eval1dBasisAtCustPoints)
      .def("EvalBasis",static_cast<double (PCBasis::*)(const double &, Array1D<double> &) const>(&PCBasis::EvalBasis))
      .def("EvalBasis",static_cast<double (PCBasis::*)(const double &, const int, double *) const>(&PCBasis::EvalBasis))
      .def("Eval1dNormSq_Exact",&PCBasis::Eval1dNormSq_Exact)
      .def("EvalDerivBasis",&PCBasis::EvalDerivBasis)
      .def("Eval1dDerivBasisAtCustPoints",&PCBasis::Eval1dDerivBasisAtCustPoints)
      .def("Eval2ndDerivBasis",&PCBasis::Eval2ndDerivBasis)
      .def("Eval2ndDerivCustPoints",&PCBasis::Eval2ndDerivCustPoints)
      .def("Get1dNormsSq",&PCBasis::Get1dNormsSq)
      .def("Get1dNormsSqExact",&PCBasis::Get1dNormsSqExact)
      .def("GetRandSample",static_cast<void (PCBasis::*)(Array1D<double>&)>(&PCBasis::GetRandSample))
      .def("GetRandSample",static_cast<void (PCBasis::*)(double*, const int&)>(&PCBasis::GetRandSample))
      .def("GetSeed",&PCBasis::GetSeed)
      .def("SeedRandNumGen",&PCBasis::SeedRandNumGen)
      .def("GetQuadRule",&PCBasis::GetQuadRule)
      .def("GetQuadPoints",&PCBasis::GetQuadPoints)
      .def("GetQuadWeights",&PCBasis::GetQuadWeights)
      .def("GetQuadIndices",&PCBasis::GetQuadIndices)
      .def("GetBasisAtQuadPoints",&PCBasis::GetBasisAtQuadPoints)
      .def("GetPCType",&PCBasis::GetPCType)
      .def("GetAlpha",&PCBasis::GetAlpha)
      .def("GetBeta",&PCBasis::GetBeta)
      ;

      py::class_<PCSet>(m,"PCSet")
        .def(py::init<const string, const int, const int, const string, const double, const double>())
        .def(py::init<const string, const int, const int, const string, const string, const double, const double>())
        .def(py::init<const string, const Array1D<int>&, const int, const string, const double, const double>())
        .def(py::init<const string, const Array2D<int>&, const string, const double, const double>())
        .def("dPhi_alpha",&PCSet::dPhi_alpha)
        .def("dPhi",static_cast<void (PCSet::*)(Array1D<double>&, Array2D<int>&, Array1D<double>&, Array1D<double>&)>(&PCSet::dPhi))
        .def("dPhi",static_cast<void (PCSet::*)(Array2D<double>&, Array2D<int>&, Array2D<double>&, Array1D<double>&)>(&PCSet::dPhi))
        .def("ddPhi_alpha",&PCSet::ddPhi_alpha)
        .def("ddPhi",&PCSet::ddPhi)
        .def("SetQd1d",&PCSet::SetQd1d)
        .def("SetQuadRule",static_cast<void (PCSet::*)(const string,const string,int)>(&PCSet::SetQuadRule))
        .def("SetQuadRule",static_cast<void (PCSet::*)(Quad&)>(&PCSet::SetQuadRule))
        .def("PrintMultiIndex",&PCSet::PrintMultiIndex)
        .def("PrintMultiIndexNormSquared",&PCSet::PrintMultiIndexNormSquared)
        .def("GetPCType",&PCSet::GetPCType)
        .def("GetAlpha",&PCSet::GetAlpha)
        .def("GetBeta",&PCSet::GetBeta)
        .def("GetMultiIndex",static_cast<void (PCSet::*)(Array2D<int> &) const>(&PCSet::GetMultiIndex))
        .def("GetMultiIndex",static_cast<void (PCSet::*)(int *) const>(&PCSet::GetMultiIndex))
        .def("GetNormSq",&PCSet::GetNormSq)
        .def("GetNumberPCTerms",&PCSet::GetNumberPCTerms)
        .def("GetNDim",&PCSet::GetNDim)
        .def("GetOrder",&PCSet::GetOrder)
        .def("GetNQuadPoints",&PCSet::GetNQuadPoints)
        .def("GetQuadPoints",static_cast<void (PCSet::*)(Array2D<double>&) const>(&PCSet::GetQuadPoints))
        .def("GetQuadPoints",static_cast<void (PCSet::*)(double *) const>(&PCSet::GetQuadPoints))
        .def("GetQuadPointsWeights",&PCSet::GetQuadPointsWeights)
        .def("GetQuadWeights",static_cast<void (PCSet::*)(Array1D<double>&) const>(&PCSet::GetQuadWeights))
        .def("GetQuadWeights",static_cast<void (PCSet::*)(double *) const>(&PCSet::GetQuadWeights))
        .def("GetPsi",static_cast<void (PCSet::*)(Array2D<double>&) const>(&PCSet::GetPsi))
        .def("GetPsi",static_cast<void (PCSet::*)(double *) const>(&PCSet::GetPsi))
        .def("GetPsiSq",static_cast<void (PCSet::*)(Array1D<double>&) const>(&PCSet::GetPsiSq))
        .def("GetPsiSq",static_cast<void (PCSet::*)(double *) const>(&PCSet::GetPsiSq))
        .def("GetTaylorTolerance",&PCSet::GetTaylorTolerance)
        .def("SetTaylorTolerance",&PCSet::SetTaylorTolerance)
        .def("GetTaylorTermsMax",&PCSet::GetTaylorTermsMax)
        .def("SetTaylorTermsMax",&PCSet::SetTaylorTermsMax)
        .def("SetLogCompMethod",&PCSet::SetLogCompMethod)
        .def("GetGMRESDivTolerance",&PCSet::GetGMRESDivTolerance)
        .def("SetGMRESDivTolerance",&PCSet::SetGMRESDivTolerance)
        .def("InitMeanStDv",static_cast<void (PCSet::*)(const double&, const double&, double*) const>(&PCSet::InitMeanStDv))
        .def("InitMeanStDv",static_cast<void (PCSet::*)(const double&, const double&, Array1D<double>&) const>(&PCSet::InitMeanStDv))
        .def("Copy",static_cast<void (PCSet::*)(double*, const double*) const>(&PCSet::Copy))
        .def("Copy",static_cast<void (PCSet::*)(Array1D<double>&, const Array1D<double>&) const>(&PCSet::Copy))
        .def("Add",static_cast<void (PCSet::*)(const double*, const double*, double*) const>(&PCSet::Add))
        .def("Add",static_cast<void (PCSet::*)(const Array1D<double>&, const Array1D<double>&, Array1D<double>&) const>(&PCSet::Add))
        .def("AddInPlace",static_cast<void (PCSet::*)(double*, const double*) const>(&PCSet::AddInPlace))
        .def("AddInPlace",static_cast<void (PCSet::*)(Array1D<double>&, const Array1D<double>&) const>(&PCSet::AddInPlace))
        .def("Multiply",static_cast<void (PCSet::*)(const double*, const double&, double*) const>(&PCSet::Multiply))
        .def("Multiply",static_cast<void (PCSet::*)(const Array1D<double>&, const double&, Array1D<double>&) const>(&PCSet::Multiply))
        .def("MultiplyInPlace",static_cast<void (PCSet::*)(double*, const double&) const>(&PCSet::MultiplyInPlace))
        .def("MultiplyInPlace",static_cast<void (PCSet::*)(Array1D<double>&, const double&) const>(&PCSet::MultiplyInPlace))
        .def("Subtract",static_cast<void (PCSet::*)(const double*, const double*, double*) const>(&PCSet::Subtract))
        .def("Subtract",static_cast<void (PCSet::*)(const Array1D<double>&, const Array1D<double>&, Array1D<double>&) const>(&PCSet::Subtract))
        .def("SubtractInPlace",static_cast<void (PCSet::*)(double*, const double*) const>(&PCSet::SubtractInPlace))
        .def("SubtractInPlace",static_cast<void (PCSet::*)(Array1D<double>&, const Array1D<double>&) const>(&PCSet::SubtractInPlace))
        .def("Prod",static_cast<void (PCSet::*)(const double*, const double*, double*) const>(&PCSet::Prod))
        .def("Prod",static_cast<void (PCSet::*)(const Array1D<double>&, const Array1D<double>&, Array1D<double>&) const>(&PCSet::Prod))
        .def("Prod3",static_cast<void (PCSet::*)(const double*, const double*, const double *, double*) const>(&PCSet::Prod3))
        .def("Prod3",static_cast<void (PCSet::*)(const Array1D<double>&, const Array1D<double>&, const Array1D<double>&, Array1D<double>&) const>(&PCSet::Prod3))
        .def("Polyn",static_cast<void (PCSet::*)(const double*, int, const double*, double*) const>(&PCSet::Polyn))
        .def("Polyn",static_cast<void (PCSet::*)(const Array1D<double>&, const Array1D<double>&, Array1D<double>&) const>(&PCSet::Polyn))
        .def("PolynMulti",&PCSet::PolynMulti)
        .def("Exp",static_cast<void (PCSet::*)(const double*, double*) const>(&PCSet::Exp))
        .def("Exp",static_cast<void (PCSet::*)(const Array1D<double>&, Array1D<double>&) const>(&PCSet::Exp))
        .def("Log",static_cast<void (PCSet::*)(const double*, double*) const>(&PCSet::Log))
        .def("Log",static_cast<void (PCSet::*)(const Array1D<double>&, Array1D<double>&) const>(&PCSet::Log))
        .def("Log10",static_cast<void (PCSet::*)(const double*, double*) const>(&PCSet::Log10))
        .def("Log10",static_cast<void (PCSet::*)(const Array1D<double>&, Array1D<double>&) const>(&PCSet::Log10))
        .def("IPow",static_cast<void (PCSet::*)(const double*, double*, const int&) const>(&PCSet::IPow))
        .def("IPow",static_cast<void (PCSet::*)(const Array1D<double>&, Array1D<double>&, const int&) const>(&PCSet::IPow))
        .def("Inv",static_cast<void (PCSet::*)(const double *,double *) const>(&PCSet::Inv))
        .def("Inv",static_cast<void (PCSet::*)(const Array1D<double>&,Array1D<double>&) const>(&PCSet::Inv))
        .def("Div",static_cast<void (PCSet::*)(const double*, const double*, double*) const>(&PCSet::Div))
        .def("Div",static_cast<void (PCSet::*)(const Array1D<double>&, const Array1D<double>&, Array1D<double>&) const>(&PCSet::Div))
        .def("StDv",static_cast<double (PCSet::*)(const double*) const>(&PCSet::StDv))
        .def("StDv",static_cast<double (PCSet::*)(const Array1D<double>&) const>(&PCSet::StDv))
        .def("GetModesRMS",static_cast<double (PCSet::*)(const double*) const>(&PCSet::GetModesRMS))
        .def("GetModesRMS",static_cast<double (PCSet::*)(const Array1D<double>&) const>(&PCSet::GetModesRMS))
        .def("Derivative",static_cast<void (PCSet::*)(const double*, double*) const>(&PCSet::Derivative))
        .def("Derivative",static_cast<void (PCSet::*)(const Array1D<double>&, Array1D<double>&) const>(&PCSet::Derivative))
        .def("GetNumTripleProd",&PCSet::GetNumTripleProd)
        .def("GetTripleProd",static_cast<void (PCSet::*)(int *, int *, int *, double *) const>(&PCSet::GetTripleProd))
        .def("GetTripleProd",static_cast<void (PCSet::*)(Array1D<int>&, Array1D<int>&, Array1D<int>&, Array1D<double>&) const>(&PCSet::GetTripleProd))
        .def("GetNumQuadProd",&PCSet::GetNumQuadProd)
        .def("GetQuadProd",static_cast<void (PCSet::*)(int *, int *, int *, int *, double *) const>(&PCSet::GetQuadProd))
        .def("GetQuadProd",static_cast<void (PCSet::*)(Array1D<int> &, Array1D<int> &, Array1D<int> &, Array1D<int> &,Array1D<double> &) const>(&PCSet::GetQuadProd))
        .def("SeedBasisRandNumGen",&PCSet::SeedBasisRandNumGen)
        .def("DrawSampleSet",static_cast<void (PCSet::*)(const Array1D<double>&, Array1D<double>&)>(&PCSet::DrawSampleSet))
        .def("DrawSampleSet",static_cast<void (PCSet::*)(const double*, double*, const int&)>(&PCSet::DrawSampleSet))
        .def("DrawSampleVar",static_cast<void (PCSet::*)(Array2D<double>&) const>(&PCSet::DrawSampleVar))
        .def("DrawSampleVar",static_cast<void (PCSet::*)(double *, const int &, const int &) const>(&PCSet::DrawSampleVar))
        .def("EvalPC",static_cast<double (PCSet::*)(const Array1D<double>&, Array1D<double>&)>(&PCSet::EvalPC))
        .def("EvalPC",static_cast<double (PCSet::*)(const double*, const double*)>(&PCSet::EvalPC))
        .def("EvalPCAtCustPoints",&PCSet::EvalPCAtCustPoints)
        .def("EvalBasisAtCustPts",static_cast<void (PCSet::*)(const Array2D<double>&,Array2D<double>&)>(&PCSet::EvalBasisAtCustPts))
        .def("EvalBasisAtCustPts",static_cast<void (PCSet::*)(const double*, const int, double*)>(&PCSet::EvalBasisAtCustPts))
        .def("GalerkProjection",&PCSet::GalerkProjection)
        .def("GalerkProjection",&PCSet::GalerkProjectionMC)
        .def("ComputeOrders",&PCSet::ComputeOrders)
        .def("ComputeEffDims",static_cast<int (PCSet::*)(int *)>(&PCSet::ComputeEffDims))
        .def("ComputeEffDims",static_cast<int (PCSet::*)(Array1D<int> &)>(&PCSet::ComputeEffDims))
        .def("EncodeMindex",&PCSet::EncodeMindex)
        .def("ComputeMean",static_cast<double (PCSet::*)(const double *)>(&PCSet::ComputeMean))
        .def("ComputeMean",static_cast<double (PCSet::*)(Array1D<double> &)>(&PCSet::ComputeMean))
        .def("ComputeVarFrac",static_cast<double (PCSet::*)(const double *, double *)>(&PCSet::ComputeVarFrac))
        .def("ComputeVarFrac",static_cast<double (PCSet::*)(Array1D<double>&, Array1D<double>&)>(&PCSet::ComputeVarFrac))
        .def("ComputeMainSens",&PCSet::ComputeMainSens)
        .def("ComputeTotSens",&PCSet::ComputeTotSens)
        .def("ComputeJointSens",&PCSet::ComputeJointSens)
        .def("SetVerbosity",&PCSet::SetVerbosity)
        .def("EvalNormSq",static_cast<void (PCSet::*)(Array1D<double>&)>(&PCSet::EvalNormSq))
        .def("EvalNormSq",static_cast<void (PCSet::*)(double*, const int)>(&PCSet::EvalNormSq))
        .def("EvalNormSqExact",&PCSet::EvalNormSqExact)
        .def("IsInDomain",&PCSet::IsInDomain)
        ;

        py::enum_<LogCompMethod>(m, "LogCompMethod")
        .value("TaylorSeries", TaylorSeries)
        .value("Integration", Integration)
        .export_values();

}
