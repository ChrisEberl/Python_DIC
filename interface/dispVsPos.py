# -*- coding: utf-8 -*-
"""
Created on 12/04/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file manages the Disp. vs Pos. mask procedure
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np, copy, matplotlib.patches as mpp
from functions import masks, DIC_Global
from interface import progressWidget

class dispVsPosDialog(QDialog):

    def __init__(self, parent, currentImage): #initiate the main layout

        QDialog.__init__(self)
        self.parent = parent
        self.fileDataPath = parent.parentWindow.fileDataPath
        self.currentMask = copy.deepcopy(parent.currentMask)
        self.activeImages = parent.activeImages
        self.activeMarkers = parent.activeMarkers
        self.activeInstances = parent.activeInstances
        self.gridInstances = parent.grid_instances
        self.data_x = parent.data_x
        self.data_y = parent.data_y
        self.disp_x = parent.disp_x
        self.disp_y = parent.disp_y

        self.setWindowTitle('Dispersion vs Position')
        self.setMinimumWidth(500)
        dialogLayout = QVBoxLayout()

        dialogLabel = QLabel('Clean markers by linear displacement analysis. Draw rectangles over the markers you want to select.')
        dialogLabel.setAlignment(Qt.AlignHCenter)
        dialogLabel.setMinimumHeight(30)

        checkBoxOptions = QHBoxLayout()
        checkBoxOptions.setAlignment(Qt.AlignHCenter)
        checkBoxOptions.setSpacing(10)

        self.displayXMarkers = QCheckBox('Displacement along X')
        self.displayXMarkers.setChecked(True)

        self.displayYMarkers = QCheckBox('Displacement along Y')

        self.imageSelectSpinBox = QSpinBox(self)
        self.imageSelectSpinBox.setRange(1, len(np.atleast_1d(self.activeImages)))
        self.imageSelectSpinBox.setValue(currentImage)

        self.allImagesCheckBox = QCheckBox('Apply on all images.')
        self.allImagesCheckBox.setChecked(True)

        checkBoxOptions.addWidget(self.displayXMarkers)
        checkBoxOptions.addWidget(self.displayYMarkers)
        checkBoxOptions.addWidget(self.imageSelectSpinBox)
        checkBoxOptions.addWidget(self.allImagesCheckBox)

        #checkBox clicked
        self.displayXMarkers.stateChanged.connect(self.plotDispersion)
        self.displayYMarkers.stateChanged.connect(self.plotDispersion)
        self.imageSelectSpinBox.valueChanged.connect(self.plotDispersion)

        self.plotArea = DIC_Global.matplotlibWidget()
        self.plotArea.setFocusPolicy(Qt.ClickFocus)
        self.plotArea.setFocus()

        buttonBox = QHBoxLayout()

        self.deleteButton = QPushButton('Delete Selection')
        self.deleteButton.setMinimumWidth(120)
        self.deleteButton.clicked.connect(self.maskSelection)
        buttonBox.addStretch(1)
        buttonBox.addWidget(self.deleteButton)
        buttonBox.addStretch(1)

        #Dialog Window Layout
        dialogLayout.addWidget(dialogLabel)
        dialogLayout.addLayout(checkBoxOptions)
        dialogLayout.addWidget(self.plotArea)
        dialogLayout.addLayout(buttonBox)

        self.setLayout(dialogLayout)
        self.plotDispersion()

    def plotDispersion(self): #refreshing function

        value = self.activeImages[self.imageSelectSpinBox.value()-1]

        self.plotArea.matPlot.cla()
        self.plotArea.mpl_connect('button_press_event', self.on_press) #activate mouse event detection
        self.plotArea.mpl_connect('button_release_event', self.on_release)
        self.plotArea.mpl_connect('key_press_event', self.on_key)

        markerSelection = self.currentMask[:, value]
        data_x_init = self.data_x[:, value]
        data_y_init = self.data_y[:, value]
        disp_x_init = self.disp_x[:, value]
        disp_y_init = self.disp_y[:, value]
        colorsX = ['green', 'lightgreen', 'limegreen', 'seagreen']
        colorsY = ['blue', 'cornflowerblue', 'royalblue', 'navy']

        plotXFit = None
        plotYFit = None

        minLimit = -0.0001
        maxLimit = 0.0001

        nbInstances = len(np.atleast_1d(self.activeInstances))
        for instance in range(nbInstances):

            #instanceMarkers = [marker for marker in self.gridInstances[self.activeInstances[instance]] if marker in self.activeMarkers[value]]
            instanceMarkers = np.intersect1d(self.gridInstances[self.activeInstances[instance]],self.activeMarkers[value], assume_unique=True).astype(np.int)
            selectedMarkers = [marker for marker in instanceMarkers if markerSelection[marker] == 0]
            unSelectedMarkers = [marker for marker in instanceMarkers if marker not in selectedMarkers]

            if self.displayXMarkers.isChecked():

                #plot the fitting line of the value the user want to keep
                clr = colorsX[instance % 4]
                lbl = 'Instance '+str(self.activeInstances[instance])+' - X-Disp.'
                if len(np.atleast_1d(unSelectedMarkers)) > 1:
                    ax, bx = np.polyfit(data_x_init[unSelectedMarkers], disp_x_init[unSelectedMarkers], 1) #calculate the fitting line without taking care of the selected markers
                    plotXFit = self.plotArea.matPlot.plot(data_x_init[unSelectedMarkers], ax*data_x_init[unSelectedMarkers]+bx, '-', color=clr)
                else:
                    clr = 'magenta'
                self.plotArea.matPlot.plot(data_x_init[unSelectedMarkers], disp_x_init[unSelectedMarkers], 'o', ms=3, color=clr, label=lbl)    #plot all the markers in X direction
                self.plotArea.matPlot.plot(data_x_init[selectedMarkers], disp_x_init[selectedMarkers], 'o', ms=5, color='red')

                if len(np.atleast_1d(disp_x_init[instanceMarkers])) > 0:
                    minLimit = min(np.min(disp_x_init[instanceMarkers]), minLimit)
                    maxLimit = max(np.max(disp_x_init[instanceMarkers]), maxLimit)

            if self.displayYMarkers.isChecked():

                #plot the fitting line of the value the user want to keep
                clr = colorsY[instance % 4]
                lbl = 'Instance '+str(self.activeInstances[instance])+' - Y-Disp.'
                if len(np.atleast_1d(unSelectedMarkers)) > 1:
                    ay, by = np.polyfit(data_y_init[unSelectedMarkers], disp_y_init[unSelectedMarkers], 1) #calculate the fitting line without taking care of the selected markers
                    plotYFit = self.plotArea.matPlot.plot(data_y_init[unSelectedMarkers], ay*data_y_init[unSelectedMarkers]+by, '-', color=clr)
                else:
                    clr = 'orange'
                self.plotArea.matPlot.plot(data_y_init[unSelectedMarkers], disp_y_init[unSelectedMarkers], 'o', ms=3, color=clr, label=lbl)    #plot all the markers in X direction
                self.plotArea.matPlot.plot(data_y_init[selectedMarkers], disp_y_init[selectedMarkers], 'o', ms=5, color='red')

                if len(np.atleast_1d(disp_y_init[instanceMarkers])) > 0:
                    minLimit = min(np.min(disp_y_init[instanceMarkers]), minLimit)
                    maxLimit = max(np.max(disp_y_init[instanceMarkers]), maxLimit)

        if minLimit != maxLimit:
            self.plotArea.matPlot.set_ylim([minLimit-.1*np.absolute(minLimit),maxLimit+.1*np.absolute(maxLimit)]) # 10% extra to be able to select all markers
        else:
            self.plotArea.matPlot.set_ylim([-1,1])

        if (self.displayXMarkers.isChecked() or self.displayYMarkers.isChecked()) and (plotXFit is not None or plotYFit is not None): #plot the legend
            self.plotArea.matPlot.legend()

        self.plotArea.draw_idle() #refresh the area

    def selectRectangleMarkers(self, x0, y0, width, height): #when a rectangle is drawn, select all the markers inside

        value = self.activeImages[self.imageSelectSpinBox.value()-1]
        if x0 is None:
            return
        markerSelection = self.currentMask[:, value]
        data_x_current = self.data_x[:, value]
        data_y_current = self.data_y[:, value]
        disp_x_current = self.disp_x[:, value]
        disp_y_current = self.disp_y[:, value]

        nbInstances = len(np.atleast_1d(self.activeInstances))
        for instance in range(nbInstances):
            #instanceMarkers = [marker for marker in self.gridInstances[self.activeInstances[instance]] if marker in self.activeMarkers[value]]
            instanceMarkers = np.intersect1d(self.gridInstances[self.activeInstances[instance]],self.activeMarkers[value], assume_unique=True).astype(np.int)

            if self.displayXMarkers.isChecked():
                for i in instanceMarkers:
                    if data_x_current[i] > min(x0, x0+width) and data_x_current[i] < max(x0, x0+width) and disp_x_current[i] > min(y0, y0+height) and disp_x_current[i] < max(y0, y0+height):
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

            if self.displayYMarkers.isChecked():
                for i in instanceMarkers:
                    if data_y_current[i] > min(x0, x0+width) and data_y_current[i] < max(x0, x0+width) and disp_y_current[i] > min(y0, y0+height) and disp_y_current[i] < max(y0, y0+height):
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

        self.plotDispersion()

    def on_press(self, event):
        self.x0 = event.xdata
        self.y0 = event.ydata
        if self.x0 is None:
            return
        self.x2 = self.x0 #save coordinates in case the user goes out of the picture limits
        self.y2 = self.y0
        self.rect = mpp.Rectangle((0,0), 0, 0, facecolor='None', edgecolor='green', linewidth=2.5) #add invisible rectangle to be shown later
        self.plotArea.matPlot.add_patch(self.rect)
        self.motionRect = self.plotArea.mpl_connect('motion_notify_event', self.on_motion)
        self.rect.set_xy((self.x0, self.y0))
        self.rect.set_linestyle('dashed')

    def on_motion(self,event):

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
        self.plotArea.draw_idle()

    def on_release(self, event):
        x1 = event.xdata
        y1 = event.ydata
        if self.x0 is None:
            return
        self.plotArea.mpl_disconnect(self.motionRect)
        if x1 is None:
            x1 = self.x2
        if y1 is None:
            y1 = self.y2
        if x1 != self.x0:
            self.selectRectangleMarkers(self.x0, self.y0, x1-self.x0, y1-self.y0)
        self.rect.set_width(0)
        self.rect.set_height(0)
        self.plotArea.draw_idle()

    def on_key(self, event):
        #print('you pressed', event.key, event.xdata, event.ydata)
        isValidEvent = False
        if event.key == 'd':
            value = self.activeImages[self.imageSelectSpinBox.value()-1]
            markerSelection = self.currentMask[:, value]

            nbInstances = len(np.atleast_1d(self.activeInstances))
            for instance in range(nbInstances):
                #instanceMarkers = [marker for marker in self.gridInstances[self.activeInstances[instance]] if marker in self.activeMarkers[value]]
                instanceMarkers = np.intersect1d(self.gridInstances[self.activeInstances[instance]],self.activeMarkers[value], assume_unique=True).astype(np.int)
                for i in instanceMarkers:
                    if markerSelection[i] == 0:
                        self.currentMask[i,:] = 1
            isValidEvent = True

        if isValidEvent is True:
            self.plotDispersion()

    def maskSelection(self): #deleted the different selected markers

        shouldApplyMask = masks.generateMask(self.currentMask, self.fileDataPath)
        if shouldApplyMask is not None:
            self.parent.parentWindow.devWindow.addInfo('Masking selected markers..')
            progressBar = progressWidget.progressBarDialog('Saving masks..')
            masks.maskData(self.parent, self.currentMask, progressBar, toRecalculate=shouldApplyMask)
            self.close()

def launchDVPDialog(self, currentImage): #initiate the variables and launch the dialog

    self.analysisWidget.parentWindow.devWindow.addInfo('Cleaning Procedure Request : Displacement vs. Position')


    self.DVP = dispVsPosDialog(self.analysisWidget, currentImage)
    self.DVP.exec_()
