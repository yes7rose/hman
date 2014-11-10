from __future__ import absolute_import
import time
import datetime

from PyQt4 import QtCore

from utils.ErrorStr import ErrorStr
from .JobWidget import JobTypes

import threading

class JobWorkerThread(QtCore.QThread):
    '''
        Thread used when job is rendered.
    '''
    
    updateProgressBar = QtCore.pyqtSignal(int)
    resetProgressBar = QtCore.pyqtSignal()
    progressBarToActivity = QtCore.pyqtSignal(bool)
    updateMessage = QtCore.pyqtSignal(str, bool)
    startJob = QtCore.pyqtSignal(bool)
    
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.jobList = []
    
    def run(self):
        
        self.resetProgressBar.emit()
        self.startJob.emit(False)
        
        globalStartTime = time.time()
        
        if not self.jobList:
            return
        
        lenJobs = len([n for n in self.jobList if not n.isBypassed and not n.warning.isVisible()])
        
        if lenJobs % 2 == 0:
            step = int(100 / lenJobs)
        else:
            step = int(100 / lenJobs) + 1
        
        k=0
        errorFound = 0
        
        self.progressBarToActivity.emit(True)
        
        for i in self.jobList:
                       
            if i.isBypassed or i.warning.isVisible():
                self.updateMessage.emit(ErrorStr.WARNING + "Job: {0} skipped.".format(i.ID), True)
                continue
            
            self.updateMessage.emit(ErrorStr.INFO + "Starting Job: {0} ({1})".format(i.ID, i.jobType), True)
            
            jobStartTime = time.time()
            
            #Render job if it is a batch job, render in a separated thread
            # if wait if not True
            
            if i.jobType == JobTypes.BATCH:
                p = threading.Thread(None, i._renderCurrent, None, args=() )
                p.start()
                
                if i.properties["wait"]:
                    p.join()
                
            else:
                i._renderCurrent()
            
            jobEndTime = time.time() - jobStartTime
            jobEndTime = datetime.timedelta(seconds=int(jobEndTime))
            
            if i.ERROR:
                self.updateMessage.emit(ErrorStr.ERROR + "Job: {0} error: {1}".format(i.ID, i.ERROR), True)
                errorFound += 1
            else:
                self.updateMessage.emit(ErrorStr.INFO + "Job: {0} finished in {1}".format(i.ID, jobEndTime), True)
            
            self.updateProgressBar.emit(step)
            
            k += 1

        globalEndTime = time.time() - globalStartTime
        globalEndTime = datetime.timedelta(seconds=int(globalEndTime))
        self.updateMessage.emit(ErrorStr.INFO + "Flowview done, {0} job(s) rendered in {1}, {2} error(s).".format(k, globalEndTime, errorFound), True)
        self.startJob.emit(True)
        self.progressBarToActivity.emit(False)

class CurrentJobWorkderThread(QtCore.QThread):
    
    updateProgressBar = QtCore.pyqtSignal(int)
    resetProgressBar = QtCore.pyqtSignal()
    progressBarToActivity = QtCore.pyqtSignal(bool)
    updateMessage = QtCore.pyqtSignal(str, bool)
    startJob = QtCore.pyqtSignal(bool)
    
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.job = None
        
    def run(self):
        
        self.resetProgressBar.emit()
        self.startJob.emit(False)
        
        jobStartTime = time.time()
        
        if self.job:
            self.updateMessage.emit(ErrorStr.INFO + "Starting Job: {0} ({1})".format(self.job.ID, self.job.jobType), True)
            self.progressBarToActivity.emit(True)
            
            if self.job.jobType == JobTypes.BATCH:
                p = threading.Thread(None, self.job._renderCurrent, None, args=() )
                p.start()
                
                if self.job.properties["wait"]:
                    p.join()
                
            else:
                self.job._renderCurrent()
                
            jobEndTime = time.time() - jobStartTime
            jobEndTime = datetime.timedelta(seconds=int(jobEndTime))
            
            self.progressBarToActivity.emit(False)
            self.updateMessage.emit(ErrorStr.INFO + "Job: {0} rendered in {1}.".format(self.job.ID, jobEndTime), True)
            self.startJob.emit(True)
            
class TimerThread(QtCore.QThread):
    
    def __init__(self, timer_label):
        QtCore.QThread.__init__(self)
        
        self.startTime = 0
        self.ACTIVE = False
        self.timer_label = timer_label
        
    def run(self):
        
        while True:
            
            self.timer_label.setText(str(datetime.timedelta(seconds=self.startTime)))
            time.sleep(1)
            self.startTime += 1
            
        