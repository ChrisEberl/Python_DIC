# -*- coding: utf-8 -*-
"""
Created on 08/11/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: Allows the user to re-calculate the current grid neighbors
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np, time
from interface import progressWidget
from functions import initData

class newNeighborsDialog(QDialog):

    def __init__(self, parent):

        QDialog.__init__(self)

        self.setWindowTitle('Re-Calculate Neighbors')
        self.setMinimumWidth(600)

        nbNeighbors = len(parent.neighbors[0])
        listMarkers = np.linspace(0, parent.nb_marker, parent.nb_marker, endpoint=False)
        nbMarkers = len(np.atleast_1d(listMarkers))

        dialogLayout = QVBoxLayout()

        dialogLabel = QLabel('Chose a minimum amount of neighbors for each marker.')
        dialogLabel.setAlignment(Qt.AlignCenter)

        spinBoxLayout = QHBoxLayout()
        self.nbNeighbors = QSpinBox()
        self.nbNeighbors.setMaximumWidth(200)
        self.nbNeighbors.setValue(nbNeighbors)
        self.nbNeighbors.setRange(1, nbMarkers)
        spinBoxLayout.addStretch(1)
        spinBoxLayout.addWidget(self.nbNeighbors)
        spinBoxLayout.addStretch(1)

        dialogButtonLayout = QHBoxLayout()
        self.dialogButton = QPushButton('Start')
        self.dialogButton.setMaximumWidth(200)
        self.dialogButton.clicked.connect(lambda: self.startCalculation(parent, listMarkers))
        dialogButtonLayout.addStretch(1)
        dialogButtonLayout.addWidget(self.dialogButton)
        dialogButtonLayout.addStretch(1)

        dialogProgressLayout = QHBoxLayout()
        self.dialogProgress = progressWidget.progressBarWidget(minimumHeight=20, maximumHeight=30, minimumWidth=200, maximumWidth=200)
        dialogProgressLayout.addStretch(1)
        dialogProgressLayout.addWidget(self.dialogProgress)
        dialogProgressLayout.addStretch(1)

        dialogLayout.addWidget(dialogLabel)
        dialogLayout.addLayout(spinBoxLayout)
        dialogLayout.addLayout(dialogButtonLayout)
        dialogLayout.addLayout(dialogProgressLayout)

        self.setLayout(dialogLayout)

    def startCalculation(self, parent, listMarkers):

        self.dialogButton.setText('Calculating..')
        firstImage = parent.activeImages[0]
        data_x_init = parent.data_x[:,firstImage]
        data_y_init = parent.data_y[:,firstImage]
        minNeighbors = int(self.nbNeighbors.value())
        neighbors = initData.calculateNeighbors(listMarkers, data_x_init, data_y_init, minNeighbors, parent.parentWindow.fileDataPath, progressBar=self.dialogProgress)
        parent.neighbors = neighbors
        self.dialogButton.setText('Done. Closing..')
        self.dialogButton.setDisabled(True)
        QTimer.singleShot(1500, self.close)


def launchNeighborsDialog(self):

    self.calcNeighbors = newNeighborsDialog(self.analysisWidget)
    self.calcNeighbors.exec_()
