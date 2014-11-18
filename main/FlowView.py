from __future__ import absolute_import
import os
import pickle

from PyQt4 import QtGui
from PyQt4 import QtCore

from .JobWidget import JobWidget
from .WorkerThread import JobWorkerThread
from .WorkerThread import CurrentJobWorkderThread
from .WorkerThread import TimerThread

from .JobWidget import JobTypes
from .JobWidget import MayaJobWidget
from .JobWidget import HoudiniJobWidget
from .JobWidget import NukeJobWidget
from .JobWidget import BatchJobWidget
from .JobWidget import PythonJobWidget

import utils.LogW as LogW
import utils.ErrorStr as ErrorStr

DARK_STYLE = os.path.dirname(os.path.dirname(__file__)) + "\\dark.style"

class FlowView(QtGui.QWidget):
    
    def __init__(self, UI_PROPERTIES, parent=None):
        QtGui.QWidget.__init__(self, parent=parent)
        
        self.setObjectName("flowview")
        
        self.mainUI = parent
        self.UI_PROPERTIES = UI_PROPERTIES
        
        # Threads
        self.workerThread = JobWorkerThread()
        self.currentWorkerThread = CurrentJobWorkderThread()
        self.timerThread = TimerThread(self.mainUI.timerLabel)
        
        self.jobs = []
        self.propertyDock = None
        self.outputDock = None
        
        self.setMinimumWidth(375)
        
        self.flowLayout = QtGui.QVBoxLayout()
        self.flowLayout.setAlignment(QtCore.Qt.AlignTop|QtCore.Qt.AlignHCenter)
        self.setLayout(self.flowLayout)
        
        # SIGNAL CONNECTIONS
        self.workerThread.updateProgressBar.connect(self._ui_updateProgressBar)
        self.workerThread.updateMessage.connect(self._ui_setInfoMessage)
        self.workerThread.resetProgressBar.connect(self._ui_resetProgressBar)
        self.workerThread.progressBarToActivity.connect(self._ui_progressBarToActivityMonitor)
        self.workerThread.startJob.connect(self._ui_disableButton)
        
        self.currentWorkerThread.updateProgressBar.connect(self._ui_updateProgressBar)
        self.currentWorkerThread.updateMessage.connect(self._ui_setInfoMessage)
        self.currentWorkerThread.resetProgressBar.connect(self._ui_resetProgressBar)
        self.currentWorkerThread.progressBarToActivity.connect(self._ui_progressBarToActivityMonitor)
        self.currentWorkerThread.startJob.connect(self._ui_disableButton)
        
    def linkToPropertiesDock(self, propertyDock):
        '''
            Link the flowview to the properties dock widget.
        '''
        self.propertyDock = propertyDock
    
    def linkToOutputDock(self, outputDock):
        '''
            Link the flowview to the output dock widget.
        '''
        self.outputDock = outputDock
    
    def addJob(self, job):
        '''
            Add a job to the flowview
        '''
        if job not in self.jobs:
            
            # Append a job tolist
            self.jobs.append(job)
            job.updateWarning()
            
            # Add flow arrow
            if self.flowLayout.count() >= 1:
                self.flowLayout.addWidget(ArrowFlow(self))
            
            # Add job widget
            self.flowLayout.addWidget(job)
                
            self.update()
            
            self.updateFlowviewHeader()
            
    def updateFlowviewHeader(self):
        
        nWarning = 0
        for job in self.jobs:
            if job.WARNING:
                nWarning += 1
                
        nJobs = len(self.jobs)
        
        self.mainUI.flowviewHeaderJobs.setText("Number of job(s): " + str(nJobs))
        self.mainUI.flowviewHeaderWarning.setText("Warning(s): " + str(nWarning))
            
    def updateFlowview(self, jobList):
        '''
            Update flowview used when jobs order changes
        '''
        
        newJobsList = list(jobList)
        self.clearJobs()

        for i in range(len(newJobsList)):
            
            # Add arriw after job 2
            if len(newJobsList) > 1:
                if i < len(newJobsList) and i > 1:
                    self.flowLayout.addWidget(ArrowFlow(self))
                    self.flowLayout.update()
            
            # Add job widget
            if newJobsList[i].jobType == JobTypes.MAYA:
                w = MayaJobWidget(self.propertyDock, i, self, self.outputDock.output, self.UI_PROPERTIES, parent=self)
                w.properties = newJobsList[i].properties
                
                if newJobsList[i].properties["file_path"]:
                    w.pathLabel.setText("Path: " + newJobsList[i].properties["file_path"])
                if newJobsList[i].properties["isbypassed"]:
                    w.isBypassed = False
                    w.bypassWidget()
                    
                w.updateWarning()
                
            elif newJobsList[i].jobType == JobTypes.NUKE:
                w = NukeJobWidget(self.propertyDock, i, self, self.outputDock.output, self.UI_PROPERTIES, parent=self)
                w.properties = newJobsList[i].properties
                if newJobsList[i].properties["file_path"]:
                    w.pathLabel.setText("Path: " + newJobsList[i].properties["file_path"])
                if newJobsList[i].properties["isbypassed"]:
                    w.isBypassed = False
                    w.bypassWidget()
                    
                w.updateWarning()
                
            elif newJobsList[i].jobType == JobTypes.HOUDINI:
                w = HoudiniJobWidget( self.propertyDock, i, self, self.outputDock.output, self.UI_PROPERTIES, parent=self)
                w.properties = newJobsList[i].properties
                if newJobsList[i].properties["file_path"]:
                    w.pathLabel.setText("Path: " + newJobsList[i].properties["file_path"])
                if newJobsList[i].properties["isbypassed"]:
                    w.isBypassed = False
                    w.bypassWidget()
                w.updateWarning()
                
            elif newJobsList[i].jobType == JobTypes.PYTHON:
                w = PythonJobWidget( self.propertyDock, i, self, self.outputDock.output, parent=self)
                w.properties = newJobsList[i].properties
                if newJobsList[i].properties["file_path"]:
                    w.pathLabel.setText("Path: " + newJobsList[i].properties["file_path"])
                if newJobsList[i].properties["isbypassed"]:
                    w.isBypassed = False
                    w.bypassWidget()
                w.updateWarning()
                
            elif newJobsList[i].jobType == JobTypes.BATCH:
                w = BatchJobWidget( self.propertyDock, i, self, self.outputDock.output, parent=self) 
                w.properties = newJobsList[i].properties
                if newJobsList[i].properties["file_path"]:
                    w.pathLabel.setText("Path: " + newJobsList[i].properties["file_path"])
                if newJobsList[i].properties["isbypassed"]:
                    w.isBypassed = False
                    w.bypassWidget()
                w.updateWarning()
                
            self.flowLayout.addWidget(w)   
            
            # Add arrow after job 1
            if i == 0 and len(newJobsList) > 1:
                self.flowLayout.addWidget(ArrowFlow(self))

            self.flowLayout.update()
            
                
        self.update()
        
        self.jobs = newJobsList

            
    def removeJob(self, ID):
        '''
            Remove a job from the flowview
        '''
        
        # Remove job widget from flowview
        if ID == 0:
            self.flowLayout.itemAt(ID).widget().setParent(None)
        else:
            self.flowLayout.itemAt(ID*2).widget().setParent(None)
        
        # Remove arrow wodget
        if ID == 0 and len(self.jobs) > 1:
            self.flowLayout.itemAt(0).widget().setParent(None)
        
        elif ID == len(self.jobs)-1:
            if ID >= 1:
                self.flowLayout.itemAt((ID*2)-1).widget().setParent(None)
        
        elif ID > 0 and len(self.jobs) > ID:
            self.flowLayout.itemAt((ID*2)).widget().setParent(None)
            
        # Remove job widget from list
        self.jobs.remove(self.jobs[ID])
        
        # Reset properties view
        self.propertyDock.hideProperties(clear=True)
        
        # Reorder IDs
        for i in range(len(self.jobs)):
            self.jobs[i].ID = i
            
        self.updateFlowviewHeader()
    
    def clearJobs(self):
        '''
            Remove all job widgets.
        '''
        # Clean flowview widgets
        while self.flowLayout.count() > 0:
            for i in range(self.flowLayout.count()):
                w = self.flowLayout.itemAt(i)
                if w:
                    w.widget().setParent(None) 
            self.flowLayout.update() 
        self.update()
        self.jobs = []

        self.updateFlowviewHeader()
    
    def deselectAllJobs(self):
        '''
            Unselect all job widgets.
        '''
        for i in self.jobs:
            i.unselectWidget()
    
    def listJobs(self):
        '''
            List all job widget of the flowview
        '''
        out = []
        
        nWidget = self.flowLayout.count()
        for i in range(nWidget):
            item = self.flowLayout.itemAt(i).widget()
            if isinstance(item, JobWidget):
                out.append(self.flowLayout.itemAt(i).widget()) 
            
        return out
    
    def renderCurrentJob(self, ID):
        '''
            Render current job according to given ID
        '''
        self.currentWorkerThread.job = self.jobs[ID]
        self.currentWorkerThread.start()
        
        
    def renderFlow(self, ID):
        '''
            Render the flowview
        '''
        
        tmpJobs = self.jobs[0:ID+1]
        
        warnings = [n.warning.isVisible() for n in tmpJobs]
        
        if any(warnings):
            ask = QtGui.QMessageBox(QtGui.QMessageBox.Warning,"Warning",
                                    "Warnings found on the flowview jobs, do you want to continue ?\nJobs with warnings will be skipped.",
                                    parent = self)
            with open(DARK_STYLE, 'r') as style:
                ask.setStyleSheet(style.read())
            ask.addButton(QtGui.QMessageBox.Yes)
            ask.addButton(QtGui.QMessageBox.No)
            p = ask.exec_()
            
            if p == QtGui.QMessageBox.No:
                return
            
        else:
            ask = QtGui.QMessageBox(QtGui.QMessageBox.Information,"Info",
                                    "Render {0} jobs ?".format(len(tmpJobs)),
                                    parent = self)
            with open(DARK_STYLE, 'r') as style:
                ask.setStyleSheet(style.read())
            ask.addButton(QtGui.QMessageBox.Yes)
            ask.addButton(QtGui.QMessageBox.Cancel)
            p = ask.exec_()
            
            if p == QtGui.QMessageBox.Cancel:
                return
        
        self.timerThread.startTime = 0
        self.workerThread.jobList = tmpJobs
        self.workerThread.start()
        
    def cancelFlowrender(self):
        '''
            Cancel flowview rendering
        '''
        ask = QtGui.QMessageBox(QtGui.QMessageBox.Warning,"Warning", "Cancel current flowview rendering ?",parent = self)
        with open(DARK_STYLE, 'r') as style:
            ask.setStyleSheet(style.read())
        ask.setInformativeText("This could cause corrupted output.")
        ask.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel);
        p = ask.exec_()
        
        if p == QtGui.QMessageBox.Ok:
            
            self.currentWorkerThread.terminate()
            self.currentWorkerThread.wait()
            self.workerThread.terminate()
            self.workerThread.wait()
            self.timerThread.terminate()
            self.timerThread.startTime = 0
            self.timerThread.wait()
            self.mainUI.cancelFlow.setEnabled(False)
            self.mainUI.progressInfo.setText("Rendering cancelled")
            self._ui_resetProgressBar()
            self._ui_disableButton(True)
            self._ui_progressBarToActivityMonitor(False)
            
            if self.UI_PROPERTIES["clean_py"]:
                self.mainUI.cleanTmpFiles()
            
            LogW.writeLog(self.outputDock.output, ErrorStr.ErrorStr.INFO + " Rendering cancelled by user.")
    
    def saveFlowview(self):
        
        if not self.jobs:
            LogW.writeLog(self.outputDock.output, ErrorStr.ErrorStr.ERROR + " Nothing to save, flowview is empty.")
            return
        
        p = QtGui.QFileDialog.getSaveFileName(parent=None, filter = "hman Files (*.hman)")
        
        if not p:
            return
        
        datas = []
        datas.append(str(self.mainUI.flowLabel.text()))
        for i in self.jobs:
            datas.append({"ID":i.ID, "jobtype":str(i.jobType), "properties":i.properties})
        
        with open(p, "wb") as f:
            pickle.dump(datas, f)

    def loadFlowview(self):
        
        p = QtGui.QFileDialog.getOpenFileNames(parent=None, filter = "hman Files (*.hman)")
        
        REPLACE = False
        
        if self.jobs and p:
            ask = QtGui.QMessageBox(QtGui.QMessageBox.Warning,"Warning", "Jobs already found in the Flowview.\nDo you want to Append new jobs or replace current jobs ?",parent = self)
            ask.addButton('Append', QtGui.QMessageBox.NoRole)
            ask.addButton('Replace', QtGui.QMessageBox.YesRole)
            ask.addButton('Cancel', QtGui.QMessageBox.RejectRole)
            ret = ask.exec_();
            
            if ret == 2:
                return
            elif ret == 1:
                REPLACE = True
                self.clearJobs()
                self.propertyDock.hideProperties(clear=True)
                for i in self.jobs: print i
        
        if p:
            for f in p:
            
                datas = None
                with open(str(f), 'rb') as handle:
                    datas = pickle.load(handle)
                
                # Change flowview label
                if REPLACE or not self.jobs:
                    self.mainUI.flowLabel.setText(str(datas[0]))
                datas = datas[1:]
            
                for data in datas:
                    
                    if data["jobtype"] == JobTypes.MAYA:
                        w = MayaJobWidget(self.propertyDock, data["ID"] + (len(self.jobs)-data["ID"]), self, self.outputDock.output, self.UI_PROPERTIES, parent=self)
                        w.properties = data["properties"]
                        self.addJob(w)
                        
                    elif data["jobtype"] == JobTypes.NUKE:
                        w = NukeJobWidget(self.propertyDock, data["ID"] + (len(self.jobs)-data["ID"]), self, self.outputDock.output, self.UI_PROPERTIES, parent=self)
                        w.properties = data["properties"]
                        self.addJob(w)
                        
                    elif data["jobtype"] == JobTypes.HOUDINI:
                        w = HoudiniJobWidget( self.propertyDock, data["ID"] + (len(self.jobs)-data["ID"]), self, self.outputDock.output, self.UI_PROPERTIES, parent=self)
                        w.properties = data["properties"]
                        self.addJob(w)
                        
                    elif data["jobtype"] == JobTypes.PYTHON:
                        w = PythonJobWidget( self.propertyDock, data["ID"] + (len(self.jobs)-data["ID"]), self, self.outputDock.output, parent=self)
                        w.properties = data["properties"]
                        self.addJob(w)
                        
                    elif data["jobtype"] == JobTypes.BATCH:
                        w = BatchJobWidget( self.propertyDock, data["ID"] + (len(self.jobs)-data["ID"]), self, self.outputDock.output, parent=self)
                        w.properties = data["properties"]
                        self.addJob(w)
                
                 
                LogW.writeLog(self.outputDock.output, ErrorStr.ErrorStr.INFO + " {0} loaded successfully.".format(str(f)))  
            
    def mousePressEvent(self, event):
        '''
            Hide properties when user click on the background of the flowview
        '''
        if self.flowLayout.count() == 0:
            return
        
        self.propertyDock.hideProperties()
        for n in self.listJobs():
            n.unselectWidget()
            
    # Update UI from thread
    def _ui_updateProgressBar(self, step):
        self.mainUI._ui_updateProgressBar(step)
        
    def _ui_resetProgressBar(self):
        self.mainUI._ui_resetProgressBar()
        
    def _ui_progressBarToActivityMonitor(self, enable=True):
        self.mainUI._ui_enableActivityMonitor(enable)
            
    def _ui_setInfoMessage(self, msg, toOutput=False):
        self.mainUI._ui_setInfoMessage(msg, toOutput)
        
    def _ui_disableButton(self, enable=False):
        self.mainUI._ui_disableButton(enable)
        if enable:
            self.mainUI.cancelFlow.setEnabled(False)
            self.timerThread.terminate()
            self.timerThread.wait()
            self.mainUI.timerLabel.setText("")
        else:
            self.timerThread.start()
            self.mainUI.cancelFlow.setEnabled(True)

#################################################

class ArrowFlow(QtGui.QWidget):
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent=parent)
        self.setFixedSize(350,40)
        
        iconsPath = os.path.dirname(os.path.dirname(__file__)) + "\\icons\\"
        layout = QtGui.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignCenter)
        bg = QtGui.QLabel("")
        pix = QtGui.QPixmap(iconsPath + "arrowDownFlow.png")
        bg.setPixmap(pix)
        layout.addWidget(bg)
        self.setLayout(layout)