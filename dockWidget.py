# -*- coding: utf-8 -*-
"""
Created on 08/08/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file manages the movable and closable dockWidgets displaying 2D and 3D plots
"""

from PySide.QtCore import *
from PySide.QtGui import *
import numpy as np
import plot3D
import plot2D
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import filterWidget
import cv2



class dockPlot(QDockWidget): #dockWidget containing a Matplotlib Widget
    
    instances = [] #will contain the class instances
    maximumSize = 10
        
    def __init__(self, title, graphType, graphDisplay, parentWindow):
        
        super(dockPlot, self).__init__()    
        
        if graphDisplay == 0:
            self.scatter = 0
            self.projection = [False,False]
        if graphDisplay == 5:
            self.averageImageNb = 1
        self.graphDisplay = graphDisplay
        self.parentWindow = parentWindow
        self.parentWindow.setTabPosition(Qt.LeftDockWidgetArea, QTabWidget.West)
        self.parentWindow.setTabPosition(Qt.RightDockWidgetArea, QTabWidget.East)
        
        self.setWindowTitle(title)
        self.setAllowedAreas(Qt.TopDockWidgetArea | Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea) #bottom is reserved for DevMode
        self.dockWidget = matplotlibWidget(graphType, self) #init 3d plot
        self.setWidget(self.dockWidget)
        self.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable) #do not allow floatable widget  
        dockPlot.instances.append(self) #add the new instance to the list
        

    def resizeEvent(self, QResizeEvent=0): #called everytime the widget is changing his size
        
        left = 1
        right = 1
        top = 0
        for instance in dockPlot.instances:
            if instance.visibleRegion().isEmpty() == False:
                area = self.parentWindow.dockWidgetArea(instance)
                if area == Qt.TopDockWidgetArea:
                    top += 1
                elif area == Qt.LeftDockWidgetArea:
                    left += 1
                elif area == Qt.RightDockWidgetArea:
                    right += 1
            
        widthWindow = self.parentWindow.width() #get the dimension of the whole window
        heightWindow = self.parentWindow.height()-self.parentWindow.menubar.height()-self.parentWindow.statusBar().height()-self.parentWindow.analysisWidget.controlWidget.height()
        
        if top < 1:
            top = 1
        dockPlot.maximumSize = min(widthWindow/top, heightWindow/left, heightWindow/right)


        for instance in dockPlot.instances: #set the boundaries of each widget
            instance.dockWidget.setMinimumHeight(dockPlot.maximumSize*.9)
            instance.dockWidget.setMinimumWidth(dockPlot.maximumSize*.9)
            
        figSize = self.dockWidget.figure.get_size_inches()
        dpi = self.dockWidget.figure.get_dpi()
        width = figSize[0]*dpi
        height = figSize[1]*dpi
        if np.isfinite(width) and np.isfinite(height):
            size = QSize(width, height)
            self.dockWidget.canvas.resize(size)
            self.dockWidget.canvas.draw_idle()
            
            
    def moveEvent(self, QMoveEvent): #when the user move a dockWidget, temporary reduce the minimumSize of widgets
    
        for instance in dockPlot.instances:
           instance.dockWidget.setMinimumHeight(dockPlot.maximumSize*.5)
           instance.dockWidget.setMinimumWidth(dockPlot.maximumSize*.5)
        
                
    def updatePlot(self, data_x, data_y, z_axis = None):
        
        activeInstances = self.parentWindow.analysisWidget.activeInstances
        currentImage = int(self.parentWindow.analysisWidget.controlWidget.imageNumber.text())
        realImage = self.parentWindow.analysisWidget.activeImages[currentImage-1]
        if self.visibleRegion().isEmpty() == False: #plot only if visible by the user
            if self.graphDisplay == 0: # 3D PLOT
                plot3D.update3D_subplot(self.dockWidget.plot, data_x, data_y, z_axis, self.scatter, self.projection)
            elif self.graphDisplay == 1: # DISPLACEMENT/DEVIATION 2D
                image = cv2.imread(self.parentWindow.filePath + '/' + str(self.parentWindow.analysisWidget.fileNameList[realImage]),0)
                filterList = self.parentWindow.analysisWidget.filterList
                if filterList is not None and image is not None:
                    image = filterWidget.applyFilterListToImage(filterList, image)
                plot2D.update2D_displacementDeviation(self.dockWidget.plot, data_x, data_y, image)   
            elif self.graphDisplay == 2: # CORRELATION 2D
                plot2D.update2D_correlation(self, self.dockWidget.figure, self.dockWidget.plot, data_x)
            elif self.graphDisplay == 3: # STRAIN 1D
                plot2D.update2D_strain(self, self.dockWidget.plot, data_x, data_y, z_axis)
            elif self.graphDisplay == 4: # STRAIN 2D
                plot2D.update2D_strain(self, self.dockWidget.plot, data_x, data_y, self.dockWidget.figure)
            elif self.graphDisplay == 5: # TRUE STRAIN 1D
                plot2D.plot_TrueStrain(self, self.dockWidget.plot, [data_x, self.averageImageNb, activeInstances])
            self.dockWidget.canvas.draw_idle()
            

class matplotlibToolbar(NavigationToolbar):
    
    def __init__(self, canvas, parent, plotType=None):

        self.parent = parent
        if plotType is not None:
            self.toolitems = [('Save', 'Save the figure', 'filesave', 'save_figure'),('Parameters', 'Change plot parameters.', 'hand', 'changeParams')]
        else:
            self.toolitems = (('Home', 'Reset original view', 'home', 'home'),('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),('Save', 'Save the figure', 'filesave', 'save_figure'),('Parameters', 'Change plot parameters.', 'hand', 'changeParams'))
        
        super(matplotlibToolbar, self).__init__(canvas, parent)
        self.setOrientation(Qt.Vertical)
        if plotType is not None:
            self.layout().takeAt(2)
        else:
            self.layout().takeAt(5)
            
    def changeParams(self):
        
        graphDisplay = self.parent.parentWidget.graphDisplay
        parametersDialog = dockParameters(self.parent, graphDisplay)
        
        parametersDialog.exec_()
        

class dockParameters(QDialog):
    
    def __init__(self, dockWidget, graphDisplay):
        
        QDialog.__init__(self)
        
        self.setWindowTitle('Dock Parameters')
        self.setMinimumWidth(300)
        self.dockWidget = dockWidget
        
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setAlignment(Qt.AlignCenter)
        
        if graphDisplay == 0:
            self.plots3D()
        elif graphDisplay == 2:
            self.correlation2D()
        elif graphDisplay == 4:
            self.strain2D()
        elif graphDisplay == 5:
            self.trueStrain()
        else:
            inDev = QLabel('Currently in development.')
            self.mainLayout.addWidget(inDev)
        
        self.setLayout(self.mainLayout)
        
    def plots3D(self):
        
        dataDisplayGroup = QGroupBox('Data Display')
        
        dataDisplayLayout = QVBoxLayout()        
        
        formatLayout = QHBoxLayout()
        formatLayout.setAlignment(Qt.AlignCenter)
        displayLbl = QLabel('Plot Format:')
        displayCombo = QComboBox()
        displayCombo.setMaximumWidth(80)
        displayCombo.addItem('Surface')
        displayCombo.addItem('Scatter')
        displayCombo.setCurrentIndex(self.dockWidget.parentWidget.scatter)
        formatLayout.addWidget(displayLbl)
        formatLayout.addWidget(displayCombo)
        
        projectionLayout = QHBoxLayout()
        projectionLayout.setAlignment(Qt.AlignCenter)
        projectionLbl = QLabel('Projections on axes: ')
        xLbl = QLabel('X')
        projectionXBox = QCheckBox()
        if self.dockWidget.parentWidget.projection[0]:
            projectionXBox.setChecked(True)
        yLbl = QLabel('Y')
        projectionYBox = QCheckBox()
        if self.dockWidget.parentWidget.projection[1]:
            projectionYBox.setChecked(True)
        projectionLayout.addWidget(projectionLbl)
        projectionLayout.addWidget(projectionXBox)
        projectionLayout.addWidget(xLbl)
        projectionLayout.addWidget(projectionYBox)
        projectionLayout.addWidget(yLbl)
        
        dataDisplayLayout.addLayout(formatLayout)
        dataDisplayLayout.addLayout(projectionLayout)
        dataDisplayGroup.setLayout(dataDisplayLayout)
        
        saveLayout = QHBoxLayout()
        saveButton = QPushButton('Save')
        saveButton.setMaximumWidth(60)
        saveButton.clicked.connect(lambda: self.plots3D_save(displayCombo.currentIndex(), [projectionXBox.isChecked(),projectionYBox.isChecked()]))
        saveLayout.addStretch(1)
        saveLayout.addWidget(saveButton)
        saveLayout.addStretch(1)
        
        self.mainLayout.addWidget(dataDisplayGroup)
        self.mainLayout.addLayout(saveLayout)
    
    def plots3D_save(self, plotFormat, projection):
        
        self.dockWidget.parentWidget.scatter = plotFormat
        self.dockWidget.parentWidget.projection = projection
        imageNb = int(self.dockWidget.parentWidget.parentWindow.analysisWidget.controlWidget.imageNumber.text())
        self.dockWidget.parentWidget.parentWindow.analysisWidget.resultAnalysis.graphRefresh(imageValue=imageNb-1)
        self.close()
        
        
    def strain2D(self):
        
        colorbarGroup = QGroupBox('Colorbar')
        
        colorbarLayout = QVBoxLayout()
        colorbarLayout.setAlignment(Qt.AlignCenter)
        
        colorbarLow = QHBoxLayout()
        colorbarLowLbl = QLabel('Lower limit:')
        colorbarLowEdit = QLineEdit()
        colorbarLowEdit.setAlignment(Qt.AlignCenter)
        colorbarLowEdit.setMaximumWidth(80)
        currentLowValue = self.dockWidget.plot.cbar.get_clim()[0]
        colorbarLowEdit.setText(str(currentLowValue))
        colorbarLow.addWidget(colorbarLowLbl)
        colorbarLow.addWidget(colorbarLowEdit)
        
        colorbarHigh = QHBoxLayout()
        colorbarHighLbl = QLabel('Higher limit:')
        colorbarHighEdit = QLineEdit()
        colorbarHighEdit.setAlignment(Qt.AlignCenter)
        colorbarHighEdit.setMaximumWidth(80)
        currentHighValue = self.dockWidget.plot.cbar.get_clim()[1]
        colorbarHighEdit.setText(str(currentHighValue))
        colorbarHigh.addWidget(colorbarHighLbl)
        colorbarHigh.addWidget(colorbarHighEdit)
        
        colorbarLayout.addLayout(colorbarLow)
        colorbarLayout.addLayout(colorbarHigh)
        colorbarGroup.setLayout(colorbarLayout)
        
        saveLayout = QHBoxLayout()
        saveButton = QPushButton('Save')
        saveButton.setMaximumWidth(60)
        saveButton.clicked.connect(lambda: self.strain2D_save(colorbarLowEdit.text(),colorbarHighEdit.text()))
        saveLayout.addStretch(1)
        saveLayout.addWidget(saveButton)
        saveLayout.addStretch(1)
        
        self.mainLayout.addWidget(colorbarGroup)
        self.mainLayout.addLayout(saveLayout)
        
        
    def strain2D_save(self, lowLimit, highLimit):
        
        if lowLimit <> '' and highLimit <> '':
            lowLimit = lowLimit.replace(',','.')
            highLimit = highLimit.replace(',','.')
            lowLimit = float(lowLimit)
            highLimit = float(highLimit)
            num_ticks = 11
            ticks = np.linspace(-0.1, 0.1, num_ticks)
            if lowLimit < highLimit:
                labels = np.linspace(lowLimit, highLimit, num_ticks)
                self.dockWidget.plot.cbar.set_clim(vmin=lowLimit,vmax=highLimit)
            else:
                labels = np.linspace(highLimit, lowLimit, num_ticks)
                self.dockWidget.plot.cbar.set_clim(vmin=highLimit,vmax=lowLimit)
            self.dockWidget.plot.cbar.set_ticks(ticks)
            self.dockWidget.plot.cbar.set_ticklabels(labels)
            self.dockWidget.parentWidget.parentWindow.devWindow.addInfo('New colorbar limits.')
        
        imageNb = int(self.dockWidget.parentWidget.parentWindow.analysisWidget.controlWidget.imageNumber.text())
        self.dockWidget.parentWidget.parentWindow.analysisWidget.resultAnalysis.graphRefresh(imageValue=imageNb-1)
        self.close()
    

    def correlation2D(self):
        
        colorbarGroup = QGroupBox('Colorbar')
        
        colorbarLayout = QHBoxLayout()
        colorbarLayout.setAlignment(Qt.AlignCenter)
        colorbarLbl = QLabel('Lower limit:')
        colorbarEdit = QLineEdit()
        colorbarEdit.setAlignment(Qt.AlignCenter)
        colorbarEdit.setMaximumWidth(80)
        currentValue = self.dockWidget.plot.cbar.get_clim()[0]
        if currentValue < 0:
            currentValue = 0
        colorbarEdit.setText(str(currentValue))
        colorbarLayout.addWidget(colorbarLbl)
        colorbarLayout.addWidget(colorbarEdit)
        colorbarGroup.setLayout(colorbarLayout)
        
        saveLayout = QHBoxLayout()
        saveButton = QPushButton('Save')
        saveButton.setMaximumWidth(60)
        saveButton.clicked.connect(lambda: self.correlation2D_save(colorbarEdit.text()))
        saveLayout.addStretch(1)
        saveLayout.addWidget(saveButton)
        saveLayout.addStretch(1)
        
        self.mainLayout.addWidget(colorbarGroup)
        self.mainLayout.addLayout(saveLayout)
        
    def correlation2D_save(self, lowLimit):
        
        if lowLimit <> '':
            lowLimit = lowLimit.replace(',','.')
            lowLimit = float(lowLimit)
            if lowLimit < 0 or lowLimit >= 1:
                errorMessage = QMessageBox()
                errorMessage.setWindowTitle('Error')
                errorMessage.setText('Wrong colorbar limit. ('+str(lowLimit)+')')
                errorMessage.exec_()
                return
            num_ticks = 11
            labels = np.linspace(lowLimit, 1, num_ticks)
            ticks = np.linspace(-0.1, 0.1, num_ticks)
            self.dockWidget.plot.cbar.set_clim(vmin=lowLimit,vmax=1)
            self.dockWidget.plot.cbar.set_ticks(ticks)
            self.dockWidget.plot.cbar.set_ticklabels(labels)
            self.dockWidget.parentWidget.parentWindow.devWindow.addInfo('New colorbar limits.')
        
        imageNb = int(self.dockWidget.parentWidget.parentWindow.analysisWidget.controlWidget.imageNumber.text())
        self.dockWidget.parentWidget.parentWindow.analysisWidget.resultAnalysis.graphRefresh(imageValue=imageNb-1)
        self.close()
        
    def trueStrain(self):
        
        averagingGroup = QGroupBox('Averaging')
        
        averagingLayout = QHBoxLayout()
        averagingLayout.setAlignment(Qt.AlignCenter)
        averagingLbl = QLabel('Average strain over')
        averagingValue = QSpinBox()
        totalActiveImages = len(np.atleast_1d(self.dockWidget.parentWidget.parentWindow.analysisWidget.activeImages))
        averagingValue.setRange(1,totalActiveImages)
        averagingValue.setValue(self.dockWidget.parentWidget.averageImageNb)
        averagingLbl2 = QLabel('images.')
        averagingLayout.addWidget(averagingLbl)
        averagingLayout.addWidget(averagingValue)
        averagingLayout.addWidget(averagingLbl2)
        averagingGroup.setLayout(averagingLayout)
        
        saveLayout = QHBoxLayout()
        saveButton = QPushButton('Save')
        saveButton.setMaximumWidth(60)
        saveButton.clicked.connect(lambda: self.trueStrain_save(averagingValue.value()))
        saveLayout.addStretch(1)
        saveLayout.addWidget(saveButton)
        saveLayout.addStretch(1)
        
        self.mainLayout.addWidget(averagingGroup)
        self.mainLayout.addLayout(saveLayout)
        
    def trueStrain_save(self, value):
        
        self.dockWidget.parentWidget.averageImageNb = value
        imageNb = int(self.dockWidget.parentWidget.parentWindow.analysisWidget.controlWidget.imageNumber.text())
        self.dockWidget.parentWidget.parentWindow.analysisWidget.resultAnalysis.graphRefresh(imageValue=imageNb-1)
        self.close()
        

class matplotlibWidget(FigureCanvas):
    
    def __init__(self, graphType, parentWidget):
        
        self.figure = Figure()
        self.parentWidget = parentWidget
        self.graphType = graphType
        super(matplotlibWidget,self).__init__(self.figure)
        
        self.figure.set_facecolor('none')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)
        
        #initialize the plot
        if graphType == 1: #3D plots
            self.plot = self.figure.add_subplot(111, projection='3d')
            self.figure.subplots_adjust(left=0.05, right=1, top=1.1, bottom=0)
            self.toolbar = matplotlibToolbar(self.canvas, self, plotType='3d')
        else: #2D plots
            self.plot = self.figure.add_subplot(111)
            self.figure.subplots_adjust(left=0.15, right=0.85, top=0.95, bottom=0.1)
            self.plot.tick_params(labelsize=9)
            self.plot.locator_params(nbins=6)
            self.toolbar = matplotlibToolbar(self.canvas, self)
                    
        self.plot.patch.set_facecolor('none')