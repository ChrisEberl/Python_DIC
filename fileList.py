# -*- coding: utf-8 -*-
"""
Created on 21/03/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file manages the open and create new analysis functions
"""

import os
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide.QtGui import *
from PySide.QtCore import *
import menubar
import dockWidget
import StrainAnalysis
import generateGrid
import cv2
import numpy as np


def generateFileList(self): #called when a new analysis is started
    
    self.devWindow.addInfo('New analysis request.') #only in DevMode
    
    
    self.filePathTest, _ = QFileDialog.getOpenFileName(self, 'Select first image', '', 'Image Files (*.tif *.tiff *.bmp *.jpg *.jpeg *.png)')
    if self.filePathTest == '':
        return
    else: #create the file list when an image is selected
        
        menubar.menuDisabled(self)
        for instance in dockWidget.dockPlot.instances: #deleting dockwidget if there are
            instance.close()
            instance.deleteLater()
        dockWidget.dockPlot.instances = []
        self.homeWidget()

        #codeFolder = os.getcwd()
        self.filePath = self.filePathTest
        #os.chdir(os.path.dirname(self.filePath))
        self.extension = os.path.splitext(os.path.basename(self.filePath))[1]
        self.fileList = os.listdir(os.path.dirname(self.filePath))
        self.fileList = [nb for nb in self.fileList if nb.endswith(self.extension)]
        self.fileNameList = []
        
        self.count = 0
        for element in self.fileList:
            self.fileNameList.append('{0}'.format(element))
            self.count+=1

        self.devWindow.addInfo('Filenamelist generated.') #only in DevMode

        
        createAnalysis = nameAnalysis(self, self.fileNameList, os.path.dirname(self.filePath))
        result = createAnalysis.exec_()
        
        if result == 1:
        
            self.filterFile = None
            
            #self.devWindow.addInfo('File saved in \''+self.directory+'\' folder.') #only in DevMode
            
            menubar.menuCreateGridEnabled(self)
            
            generateGrid.createGrid(self)
    
    
def openFileList(self): #when opening a previous analysis, ask for the project folder and launch the analysis widget
    
    self.devWindow.addInfo('Open file request.') #only in DevMode
    
    self.flags = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
    self.directory = QFileDialog.getExistingDirectory(self, 'Data Folder', '', self.flags)
    
    if self.directory == "":
        return
    else:
        
        for instance in dockWidget.dockPlot.instances: #deleting dockwidget if there are
            instance.close()
            instance.deleteLater()
        dockWidget.dockPlot.instances = []
            
        self.filePath = os.path.dirname(self.directory)
        self.fileDataPath = self.directory
        
        self.devWindow.addInfo('Starting analysis : '+os.path.basename(self.fileDataPath), self.statusBar())

        StrainAnalysis.analyseResult(self, self)

class nameAnalysis(QDialog):
    
    def __init__(self, parent, fileNameList, filePath):
        
        QDialog.__init__(self)
        dialogLayout = QVBoxLayout()
        dialogLayout.setSpacing(20)
        self.setWindowTitle('Analysis Creation')
        self.setMaximumWidth(500)
        self.setMaximumHeight(600)
        
        infoLbl = QLabel('Please verify the automatic image selection.')
        infoLbl.setAlignment(Qt.AlignCenter)
        
        imageLayout = QHBoxLayout()
        self.plotArea = MatplotlibImageWidget(self)
        self.plotArea.setMaximumHeight(300)
        self.imageList = QListView()
        self.imageList.setMinimumWidth(200)
        self.imageList.setMaximumHeight(300)
        self.imageList.setContentsMargins(0,20,0,20)
        self.imageModel = QStandardItemModel(self.imageList)
        for image in fileNameList:
            imageItem = QStandardItem(image)
            imageItem.setCheckable(True)
            imageItem.setCheckState(Qt.CheckState.Checked)
            self.imageModel.appendRow(imageItem)
        self.imageList.setModel(self.imageModel)
        self.imageList.setCurrentIndex(self.imageModel.indexFromItem(self.imageModel.item(0)))
        self.imageList.clicked.connect(lambda: self.displayImage(filePath, fileNameList))
        imageLayout.addWidget(self.plotArea)
        imageLayout.addWidget(self.imageList)
        
        imageNumberLayout = QHBoxLayout()
        imageLbl = QLabel('Selection:')
        self.imageSelected = QLabel('-')
        totalImage = QLabel('/ '+str(len(np.atleast_1d(fileNameList))))
        imageNumberLayout.addStretch(1)
        imageNumberLayout.addWidget(imageLbl)
        imageNumberLayout.addWidget(self.imageSelected)
        imageNumberLayout.addWidget(totalImage)
        imageNumberLayout.addStretch(1)
        
        analysisName = QHBoxLayout()
        analysisName.setSpacing(20)
        self.analysisLbl = QLabel('-')
        self.analysisInput = QLineEdit()
        self.analysisInput.setCursorPosition(0)
        self.analysisInput.setTextMargins(3,3,3,3)
        currentFont = self.analysisInput.font()
        currentFont.setPointSize(15)
        self.analysisInput.setFont(currentFont)
        self.analysisInput.setMinimumWidth(200)
        self.analysisInput.setMinimumHeight(40)
        validatorRx = QRegExp("\\w+")
        validator = QRegExpValidator(validatorRx, self)
        self.analysisInput.setValidator(validator)
        analysisName.addStretch(1)
        analysisName.addWidget(self.analysisLbl)
        analysisName.addWidget(self.analysisInput)
        analysisName.addStretch(1)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.setSpacing(40)
        cancelButton = QPushButton('Cancel')
        cancelButton.setMaximumWidth(100)
        cancelButton.setMinimumHeight(30)
        self.createButton = QPushButton('Start Analysis')
        self.createButton.setMinimumWidth(150)
        self.createButton.setMinimumHeight(30)
        self.createButton.setEnabled(False)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(cancelButton)
        buttonLayout.addWidget(self.createButton)
        buttonLayout.addStretch(1)
        
        self.analysisInput.textChanged.connect(lambda: self.textChanged(filePath, self.analysisInput.text()))
        self.createButton.clicked.connect(lambda: self.createAnalysis(parent, filePath, self.analysisInput.text()))
        cancelButton.clicked.connect(self.reject)
        
        dialogLayout.addWidget(infoLbl)
        dialogLayout.addLayout(imageLayout)
        dialogLayout.addLayout(imageNumberLayout)
        dialogLayout.addLayout(analysisName)
        dialogLayout.addLayout(buttonLayout)
        
        self.setLayout(dialogLayout)
        self.textChanged(filePath, '')
        self.displayImage(filePath, fileNameList)
        
        
    def displayImage(self, filePath, fileNameList):
        
        self.plotArea.imagePlot.cla()
        imageName = self.imageModel.itemFromIndex(self.imageList.currentIndex()).text()
        readImage = cv2.imread(filePath+'/'+imageName,0)
        self.plotArea.imagePlot.imshow(readImage, cmap='gray')
        self.plotArea.imagePlot.axes.xaxis.set_ticklabels([])
        self.plotArea.imagePlot.axes.yaxis.set_ticklabels([])
        self.plotArea.draw_idle()
        nbChecked = 0
        for image in range(self.imageModel.rowCount()):
            if self.imageModel.item(image).checkState() == Qt.CheckState.Checked:
                nbChecked += 1
        self.imageSelected.setText(str(nbChecked))
        if nbChecked > 1:
            self.imageSelected.setText(str(nbChecked))
            self.textChanged(filePath, self.analysisInput.text())
        else:
            self.imageSelected.setText('<font color=red>'+str(nbChecked)+'</font>')
            self.createButton.setEnabled(False)
        
    def textChanged(self, filePath, name):
        
        if name <> '':
            checkName = filePath+'/'+name
            if os.path.exists(checkName):
                self.analysisLbl.setText('<font size=5><font color=red>Already Exist.</font></font>')
                self.createButton.setEnabled(False)
            else:
                self.analysisLbl.setText('<font size=5><font color=green>Analysis Name:</font></font>')
                if int(self.imageSelected.text()) > 1:
                    self.createButton.setEnabled(True)
        else:
            self.analysisLbl.setText('<font size=5>Analysis Name:</font>')
            self.createButton.setEnabled(False)
            
    def createAnalysis(self, parent, filePath, name):
        
        directory = filePath+'/'+name
        os.makedirs(directory)
        fileNameList = []
        for image in range(self.imageModel.rowCount()):
            if self.imageModel.item(image).checkState() == Qt.CheckState.Checked:
                fileNameList.append(self.imageModel.item(image).text())
        np.savetxt(directory+'/filenamelist.dat', fileNameList, fmt="%s")
        parent.filePath = filePath
        parent.fileDataPath = directory
        parent.statusBar().showMessage('Image list file created in '+directory)
        self.accept()
            
class MatplotlibImageWidget(FigureCanvas): 
    
    def __init__(self, parentWidget):
        super(MatplotlibImageWidget,self).__init__(Figure())
        self.figure = Figure()
        self.figure.set_facecolor('none')
        self.canvas = FigureCanvas(self.figure)
        self.imagePlot = self.figure.add_subplot(111)
        self.imagePlot.set_aspect('equal')
        self.figure.tight_layout()