# -*- coding: utf-8 -*-
"""
Created on 15/07/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file manages the control tools in the analysis results
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os, numpy as np
from functions import masks

class controlWidget(QWidget):

    def __init__(self, parent):

        super(controlWidget, self).__init__()

        self.parent = parent

        layout = QVBoxLayout()
        layout.setContentsMargins(10,10,10,10)
        layout.setSpacing(0)
        self.setMinimumWidth(300)

        # Analysis Infos
        analysisFrame = QFrame()
        analysisFrame.setFrameShape(QFrame.StyledPanel)
        analysisFrame.setFixedHeight(80)
        analysisLayout = QVBoxLayout()
        analysisLayout.setContentsMargins(0,0,0,0)
        analysisLayout.setAlignment(Qt.AlignCenter)

        analysisTitleLayout = QHBoxLayout()
        analysisTitleLayout.setContentsMargins(0,0,0,0)
        analysisTitle = QLabel('Name:')
        analysisTitle.setAlignment(Qt.AlignLeft)
        analysisTitle.setContentsMargins(2,0,0,0)
        analysisTitle.setMinimumWidth(100)
        analysisName = QLabel('<b>'+os.path.basename(parent.parentWindow.fileDataPath)+'</b>')
        analysisName.setAlignment(Qt.AlignCenter)
        analysisTitleLayout.addWidget(analysisTitle)
        analysisTitleLayout.addWidget(analysisName)

        imagesLayout = QHBoxLayout()
        imagesLayout.setContentsMargins(0,0,0,0)
        imagesLbl = QLabel('Active images:')
        imagesLbl.setAlignment(Qt.AlignLeft)
        imagesLbl.setContentsMargins(2,0,0,0)
        imagesLbl.setMinimumWidth(100)
        self.totalActive = QLabel(str(len(parent.activeImages)))
        self.totalActive.setAlignment(Qt.AlignCenter)
        totalImages = QLabel('('+str(parent.nb_image)+')')
        imagesLayout.addWidget(imagesLbl)
        imagesLayout.addWidget(self.totalActive)
        imagesLayout.addWidget(totalImages)

        markersLayout = QHBoxLayout()
        markersLayout.setContentsMargins(0,0,0,0)
        markersLbl = QLabel('Active markers:')
        markersLbl.setAlignment(Qt.AlignLeft)
        markersLbl.setContentsMargins(2,0,0,0)
        markersLbl.setMinimumWidth(100)
        self.nonMaskedMarkers = QLabel('-')
        self.nonMaskedMarkers.setAlignment(Qt.AlignCenter)
        totalMarkers = QLabel('('+str(int(parent.data_x.size))+')')
        markersLayout.addWidget(markersLbl)
        markersLayout.addWidget(self.nonMaskedMarkers)
        markersLayout.addWidget(totalMarkers)

        versionLayout = QHBoxLayout()
        versionLayout.setContentsMargins(0,0,0,0)
        versionLbl = QLabel('Version:')
        versionLbl.setAlignment(Qt.AlignLeft)
        versionLbl.setContentsMargins(2,0,0,0)
        versionLbl.setMinimumWidth(100)
        self.currentVersionName = '-'
        self.currentVersion = QLabel(self.currentVersionName)
        self.currentVersion.setAlignment(Qt.AlignCenter)
        self.currentVersion.enterEvent = lambda x: self.currentVersion.setText('Click to rename.')
        self.currentVersion.leaveEvent = lambda x: self.currentVersion.setText(self.currentVersionName)
        self.currentVersion.mousePressEvent = lambda x: masks.renameMask(self.parent.parentWindow, self.currentVersionName)
        versionLayout.addWidget(versionLbl)
        versionLayout.addWidget(self.currentVersion)

        analysisLayout.addLayout(analysisTitleLayout)
        analysisLayout.addLayout(imagesLayout)
        analysisLayout.addLayout(markersLayout)
        analysisLayout.addLayout(versionLayout)
        analysisFrame.setLayout(analysisLayout)


        # Current Image Infos
        currentLayout = QHBoxLayout()

        imageInfoFrame = QWidget()
        imageInfoFrame.setMaximumWidth(300)
        imageInfoLayout = QVBoxLayout()
        imageInfoLayout.setAlignment(Qt.AlignCenter)
        self.imageName = QLabel('-')
        imageNbLbl = QLabel('Image')
        imageNbLbl.setContentsMargins(0,5,0,0)
        self.imageNumber = QLabel('1')
        self.imageNumber.setFrameStyle(QFrame.StyledPanel)
        self.imageNumber.setAlignment(Qt.AlignCenter)
        markersInImageLbl = QLabel('Markers')
        markersInImageLbl.setContentsMargins(0,5,0,0)
        self.markersInImage = QLabel('-')
        self.markersInImage.setFrameStyle(QFrame.StyledPanel)
        self.markersInImage.setAlignment(Qt.AlignCenter)
        strainLbl = QLabel('Strain')
        strainLbl.setContentsMargins(0,5,0,0)
        self.strainValue = QLabel('-')
        self.strainValue.setFrameStyle(QFrame.StyledPanel)
        self.strainValue.setAlignment(Qt.AlignCenter)
        imageInfoLayout.addStretch(1)
        imageInfoLayout.addWidget(self.imageName)
        imageInfoLayout.addStretch(1)
        imageInfoLayout.addWidget(imageNbLbl)
        imageInfoLayout.addWidget(self.imageNumber)
        imageInfoLayout.addWidget(markersInImageLbl)
        imageInfoLayout.addWidget(self.markersInImage)
        imageInfoLayout.addWidget(strainLbl)
        imageInfoLayout.addWidget(self.strainValue)
        imageInfoLayout.addStretch(1)
        imageInfoFrame.setLayout(imageInfoLayout)

        self.imageSelector = QDial()
        self.imageSelector.setContentsMargins(0,0,0,0)
        self.imageSelector.valueChanged.connect(lambda: self.updateSlider(self.imageSelector))

        currentLayout.addWidget(imageInfoFrame)
        currentLayout.addWidget(self.imageSelector)

        self.sliderSelector = QSlider(Qt.Horizontal)
        self.sliderSelector.valueChanged.connect(lambda: self.updateSlider(self.sliderSelector))

        layout.addStretch(1)
        layout.addWidget(analysisFrame)
        layout.addLayout(currentLayout)
        layout.addWidget(self.sliderSelector)

        self.setLayout(layout)

    def updateSlider(self, slider):

        imageValue = slider.value()
        if slider == self.imageSelector:
            if self.sliderSelector.value != imageValue:
                self.sliderSelector.setValue(imageValue)
        else:
            if self.imageSelector.value != imageValue:
                self.imageSelector.setValue(imageValue)
        self.parent.resultAnalysis.graphRefresh(imageValue)

    def updateAnalysisInfos(self):

        nbActiveImages = len(self.parent.activeImages)
        self.imageSelector.setRange(0, nbActiveImages - 1)
        self.sliderSelector.setRange(0, nbActiveImages - 1)
        self.totalActive.setText(str(nbActiveImages))
        self.nonMaskedMarkers.setText(str(int(np.sum(self.parent.currentMask))))
        self.imageSelector.setValue(0)
        self.sliderSelector.setValue(0)


    def updateImageInfos(self, image):


        currentImage = self.parent.activeImages[image]
        self.imageName.setText('<b>'+str(self.parent.fileNameList[currentImage])+'</b>')
        self.imageNumber.setText(str(image+1))
        nbMarkersInImage = 0
        for instance in self.parent.activeInstances:
            nbMarkersInImage += len(np.atleast_1d(self.parent.grid_instances[instance]))
        self.markersInImage.setText(str(nbMarkersInImage))
        self.strainValue.setText('-')

    def resizeEvent(self, event=0):

        self.resize(self.minimumSizeHint())
