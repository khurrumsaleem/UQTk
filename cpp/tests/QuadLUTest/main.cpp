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
#include <iostream>
#include "math.h"
#include "Array1D.h"
#include "Array2D.h"
#include "mcmc.h"
#include "quad.h"
#include "dsfmt_add.h"
#include "arrayio.h"
#include "arraytools.h"
#include "assert.h"

using namespace std;

/*************************************************
Begin main code
*************************************************/
int main(int argc, char ** argv){

	/*************************************************
	get 2d quadrature points
	*************************************************/
	Array2D<double> x;
	Array1D<double> w;

	int ndim = 2;
	int level = 5;
	Quad q("LU","sparse",ndim,level,0,1);

	q.SetRule();
	q.GetRule(x,w);

	// Array2D<double> x_ref(x.XSize(),x.YSize(),0);
	// Array1D<double> w_ref(w.Length(),0);

	// read_datafile(x_ref,"quadpnts.txt");
	// read_datafile_1d(w_ref,"quadwghts.txt");

	// // check to make sure weights are correct
	// for (int i = 0; i < w.Length(); i++){
	// 	double error = fabs(w(i) - w_ref(i));
	// 	assert(error < 1e-16);
	// }

	// // check to make sure points are correct
	// for (int i = 0; i < w.Length(); i++){
	// 	double error_x1 = fabs(x(i,0) - x_ref(i,0));
	// 	double error_x2 = fabs(x(i,1) - x_ref(i,1));
	// 	assert(error_x1 < 1e-16);
	// 	assert(error_x2 < 1e-16);
	// }

	double sum = 0e0;
	double sum2 = 0e0;
	double sum3 = 0e0;
	for (int i = 0; i < w.Length(); i++){
		sum += w(i);
		sum2 += pow(x(i,0),2)*w(i);
		sum3 += pow(x(i,1),2)*pow(x(i,0),2)*w(i);
	}
	assert(fabs(sum - 1) < 1e-12); // sum of weights is 1
	assert(fabs(sum2 - 1./3) < 1e-12); // int of x^2 is 1/3
	assert(fabs(sum3 - 1./9) < 1e-12); // int of x^2y^2 is 1/9


	return 0;

}
