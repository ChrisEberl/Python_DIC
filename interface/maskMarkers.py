# -*- coding: utf-8 -*-
"""
Created on 15/08/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file manages mask marker feature dialog
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np, cv2, copy, matplotlib.patches as mpp
from functions import filterFunctions, masks, DIC_Global
from interface import progressWidget

class deleteMarkersDialog(QDialog):

    def __init__(self, parent, currentImage): #create the layout of the window dialog

        QDialog.__init__(self)

        self.setWindowTitle('Mask markers')
        self.setMinimumWidth(500)
        dialogLayout = QVBoxLayout()

        #init_Variables
        self.parentWidget = parent
        self.fileDataPath = parent.parentWindow.fileDataPath
        self.filePath = parent.parentWindow.filePath
        self.filenamelist = parent.fileNameList
        self.filterList = parent.filterList
        self.currentMask = copy.deepcopy(parent.currentMask)
        self.activeImages = parent.activeImages
        self.activeMarkers = parent.activeMarkers
        self.activeInstances = parent.activeInstances
        self.gridInstances = parent.grid_instances
        self.data_x = parent.data_x
        self.data_y = parent.data_y
        self.disp_x = parent.disp_x
        self.disp_y = parent.disp_y
        self.graphDisplay = 99 #temporary toolbar fix

        dialogLabel = QLabel('Select markers you want to mask.<br>A first click initiate the selection, a second click confirms the selection. (Type C to cancel)')
        dialogLabel.setAlignment(Qt.AlignHCenter)
        dialogLabel.setMinimumHeight(30)

        checkBoxOptions = QHBoxLayout()
        checkBoxOptions.setAlignment(Qt.AlignHCenter)
        checkBoxOptions.setSpacing(10)
        self.baseMarkers = QCheckBox('Base Grid Markers')
        self.baseMarkers.setChecked(True)
        self.dispMarkers = QCheckBox('Displacement Arrows')
        checkBoxOptions.addWidget(self.baseMarkers)
        checkBoxOptions.addWidget(self.dispMarkers)

        #checkBox clicked
        self.baseMarkers.stateChanged.connect(lambda: self.selectMarkers())
        self.dispMarkers.stateChanged.connect(lambda: self.selectMarkers())

        self.plotArea = DIC_Global.matplotlibWidget(self, parent=self, toolbar=1) #toolbar != None for horizontal toolbar
        self.plotArea.setMinimumHeight(self.plotArea.canvas.height())
        self.plotArea.canvas.setFocusPolicy(Qt.ClickFocus)
        self.plotArea.canvas.setFocus()

        deleteButtonBox = QHBoxLayout()
        deleteButton = QPushButton('Delete Selection')
        deleteButton.setMinimumWidth(120)
        deleteButton.clicked.connect(self.maskSelection)
        self.imageSelectSpinBox = QSpinBox(self)
        self.imageSelectSpinBox.setRange(1, len(self.activeImages))
        self.imageSelectSpinBox.setValue(currentImage)
        self.imageSelectSpinBox.valueChanged.connect(lambda: self.selectMarkers())
        self.allImagesCheckBox = QCheckBox('Apply on all images.')
        self.allImagesCheckBox.setChecked(True)

        deleteButtonBox.addStretch(1)
        deleteButtonBox.addWidget(deleteButton)
        deleteButtonBox.addWidget(self.imageSelectSpinBox)
        deleteButtonBox.addWidget(self.allImagesCheckBox)
        deleteButtonBox.addStretch(1)

        #Dialog Window Layout
        dialogLayout.addWidget(dialogLabel)
        dialogLayout.addLayout(checkBoxOptions)
        dialogLayout.addWidget(self.plotArea)
        dialogLayout.addLayout(deleteButtonBox)

        self.setLayout(dialogLayout)

        #init Plot
        self.unselectedMarkersPlot = []
        self.selectedMarkersPlot = []
        self.arrowsPlot = []
        self.selectMarkers(firstStart=1)

    def selectMarkers(self, firstStart=0):

        self.firstClic = 0
        self.plotArea.canvas.mpl_connect('button_release_event', self.on_release)
        self.plotArea.canvas.mpl_connect('key_press_event', self.on_key)

        value = self.activeImages[self.imageSelectSpinBox.value()-1]
        readImage = cv2.imread(self.filePath+'/'+self.filenamelist[value],0)
        readImage = filterFunctions.applyFilterListToImage(self.filterList, readImage)

        data_x_init = self.data_x[:, self.activeImages[0]]
        data_y_init = self.data_y[:, self.activeImages[0]]
        disp_x_init = self.disp_x[:, self.activeImages[value]]
        disp_y_init = self.disp_y[:, self.activeImages[value]]
        markerSelection = self.currentMask[:, value]

        nbInstances = len(np.atleast_1d(self.activeInstances))
        for instance in range(nbInstances):
            #instanceMarkers = [marker for marker in self.gridInstances[self.activeInstances[instance]] if marker in self.activeMarkers[value]]
            instanceMarkers = np.intersect1d(self.gridInstances[self.activeInstances[instance]], self.activeMarkers[value], assume_unique=True)
            selectedMarkers = [marker for marker in instanceMarkers if markerSelection[marker] == 0]
            unSelectedMarkers = [marker for marker in instanceMarkers if marker not in selectedMarkers]
            try:
                self.unselectedMarkersPlot[instance].remove()
            except:
                pass
            try:
                self.selectedMarkersPlot[instance].remove()
            except:
                pass

            if self.baseMarkers.isChecked():
                try:
                    self.selectedMarkersPlot[instance] = self.plotArea.matPlot.plot(data_x_init[unSelectedMarkers], data_y_init[unSelectedMarkers], 'o', ms=5, color='green')[0]
                except:
                    self.selectedMarkersPlot.append(self.plotArea.matPlot.plot(data_x_init[unSelectedMarkers], data_y_init[unSelectedMarkers], 'o', ms=3, color='green')[0])

            if self.dispMarkers.isChecked():
                nb = 0
                nbUnselected = len(np.atleast_1d(unSelectedMarkers))
                if len(np.atleast_1d(self.arrowsPlot)) < instance+1:
                    self.arrowsPlot.append([])
                for marker in unSelectedMarkers:
                    try:
                        self.arrowsPlot[instance][nb].remove()
                        self.arrowsPlot[instance][nb] = self.plotArea.matPlot.arrow(data_x_init[marker], data_y_init[marker], disp_x_init[marker], disp_y_init[marker], head_width=3, head_length=7, color='blue')
                    except:
                        if len(np.atleast_1d(self.arrowsPlot[instance])) < nbUnselected:
                            self.arrowsPlot[instance].append(self.plotArea.matPlot.arrow(data_x_init[marker], data_y_init[marker], disp_x_init[marker], disp_y_init[marker], head_width=3, head_length=7, color='blue'))
                        else:
                            self.arrowsPlot[instance][nb] = self.plotArea.matPlot.arrow(data_x_init[marker], data_y_init[marker], disp_x_init[marker], disp_y_init[marker], head_width=3, head_length=7, color='blue')
                    nb+=1
            else:
                try:
                    for element in self.arrowsPlot[instance]:
                        element.remove()
                except:
                    pass

                try:
                    self.unselectedMarkersPlot[instance] = self.plotArea.matPlot.plot(data_x_init[selectedMarkers], data_y_init[selectedMarkers], 'o', ms=5, color='red')[0]
                except:
                    self.unselectedMarkersPlot.append(self.plotArea.matPlot.plot(data_x_init[selectedMarkers], data_y_init[selectedMarkers], 'o', ms=5, color='red')[0])


        self.imagePlot = self.plotArea.matPlot.imshow(readImage, cmap='gray')
        self.plotArea.canvas.draw_idle()

        if firstStart == 1:
            self.plotArea.matPlot.cla()
            self.selectMarkers()

    def on_motion(self,event): #allow a live drawing of the rectangle area

        x1 = event.xdata
        y1 = event.ydata
        if x1 is None:
            x1 = self.x2
        if y1 is None:
            y1 = self.y2
        self.x2 = x1
        self.y2 = y1
        width = x1 - self.x0
        height = y1 - self.y0
        self.rect.set_width(width)
        self.rect.set_height(height)
        #self.rect.set_xy((self.x0, self.y0))
        self.rect.set_linestyle('dashed')
        self.plotArea.canvas.draw_idle()

    def on_release(self, event):
        if self.plotArea.toolbar._active is None: #if toolbar is not active
            if self.firstClic == 0:
                self.x0 = event.xdata
                self.y0 = event.ydata
                if self.x0 is None:
                    return
                self.x2 = self.x0 #save coordinates in case the user goes out of the picture limits
                self.y2 = self.y0
                self.rect = mpp.Rectangle((self.x0, self.y0), 1, 1, facecolor='None', edgecolor='green', linewidth=2.5)
                self.plotArea.matPlot.add_patch(self.rect)
                self.motionRect = self.plotArea.canvas.mpl_connect('motion_notify_event', self.on_motion)
                self.rect.set_linestyle('dashed')
                self.firstClic = 1
            else:
                x1 = event.xdata
                y1 = event.ydata
                if self.x0 is None:
                    return
                self.plotArea.canvas.mpl_disconnect(self.motionRect)
                if x1 is None:
                    x1 = self.x2
                if y1 is None:
                    y1 = self.y2
                self.selectRectangleMarkers(self.x0, self.y0, x1 - self.x0, y1 - self.y0)
                self.rect.remove()

    def on_key(self, event):
        #print('you pressed', event.key, event.xdata, event.ydata)
        isValidEvent = False
        if event.key == 'd':
            value = self.activeImages[self.imageSelectSpinBox.value()-1]
            markerSelection = self.currentMask[:, value]

            nbInstances = len(np.atleast_1d(self.activeInstances))
            for instance in range(nbInstances):
                #instanceMarkers = [marker for marker in self.gridInstances[self.activeInstances[instance]] if marker in self.activeMarkers[value]]
                instanceMarkers = np.intersect1d(self.gridInstances[self.activeInstances[instance]], self.activeMarkers[value], assume_unique=True)
                for i in instanceMarkers:
                    if markerSelection[i] == 0:
                        self.currentMask[i,:] = 1
            isValidEvent = True
        if event.key == 'c' and self.firstClic == 1:
            self.plotArea.canvas.mpl_disconnect(self.motionRect)
            self.rect.remove()
            isValidEvent = True
        if event.key == 'r':
            self.plotArea.matPlot.cla()
            isValidEvent = True

        if isValidEvent is True:
            self.selectMarkers()

    def selectRectangleMarkers(self, x0, y0, width, height): #when an area is selected, select all the markers inside

        value = self.activeImages[self.imageSelectSpinBox.value()-1]
        if x0 is None:
            return
        markerSelection = self.currentMask[:, value]
        data_x_current = self.data_x[:, value]
        data_y_current = self.data_y[:, value]

        nbInstances = len(np.atleast_1d(self.activeInstances))
        for instance in range(nbInstances):
            #instanceMarkers = [marker for marker in self.gridInstances[self.activeInstances[instance]] if marker in self.activeMarkers[value]]
            instanceMarkers = np.intersect1d(self.gridInstances[self.activeInstances[instance]], self.activeMarkers[value], assume_unique=True)
            for i in instanceMarkers:
                if data_x_current[i] > min(x0, x0+width) and data_x_current[i] < max(x0, x0+width) and data_y_current[i] > min(y0, y0+height) and data_y_current[i] < max(y0, y0+height):
                    if markerSelection[i] == 1:
                        if self.allImagesCheckBox.isChecked():
                            self.currentMask[i, :] = 0
                        else:
                            self.currentMask[i, value] = 0
                    else:
                        if self.allImagesCheckBox.isChecked():
                            self.currentMask[i, :] = 1
                        else:
                            self.currentMask[i, value] = 1

        self.selectMarkers() #refresh the canvas which selected markers

    def maskSelection(self): #when the selection is done and 'Delete' button clicked, remove all selected markers on all images

        shouldApplyMask = masks.generateMask(self.currentMask, self.fileDataPath)
        if shouldApplyMask is not None:
            self.parentWidget.parentWindow.devWindow.addInfo('Deleting selected markers..')
            progressBar = progressWidget.progressBarDialog('Saving masks..')
            masks.maskData(self.parentWidget, self.currentMask, progressBar, toRecalculate=shouldApplyMask)
            self.close()

def launchMaskDialog(self, currentImage): #initialize the variable and execute the window dialog

    self.analysisWidget.parentWindow.devWindow.addInfo('Cleaning Procedure Request : Mask Markers.')
    deleteMarkers = deleteMarkersDialog(self.analysisWidget, currentImage)
    deleteMarkers.exec_()
