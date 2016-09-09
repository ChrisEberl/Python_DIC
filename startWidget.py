# -*- coding: utf-8 -*-
"""
Created on 30/03/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file manages the start-up event
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import fileList

def StartWidget(self, parent, message):

    welcome = QVBoxLayout()
    welcome.setSpacing(30)
    welcome.setAlignment(Qt.AlignHCenter)

    new = QPushButton('New Analysis')
    newFont = new.font()
    newFont.setPointSize(12)
    new.setFont(newFont)
    new.setMinimumWidth(200)
    new.setMinimumHeight(50)
    new.enterEvent = lambda x: testEvent(new, 'Correlate Images')
    new.leaveEvent = lambda x: testEvent(new, 'New Analysis')

    openFile = QPushButton('Open Analysis')
    openFont = openFile.font()
    openFont.setPointSize(12)
    openFile.setFont(openFont)
    openFile.setMinimumWidth(200)
    openFile.setMinimumHeight(50)
    openFile.enterEvent = lambda x: testEvent(openFile, 'Analyse Results')
    openFile.leaveEvent = lambda x: testEvent(openFile, 'Open Analysis')


    welcome.addWidget(new)
    welcome.addWidget(openFile)

    if message is not None:
        messageLbl = QLabel(message)
        messageLbl.setAlignment(Qt.AlignCenter)
        messageLbl.setMaximumHeight(30)
        messageLbl.setMinimumWidth(260)
        p = messageLbl.palette()
        p.setColor(messageLbl.backgroundRole(), Qt.red)
        messageLbl.setAutoFillBackground(True)
        messageLbl.setPalette(p)
        welcome.addWidget(messageLbl)

    new.clicked.connect(lambda: fileList.generateFileList(parent))
    openFile.clicked.connect(lambda: fileList.openFileList(parent))

    self.setLayout(welcome)

def testEvent(button, text):

    currentFont = button.font()
    button.setText(text)
    button.setFont(currentFont)
