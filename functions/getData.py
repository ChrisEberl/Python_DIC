# -*- coding: utf-8 -*-
"""
Created on 05/04/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file manages the analysis files and open/generate data from them
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import csv, os, numpy as np, time, multiprocessing, pandas
from math import sqrt
from functions import DIC_Global, filterFunctions, initData


def openData(parentWindow, progressBar, parent): #parent contains the Thread in which the opening is made

    dataList = generateData(parentWindow, progressBar)
    if dataList is not None:
        parentWindow.devWindow.addInfo('Data extracted from files. Preparing the calculation.')
        parent.signal.threadSignal.emit(dataList)
    else:
        parent.signal.threadSignal.emit([0])
    return

def generateData(parentWindow, progressBar):

    #Opening main files
    progressBar.currentTitle = "Opening validx.csv"
    data_x = testReadFile(parentWindow.fileDataPath+'/validx.csv')
    progressBar.currentTitle = "Opening validy.csv"
    progressBar.percent = 15
    data_y = testReadFile(parentWindow.fileDataPath+'/validy.csv')
    progressBar.currentTitle = "Opening corrcoef.csv"
    progressBar.percent = 30
    data_corr = testReadFile(parentWindow.fileDataPath+'/corrcoef.csv')
    progressBar.currentTitle = "Opening stdx.csv"
    progressBar.percent = 45
    data_stdx = testReadFile(parentWindow.fileDataPath+'/stdx.csv')
    progressBar.currentTitle = "Opening stdy.csv"
    progressBar.percent = 60
    data_stdy = testReadFile(parentWindow.fileDataPath+'/stdy.csv')
    progressBar.currentTitle = "Opening dispx.csv"
    progressBar.percent = 75
    disp_x = testReadFile(parentWindow.fileDataPath+'/dispx.csv')
    progressBar.currentTitle = "Opening dispy.csv"
    progressBar.percent = 90
    disp_y = testReadFile(parentWindow.fileDataPath+'/dispy.csv')
    if data_x is None or data_y is None or data_corr is None or data_stdx is None or data_stdy is None or disp_x is None or disp_y is None:
        return None

    progressBar.currentTitle = "Finishing preparation..."
    filenamelist = []
    filenamelistRead = testReadFile(parentWindow.fileDataPath+'/filenamelist.csv', lib=1)
    if filenamelistRead is None:
        return None
    else:
        for row in filenamelistRead:
            filenamelist.append(row.decode(encoding='utf-8'))

    grid_entities = testReadFile(parentWindow.fileDataPath+'/gridx.csv')
    if grid_entities is None:
        return None

    temp_grid_instances = []
    for (coor, instance) in grid_entities:
        temp_grid_instances.append(instance)
    temp_grid_instances = np.array(temp_grid_instances)

    filterList = filterFunctions.saveOpenFilter(parentWindow.fileDataPath)
    nbImages = len(filenamelist)

    largeDisp = testReadFile(parentWindow.fileDataPath+'/largeDisp.csv')

    #Last operations
    nb_marker = data_x.shape[0]
    nb_image = data_x.shape[1]

    instances = np.unique(temp_grid_instances).tolist()
    grid_instances = []
    for instance in instances:
        grid_instances.append([])
    for marker in range(nb_marker):
        grid_instances[instances.index(temp_grid_instances[marker])].append(marker)

    return [data_x, data_y, data_corr, data_stdx, data_stdy, disp_x, disp_y, filenamelist, nb_marker, nb_image, filterList, grid_instances, largeDisp]


def testReadFile(filePath, lib=None):

    #test if the file exist
    try:
        if lib is not None: #for filenamelist to avoid type problems and errors due to space in file naming
            readFile = np.genfromtxt(filePath, dtype=None, delimiter=',')
        else:
            readFile = pandas.read_csv(filePath, dtype=None, delimiter=',', header=None).values #pandas is way faster than numpy for this
    except:
        return None
    return readFile
