# -*- coding: utf-8 -*-
"""
Created on 08/09/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: Allows the user to re-calculate the current grid neighbors
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np
from interface import progressWidget
from functions import initData

class newNeighborsDialog(QDialog):

    def __init__(self, parent):

        QDialog.__init__(self)

        self.setWindowTitle('Re-Calculate Neighbors')
        self.setMinimumWidth(600)

        nbNeighbors = len(parent.neighbors[0])
        activeMarkers = []
        for image in parent.activeMarkers:
            for marker in image:
                if marker not in activeMarkers:
                    activeMarkers.append(marker)
        nbActiveMarkers = len(np.atleast_1d(activeMarkers))

        dialogLayout = QVBoxLayout()

        dialogLabel = QLabel('Chose a minimum amount of neighbors for each marker.')
        dialogLabel.setAlignment(Qt.AlignCenter)

        spinBoxLayout = QHBoxLayout()
        self.nbNeighbors = QSpinBox()
        self.nbNeighbors.setMaximumWidth(200)
        self.nbNeighbors.setValue(nbNeighbors)
        self.nbNeighbors.setRange(1, nbActiveMarkers)
        spinBoxLayout.addStretch(1)
        spinBoxLayout.addWidget(self.nbNeighbors)
        spinBoxLayout.addStretch(1)

        dialogButtonLayout = QHBoxLayout()
        self.dialogButton = QPushButton('Start')
        self.dialogButton.setMaximumWidth(100)
        self.dialogButton.clicked.connect(lambda: self.startCalculation(parent, activeMarkers))
        dialogButtonLayout.addStretch(1)
        dialogButtonLayout.addWidget(self.dialogButton)
        dialogButtonLayout.addStretch(1)

        self.dialogProgress = progressWidget.progressBarWidget(minimumHeight=20, maximumHeight=30, minimumWidth=500, maximumWidth=500)

        dialogLayout.addWidget(dialogLabel)
        dialogLayout.addLayout(spinBoxLayout)
        dialogLayout.addLayout(dialogButtonLayout)
        dialogLayout.addWidget(self.dialogProgress)

        self.setLayout(dialogLayout)

    def startCalculation(self, parent, activeMarkers):

        self.dialogButton.setText('Calculating..')
        firstImage = parent.activeImages[0]
        data_x_init = parent.data_x[:,firstImage]
        data_y_init = parent.data_y[:,firstImage]
        minNeighbors = int(self.nbNeighbors.value())
        neighbors = initData.calculateNeighbors(activeMarkers, data_x_init, data_y_init, minNeighbors, parent.parentWindow.fileDataPath, progressBar=self.dialogProgress)
        parent.neighbors = neighbors
        self.dialogButton.setText('Done.')
        self.dialogButton.setDisabled(True)

def launchNeighborsDialog(self):

    self.calcNeighbors = newNeighborsDialog(self.analysisWidget)
    self.calcNeighbors.exec_()
