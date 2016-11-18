"""
Created on 18/11/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: Allows the user to re-calculate the current 2D mapped coordinates
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np
from interface import progressWidget
from functions import initData, masks, DIC_Global

class newCoordinatesDialog(QDialog):

    def __init__(self, parent):

        QDialog.__init__(self)

        self.setWindowTitle('Re-Calculate Coordinates')
        self.setMinimumWidth(600)

        dialogLayout = QVBoxLayout()

        dialogLabel = QLabel('Which coordinates do you want to re-calculate?')
        dialogLabel.setAlignment(Qt.AlignCenter)

        checkBoxLayout = QHBoxLayout()
        self.corrBox = QCheckBox('Correlation 2D')
        self.xStrainBox = QCheckBox('2D Local Strain (X)')
        self.yStrainBox = QCheckBox('2D Local Strain (Y)')
        self.corrBox.setChecked(True)
        self.xStrainBox.setChecked(True)
        self.yStrainBox.setChecked(True)
        checkBoxLayout.addWidget(self.corrBox)
        checkBoxLayout.addWidget(self.xStrainBox)
        checkBoxLayout.addWidget(self.yStrainBox)

        dialogButtonLayout = QHBoxLayout()
        self.dialogButton = QPushButton('Calculate')
        self.dialogButton.setMaximumWidth(100)
        self.dialogButton.clicked.connect(lambda: self.startCalculation(parent))
        dialogButtonLayout.addStretch(1)
        dialogButtonLayout.addWidget(self.dialogButton)
        dialogButtonLayout.addStretch(1)

        dialogLayout.addWidget(dialogLabel)
        dialogLayout.addLayout(checkBoxLayout)
        dialogLayout.addLayout(dialogButtonLayout)

        self.setLayout(dialogLayout)

    def startCalculation(self, parent):

        recalculateCoordinates = [self.corrBox.isChecked(), self.xStrainBox.isChecked(), self.yStrainBox.isChecked()]
        progressBar = progressWidget.progressBarDialog('Starting calculation...')
        self.close()
        calculatingThread = DIC_Global.createThread(parent.parentWindow, [parent, progressBar, parent.currentMask, recalculateCoordinates], initData.initPlottedData, signal=1)
        calculatingThread.signal.threadSignal.connect(lambda: masks.newMasksCalculated(parent, progressBar))
        calculatingThread.start()

def launchCoordinatesDialog(self):

    self.calcCoordinates = newCoordinatesDialog(self.analysisWidget)
    self.calcCoordinates.exec_()
