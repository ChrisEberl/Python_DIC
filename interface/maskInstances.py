# -*- coding: utf-8 -*-
"""
Created on 22/07/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file manages the grid instances dialog
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np
from interface import progressWidget
from functions import masks

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class maskGridInstanceDialog(QDialog):

    def __init__(self, parent):

        QDialog.__init__(self)

        self.setWindowTitle('Mask Grid Instance')
        self.setMinimumWidth(600)

        dialogLayout = QVBoxLayout()

        dialogLabel = QLabel('Chose grid instances you want to display on the visualisation panel.')
        dialogLabel.setAlignment(Qt.AlignCenter)

        self.plotArea = MatplotlibImageWidget(self)
        self.plotArea.setFocusPolicy(Qt.ClickFocus)
        self.plotArea.setFocus()

        infosLayout = QHBoxLayout()

        allButton = QPushButton('(De)Select *')
        allButton.setMaximumWidth(80)
        allButton.clicked.connect(self.allSelect)

        infoLbl = QLabel('Active Instances:')
        self.infoValue = QLabel('0')

        infosLayout.addStretch(1)
        infosLayout.addWidget(allButton)
        infosLayout.addStretch(1)
        infosLayout.addWidget(infoLbl)
        infosLayout.addWidget(self.infoValue)
        infosLayout.addStretch(1)


        buttonLayout = QHBoxLayout()
        self.dialogButton = QPushButton('Apply')
        self.dialogButton.setMaximumWidth(100)
        self.dialogButton.clicked.connect(lambda: self.showSelection(parent))
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.dialogButton)
        buttonLayout.addStretch(1)


        noteLbl = QLabel('No masks will be created. Deactivated instances will only be hidden temporaly.')
        noteLbl.setAlignment(Qt.AlignCenter)

        dialogLayout.addWidget(dialogLabel)
        dialogLayout.addWidget(self.plotArea)
        dialogLayout.addLayout(infosLayout)
        dialogLayout.addLayout(buttonLayout)
        dialogLayout.addWidget(noteLbl)

        self.setLayout(dialogLayout)


    def initiateInstances(self, activeInstances, grid_instances, data_x, data_y):

        instancesList = []
        instanceNb = len(np.atleast_1d(grid_instances))

        for instance in range(instanceNb):
            dataX = data_x[grid_instances[instance]]
            dataY = data_y[grid_instances[instance]]
            if len(np.atleast_1d(dataX)) > 0:
                centerX = np.mean(dataX)
                centerY = np.mean(dataY)
                isActive = instance in activeInstances
                instancesList.append([centerX,centerY, isActive, instance])

        self.instancesList = instancesList
        self.axesLimit = [np.nanmin(data_x), np.nanmax(data_x), np.nanmin(data_y), np.nanmax(data_y)]

        self.plotInstances()

    def allSelect(self):

        nbInstances = len(self.instancesList)
        totalTrue = 0
        for instance in self.instancesList:
            if instance[2] == True:
                totalTrue += 1

        if totalTrue == nbInstances:
            for instance in range(nbInstances):
                self.instancesList[instance][2] = False
        else:
            for instance in range(nbInstances):
                self.instancesList[instance][2] = True

        self.plotInstances()

    def plotInstances(self):

        self.plotArea.imagePlot.cla()
        self.plotArea.mpl_connect('button_press_event', self.on_press)


        activeInstances = 0
        nb_instances = len(self.instancesList)
        if nb_instances > 30:
            sizeLbl = 10
        else:
            sizeLbl = 25

        for instance in self.instancesList:
            if instance[2] == False:
                self.plotArea.imagePlot.text(instance[0], instance[1], instance[3], color='red', size=.9*sizeLbl, ha="center", va="center", bbox=dict(boxstyle="circle", ec='r', fc='lightcoral', pad=.5))
            else:
                self.plotArea.imagePlot.text(instance[0], instance[1], instance[3], color='green', size=1.1*sizeLbl, ha="center", va="center", bbox=dict(boxstyle="circle", ec='g', fc='lightgreen', pad=.5))
                activeInstances += 1

        self.infoValue.setText(str(activeInstances))
        if activeInstances < 1:
            self.dialogButton.setDisabled(True)
        else:
            self.dialogButton.setEnabled(True)

        self.plotArea.imagePlot.set_xlim([self.axesLimit[0], self.axesLimit[1]])
        self.plotArea.imagePlot.set_ylim([self.axesLimit[3], self.axesLimit[2]])
        self.plotArea.draw_idle()


    def showSelection(self, parent):

        currentMask = parent.currentMask

        activeInstances = []
        for instance in self.instancesList:
            if instance[2] == True:
                activeInstances.append(instance[3])

        parent.activeInstances = activeInstances
        progressBar = progressWidget.progressBarDialog('Re-initializing the display..')
        masks.maskData(parent, currentMask, progressBar)

        self.close()


    def on_press(self, event):

        x0 = event.xdata
        y0 = event.ydata
        if x0 is None:
            return

        closerInstance = 0
        distance = 10000

        nb = 0
        for instance in self.instancesList:
            instanceDistance = ((x0-instance[0])**2+(y0-instance[1])**2)**(0.5)
            if instanceDistance < distance:
                distance = instanceDistance
                closerInstance = nb
            nb += 1

        self.instancesList[closerInstance][2] = not self.instancesList[closerInstance][2]
        self.plotInstances()





def launchMaskGridDialog(self):

    self.analysisWidget.parentWindow.devWindow.addInfo('Mask Procedure Request : Mask Instances')

    referenceImage = self.analysisWidget.activeImages[0]
    activeMarkers = self.analysisWidget.activeMarkers[referenceImage]
    self.maskInstances = maskGridInstanceDialog(self.analysisWidget)
    self.maskInstances.initiateInstances(self.analysisWidget.activeInstances, self.analysisWidget.grid_instances, self.analysisWidget.data_x[:, referenceImage], self.analysisWidget.data_y[:, referenceImage])

    self.maskInstances.exec_()


class MatplotlibImageWidget(FigureCanvas):

    def __init__(self, parentWidget):
        super(MatplotlibImageWidget,self).__init__(Figure())
        #self.figure = Figure(figsize=(12,3.5))
        self.figure = Figure()
        self.figure.set_facecolor('none')
        self.canvas = FigureCanvas(self.figure)
        self.imagePlot = self.figure.add_subplot(111)
        self.figure.tight_layout()
