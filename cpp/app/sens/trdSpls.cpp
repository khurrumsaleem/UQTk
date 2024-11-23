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
#include <cstdio>
#include <stddef.h>
#include <fstream>
#include <string>
#include <vector>
#include <math.h>
#include <iostream>
#include <iomanip>     
#include "assert.h"
#include <getopt.h>

using namespace std;

#include "dsfmt_add.h"
#include "error_handlers.h"
#include "probability.h"

#define DPI   6.28318530717959
#define NPTS  129
#define NSPL  10000
#define SEED  0
#define SFILE "samples.dat"
//#define SAVECDF

void usage() {
  printf("Generate random samples for truncated normal or log-normal distributions.\n");
  printf("usage: genSpls [-h] [-a<xmin>] [-b<xmax>] [-m<mean>] [-s<sig>] [-c<npts>] [-n<nspl>] [-t<type>] [-i<seed>] [-f<fname>] \n");
  printf(" -h         : print out this help message \n");
  printf(" -a <xmin>  : lower bound of the sample range (no default) \n");
  printf(" -b <xmax>  : upper bound of the sample range (no default) \n");
  printf(" -m <mean>  : mean of the distribution (no default) \n");
  printf(" -s <sig>   : standard deviation of the distribution (no default) \n");
  printf(" -c <npts>  : no. of points for the discretized CDF map (default=%d) \n",NPTS);
  printf(" -n <nspl>  : no. of random samples (default=%d) \n",NSPL);
  printf(" -i <seed>  : rng seed (default=%d) \n",SEED);
  printf(" -t <type>  : distribution type: \"n\" (normal) / \"ln\" (log-normal) (no default) \n");
  printf(" -f <fname> : file name for output samples (default=%s) \n",SFILE);
  return;
}

/* PDF of normal distribution */
double ndist(double x, double mean, double sig) {
  double s2 = sig*sig;
  return ( exp(-pow(x-mean,2)/(2.0*s2))/sqrt(DPI*s2));
}

/* PDF of log-normal distribution */
double logndist(double x, double mean, double sig) {
  double s2 = sig*sig;
  return ( exp(-pow(log(x)-mean,2)/(2.0*s2))/(x*sqrt(DPI*s2)));
}

/* Create CDF map */
void CDFmap(double xmin, double xmax, double mean, double sig, string type, 
            vector<double> &x,vector<double> &cdfmap) {

  int npts = x.size() ;
  cdfmap.resize(npts,0.0); 
  if ( type == string("n") ) {
    double cdfmin = normcdf((xmin-mean)/sig);
    double cdfmax = normcdf((xmax-mean)/sig);
    for ( int i=1; i<npts-1; i++ ) {
      cdfmap[i] = i/(npts-1.0);
      double cdfi = cdfmin+(cdfmax-cdfmin)*cdfmap[i];
      x[i] = mean+sig*invnormcdf(cdfi);
    }
  }
  else {
    double cdfmin = normcdf((log(xmin)-mean)/sig);
    double cdfmax = normcdf((log(xmax)-mean)/sig);
    for ( int i=1; i<npts-1; i++ ) {
      cdfmap[i] = i/(npts-1.0);
      double cdfi = cdfmin+(cdfmax-cdfmin)*cdfmap[i];
      x[i] = exp(mean+sig*invnormcdf(cdfi));
    }
  }
  x[0] = xmin;
  x[npts-1] = xmax;
  cdfmap[npts-1] = 1.0;

  return ;

}

/* Inverse truncated normal/log-normal CDF */
double invTrCdf(double xmin, double xmax, double mean, double sig, string type, double xi) {

  double cdfmin, cdfmax, cdfi ;
  if ( type == string("n") ) {
    cdfmin = normcdf((xmin-mean)/sig) ;
    cdfmax = normcdf((xmax-mean)/sig) ;
    cdfi   = cdfmin+xi*(cdfmax-cdfmin) ;
    return (mean+sig*invnormcdf(cdfi));
  }
  else {
    cdfmin = normcdf((log(xmin)-mean)/sig);
    cdfmax = normcdf((log(xmax)-mean)/sig);
    cdfi   = cdfmin+xi*(cdfmax-cdfmin) ;
    return (exp(mean+sig*invnormcdf(cdfi)));
  }

}

int main(int argc, char *argv[]) {

  int  npts  = NPTS ;
  int  nspl  = NSPL ;
  int  iseed = SEED ;
  double xmin=0.0, xmax=0.0, mean=0.0, sig=0.0 ;
  bool xminSet, xmaxSet, meanSet, sigSet, typeSet ;
  char *sfile = (char *)SFILE ;
  string type;
  dsfmt_t RandomState; /* random number structure */

  /* Read user input */
  xminSet = xmaxSet = meanSet = sigSet = typeSet = false;
  int c;
  while ((c=getopt(argc,(char **)argv,"ha:b:m:s:c:n:t:i:f:"))!=-1){
    switch (c) {
    case 'h':
      usage();
      return (0);
      break;
    case 'a':
      xminSet = true;
      xmin = strtod(optarg, (char **)NULL);
      break;
    case 'b':
      xmaxSet = true;
      xmax = strtod(optarg, (char **)NULL);
      break;
    case 'm':
      meanSet = true;
      mean = strtod(optarg, (char **)NULL);
      break;
    case 's':
      sigSet = true;
      sig = strtod(optarg, (char **)NULL);
      break;
    case 'c':
      npts = strtol(optarg, (char **)NULL,0);
      break;
    case 'n':
      nspl = strtol(optarg, (char **)NULL,0);
      break;
    case 'i':
      iseed = strtol(optarg, (char **)NULL,0);
      break;
    case 't':
      typeSet = true;
      type = string(optarg);
      break;
    case 'f':
      sfile = optarg;
      break;
   }
  }

  /* Check if all things are set */ 
  if ( !typeSet ) { printf("Need to set the distribution type !\n"); exit(1);}
  if ( !xminSet ) { printf("Need to set lower bound !\n"); exit(1);}
  if ( !xmaxSet ) { printf("Need to set upper bound !\n"); exit(1);}
  if ( (type == string("n")) || (type == string("ln")) ){
    if ( !meanSet ) { printf("Need to set the mean !\n"); exit(1);}
    if ( !sigSet  ) { printf("Need to set the standard deviation !\n"); exit(1);}
  }
  /* Check a few things for consistency */
  if ( xmin >= xmax) { printf("Error: Lower bound is greater than upper bound !\n"); exit(1);}
  if (( type == string("n") ) && ( ( xmin >= mean ) || (xmax <= mean ) )){ 
    printf("Warning: Mean is outside the range !\n");
  }
  if (( type == string("ln") ) && ( ( log(xmin) >= mean ) || (log(xmax) <= mean ) )){ 
    printf("Warning: Mean is outside the range !\n");
  }

  if ( ( type != string("n") ) && ( type != string("ln") ) && ( type != string("u") ) ) {
    printf("Error: Distribution type should be either \"n\" or \"ln\" or \"u\" !\n"); exit(1);
  }

#ifdef USECDFMAP
  vector<double> x(npts);
  vector<double> cdfmap(npts);
  if ( (type == string("n")) || (type == string("ln")) )
    CDFmap(xmin, xmax, mean, sig, type, x, cdfmap);
#endif

  /* generate and output samples */
  ofstream sout(sfile);
  if(!sout){ printf("Error : Could not open file %s\n",sfile) ; exit(1) ;}
  dsfmt_init_gen_rand(&RandomState,iseed);
  for ( int i=0; i<nspl; i++ ) {
    double uxi = dsfmt_genrand_urv(&RandomState);
    double xspl ;
#ifdef USECDFMAP
    if ( (type == string("n")) || (type == string("ln")) ) {
      int iseg = 0;
      for ( int j=1; j<npts; j++ )
        if ( uxi < cdfmap[j] ) {
          iseg = j-1;
          break;
        }
      xspl = x[iseg]+(x[iseg+1]-x[iseg])*(uxi-cdfmap[iseg])/(cdfmap[iseg+1]-cdfmap[iseg]);
    } else
#else
    if ( (type == string("n")) || (type == string("ln")) )
       xspl = invTrCdf(xmin, xmax, mean, sig, type, uxi);
    else
#endif
      xspl = xmin+(xmax-xmin)*uxi;
    sout << setprecision(9) << xspl << endl;
  }
  sout.close();

#ifdef USECDFMAP
#ifdef SAVECDF
  ofstream cdfout("cdfmap.dat");
  if(!cdfout){ printf("Error : Could not open file cdfmap.dat\n") ; exit(1) ;}
  for ( int i=0; i<npts; i++ ) {
    cdfout << x[i] << " "<< cdfmap[i] << endl;
  }
  cdfout.close();
#endif
#endif

  return (0) ;

}

