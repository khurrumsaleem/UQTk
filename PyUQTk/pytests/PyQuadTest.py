#=====================================================================================
#
#                      The UQ Toolkit (UQTk) version 3.1.5
#                          Copyright (2024) NTESS
#                        https://www.sandia.gov/UQToolkit/
#                        https://github.com/sandialabs/UQTk
#
#     Copyright 2024 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
#     Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government
#     retains certain rights in this software.
#
#     This file is part of The UQ Toolkit (UQTk)
#
#     UQTk is open source software: you can redistribute it and/or modify
#     it under the terms of BSD 3-Clause License
#
#     UQTk is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     BSD 3 Clause License for more details.
#
#     You should have received a copy of the BSD 3 Clause License
#     along with UQTk. If not, see https://choosealicense.com/licenses/bsd-3-clause/.
#
#     Questions? Contact the UQTk Developers at https://github.com/sandialabs/UQTk/discussions
#     Sandia National Laboratories, Livermore, CA, USA
#=====================================================================================
from __future__ import print_function # To make print() in Python 2 behave like in Python 3

# include path to include PyUQTk
import sys
sys.path.append('../pyuqtkarray/')
sys.path.append('../quad/')
sys.path.append('../')


import os
src = os.getenv('UQTK_SRC')

sys.path.append('../pyuqtkarray_tools')

try:
	import numpy as np
except ImportError:
	print("Need numpy to test PyUQTk")

# import numpy as np

try:
	import _uqtkarray as uqtkarray
	import pyuqtkarray_tools as tools
except ImportError:
	print("PyUQTk array modules not found")

try:
	import _quad as uqtkquad
except ImportError:
	print("PyUQTk quad module not found")

'''
This file tests the quadrature pyqutk routine
'''

# true quad points for sparse LU with ndim = 2 and level = 3
qpnts_ref = np.array([[-9.681602395076263079e-01, 0.000000000000000000e+00],
[-9.061798459386638527e-01, -7.745966692414832933e-01],
[-9.061798459386638527e-01, 0.000000000000000000e+00],
[-9.061798459386638527e-01, 7.745966692414834043e-01],
[-8.360311073266358806e-01, 0.000000000000000000e+00],
[-7.745966692414832933e-01, -9.061798459386638527e-01],
[-7.745966692414832933e-01, -7.745966692414832933e-01],
[-7.745966692414832933e-01, -5.384693101056832187e-01],
[-7.745966692414832933e-01, 0.000000000000000000e+00],
[-7.745966692414832933e-01, 5.384693101056829967e-01],
[-7.745966692414832933e-01, 7.745966692414834043e-01],
[-7.745966692414832933e-01, 9.061798459386638527e-01],
[-6.133714327005902467e-01, 0.000000000000000000e+00],
[-5.384693101056832187e-01, -7.745966692414832933e-01],
[-5.384693101056832187e-01, 0.000000000000000000e+00],
[-5.384693101056832187e-01, 7.745966692414834043e-01],
[-3.242534234038090268e-01, 0.000000000000000000e+00],
[0.000000000000000000e+00, -9.681602395076263079e-01],
[0.000000000000000000e+00, -9.061798459386638527e-01],
[0.000000000000000000e+00, -8.360311073266358806e-01],
[0.000000000000000000e+00, -7.745966692414832933e-01],
[0.000000000000000000e+00, -6.133714327005902467e-01],
[0.000000000000000000e+00, -5.384693101056832187e-01],
[0.000000000000000000e+00, -3.242534234038090268e-01],
[0.000000000000000000e+00, 0.000000000000000000e+00],
[0.000000000000000000e+00, 3.242534234038088048e-01],
[0.000000000000000000e+00, 5.384693101056829967e-01],
[0.000000000000000000e+00, 6.133714327005905798e-01],
[0.000000000000000000e+00, 7.745966692414834043e-01],
[0.000000000000000000e+00, 8.360311073266353254e-01],
[0.000000000000000000e+00, 9.061798459386638527e-01],
[0.000000000000000000e+00, 9.681602395076263079e-01],
[3.242534234038088048e-01, 0.000000000000000000e+00],
[5.384693101056829967e-01, -7.745966692414832933e-01],
[5.384693101056829967e-01, 0.000000000000000000e+00],
[5.384693101056829967e-01, 7.745966692414834043e-01],
[6.133714327005905798e-01, 0.000000000000000000e+00],
[7.745966692414834043e-01, -9.061798459386638527e-01],
[7.745966692414834043e-01, -7.745966692414832933e-01],
[7.745966692414834043e-01, -5.384693101056832187e-01],
[7.745966692414834043e-01, 0.000000000000000000e+00],
[7.745966692414834043e-01, 5.384693101056829967e-01],
[7.745966692414834043e-01, 7.745966692414834043e-01],
[7.745966692414834043e-01, 9.061798459386638527e-01],
[8.360311073266353254e-01, 0.000000000000000000e+00],
[9.061798459386638527e-01, -7.745966692414832933e-01],
[9.061798459386638527e-01, 0.000000000000000000e+00],
[9.061798459386638527e-01, 7.745966692414834043e-01],
[9.681602395076263079e-01, 0.000000000000000000e+00]])

# initiate uqtk arrays for quad points and weights
x = uqtkarray.dblArray2D()
w = uqtkarray.dblArray1D()

# create instance of quad class and output
# points and weights
print('Create an instance of Quad class')
ndim = 2
level = 3
q = uqtkquad.Quad('LU','sparse',ndim,level,0,1)
print('Now set and get the quadrature rule...')
q.SetRule()
q.GetRule(x,w)

# print out x and w
print('Displaying the quadrature points and weights:\n')
x_np = tools.uqtk2numpy(x)
print(x_np)
n = x.XSize()
print('Number of quad points is ', n, '\n')

# plot the quadrature points
# print('Plotting the points (get points in column major order as a flattened vector)')
# print('need to use reshape with fortran ordering')
xpnts = np.zeros((n,ndim))
xpnts = uqtkarray.getnpdblArray(x)
# plot(xpnts[:,0], xpnts[:,1],'ob',ms=10,alpha=.25)
# show()

# convert the quad weights to numpy arrays
w_np = np.zeros(n)
#w.getnpdblArray(w_np,n)
w_np = uqtkarray.getnpdblArray(w)

# asserting the quadrature points are correct
dec_place=14
reg=(np.round(x_np, dec_place)==np.round(qpnts_ref, dec_place))
assert (np.all(reg) and reg[0,0]==True)
print("The quadrature points agree to within %d decimal places."%(dec_place))
