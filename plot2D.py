# -*- coding: utf-8 -*-
"""
Created on 15/04/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file manages the initiation and update of 2D plots
"""

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.mlab as ml
from matplotlib.pyplot import clabel
import matplotlib.colors as mplc
import cv2
import scipy
from scipy.interpolate import griddata
import masks
import filterWidget


##############################
## DISPLACEMENT / DEVIATION ##
##############################

def plot2D_displacementDeviation(self, plotAx, data_x, data_y, disp_x, disp_y, value, grid_instances, activeInstances):

    plotAx.cla() #clear the figure
    plotAx.patch.set_facecolor('none') #remove figure background

    plotAx.red = []
    for instance in activeInstances:
        instanceMarkers = grid_instances[instance]
        plotAx.red.append(plotAx.plot(data_x[instanceMarkers,0], data_y[instanceMarkers,0], '+', ms=3)[0])

def update2D_displacementDeviation(plotAx, xAxis, yAxis, image): #data = red_x, red_y, blue_x, blue_y, value, parentWidget


    nbInstances = len(np.atleast_1d(xAxis))
    if image is not None:
        plotAx.image = plotAx.imshow(image[::10,::10], cmap='gray', extent=[0, image.shape[1], image.shape[0],0]) # plot the image in low quality (reduce plotting time)
    for instance in range(nbInstances):
        plotAx.red[instance].set_data(xAxis[instance], yAxis[instance])


#################
## CORRELATION ##
#################

def plot2D_correlation(self, plotFig, plotAx, data_x, data_y, corr):

    plotAx.cla() #clear the figure
    plotAx.patch.set_facecolor('none') #remove figure background

    try:
        plotFig.delaxes(plotFig.axes[1])
    except:
        pass

    #plotAx.mappable = plotAx.contourf(data_x, data_y, corr, np.linspace(0, 1, 9), cmap = 'Spectral', extend='min', spacing='proportional')
    plotAx.mappable = plotAx.imshow(corr, cmap = 'RdBu')
    plotAx.mappable.axes.xaxis.set_ticklabels([])
    plotAx.mappable.axes.yaxis.set_ticklabels([])
    plotAx.invert_yaxis()

    #colorbar display
    divider = make_axes_locatable(plotAx)
    plotAx.cax = divider.append_axes('right', size='5%', pad='1%')
    plotAx.cbar = plotFig.colorbar(plotAx.mappable, cax=plotAx.cax, extend='min')
    plotAx.cbar.ax.tick_params(labelsize=7)
    labels = np.linspace(0, 1, 11)
    ticks = np.linspace(-0.1, 0.1, 11)
    plotAx.cbar.set_ticks(ticks)
    plotAx.cbar.set_ticklabels(labels)


def update2D_correlation(self, plotFig, plotAx, data): #data = dataCorr2D


    nbInstances = len(np.atleast_1d(data))
    try:
        for instance in range(nbInstances):
            plotAx.mappable[instance].remove()
    except:
        pass

    vmin, vmax = plotAx.cbar.get_clim()
    plotAx.mappable = []

    for instance in range(nbInstances):
        if data[instance][0,0] != 99999:
            plotAx.mappable.append(plotAx.imshow(data[instance], cmap = 'RdBu', vmin=vmin, vmax=vmax))


##########################
## LOCAL STRAIN 1D / 2D ##
##########################

def plot2D_strain(self, plotAx, data_x, data_y, disp_strain, grid_instances, activeInstances, activeMarkers, plotFig=None, refImg=0):

    plotAx.cla() #clear the figure
    plotAx.patch.set_facecolor('none') #remove figure background

    if plotFig is not None: #2D Strain

        try:
            plotFig.delaxes(plotFig.axes[1])
        except:
            pass

        plotAx.mappable = plotAx.imshow(disp_strain, cmap = 'jet') #old_cmap : RdBu
        plotAx.mappable.axes.xaxis.set_ticklabels([])
        plotAx.mappable.axes.yaxis.set_ticklabels([])

        divider = make_axes_locatable(plotAx)
        plotAx.cax = divider.append_axes('right', size='5%', pad='1%')
        plotAx.cbar = plotFig.colorbar(plotAx.mappable, cax=plotAx.cax, extend='both')
        plotAx.cbar.ax.tick_params(labelsize=7)
        plotAx.set_aspect('auto')

    else: #1D Strain

        nbInstances = len(np.atleast_1d(activeInstances))
        lowLimitData = np.max(data_x)
        highLimitData = np.min(data_x)
        lowLimitDisp = np.max(disp_strain)
        highLimitDisp = np.min(disp_strain)
        plotAx.strainPlot = []
        plotAx.strainFit = []
        for instance in range(nbInstances):
            instanceMarkers = np.intersect1d(grid_instances[activeInstances[instance]],activeMarkers[refImg], assume_unique=True).astype(np.int)
            nbInstanceMarkers = len(np.atleast_1d(instanceMarkers))
            if  nbInstanceMarkers > 1:
                s, b = np.polyfit(data_x[instanceMarkers,refImg], disp_strain[instanceMarkers,refImg], 1)  #calculate the linear regression of the data
                plotAx.strainFit.append(plotAx.plot(data_x[instanceMarkers,refImg], s * data_x[instanceMarkers,refImg] + b,'--k')[0])
                plotAx.strainPlot.append(plotAx.plot(data_x[instanceMarkers,refImg], disp_strain[instanceMarkers,refImg], '.')[0])
            elif nbInstanceMarkers == 1:
                plotAx.strainFit.append(None)
                plotAx.strainPlot.append(plotAx.plot(data_x[instanceMarkers,refImg], disp_strain[instanceMarkers,refImg], '.')[0])
            else:
                continue
            lowLimitDisp = min(lowLimitDisp,np.min(disp_strain[instanceMarkers,:]))
            highLimitDisp = max(highLimitDisp,np.max(disp_strain[instanceMarkers,:]))
            lowLimitData = min(lowLimitData,np.min(data_x[instanceMarkers,:]))
            highLimitData = max(highLimitData, np.max(data_x[instanceMarkers,:]))
        plotAx.set_xlim([lowLimitData, highLimitData])
        plotAx.set_ylim([lowLimitDisp, highLimitDisp])


def update2D_strain(self, plotAx, xAxis, yAxis, data): #data = [slope, intersect] for 1D strain or data = plotFig for 2D strain

    nbInstances = len(np.atleast_1d(xAxis))
    if yAxis is None: #2D Strain

        try:
            for instance in range(nbInstances):
                plotAx.mappable[instance].remove()
        except:
            pass

        vmin, vmax = plotAx.cbar.get_clim()
        plotAx.mappable = []
        for instance in range(nbInstances):
            if xAxis[instance][0,0] != 99999:
                plotAx.mappable.append(plotAx.imshow(xAxis[instance], cmap = 'jet', vmin=vmin, vmax=vmax))
        plotAx.set_aspect('auto')

    else: #1D Strain

        for instance in range(nbInstances):
            if plotAx.strainFit[instance] is not None:
                plotAx.strainFit[instance].set_data(xAxis[instance], data[0][instance] * xAxis[instance] + data[1][instance])
            plotAx.strainPlot[instance].set_data(xAxis[instance], yAxis[instance])


def plot_TrueStrain(self, plotAx, data): #data = strainX/Y, averageImageNb, activeInstances

    plotAx.cla()
    nbImages = len(np.atleast_1d(data[0]))
    nbInstances = len(np.atleast_1d(data[0][0,:]))

    if data[1] < 1:
        data[1] = 1
    if data[1] > nbImages:
        data[1] = nbImages

    for instance in range(nbInstances):
        slope = []
        currentCumulatedStrain = 0
        nb = 0
        for image in range(nbImages):
            currentCumulatedStrain += data[0][image,instance]
            nb+=1
            if nb > data[1]-1 or image == nbImages-1:
                slope.append([image+1,data[0][image,instance]/nb])
                nb, currentCumulatedStrain = 0, 0
        slope = np.array(slope)
        lbl = 'Instance '+str(data[2][instance])
        plotAx.plot(slope[:,0], slope[:,1], '.-', label=lbl)
    if nbInstances > 1:
        plotAx.legend()
