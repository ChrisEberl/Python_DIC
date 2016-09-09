# -*- coding: utf-8 -*-
"""
Created on 19/07/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file manages the filter functions available in the grid creation tool
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import numpy as np
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.figure
import cv2
import getData



class filterCreationWidget(QWidget): # contains the main filter informations and allow user to apply filter to the set of images

    def __init__(self, parent):

        super(filterCreationWidget, self).__init__()

        self.setMinimumWidth(200)
        self.setMaximumWidth(250)
        self.parent = parent
        self.setContentsMargins(0,0,0,0)

        verticalLayout = QVBoxLayout()
        verticalLayout.setAlignment(Qt.AlignCenter)
        verticalLayout.setContentsMargins(0,0,0,0)

        filterListLbl = QLabel('Filters')

        self.availableFilters = QListWidget()
        self.availableFilters.setMinimumHeight(50)

        #filterlist
        self.filterList = [['Zoom','Width','Height','Top-Left Coord.',200,100,'0,0'],['Blur','Kernel Width','Kernel Height','',5,5,0],['Gaussian','Kernel Width','Kernel Height','Standard Dev.',9,9,'0,0'],['Brightness','Phi','Theta','Degree',1,1,'2'],['Darkness','Phi','Theta','Degree',1,1,'2'],['Contrast','Phi','Theta','Degree',1,1,'2']]
        #end filterlist
        for element in self.filterList:
            currentFilter = QListWidgetItem(element[0])
            self.availableFilters.addItem(currentFilter)

        self.availableFilters.itemSelectionChanged.connect(self.itemSelected)

        filterParameterLayout = QHBoxLayout()
        filterParameterLayout.setAlignment(Qt.AlignCenter)
        filterParameterLayout.setContentsMargins(0,0,0,0)

        filterParameterLblLayout = QVBoxLayout()
        filterParameterLblLayout.setContentsMargins(0,0,0,0)
        self.parameterLbls = [QLabel('-'),QLabel('-'),QLabel('-')]
        for label in self.parameterLbls:
            filterParameterLblLayout.addWidget(label)

        filterParameterValueLayout = QVBoxLayout()
        filterParameterValueLayout.setContentsMargins(0,0,0,0)
        self.parameterValues = [QSpinBox(), QSpinBox(), QLineEdit()]
        for values in self.parameterValues:
            values.setMaximumWidth(50)
            filterParameterValueLayout.addWidget(values)
        filterParameterLayout.addLayout(filterParameterLblLayout)
        filterParameterLayout.addLayout(filterParameterValueLayout)

        saveButtonLayout = QHBoxLayout()
        saveButtonLayout.setContentsMargins(0,0,0,0)
        self.previewButton = QPushButton('Preview')
        self.previewButton.setMaximumWidth(50)
        self.previewButton.setDisabled(True)
        self.previewButton.mousePressEvent = lambda x: self.parent.plotImage(filterPreview=[self.availableFilters.currentItem().text(), self.parameterValues[0].value(), self.parameterValues[1].value(), self.parameterValues[2].text()])
        self.previewButton.mouseReleaseEvent = lambda x: self.parent.plotImage()
        self.saveButton = QPushButton('Apply Filter')
        self.saveButton.setMaximumWidth(80)
        self.saveButton.setDisabled(True)
        self.saveButton.clicked.connect(self.addFilterToApply)
        saveButtonLayout.addStretch(1)
        saveButtonLayout.addWidget(self.previewButton)
        saveButtonLayout.addWidget(self.saveButton)
        saveButtonLayout.addStretch(1)

        appliedFiltersLbl = QLabel('Applied Filter(s)')

        self.appliedFilters = QListWidget()
        self.appliedFilters.setMinimumHeight(50)
        self.appliedFiltersList = []

        deleteButtonLayout = QHBoxLayout()
        deleteButtonLayout.setContentsMargins(0,0,0,0)
        self.deleteButton = QPushButton('Delete Selection')
        self.deleteButton.setContentsMargins(0,0,0,0)
        self.deleteButton.setMaximumWidth(100)
        self.deleteButton.setDisabled(True)
        self.deleteButton.clicked.connect(self.deleteAppliedFilter)
        deleteButtonLayout.addStretch(1)
        deleteButtonLayout.addWidget(self.deleteButton)
        deleteButtonLayout.addStretch(1)

        self.histoPlot = matplotlibWidget()
        self.histoPlot.setContentsMargins(0,0,0,0)
        self.histoPlot.setMinimumHeight(60)
        self.histoPlot.setMaximumHeight(200)

        verticalLayout.addWidget(filterListLbl)
        verticalLayout.addWidget(self.availableFilters)
        verticalLayout.addLayout(filterParameterLayout)
        verticalLayout.addLayout(saveButtonLayout)
        verticalLayout.addWidget(appliedFiltersLbl)
        verticalLayout.addWidget(self.appliedFilters)
        verticalLayout.addLayout(deleteButtonLayout)
        verticalLayout.addWidget(self.histoPlot)

        self.setLayout(verticalLayout)

    def itemSelected(self):

        self.saveButton.setEnabled(True)
        self.previewButton.setEnabled(True)
        for element in self.filterList:
            if element[0] == self.availableFilters.currentItem().text():
                for parameter in range(3):
                    parameterName = element[1+parameter]
                    if parameterName != '':
                        self.parameterLbls[parameter].setText(parameterName)
                        self.parameterValues[parameter].setEnabled(True)
                        try:
                            if element[0] == 'Zoom':
                                self.parameterValues[parameter].setRange(0,10000)
                            self.parameterValues[parameter].setValue(element[parameter+4])
                        except:
                            self.parameterValues[parameter].setText(str(element[parameter+4]))
                    else:
                        self.parameterValues[parameter].setDisabled(True)
                        self.parameterLbls[parameter].setText('-')

    def addFilterToApply(self):

        filterName = self.availableFilters.currentItem().text()
        filterDisplayName = filterName
        changeZoom = 0
        if len(self.appliedFiltersList) > 0:
            for element in self.appliedFiltersList:
                if element[0] == filterName and filterName != 'Zoom':
                    filterDisplayName = filterName+str(np.random.randint(100))
                elif element[0] == filterName and filterName == 'Zoom':
                    changeZoom = 1
                    try:
                        coordinates = str(int(self.parameterValues[2].text().split(',')[0])+int(element[4].split(',')[0]))+','+str(int(self.parameterValues[2].text().split(',')[1])+int(element[4].split(',')[1]))
                    except:
                        element[2:5] = [element[2]+self.parameterValues[0].value(), element[3]+self.parameterValues[1].value(), '0,0']
                        break
                    element[2:5] = [element[2]+self.parameterValues[0].value(), element[3]+self.parameterValues[1].value(), coordinates]

        if changeZoom < 1:
            self.appliedFiltersList.append([filterDisplayName, filterName, self.parameterValues[0].value(), self.parameterValues[1].value(), self.parameterValues[2].text()])

        self.refreshAppliedFilters()

    def deleteAppliedFilter(self):

        nb = 0
        if len(self.appliedFiltersList) > 0:
            for element in self.appliedFiltersList:
                if element[0] == self.appliedFilters.currentItem().text():
                    self.appliedFiltersList = np.delete(np.array(self.appliedFiltersList), nb, 0).tolist()
                    break
                nb+=1
        self.refreshAppliedFilters()

    def refreshAppliedFilters(self):

        self.appliedFilters.clear()
        if len(self.appliedFiltersList) > 0:
            self.deleteButton.setEnabled(True)
            for filterToApply in self.appliedFiltersList:
                currentFilter = QListWidgetItem(filterToApply[0])
                self.appliedFilters.addItem(currentFilter)
        else:
            self.deleteButton.setDisabled(True)
        self.parent.plotImage()



def applyFilterListToImage(filterList, image):

    if filterList is not None:
        nbFilters = len(np.atleast_1d(filterList))
        if nbFilters > 0:
            for currentFilter in np.atleast_1d(filterList):
                filterName = currentFilter[1]
                filterParameters = [currentFilter[2], currentFilter[3], currentFilter[4]]
                image = applyFilterToImage(filterName, filterParameters, image)

    return image

def applyFilterToImage(filterName, filterParameters, image):

    backupImage = image
    if filterName == 'Zoom':

        try:
            minY = int(filterParameters[2].split(',')[0])
            maxY = minY + int(filterParameters[0])
            minX = int(filterParameters[2].split(',')[1])
            maxX = minX + int(filterParameters[1])
            image = image[minX:maxX, minY:maxY]
        except:
            image = backupImage

    elif filterName == 'Blur':

        image = cv2.blur(image, (int(filterParameters[0]), int(filterParameters[1])))

    elif filterName == 'Gaussian':

        try:
            image = cv2.GaussianBlur(image, (int(filterParameters[0]), int(filterParameters[1])), int(filterParameters[2].split(',')[0]), int(filterParameters[2].split(',')[1]))
        except:
            image = backupImage

    elif filterName == 'Brightness':

        maxValue = np.max(image)
        phi = float(filterParameters[0])/100
        theta = float(filterParameters[1])/100
        degree = float(filterParameters[2])
        image = image.astype(np.float_)
        image = maxValue*(1+theta)*(image/maxValue/(1-phi))**(1/degree)
        image[image > 255] = 255
        image[image < 0] = 0
        image = image.astype(np.uint8)

    elif filterName == 'Darkness':

        maxValue = np.max(image)
        phi = float(filterParameters[0])/100
        theta = float(filterParameters[1])/100
        degree = float(filterParameters[2])
        image = image.astype(np.float_)
        image = maxValue*(1-theta)*(image/maxValue/(1+phi))**(degree)
        image[image > 255] = 255
        image[image < 0] = 0
        image = image.astype(np.uint8)

    elif filterName == 'Contrast':

        maxValue = np.max(image)
        phi = float(filterParameters[0])/100
        theta = float(filterParameters[1])/100
        degree = float(filterParameters[2])
        medium = (float(maxValue)+np.min(image))/2
        image = image.astype(np.float_)
        image[image > medium] = medium*(1+theta)*(image[image > medium]/medium/(1-phi))**(1/degree)
        image[image < medium] = medium*(1-theta)*(image[image < medium]/medium/(1+phi))**(degree)
        image[image > 255] = 255
        image[image < 0] = 0
        image = image.astype(np.uint8)

    return image

def saveOpenFilter(filePath, filterList=None):

    filterFileName = '/filter.dat'
    if filterList is None: #we want to open the filterFileName file
        filterList = getData.testReadFile(filePath+filterFileName)
        return filterList
    else:
        np.savetxt(filePath+filterFileName, np.array(filterList), fmt="%s")


class matplotlibWidget(FigureCanvas):  #widget to plot image and points inside the dialog and not on a separate window

    def __init__(self):
        super(matplotlibWidget,self).__init__(matplotlib.figure.Figure())
        self.figure = matplotlib.figure.Figure()
        self.figure.set_facecolor('none')
        self.canvas = FigureCanvas(self.figure)
        self.plot = self.figure.add_subplot(111)
        #self.figure.tight_layout()
