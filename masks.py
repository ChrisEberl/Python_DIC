# -*- coding: utf-8 -*-
"""
Created on 23/05/2016


@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file manages the whole masks saving and opening features
"""

from PySide.QtCore import *
from PySide.QtGui import *
import time
import os
import numpy as np
import initData
import plot2D
import plot3D
import getData
import progressWidget
import dockWidget

def generateMask(mask, path, fileName=None, confirmDialog=True):    
    
    if confirmDialog is True:
        confirmDialog = confirmMask()
        result = confirmDialog.exec_()
    else:
        result = 1
    
    if result == 1:    
        #Save mask file into log folder
        currentTime = time.localtime()
        if fileName is None:
            fileName=str(currentTime[0])+'_'+str(currentTime[1])+'_'+str(currentTime[2])+'_'+str(currentTime[3])+str(currentTime[4])+str(currentTime[5])+'.dat'
        directory = path+'/log/'
        if not os.path.exists(directory):
            os.makedirs(directory)
            np.savetxt(directory+'Original.dat', np.ones_like(mask), fmt='%1d')
            
        np.savetxt(directory+fileName, mask, fmt='%1d') 
        return 'OK'
    else:
        return None
    
class confirmMask(QDialog):
    
    def __init__(self):
        
        QDialog.__init__(self)
        
        self.setWindowTitle('Confirm Mask')
        self.setMinimumWidth(300)
        dialogLayout = QVBoxLayout()
        
        questionLbl = QLabel('<font size=5>Do you confirm the selection?</font>')
        questionLbl.setAlignment(Qt.AlignCenter)
        infoLbl = QLabel('Re-calculate coordinates:')
        
        checkBoxLayout = QHBoxLayout()
        corrBox = QCheckBox('Correlation 2D')
        xStrainBox = QCheckBox('2D Local Strain (X)')
        yStrainBox = QCheckBox('2D Local Strain (Y)')
        corrBox.setChecked(True)
        xStrainBox.setChecked(True)
        yStrainBox.setChecked(True)
        #temp
        corrBox.setDisabled(True)
        xStrainBox.setDisabled(True)
        yStrainBox.setDisabled(True)
        #end temp
        checkBoxLayout.addWidget(corrBox)
        checkBoxLayout.addWidget(xStrainBox)
        checkBoxLayout.addWidget(yStrainBox)
        
        buttonLayout = QHBoxLayout()
        cancelButton = QPushButton('Select more markers')
        cancelButton.setMaximumWidth(150)
        confirmButton = QPushButton('Confirm and Calculate')
        confirmButton.setMaximumWidth(120)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(cancelButton)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(confirmButton)
        buttonLayout.addStretch(1)
        
        cancelButton.clicked.connect(self.reject)
        confirmButton.clicked.connect(self.accept)
        
        
        dialogLayout.addWidget(questionLbl)
        dialogLayout.addWidget(infoLbl)
        dialogLayout.addLayout(checkBoxLayout)
        dialogLayout.addLayout(buttonLayout)
        self.setLayout(dialogLayout)
        
        
    
def renameMask(parent, name):
    
    filePath = parent.fileDataPath+'/log/'
    if not os.path.exists(filePath):
        os.makedirs(filePath)
        np.savetxt(filePath+'Original.dat', np.ones_like(parent.analysisWidget.data_x), fmt='%1d')
        
    newName, ok = QInputDialog.getText(parent, 'Rename Version', 'Enter the new version name:', text=name)
    if ok:
        if newName == "":
            return
        else:
            os.rename(filePath+name+'.dat', filePath+newName+'.dat')
            parent.analysisWidget.controlWidget.currentVersionName = newName
            parent.analysisWidget.controlWidget.currentVersion.setText(newName)
            
    
def maskData(parentWindow, mask, progressBar=None, dataList=None):
    
    if progressBar is not None:
        progressBar.changeValue(1, 'Applying masks...')        
    
#    if dataList is None:
#        data_x = parentWindow.data_x
#        disp_x = parentWindow.disp_x
#        data_y = parentWindow.data_y
#        disp_y = parentWindow.disp_y
#        data_corr = parentWindow.data_corr
#        data_stdx = parentWindow.data_stdx
#        data_stdy = parentWindow.data_stdy
#    else:
#        data_x = dataList[0]
#        disp_x = dataList[5]
#        data_y = dataList[1]
#        disp_y = dataList[6]
#        data_corr = dataList[2]
#        data_stdx = dataList[3]
#        data_stdy = dataList[4]  
#    
#    markers = 0
#    rownum = 0
#    for row in mask:
#        colnum = 0
#        for col in row:
#            if col == 0:
#                data_x[rownum, colnum] = np.nan
#                disp_x[rownum, colnum] = np.nan
#                data_y[rownum, colnum] = np.nan
#                disp_y[rownum, colnum] = np.nan
#                data_corr[rownum, colnum] = np.nan
#                data_stdx[rownum, colnum] = np.nan
#                data_stdy[rownum, colnum] = np.nan
#                markers += 1
#            colnum += 1
#        rownum += 1
#    
#    parentWindow.data_x = data_x
#    parentWindow.disp_x = disp_x
#    parentWindow.data_y = data_y
#    parentWindow.disp_y = disp_y
#    parentWindow.data_corr = data_corr
#    parentWindow.data_stdx = data_stdx
#    parentWindow.data_stdy = data_stdy
    
    
    #parentWindow.parentWindow.devWindow.addInfo(str(markers)+' markers masked.', statusBar=parentWindow.parentWindow.statusBar())
    
    #parentWindow.currentMask = mask
    
    if dataList is None:
        calculatingThread = parentWindow.parentWindow.createThread([parentWindow, progressBar, mask], initData.initPlottedData, signal=1)
        calculatingThread.signal.threadSignal.connect(lambda: newMasksCalculated(parentWindow, progressBar))
        calculatingThread.start()
    else:
        parentWindow.grid_instances = dataList[11]
        initData.initPlottedData(parentWindow, progressBar, mask, dataList[13])
    
    
def newMasksCalculated(parentWindow, progressBar):
    
    plot3D.plot3D_init(parentWindow.displacementX.dockWidget.plot, parentWindow.xLimit, parentWindow.yLimit, parentWindow.disp_x)
    plot3D.plot3D_init(parentWindow.displacementY.dockWidget.plot, parentWindow.xLimit, parentWindow.yLimit, parentWindow.disp_y)
    plot3D.plot3D_init(parentWindow.correlation.dockWidget.plot, parentWindow.xLimit, parentWindow.yLimit, np.array([0,1]))   
    plot2D.plot2D_correlation(parentWindow, parentWindow.correlation2D.dockWidget.figure, parentWindow.correlation2D.dockWidget.plot, parentWindow.xi, parentWindow.yi, parentWindow.zi[0][0])
    plot3D.plot3D_init(parentWindow.deviationX.dockWidget.plot, parentWindow.xLimit, parentWindow.yLimit, parentWindow.data_stdx)
    plot3D.plot3D_init(parentWindow.deviationY.dockWidget.plot, parentWindow.xLimit, parentWindow.yLimit, parentWindow.data_stdy)
    plot2D.plot2D_strain(parentWindow, parentWindow.strain2DX.dockWidget.plot, parentWindow.xi, parentWindow.yi, parentWindow.zi_strainX[0][0], parentWindow.grid_instances, parentWindow.activeInstances, parentWindow.activeMarkers[parentWindow.activeImages[0]], plotFig = parentWindow.strain2DX.dockWidget.figure)
    plot2D.plot2D_strain(parentWindow, parentWindow.strain2DY.dockWidget.plot, parentWindow.xi, parentWindow.yi, parentWindow.zi_strainY[0][0], parentWindow.grid_instances, parentWindow.activeInstances, parentWindow.activeMarkers[parentWindow.activeImages[0]], plotFig = parentWindow.strain2DY.dockWidget.figure)
    plot2D.plot2D_displacementDeviation(parentWindow, parentWindow.displacement2D.dockWidget.plot, parentWindow.data_x, parentWindow.data_y, parentWindow.disp_x, parentWindow.disp_y, 0, parentWindow.grid_instances, parentWindow.activeInstances)
    #plot2D.plot2D_displacementDeviation(parentWindow, parentWindow.deviation2D.dockWidget.plot, parentWindow.data_x, parentWindow.data_y, parentWindow.disp_x, parentWindow.disp_y, 0, parentWindow.grid_instances, parentWindow.activeInstances)
    plot2D.plot2D_strain(parentWindow, parentWindow.strainX.dockWidget.plot, parentWindow.data_x, 0, parentWindow.disp_x, parentWindow.grid_instances, parentWindow.activeInstances, parentWindow.activeMarkers, refImg=parentWindow.activeImages[0])
    plot2D.plot2D_strain(parentWindow, parentWindow.strainY.dockWidget.plot, parentWindow.data_y, 0, parentWindow.disp_y,parentWindow.grid_instances, parentWindow.activeInstances, parentWindow.activeMarkers, refImg=parentWindow.activeImages[0])
    plot2D.plot_TrueStrain(parentWindow, parentWindow.trueStrainX.dockWidget.plot, [parentWindow.strainX_data, parentWindow.trueStrainX.averageImageNb, parentWindow.activeInstances])
    plot2D.plot_TrueStrain(parentWindow, parentWindow.trueStrainY.dockWidget.plot, [parentWindow.strainY_data, parentWindow.trueStrainY.averageImageNb, parentWindow.activeInstances])

    for instance in dockWidget.dockPlot.instances:
        instance.dockWidget.draw() #refresh all the plots

    openMask(parentWindow.parentWindow)
    parentWindow.controlWidget.updateAnalysisInfos()
    progressBar.changeValue(100, '-')
    parentWindow.resultAnalysis.graphRefresh(imageValue=0)
    
#def getMask(data):
#    
#    currentMask = np.ones((len(data),len(data[0,:])))
#    rownum = 0
#    for row in data:
#        colnum = 0
#        for col in row:
#            if np.isnan(data[rownum,colnum]):
#                currentMask[rownum,colnum] = 0
#            colnum += 1
#        rownum += 1
#    
#    return currentMask
    
def openMask(parent, maskName = 0, getNbMasks = 0):
    
    dirpath = parent.fileDataPath+'/log'
    fileName = 'Original'
    filePath = None
    currentMask = np.ones((len(parent.analysisWidget.data_x),len(parent.analysisWidget.data_x[0,:])))
    if maskName == 0:
        if os.path.exists(dirpath):
            a = [s for s in os.listdir(dirpath) if os.path.isfile(os.path.join(dirpath, s))]
            a.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)))
            if getNbMasks > 0:
                return len(a)
            if len(a) > 0:
                filePath = dirpath+'/'+a[len(a)-1]
                currentMask = getData.testReadFile(filePath)
        else:
            if getNbMasks > 0:
                return 1
            
    else:
        filePath = maskName
        currentMask = getData.testReadFile(filePath)
    
    if filePath is not None:
        fileName = os.path.splitext(os.path.basename(filePath))[0]
    parent.analysisWidget.controlWidget.currentVersionName = fileName
    parent.analysisWidget.controlWidget.currentVersion.setText(fileName)

    return currentMask
    
def openMaskRequest(parent):
    
    filePathTest, _ = QFileDialog.getOpenFileName(parent, 'Select the mask file', '', 'Dat Files (*.dat)')
    if filePathTest == '':
        return
    else: #open the mask
        newMask = openMask(parent, maskName = filePathTest)
        progressBar = progressWidget.progressBarDialog('Saving masks..')
        if generateMask(newMask, parent.fileDataPath, fileName=os.path.basename(filePathTest), confirmDialog=False) == 'OK':
            #maskData(parent.analysisWidget, newMask, progressBar)
            openingThread = parent.createThread([parent, progressBar, newMask], fileOpenedForImportation, signal=1)
            openingThread.signal.threadSignal.connect(lambda: newMasksCalculated(parent.analysisWidget, progressBar))
            openingThread.start()
    
def fileOpenedForImportation(parent, progressBar, newMask, thread):
    
    dataList = getData.generateData(parent, progressBar)
    if dataList is not None:
        dataList += (thread, ) #we put the thread in the dataList to use the signal in initData.initPlottedData
        maskData(parent.analysisWidget, newMask, progressBar, dataList)
#    
#def cleanedData(data):
#    
#    maskedData = data[np.isnan(data)==False]
#    return maskedData
