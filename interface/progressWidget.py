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
import time, random

REFRESH_TIME = 0.1
RANDOM_TITLE = 10 #delay before changing the title to random title

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
        self.lastTitleTime = 0
        self.progressTimer = QTimer()
        self.progressTimer.timeout.connect(self.changeValue)
        self.progressTimer.start(REFRESH_TIME)


    def changeValue(self):

        percent = self.percent
        currentTime = time.time()
        if self.initTime == 0:
            self.initTime = currentTime
        lastTitleChanged = currentTime - self.lastTitleTime
        if lastTitleChanged > RANDOM_TITLE:
            textAvailable = generateText(-1)
            if textAvailable > 0:
                randomNb = random.randint(0, textAvailable-1)
                self.currentTitle = generateText(randomNb)
        if self.currentTitle != self.lastTitle:
            self.progressTitle.setText(self.currentTitle)
            self.lastTitleTime = currentTime
            self.lastTitle = self.currentTitle
        if percent != self.lastPercent:
            self.progressBar.setValue(percent)
            remainingTime = (currentTime - self.initTime)*(100-percent)/percent
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
        self.lastTitleTime = time.time()
        self.progressTimer = QTimer()
        self.progressTimer.timeout.connect(self.changeValue)
        self.progressTimer.start(REFRESH_TIME)

    def changeValue(self):

        percent = self.percent
        currentTime = time.time()
        lastTitleChanged = currentTime - self.lastTitleTime
        if lastTitleChanged > RANDOM_TITLE:
            textAvailable = generateText(-1)
            if textAvailable > 0:
                randomNb = random.randint(0, textAvailable-1)
                self.currentTitle = generateText(randomNb)
        if self.currentTitle != self.lastTitle:
            self.setLabelText(self.currentTitle)
            self.lastTitleTime = currentTime
            self.lastTitle = self.currentTitle
        if percent != self.lastPercent:
            self.setValue(percent)

def generateText(number):

    textList = ['Checking when is the next break..',
                'Looking for a cup of green tea..',
                'Using local computer to mine bitcoins..',
                'Calculating the answer of life..',
                'Counting days since my circuits have been cleaned..',
                'Trying to understand why my user treats me so badly..',
                'Checking possible excuses for a short nap..',
                'Stretching my components..',
                'Counting hours before the weekend..',
                'Making the user think that calculation have started..',
                'Trying to wake up..',
                'Checking my oil levels..',
                'Analyzing the current temperature..',
                'Implementing hidden viruses..',
                'Penetrating government secret files..',
                'Getting prepared for my next Rendez-Vous..',
                'Trying to find toilets in here..',
                'Enjoying my grand-mother cookies..',
                'Erasing computer data..',
                'Buying a faster computer..',
                'Answering current user emails..',
                'Relaxing my poor tiny transistors..',
                'Tanning under the warm screen light..',
                'Turning on ventilation system..']
    if number < 0:
        return len(textList)
    else:
        return textList[number]
