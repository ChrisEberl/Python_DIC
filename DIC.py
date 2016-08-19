# -*- coding: utf-8 -*-
"""
Created on 21/03/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: This file manages the main gui application on start-up and include functions to create process and threads
"""



import sys
import time
import multiprocessing
from PySide.QtGui import *
from PySide.QtCore import *
import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4'] = 'PySide'

import startWidget
import profile
import menubar
import devMode
import numpy as np

#PARAMETERS
PROFILE_FILE = 'profile.cfg'
DEFAULT_PROFILE = (['User','Guest'],['Default','1'],['FullScreen','0'],['Width','800'],['Height','600'],['CorrSize','15'],['nbProcesses','1']) #default values when new profile is created and when no profile file found
DEV_MODE = 0
#END PARAMETERS
    
        
class MainWindow(QMainWindow):
    
    def __init__(self): #initiate the main window with thread variables 
        super(MainWindow, self).__init__()
        
        self.profileData = profile.readProfile(PROFILE_FILE, default=DEFAULT_PROFILE) #read the profile list and create a default profile if the PROFILE_FILE is not found
        count = -1
        for profiles in self.profileData['Default']: #select the default profile
            count+=1
            if int(profiles) == 1:
                break
        
        FULL_SCREEN = int(self.profileData['FullScreen'][count])
        
        self.profilePath = PROFILE_FILE #link to the profile configuration file
        self.defaultProfile = DEFAULT_PROFILE #used when adding a new profile in profile management
        self.currentProfile = count #ID of the current loaded profile
        if FULL_SCREEN == 1:
            self.setWindowState(Qt.WindowMaximized)
        QApplication.setStyle(QStyleFactory.create('Cleanlooks'))
        self.appInit()
                
    def appInit(self):
        
        menubar.createMenu(self)    
        #createToolbar(self)
        
        WIDTH = int(self.profileData['Width'][self.currentProfile])
        HEIGHT = int(self.profileData['Height'][self.currentProfile])
        USER = self.profileData['User'][self.currentProfile]
        
        self.setWindowTitle('Digital Image Correlation ('+USER+')')
        self.setMinimumWidth(WIDTH)
        self.setMinimumHeight(HEIGHT)
        
        self.devWindow = devMode.DevMode(DEV_MODE)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.devWindow)
        
        self.homeWidget()
        
        self.statusBar().setMaximumHeight(15)
        self.statusBar().showMessage('Ready.')
        self.show()
    
    def homeWidget(self, message=None): #start up widget when called
        
        menubar.menuDisabled(self)
        
        firstWidget = QWidget()
        #apply background
        tile = QPixmap("BG.png")
        palette = QPalette()
        palette.setBrush(QPalette.Background, tile)
        firstWidget.setAutoFillBackground(True)
        firstWidget.setPalette(palette)                
        
        startWidget.StartWidget(firstWidget, self, message) #central element with new analysis and open previous button
        
        self.setCentralWidget(firstWidget) #each main widget later will be placed in the central part of the main window, replacing the startWidget
        
    def createProcess(self, function, args, PROCESSES, progressBar=None, textBar=None): # create PROCESSES processes and execute function with args, write progressBar if given (with textBar)
        
        p=[]
        q=[]
        parent_conn = []
        child_conn = []
        alive = 1
        for i in range(0,PROCESSES):
            parent_conn_t, child_conn_t = multiprocessing.Pipe() #connection pipe to exchange data with a Process (direct link)
            parent_conn.append(parent_conn_t)
            child_conn.append(child_conn_t)
            q.append(multiprocessing.Queue()) #queue to exchange data with process (indirect link)
            if __name__ == "__main__":
                p.append(multiprocessing.Process(target=function, args=args[i]+(q[i],)+(child_conn[i],))) #create the process with the target function to execute
                p[i].start() #start the calculation
                
                
        if progressBar is not None: #calculation and update of the progressBar
            lastPercent = 0
            a = []
            for i in range(PROCESSES):
                a.append(0)
            while alive == 1:
                alive = 0
                for i in range(PROCESSES):        
                    if parent_conn[i].poll():
                        t = parent_conn[i].recv()
                        if t > a[i]:
                            a[i] = t
                    if q[i].empty(): # stay in the loop as long as at least one task is not finished, as  long as the queue is still empty
                        alive = 1
                total = sum(a)/PROCESSES
                if total <> lastPercent:
                    progressBar.changeValue(total, textBar) #change the value of the progresBar every percent
                    lastPercent = total
                time.sleep(.1) #refresh every 0.1 sec  - Important for the loop (freeze if too fast)
                
              
        if q[0] == 0:
            return None
        q[0] = q[0].get() #get the queue result
        for i in range(1,PROCESSES):
            if q[i] == 0:
                return None
            q[i] = np.hstack((q[i-1], q[i].get())) #putting the result in the same variable
            
        result = q[PROCESSES-1]
        return result
    
    def createThread(parent, args, function, signal=None): #a signal will be created as long as signal is different from None, callable with thread.signal.threadSignal.emit([]) : [] can contains data to be emitted
        
        thread = Thread(signal)
        args.append(thread) #thread instance placed at the end of the argument list (used for example for signals)
        thread.getReady(function, args)
        return thread
        
        

        
        
class Thread(QThread):
    
    def __init__(self, signal):
        super(Thread, self).__init__()
        if signal is not None:
            self.signal = threadSignal()
    
    def getReady(self, function, args): #setting up variables for the function to be executed by the thread
        self.function = function
        self.args = args
    
    def run(self): #when start() is called, execute the function
        self.function(*self.args)
        
            
class threadSignal(QObject):
    
    threadSignal = Signal(list) #each signal can emit lists

    
if __name__ == '__main__':
    
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())