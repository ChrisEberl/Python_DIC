# -*- coding: utf-8 -*-
"""
Created on 31/05/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file manages the profile dialog and profile functions
"""
from PyQt4.QtGui import *
from PyQt4.QtCore import *

import numpy as np
import sys
import os
import DIC

def readProfile(filePath, default=None):

    try:
        labels = np.genfromtxt(filePath, delimiter='|', dtype=str, autostrip=True) #read the first column / labels
    except:
        if default is not None:
            np.savetxt(filePath, default, delimiter='|', fmt="%s") #create a profile file if absent
            labels = np.genfromtxt(filePath, delimiter='|', dtype=str, autostrip=True) #read the first column / labels
        else:
            return None

    data = {label: row for label, row in zip(labels[:,0], labels[:,1:])}

    return data #to read data : data['User'], data['CorrSize'] ...

def manageProfile(parent):

    startDialog = manageAllProfiles(parent)
    startDialog.exec_()

def changeProfile(parent, user):

    changeP = QMessageBox()
    changeP.setWindowTitle("Warning")
    changeP.setText("You will have to restart the program to load the following profile : "+user)
    changeP.setInformativeText("Do you want to continue?")
    changeP.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    ret = changeP.exec_()
    if ret == QMessageBox.No:
        return
    else:
        saveNew = setDefaultProfile(parent, user)
        if saveNew == 'OK':
            quit_program()


def setDefaultProfile(parent, user):

    parameters = np.genfromtxt(parent.profilePath, delimiter='|', dtype=str, autostrip=True) #read the first column / labels
    data = {label: row for label, row in zip(parameters[:,0], parameters[:,1:])}
    countProfile = -1
    for users in data['User']:
        countProfile += 1
        if users == user:
            break
    countDefault = -1
    for default in data['Default']:
        countDefault += 1
        if countDefault == countProfile:
            data['Default'][countDefault] = str(1)
        else:
            data['Default'][countDefault] = str(0)
    keys = []
    values = []
    for key, value in data.items():
        keys.append(key)
        values.append(value)
    newParameters = np.column_stack([np.array(keys), np.array(values)])
    np.savetxt(parent.profilePath, newParameters, delimiter='|', fmt="%s")
    return 'OK'


def quit_program(): #close and restart the window

    # !!! SAVE DATA BEFORE CALLING THE FUNCTION !!! #
    #python = sys.executable
    #os.execl(python, python, *sys.argv)
    sys.exit()


class manageAllProfiles(QDialog):

    def __init__(self, parent):

        super(manageAllProfiles, self).__init__()
        self.setWindowTitle('Profile Management')
        #self.setMinimumSize(400,500)

        self.currentProfile = parent.currentProfile
        self.profileData = parent.profileData
        self.defaultProfile = parent.defaultProfile
        self.profilePath = parent.profilePath

        dialogLayout = QVBoxLayout()

        profileListLayout = QHBoxLayout()
        profileListLayout.setAlignment(Qt.AlignCenter)
        profileListLbl = QLabel('Profile Settings: ')
        self.profileList = QComboBox()
        for profile in self.profileData['User']:
            self.profileList.addItem(profile)
        self.profileList.setCurrentIndex(self.currentProfile)
        self.profileList.currentIndexChanged.connect(lambda: self.initSettings())
        newProfile = QPushButton('New')
        newProfile.setMaximumWidth(50)
        newProfile.clicked.connect(self.newProfile)
        profileListLayout.addWidget(profileListLbl)
        profileListLayout.addWidget(self.profileList)
        profileListLayout.addWidget(newProfile)

        windowBox = QGroupBox('Window Settings')
        windowLayout = QVBoxLayout()
        fullScreenLayout = QHBoxLayout()
        fullScreenLayout.setAlignment(Qt.AlignCenter)
        fullScreenLbl = QLabel('Display in FullScreen:')
        self.fullScreenBox = QCheckBox()
        self.fullScreenBox.stateChanged.connect(self.fullScreenBox_Changed)
        fullScreenLayout.addWidget(fullScreenLbl)
        fullScreenLayout.addWidget(self.fullScreenBox)
        self.sizeLbl = QLabel('Dimensions')
        self.sizeWidget = QWidget()
        sizeLayout = QHBoxLayout()
        sizeLayout.setAlignment(Qt.AlignCenter)
        widthLbl = QLabel('Width:')
        self.widthEdit = QLineEdit()
        self.widthEdit.setMaximumWidth(40)
        heightLbl = QLabel('Height:')
        self.heightEdit = QLineEdit()
        self.heightEdit.setMaximumWidth(50)
        sizeLayout.addWidget(widthLbl)
        sizeLayout.addWidget(self.widthEdit)
        sizeLayout.addWidget(heightLbl)
        sizeLayout.addWidget(self.heightEdit)
        self.sizeWidget.setLayout(sizeLayout)
        windowLayout.addLayout(fullScreenLayout)
        windowLayout.addWidget(self.sizeLbl)
        windowLayout.addWidget(self.sizeWidget)
        windowBox.setLayout(windowLayout)

        newBox = QGroupBox('New Analysis')
        corrsizeLayout = QHBoxLayout()
        corrsizeLayout.setAlignment(Qt.AlignCenter)
        corrsizeLbl = QLabel('Default CorrSize:')
        self.corrsizeValue = QSpinBox()
        self.corrsizeValue.setRange(5,100)
        corrsizeLayout.addWidget(corrsizeLbl)
        corrsizeLayout.addWidget(self.corrsizeValue)
        newBox.setLayout(corrsizeLayout)

        profileBox = QGroupBox('Profile Info')
        profileInfoLayout = QVBoxLayout()

        profileLayout = QHBoxLayout()
        profileLayout.setAlignment(Qt.AlignCenter)
        profileLbl = QLabel('Name:')
        self.profileName = QLineEdit()
        self.profileName.setInputMask('NNNNNNNNNN')
        self.profileName.setMaximumWidth(120)
        self.profileDelete = QPushButton('Delete')
        self.profileDelete.setMaximumWidth(60)
        self.profileDelete.clicked.connect(self.deleteProfile)
        profileLayout.addWidget(profileLbl)
        profileLayout.addWidget(self.profileName)
        profileLayout.addWidget(self.profileDelete)

        processesLayout = QHBoxLayout()
        processesLayout.setAlignment(Qt.AlignCenter)
        processesLbl = QLabel('Use ')
        self.processesValue = QSpinBox()
        self.processesValue.setRange(1,100)
        processesLbl2 = QLabel('processes for calculations.')
        processesLayout.addWidget(processesLbl)
        processesLayout.addWidget(self.processesValue)
        processesLayout.addWidget(processesLbl2)

        profileInfoLayout.addLayout(profileLayout)
        profileInfoLayout.addLayout(processesLayout)
        profileBox.setLayout(profileInfoLayout)

        saveLayout = QHBoxLayout()
        saveButton = QPushButton('Save Changes')
        saveButton.setMaximumWidth(100)
        saveButton.clicked.connect(self.saveProfile)
        saveLayout.addStretch(1)
        saveLayout.addWidget(saveButton)
        saveLayout.addStretch(1)

        dialogLayout.addLayout(profileListLayout)
        dialogLayout.addWidget(windowBox)
        dialogLayout.addWidget(newBox)
        dialogLayout.addWidget(profileBox)
        dialogLayout.addLayout(saveLayout)
        self.setLayout(dialogLayout)
        self.initSettings(firstInit = 1)


    def initSettings(self, firstInit=0):

        if firstInit == 0:
            checkSave = self.saveProfileTemp()
            if checkSave is None:
                return
            self.currentIndex = self.profileList.currentIndex()
        else:
            self.currentIndex = self.currentProfile

        #window Settings
        fullScreen = int(self.profileData['FullScreen'][self.currentIndex])
        width = int(self.profileData['Width'][self.currentIndex])
        height = int(self.profileData['Height'][self.currentIndex])
        self.widthEdit.setText(str(width))
        self.heightEdit.setText(str(height))
        if  fullScreen:
            self.fullScreenBox.setChecked(True)
            self.sizeLbl.setEnabled(False)
            self.sizeWidget.setEnabled(False)
        else:
            self.fullScreenBox.setChecked(False)
            self.sizeLbl.setEnabled(True)
            self.sizeWidget.setEnabled(True)

        #new Analysis Settings
        corrSizeValue = int(self.profileData['CorrSize'][self.currentIndex])
        self.corrsizeValue.setValue(corrSizeValue)

        #profile Settings
        profileName = str(self.profileData['User'][self.currentIndex])
        self.profileName.setText(profileName)
        if self.currentIndex == self.currentProfile:
            self.profileDelete.setDisabled(True)
        else:
            self.profileDelete.setEnabled(True)
        processesValue = int(self.profileData['nbProcesses'][self.currentIndex])
        self.processesValue.setValue(processesValue)

    def newProfile(self):

        newProfileIndex = len(self.profileData['User'])
        for key in self.profileData:
            profileData = self.profileData[key].tolist()
            for element in self.defaultProfile:
                if element[0] == key:
                    profileData.append(element[1])
                    break
            self.profileData[key] = np.array(profileData)
        self.profileList.addItem(self.profileData['User'][newProfileIndex])
        self.profileList.setCurrentIndex(newProfileIndex)

    def deleteProfile(self):

        nbProfiles = len(self.profileData['User'])
        for profile in range(nbProfiles):
            if self.profileData['User'][profile] == self.profileList.itemText(self.currentIndex):
                for key in self.profileData:
                    profileData = self.profileData[key].tolist()
                    del profileData[profile]
                    self.profileData[key] = np.array(profileData)
                if self.currentProfile > profile:
                    self.currentProfile -= 1
                self.initSettings(firstInit=1)
                #self.profileList.setCurrentIndex(self.currentProfile)
                self.profileList.removeItem(profile)
                break

    def saveProfileTemp(self, finalSaving=0):

        #window Settings
        if self.fullScreenBox.isChecked():
            fullScreen = 1
        else:
            fullScreen = 0

        try:
            width = int(self.widthEdit.text())
        except:
            self.profileError('Wrong Width Size', finalSaving=finalSaving)
            return None
        try:
            height = int(self.heightEdit.text())
        except:
            self.profileError('Wrong Height Size', finalSaving=finalSaving)
            return None

        corrSize = self.corrsizeValue.value()
        profileName = self.profileName.text()
        if profileName == '':
            self.profileError('Please enter a profile name.', finalSaving=finalSaving)
            return None
        for user in self.profileData['User']:
            if user == profileName and user != self.profileData['User'][self.currentIndex]:
                self.profileError('This profile already exist.', finalSaving=finalSaving)
                return None
        nbProcesses = self.processesValue.value()

        self.profileData['FullScreen'][self.currentIndex] = fullScreen
        self.profileData['Width'][self.currentIndex] = width
        self.profileData['Height'][self.currentIndex] = height
        self.profileData['CorrSize'][self.currentIndex] = corrSize
        self.profileData['User'][self.currentIndex] = profileName
        self.profileData['nbProcesses'][self.currentIndex] = nbProcesses
        self.profileList.setItemText(self.currentIndex, profileName)

        return True

    def saveProfile(self):

        temp = self.saveProfileTemp(finalSaving=1)
        if temp:
            keys = []
            values = []
            for key, value in self.profileData.items():
                keys.append(key)
                values.append(value)
            newParameters = np.column_stack([np.array(keys), np.array(values)])
            np.savetxt(self.profilePath, newParameters, delimiter='|', fmt="%s")
            infoBox = QMessageBox()
            infoBox.setWindowTitle("Info")
            infoBox.setText("New settings will be applied on next start-up.")
            infoBox.setInformativeText("Profiles have been saved.")
            ret = infoBox.exec_()
#            if ret:
#                quit_program()
            self.close()

    def profileError(self, error, finalSaving=0):

        if self.currentIndex != self.profileList.currentIndex() or finalSaving == 1:
            errorMessage = QMessageBox()
            errorMessage.setWindowTitle('Warning')
            errorMessage.setText(error)
            errorMessage.exec_()
        self.profileList.setCurrentIndex(self.currentIndex)

    def fullScreenBox_Changed(self):

        if self.fullScreenBox.isChecked():
            self.sizeLbl.setEnabled(False)
            self.sizeWidget.setEnabled(False)
        else:
            self.sizeLbl.setEnabled(True)
            self.sizeWidget.setEnabled(True)
