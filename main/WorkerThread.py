from __future__ import absolute_import
import time
import os
import datetime
import pickle

from PyQt4 import QtCore

from utils.ErrorStr import ErrorStr
from .JobWidget import JobTypes

import threading

TMP_GRAPHDATA = os.path.dirname(os.path.dirname(__file__)) + "\\_pytmp\\graphdata.tmp"

class JobWorkerThread(QtCore.QThread):
    '''
        Thread used when job is rendered.
    '''
    
    updateProgressBar = QtCore.pyqtSignal(int)
    resetProgressBar = QtCore.pyqtSignal()
    progressBarToActivity = QtCore.pyqtSignal(bool)
    updateMessage = QtCore.pyqtSignal(str, bool, bool)
    startJob = QtCore.pyqtSignal(bool)
    graphDataRefresh = QtCore.pyqtSignal(list)
    
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.jobList = []
        self.enableGraphData = False
    
    def run(self):
        
        self.graphDataValues = [[],[]]
        # delete tmp graphdata if any
        if os.path.exists(TMP_GRAPHDATA):
            os.remove(TMP_GRAPHDATA)
        
        self.resetProgressBar.emit()
        self.startJob.emit(True)
        
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
                self.updateMessage.emit(ErrorStr.WARNING + "Job: {0} skipped.".format(i.ID), True, False)
                continue
            
            self.updateMessage.emit(ErrorStr.INFO + "Starting Job: {0} ({1})".format(i.ID, i.jobType), True, False)
            
            i.switchRenderingMode(True)
            
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
            jobEndTimeSec = jobEndTime
            jobEndTime = datetime.timedelta(seconds=int(jobEndTime))
            
            if i.ERROR:
                self.updateMessage.emit(ErrorStr.ERROR + "Job: {0} error: {1}".format(i.ID, i.ERROR), True, False)
                errorFound += 1
            else:
                self.updateMessage.emit(ErrorStr.INFO + "Job: {0} finished in {1}".format(i.ID, jobEndTime), True, False)
            
            i.switchRenderingMode(False)
            
            self.updateProgressBar.emit(step)
            
            self.graphDataValues[0].append(k)
            self.graphDataValues[1].append(jobEndTimeSec)
            k += 1
            
        if self.enableGraphData:
            self.graphDataRefresh.emit(self.graphDataValues)
        
        # Save graphdata to tmp folder   
        with open(TMP_GRAPHDATA, "wb") as f:
            pickle.dump(self.graphDataValues, f)

        globalEndTime = time.time() - globalStartTime
        globalEndTime = datetime.timedelta(seconds=int(globalEndTime))
        
        if errorFound:
            msg = ErrorStr.WARNING
        else:
            msg = ErrorStr.INFO
        
        self.updateMessage.emit(msg + "Flowview done, {0} job(s) rendered in {1}, {2} error(s).".format(k, globalEndTime, errorFound), True, True)
        self.startJob.emit(False)
        self.progressBarToActivity.emit(False)

class CurrentJobWorkderThread(QtCore.QThread):
    
    updateProgressBar = QtCore.pyqtSignal(int)
    resetProgressBar = QtCore.pyqtSignal()
    progressBarToActivity = QtCore.pyqtSignal(bool)
    updateMessage = QtCore.pyqtSignal(str, bool, bool)
    startJob = QtCore.pyqtSignal(bool)
    
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.job = None
        
    def run(self):
        
        self.resetProgressBar.emit()
        self.startJob.emit(True)
        
        jobStartTime = time.time()
        
        if self.job:
            self.updateMessage.emit(ErrorStr.INFO + "Starting Job: {0} ({1})".format(self.job.ID, self.job.jobType), True, False)
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
            
            if self.job.ERROR:
                self.updateMessage.emit(ErrorStr.ERROR + "Job: {0} failed: {1}".format(self.job.ID, self.job.ERROR), True, True)
            else:
                self.updateMessage.emit(ErrorStr.INFO + "Job: {0} rendered in {1}.".format(self.job.ID, jobEndTime), True, True)
                
            self.startJob.emit(False)
            
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
            
        