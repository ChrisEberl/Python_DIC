# -*- coding: utf-8 -*-
"""
Created on 20/10/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: Contains functions used by the filterWidget classes and associated to image filtering
"""
import numpy as np, cv2
from functions import getData

def applyFilterListToImage(filterList, image):

    if filterList is not None:
        nbFilters = len(np.atleast_1d(filterList))
        if nbFilters > 0:
            for currentFilter in np.atleast_1d(filterList):
                filterName = currentFilter[1]
                filterParameters = [currentFilter[2], currentFilter[3], currentFilter[4]]
                image = applyFilterToImage(filterName, filterParameters, image)

    return image

def applyFilterToImage(filterName, filterParameters, image):

    backupImage = image
    if filterName == 'Zoom':

        try:
            minY = int(filterParameters[2].split(',')[0])
            maxY = minY + int(filterParameters[0])
            minX = int(filterParameters[2].split(',')[1])
            maxX = minX + int(filterParameters[1])
            image = image[minX:maxX, minY:maxY]
        except:
            image = backupImage

    elif filterName == 'Blur':

        image = cv2.blur(image, (int(filterParameters[0]), int(filterParameters[1])))

    elif filterName == 'Gaussian':

        try:
            image = cv2.GaussianBlur(image, (int(filterParameters[0]), int(filterParameters[1])), int(filterParameters[2].split(',')[0]), int(filterParameters[2].split(',')[1]))
        except:
            image = backupImage

    elif filterName == 'Brightness':

        maxValue = np.max(image)
        phi = float(filterParameters[0])/100
        theta = float(filterParameters[1])/100
        degree = float(filterParameters[2])
        image = image.astype(np.float_)
        image = maxValue*(1+theta)*(image/maxValue/(1-phi))**(1/degree)
        image[image > 255] = 255
        image[image < 0] = 0
        image = image.astype(np.uint8)

    elif filterName == 'Darkness':

        maxValue = np.max(image)
        phi = float(filterParameters[0])/100
        theta = float(filterParameters[1])/100
        degree = float(filterParameters[2])
        image = image.astype(np.float_)
        image = maxValue*(1-theta)*(image/maxValue/(1+phi))**(degree)
        image[image > 255] = 255
        image[image < 0] = 0
        image = image.astype(np.uint8)

    elif filterName == 'Contrast':

        maxValue = np.max(image)
        phi = float(filterParameters[0])/100
        theta = float(filterParameters[1])/100
        degree = float(filterParameters[2])
        medium = (float(maxValue)+np.min(image))/2
        image = image.astype(np.float_)
        image[image > medium] = medium*(1+theta)*(image[image > medium]/medium/(1-phi))**(1/degree)
        image[image < medium] = medium*(1-theta)*(image[image < medium]/medium/(1+phi))**(degree)
        image[image > 255] = 255
        image[image < 0] = 0
        image = image.astype(np.uint8)

    return image

def saveOpenFilter(filePath, filterList=None):

    filterFileName = '/filter.dat'
    if filterList is None: #we want to open the filterFileName file
        filterList = getData.testReadFile(filePath+filterFileName)
        return filterList
    else:
        np.savetxt(filePath+filterFileName, np.array(filterList), fmt="%s")
