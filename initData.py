# -*- coding: utf-8 -*-
"""
Created on 02/05/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file manages the opened data and initiate variables content along with strain and marker neighbors calculation
"""


from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np
import scipy
import time
import progressWidget
import dockWidget


def initPlottedData(parent, progressBar, currentMask, thread):

    tic = time.time()

    if progressBar is None:
        progressBar = progressWidget.progressBarDialog('Starting Processes..')

    #building the list of activeMarkers and activeImages
    #activeMarkers contains the list of each active markers on each image : activeMarkers are markers which are not masked
    #activeImages contains the list of active images : activeImages are images with at least 3 markers not masked
    allMarkers = np.linspace(0, parent.nb_marker, parent.nb_marker, endpoint=False).astype(np.int)
    activeMarkers = []
    activeImages = []
    parent.currentMask = currentMask
    for image in range(parent.nb_image):
        markersActiveOnCurrentImage = np.array([marker for marker in allMarkers if currentMask[marker,image] == 1]).astype(np.int)
        nbActiveMarkersInImage = len(np.atleast_1d(markersActiveOnCurrentImage))
        if nbActiveMarkersInImage >= 1:
            activeImages.append(image)
        activeMarkers.append(markersActiveOnCurrentImage)
    parent.activeMarkers = activeMarkers
    parent.activeImages = activeImages
    nbActiveImages = len(np.atleast_1d(activeImages))


    #getting coordinates from parent
    data_x = parent.data_x
    data_y = parent.data_y
    disp_x = parent.disp_x
    disp_y = parent.disp_y

    referenceImage = activeImages[0]

    #getting coordinates of active markers on the first active image
    data_x_init = parent.data_x[:,referenceImage]
    data_y_init = parent.data_y[:,referenceImage]

    #update the grid instances list
    gridInstances = parent.grid_instances
    activeInstances = parent.activeInstances
    for instance in activeInstances:
        gridInstances[instance] = np.intersect1d(gridInstances[instance], activeMarkers[referenceImage], assume_unique=True).astype(np.int)
        nbMarkersInInstance = len(np.atleast_1d(gridInstances[instance]))
        if nbMarkersInInstance < 1:
            activeInstances = np.setdiff1d(activeInstances, instance, assume_unique=True)
    parent.grid_instances = gridInstances
    parent.activeInstances = activeInstances

    #getting markers neighborhood
    fileDataPath = parent.parentWindow.fileDataPath
    if parent.neighbors is None:
        neighbors = np.genfromtxt(fileDataPath+'/neighbors.dat')
        parent.neighbors = neighbors
    else:
        neighbors = parent.neighbors

    #X and Y axis limits for 3D plots + 1D strain
    nbInstances = len(np.atleast_1d(activeInstances))
    StrainX = np.zeros((nbActiveImages,nbInstances))
    StrainY = np.zeros((nbActiveImages,nbInstances))
    localStrainIntersectX = np.zeros((nbActiveImages,nbInstances))
    localStrainIntersectY = np.zeros((nbActiveImages,nbInstances))
    minCoordX, maxCoordX = np.max(data_x_init), 0
    minCoordY, maxCoordY = np.max(data_y_init), 0
    for image in range(nbActiveImages):
        currentImage = activeImages[image]
        for instance in range(nbInstances):
            currentInstance = activeInstances[instance]
            currentMarkers = np.intersect1d(activeMarkers[currentImage], gridInstances[currentInstance], assume_unique=True).astype(np.int)
            if len(np.atleast_1d(currentMarkers)) > 1:
                StrainX[image,instance], localStrainIntersectX[image,instance] = np.polyfit(data_x[currentMarkers, currentImage], disp_x[currentMarkers, currentImage], 1)
                StrainY[image,instance], localStrainIntersectY[image,instance] = np.polyfit(data_y[currentMarkers, currentImage], disp_y[currentMarkers, currentImage], 1)
                currentMinX, currentMaxX = np.min(data_x[currentMarkers,currentImage]), np.max(data_x[currentMarkers,currentImage])
                currentMinY, currentMaxY = np.min(data_y[currentMarkers,currentImage]), np.max(data_y[currentMarkers,currentImage])
                if currentMinX < minCoordX:
                    minCoordX = currentMinX
                if currentMaxX > maxCoordX:
                    maxCoordX = currentMaxX
                if currentMinY < minCoordY:
                    minCoordY = currentMinY
                if currentMaxY > maxCoordY:
                    maxCoordY = currentMaxY
    parent.xLimit = [minCoordX, maxCoordX]
    parent.yLimit = [minCoordY, maxCoordY]
    parent.localStrainIntersectX = localStrainIntersectX
    parent.localStrainIntersectY = localStrainIntersectY

    #saving 1D strain
    np.savetxt(parent.parentWindow.fileDataPath+'/strainx.dat', StrainX)
    np.savetxt(parent.parentWindow.fileDataPath+'/strainy.dat', StrainY)
    parent.strainX_data = StrainX
    parent.strainY_data = StrainY

    #calculation for correlation 2D
    parent.xi = np.linspace(minCoordX, maxCoordX, 100)
    parent.yi = np.linspace(minCoordY, maxCoordY, 100)

    parent.zi = []
    parent.zi_strainX = []
    parent.zi_strainY = []
    #parent.zi_strainXY = []


    #MULTIPROCESSING
    PROCESSES = int(parent.parentWindow.profileData['nbProcesses'][parent.parentWindow.currentProfile])
    if PROCESSES > 0:
        args = []
        nbImageCore = nbActiveImages/PROCESSES
        if nbImageCore < 2:
            nbImageCore = 2
            PROCESSES = nbActiveImages/2+1
        parent.parentWindow.devWindow.addInfo('Starting calculation with '+str(PROCESSES)+' processes.')
        for i in range (0, PROCESSES):
            start = int(i*nbImageCore)
            if i >= PROCESSES-1: #last process do all the last images
                end = nbActiveImages
            else:
                end = int((i+1)*nbImageCore)
            args.append((start,end, data_x[:, activeImages[start:end]], data_y[:, activeImages[start:end]], disp_x[:, activeImages[start:end]], disp_y[:, activeImages[start:end]], parent.data_corr[:, activeImages[start:end]], parent.xi, parent.yi, activeImages, gridInstances, activeInstances, neighbors, data_x_init, data_y_init))

        result = parent.parentWindow.createProcess(calculateCoordinates, args, PROCESSES, progressBar, 'Calculating missing coordinates ...')

    else:
        result = calculateCoordinates(0, nbActiveImages, data_x, data_y, disp_x, disp_y, parent.data_corr, parent.xi, parent.yi, activeImages, gridInstances, activeInstances, neighbors, None, None)

    nbInstances = len(np.atleast_1d(activeInstances))
    for instance in range(nbInstances):
        parent.zi.append(result[instance])
        parent.zi_strainX.append(result[nbInstances+instance])
        parent.zi_strainY.append(result[nbInstances+instance])

    parent.parentWindow.devWindow.addInfo('Calculation terminated in '+str(time.time()-tic)+' seconds.')


    thread.signal.threadSignal.emit([])
    return


def calculateCoordinates(imageStart, imageEnd, data_x, data_y, disp_x, disp_y, data_corr, xi, yi, activeImages, grid_instances, activeInstances, neighbors, data_x_init, data_y_init, q, pipe):

    nbImages = imageEnd-imageStart
    nbInstances = len(np.atleast_1d(activeInstances))
    result = np.zeros((3*nbInstances, nbImages, xi.shape[0], yi.shape[0]))
    previousTime = time.time()
    for image in range(0, nbImages):
        if pipe is not None:
            currentProgress = image * 100 / nbImages
            currentTime = time.time()
            if currentTime > previousTime + .05:
                previousTime = currentTime
                pipe.send(currentProgress)
        currentImage = image
        data_x_current = data_x[:, currentImage]
        data_y_current = data_y[:, currentImage]

        for instance in range(nbInstances):
            instanceMarkers = np.atleast_1d(grid_instances[activeInstances[instance]])
            if len(np.atleast_1d(instanceMarkers)) < 3:
                result[instance][image][0,0] = 99999
                result[nbInstances+instance][image][0,0] = 99999
                result[2*nbInstances+instance][image][0,0] = 99999
                continue
            #CORRELATION 2D
            data_corr_clean = data_corr[instanceMarkers, currentImage]
            result[instance][image] = scipy.interpolate.griddata((data_x_init[instanceMarkers], data_y_init[instanceMarkers]), data_corr_clean, (xi[None,:], yi[:,None]), method='cubic')

            ## 2D STRAIN ##
            currentStrainXX = []
            currentStrainXY = []
            currentStrainYY = []
            currentStrainYX = []
            strainCalculated = []
            for marker in instanceMarkers:
                activeNeighbors = np.array([neighbor for neighbor in neighbors[marker] if neighbor in instanceMarkers]).astype(np.int)

                xData = data_x[activeNeighbors, currentImage]
                yData = data_y[activeNeighbors, currentImage]
                dispDataX = disp_x[activeNeighbors, currentImage]
                dispDataY = disp_y[activeNeighbors, currentImage]
                if len(np.atleast_1d(xData)) > 6:
                    matrixDataX = np.c_[xData,yData,dispDataX]
                    matrixDataY = np.c_[yData,xData,dispDataY]
                    #2n Order
                    A = np.c_[np.ones(matrixDataX.shape[0]), matrixDataX[:,:2], np.prod(matrixDataX[:,:2], axis=1), matrixDataX[:,:2]**2]
                    B = np.c_[np.ones(matrixDataY.shape[0]), matrixDataY[:,:2], np.prod(matrixDataY[:,:2], axis=1), matrixDataY[:,:2]**2]
                    C,_,_,_ = scipy.linalg.lstsq(A, matrixDataX[:,2]) # Z = C[4]*X**2. + C[5]*Y**2. + C[3]*X*Y + C[1]*X + C[2]*Y + C[0]
                    D,_,_,_ = scipy.linalg.lstsq(B, matrixDataY[:,2])
                    resultStrainXX = 2*C[4]*data_x_current[marker]+C[1]+C[3]*data_y_current[marker]
                    resultStrainXY = 2*C[5]*data_y_current[marker]+C[2]+C[3]*data_x_current[marker]
                    resultStrainYY = 2*D[4]*data_y_current[marker]+D[1]+D[3]*data_x_current[marker]
                    resultStrainYX = 2*D[5]*data_x_current[marker]+D[2]+D[3]*data_y_current[marker]
                    #1rst Order #NON-TESTED
    #                A = np.c_[data[:,0], data[:,1], np.ones(data.shape[0])]
    #                C,_,_,_ = scipy.linalg.lstsq(A, data[:,2])
    #                resultStrainXX = C[0]
    #                resultStrainXY = C[1]
    #                resultStrainYY = D[0]
    #                resultStrainYX = D[1]
                    currentStrainXX.append(resultStrainXX)
                    currentStrainXY.append(resultStrainXY)
                    currentStrainYY.append(resultStrainYY)
                    currentStrainYX.append(resultStrainYX)
                    strainCalculated.append(marker)

            if len(np.atleast_1d(strainCalculated)) > 3:
                result[nbInstances+instance][image] = scipy.interpolate.griddata((data_x_init[strainCalculated], data_y_init[strainCalculated]), currentStrainXX, (xi[None,:], yi[:,None]), method='cubic')
                result[2*nbInstances+instance][image] = scipy.interpolate.griddata((data_x_init[strainCalculated], data_y_init[strainCalculated]), currentStrainYY, (xi[None,:], yi[:,None]), method='cubic')
            else:
                 result[nbInstances+instance][image][0,0] = 99999
                 result[2*nbInstances+instance][image][0,0] = 99999


    if q is not None: #if multiprocessing, results are put in the queue
        q.put(result)
        q.close()
        return
    else:
        return result



def calculateNeighbors(activeMarkers, data_x_init, data_y_init, minNeighbors, fileDataPath, progressBar=None):
#return an array containing at least the 'minNeighbors' closest neighbors of each marker and save it in analysis folder

    activeMarkers = np.array(activeMarkers).astype(np.int)
    markerNeighbors = []
    maxCorrDistance = 0
    data_x_unique = np.unique(data_x_init.astype(np.int))
    data_y_unique = np.unique(data_y_init.astype(np.int))
    if len(np.atleast_1d(data_x_unique)) > 1 and len(np.atleast_1d(data_y_unique)) > 1:
        minDistance = max(np.absolute(data_x_unique[1]-data_x_unique[0]), np.absolute(data_y_unique[1]-data_y_unique[0]))
        maxCorrDistance = max(np.max(data_x_unique)-np.min(data_x_unique), np.max(data_y_unique)-np.min(data_y_unique))
    else:
        minDistance = maxCorrDistance
    if minDistance < 5:
        minDistance = 5
    nbMarkers = len(activeMarkers)
    maxNeighbors = 0
    maxIteration = int(maxCorrDistance / minDistance) + 1
    if nbMarkers < minNeighbors:
        minNeighbors = nbMarkers
    previousTime = time.time()
    previousProgress = 1
    markerProcessed = 0
    for target_marker in activeMarkers:

        if progressBar is not None:
            currentProgress = int(markerProcessed * 100 / nbMarkers)
            currentTime = time.time()
            if currentTime > previousTime + .05 and currentProgress != previousProgress and currentProgress < 100:
                previousTime = currentTime
                previousProgress = currentProgress
                progressBar.percent = currentProgress

        nbNeighbors = 0
        distance = minDistance
        currentMarkerNeighbors = []
        for iteration in range(maxIteration):
            minX = data_x_init[target_marker]-distance
            maxX = data_x_init[target_marker]+distance
            minY = data_y_init[target_marker]-distance
            maxY = data_y_init[target_marker]+distance
            currentMarkerNeighbors = [marker for marker in activeMarkers if data_x_init[marker] < maxX and data_x_init[marker] > minX and data_y_init[marker] < maxY and data_y_init[marker] > minY]
            nbNeighbors = len(np.atleast_1d(currentMarkerNeighbors))
            if nbNeighbors < minNeighbors:
                distance += minDistance
            else:
                break
        if nbNeighbors > maxNeighbors:
            maxNeighbors = nbNeighbors
        markerNeighbors.append(currentMarkerNeighbors)
        markerProcessed += 1


    neighbors = np.zeros((nbMarkers,maxNeighbors))
    for marker in range(nbMarkers):
        currentNeighbors = len(np.atleast_1d(markerNeighbors[marker]))
        neighbors[marker, :currentNeighbors] = markerNeighbors[marker]
        neighbors[marker, currentNeighbors:maxNeighbors] = np.nan
    np.savetxt(fileDataPath+'/neighbors.dat', neighbors, fmt='%1.0f')
    return neighbors


def createPlots(self):

    self.parentWindow.devWindow.addInfo('Setting up the plots.')

    for instance in dockWidget.dockPlot.instances: #deleting dockwidget if there are
        instance.close()
        instance.deleteLater()
    dockWidget.dockPlot.instances = []

    ######## CREATION OF PLOTS ###########
    self.displacementX = dockWidget.dockPlot('X-Displacement (3D)', 1, 0, self.parentWindow)
    self.parentWindow.addDockWidget(Qt.TopDockWidgetArea, self.displacementX)

    self.displacementY = dockWidget.dockPlot('Y-Displacement (3D)', 1, 0, self.parentWindow)
    self.parentWindow.addDockWidget(Qt.TopDockWidgetArea, self.displacementY)


    self.correlation = dockWidget.dockPlot('Correlation (3D)', 1, 0, self.parentWindow)
    self.parentWindow.addDockWidget(Qt.TopDockWidgetArea, self.correlation)


    self.correlation2D = dockWidget.dockPlot('Correlation (2D)', 0, 2, self.parentWindow)
    self.parentWindow.addDockWidget(Qt.TopDockWidgetArea, self.correlation2D)


    self.deviationX = dockWidget.dockPlot('X-Standard Deviation (3D)', 1, 0, self.parentWindow)
    self.parentWindow.addDockWidget(Qt.TopDockWidgetArea, self.deviationX)


    self.deviationY = dockWidget.dockPlot('Y-Standard Deviation (3D)', 1, 0, self.parentWindow)
    self.parentWindow.addDockWidget(Qt.TopDockWidgetArea, self.deviationY)


    self.displacement2D = dockWidget.dockPlot('Displacement (2D)', 0, 1, self.parentWindow)
    self.parentWindow.addDockWidget(Qt.LeftDockWidgetArea, self.displacement2D)

    self.strainX = dockWidget.dockPlot('X-Local Strain (1D)', 0, 3, self.parentWindow)
    self.parentWindow.addDockWidget(Qt.RightDockWidgetArea, self.strainX)

    self.strainY = dockWidget.dockPlot('Y-Local Strain (1D)', 0, 3, self.parentWindow)
    self.parentWindow.addDockWidget(Qt.RightDockWidgetArea, self.strainY)

    self.strain2DX = dockWidget.dockPlot('X-Local Strain (2D)', 0, 4, self.parentWindow)
    self.parentWindow.addDockWidget(Qt.RightDockWidgetArea, self.strain2DX)

    self.strain2DY = dockWidget.dockPlot('Y-Local Strain (2D)', 0, 4, self.parentWindow)
    self.parentWindow.addDockWidget(Qt.RightDockWidgetArea, self.strain2DY)

    self.trueStrainX = dockWidget.dockPlot('X-True Strain', 0, 5, self.parentWindow)
    self.parentWindow.addDockWidget(Qt.TopDockWidgetArea, self.trueStrainX)

    self.trueStrainY = dockWidget.dockPlot('Y-True Strain', 0, 5, self.parentWindow)
    self.parentWindow.addDockWidget(Qt.TopDockWidgetArea, self.trueStrainY)

    #Disabled plots by default
    self.trueStrainX.setVisible(False)
    self.trueStrainY.setVisible(False)

    #create tabs
    self.parentWindow.tabifyDockWidget(self.displacementX, self.displacementY)
    self.parentWindow.tabifyDockWidget(self.correlation, self.correlation2D)
    self.parentWindow.tabifyDockWidget(self.deviationX, self.deviationY)
    self.parentWindow.tabifyDockWidget(self.strainX, self.strainY)
    self.parentWindow.tabifyDockWidget(self.strainY, self.strain2DX)
    self.parentWindow.tabifyDockWidget(self.strain2DX, self.strain2DY)

    ##############################


    self.parentWindow.devWindow.addInfo('Plots initiated.', self.parentWindow.statusBar())
