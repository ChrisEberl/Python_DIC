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

REFRESH_TIME = 0.1

class progressBarWidget(QWidget): #Called for every time consuming operation / Embedded in a layout

    def __init__(self, minimumWidth = 400, maximumWidth = 600, minimumHeight = 100, maximumHeight = 150, title = ''):

        super(progressBarWidget, self).__init__()

        self.setMaximumWidth(maximumWidth)
        self.setMaximumHeight(maximumHeight)
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
        self.horizontalWidget.setContentsMargins(0,0,0,0)
        self.horizontalWidget.setMinimumHeight(40)
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

        self.initTime = 0
        self.percent = 0
        self.lastPercent = 0
        self.currentTitle = title
        self.lastTitle = title
        self.progressTimer = QTimer()
        self.progressTimer.timeout.connect(self.changeValue)
        self.progressTimer.start(REFRESH_TIME)


    def changeValue(self):

        percent = self.percent
        if self.initTime == 0:
            self.initTime = time.time()
        if self.currentTitle != self.lastTitle:
            self.progressTitle.setText(self.currentTitle)
        if percent != self.lastPercent:
            self.progressBar.setValue(percent)
            remainingTime = (time.time() - self.initTime)*(100-percent)/percent
            if remainingTime >= 60:
                remainingTime = remainingTime / 60
                if remainingTime - int(remainingTime) > 0.5:
                    self.timeValue.setText(str(int(remainingTime+1))+ ' minutes')
                else:
                    self.timeValue.setText(str(int(remainingTime))+ ' minutes and 30 secondes')
            elif remainingTime > 30 and remainingTime < 60:
                self.timeValue.setText('< 1 minute')
            else:
                self.timeValue.setText(str(int(remainingTime))+ ' secondes.')


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

        self.percent = 0
        self.lastPercent = 0
        self.currentTitle = labelText
        self.lastTitle = labelText
        self.progressTimer = QTimer()
        self.progressTimer.timeout.connect(self.changeValue)
        self.progressTimer.start(REFRESH_TIME)

    def changeValue(self):

        percent = self.percent
        if self.currentTitle != self.lastTitle:
            self.setLabelText(self.currentTitle)
        if percent != self.lastPercent:
            self.setValue(percent)
