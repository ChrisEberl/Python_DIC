# -*- coding: utf-8 -*-
"""
Created on 05/04/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file manages the analysis files and open/generate data from them
"""

import csv
import os
import numpy as np
from math import sqrt
import startWidget
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import time
import initData
import multiprocessing
import filterWidget


def openData(parentWindow, progressBar, parent): #parent contains the Thread in which the opening is made


    dataList = generateData(parentWindow, progressBar)
    if dataList is not None:
        parentWindow.devWindow.addInfo('Data extracted from files. Preparing the calculation.')
        parent.signal.threadSignal.emit(dataList)
    else:
        parent.signal.threadSignal.emit([0])

    return


def generateData(parentWindow, progressBar):

    ######### CREATING PROCESSES AND OPENING FILES #########
    PROCESSES = int(parentWindow.profileData['nbProcesses'][parentWindow.currentProfile])
    tic = time.time()

    # files to load (Must be all the same type = m x n matrices - Do not use the fileNameList)
    dataToLoad = [parentWindow.fileDataPath+'/validx.dat', parentWindow.fileDataPath+'/validy.dat', parentWindow.fileDataPath+'/corrcoef.dat', parentWindow.fileDataPath+'/stdx.dat', parentWindow.fileDataPath+'/stdy.dat', parentWindow.fileDataPath+'/dispx.dat', parentWindow.fileDataPath+'/dispy.dat']


    args = []
    nbFilesPerProcess = len(dataToLoad)/PROCESSES
    if nbFilesPerProcess < 1:
        nbFilesPerProcess = 1
        PROCESSES = len(dataToLoad)
    parentWindow.devWindow.addInfo('Opening files with '+str(PROCESSES)+' processes.')
    for i in range(0,PROCESSES):
        start = int(i*nbFilesPerProcess)
        if i >= PROCESSES-1: #last process do all the last files
            end = len(dataToLoad)
        else:
            end = int((i+1)*nbFilesPerProcess)
        args.append((dataToLoad[start:end],))

    result = parentWindow.createProcess(getDataFromFile, args, PROCESSES, progressBar=progressBar, textBar='Opening data files ...') #result is a (nbImages*nbFiles) x nbMarkers matrix

    if result is None:
        return None

    filenamelist = getDataFromFile([parentWindow.fileDataPath+'/filenamelist.dat'], 0, singleColumn=1) #0 is here to replace the Queue from Multiprocessing
    if filenamelist is None:
        return None

    grid_entities = getDataFromFile([parentWindow.fileDataPath+'/gridx.dat'], 0, singleColumn=1)

    if grid_entities is None:
        return None

    temp_grid_instances = []
    for (coor, instance) in grid_entities:
        temp_grid_instances.append(instance)
    temp_grid_instances = np.array(temp_grid_instances)


    filterList = filterWidget.saveOpenFilter(parentWindow.fileDataPath)
    nbImages = len(filenamelist)

    largeDisp = getDataFromFile([parentWindow.fileDataPath+'/largeDisp.dat'], 0, singleColumn=1)


    data_x = result[:,0:nbImages]
    data_y = result[:,nbImages:2*nbImages]
    data_corr = result[:,2*nbImages:3*nbImages]
    data_stdx = result[:,3*nbImages:4*nbImages]
    data_stdy = result[:,4*nbImages:5*nbImages]
    disp_x = result[:,5*nbImages:6*nbImages]
    disp_y = result[:,6*nbImages:7*nbImages]


    parentWindow.devWindow.addInfo('Terminated in '+str(time.time()-tic)+' seconds.')
    #########################

    if data_x is not None:
        nb_marker = data_x.shape[0]
        nb_image = data_x.shape[1]
    else:
        nb_marker = 0
        nb_image = 0

    instances = np.unique(temp_grid_instances).tolist()
    grid_instances = []
    for instance in instances:
        grid_instances.append([])
    for marker in range(nb_marker):
        grid_instances[instances.index(temp_grid_instances[marker])].append(marker)

    return [data_x, data_y, data_corr, data_stdx, data_stdy, disp_x, disp_y, filenamelist, nb_marker, nb_image, filterList, grid_instances, largeDisp]


def testReadFile(filePath):

    #test if the file exist
    try:
        readFile = np.genfromtxt(filePath, dtype=None)
    except:
        return None
    return readFile


def getDataFromFile(filePath, q, pipe=None, singleColumn=0):

    fileResult = []

    numFiles = len(np.atleast_1d(filePath))

    for element in range(numFiles):


        readFile = testReadFile(filePath[element])

        if readFile is None or readFile is filePath[element]:
            if q != 0:
                q.put(0)
                q.close()
                return
            else:
                return None

        try:
            rownum = 0
            for row in readFile:
                colnum = 0
                if type(row) == np.ndarray:
                    for col in row:
                        colnum+=1
                rownum+=1
        except:
            if q != 0:
                q.put(0)
                q.close()
                return
            else:
                return None

        if singleColumn < 1:

            #create zero matrix to write the data
            data = np.zeros((rownum, colnum))

            rownum = 0
            for row in readFile:
                colnum = 0
                for col in row:
                    col = float(col)
                    #if np.isfinite(col) <> True: #verify if number is finite, do not register if not finite
                    #    continue
                    data[rownum, colnum] = col
                    colnum+=1
                rownum+=1
        else:
            data = []
            for row in readFile:
                data.append(row)

        fileResult.append(data)

        if pipe is not None:
            percent = (element+1.0)/numFiles*100
            pipe.send(percent)

    result = fileResult[0]
    for i in range(1,len(fileResult)):
        result = np.hstack((result, fileResult[i]))

    if q != 0:
        q.put(result)
        q.close()
        return
    else:
        return result



def errorMessage(title, message): #show message dialog when an error is generated

    errorMessage = QMessageBox()
    errorMessage.setWindowTitle(title)
    errorMessage.setText(message)
    errorMessage.exec_()
