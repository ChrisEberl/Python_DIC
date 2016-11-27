# -*- coding: utf-8 -*-
"""
Created on 13/04/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file manages the relative neighbors mask procedure dialog
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np, cv2, os, csv, scipy.optimize, copy, time, matplotlib.pyplot as plt, matplotlib.path as mpath
from functions import getData, masks, DIC_Global
from interface import progressWidget

class RelativeNDialog(QDialog):

    def __init__(self, parent):

        QDialog.__init__(self)
        self.parent = parent
        self.activeMarkers = copy.deepcopy(self.parent.activeMarkers)

        self.setWindowTitle('Relative Neighbors Displacement')
        self.setMinimumWidth(500)
        dialogLayout = QVBoxLayout()

        dialogLabel = QLabel('Clean markers by relative neighbors displacement.')
        dialogLabel.setAlignment(Qt.AlignHCenter)
        dialogLabel.setMinimumHeight(30)

        checkBoxOptions = QHBoxLayout()
        checkBoxOptions.setAlignment(Qt.AlignHCenter)
        checkBoxOptions.setSpacing(10)

        self.displayXMarkers = QCheckBox('Displacement along X')
        self.displayXMarkers.setCheckable(True)
        self.displayXMarkers.setChecked(True)

        self.displayYMarkers = QCheckBox('Displacement along Y')
        self.displayYMarkers.setCheckable(True)

        self.nbMarkers = QLabel('-')
        markersLbl = QLabel('Markers')
        self.cumulativeDisp = QCheckBox('Cumulative displacement')
        self.cumulativeDisp.setCheckable(True)
        self.cumulativeDisp.setChecked(True)

        checkBoxOptions.addStretch(1)
        checkBoxOptions.addWidget(self.displayXMarkers)
        checkBoxOptions.addWidget(self.displayYMarkers)
        checkBoxOptions.addStretch(1)
        checkBoxOptions.addWidget(self.nbMarkers)
        checkBoxOptions.addWidget(markersLbl)
        checkBoxOptions.addWidget(self.cumulativeDisp)

        #checkBox clicked
        self.displayXMarkers.stateChanged.connect(self.plotRelativeN)
        self.displayYMarkers.stateChanged.connect(self.plotRelativeN)
        self.cumulativeDisp.stateChanged.connect(self.plotRelativeN)

        self.plotArea = DIC_Global.matplotlibWidget()
        self.plotArea.setFocusPolicy(Qt.ClickFocus)
        self.plotArea.setFocus()

        infosBox = QGroupBox('Settings')
        infosLayout = QHBoxLayout()

        calculationLayout = QVBoxLayout()

        settingsLayout = QHBoxLayout()

        iterationsLbl = QLabel('Max Iterations')
        self.iterationsBox = QSpinBox()
        self.iterationsBox.setRange(1,1000)
        self.iterationsBox.setValue(10)

        settingsLayout.addWidget(iterationsLbl)
        settingsLayout.addWidget(self.iterationsBox)

        self.calculateButton = QPushButton('Calculate')
        self.calculateButton.clicked.connect(self.startCalculation)
        self.targetNotReached = QLabel('<i>Waiting for calculation..</i>')
        self.targetNotReached.setAlignment(Qt.AlignCenter)
        self.targetNotReached.setContentsMargins(0,5,0,0)

        calculationLayout.addLayout(settingsLayout)
        calculationLayout.addWidget(self.calculateButton)
        calculationLayout.addWidget(self.targetNotReached)

        self.nodesValueLayout = QVBoxLayout()

        self.firstNodeLbl = QLabel('First Nodes Target')

        self.firstNodeLayout = QHBoxLayout()
        self.minValue_FirstLbl = QLabel('Min.')
        self.minValue_First = QLineEdit()
        self.minValue_First.setMaximumWidth(60)
        self.maxValue_FirstLbl = QLabel('Max.')
        self.maxValue_First = QLineEdit()
        self.maxValue_First.setMaximumWidth(60)
        self.firstNodeLayout.addWidget(self.minValue_FirstLbl)
        self.firstNodeLayout.addWidget(self.minValue_First)
        self.firstNodeLayout.addWidget(self.maxValue_FirstLbl)
        self.firstNodeLayout.addWidget(self.maxValue_First)

        self.lastNodeLbl = QLabel('Last Nodes Target')

        self.lastNodeLayout = QHBoxLayout()
        self.minValue_LastLbl = QLabel('Min.')
        self.minValue_Last = QLineEdit()
        self.minValue_Last.setMaximumWidth(60)
        self.maxValue_LastLbl = QLabel('Max.')
        self.maxValue_Last = QLineEdit()
        self.maxValue_Last.setMaximumWidth(60)
        self.lastNodeLayout.addWidget(self.minValue_LastLbl)
        self.lastNodeLayout.addWidget(self.minValue_Last)
        self.lastNodeLayout.addWidget(self.maxValue_LastLbl)
        self.lastNodeLayout.addWidget(self.maxValue_Last)

        self.minValue_First.textEdited.connect(self.coordinatesChanged)
        self.maxValue_First.textEdited.connect(self.coordinatesChanged)
        self.minValue_Last.textEdited.connect(self.coordinatesChanged)
        self.maxValue_Last.textEdited.connect(self.coordinatesChanged)

        self.nodesValueLayout.addWidget(self.firstNodeLbl)
        self.nodesValueLayout.addLayout(self.firstNodeLayout)
        self.nodesValueLayout.addWidget(self.lastNodeLbl)
        self.nodesValueLayout.addLayout(self.lastNodeLayout)

        infosLayout.addStretch(1)
        infosLayout.addLayout(calculationLayout)
        infosLayout.addStretch(1)
        infosLayout.addLayout(self.nodesValueLayout)
        infosLayout.addStretch(1)

        deleteLayout = QHBoxLayout()

        self.deleteButton = QPushButton('Delete Jumpers')
        self.deleteButton.setMaximumWidth(150)
        self.deleteButton.setContentsMargins(0,30,0,10)
        self.deleteButton.setDisabled(True)
        self.deleteButton.clicked.connect(self.deleteSelection)

        deleteLayout.addStretch(1)
        deleteLayout.addWidget(self.deleteButton)
        deleteLayout.addStretch(1)

        infosBox.setLayout(infosLayout)
        #Dialog Window Layout
        dialogLayout.addWidget(dialogLabel)
        dialogLayout.addLayout(checkBoxOptions)
        dialogLayout.addWidget(self.plotArea)
        dialogLayout.addWidget(infosBox)
        dialogLayout.addLayout(deleteLayout)

        self.setLayout(dialogLayout)

    def plotRelativeN(self):

        x_min, x_max , validPlot = self.savePlotPng()
        y_min, y_max = self.plotArea.matPlot.get_ylim()

        if validPlot != 0:
            self.plotArea.mpl_connect('button_press_event', self.on_press)

            self.topLimit = [y_max/2,y_max/2] #coordinates of nodes > 0 along the relative displacement axis
            self.bottomLimit = [y_min/2, y_min/2] #coordinates of nodes < 0 along the relative displacement axis
            self.nodeOnImage = [1, len(self.imageMatrix[0,:])] #coordinates of nodes along the image axis
            self.topLimitLine = self.plotArea.matPlot.plot(self.nodeOnImage, self.topLimit, '.-', color="red")
            self.bottomLimitLine = self.plotArea.matPlot.plot(self.nodeOnImage, self.bottomLimit, '.-', color="red")

            self.plotArea.matPlot.set_xlim([x_min, x_max])

            self.minValue_First.setText(str(self.bottomLimit[0]))
            self.maxValue_First.setText(str(self.topLimit[0]))
            self.minValue_Last.setText(str(self.bottomLimit[1]))
            self.maxValue_Last.setText(str(self.topLimit[1]))

        self.plotArea.draw_idle()

    def savePlotPng(self):

        activeImages = self.parent.activeImages
        refImg = activeImages[0]
        nbActiveImages = len(np.atleast_1d(activeImages))
        nbMarkers = len(np.atleast_1d(self.activeMarkers[refImg]))
        [x_min, x_max] = [0,nbActiveImages-1]
        validPlot = 0
        colorsX = ['green', 'lightgreen', 'limegreen', 'seagreen']
        colorsY = ['blue', 'cornflowerblue', 'royalblue', 'navy']
        cumulativePlot = self.cumulativeDisp.isChecked()

        self.plotArea.matPlot.cla()
        activeInstances = self.parent.activeInstances
        gridInstances = self.parent.grid_instances
        nbInstances = len(np.atleast_1d(activeInstances))
        for instance in range(nbInstances):
            instanceMarkers = np.intersect1d(gridInstances[activeInstances[instance]], self.activeMarkers[refImg], assume_unique=True).astype(np.int)
            nbInstancesMarkers = len(np.atleast_1d(instanceMarkers))
            markerList = np.linspace(0, nbInstancesMarkers, num=nbInstancesMarkers, endpoint=False).astype(np.int)
            if self.displayXMarkers.isChecked():
                clr = colorsX[instance % 4]
                lbl = 'Instance '+str(activeInstances[instance])+' - X-Rel. Disp.'
                if cumulativePlot:
                    self.plotArea.matPlot.plot(self.imageMatrix[0,:], self.relativeX[instance, 0, :], '-', color=clr, label=lbl)
                    for marker in range(1, nbInstancesMarkers):
                        self.plotArea.matPlot.plot(self.imageMatrix[marker,:], self.relativeX[instance, marker, :], '-', color=clr)
                else:
                    self.plotArea.matPlot.plot(self.imageMatrix[0,1:], self.relativeX[instance, 0, 1:]-self.relativeX[instance, 0, :-1], '-', color=clr, label=lbl)
                    for marker in range(1, nbInstancesMarkers):
                        self.plotArea.matPlot.plot(self.imageMatrix[marker,1:], self.relativeX[instance, marker, 1:]-self.relativeX[instance, marker, :-1], '-', color=clr)
                if nbInstancesMarkers > 0:
                    validPlot = 1
            if self.displayYMarkers.isChecked():
                clr = colorsY[instance % 4]
                lbl = 'Instance '+str(activeInstances[instance])+' - Y-Rel. Disp.'
                if cumulativePlot:
                    self.plotArea.matPlot.plot(self.imageMatrix[0,:], self.relativeX[instance, 0, :], '-', color=clr, label=lbl)
                    for marker in range(1, nbInstancesMarkers):
                        self.plotArea.matPlot.plot(self.imageMatrix[marker,:], self.relativeY[instance, marker, :], '-', color=clr)
                else:
                    self.plotArea.matPlot.plot(self.imageMatrix[0,1:], self.relativeY[instance, 0, 1:]-self.relativeY[instance, 0, :-1], '-', color=clr, label=lbl)
                    for marker in range(1, nbInstancesMarkers):
                        self.plotArea.matPlot.plot(self.imageMatrix[marker,1:], self.relativeY[instance, marker, 1:]-self.relativeY[instance, marker, :-1], '-', color=clr)
                if nbInstancesMarkers > 0:
                    validPlot = 1
        if (self.displayXMarkers.isChecked() or self.displayYMarkers.isChecked()): #plot the legend
            self.plotArea.matPlot.legend()

        self.nbMarkers.setText(str(nbMarkers))

        return x_min, x_max, validPlot

    def startCalculation(self, startUp=0):

        if startUp > 0:

            self.progressBarDialog = progressWidget.progressBarDialog('Calculation started.')
            self.neighborsThread = DIC_Global.createThread(self.parent.parentWindow, [self.parent.disp_x, self.parent.disp_y, self.parent.activeImages, self.activeMarkers, self.parent.activeInstances, self.parent.grid_instances, self.parent.neighbors], calculateOutsiders, signal=1)
            self.neighborsThread.signal.threadSignal.connect(self.getResults)
            self.neighborsThread.start()

        else:
            iterations = self.iterationsBox.value()

            relativeX = None
            relativeY = None
            if self.displayXMarkers.isChecked():
                relativeX = self.relativeX
            if self.displayYMarkers.isChecked():
                relativeY = self.relativeY

            #create Thread for calculations
            self.neighborsThread = DIC_Global.createThread(self.parent.parentWindow, [self.parent.disp_x, self.parent.disp_y, self.parent.activeImages, self.activeMarkers, self.parent.activeInstances, self.parent.grid_instances, self.parent.neighbors, iterations, self.nodeOnImage, self.topLimit, self.bottomLimit, relativeX, relativeY], newCalculation, signal=1)
            self.neighborsThread.signal.threadSignal.connect(self.getResults)
            self.deleteButton.setEnabled(False)

            cancelButton = QPushButton('Abort')
            self.progressBarDialog = progressWidget.progressBarDialog('Cleaning started.', cancel=cancelButton)
            self.progressBarDialog.canceled.connect(self.stopCalculation)

            self.neighborsThread.start()

    def stopCalculation(self):

        self.neighborsThread.args = None

        self.progressBarDialog.setCancelButtonText('Terminating..')


    def getResults(self, data):  #imageMatrix, relativeX, relativeY, activeMarkers, reachTarget OR percent, totalIterations, iterationTime, nbMarkers, currentIteration

        try:
            matrixOrInt = len(data[0])
            matrix = 1
        except:
            matrixOrInt = data[0]
            matrix = 0

        if matrix > 0: #calculation finished

            self.imageMatrix = data[0]
            self.relativeX = data[1]
            self.relativeY = data[2]
            if data[3] is not None:
                self.activeMarkers = data[3]
                if data[4] > 0:
                    self.targetNotReached.setText('<font color=green>Target reached.</font>')
                else:
                    self.targetNotReached.setText('<font color=red><b>Could not reach target.</b></font>')
            self.progressBarDialog.percent = 100
            self.deleteButton.setEnabled(True)
            self.plotRelativeN()

        else: #calculation

            if matrixOrInt == 0: #finished but couldnt reach target
                self.progressBarDialog.percent = 100
                self.targetNotReached.setText('No markers to delete.')
                self.deleteButton.setEnabled(True)
                self.plotRelativeN()
            else: #running
                display = 'Iteration : '+str(data[4])+'/'+str(data[1])+' | '+str(data[3])+' markers. | Iteration Time : '+str(data[2])
                self.progressBarDialog.percent = int(matrixOrInt)
                self.progressBarDialog.currentTitle = display

    def coordinatesChanged(self):

        toAvoid = ['', '-']

        if self.minValue_First.text() not in toAvoid:
            self.bottomLimit[0] = -np.absolute(float(self.minValue_First.text()))

        if self.maxValue_First.text() not in toAvoid:
            self.topLimit[0] = np.absolute(float(self.maxValue_First.text()))

        if self.minValue_Last.text() not in toAvoid:
            self.bottomLimit[1] = -np.absolute(float(self.minValue_Last.text()))

        if self.maxValue_Last.text() not in toAvoid:
            self.topLimit[1] = np.absolute(float(self.maxValue_Last.text()))

        self.bottomLimitLine[0].set_data(self.nodeOnImage, self.bottomLimit)
        self.topLimitLine[0].set_data(self.nodeOnImage, self.topLimit)

        self.plotArea.draw_idle()

    def on_press(self, event):

        x0 = event.xdata
        y0 = event.ydata
        if x0 is None:
            return
        distance = 50
        closerNode = len(self.bottomLimit)

        if y0 < 0:
            coeff = len(self.relativeX[0, 0,:] / np.min(self.bottomLimit))
            for node in range(closerNode):
                nodeDistance = ((x0-self.nodeOnImage[node])**2+(y0/coeff-self.bottomLimit[node]/coeff)**2)**(0.5)
                if nodeDistance < distance:
                    distance = nodeDistance
                    closerNode = node
        else:
            coeff = np.absolute(len(self.relativeX[0, 0,:]) / np.max(self.topLimit))
            for node in range(closerNode):
                nodeDistance = ((x0-self.nodeOnImage[node])**2+(y0/coeff-self.topLimit[node]/coeff)**2)**(0.5)
                if nodeDistance < distance:
                    distance = nodeDistance
                    closerNode = node

        if closerNode != len(self.bottomLimit):
            self.selectedNode = closerNode
            self.motionRect = self.plotArea.mpl_connect('motion_notify_event', self.on_motion)

    def on_motion(self,event):

        x1 = event.xdata
        y1 = event.ydata
        if x1 is None:
            return

        self.releaseEvent = self.plotArea.mpl_connect('button_release_event', self.on_release)
        if x1 > np.nanmax(self.parent.activeImages)+.6:
            x1 = np.nanmax(self.parent.activeImages)+1
        elif x1 < 1:
            x1 = 1
        self.nodeOnImage[self.selectedNode] = int(x1)

        if y1 < 0:
            self.bottomLimit[self.selectedNode] = np.around(y1, decimals=3)
        else:
            self.topLimit[self.selectedNode] = np.around(y1, decimals=3)

        self.bottomLimitLine[0].set_data(self.nodeOnImage, self.bottomLimit)
        self.topLimitLine[0].set_data(self.nodeOnImage, self.topLimit)

        self.minValue_First.setText(str(self.bottomLimit[0]))
        self.maxValue_First.setText(str(self.topLimit[0]))
        self.minValue_Last.setText(str(self.bottomLimit[1]))
        self.maxValue_Last.setText(str(self.topLimit[1]))

        self.plotArea.draw_idle()

    def on_release(self, event):

        self.plotArea.mpl_disconnect(self.motionRect)
        self.plotArea.mpl_disconnect(self.releaseEvent)

    def deleteSelection(self):

        self.parent.parentWindow.devWindow.addInfo('Deleting selected markers..')
        currentMask = copy.deepcopy(self.parent.currentMask)
        imgRef = self.parent.activeImages[0]
        maskedMarkers = np.setdiff1d(self.parent.activeMarkers[imgRef], self.activeMarkers[imgRef])
        for marker in maskedMarkers:
            currentMask[marker,:] = 0

        shouldApplyMask = masks.generateMask(currentMask, self.parent.parentWindow.fileDataPath)
        if shouldApplyMask is not None:
            self.parent.parentWindow.devWindow.addInfo('Masking selected markers..')
            progressBar = progressWidget.progressBarDialog('Saving masks..')
            masks.maskData(self.parent, currentMask, progressBar, toRecalculate=shouldApplyMask)
            self.close()

def launchRNDialog(self):

    self.analysisWidget.parentWindow.devWindow.addInfo('Cleaning Procedure Request : Relative Neighbors')
    self.relativeN = RelativeNDialog(self.analysisWidget)
    self.relativeN.startCalculation(startUp = 1)
    self.relativeN.exec_()

def newCalculation(disp_x, disp_y, activeImages, activeMarkers, activeInstances, gridInstances, neighbors, iterations, nodeOnImage, topLimitV, bottomLimitV, relativeX, relativeY, thread):

    imageMatrix = 0
    refImg = activeImages[0]
    nbInstances = len(np.atleast_1d(activeInstances))
    reachTarget = 0

    alongX = True
    alongY = True
    if relativeX is None:
        alongX = False
    if relativeY is None:
        alongY = False

    for i in range(iterations):

        currentMarkers = len(np.atleast_1d(activeMarkers[refImg]))
        toDelete = []
        startImage = int(nodeOnImage[0])
        endImage = int(nodeOnImage[1])
        nbImagesInSlice = endImage - startImage
        for image in range(startImage, endImage):
            realImage = activeImages[image]
            topLimit = topLimitV[0]+(image-startImage)/float(nbImagesInSlice)*(topLimitV[1]-topLimitV[0])
            bottomLimit = bottomLimitV[0]+(image-startImage)/float(nbImagesInSlice)*(bottomLimitV[1]-bottomLimitV[0])
            for instance in range(nbInstances):
                instanceMarkers = np.intersect1d(gridInstances[activeInstances[instance]], activeMarkers[realImage], assume_unique=True).astype(np.int)
                nbInstanceMarkers = len(np.atleast_1d(instanceMarkers))
                if alongX:
                    for marker in range(nbInstanceMarkers):
                        currentValue = relativeX[instance, marker, image]
                        if currentValue > topLimit or currentValue < bottomLimit:
                            if instanceMarkers[marker] not in toDelete:
                                toDelete.append(instanceMarkers[marker])
                if alongY:
                    for marker in range(nbInstanceMarkers):
                        currentValue = relativeY[instance, marker, image]
                        if currentValue > topLimit or currentValue < bottomLimit:
                            if instanceMarkers[marker] not in toDelete:
                                toDelete.append(instanceMarkers[marker])

        if len(np.atleast_1d(toDelete)) > 0:
            for delete in range(len(np.atleast_1d(activeMarkers))):
                maskedMarkers = np.setdiff1d(activeMarkers[delete], toDelete)
                activeMarkers[delete] = maskedMarkers
                    #activeMarkers = np.delete(activeMarkers, toDelete, 1)

        nbActiveMarkers = len(np.atleast_1d(activeMarkers[refImg]))
        if nbActiveMarkers != currentMarkers and nbActiveMarkers > 2 and thread.args is not None:
            imageMatrix, relativeX, relativeY = calculateOutsiders(disp_x, disp_y, activeImages, activeMarkers, activeInstances, gridInstances, neighbors, thread, iteration=i, totalIteration=iterations, startUp=0)
        else:
            if nbActiveMarkers < 3:
                reachTarget = 0
            else:
                reachTarget = 1
            break
    thread.signal.threadSignal.emit([imageMatrix, relativeX, relativeY, activeMarkers, reachTarget])

def calculateOutsiders(disp_x, disp_y, activeImages, activeMarkers, activeInstances, gridInstances, neighbors, thread, iteration=0, totalIteration=1, startUp=1):

    startTime = time.time()
    nbActiveImages = len(np.atleast_1d(activeImages))
    nbInstances = len(np.atleast_1d(activeInstances))
    referenceImage = activeImages[0]

    old_percent = iteration*100/totalIteration+1
    thread.signal.threadSignal.emit([old_percent, 0, 0, len(np.atleast_1d(activeMarkers[referenceImage])), iteration+1])

    maxMarkersPerInstance = 0
    for instance in range(nbInstances):
        nbMarkersInInstance = len(np.atleast_1d(gridInstances[activeInstances[instance]]))
        if nbMarkersInInstance > maxMarkersPerInstance:
            maxMarkersPerInstance = nbMarkersInInstance

    relativeDispX = np.zeros((nbInstances, maxMarkersPerInstance, nbActiveImages))
    relativeDispY = np.zeros((nbInstances, maxMarkersPerInstance, nbActiveImages))
    imageMatrix = np.ones((maxMarkersPerInstance, nbActiveImages))
    totalMarkers = 0
    for imageNb in range(nbActiveImages):
        image = activeImages[imageNb]
        for instance in range(nbInstances):
            instanceMarkers = np.intersect1d(gridInstances[activeInstances[instance]], activeMarkers[image], assume_unique=True).astype(np.int)
            nbInstanceMarkers = len(np.atleast_1d(instanceMarkers))
            for marker in range(nbInstanceMarkers):
                currentMarker = instanceMarkers[marker]
                activeNeighbors = np.intersect1d(neighbors[currentMarker], activeMarkers[image], assume_unique=True).astype(np.int)
                totalMarkers += 1
                if len(np.atleast_1d(activeNeighbors)) > 0:
                    medianX = np.median(disp_x[activeNeighbors, image])
                    medianY = np.median(disp_y[activeNeighbors, image])
                    relativeDispX[instance, marker, imageNb] = disp_x[currentMarker, image] - medianX
                    relativeDispY[instance, marker, imageNb] = disp_y[currentMarker, image] - medianY

        percent = int(iteration*100/totalIteration+imageNb*100/totalIteration/nbActiveImages)
        if percent > old_percent:
            thread.signal.threadSignal.emit([percent, totalIteration, np.around(time.time()-startTime, decimals=2), len(np.atleast_1d(activeMarkers[referenceImage])), iteration+1])
            old_percent = percent

        imageMatrix[:,imageNb] = imageNb*imageMatrix[:,imageNb]

    if startUp < 1:
        return imageMatrix, relativeDispX, relativeDispY
    else:
        thread.signal.threadSignal.emit([imageMatrix, relativeDispX, relativeDispY, None, 1])
