# -*- coding: utf-8 -*-
"""
Created on 16/10/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: Defines the start-up process and load the interface
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from interface import menubar, profile
from functions import startOptions

def initProfile(self, PROFILE_FILE, DEFAULT_PROFILE):

    self.profileData = profile.readProfile(PROFILE_FILE, default=DEFAULT_PROFILE) #read the profile list and create a default profile if the PROFILE_FILE is not found
    count = -1
    for profiles in self.profileData['Default']: #select the default profile
        count+=1
        if int(profiles) == 1:
            break
    self.profilePath = PROFILE_FILE #link to the profile configuration file
    self.defaultProfile = DEFAULT_PROFILE #used when adding a new profile in profile management
    self.currentProfile = count #ID of the current loaded profile

def setUpInterface(self, currentProfile):

    FULL_SCREEN = int(self.profileData['FullScreen'][currentProfile])
    WIDTH = int(self.profileData['Width'][currentProfile])
    HEIGHT = int(self.profileData['Height'][currentProfile])
    USER = self.profileData['User'][currentProfile]

    if FULL_SCREEN == 1:
        self.setWindowState(Qt.WindowMaximized)
    self.setWindowTitle('Digital Image Correlation ('+USER+')')
    self.setMinimumWidth(WIDTH)
    self.setMinimumHeight(HEIGHT)
    self.setContentsMargins(0,0,0,0)

    menubar.createMenu(self)
    menubar.menuDisabled(self)

    firstWidget = defaultWidget(self)
    self.setCentralWidget(firstWidget)
    firstWidget.printMessage('What do you want to do today?')

    self.statusBar().setMaximumHeight(15)
    self.statusBar().showMessage('Welcome in Python_DIC')
    self.show()

class defaultWidget(QWidget):

    def __init__(self, parent):

        super(defaultWidget, self).__init__()

    #initiate Layout
        firstLayout = QVBoxLayout()
        firstLayout.setSpacing(30)
        firstLayout.setAlignment(Qt.AlignHCenter)

    #initiate Widget
        newAnalysis = QPushButton('New Analysis')
        newFont = newAnalysis.font()

        openAnalysis = QPushButton('Open Analysis')
        openFont = openAnalysis.font()

        self.messageLbl = QLabel()

    #configure Widgets
        newFont.setPointSize(12)
        newAnalysis.setFont(newFont)
        newAnalysis.setMinimumWidth(200)
        newAnalysis.setMinimumHeight(50)

        openFont.setPointSize(12)
        openAnalysis.setFont(openFont)
        openAnalysis.setMinimumWidth(200)
        openAnalysis.setMinimumHeight(50)

        self.messageLbl.setAlignment(Qt.AlignCenter)
        self.messageLbl.setMaximumHeight(30)
        self.messageLbl.setMinimumWidth(260)
        self.messageLbl.setAutoFillBackground(True)

    #Attribute functions
        newAnalysis.enterEvent = lambda x: self.smallEvent(newAnalysis, 'Correlate Images')
        newAnalysis.leaveEvent = lambda x: self.smallEvent(newAnalysis, 'New Analysis')
        newAnalysis.clicked.connect(lambda: startOptions.startNewAnalysis(parent))

        openAnalysis.enterEvent = lambda x: self.smallEvent(openAnalysis, 'Analyse Results')
        openAnalysis.leaveEvent = lambda x: self.smallEvent(openAnalysis, 'Open Analysis')
        openAnalysis.clicked.connect(lambda: startOptions.openPrevious(parent))

    #Applying Layout
        firstLayout.addWidget(newAnalysis)
        firstLayout.addWidget(openAnalysis)
        firstLayout.addWidget(self.messageLbl)

        self.setLayout(firstLayout)

    def printMessage(self, message, imp=0):

        p = self.messageLbl.palette()
        if imp != 0:
            p.setColor(self.messageLbl.backgroundRole(), Qt.red)
        else:
            p.setColor(self.messageLbl.backgroundRole(), Qt.transparent)
        self.messageLbl.setPalette(p)
        self.messageLbl.setText(message)

    def smallEvent(self, button, text):

        currentFont = button.font()
        button.setText(text)
        button.setFont(currentFont)
