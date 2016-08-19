# -*- coding: utf-8 -*-
"""
Created on 05/07/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file manages the developer mode - NOT TESTED COMPLETELY
"""

from PySide.QtGui import *
from PySide.QtCore import *


class DevMode(QDockWidget): #dockWidget used in DevMode to display more informations to the developer
    
    def __init__(self, Mode):
        
        super(DevMode, self).__init__()
        
        self.devMode = Mode
        
        if self.devMode == 1:
            self.devWidget = QWidget()
            self.devWidget.setMaximumHeight(100)
            self.devLayout = QVBoxLayout()
            self.label = QLabel('Welcome in Dev. Mode')
            self.textInfo = QTextEdit()
            self.textInfo.setReadOnly(True)
            self.devInfo = self.textInfo
            self.devInfo.verticalScrollBar().rangeChanged.connect(self.ResizeScroll) #auto-scroll down 
            self.devLayout.addWidget(self.label)
            self.devLayout.addWidget(self.textInfo)
            self.devWidget.setLayout(self.devLayout)
            self.setWidget(self.devWidget)
            #self.show()
            self.addInfo('Application started.')
        else:
            self.setHidden(True)
            
    def ResizeScroll(self, min, maxi): #auto-scroll down function for DevMode
        self.devInfo.verticalScrollBar().setValue(maxi)
        
    def addInfo(self, message, statusBar=None):
        
        if self.devMode == 1:
            self.devInfo.append(message) #add the message to the developer widget if the devMode is activated
        if statusBar is not None:
            statusBar.showMessage(message) #add the message in the statusBar for the used if statusBar specified
