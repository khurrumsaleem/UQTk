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

# This is only necessary for the user to pass the ctest without the need for install
import sys
sys.path.append('../pyuqtkarray/')
sys.path.append('../pce/')
sys.path.append('../quad/')
sys.path.append('../tools/')
sys.path.append('../..')
sys.path.append('../utils/')

# Import Modules
try:
    import uqtkarray
except ImportError:
    print('PyUQTk array module not found')
try:
    import quad as uqtkquad
except ImportError:
    print('PyUQTk quad module not found')
try:
    import pce as uqtkpce
except ImportError:
    print('PyUQTk pce module not found')
try:
    import tools as uqtktools
except ImportError:
    print('PyUQTk tools module not found')
try:
    import bcs as bcs
except ImportError:
    print('PyUQTk bcs module not found')
try:
    import utils.multiindex as uqtkmi
except ImportError:
    print('PyUQTk utils.multiindex module not found')
try:
    import numpy as np
except ImportError:
    print("Numpy module could not be found")
try:
    from scipy import stats
    import math
except ImportError:
    print("Scipy stats or math module could not be found")
try:
    import matplotlib.pyplot as plt
    from matplotlib import rc
    rc('mathtext', default='regular')
except ImportError:
    print("Matplotlib not found")
try:
    from functools import reduce
except ImportError:
    print('functools module could not be found')

################################################################################
def UQTkMap2PCE(pc_model,rvs_in,verbose=0):
    """Obtain PC representation for the random variables that are described by samples.
    Employ a Rosenblatt transformation to build a map between the input RVs and the space
    of the PC germ.
    Input:
        pc_model: object with properties of the PCE to be constructed
        rvs_in    : numpy array with input RV samples. Each line is a sample. The columns
                  represent the dimensions of the input RV.
        verbose : verbosity level (more output for higher values)

    Output:
        Numpy array with PC coefficients for each RV in the original rvs_in input
    """

    # Dimensionality and number of samples of input RVs
    ndim = rvs_in.shape[1]
    nsamp = rvs_in.shape[0]

    # Algorithm parameters
    bw = -1 # KDE bandwidth for Rosenblatt (on interval 0.1)
    iiout = 50 # interval for output to screen

    # Number of PCE terms
    npce = pc_model.GetNumberPCTerms()

    # Get the default quadrature points
    qdpts = uqtkarray.dblArray2D()
    pc_model.GetQuadPoints(qdpts)

    totquat = pc_model.GetNQuadPoints()
    if (verbose>0):
        print("Total number of quadrature points =",totquat)

    # Set up transpose of input data for the inverse Rosenblatt transformation in a UQTk array
    ydata_t = uqtkarray.dblArray2D(ndim,nsamp)
    #ydata_t.setnpdblArray(np.asfortranarray(rvs_in.T))
    y_data_t=uqtkarray.numpy2uqtk(np.asfortranarray(rvs_in.T))

    # Set up numpy array for mapped quadrature points
    invRosData = np.zeros((totquat,ndim))

    # Map all quadrature points in chosen PC set to the distribution given by the data
    # using the inverse Rosenblatt transformation
    for ipt in range(totquat):

        # print("Converting quadrature point #",ipt)

        # Set up working arrays
        quadunif = uqtkarray.dblArray1D(ndim,0.0)
        invRosData_1s = uqtkarray.dblArray1D(ndim,0.0)

        # First map each point to uniform[0,1]
        # PCtoPC maps to [-1,1], which then gets remapped to [0,1]
        for idim in range(ndim):
            quadunif[idim] = (uqtktools.PCtoPC(qdpts[ipt,idim],pc_model.GetPCType(),pc_model.GetAlpha(),pc_model.GetBeta(),"LU",0.0,0.0)+1.0)/2.0

        # Map each point from uniform[0,1] to the distribution given by the original samples via inverse Rosenblatt
        if bw > 0:
            uqtktools.invRos(quadunif,ydata_t,invRosData_1s,bw)
        else:
            uqtktools.invRos(quadunif,ydata_t,invRosData_1s)

        # Store results
        for idim in range(ndim):
            invRosData[ipt,idim] = invRosData_1s[idim]

        # Screen diagnostic output
        if (verbose>0):
            if ((ipt+1)%iiout == 0) or ipt==0 or (ipt+1)==totquat:
                print("Inverse Rosenblatt for Galerkin projection:",(ipt+1),"/",totquat,"=",(ipt+1)*100/totquat,"% completed")

    # Get PC coefficients by Galerkin projection
    # Set up numpy array for PC coefficients (one column for each transformed random variable)
    c_k = np.zeros((npce,ndim))

    # Project each random variable one by one
    # Could replace some of this with the UQTkGalerkinProjection function below
    for idim in range(ndim):

        # UQTk array for PC coefficients for one variable
        c_k_1d = uqtkarray.dblArray1D(npce,0.0)

        # UQTk array for map evaluations at quadrature points for that variable
        invRosData_1d = uqtkarray.dblArray1D(totquat,0.0)
        # invRosData_1d.setnpdblArray(np.asfortranarray(invRosData[:,idim])
        for ipt in range(totquat):
            invRosData_1d[ipt]=invRosData[ipt,idim]

        # Galerkin Projection
        pc_model.GalerkProjection(invRosData_1d,c_k_1d)

        # Put coefficients in full array
        for ip in range(npce):
            c_k[ip,idim] = c_k_1d[ip]

    # Return numpy array of PC coefficients
    return c_k
################################################################################
def UQTkEvalPC(pce_model,pce_coeffs,germ_sample):
    """
    Use UQTkEvaluatePCE instead
    """
    print("Use UQTkEvaluatePCE instead of UQTkEvalPC.")
    exit(1)
################################################################################
def UQTkDrawSamplesPCE(pc_model,pc_coeffs,n_samples):
    """
    Draw samples of the germ underneath the pc_model and evaluates one PCE
    for those samples.

    Input:
        pc_model:   PC object with into about PCE
        pc_coeffs:  1D numpy array with PC coefficients of the RV to be evaluated. [n_dim]
        n_samples:    number of samples to be drawn
    Output:
        1D Numpy array with PCE evaluations

    """

    #need a 1d array passed into pc_coeffs
    if(len(pc_coeffs.shape) != 1):
        print("UQTkEvaluatePCE only takes one PCE. pc_coeff needs to be 1 dimension.")
        exit(1)

    #get number of nTerms
    npce = pc_model.GetNumberPCTerms()

    # Create and fill UQTk array for PC coefficients
    p = uqtkarray.dblArray1D(npce,0.0)
    for ip in range(npce):
        #p[ip] = pc_coeffs[ip]
        p.assign(ip,pc_coeffs[ip])

    #create UQTk array to store outputs in
    samples = uqtkarray.dblArray1D(n_samples,0.0)

    #draw the samples
    pc_model.DrawSampleSet(p, samples)

    #convert samples to a numpy array
    pce_samples = np.zeros(n_samples)
    for isamp in range(n_samples):
        pce_samples[isamp] = samples[isamp]

    #return samples in numpy array
    return pce_samples
################################################################################
def UQTkEvaluatePCE(pc_model,pc_coeffs,samples):
    """
    Evaluate PCE at a set of samples of this PCE
    Input:
        pc_model:   PC object with into about PCE
        pc_coeffs:  1D numpy array with PC coefficients of the RV to be evaluated. [npce]
        samples:    2D numpy array with samples of the PCE at which the RV
                    are to be evaluated. Each line is one sample. [n_samples, ndim]
    Output:
        1D Numpy array with PCE evaluations [n_test_samples,]
    """

    #need a 1d array passed into pc_coeffs
    if(len(pc_coeffs.shape) != 1):
        print("UQTkEvaluatePCE only takes one PCE. pc_coeff needs to be 1 dimension.")
        exit(1)

    # Get data set dimensions etc.
    n_test_samples = samples.shape[0]
    npce = pc_model.GetNumberPCTerms()

    # Put PC samples in a UQTk array
    if len(samples.shape)>1:
        ndim = samples.shape[1]
        std_samples_uqtk = uqtkarray.dblArray2D(n_test_samples, ndim)
        std_samples_uqtk = uqtkarray.numpy2uqtk(np.asfortranarray(samples))
    else:
        std_samples_uqtk=uqtkarray.dblArray2D(n_test_samples,1) #UQTk array for samples - [nsam, ndim]
        for i in range(n_test_samples):
            std_samples_uqtk.assign(i, 0, samples[i])

    # Create and fill UQTk array for PC coefficients
    c_k_1d_uqtk = uqtkarray.dblArray1D(npce,0.0)
    for ip in range(npce):
        c_k_1d_uqtk.assign(ip,pc_coeffs[ip])

    # Create UQTk array to store outputs in
    rv_from_pce_uqtk = uqtkarray.dblArray1D(n_test_samples,0.0)

    # Evaluate the PCEs for reach input RV at those random samples
    pc_model.EvalPCAtCustPoints(rv_from_pce_uqtk,std_samples_uqtk,c_k_1d_uqtk)

    # Numpy array to store all RVs evaluated from sampled PCEs
    rvs_sampled = np.zeros((n_test_samples,))

    # Put evaluated samples in full 2D numpy array
    for isamp in range(n_test_samples):
        rvs_sampled[isamp] = rv_from_pce_uqtk[isamp]

    # return numpy array of PCE evaluations
    return rvs_sampled
################################################################################
def UQTkGalerkinProjection(pc_model,f_evaluations):
    """
    Obtain PC coefficients by Galerkin Projection via UQTk

    Note: Need to generalize this to allow projecting multiple variables at a time

    Input:
        pc_model : PC object with info about basis to project on
        f_evaluations: 1D numpy array (vector) with function to be projected,
                       evaluated at the quadrature points [npq,]
    Output:
        1D Numpy array with PC coefficients [npce,]
    """

    # Sends error message if y-values are multi-dimensional
    if len(f_evaluations.shape) > 1:
        print("This function can only project single variables for now")
        exit(1)

    # Get parameters
    npce = pc_model.GetNumberPCTerms()  # Number of PC terms
    nqp = f_evaluations.shape[0]        # Number of quadrature points

    # UQTk array for PC coefficients for one variable
    c_k_1d_uqtk = uqtkarray.dblArray1D(npce,0.0)

    # UQTk array for function evaluations at quadrature points for that variable
    f_uqtk = uqtkarray.dblArray1D(nqp,0.0)
    for ipt in range(nqp):
        f_uqtk.assign(ipt,f_evaluations[ipt])

    # Galerkin Projection
    pc_model.GalerkProjection(f_uqtk,c_k_1d_uqtk)

    # Put PC coefficients in numpy array
    c_k = np.zeros(npce)
    for ip in range(npce):
        c_k[ip] = c_k_1d_uqtk[ip]

    # Return numpy array of PC coefficients
    return c_k
################################################################################
def UQTkRegression(pc_model,f_evaluations, samplepts):
    """
    Obtain PC coefficients by regression

    Note: Need to generalize this to allow projecting multiple variables at a time

    Input:
        pc_model :     PC object with info about basis
        f_evaluations: 1D NumPy array (vector) with function evaluated at the
                            sample points [nsam,]
        samplepts:     n-dimensional NumPy array with sample points
                            [nsam, ndim]
    Output:
        1D Numpy array with PC coefficients for each PC term [npce,]
    """

    # Sends error message if y-values are multi-dimensional
    if len(f_evaluations.shape) > 1:
        print("This function can only project single variables for now")
        exit(1)

    # Get parameters
    npce = pc_model.GetNumberPCTerms()  # Number of PC terms
    nsam = f_evaluations.shape[0]       # Number of sample points

    # Create UQTk array for sample points - [nsam, ndim]
    # if dim>1
    if len(samplepts.shape)>1:
        ndim=samplepts.shape[1]         # Number of dimensions
        sam_uqtk=uqtkarray.numpy2uqtk(np.asfortranarray(samplepts))
    # if dim = 1
    else:
        sam_uqtk=uqtkarray.dblArray2D(nsam,1)
        for i in range(nsam):
            sam_uqtk.assign(i, 0, samplepts[i])

    # UQTk array for the basis terms evaluated at the sample points
    psi_uqtk = uqtkarray.dblArray2D()
    pc_model.EvalBasisAtCustPts(sam_uqtk, psi_uqtk)

    # NumPy array for basis terms evaluated at the sample points - [nsam, npce]
    psi_np = uqtkarray.uqtk2numpy(psi_uqtk)

    # Regression
    c_k, resids, rank, s = np.linalg.lstsq(psi_np,f_evaluations,rcond=None)

    # Return numpy array of PC coefficients
    return c_k
################################################################################
def UQTkBCS(pc_begin, xdata, ydata, eta=1.e-3, niter=1, mindex_growth=None, ntry=1,\
            eta_folds=5, eta_growth = False, eta_plot = False,\
            regparams=None, sigma2=1e-8, npccut=None, pcf_thr=None,\
            verbose=0, return_sigma2=False):
    """
    Obtain PC coefficients by Bayesian compressive sensing

    Note: Need to generalize this to allow multiple variables at a time
    ToDo: add documentation in UQTk manual on what BCS is and the basis growth schemes

    Input:
        pc_begin:   PC object with information about the starting basis
        xdata:      N-dimensional NumPy array with sample points [#samples,
                            #dimensions]
        ydata:      1D numpy array (vector) with function, evaluated at the
                            sample points [#samples,]
        eta:        NumPy array, list, or float with the threshold for
                            stopping the algorithm. Smaller values
                            retain more nonzero coefficients. If eta is an array/list,
                            the optimum value of the array is chosen. If a float,
                            the given value is used.
        niter:      Number of iterations for order growth
        mindex_growth: Method for basis growth; options are None,
                            'nonconservative', 'conservative'; default is 'None'
        ntry:       Number of splits for cross-validation of the retained basis
                            through bcs; default is 1
        eta_folds:  Number of folds to use for eta cross-valiation; default is 5
        eta_growth: Flag for using basis growth in eta optimization
        eta_plot    Flag for saving a plot of etas vs. RMSE
        regparams:  Regularization weights
                            To set a fixed scalar, provide a fixed nonnegative value.
                            To autopopulate a scalar, set regparams = 0.
                            To set a fixed vector of weights, provide an array [#PC terms,].
                            To autopopulate a vector, set reg_params = None, which is the suggested method.
        sigma2:     Inital noise variance we assume is in the data; default is 1e-8
        npccut:     Maximum number of PC terms to retain, for pruning 'by hand';
                            default is None
        pcf_thr:    Minimum value (magnitude) for PC coefficients, for pruning low PC coefficients 'by hand'
                            default is None
        verbose:    Flag for optional print statements
        return_sigma2:   Flag to retun reestimated sigma2


    Output:
        pc_model_final: PC object with basis expanded by the iterations
        cfs_final:      1D Numpy array with PC coefficients for each term of the final
                        model [#terms_in_final_basis,]
        sigma2:         data noise variance, updated by bcs algorithm (if desired), scalar
    """

    # Sends error message if y-values are multi-dimensional
    if len(ydata.shape) > 1:
        print("This function can only project single variables for now.")
        exit(1)

    # Choose whether to optimize eta
    if (type(eta)==np.float64 or type(eta)==float):
        eta_opt = eta
    elif (type(eta)==np.ndarray or type(eta)==list):
        # the eta with the lowest RMSE is selected from etas
        if eta_growth:
            # Get optimal eta through CV and grow the basis to full order in each fold
            eta_opt = UQTkOptimizeEta(pc_begin, ydata, xdata, eta, niter, eta_folds, mindex_growth, verbose, eta_plot)
        else:
            # Get optimal eta through CV, but stick to initial basis in each fold for efficiency
            eta_opt = UQTkOptimizeEta(pc_begin, ydata, xdata, eta, 1, eta_folds, None, verbose, eta_plot)
        if verbose:
            print("Optimal eta is", eta_opt)
    else:
        print("Invalid input for eta.")

    #set up parameters
    nsam = xdata.shape[0] # Number of samples in xdata

    trval_frac=1/ntry #Fraction of the total input data to use in each split;
    ntrain = int(trval_frac * nsam) # Number of training samples per split

    mi_selected = []


    # set regularization weights
    if regparams is None:
        regparams = np.array([])
    elif type(regparams)==int or type(regparams)==float:
        regparams = regparams*np.ones((pc_begin.GetNumberPCTerms(),))

    if mindex_growth == None:
        full_basis_size = pc_begin.GetNumberPCTerms()
    else:
        full_basis_size = uqtkpce.PCSet("NISPnoq", pc_begin.GetOrder() + niter -1, pc_begin.GetNDim(), pc_begin.GetPCType(), pc_begin.GetAlpha(), pc_begin.GetBeta()).GetNumberPCTerms()

    # loop through iterations with different splits of the data
    for i in range(ntry):
        # Split the data
        ind_tr, ind_val = ind_split(nsam, 'trval', [ntrain, nsam - ntrain])
        x_split=xdata[ind_tr,:]
        y_split=ydata[ind_tr]

        if verbose>0:
            print("============  Split # %d / %d ============" % (i + 1, ntry))

        pc_model = pc_begin # reinitialize pc_model for each split

        # Iterations of multiindex growth
        for j in range(niter):
            # Retrieve multiindex
            mi_uqtk = uqtkarray.intArray2D(pc_model.GetNumberPCTerms(), nsam)
            pc_model.GetMultiIndex(mi_uqtk)
            mindex=uqtkarray.uqtk2numpy(mi_uqtk)
            if verbose>0:
                print("==== BCS with multiindex of size %d ====" % (mindex.shape[0],))
                if verbose>1:
                    print(mindex)

            # One run of BCS to obtain an array of coefficients and a new multiindex
            c_k, used_mi_np, sigma2 = UQTkEvalBCS(pc_model, y_split, x_split, sigma2, eta_opt, regparams, verbose)

            # Custom 'cuts' by number of PC terms or by value of PC coefficients
            npcall = c_k.shape[0] # number of PC terms
            if pcf_thr==None:
                pcf_thr=0.0
            indhigh = np.arange(npcall)[np.abs(c_k) > pcf_thr] # indices of coefficients above the pcf_thr threshold
            if verbose>0:
                if indhigh.shape[0]<npcall:
                    print(npcall-indhigh.shape[0],"coefficients equal to zero or below the magnitude threshold have been cut.")
            indsort_ = np.abs(c_k[indhigh]).argsort()[::-1] # indices of largest to smallest coefficients
            if npccut==None:
                npccut=100000
            indsort = indsort_[:min(npccut, indhigh.shape[0])] # trim lowest coefficients if there above npccut threshold
            if verbose>0:
                if indsort.shape[0]<indhigh.shape[0]:
                    print(indhigh.shape[0]-indsort.shape[0],"coefficients have been cut because only", npccut," terms are allowed.")
            mindex = used_mi_np[indhigh][indsort] # indices of the selected coefficients
            cfs = c_k[indhigh][indsort] # selected coefficients
            npc = cfs.shape[0] # number of coefficients
            # Multiindex growth with optional update of weights
            if j < niter - 1:

                if mindex_growth=='nonconservative': # nonconservative growth
                    mindex_new, mindex_add, mindex_f = uqtkmi.mi_addfront(mindex)
                    mindex = mindex_new.copy()

                if mindex_growth=='conservative': # conservative growth
                    mindex_new, mindex_add, mindex_f = uqtkmi.mi_addfront_cons(mindex)
                    mindex = mindex_new.copy()

                # update weights
                update_weights=True
                if update_weights:
                    eps = 1.e-3
                    npc_new = mindex.shape[0]
                    regparams_new = np.ones(npc_new) / eps
                    regparams_new[0:npc] = 1. / (abs(cfs) + eps)  # regparams
                    regparams = regparams_new.copy()

            # multiindex from a numpy array to a uqtk array
            mindex_uq=uqtkarray.intArray2D(mindex.shape[0], mindex.shape[1])
            for i2 in range(mindex.shape[0]):
                for j2 in range(mindex.shape[1]):
                    mindex_uq.assign(i2,j2, mindex[i2][j2])

            # create a pc object with the new multiindex
            pc_model=uqtkpce.PCSet("NISPnoq", mindex_uq, pc_model.GetPCType(),\
                    pc_model.GetAlpha(), pc_model.GetBeta())

        # Save for this trial
        mi_selected.append(mindex)

    # Intersect across trials
    mindex_final = reduce(multidim_intersect, mi_selected)
    # If no intersection, add the constant term [not sure why]
    if mindex_final.shape[0] == 0:
        print("No intersection found between the splits. Adding back the constant term.")
        mindex_final = np.zeros((1, xdata.shape[1]), dtype=int)

    # create a pc object with the final multiindex
    mindex_final_uq=uqtkarray.intArray2D(mindex_final.shape[0], mindex_final.shape[1])
    for i2 in range(mindex_final.shape[0]):
        for j2 in range(mindex_final.shape[1]):
            mindex_final_uq.assign(i2,j2, mindex_final[i2][j2])
    pc_model_final=uqtkpce.PCSet("NISPnoq", mindex_final_uq, pc_model.GetPCType(),\
            pc_model.GetAlpha(), pc_model.GetBeta())

    # Determine coefficients corresponding to final multiindex with regression
    cfs_final = UQTkRegression(pc_model_final, ydata, xdata)

    if verbose>0:
        if verbose>1:
            print("Final Multiindex:")
            print(mindex_final)
        print("Coefficients:")
        print(cfs_final)
        print(len(cfs_final), " terms retained out of a full basis of size", full_basis_size)
        print("Reestimated sigma2: %.3e"%sigma2)

    if return_sigma2:
        return pc_model_final, cfs_final, sigma2
    else:
        print("\nPlease note that sigma2 will be returned by default in future versions.")
        print("To remain compatible, set input argument return_sigma2 to True and expect")
        print("three return arguments: pc_model, coefficients, updated noise variance\n")
        return pc_model_final, cfs_final
################################################################################
def UQTkOptimizeEta(pc_start, y, x, etas, niter, nfolds, mindex_growth, verbose, plot=False):
    """
    Choose the opimum eta for Bayesian compressive sensing with nonconservative
        basis growth, splitting for basis crossvalidation. Calculates the RMSE
        for each eta for a specified number of folds. Selects the eta with the lowest
        RMSE after averaging the RMSEs over the folds.
    Helper function for UQTkBCS

    Input:
        pc_start :     PC object with information about the starting basis
        y:             1D numpy array (vector) with function, evaluated at the
                            sample points [#samples,]
        x:             N-dimensional NumPy array with sample points [#samples,
                            #dimensions]
        etas:          NumPy array or list with the threshold for stopping the
                            algorithm. Smaller values retain more nonzero
                            coefficients
        niter:         Number of iterations for basis growth
        nfolds:        Number of folds to use for eta cross-validation
        mindex_growth: Type of multiindex growth to use
        verbose:       Flag for print statements
        plot:          Flag for whether to generate a plot for eta optimization

    Output:
        eta_opt:      Optimum eta

    """
    # split data in k folds
    k=kfoldCV(x, y, nfolds)

    RMSE_list_per_fold=[] # list to whole eta RMSEs, organized by fold
    RMSE_list_per_fold_tr=[]

    if mindex_growth == None:
        full_basis_size = pc_start.GetNumberPCTerms()
    else:
        full_basis_size = uqtkpce.PCSet("NISPnoq", pc_start.GetOrder() + niter -1, pc_start.GetNDim(), pc_start.GetPCType(), pc_start.GetAlpha(), pc_start.GetBeta()).GetNumberPCTerms()

    # loop through each fold
    for i in range(nfolds):
        # retrieve training and validation data
        x_tr=k[i]['xtrain']
        y_tr=k[i]['ytrain']
        x_val=k[i]['xval']
        y_val=k[i]['yval']
        RMSE_per_eta=[] # array of RMS errors, one per eta
        RMSE_per_eta_tr=[]

        # loop through each eta
        for eta in etas:

            # Obtain coefficients through BCS
            pc_final, c_k, _ = UQTkBCS(pc_start, x_tr, y_tr, eta, niter, mindex_growth, ntry=1, return_sigma2=True)

            if verbose > 1:
                print("Fold ", i+1, ", eta ", eta, ", ", len(c_k), " terms retained out of a full basis of size", full_basis_size)


            # Evaluate the PCE at the validation points
            pce_evals = UQTkEvaluatePCE(pc_final, c_k, x_val) #testing error
            pce_evals_tr = UQTkEvaluatePCE(pc_final, c_k, x_tr) #training error

            # Calculate error metric: testing
            MSE = np.square(np.subtract(y_val, pce_evals)).mean()
            RMSE = math.sqrt(MSE)
            RMSE_per_eta.append(RMSE)

            # Calculate error metric: training
            MSE_tr = np.square(np.subtract(y_tr, pce_evals_tr)).mean()
            RMSE_tr = math.sqrt(MSE_tr)
            RMSE_per_eta_tr.append(RMSE_tr)

        RMSE_list_per_fold.append(RMSE_per_eta)
        RMSE_list_per_fold_tr.append(RMSE_per_eta_tr)

    # Compute the average and standard deviation of the RMSEs over the folds for testing error
    avg = np.array(RMSE_list_per_fold).mean(axis=0)
    avg_tr = np.array(RMSE_list_per_fold_tr).mean(axis=0)

    std = np.std(np.array(RMSE_list_per_fold), axis=0)
    std_tr = np.std(np.array(RMSE_list_per_fold_tr), axis=0)

    # standard deviation of the mean
    std_m = std/math.sqrt(nfolds)
    std_m_tr = std/math.sqrt(nfolds)

    # Choose eta with lowest RMSE
    eta_opt = etas[np.argmin(avg)]

    # Plot RMSE vs. eta for training and testing RMSE
    if plot:
        fig, ax = plt.subplots(figsize=(10,10))

        plt.errorbar(etas, avg, xerr=None, yerr=std, linewidth=2, markersize=8, capsize=8, label=('Testing'))
        plt.errorbar(etas, avg_tr, xerr=None, yerr=std_tr, linewidth=2, markersize=8, capsize=8, label=('Training'))

        plt.plot(eta_opt, np.min(avg), marker="o", markersize=15, color='black', label=("Optimum"))

        plt.xlabel("Eta",fontsize=20)
        plt.ylabel('RMSE',fontsize=20)

        #Change size of tick labels
        plt.tick_params(axis='both', labelsize=16)

        plt.xscale('log')
        plt.yscale('log')

        # Create legend
        plt.legend(loc='upper left')

        #Save
        plt.savefig('eta_opt.pdf', format='pdf', dpi=1200)

    return eta_opt
################################################################################
def UQTkEvalBCS(pc_model, f_evaluations, samplepts, sigma2, eta, regparams, verbose):
    """
    Perform one iteration of Bayesian compressive sensing
    Helper function for UQTkBCS

    Input:
        pc_model:  PC object with information about the basis
        f_evaluations: 1D NumPy array of function evaluations [#samples,]
        sam_uqtk:  N-dimensional NumPy array of samples [#samples, #dimensions]
        sigma2:     Inital noise variance we assume is in the data
        eta:       Threshold for stopping the algorithm. Smaller values
                        retain more nonzero coefficients.
        regparams: Regularization weights
                        To set a fixed scalar, provide a fixed nonnegative value.
                        To autopopulate a scalar, set regparams = 0.
                        To set a fixed vector of weights, provide an array [#PC terms,].
                        To autopopulate a vector, set regparams = [], which is the suggested method.

        verbose:   Flag for optional print statements

    Output:
        c_k:                1D NumPy array of nonzero coefficients
        used_mi_np:         NumPy array with the multiindex containing only terms
                                selected by BCS
        sigma2_reestimated: Noise variance reestimated by BCS returned if return_sigma2 = True
    """
    # Configure BCS parameters to defaults
    adaptive = 0 # Flag for adaptive CS, using a generative basis, set to 0 or 1
    optimal = 1  # Flag for optimal implementation of adaptive CS, set to 0 or 1
    scale = 0.1  # Diagonal loading parameter; relevant only in adaptive,
                    # non-optimal implementation

    bcs_verbose = 0 # silence print statements

    #UQTk array for samples - [#samples, #dimensions]
    sam_uqtk=uqtkarray.numpy2uqtk(np.asfortranarray(samplepts))
    # UQTk array for function f_evaluations - [#evaluations,]
    y = uqtkarray.numpy2uqtk(np.asfortranarray(f_evaluations))

    # UQTk array for lambda_init
    lambda_init = regparams    # Initial regularization weights, which will be updated through BCS.
    lam_uqtk=uqtkarray.dblArray1D(lambda_init.shape[0])
    for i2 in range(lambda_init.shape[0]):
        lam_uqtk.assign(i2, lambda_init[i2])

    # uqtkarray for sigma2
    sigma2_array=uqtkarray.dblArray1D(1,sigma2)

    #UQTk array for the basis terms evaluated at the sample points
    psi_uqtk = uqtkarray.dblArray2D()
    pc_model.EvalBasisAtCustPts(sam_uqtk, psi_uqtk)

    # UQTk arrays for outputs
    weights = uqtkarray.dblArray1D()  # sparse weights
    used = uqtkarray.intArray1D()     # position of the sparse weights;
                                          #indices of selected basis terms
    errbars = uqtkarray.dblArray1D()  # 1 standard dev around sparse weights
    basis = uqtkarray.dblArray1D()    # if adaptive==1, basis = next projection
                                          #vector
    alpha = uqtkarray.dblArray1D()    # inverse variance of the coefficient priors,
                                      # updated through the algorithm
    Sig = uqtkarray.dblArray2D()      # covariance matrix of the weights

    # Run BCS through the c++ implementation
    bcs.WBCS(psi_uqtk, y, sigma2_array, eta, lam_uqtk, adaptive, optimal, scale,\
      bcs_verbose, weights, used, errbars, basis, alpha, Sig)

    # Print result of the BCS iteration
    if (verbose):
        print("BCS has selected", used.XSize(), "basis terms out of",\
            pc_model.GetNumberPCTerms())

    # Nonzero coefficients in a numpy array
    c_k = np.zeros(used.XSize())
    for i in range(used.XSize()):
        c_k[i]=weights[i]

    # Obtain new multiindex with only terms selected by BCS
    mi_uqtk = uqtkarray.intArray2D(pc_model.GetNumberPCTerms(), sam_uqtk.YSize())
    pc_model.GetMultiIndex(mi_uqtk)
    used_mi_uqtk=uqtkarray.intArray2D()
    uqtkarray.subMatrix_row_int(mi_uqtk, used, used_mi_uqtk)
    used_mi_np=uqtkarray.uqtk2numpy(used_mi_uqtk)

    # convert the returned noise variance to a scalar
    sigma2_reestimated=sigma2_array[0]

    # Return coefficients and their locations with respect to the basis terms
    return c_k, used_mi_np, sigma2_reestimated
################################################################################
def UQTkCallBCSDirect(vdm_np, rhs_np, sigma2, eta=1.e-8, regparams_np=None, verbose=False, return_sigma2=False):
    """
    Calls the C++ BCS routines directly with a VanderMonde Matrix and Right Hand
    Side (Rather than relying on a PCE Model to provide the basis) to solve
    system vdm_np * c_k = rhs_np and return the sparse vector c_k
    Input:
        vdm_np:    VanderMonde Matrix, evaluated at sample points;
                        numpy array [n_samples, n_basis_terms]
        rhs_np:    right hand side for regression; 1D numpy array [n_samples,]
        sigma2:    Inital noise variance we assume is in the data
        eta:       Threshold for stopping the algorithm. The algorithm stops
                        if the change in the marginal likelhood over the last iteration
                        is smaller than eta times the overall change in marginal likelihood so far.
                        Note: Smaller values of eta tend to
                        retain more nonzero coefficients; float [default 1.e-8]
        regparams_np: Regularization weights; float or 1D numpy array
                        To set a fixed scalar, provide a fixed nonnegative value.
                        To autopopulate a scalar, set regparams_np = 0.
                        To set a fixed vector of weights, provide an array [n_basis_terms,].
                        To autopopulate a vector, set regparams_np = None, which is the suggested method.

        verbose:   Flag for optional print statements (defaults to False)

    Output:
        c_k:    1D numpy array with regression coefficients. The only non-zero
                        terms correspond to the retained basis terms
                        [n_basis_terms,]
        sigma2: Reestimated noise variance returned if return_sigma2 = True
    """
    # Set dimensions
    n_samples = vdm_np.shape[0]
    n_basis_terms = vdm_np.shape[1]

    # Configure BCS parameters to defaults
    adaptive = 0 # Flag for adaptive CS, using a generative basis, set to 0 or 1
    optimal = 1  # Flag for optimal implementation of adaptive CS, set to 0 or 1
    scale = 0.1  # Diagonal loading parameter; relevant only in adaptive,
                 # non-optimal implementation

    bcs_verbose = 0 # silence print statements

    # Convert numpy arrays to UQTk arrays

    # UQTk array for vdm matrix - [#samples, #dimensions]
    psi_uqtk = uqtkarray.numpy2uqtk(np.asfortranarray(vdm_np))
    # UQTk array for RHS [#samples,]
    rhs_uqtk = uqtkarray.numpy2uqtk(np.asfortranarray(rhs_np))

    # UQTk array for regparams, the initial regularization weights, which will be updated through BCS.
    # First properly set up numpy array.
    if regparams_np is None:
        regparams_np = np.array([])
    elif type(regparams_np)==int or type(regparams_np)==float:
        regparams_np = regparams_np*np.ones((n_basis_terms,))

    # Convert to UQTk array
    lam_uqtk=uqtkarray.dblArray1D(regparams_np.shape[0])
    for i2 in range(regparams_np.shape[0]):
        lam_uqtk.assign(i2, regparams_np[i2])

    sigma2_array = uqtkarray.dblArray1D(1,sigma2)


    # UQTk arrays for outputs
    weights = uqtkarray.dblArray1D()  # sparse weights
    used = uqtkarray.intArray1D()     # position of the sparse weights;
                                          #indices of selected basis terms
    errbars = uqtkarray.dblArray1D()  # 1 standard dev around sparse weights
    basis = uqtkarray.dblArray1D()    # if adaptive==1, basis = next projection
                                          #vector
    alpha = uqtkarray.dblArray1D()    # inverse variance of the coefficient priors,
                                      # updated through the algorithm
    Sig = uqtkarray.dblArray2D()      # re-estimated noise variance

    # Run BCS through the c++ implementation
    bcs.WBCS(psi_uqtk, rhs_uqtk, sigma2_array, eta, lam_uqtk, adaptive, optimal, scale,\
      bcs_verbose, weights, used, errbars, basis, alpha, Sig)

    # reestimated sigma2 as a scalar
    sigma2 = sigma2_array[0]

    # Print result of the BCS iteration
    if (verbose):
        print("BCS has selected", used.XSize(), "basis terms out of %d basis terms"%(n_basis_terms))

    # Coefficients in a numpy array
    c_k=np.zeros(n_basis_terms)
    for i in range(used.XSize()):
        c_k[used[i]]=weights[i]

    if return_sigma2:
        return c_k, sigma2
    else:
        print("Please note that sigma2 will be returned by default in future versions.")
        return c_k
################################################################################
def multidim_intersect(arr1, arr2):
    """
    Finds the intersection of two arrays

    Input:
        arr1: First NumPy array
        arr2: Second NumPy array

    Output: Intersection of the two arrays
    """
    arr1_view = arr1.view([('', arr1.dtype)] * arr1.shape[1])
    arr2_view = arr2.view([('', arr2.dtype)] * arr2.shape[1])
    intersected = np.intersect1d(arr1_view, arr2_view)
    return intersected.view(arr1.dtype).reshape(-1, arr1.shape[1])

################################################################################
def ind_split(ns, split_method, split_params):
    """
    Split indices in a few ways for validation=

    Input:
        ns:             Number of samples
        split_method:   Method for splitting; options are Kfold_small, Kfold, rand_fold,
                             and trval
        split_params:   A list of the form [# training samples, # validation samples]

    Output:
        list_ind:       A list of the form [indices training samples, indices of validation samples]
    """

    if (split_method == 'Kfold_small'):
        KK = split_params[0]
        # ind=np.ones((ns))
        indp = np.random.permutation(ns)
        list_ind = np.array_split(indp, KK)

    elif (split_method == 'Kfold'):
        KK = split_params[0]

        indp = np.random.permutation(ns)
        full_ind = range(ns)
        fold_ind = np.array_split(indp, KK)
        list_ind = []
        for cur_ind in fold_ind:
            list_ind.append(np.array(list(set(full_ind) - set(cur_ind))))

    elif (split_method == 'rand_fold'):
        KK = split_params[0]

        npt = split_params[1]

        list_ind = []
        for i in range(KK):
            list_ind.append(np.random.permutation(ns)[0:npt])

    elif (split_method == 'trval'):
        assert(ns == np.sum(split_params))
        KK = len(split_params)
        perms = np.random.permutation(ns)
        list_ind = []
        begin = 0
        for i in range(KK):
            list_ind.append(perms[begin:begin + split_params[i]])
            begin += split_params[i]

    return list_ind
################################################################################
def UQTkGetQuadPoints(pc_model):
    """
    Generates quadrature points through UQTk and returns them in numpy array
    Input:
        pc_model: PC object with info about PCE
    Output:
        qdpts: numpy array of quadrature points [totquat, n_dim]
        totquat: total number of quadrature points
    """

    # Info about PCE
    n_dim = pc_model.GetNDim()

    # Get the quadrature points
    qdpts_uqtk = uqtkarray.dblArray2D()
    pc_model.GetQuadPoints(qdpts_uqtk)
    totquat = pc_model.GetNQuadPoints() # Total number of quadrature points

    # Convert quad points to a numpy array
    qdpts = np.zeros((totquat,n_dim))
    #qdpts_uqtk.getnpdblArray(qdpts)
    qdpts = uqtkarray.uqtk2numpy(qdpts_uqtk)
    return qdpts, totquat
################################################################################
def UQTkStDv(pc_model,pc_coeffs):
    """
    Compute Standard Deviation of a PCE through UQTk
    Input:
        pc_model: PC object with info about PCE
        pc_coeffs: 1D numpy array with PCE coefficients
    Output:
        pc_stdv: Standard Deviation of the PCE
    """

    # Info about PCE
    n_pce = pc_model.GetNumberPCTerms()

    # Create and fill UQTk array for PC coefficients
    c_k_1d_uqtk = uqtkarray.dblArray1D(n_pce,0.0)
    for ip in range(n_pce):
        c_k_1d_uqtk[ip] = pc_coeffs[ip]

    pc_stdv = pc_model.StDv(c_k_1d_uqtk)

    return pc_stdv
################################################################################
def UQTkGSA(pc_model, pc_coeffs):
    """
    Computes Sobol' sensivity indices

    ToDo: refer to documentation in the UQTk manual

    Input:
        pc_model: PC object with information about the basis
        pc_coeffs: NumPy array of PC coefficients [#PCTerms,]
    Output:
        mainsens:  1D NumPy array of the main sensitivities for each dimension [#dim,]
        totsens:   1D NumPy array of the total sensivities for each dimension [#dim,]
        jointsens: 2D NumPy array of joint sensitivities for each pair of dimensions [#dim, #dim]
    """
    # coefficients in a uqtk array
    coef_uqtk = uqtkarray.numpy2uqtk(pc_coeffs)

    # Compute main sensitivities
    mainsens_uqtk=uqtkarray.dblArray1D()
    pc_model.ComputeMainSens(coef_uqtk,mainsens_uqtk)
    mainsens = uqtkarray.uqtk2numpy(mainsens_uqtk)

    # Compute total sensitivities
    totsens_uqtk=uqtkarray.dblArray1D()
    pc_model.ComputeTotSens(coef_uqtk,totsens_uqtk)
    totsens = uqtkarray.uqtk2numpy(totsens_uqtk)

    # Compute joint sensitivities
    jointsens_uqtk = uqtkarray.dblArray2D()
    pc_model.ComputeJointSens(coef_uqtk,jointsens_uqtk)
    for id in range(pc_model.GetNDim()):
        jointsens_uqtk.assign(id, id, mainsens_uqtk[id])
    jointsens = uqtkarray.uqtk2numpy(jointsens_uqtk)

    return mainsens, totsens, jointsens
################################################################################
def UQTkKDE(fcn_evals):
    """
    Performs kernel density estimation
    Input:
        fcn_evals: numpy array of evaluations of the forward model [n_samples,]
    Output:
        xpts_pce: numpy array of points at which the PDF is estimated.
        PDF_data_pce: numpy array of estimated PDF values.
    """
    # Perform KDE on fcn_evals
    kern_pce=stats.kde.gaussian_kde(fcn_evals)
    # Generate points at which to evaluate the PDF
    xpts=np.linspace(fcn_evals.min(),fcn_evals.max(),200)
    # Evaluate the estimated PDF at these points
    PDF_data=kern_pce(xpts)
    return xpts, PDF_data
################################################################################
def UQTkGetMultiIndex(pc_model,ndim):
    """
    Function that returns a 2D array of the PC multiindex.
    Input:
        pc_model, ndim.
    Output:
        2D array of the PC multiindex
    """
    # Get number of PC terms
    totpc = pc_model.GetNumberPCTerms()
    # Create  2D int UQTk array with width of ndim and height of totpc
    mi_uqtk = uqtkarray.intArray2D(totpc,ndim)
    # Populate UQTk array with PC multiindex
    pc_model.GetMultiIndex(mi_uqtk)
    # Convert UQTk array to numpy array
    mi = np.zeros((totpc,ndim))
    mi = uqtkarray.uqtk2numpy(mi_uqtk)
    #mi_uqtk.getnpdblArray(mi)
    return mi
################################################################################
def UQTkPlotMiDims(pc_model,c_k,ndim, nord, type):
    """
    Function that creates a plot of the behavior of the absolute value of the
    PC coefficient for each order.
    Input:
        pc_model, ndim(number of parameters), and c_k(array of pc coefficients).
        Order of the PC
        string indicating the type of plot for labeling purposes
    Output:
        Matplotlib plot.
    """
    # Get array of PC multiindicies
    mi = UQTkGetMultiIndex(pc_model,ndim)

    # Get the order of the PC coefficient by taking the sum of the multiindex row
    # that corresponds to that value
    misum = np.sum(mi, axis=1)

    #find values that separate the orders
    sep=[]
    for i in range(misum.shape[0]):
        if misum[i]!=misum[i-1]:
            sep.append(i)

    # Create an numpy array of the log of the absolute value of the PC coefficients
    cklen = len(c_k)
    ac_k = np.absolute(c_k)
    ac_k = np.log10(ac_k)

    # Create an array to represent the PC coefficient number
    x = np.arange(1,cklen+1)

    # Set the plot size
    plt.figure(figsize=(16,10))
    # Set Plot min, max
    xmin = np.amin(x)
    xmax = np.amax(x)
    ymin = np.amin(ac_k)
    ymax = np.amax(ac_k)
    plt.ylim(ymin,ymax)
    plt.xlim(xmin-2,xmax)

    # Create axis and title labels
    plt.xlabel("Coefficient Number", size=25)
    plt.ylabel("PC Coefficient Magnitude", size=25)
    sup="Spectral Decay of the PC Coefficients for "+type+" Quadrature"
    plt.suptitle(sup, size=25)

    # Get the correct number of y-labels
    y=[]
    val=0
    while (val>ymin-2):
        y.insert(0, val)
        val=val-2
    labels=[]
    for val in y:
        new=r'$10^{'+str(val)+'}$'
        labels.append(new)

    plt.yticks(y,labels,size=20)
    plt.xticks(size=20)


    # Create verticle lines seperating orders
    for i in range(nord+1):
        if (i==1):
            label=r'$'+str(i)+'^{st}$'
        elif (i==2):
            label=r'$'+str(i)+'^{nd}$'
        elif (i==3):
            label=r'$'+str(i)+'^{rd}$'
        else:
            label=r'$'+str(i)+'^{th}$'

        if i>0:
            dotted_line=plt.Line2D((sep[i],sep[i]), (y[0],ymax), lw=1, c='r')
            plt.gca().add_line(dotted_line)

        if (sep[i]==sep[-1]):
            plt.annotate(label, xy=(sep[i],ac_k[2]),xytext=((sep[i]+cklen)/2,ac_k[2]),size = 16)
        else:
            plt.annotate(label, xy=(sep[i],ac_k[2]),xytext=((sep[i+1]+sep[i])/2,ac_k[2]),size = 16)

    # Plot figure
    plt.plot(x,ac_k,linewidth=2,color='b',)
    # Set plot name, and save as PDF
    #fig_name="Multi_Index_Dim_"+type+".pdf"
    #plt.savefig(fig_name)
    #print("\n"+fig_name+" has been saved.")
    plt.show()

################################################################################
def kfold_split(nsamples,nfolds,seed=13):
    '''
    return dictionary of training and testing pairs using k-fold cross-validation
    '''
    # returns split data where each data is one fold left out
    KK=nfolds
    rn = np.random.RandomState(seed)

    indp=rn.permutation(nsamples)
    split_index=np.array_split(indp,KK)


    cvindices = {}
    # create testing and training folds
    for j in range(KK):
        fold = j
        newindex = [split_index[i] for i in range(len(split_index)) if i != (fold)]
        train_ind = np.array([],dtype='int64')
        for i in range(len(newindex)): train_ind = np.concatenate((train_ind,newindex[i]))
        test_ind = split_index[fold]
        cvindices[j] = {'train index': train_ind, 'val index': test_ind}

    return cvindices
################################################################################
def kfoldCV(x,y,nfolds=3,seed=13):
    '''
     Splits data into training/testing pairs for kfold cross-val
    x is a data matrix of size n x d1, d1 is dim of input
    y is a data matrix of size n x d2, d2 is dim of output

    Test:
    xtest = array([i*ones(6) for i in range(1,501)])
    xtest = np.array([i*np.ones(6) for i in range(1,501)])
    ytest = xtest[:,:2]
    K,ci = kfoldCV(xtest,ytest)

    for k in K.keys():
        a = K[k]['xtrain'][:,0]
        b = K[k]['xval'][:,0]
        test = sum(np.in1d(a,b)) + sum(np.in1d(b,a))
        print test
     '''
    if len(x.shape)>1:
        n,d1 = x.shape
    else:
        n=x.shape
    ynew = np.atleast_2d(y)
    if len(ynew) == 1: ynew = ynew.T # change to shape (n,1)
    _,d2 = ynew.shape
    cv_idx = kfold_split(n,nfolds,seed)

    kfold_data = {}
    for k in cv_idx.keys():
        kfold_data[k] = {
        'xtrain': x[cv_idx[k]['train index']],
        'xval': x[cv_idx[k]['val index']],
        'ytrain': np.squeeze(ynew[cv_idx[k]['train index']]),
        'yval': np.squeeze(ynew[cv_idx[k]['val index']])
        } # use squeeze to return 1d array

        # set train and test to the same if 1 fold
        if nfolds == 1:
            kfold_data[k]['xtrain'] = kfold_data[k]['xval']
            kfold_data[k]['ytrain'] = kfold_data[k]['yval']

    return kfold_data
