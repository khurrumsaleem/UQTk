/* =====================================================================================

                      The UQ Toolkit (UQTk) version 3.1.5
                          Copyright (2024) NTESS
                        https://www.sandia.gov/UQToolkit/
                        https://github.com/sandialabs/UQTk

     Copyright 2024 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
     Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government
     retains certain rights in this software.

     This file is part of The UQ Toolkit (UQTk)

     UQTk is open source software: you can redistribute it and/or modify
     it under the terms of BSD 3-Clause License

     UQTk is distributed in the hope that it will be useful,
     but WITHOUT ANY WARRANTY; without even the implied warranty of
     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
     BSD 3 Clause License for more details.

     You should have received a copy of the BSD 3 Clause License
     along with UQTk. If not, see https://choosealicense.com/licenses/bsd-3-clause/.

     Questions? Contact the UQTk Developers at https://github.com/sandialabs/UQTk/discussions
     Sandia National Laboratories, Livermore, CA, USA
===================================================================================== */

#include <math.h>
#include "XMLUtils.h"
#include "uqtktools.h"
#include "uqtkmcmc.h"

#include "model.h"
#include "posterior.h"
#include "XMLreader.h"

using namespace std;

/// \brief Example that infers parameters, given data on species concentrations, 
/// in a 3-equation model for heterogeneous surface
/// reaction involving a monomer, dimer, and inert species adsorbing
/// onto a surface out of gas phase. This model mimics some aspects
/// of CO oxidation.
///
/// For more details on the reaction model, see
/// [1] R. Vigil and F. Willmore, “Oscillatory dynamics in a heterogeneous surface
///     reaction: Breakdown of the mean-field approximation.,” Phys Rev E,
///     vol. 54, no. 2, pp. 1225–1231, Aug. 1996.
/// [2] A. G. Makeev, D. Maroudas, and I. G. Kevrekidis, “‘Coarse’ stability and
///     bifurcation analysis using stochastic simulators: Kinetic Monte Carlo examples,”
///     J. Chem. Phys., vol. 116, no. 23, p. 10083, 2002.
/// The equations solved are:
///     du/dt = az - cu - 4duv (coverage fraction of monomer)
///     dv/dt = 2bz^2 - 4duv   (coverage fraction of dimer)
///     dw/dt = ez - fw        (coverage fraction of inert species)
///       z   = 1 - u - v - w  (vacant fraction)


/// Main program: MCMC inference of the ODE model parameters given data
int main(int argc, char *argv[])
{
  // Pointer to posterior information
  postAux* pinfo=new postAux;
  // Read the xml tree
  RefPtr<XMLElement> xmlTree=readXMLTree("surf_rxn.in.xml");
  // Read the model specification and send them to the posterior information structure
  readXMLModelInput(xmlTree,pinfo->modelparams, pinfo->modelparamnames, pinfo->modelauxparams);
  // Read specific information needed by inference, e.g. data and the parameters to be inferred
  readXMLDataInput(xmlTree,pinfo->data, pinfo->postparams,&(pinfo->noisetype));


  // Number of MCMC steps
  int nsteps;
  // Array to hold the starting values of the chain
  Array1D<double> chstart;
  // Define the MCMC object
  MCMC mchain(LogPosterior,(void*) pinfo);
  // Read the xml file for MCMC-specific information
  readXMLChainInput(xmlTree,&mchain, chstart, &nsteps,pinfo->chainParamInd,pinfo->priortype,pinfo->priorparam1,pinfo->priorparam2);

  // Prepend the parameter names to the output file
  FILE* f_out;  
  string filename=mchain.getFilename();
  int chdim=chstart.XSize();
  
  f_out = fopen(filename.c_str(),"w"); 

  fprintf(f_out, "%s ","Step");
  for(int i=0;i<chdim;i++)
    fprintf(f_out, "%21s ",pinfo->modelparamnames(pinfo->chainParamInd(i)).c_str());
  fprintf(f_out, "%24s %24s \n","Accept_prob","Log_posterior");
  fclose(f_out);

  // Set the flag
  mchain.namesPrepended();
  // Run the chain
  mchain.runChain(nsteps, chstart);
   
  return 0;
}


