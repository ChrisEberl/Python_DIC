# -*- coding: utf-8 -*-
"""
Created on 21/07/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file manages dialog to mask images from the current analysis
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np, copy
from functions import masks
from interface import progressWidget

class deleteImageDialog(QDialog):

    def __init__(self, fileNameList, activeImages, parent):

        QDialog.__init__(self)

        self.fileNameList = fileNameList
        currentMask = copy.deepcopy(parent.currentMask)

        self.setWindowTitle('Mask Images')
        self.setMinimumWidth(300)

        dialogLayout = QVBoxLayout()

        dialogLabel = QLabel('Select images you want to mask from the current analysis.')

        self.dialogListWidget = QListWidget()
        self.dialogListWidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.dialogListWidget.itemSelectionChanged.connect(self.refreshLbl)

        for image in activeImages:
            currentImage = QListWidgetItem(fileNameList[image])
            self.dialogListWidget.addItem(currentImage)

        selectedLayout = QHBoxLayout()
        selectedLabel = QLabel('Total selection: ')
        self.selectedValueLbl = QLabel('0')
        selectedLayout.addStretch(1)
        selectedLayout.addWidget(selectedLabel)
        selectedLayout.addWidget(self.selectedValueLbl)
        selectedLayout.addStretch(1)

        buttonLayout = QHBoxLayout()
        dialogButton = QPushButton('Mask Images')
        dialogButton.setMaximumWidth(100)
        dialogButton.clicked.connect(lambda: self.deleteSelection(currentMask, activeImages, parent))
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(dialogButton)
        buttonLayout.addStretch(1)

        dialogLayout.addWidget(dialogLabel)
        dialogLayout.addWidget(self.dialogListWidget)
        dialogLayout.addLayout(selectedLayout)
        dialogLayout.addLayout(buttonLayout)

        self.setLayout(dialogLayout)

    def deleteSelection(self, currentMask, activeImages, parent):


        selectedItems = self.dialogListWidget.selectedItems()
        nbSelected = len(selectedItems)
        if nbSelected > 0:

            indicesToDelete = []
            for element in selectedItems:
                indicesToDelete.append(self.dialogListWidget.row(element))

            currentMask[:, np.array(activeImages)[indicesToDelete]] = 0

            if masks.generateMask(currentMask, parent.parentWindow.fileDataPath) is not None:
                progressBar = progressWidget.progressBarDialog('Saving masks..')
                masks.maskData(parent, currentMask, progressBar)
                self.close()


    def refreshLbl(self):

        nbSelected = len(self.dialogListWidget.selectedItems())
        self.selectedValueLbl.setText(str(nbSelected))



def launchDeleteImageDialog(self):

    self.analysisWidget.parentWindow.devWindow.addInfo('Cleaning Procedure Request : Delete Images')


    self.deleteImg = deleteImageDialog(self.analysisWidget.fileNameList, self.analysisWidget.activeImages, self.analysisWidget)


    self.deleteImg.exec_()
