# -*- coding: utf-8 -*-
"""
Created on 09/08/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file manages the analysis info dialog
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np, matplotlib as mpl, time
from functions import plot2D, plot3D, getData, masks, DIC_Global

def launchDialog(parent):

    analysisDialog = analysisInfos(parent)
    analysisDialog.exec_()

class analysisInfos(QDialog):

    def __init__(self, parent):

        super(analysisInfos, self).__init__()

        self.parent = parent

        self.setWindowTitle('Analysis Info')
        self.setMinimumWidth(500)

        self.mainLayout = QVBoxLayout()
        #self.mainLayout.setAlignment(Qt.AlignCenter)
        #self.mainLayout.setSpacing(30)

        self.setLayout(self.mainLayout)

        self.openInfos()

    def openInfos(self):

        filePath =  self.parent.fileDataPath+'/infoAnalysis.csv'
        filePathMarkers =  self.parent.fileDataPath+'/infoMarkers.csv'
        strainX = self.parent.fileDataPath+'/strainx.csv'
        strainY = self.parent.fileDataPath+'/strainy.csv'
        infos = getData.testReadFile(filePath, lib=1) #None if not found
        # 0 Name, 1 Reference Mode, 2 CorrSize, 3 nbProcesses, 4 total processing time, 5 nbImages, 6 nbMarkers, 7 nbImages * nbMarkers, 8 largeDisp YES/NO, 9 Author
        self.infos = np.char.decode(infos, encoding="ascii")
        self.markersInfos = getData.testReadFile(filePathMarkers) #None if not found
        self.fileStrainX = getData.testReadFile(strainX) #None if not found
        self.fileStrainY = getData.testReadFile(strainY) #None if not found
        if self.infos is None:
            missingFile = QLabel('infoAnalysis.csv file not found.')
            self.mainLayout.addWidget(missingFile)
        else:
            self.displayInfos()

    def displayInfos(self):

        infoFrame = QFrame()
        infoFrame.setFrameShape(QFrame.StyledPanel)
        nameLayout = QHBoxLayout()
        nameLayout.setAlignment(Qt.AlignCenter)
        nameLbl = QLabel('Name:')
        nameLblValue = QLabel('<b>'+str(self.infos[0])+'</b>')
        versionLbl = QLabel('Version:')
        versionName = self.parent.analysisWidget.controlWidget.currentVersion.text()
        versionLblValue = QLabel('<b>'+str(versionName)+'</b>')
        authorLbl = QLabel('Author:')
        authorLblValue = QLabel('<b>'+str(self.infos[9])+'</b>')

        simpleSeparator = QFrame()
        simpleSeparator.setFrameShape(QFrame.VLine)
        simpleSeparator2 = QFrame()
        simpleSeparator2.setFrameShape(QFrame.VLine)
        nameLayout.addWidget(nameLbl)
        nameLayout.addWidget(nameLblValue)
        nameLayout.addWidget(simpleSeparator)
        nameLayout.addWidget(versionLbl)
        nameLayout.addWidget(versionLblValue)
        nameLayout.addWidget(simpleSeparator2)
        nameLayout.addWidget(authorLbl)
        nameLayout.addWidget(authorLblValue)

        infoFrame.setLayout(nameLayout)

        globalInfosLayout = QHBoxLayout()
        globalInfosLayout.setContentsMargins(50,0,20,20)
        #globalInfosLayout.setAlignment(Qt.AlignCenter)
        imageOriginalLbl = QLabel('<u><font color="Gray">Original Version:</font></u>')
        imagesLbl = QLabel('<font color="Gray">Nb. Images:</font>')
        imagesLbl.setContentsMargins(20,0,0,0)
        imagesLblValue = QLabel('<font color="Gray"><b>'+str(self.infos[5])+'</b></font>')
        markersLbl = QLabel('<font color="Gray">Nb. Markers:</font>')
        markersLblValue = QLabel('<font color="Gray"><b>'+str(self.infos[7])+'</b> ('+str(self.infos[6])+'/image)</font>')
        #globalInfosLayout.addStretch(1)
        globalInfosLayout.addWidget(imageOriginalLbl)
        globalInfosLayout.addWidget(imagesLbl)
        globalInfosLayout.addWidget(imagesLblValue)
        globalInfosLayout.addWidget(markersLbl)
        globalInfosLayout.addWidget(markersLblValue)

        currentInfosLayout = QHBoxLayout()
        currentInfosLayout.setContentsMargins(50,20,20,0)
        #currentInfosLayout.setAlignment(Qt.AlignCenter)
        imageCurrentLbl = QLabel('<u>Current Version:</u>')
        currentImagesLbl = QLabel('Nb. Images:')
        currentImagesLbl.setContentsMargins(20,0,0,0)
        self.nbActiveImages = self.parent.analysisWidget.controlWidget.totalActive.text()
        currentImagesLblValue = QLabel('<b>'+str(self.nbActiveImages)+'</b>')
        currentMarkersLbl = QLabel('Nb. Markers:')
        nbActiveMarkers = self.parent.analysisWidget.controlWidget.nonMaskedMarkers.text()
        currentMarkersLblValue = QLabel('<b>'+str(nbActiveMarkers)+'</b>')
        #currentInfosLayout.addStretch(1)
        currentInfosLayout.addWidget(imageCurrentLbl)
        currentInfosLayout.addWidget(currentImagesLbl)
        currentInfosLayout.addWidget(currentImagesLblValue)
        currentInfosLayout.addWidget(currentMarkersLbl)
        currentInfosLayout.addWidget(currentMarkersLblValue)

        otherInfosLbl = QLabel('- ADDITIONAL INFORMATIONS -')
        otherInfosLbl.setContentsMargins(0,0,0,10)
        otherInfosLbl.setAlignment(Qt.AlignCenter)

        otherInfosLayout = QHBoxLayout()
        otherInfosLayout.setContentsMargins(0,0,0,10)
        #otherInfosLayout.setAlignment(Qt.AlignCenter)
        corrsizeLbl = QLabel('CorrSize:')
        corrsizeLbl.setContentsMargins(20,0,0,0)
        corrsizeLblValue = QLabel('<b>'+str(self.infos[2])+'</b>')
        referenceLbl = QLabel('Reference:')
        referenceLbl.setContentsMargins(20,0,0,0)
        if self.infos[1] == '0':
            referenceLblTxt = 'Previous'
        elif self.infos[1] == '1':
            referenceLblTxt = 'First'
        else:
            referenceLblTxt = 'Shifted'
        referenceLblValue = QLabel('<b>'+referenceLblTxt+'</b>')
        instanceLbl = QLabel('Nb. Grid Instances:')
        instanceLbl.setContentsMargins(20,0,0,0)
        instanceLblValue = QLabel('<b>'+str(len(np.atleast_1d(self.parent.analysisWidget.grid_instances)))+'</b> (Active: '+str(len(self.parent.analysisWidget.activeInstances))+')')
        nbVersionsLbl = QLabel('Nb. Versions:')
        nbVersionsLbl.setContentsMargins(20,0,0,0)
        nbVersionsLblValue = QLabel('<b>'+str(masks.openMask(self.parent, getNbMasks = 1))+'</b>')
        nbVersionsLblValue.setContentsMargins(0,0,20,0)
        otherInfosLayout.addWidget(corrsizeLbl)
        otherInfosLayout.addWidget(corrsizeLblValue)
        otherInfosLayout.addWidget(referenceLbl)
        otherInfosLayout.addWidget(referenceLblValue)
        otherInfosLayout.addWidget(instanceLbl)
        otherInfosLayout.addWidget(instanceLblValue)
        otherInfosLayout.addWidget(nbVersionsLbl)
        otherInfosLayout.addWidget(nbVersionsLblValue)

        extraInfosLayout = QHBoxLayout()
        extraInfosLayout.setAlignment(Qt.AlignLeft)
        processingLbl = QLabel('Correlation processing time:')
        processingLbl.setContentsMargins(20,0,0,0)
        processingLblValue = QLabel('<b>'+str(self.infos[4])+'</b>')
        nbProcessesLbl = QLabel('Nb. Processes:')
        nbProcessesLbl.setContentsMargins(20,0,0,0)
        nbProcessesLblValue = QLabel('<b>'+str(self.infos[3])+'</b>')
        shiftCorrectionLbl = QLabel('Shift Correction:')
        shiftCorrectionLbl.setContentsMargins(20,0,0,0)
        if self.infos[8] == '0':
            shiftCorrectionLblTxt = 'No'
        else:
            shiftCorrectionLblTxt = 'Yes'
        shiftCorrectionLblValue = QLabel('<b>'+shiftCorrectionLblTxt+'</b>')
        filterLbl = QLabel('Filters:')
        filterLbl.setContentsMargins(20,0,0,0)
        filterList = self.parent.analysisWidget.filterList
        if filterList is None:
            filterApplied = 0
        else:
            filterApplied = len(np.atleast_1d(filterList))
        filterLblValue = QLabel('<b>'+str(filterApplied)+'</b>')
        #filterLblValue.setContentsMargins(0,0,20,0)
        extraInfosLayout.addWidget(processingLbl)
        extraInfosLayout.addWidget(processingLblValue)
        extraInfosLayout.addWidget(nbProcessesLbl)
        extraInfosLayout.addWidget(nbProcessesLblValue)
        extraInfosLayout.addWidget(shiftCorrectionLbl)
        extraInfosLayout.addWidget(shiftCorrectionLblValue)
        extraInfosLayout.addWidget(filterLbl)
        extraInfosLayout.addWidget(filterLblValue)


        plotListLayout = QHBoxLayout()
        plotListLayout.setAlignment(Qt.AlignLeft)
        plotListLayout.setContentsMargins(20,25,0,0)
        plotListLbl = QLabel('Display:')
        self.plotListBox = QComboBox()
        self.plotListBox.setMinimumWidth(200)
        availablePlots = ['Correlation Errors', 'Poisson Ratio']
        for plot in availablePlots:
            self.plotListBox.addItem(plot)
        self.plotListOptions = QComboBox()
        self.plotListOptions.setMinimumWidth(150)
        self.plotListCheckBox = QCheckBox('Only Active Images')
        self.plotListCheckBox.setContentsMargins(30,0,0,0)
        plotListLayout.addWidget(plotListLbl)
        plotListLayout.addWidget(self.plotListBox)
        plotListLayout.addWidget(self.plotListOptions)
        plotListLayout.addWidget(self.plotListCheckBox)

        matplotlibLayout = QHBoxLayout()
        matplotlibLayout.setContentsMargins(0,0,0,0)
        self.matplotlibPlot = DIC_Global.matplotlibWidget()
        self.matplotlibPlot.setContentsMargins(0,0,0,0)
        matplotlibLayout.addStretch(1)
        matplotlibLayout.addWidget(self.matplotlibPlot)
        matplotlibLayout.addStretch(1)
        self.plotListBox.currentIndexChanged.connect(self.plotOptions)
        self.plotListOptions.currentIndexChanged.connect(self.plotInfos)
        self.plotListCheckBox.stateChanged.connect(lambda: self.plotInfos(self.plotListOptions.currentIndex()))

        self.mainLayout.addWidget(infoFrame)
        self.mainLayout.addLayout(currentInfosLayout)
        self.mainLayout.addLayout(globalInfosLayout)
        self.mainLayout.addWidget(otherInfosLbl)
        self.mainLayout.addLayout(otherInfosLayout)
        self.mainLayout.addLayout(extraInfosLayout)
        self.mainLayout.addLayout(plotListLayout)
        self.mainLayout.addLayout(matplotlibLayout)
        self.plotOptions(0)

    def plotOptions(self, item):

        self.plotListOptions.clear()
        plotOptions = []
        if item == 0:
            plotOptions = ['All', 'Edge Area', 'Marker Out', 'NaN', 'No Std. Dev.', 'Outside SubPx.', 'Div. by 0', 'Low Corr.', 'Bad Peak']
        if item == 1:
            plotOptions = ['Compression/Extension along X', 'Compression/Extension along Y']
        for option in plotOptions:
            self.plotListOptions.addItem(option)
        self.plotInfos(0)

    def plotInfos(self, option):

        self.matplotlibPlot.matPlot.cla()
        plotType = self.plotListBox.currentIndex()
        onlyActives = self.plotListCheckBox.isChecked()
        activeImages = self.parent.analysisWidget.activeImages
        totalImages = self.parent.analysisWidget.nb_image

        if plotType == 0:
            self.plotListCheckBox.setEnabled(True)
            errorList = []
            legend = []
            if onlyActives:
                imageRange = len(activeImages)
            else:
                imageRange = totalImages
            if option == 0:
                errors = np.unique(self.markersInfos)
                for error in errors:
                    if error == 0:
                        continue
                    currentList = []
                    for image in range(imageRange):
                        if onlyActives:
                            imageNb = activeImages[image]
                            occurence = list(self.markersInfos[:,imageNb]).count(error)
                            for nb in range(occurence):
                                currentList.append(imageNb)
                        else:
                            occurence = list(self.markersInfos[:,image]).count(error)
                            for nb in range(occurence):
                                currentList.append(image)
                    if currentList != []:
                        legend.append(self.plotListOptions.itemText(error))
                    errorList.append(currentList)
            else:
                currentList = []
                for image in range(imageRange):
                    if onlyActives:
                        imageNb = activeImages[image]
                        occurence = list(self.markersInfos[:,imageNb]).count(option)
                        for nb in range(occurence):
                            currentList.append(imageNb)
                    else:
                        occurence = list(self.markersInfos[:,image]).count(option)
                        for nb in range(occurence):
                            currentList.append(image)
                if currentList != []:
                    legend.append(self.plotListOptions.itemText(option))
                    errorList.append(currentList)
            #errorList = np.array(errorList)
            nbList = len(np.atleast_1d(errorList))
            if nbList:
                self.matplotlibPlot.matPlot.hist(errorList, totalImages+1, range=(0, totalImages+1), align='right', histtype='bar', stacked=True, label=legend)
                if onlyActives is False:
                    self.matplotlibPlot.matPlot.plot(activeImages+np.ones_like(activeImages), np.zeros_like(activeImages), 'o', c='red')
                self.matplotlibPlot.matPlot.set_xlim([0.5,totalImages+0.5])
                self.matplotlibPlot.matPlot.set_ylim(bottom=0)
            else:
                ax = self.matplotlibPlot.matPlot
                ax.text(.5, .5, 'No error.', ha='center', va='center', transform = ax.transAxes, color='red')

        if plotType == 1:
            self.plotListCheckBox.setEnabled(False)
            nbImages = self.fileStrainX.shape[0]
            nbInstances = self.fileStrainX.shape[1]
            imageList = np.linspace(1, totalImages+1, totalImages, endpoint=False).astype(np.int)
            poissonRatio = np.zeros((nbInstances, nbImages))
            colors = ['blue', 'cornflowerblue', 'royalblue', 'navy']
            if option > 0:
                numerator = self.fileStrainX
                denominator = self.fileStrainY
            else:
                numerator = self.fileStrainY
                denominator = self.fileStrainX
            for instance in range(nbInstances):
                for image in range(len(activeImages)):
                    if denominator[image, instance] != 0:
                        poissonRatio[instance, image] = numerator[image, instance]/denominator[image, instance]
                    else:
                        poissonRatio[instance, image] = np.nan
                clr = colors[instance % 4]
                lbl = 'Instance '+str(instance)
                self.matplotlibPlot.matPlot.plot(activeImages, poissonRatio[instance, :], '-', color=clr, label=lbl)
                if nbInstances > 1:
                    self.matplotlibPlot.matPlot.legend()
        self.matplotlibPlot.draw_idle()
