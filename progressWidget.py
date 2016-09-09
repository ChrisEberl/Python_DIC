# -*- coding: utf-8 -*-
"""
Created on 13/05/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file manages the progress bars functions
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import time

class progressBarWidget(QWidget): #Called for every time consuming operation / Embedded in a layout

    def __init__(self, minimumWidth = 0, maximumWidth = 100, minimumHeight = 0, maximumHeight = 60, title = ''):

        super(progressBarWidget, self).__init__()

        self.setMaximumWidth(maximumWidth*1.1)
        self.setMaximumHeight(maximumHeight*2)
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignVCenter)
        self.layout.setAlignment(Qt.AlignHCenter)

        self.progressTitle = QLabel(title)

        self.progressBar = QProgressBar()
        self.progressBar.setMinimumWidth(minimumWidth)
        self.progressBar.setMaximumWidth(maximumWidth)
        self.progressBar.setMinimumHeight(minimumHeight)
        self.progressBar.setMaximumHeight(maximumHeight)

        self.horizontalWidget = QWidget()
        self.horizontalLayout = QHBoxLayout()
        self.timeLbl = QLabel('Remaining Time :')
        self.timeValue = QLabel('-')
        self.horizontalLayout.addWidget(self.timeLbl)
        self.horizontalLayout.addWidget(self.timeValue)
        self.horizontalWidget.setLayout(self.horizontalLayout)

        self.layout.addWidget(self.progressTitle)
        self.layout.addWidget(self.progressBar)
        self.layout.addWidget(self.horizontalWidget)

        self.setLayout(self.layout)

        self.initTime = time.time()


    def changeValue(self, percent, text=None):

        self.progressBar.setValue(percent)
        if text is not None:
            self.progressTitle.setText(text)
        if percent != 0:
            self.remainingTime = (time.time() - self.initTime)*(100-percent)/percent
            self.timeValue.setText(str(self.remainingTime))


class progressBarDialog(QProgressDialog): #Called for every time consuming operation / Separated Window Dialog

    def __init__(self, labelText, cancel=None):

        super(progressBarDialog, self).__init__()

        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.setLabelText(labelText)
        self.setCancelButton(cancel)
        self.setModal(True)
        self.setMinimum(0)
        self.setMaximum(100)
        self.setMinimumDuration(1000)
        self.setValue(0)

    def changeValue(self, percent, text=None):

        if percent > 0:
            self.setValue(percent)
        if text is not None:
            self.setLabelText(text)
