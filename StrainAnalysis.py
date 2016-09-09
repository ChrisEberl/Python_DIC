#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 08/03/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file runs the Main Analysis widget, parent of the whole visualization tool
"""

import menubar
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import getData
import initData
import progressWidget
import masks
import controlWidget

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.mlab as ml
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib import cm

import numpy as np

class MainAnalysis(QWidget):

    def __init__(self, parentWindow):

        QWidget.__init__(self)

        self.parentWindow = parentWindow
        self.parentWindow.devWindow.addInfo('Visualisation Widget started. Ready to load the data. Setting up the layout.')

        #Layout parameters
        self.mainLayout = QHBoxLayout()
        #self.mainLayout.setAlignment(Qt.AlignVCenter)
        self.mainLayout.setAlignment(Qt.AlignHCenter)

        #Creation of the temporary progressBar
        self.openingBar = progressWidget.progressBarWidget(maximumWidth=250, minimumHeight=30)
        self.mainLayout.addWidget(self.openingBar)
        self.setLayout(self.mainLayout)

        self.parentWindow.devWindow.addInfo('Starting the thread.. Analysis Loading..')

        #initiate and start the opening thread
        self.openingThread = self.parentWindow.createThread([self.parentWindow, self.openingBar], getData.openData, signal=1)
        self.openingThread.signal.threadSignal.connect(self.dataLoaded)
        self.openingThread.start()

    def dataLoaded(self, variables):


        #remove the progressBar
        self.mainLayout.removeWidget(self.openingBar)
        self.openingBar.deleteLater()
        self.openingBar = None

        if len(variables) > 1:
            self.data_x = variables[0]
            self.data_y = variables[1]
            self.data_corr = variables[2]
            self.data_stdx = variables[3]
            self.data_stdy = variables[4]
            self.disp_x = variables[5]
            self.disp_y = variables[6]
            self.fileNameList = variables[7]
            self.nb_marker = variables[8]
            self.nb_image = variables[9]
            self.filterList = variables[10] #contains None when no filter
            self.grid_instances = variables[11] #list of markers per instance : [[1,2,3],[4,5,6]] => Markers 1,2,3 in grid 1, markers 4,5,6 in grid 2
            self.largeDisp = variables[12] #contains None when no largeDisp
            self.activeImages = []
            nbInstances = len(np.atleast_1d(self.grid_instances))
            self.activeInstances = np.linspace(0, nbInstances, num=nbInstances, endpoint=False, dtype=np.int)
            self.activeMarkers = [] #list of active markers in each image : [[1,2,3],[2,3,4]] => Markers 1,2,3 are active in image 1, markers 2,3,4 are active in image 2
            self.xLimit = [0,1]
            self.yLimit = [0,1]
            self.strainX_data = []
            self.strainY_data = []
            self.neighbors = None
            self.createLayout()
        else:
            self.parentWindow.homeWidget('Missing Files. Please check the documentation.')



    def createLayout(self):


        #self.layout = QVBoxLayout() #create main vertical layout
        self.mainLayout.setContentsMargins(0,0,0,0)

        #activate Menu Actions
        menubar.menuDisabled(self.parentWindow)
        menubar.menuEnabled(self.parentWindow)

        self.parentWindow.devWindow.addInfo('Menus enabled. Toolbar created. Setting-up the layout.')


        #control widget
        self.controlWidget = controlWidget.controlWidget(self)
        self.mainLayout.addStretch(1)
        self.mainLayout.addWidget(self.controlWidget)
        self.mainLayout.addStretch(1)


        self.parentWindow.devWindow.addInfo('Layout ready. Starting the visualisation.')

        self.run()


    def run(self):


        self.resultAnalysis = ResultAnalysis(self)

        self.currentMask = masks.openMask(self.parentWindow)
        initData.createPlots(self)

        #activate event for slider
        self.controlWidget.imageSelector.valueChanged.connect(self.resultAnalysis.graphRefresh)
        self.controlWidget.sliderSelector.valueChanged.connect(self.resultAnalysis.graphRefresh)

        progressBar = progressWidget.progressBarDialog('Opening processes..')

        masks.maskData(self, self.currentMask, progressBar)

        #self.controlWidget.updateAnalysisInfos()


    def changeParameters(self):

        self.new_coeff, self.ok = QInputDialog.getInt(self, 'Standard Dev.', 'Multiplication Coeff. :', value=self.m_coeff, minValue=1, step=5)
        if self.ok:
            self.m_coeff = self.new_coeff
            self.parentWindow.devWindow.addInfo('New Std. Dev. Multiplication Coeff. : '+str(self.m_coeff))

            self.parentWindow.statusBar().showMessage('Multiplication coefficient for standard deviation changed. New value : '+str(self.m_coeff))
            self.resultAnalysis.graphRefresh(self.slider.value())


class ResultAnalysis(QWidget):

    def __init__(self, parentWidget):

        self.parentWidget = parentWidget


#    @Slot()
#    def sliderChange(self, value): #called when the value of the slider change
#        tic = time.time()
#        self.graphRefresh(value)
#        toc = time.time()
#        self.parentWidget.parentWindow.statusBar().showMessage('Refreshing Time : '+str(toc-tic)+'s') #change infos label


    def graphRefresh(self, imageValue=0): #function to refresh the different 3d-plots

        activeImages = self.parentWidget.activeImages
        nbActiveImages = len(activeImages)
        
        if nbActiveImages < 1 or len(np.atleast_1d(self.parentWidget.zi)) < 1:
            return

        self.parentWidget.controlWidget.updateImageInfos(imageValue)
        value = activeImages[imageValue]

        activeMarkers = self.parentWidget.activeMarkers[value]
        activeInstances = self.parentWidget.activeInstances
        grid_instances = self.parentWidget.grid_instances

        xAxis = []
        yAxis = []
        dispX = []
        dispY = []
        dataStdX = []
        dataStdY = []
        dataCorr = []
        dataCorr2D = []
        strain2DX = []
        strain2DY = []

        nbInstances = len(np.atleast_1d(activeInstances))
        for instance in range(nbInstances):
            currentInstance = activeInstances[instance]
            instanceMarkers = np.intersect1d(grid_instances[currentInstance], activeMarkers, assume_unique=True).astype(np.int)
            xAxis.append(self.parentWidget.data_x[instanceMarkers,value])
            yAxis.append(self.parentWidget.data_y[instanceMarkers,value])
            dispX.append(self.parentWidget.disp_x[instanceMarkers,value])
            dispY.append(self.parentWidget.disp_y[instanceMarkers,value])
            dataStdX.append(self.parentWidget.data_stdx[instanceMarkers,value])
            dataStdY.append(self.parentWidget.data_stdy[instanceMarkers,value])
            dataCorr.append(self.parentWidget.data_corr[instanceMarkers,value])
            dataCorr2D.append(self.parentWidget.zi[instance][imageValue])
            strain2DX.append(self.parentWidget.zi_strainX[instance][imageValue])
            strain2DY.append(self.parentWidget.zi_strainY[instance][imageValue])


        ########################
        ###### 3D PLOTS ########
        ########################

        #3D-Displacement along X
        self.parentWidget.displacementX.updatePlot(xAxis, yAxis, z_axis=dispX)

        #3D-Displacement along Y
        self.parentWidget.displacementY.updatePlot(xAxis, yAxis, z_axis=dispY)

        #3D-Standard Deviation along X
        self.parentWidget.deviationX.updatePlot(xAxis, yAxis, z_axis=dataStdX)

        #3D-Standard Deviation along Y
        self.parentWidget.deviationY.updatePlot(xAxis, yAxis, z_axis=dataStdY)

        #3D-Correlation
        self.parentWidget.correlation.updatePlot(xAxis, yAxis, z_axis=dataCorr)

        ########################
        ###### 2D PLOTS ########
        ########################

        #2D-Displacement
        self.parentWidget.displacement2D.updatePlot(xAxis, yAxis)

        #2D-Correlation
        self.parentWidget.correlation2D.updatePlot(dataCorr2D, 0)

        #1D Local Strain along X
        self.parentWidget.strainX.updatePlot(xAxis, dispX, z_axis=[self.parentWidget.strainX_data[imageValue, :], self.parentWidget.localStrainIntersectX[imageValue,:]])

        #1D Local Strain along Y
        self.parentWidget.strainY.updatePlot(yAxis, dispY, z_axis=[self.parentWidget.strainY_data[imageValue, :], self.parentWidget.localStrainIntersectY[imageValue, :]])

        #2D Local Strain along X
        self.parentWidget.strain2DX.updatePlot(strain2DX, None)

        #2D Local Strain along Y
        self.parentWidget.strain2DY.updatePlot(strain2DY, None)

        #1D True Strain along X
        self.parentWidget.trueStrainX.updatePlot(self.parentWidget.strainX_data, 0)

        #1D True Strain along Y
        self.parentWidget.trueStrainY.updatePlot(self.parentWidget.strainY_data, 0)



#######################
### Run Application ###
#######################

def analyseResult(self, parentWindow):

    self.analysisWidget = MainAnalysis(self)

    self.setCentralWidget(self.analysisWidget)
