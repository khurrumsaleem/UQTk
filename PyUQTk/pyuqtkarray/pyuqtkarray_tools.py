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

import numpy as np
import sys

sys.path.append('../pyuqtkarray')

try:
    import _uqtkarray as pyuqtkarray
except ImportError:
    print("PyUQTk array module not found")
    print("If installing in a directory other than the build directory, make sure PYTHONPATH includes the install directory")

def uqtk2numpy(x):
    if x.type() == 'int':
        s = x.shape()
        imin = np.argmin(s)
        if len(s) == 1:
            n = s[0]
            y = np.zeros(n,dtype='int64')
            y = pyuqtkarray.getnpintArray(x)
        if len(s) == 2:
            #n = s[0]
            #m = s[1]
            #z = np.zeros((n,m),dtype='int64')
            #z = pyuqtkarray.getnpintArray(x)
            #y = fixer(z)
            list = pyuqtkarray.getnpintArray(x)
            m = x.XSize();
            n = x.YSize();
            y = np.full((m,n),0,dtype=int)
            counter = 0
            for i in range(m):
                for j in range(n):
                    y[i,j]=list[counter]
                    counter = counter + 1
#        if len(s) == 2 and np.amin(s) == 1:
#            y = np.array(x.flatten())
#            y = y[...,None]
        return y.copy()
    else:
        s = x.shape()
        imin = np.argmin(s)
        if len(s) == 1:
            n = s[0]
            y = np.zeros(n)
            y = pyuqtkarray.getnpdblArray(x)
        if len(s) == 2:
            list = pyuqtkarray.getnpdblArray(x)
            m = x.XSize();
            n = x.YSize();
            y = np.full((m,n),0,dtype=float)
            counter = 0
            for i in range(m):
                for j in range(n):
                    y[i,j]=list[counter]
                    counter = counter + 1
#        if len(s) == 2 and np.amin(s) == 1:
#            y = np.array(x.flatten())
#            y = y[...,None]
        return y.copy()

def numpy2uqtk(y):
    if (y.dtype.name).find('int')>=0:
        s = np.shape(y)
        if len(s) == 1:
            n = s[0]
            x = pyuqtkarray.intArray1D(n)
            x.setnpintArray(y,n)
        if len(s) == 2:
            n = s[0]
            m = s[1]
            x = pyuqtkarray.intArray2D(n,m)
            for i in range(n):
                for j in range(m):
                    x.assign(i, j, y[i][j])
            # pyuqtkarray.setnpintArray(x,np.asfortranarray(y.copy()))
    elif (y.dtype.name).find('float')>=0:
        s = np.shape(y)
        if len(s) == 1:
            n = s[0]
            x = pyuqtkarray.dblArray1D(n)
            x.setnpdblArray(y,n)
        if len(s) == 2:
            n = s[0]
            m = s[1]
            x = pyuqtkarray.dblArray2D(n,m)
            #pyuqtkarray.setnpdblArray(x,np.asfortranarray(y.copy()))
            for i in range(n):
                for j in range(m):
                    x.assign(i, j, y[i][j])
    else:
        print('numpy2uqtk accepts arrays of integers or floats only')

    return x
