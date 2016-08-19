# -*- coding: utf-8 -*-
"""
Created on 18/04/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file manages the initiation and update of 3D plots
"""

from matplotlib import cm
import numpy as np


def set_aspect_equal_3d(ax):
    """Fix equal aspect bug for 3D plots."""

    xlim = ax.get_xlim3d()
    ylim = ax.get_ylim3d()
    #zlim = ax.get_zlim3d()

    from numpy import mean
    xmean = mean(xlim)
    ymean = mean(ylim)

    plot_radius = max([abs(lim - mean_)
                       for lims, mean_ in ((xlim, xmean),
                                           (ylim, ymean))
                       for lim in lims])

    ax.set_xlim3d([xmean + plot_radius, xmean - plot_radius])
    ax.set_ylim3d([ymean - plot_radius, ymean + plot_radius])
    #ax.set_zlim3d([zmean - plot_radius, zmean + plot_radius])



def plot3D_init(plotAx, xLimit, yLimit, zData):
    
    plotAx.cla() #clear the figure
    plotAx.patch.set_facecolor('none') #remove figure background
    
    plotAx.view_init(15,50) #initiate the angle of the view
    plotAx.tick_params(labelsize=10)
    plotAx.locator_params(nbins=4)
    
    zLimit = [np.nanmin(zData), np.nanmax(zData)]
    
    plotAx.set_xlim(xLimit)
    plotAx.set_ylim(yLimit)
    plotAx.set_zlim(zLimit)
    set_aspect_equal_3d(plotAx)
    

def update3D_subplot(plotAx, xAxis, yAxis, zAxis, plotType, projection):
    
    nbInstances = len(np.atleast_1d(xAxis))
    try:
        for instance in range(nbInstances):
            plotAx.current[instance].remove()
    except:
        pass
    try:
        for instance in range(nbInstances):
            plotAx.projectionX[instance].remove()
    except:
        pass
    try:
        for instance in range(nbInstances):
            plotAx.projectionY[instance].remove()
    except:
        pass
    
    plotAx.current = []
    plotAx.projectionX = []
    plotAx.projectionY = []
    for instance in range(nbInstances):
        nbMarkers = len(np.atleast_1d(xAxis[instance]))
        if plotType == 0 and nbMarkers > 2:
            plotAx.current.append(plotAx.plot_trisurf(xAxis[instance], yAxis[instance], zAxis[instance], cmap=cm.Spectral, linewidth=0, alpha=0.7))
        else:
            plotAx.current.append(plotAx.scatter(xAxis[instance], yAxis[instance], zAxis[instance], cmap=cm.Spectral, s=5))

        if projection[0]:
            plotAx.projectionX.append(plotAx.plot(xAxis[instance], zAxis[instance], '.', zs=plotAx.get_ylim3d()[1], zdir='y', alpha=.2)[0])
        if projection[1]:
            plotAx.projectionY.append(plotAx.plot(yAxis[instance], zAxis[instance], '.', zs=plotAx.get_xlim3d()[1], zdir='x', alpha=.2)[0])
     


    