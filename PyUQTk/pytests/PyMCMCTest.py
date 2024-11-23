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
sys.path.append('../../')

try:
	from numpy import *
except ImportError:
	print('NumPy needed to test PyUQTk')
try:
	from matplotlib.pyplot import *
	print('Matplotlib needed to test PyUQTk')
except ImportError:
try:
	import time
except ImportError:
	print("Time module needed to test PyUQTk")

try:
	import PyUQTk.array as uqtkarray
except ImportError:
	print("PyUQTk array module not found")
try:
	import PyUQTk.quad as uqtkquad
except ImportError:
	print("PyUQTk quad module not found")
try:
	import PyUQTk.mcmc as uqtkmcmc
except ImportError:
	print("PyUQTk mcmc module not found")

# class pyLikelihood(uqtkmcmc.LikelihoodBase):
# 	def eval(self,x):
# 		x0 = x[0]
# 		x1 = x[1]
# 		return -(1-x0)*(1-x0) - 100*(x1 - x0*x0)*(x1 - x0*x0)
# class pyLikelihood(uqtkmcmc.LikelihoodBase):
# 	def eval(self,x):
# 		'''
# 		sample from 1./(abs(1-x**2))
# 		'''
# 		y1 = x[0]
# 		y2 = x[1]
# 		if sqrt(y1**2 + y2**2) > 1:
# 			return -1e16
# 		else:
# 			return -.0001*log(1 - y2**2 - y1**2)
class pyLikelihood(uqtkmcmc.LikelihoodBase):
	def eval(self,x):
		'''
		sample from exp(-.5*(x**2/.1**2 - y**2/.8**2))
		'''
		y1 = x[0]
		y2 = x[1]
		return -.5*(y1**2/.1**2 + y2**2/.8**2)

start = time.time()
# testing MCMC library
print('\n*****************\nTesting MCMC\n*****************\n')
print('Setting LogPosterior function, L')
print('L is defined in uqtk.cpp (Rosenbrock function)')
L = pyLikelihood()
print('Testing logposterior function')
xstart = uqtkarray.dblArray1D(2,0)
print(xstart)
print('L.eval(x) =  ', L.eval(xstart))

print('Setting up the sampler')
mchain = uqtkmcmc.MCMC(L)

print('Setting chain dim, type (ss), initial proposal covariance')
dim = 2
mchain.setChainDim(dim)
mchain.initMethod("am")
g = uqtkarray.dblArray1D(dim,.5)
mchain.initChainPropCovDiag(g)

print('Running chain to chain.dat ...')
nCalls = 100000
# mchain.setOutputInfo("txt","chain.dat",nCalls,nCalls);
mchain.setWriteFlag(0)
mchain.runChain(nCalls,xstart);

print('Getting samples into numpy array...')
mchain.getSamples()
samples = array(mchain.samples).T[3000::5,:]
print(std(samples,0) - array([.1,.8]))

# print('loading samples and plotting')
# thin = 25
# samples = loadtxt('chain.dat')[3001:-1:thin,1:3]
# figure()
# plot(samples[:,0],samples[:,1],'.')


# # get quad points and weights
# x = uqtkarray.dblArray2D()
# w = uqtkarray.dblArray1D()

# print('Create an instance of Quad class')
# ndim = 2
# level = 5
# q = uqtkquad.Quad('LU','sparse',ndim,level,0,1)
# print('Now set and get the quadrature rule...')
# q.SetRule()
# q.GetRule(x,w)

# # print out x and w
# print('Displaying the quadrature points and weights:\n')
# # print(x)
# # print(w)
# n = len(x)
# print('Number of quad points is ', n, '\n')

# # now we plot the points
# print('Plotting the points (get points in column major order as a flattened vector)')
# print('need to use reshape with fortran ordering')
# xpnts = zeros((n,ndim))
# x.getnpdblArray(xpnts)
# plot(xpnts[:,0], xpnts[:,1],'ob',ms=10,alpha=.25)
# savefig('quadpnts.pdf')

# # get quad weights
# w_np = zeros(n)
# w.getnpdblArray(w_np)
# clf()
# plot(w,'ro-',lw=4)
# savefig('quadweights.pdf')
