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
/// \file pce_eval.cpp 
/// \author K. Sargsyan 2012 - 
/// \brief Command-line utility for PC-related evaluations

#include <unistd.h>

#include "PCSet.h"
#include "tools.h"
#include "arrayio.h"
#include "arraytools.h"

using namespace std;



/// default function type
#define FCNTYPE "PC"
/// default PC order
#define PCORD 1
/// default parameter file
#define PARAMFILE "pccf.dat"
/// default a parameter
#define AA 0.0 
/// default b parameter
#define BB 1.0 
/// default c parameter
#define CC 0.0 
/// default d parameter
#define DD 1.0 
/// default string parameter # 1
#define STR1 "HG" 
/// default string parameter # 2
#define STR2 "mindex.dat" 


/// \brief Evaluates a PC given dimensionality, order, and coefficients array
void fEval_PC(Array2D<double>& xdata, Array1D<double>& ydata, int pcdim, int pcord, Array1D<double>& c_k, char* pcType, double alpha, double beta);
/// \brief Evaluates the gradient of a PC given dimensionality, order, and coefficients array (only for LU PC)
void gEval_PC(Array2D<double>& xdata, Array2D<double>& gdata, int pcdim, int pcord, Array1D<double>& c_k, char* pcType, double alpha, double beta);
/// \brief Evaluates a PC given multiindex file and coefficients array
void fEval_PCmi(Array2D<double>& xdata, Array1D<double>& ydata, Array1D<double>& c_k, char* pcType, char* miFile, double alpha, double beta);
/// \brief Maps given points according to PC maps, i.e. if x=PC1(\xi) and y=PC2(\xi), this function is y=PC2( PC1^{-1} (x) )
void fEval_PCmap(Array2D<double>& xdata, Array1D<double>& ydata,  string pcIn, double a,double b, string pcOut, double c,double d);

/******************************************************************************/
/// \brief Displays information about this program
int usage(){
  printf("usage: pce_eval [-h] [-x<fcn_type>] [-o<pcord>] [-f<param_file>] [-a<a>] [-b<b>]  [-c<c>] [-d<d>]  [-s<str1>] [-r<str2>]\n");
  printf(" -h                : print out this help message \n");
  printf(" -x <fcn_type>     : define the type of fcn (default=%s) \n",FCNTYPE);
  printf(" -o <pcord>        : define the PC order(default=%d) \n",PCORD);
  printf(" -f <param_file>   : point to parameter file, if any  (default=%s) \n",PARAMFILE);
  printf(" -a <a>     : define the double parameter #1 (default=%lg) \n",AA);
  printf(" -b <b>     : define the double parameter #2 (default=%lg) \n",BB);
  printf(" -c <c>     : define the double parameter #3 (default=%lg) \n",CC);
  printf(" -d <d>     : define the double parameter #4 (default=%lg) \n",DD);
  printf(" -s <str1>  : define the string parameter #1  (default=%s) \n",STR1);
  printf(" -r <str2>  : define the string parameter #2  (default=%s) \n",STR2);
  
  printf("================================================================================\n");
  printf("Input  : xdata.dat \n");
  printf("Output : ydata.dat  -  function evaluations at xdata.dat \n");
  printf("Output : gdata.dat  -  gradient evaluations at xdata.dat for LU PC function type\n");
  printf("================================================================================\n");
  exit(0);
  return 0;
}

/// Main program: evaluates PC-related functions
/// \todo Make the input arguments more transparent, i.e. what do they mean in different scenarios? 
int main (int argc, char *argv[]) 
{
  /// Set the default values
  char* fcn_type = (char *)FCNTYPE ; 
  int pcord=PCORD;
  char* param_file  = (char *)PARAMFILE;
  double a=AA;
  double b=BB;
  double c=CC;
  double d=DD;
  char* str1=(char *)STR1;
  char* str2=(char *)STR2;

  bool oflag=false;
  bool fflag=false;
  bool aflag=false;
  bool bflag=false;
  bool cflag=false;	
  bool dflag=false;
  bool sflag=false;
  bool rflag=false;

  /// Read the user input
  int ch;

  while ((ch=getopt(argc,(char **)argv,"hx:o:f:a:b:c:d:s:r:"))!=-1){
    switch (ch) {
    case 'h':
      usage();
      break;
    case 'x':
      fcn_type = optarg;
      break;
    case 'o':
      oflag=true;
      pcord = strtol(optarg, (char **)NULL,0);	
      break;
    case 'f':
      fflag=true;
      param_file = optarg;
      break;
    case 'a':
      aflag=true;
      a = strtod(optarg, (char **)NULL);	
      break;
    case 'b':
      bflag=true;
      b = strtod(optarg, (char **)NULL);	
      break;
    case 'c':
      cflag=true;
      c = strtod(optarg, (char **)NULL);	
      break;
    case 'd':
      dflag=true;
      d = strtod(optarg, (char **)NULL);	
      break;
    case 's':
      sflag=true;
      str1 = optarg;
      break;
    case 'r':
      rflag=true;
      str2 = optarg;
      break;
    default :
      break;
    }
  }
  
  /// Print the input information on screen 
  fprintf(stdout,"fcn_type = %s \n",fcn_type);  
  if (oflag)
    fprintf(stdout,"pcord        = %d \n",pcord);
  if (fflag)
    fprintf(stdout,"param_file  = %s \n",param_file);  
  if (aflag)
    fprintf(stdout,"a     = %lg \n",a);
  if (bflag)
    fprintf(stdout,"b     = %lg \n",b);
  if (cflag)
    fprintf(stdout,"c     = %lg \n",c);
  if (dflag)
    fprintf(stdout,"d     = %lg \n",d);
  if (sflag)
    fprintf(stdout,"str1  = %s \n",str1);  
  if (rflag)
    fprintf(stdout,"str2  = %s \n",str2);  

/*----------------------------------------------------------------------------*/ 
  
  /// Read the input data
  Array2D<double> xdata;
  read_datafileVS(xdata,"xdata.dat");
  // Create output container
  Array1D<double> ydata;
  // Coefficient array (for PC and PC_mi)
  Array1D<double> c_k;

  /// Check which function is requested and compute it
  if (string(fcn_type) =="PC"){
    Array2D<double> c_k_; 
    read_datafileVS(c_k_,param_file);
    array2Dto1D(c_k_,c_k);
    fEval_PC(xdata,ydata, xdata.YSize(), pcord, c_k, str1,a, b);
  }
  else if (string(fcn_type) =="PC_mi"){
    Array2D<double> c_k_; 
    read_datafileVS(c_k_,param_file);
    array2Dto1D(c_k_,c_k);
    fEval_PCmi(xdata,ydata, c_k, str1,str2,a, b);
  }
  else if (string(fcn_type) =="PCmap")
    fEval_PCmap(xdata,ydata,string(str1),a,b,string(str2),c,d);
  else
    throw Tantrum("pce_eval.cpp::Function type is not recognized");

  /// Write the resulting array to a file
  write_datafile_1d(ydata,"ydata.dat");

  /// Gradient info, only available for LU PC
  if (string(fcn_type) =="PC"){
    if (string(str1) =="LU"){
      Array2D<double> gdata;
      /// Write the resulting array to a file
      gEval_PC(xdata,gdata, xdata.YSize(), pcord, c_k, str1,a, b);
      /// Write the resulting 2D array to a file
      write_datafile(gdata,"gdata.dat");
    }
  }

  return ( 0 ) ;

}

/// \brief Evaluates a PC given dimensionality, order, and coefficients array
/// \param[in]  xdata  : Input samples
/// \param[out] ydata  : Output array
/// \param[in]  ndim   : PC dimesnionality
/// \param[in]  nord   : PC order
/// \param[in]  c_k    : Coefficient array
/// \param[in]  pcType : PC type
/// \param[in]  alpha  : PC parameter #1
/// \param[in]  beta   : PC parameter #2
void fEval_PC(Array2D<double>& xdata, Array1D<double>& ydata, int ndim, int nord, Array1D<double>& c_k, char* pcType, double alpha, double beta)
{

  /// Get the number of input points and appropriately resize the output array
  int ns=xdata.XSize();
  ydata.Resize(ns);

  /// Sanity check of dimensionality
  if (ndim != (int) xdata.YSize())
    throw Tantrum("fEval_PC(): the input data does not have the requested dimensionality");

  /// Declare the PC object
  PCSet currPCModel("NISPnoq",nord,ndim,pcType,alpha, beta);
  /// Get the number of terms
  int npc=currPCModel.GetNumberPCTerms();
  assert(npc==c_k.Length());

  /// Evaluate the PC expansion 
  currPCModel.EvalPCAtCustPoints(ydata,xdata,c_k);

  return;

}

/// \brief Evaluates the gradient of a PC given dimensionality, order, and coefficients array (only for LU PC)
/// \param[in]  xdata  : Input samples
/// \param[out] gdata  : Output gradient information stired in 2D array
/// \param[in]  ndim   : PC dimesnionality
/// \param[in]  nord   : PC order
/// \param[in]  c_k    : Coefficient array
/// \param[in]  pcType : PC type
/// \param[in]  alpha  : PC parameter #1
/// \param[in]  beta   : PC parameter #2
void gEval_PC(Array2D<double>& xdata, Array2D<double>& gdata, int ndim, int nord, Array1D<double>& c_k, char* pcType, double alpha, double beta)
{

  /// Get the number of input points
  int ns=xdata.XSize();
  /// Get the dimensionality
  int nd=xdata.XSize();
  /// Resize the output array
  gdata.Resize(ns,nd);

  /// Sanity check of dimensionality
  if (ndim != (int) xdata.YSize())
    throw Tantrum("fEval_PC(): the input data does not have the requested dimensionality");

  /// Declare the PC object
  PCSet currPCModel("NISPnoq",nord,ndim,pcType,alpha, beta);
  /// Get the number of terms
  int npc=currPCModel.GetNumberPCTerms();
  assert(npc==c_k.Length());

  /// Get the multi-indices for this PC representation 
  Array2D<int> mindex;
  currPCModel.GetMultiIndex(mindex);
  /// Evaluate the gradient of th PC expansion 
  currPCModel.dPhi(xdata, mindex, gdata, c_k);

  return;

}

/// \brief Evaluates a PC given multiindex file and coefficients array
/// \param[in]  xdata  : Input samples
/// \param[out] ydata  : Output array
/// \param[in]  c_k    : Coefficient array
/// \param[in]  pcType : PC type
/// \param[in]  nord   : PC multiindex array
/// \param[in]  alpha  : PC parameter #1
/// \param[in]  beta   : PC parameter #2
void fEval_PCmi(Array2D<double>& xdata, Array1D<double>& ydata, Array1D<double>& c_k, char* pcType, char* miFile, double alpha, double beta)
{
  /// Read the multiindex given the file
  Array2D<int> mindex;
  read_datafileVS(mindex,miFile);

  /// Get the number of input points and appropriately resize the output array
  int ns=xdata.XSize();
  ydata.Resize(ns);

  /// Sanity check of dimensionality
  if (mindex.YSize() != xdata.YSize())
    throw Tantrum("fEval_PCmi(): the input data and the multiindex do not have the same dimensionality");

  /// Declare the PC object
  PCSet currPCModel("NISPnoq",mindex,pcType,alpha, beta);

  /// Get the number of terms
  int npc=currPCModel.GetNumberPCTerms();
  assert(npc==c_k.Length());


  /// Evaluate the PC expansion
  currPCModel.EvalPCAtCustPoints(ydata,xdata,c_k);

  return;

}

/// \brief Maps given points according to PC maps, i.e. if x=PC1(\xi) and y=PC2(\xi), this function is y=PC2( PC1^{-1} (x) )
/// \param[in]  xdata  : Input samples
/// \param[out] ydata  : Output array
/// \param[in]  pcIn   : Input PC type (PC1)
/// \param[in]  a      : Input PC parameter #1
/// \param[in]  b      : Input PC parameter #2
/// \param[in]  pcOut  : Output PC type (PC2)
/// \param[in]  c      : Output PC parameter #1
/// \param[in]  d      : Output PC parameter #2
void fEval_PCmap(Array2D<double>& xdata, Array1D<double>& ydata,  string pcIn, double a,double b, string pcOut, double c,double d)
{

  /// Get the number of input points and appropriately resize the output array
  int ns=xdata.XSize();
  int ndim=xdata.YSize();
  ydata.Resize(ns);

  /// Ensure dimensionality = 1
  if (ndim!=1)
    throw Tantrum("fEval_PCmap():Only one-dimensional case is implemented for PCmap!");

  /// Compute the PC map using function in pcmaps.cpp
  for(int i=0;i<ns;i++)
    ydata(i)=PCtoPC(xdata(i,0),pcIn,a,b,pcOut,c,d);
  
  return;
}
