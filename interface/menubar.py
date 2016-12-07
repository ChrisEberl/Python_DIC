# -*- coding: utf-8 -*-
"""
Created on 21/03/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file manages the menubar and create menus and actions
"""

from PyQt4.QtGui import *
from functions import startOptions, masks
from interface import profile, dispVsPos, relativeNeighborsDialog, deleteImages, maskInstances, analysisInfos, maskMarkers, newNeighbors, newCoordinates

def createMenuActions(self):

    #fileMenu Actions
    self.newAction = QAction('New Analysis', self)
    self.openAction = QAction('Open', self)
    self.openGrid = QAction('Open Grid', self)
    self.openFilter = QAction('Open Filter', self)
    self.openMask = QAction('Open Mask/Version', self)
    self.exitAction = QAction('Exit', self)

    #profile Actions
    self.listProfiles = []
    for profiles in self.profileData['User']:
        self.listProfiles.append(QAction(profiles, self))

    self.manageProfile = QAction('Manage Profiles', self)

    #maskMenu Actions
    self.maskInstances = QAction('Manage Grids', self)
    self.deleteImages = QAction('Mask Images', self)
    self.deleteMarkers = QAction('Mask Markers', self)
    self.dispPos = QAction('Disp. vs Position', self)
    self.relativeDisp = QAction('Relative Neighbors Disp.', self)

    #moreMenu
    self.analysisInfos = QAction('Analysis Infos', self)
    self.newNeighborsCalc = QAction('Re-calculate Neighbors', self)
    self.newCoordinatesCalc = QAction('New Coordinates', self)


    #Actions Parameters
    self.newAction.setShortcut('Ctrl+N')
    self.openAction.setShortcut('Ctrl+O')
    self.exitAction.setShortcut('Ctrl+Q')

    self.newAction.setStatusTip('Open an image to create a new analysis.')
    self.openAction.setStatusTip('Open a previous analysis.')
    self.exitAction.setStatusTip('Exit the application.')
    self.openGrid.setStatusTip('Load previously created grids from another analysis.')
    self.openFilter.setStatusTip('Load previously created filters from another analysis.')
    self.openMask.setStatusTip('Open another version of the current analysis or a mask from another analysis.')
    self.maskInstances.setStatusTip('Temporarily hide grid instances from your analysis.')
    self.deleteImages.setStatusTip('Select images to mask in the current analysis.')
    self.deleteMarkers.setStatusTip('Manually select markers to mask on images.')
    self.dispPos.setStatusTip('Plot displacement versus position and mask selected markers.')
    self.relativeDisp.setStatusTip('Plot relative neighbors displacement over all the images and mask jumpers.')
    self.analysisInfos.setStatusTip('Get detailed informations on the current analysis.')
    self.newNeighborsCalc.setStatusTip = ('Update the current markers neighbors list.')
    self.newCoordinatesCalc.setStatusTip = ('Re-calculate the mapped plot coordinates.')

    #Actions Triggers
    self.newAction.triggered.connect(lambda: startOptions.startNewAnalysis(self))
    self.openAction.triggered.connect(lambda: startOptions.openPrevious(self))
    self.exitAction.triggered.connect(self.close)
    self.openGrid.triggered.connect(lambda: self.centralWidget().openGrid())
    self.openFilter.triggered.connect(lambda: self.centralWidget().openFilter())
    self.openMask.triggered.connect(lambda: masks.openMaskRequest(self))
    self.maskInstances.triggered.connect(lambda: maskInstances.launchMaskGridDialog(self))
    self.deleteImages.triggered.connect(lambda: deleteImages.launchDeleteImageDialog(self))
    self.deleteMarkers.triggered.connect(lambda: maskMarkers.launchMaskDialog(self, int(self.analysisWidget.controlWidget.imageNumber.text())))
    self.dispPos.triggered.connect(lambda: dispVsPos.launchDVPDialog(self, int(self.analysisWidget.controlWidget.imageNumber.text())))
    self.relativeDisp.triggered.connect(lambda: relativeNeighborsDialog.launchRNDialog(self))
    self.analysisInfos.triggered.connect(lambda: analysisInfos.launchDialog(self))
    self.newNeighborsCalc.triggered.connect(lambda: newNeighbors.launchNeighborsDialog(self))
    self.newCoordinatesCalc.triggered.connect(lambda: newCoordinates.launchCoordinatesDialog(self))

    self.manageProfile.triggered.connect(lambda: profile.manageProfile(self))


def createMenu(self):

    self.menubar = self.menuBar()
    #create Menus
    fileMenu = self.menubar.addMenu('File')
    masksMenu = self.menubar.addMenu('Masks')
    moreMenu = self.menubar.addMenu('More')

    createMenuActions(self) #generate Actions with function

    #add created Actions to Menus
    fileMenu.addAction(self.newAction)
    fileMenu.addAction(self.openAction)
    fileMenu.addSeparator()
    fileMenu.addAction(self.openGrid)
    fileMenu.addAction(self.openFilter)
    fileMenu.addAction(self.openMask)
    fileMenu.addSeparator()
    profileMenu = fileMenu.addMenu('Profile')

    profileActionGroup = QActionGroup(self)
    for profiles in self.listProfiles: #add profile actions to profile menu
        profiles.setCheckable(True)
        profileActionGroup.addAction(profiles)
        profileMenu.addAction(profiles)
        if self.profileData['User'][self.currentProfile] == profiles.text():
            profiles.setChecked(True)
    profileMenu.addSeparator()
    profileMenu.addAction(self.manageProfile)

    profileActionGroup.triggered.connect(lambda: profile.changeProfile(self, profileActionGroup.checkedAction().text()))
    fileMenu.addSeparator()
    fileMenu.addAction(self.exitAction)

    masksMenu.addAction(self.maskInstances)
    masksMenu.addSeparator()
    masksMenu.addAction(self.deleteImages)
    masksMenu.addSeparator()
    masksMenu.addAction(self.deleteMarkers)
    masksMenu.addAction(self.dispPos)
    masksMenu.addAction(self.relativeDisp)

    moreMenu.addAction(self.analysisInfos)
    moreMenu.addAction(self.newNeighborsCalc)
    moreMenu.addAction(self.newCoordinatesCalc)

    #disabled actions
    menuDisabled(self)

def menuDisabled(parent):

    parent.deleteMarkers.setDisabled(True)
    parent.dispPos.setDisabled(True)
    parent.openMask.setDisabled(True)
    parent.relativeDisp.setDisabled(True)
    parent.openGrid.setDisabled(True)
    parent.openFilter.setDisabled(True)
    parent.deleteImages.setDisabled(True)
    parent.maskInstances.setDisabled(True)
    parent.analysisInfos.setDisabled(True)
    parent.newNeighborsCalc.setDisabled(True)
    parent.newCoordinatesCalc.setDisabled(True)

def menuEnabled(parent): #menu enabled when analysis is open

    parent.deleteMarkers.setEnabled(True)
    parent.dispPos.setEnabled(True)
    parent.openMask.setEnabled(True)
    parent.relativeDisp.setEnabled(True)
    parent.deleteImages.setEnabled(True)
    parent.maskInstances.setEnabled(True)
    parent.analysisInfos.setEnabled(True)
    parent.newNeighborsCalc.setEnabled(True)
    parent.newCoordinatesCalc.setEnabled(True)

def menuCreateGridEnabled(parent): #menu enabled when creating a grid

    parent.openGrid.setEnabled(True)
    parent.openFilter.setEnabled(True)
