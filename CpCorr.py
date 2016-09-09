#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on --/--/20--

@author: ---
Revised by Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file has been translated, adapted and further developed from 'Digital Image Correlation and Tracking' for Matlab exchanged by Melanie Senn on Mathworks
"""

import numpy as np
from scipy import interpolate
import cv2

def cpcorr(InputPoints,BasePoints,Input,Base, CORRSIZE):

    [xymoving_in,xyfixed_in,moving,fixed] = ParseInputs(InputPoints,BasePoints,Input,Base)
    CorrCoef=[]

    # get all rectangle coordinates
    rects_moving = np.array(calc_rects(xymoving_in,CORRSIZE,moving)).astype(np.int)
    rects_fixed = np.array(calc_rects(xyfixed_in,2*CORRSIZE,fixed)).astype(np.int)
    ncp = len(np.atleast_1d(xymoving_in))

    xymoving = xymoving_in    # initialize adjusted control points matrix
    CorrCoef=np.zeros((ncp,1))
    StdX=np.zeros((ncp,1))
    StdY=np.zeros((ncp,1))

    errorInfos = np.zeros((ncp,1))
    #### Error Type ####
    # 1 : Edge Area
    # 2 : Marker Out
    # 3 : Non finite number
    # 4 : No Std. Dev
    # 5 : SubPx outside limits
    # 6 : Div. by 0
    # 7 : Low Corr.
    # 8 : Peak badly constrained
    ####################

    for icp in range(ncp):

        if (rects_moving[2][icp] == 0 and rects_moving[3][icp] == 0) or (rects_fixed[2][icp] == 0 and rects_moving[3][icp] == 0):
            #near edge, unable to adjust
            #print 'CpCorr : Edge area. No Adjustement.'
            errorInfos[icp] = 1
            continue

        sub_moving = moving[rects_moving[1][icp]:rects_moving[1][icp]+rects_moving[3][icp],rects_moving[0][icp]:rects_moving[0][icp]+rects_moving[2][icp]]
        sub_fixed = fixed[rects_fixed[1][icp]:rects_fixed[1][icp]+rects_fixed[3][icp],rects_fixed[0][icp]:rects_fixed[0][icp]+rects_fixed[2][icp]]

        #make sure the image data exist
        if sub_moving.shape[0] == 0 or sub_moving.shape[1] == 0 or sub_fixed.shape[0] == 0 or sub_fixed.shape[1] == 0:
            #print 'CpCorr : Marker out of image.'
            errorInfos[icp] = 2
            continue

         #make sure finite
        if np.logical_or(np.any(np.isfinite(sub_moving[:])==False),np.any(np.isfinite(sub_fixed[:]))==False):
            # NaN or Inf, unable to adjust
            #print 'CpCorr : Wrong Number. No Adjustement.'
            errorInfos[icp] = 3
            continue


        # check that template rectangle moving has nonzero std
        if np.std(sub_moving[:])== 0:
            # zero standard deviation of template image, unable to adjust
            #print 'CpCorr : No Std Dev. No Adjustement.'
            errorInfos[icp] = 4
            continue


        norm_cross_corr = cv2.matchTemplate(sub_moving,sub_fixed,cv2.TM_CCORR_NORMED)
        #norm_cross_corr=scipy.signal.correlate2d(sub_fixed, sub_moving)
        #norm_cross_corr=sklearn.preprocessing.normalize(norm_cross_corr, norm='l2', axis=1, copy=True)
        #norm_cross_corr=match_template(sub_fixed,sub_moving)

        # get subpixel resolution from cross correlation
        subpixel = True
        [xpeak, ypeak, stdx, stdy, corrcoef, info] = findpeak(norm_cross_corr,subpixel)
        CorrCoef[icp]=corrcoef
        StdX[icp]=stdx
        StdY[icp]=stdy
        xpeak = float(xpeak)
        ypeak = float(ypeak)

        if info == 1:
            errorInfos[icp] = 5
        elif info == 2:
            errorInfos[icp] = 6


        # eliminate any poor correlations
        THRESHOLD = 0.5
        if (corrcoef < THRESHOLD):
            # low correlation, unable to adjust
            #print 'CpCorr : Low Correlation. Marker avoided.'
            errorInfos[icp] = 7
            continue

        # offset found by cross correlation
        corroffset = [xpeak-CORRSIZE, ypeak-CORRSIZE]

        # eliminate any big changes in control points
        if corroffset[0] > (CORRSIZE-1) or corroffset[1] > (CORRSIZE-1):
        # peak of norxcorr2 not well constrained, unable to adjust
            #print 'CpCorr : Peak not well constrained. No adjustement'
            errorInfos[icp] = 8
            continue

        movingfractionaloffset = np.array([xymoving[icp,:] - np.around(xymoving[icp,:])])
        fixedfractionaloffset = np.array([xyfixed_in[icp,:] - np.around(xyfixed_in[icp,:])])


        # adjust control point
        xymoving[icp,:] = xymoving[icp,:] - movingfractionaloffset - corroffset + fixedfractionaloffset
        #xymoving[icp,:] = xymoving[icp,:] - corroffset


    return xymoving,StdX,StdY,CorrCoef, errorInfos

def calc_rects(xy,halfwidth,img):

    # Calculate rectangles so imcrop will return image with xy coordinate inside center pixel
    default_width = 2*halfwidth
    default_height = default_width
    [row, col] = img.shape

    # xy specifies center of rectangle, need upper left
    upperleft=np.around(xy)-halfwidth
    lowerright=np.around(xy)+halfwidth


    # need to modify for pixels near edge of images
    left = upperleft[:,0]
    upper = upperleft[:,1]
    right = lowerright[:,0]
    lower = lowerright[:,1]

    #lower = upper + default_height
    #right = left + default_width
    width = default_width * np.ones(np.shape(upper))
    height = default_height * np.ones(np.shape(upper))

    #check edges for coordinates outside image
    [upper, height] = adjust_lo_edge(upper,1,height)
    [lower, height] = adjust_hi_edge(lower,row,height)
    [left,width] = adjust_lo_edge(left,1,width)
    [right, width] = adjust_hi_edge(right,col,width)

    # set width and height to zero when less than default size
    #iw = find(width<default_width)
    #ih = find(height<default_height)
    #idx = unique([iw,ih])
    #width[idx] = 0
    #height[idx] = 0

    rect = [left.astype(np.int), upper.astype(np.int), width.astype(np.int), height.astype(np.int)]

    return rect

def adjust_lo_edge(coordinates,edge,breadth):

    for indx in range(0,len(coordinates)):
        if coordinates[indx] < edge:
            #breadth[indx] = breadth[indx] - np.absolute(coordinates[indx]-edge)
            breadth[indx] = 0
            coordinates[indx] = edge
    return coordinates, breadth

def adjust_hi_edge(coordinates,edge,breadth):

    for indx in range(0,len(coordinates)):
        if coordinates[indx] > edge:
            #breadth[indx] = breadth[indx] - np.absolute(coordinates[indx]-edge)
            breadth[indx] = 0
            coordinates[indx] = edge
    return coordinates, breadth

def ParseInputs(InputPoints,BasePoints,Input,Base):

    xymoving_in = InputPoints
    xyfixed_in = BasePoints
    moving = Input
    fixed = Base
    return xymoving_in,xyfixed_in,moving,fixed

# sub pixel accuracy by 2D polynomial fit (quadratic)
def findpeak(f,subpixel):
    stdx=1e-4
    stdy=1e-4

    # Get absolute peak pixel

    max_f = np.amax(f)
    [xpeak,ypeak] = np.unravel_index(f.argmax(), f.shape) #coordinates of the maximum value in f

    if subpixel == False or xpeak==0 or xpeak==np.shape(f)[0]-1 or ypeak==0 or ypeak==np.shape(f)[1]-1: # on edge
        #print 'CpCorr : No Subpixel Adjustement.'
        return ypeak, xpeak, stdx, stdy, max_f, 0# return absolute peak

    else:
        # fit a 2nd order polynomial to 9 points
        # using 9 pixels centered on irow,jcol
        u = f[xpeak-1:xpeak+2,ypeak-1:ypeak+2]
        u = np.reshape(np.transpose(u),(9,1))
        x = np.array([-1,  0,  1, -1,  0,  1, -1,  0,  1])
        y = np.array([-1, -1, -1,  0,  0,  0,  1, 1,  1])
        x = np.reshape(x,(9,1))
        y = np.reshape(y,(9,1))

        # u(x,y) = A(0) + A(1)*x + A(2)*y + A(3)*x*y + A(4)*x^2 + A(5)*y^2
        X = np.hstack((np.ones((9,1)), x, y, x*y, x**2, y**2))
        # u = X*A

        #A = np.linalg.lstsq(X,u, rcond=1e-1)
        A = np.linalg.lstsq(X,u, rcond=1e-20)

        e = A[1] #residuals returned by Linalg Lstsq
        A=np.reshape(A[0],(6,1)) # A[0] array of least square solution to the u = AX equation


        # get absolute maximum, where du/dx = du/dy = 0
        x_num = (-A[2]*A[3]+2*A[5]*A[1])
        y_num = (-A[3]*A[1]+2*A[4]*A[2])

        den = (A[3]**2-4*A[4]*A[5])
        x_offset = x_num / den
        y_offset = y_num / den


        #print x_offset, y_offset
        if np.absolute(x_offset)>1 or np.absolute(y_offset)>1:
            #print 'CpCorr : Subpixel outside limit. No adjustement'
            # adjusted peak falls outside set of 9 points fit,
            return ypeak, xpeak, stdx, stdy, max_f, 1 # return absolute peak

        #x_offset = np.round(10000*x_offset)/10000
        #y_offset = np.round(10000*y_offset)/10000
        x_offset = np.around(x_offset, decimals=4)
        y_offset = np.around(y_offset, decimals=4)

        xpeak = xpeak + x_offset
        ypeak = ypeak + y_offset
        #print xpeak, ypeak

        # calculate residuals
        #e=u-np.dot(X,A)

        # calculate estimate of the noise variance
        n=9     # number of data points
        p=6     # number of fitted parameters
        var=np.sum(e**2)/(n-p)

        # calculate covariance matrix
        cov=np.linalg.inv(np.dot(np.transpose(X),X))*var
        # produce vector of std deviations on each term
        s=np.sqrt([cov[0,0],cov[1,1],cov[2,2],cov[3,3],cov[4,4],cov[5,5]])
        # Calculate standard deviation of denominator, and numerators
        if A[1] == 0 or A[2] == 0 or A[3] == 0 or A[4] == 0 or A[5] == 0: #avoid divide by zero error and invalid value
            #print 'CpCorr : Div. by 0 error escaped.'
            return ypeak, xpeak, stdx, stdy, max_f, 2# return absolute peak
        else:
            x_num_std=np.sqrt(4*A[5]**2*A[1]**2*((s[5]/A[5])**2+(s[1]/A[1])**2)+A[2]**2*A[3]**2*((s[2]/A[2])**2+(s[3]/A[3])**2))
            den_std=np.sqrt(16*A[4]**2*A[5]**2*((s[4]/A[4])**2+(s[5]/A[5])**2)+2*s[3]**2*A[3]**2)
            y_num_std=np.sqrt(4*A[4]**2*A[2]**2*((s[4]/A[4])**2+(s[2]/A[2])**2)+A[3]**2*A[1]**2*((s[3]/A[3])**2+(s[1]/A[1])**2))

        # Calculate standard deviation of x and y positions
        stdx=np.sqrt(x_offset**2*((x_num_std/x_num)**2+(den_std/den)**2))
        stdy=np.sqrt(y_offset**2*((den_std/den)**2+(y_num_std/y_num)**2))

        # Calculate extremum of fitted function
        max_f = np.dot([1, x_offset, y_offset, x_offset*y_offset, x_offset**2, y_offset**2],A)
        max_f = np.absolute(max_f)


    return ypeak, xpeak, stdx, stdy, max_f, 0

# sub pixel accuracy by upsampling and interpolation
def findpeak2(f,subpixel):
    stdx=1e-4
    stdy=1e-4

    kernelsize=3

    # get absolute peak pixel
    max_f = np.amax(f)
    [xpeak,ypeak] = np.unravel_index(f.argmax(), f.shape)

    if subpixel==False or xpeak < kernelsize or xpeak > np.shape(f)[0]-kernelsize or ypeak < kernelsize or ypeak > np.shape(f)[1]-kernelsize: # on edge
        return xpeak, ypeak, stdx, stdy, max_f # return absolute peak
    else:
        # determine sub pixel accuracy by upsampling and interpolation
        fextracted=f[xpeak-kernelsize:xpeak+kernelsize+1,ypeak-kernelsize:ypeak+kernelsize+1]
        totalsize=2*kernelsize+1
        upsampling=totalsize*10+1
        #step=2/upsampling
        x=np.linspace(-kernelsize,kernelsize,totalsize)
        #[X,Y]=np.meshgrid(x,x)
        xq=np.linspace(-kernelsize,kernelsize,upsampling)
        #[Xq,Yq]=np.meshgrid(xq,xq)

        bilinterp = interpolate.interp2d(x, x, fextracted, kind='cubic')
        fq = bilinterp(xq, xq)
        #splineint = RectBivariateSpline(x, x, fextracted, kx=3, ky=3, s=0)
        #fq=splineint(xq,xq)
        #fq=griddata((x, x), fextracted, (Xq, Yq), method='cubic')

        max_f = np.amax(fq)
        [xpeaknew,ypeaknew] = np.unravel_index(fq.argmax(), fq.shape)

        #xoffset=Xq[0,xpeaknew]
        #yoffset=Yq[ypeaknew,0]
        xoffset=xq[xpeaknew]
        yoffset=xq[ypeaknew]

        # return only one-thousandths of a pixel precision
        xoffset = np.round(1000*xoffset)/1000
        yoffset = np.round(1000*yoffset)/1000
        xpeak=xpeak+xoffset
        ypeak=ypeak+yoffset

        # peak width (full width at half maximum)
        scalehalfwidth=1.1774;
        fextractedx=np.mean(fextracted,0)
        fextractedy=np.mean(fextracted,1)
        stdx=scalehalfwidth*np.std(fextractedx)
        stdy=scalehalfwidth*np.std(fextractedy)

    return xpeak, ypeak, stdx, stdy, max_f

 # sub pixel accuracy by centroid
def findpeak3(f,subpixel):
    stdx=1e-4
    stdy=1e-4

    kernelsize=3

    # get absolute peak pixel
    max_f = np.amax(f)
    [xpeak,ypeak] = np.unravel_index(f.argmax(), f.shape)

    if subpixel==False or xpeak < kernelsize or xpeak > np.shape(f)[0]-kernelsize or ypeak < kernelsize or ypeak > np.shape(f)[1]-kernelsize: # on edge
        return xpeak, ypeak, stdx, stdy, max_f # return absolute peak
    else:
        # determine sub pixel accuracy by centroid
        fextracted=f[xpeak-kernelsize:xpeak+kernelsize+1,ypeak-kernelsize:ypeak+kernelsize+1]
        fextractedx=np.mean(fextracted,0)
        fextractedy=np.mean(fextracted,1)
        x=np.arange(-kernelsize,kernelsize+1,1)
        y=np.transpose(x)

        xoffset=np.dot(x,fextractedx)
        yoffset=np.dot(y,fextractedy)

        # return only one-thousandths of a pixel precision
        xoffset = np.round(1000*xoffset)/1000
        yoffset = np.round(1000*yoffset)/1000
        xpeak=xpeak+xoffset
        ypeak=ypeak+yoffset

        # 2D linear interpolation
        bilinterp = interpolate.interp2d(x, x, fextracted, kind='linear')
        max_f = bilinterp(xoffset,yoffset)

        # peak width (full width at half maximum)
        scalehalfwidth=1.1774
        stdx=scalehalfwidth*np.std(fextractedx)
        stdy=scalehalfwidth*np.std(fextractedy)

    return xpeak, ypeak, stdx, stdy, max_f
