# -*- coding: utf-8 -*-
"""
Created on 19/07/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file manages the filter widget available in the grid creation tool
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np, cv2
from functions import DIC_Global, filterFunctions, getData

class filterCreationWidget(QWidget): # contains the main filter informations and allow user to apply filter to the set of images

    def __init__(self, parent):

        super(filterCreationWidget, self).__init__()

        self.parent = parent

        verticalLayout = QVBoxLayout()
        verticalLayout.setAlignment(Qt.AlignCenter)
        verticalLayout.setContentsMargins(0,0,0,0)

        self.filterListLbl = QLabel('Filters')

        self.availableFilters = QListWidget()

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
            filterParameterValueLayout.addWidget(values)
        filterParameterLayout.addLayout(filterParameterLblLayout)
        filterParameterLayout.addLayout(filterParameterValueLayout)

        saveButtonLayout = QHBoxLayout()
        saveButtonLayout.setContentsMargins(0,0,0,0)
        self.previewButton = QToolButton()
        self.previewButton.setText('Preview')
        self.previewButton.setDisabled(True)
        self.previewButton.mousePressEvent = lambda x: self.parent.plotImage(filterPreview=[self.availableFilters.currentItem().text(), self.parameterValues[0].value(), self.parameterValues[1].value(), self.parameterValues[2].text()])
        self.previewButton.mouseReleaseEvent = lambda x: self.parent.plotImage()
        self.saveButton = QToolButton()
        self.saveButton.setText('Apply Filter')
        self.saveButton.setDisabled(True)
        self.saveButton.clicked.connect(self.addFilterToApply)
        saveButtonLayout.addStretch(1)
        saveButtonLayout.addWidget(self.previewButton)
        saveButtonLayout.addWidget(self.saveButton)
        saveButtonLayout.addStretch(1)

        self.appliedFiltersLbl = QLabel('Applied Filter(s)')

        self.appliedFilters = QListWidget()
        self.appliedFiltersList = []

        deleteButtonLayout = QHBoxLayout()
        deleteButtonLayout.setContentsMargins(0,0,0,0)
        self.deleteButton = QToolButton()
        self.deleteButton.setText('Delete Selection')
        self.deleteButton.setContentsMargins(0,0,0,0)
        self.deleteButton.setDisabled(True)
        self.deleteButton.clicked.connect(self.deleteAppliedFilter)
        deleteButtonLayout.addStretch(1)
        deleteButtonLayout.addWidget(self.deleteButton)
        deleteButtonLayout.addStretch(1)

        self.histoPlot = DIC_Global.matplotlibWidget()

        verticalLayout.addWidget(self.filterListLbl)
        verticalLayout.addWidget(self.availableFilters)
        verticalLayout.addLayout(filterParameterLayout)
        verticalLayout.addLayout(saveButtonLayout)
        verticalLayout.addWidget(self.appliedFiltersLbl)
        verticalLayout.addWidget(self.appliedFilters)
        verticalLayout.addLayout(deleteButtonLayout)
        verticalLayout.addWidget(self.histoPlot)

        self.setLayout(verticalLayout)

    def resizeCall(self):

        maxWidth = self.parent.parentWindow.width()
        maxHeight = self.parent.parentWindow.height()
        self.setContentsMargins(0.01*maxWidth,0,0.01*maxWidth,0.05*maxHeight)
        self.setFixedHeight(0.75*maxHeight)
        self.setFixedWidth(0.25*maxWidth)
        self.filterListLbl.setFixedHeight(.03*maxHeight)
        self.availableFilters.setFixedHeight(.1*maxHeight)
        self.appliedFiltersLbl.setFixedHeight(.03*maxHeight)
        self.appliedFilters.setFixedHeight(.1*maxHeight)
        self.histoPlot.setFixedHeight(.15*maxHeight)

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
