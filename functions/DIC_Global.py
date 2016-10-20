# -*- coding: utf-8 -*-
"""
Created on 18/10/2016

@author: Charlie Bourigault
@contact: bourigault.charlie@gmail.com

Please report issues and request on the GitHub project from ChrisEberl (Python_DIC)
More details regarding the project on the GitHub Wiki : https://github.com/ChrisEberl/Python_DIC/wiki

Current File: Contains mains classes and functions
"""

import time, multiprocessing, numpy as np, matplotlib as mpl
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
mpl.rcParams.update({'figure.autolayout': True})

class matplotlibWidget(FigureCanvas):

    def __init__(self):

        super(matplotlibWidget,self).__init__(mpl.figure.Figure())
        self.figure = mpl.figure.Figure()
        self.figure.set_facecolor('none')
        self.canvas = FigureCanvas(self.figure)
        self.matPlot = self.figure.add_subplot(111)
        self.matPlot.set_aspect('auto')
        self.setContentsMargins(0,0,0,0)
        self.figure.tight_layout()

def createThread(parent, args, function, signal=None): #a signal will be created as long as signal is different from None, callable with thread.signal.threadSignal.emit([]) : [] can contains data to be emitted

    thread = Thread(signal)
    args.append(thread) #thread instance placed at the end of the argument list (used for example for signals)
    thread.getReady(function, args)
    return thread

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
        #if __name__ == "__main__":
        p.append(multiprocessing.Process(target=function, args=args[i]+(q[i],)+(child_conn[i],))) #create the process with the target function to execute
        p[i].start() #start the calculation

    if progressBar is not None: #calculation and update of the progressBar
        progressBar.currentTitle = textBar
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
            if total != lastPercent:
                progressBar.percent = total #change the value of the progresBar every percent
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

    threadSignal = pyqtSignal(list) #each signal can emit lists
