import os
import webbrowser

from PyQt4 import QtGui
from PyQt4 import QtCore

from IO_path import readInitPath
import utils.LogW
import utils.ErrorStr

from main.PathPicker import PathPicker

from JobWidget import MayaJobWidget
from JobWidget import HoudiniJobWidget
from JobWidget import NukeJobWidget
from JobWidget import BatchJobWidget
from JobWidget import PythonJobWidget

from PropertiesDock import PropertyDock
from OutputDock import OutputDock
from GraphdataDock import GraphdataDock
from FlowView import FlowView

from JobWidget import JobTypes
import subprocess

DARK_STYLE = os.path.dirname(os.path.dirname(__file__)) + "\\dark.style"

class HmanMainUi(QtGui.QMainWindow):
    
    def __init__(self, version, parent=None):
        QtGui.QMainWindow.__init__(self, parent=parent)
        
        self.version = version
        
        with open(DARK_STYLE,"r") as style:
            self.setStyleSheet(style.read())
            
        #Main attrib
        self.setWindowTitle("hman v" + version)
        
        self.parentPath = os.path.dirname(__file__)
        self.parentPath = os.path.dirname(self.parentPath)
        self.setWindowIcon(QtGui.QIcon(self.parentPath + r"/icons/hman_small.png"))
        self.softwareLoaded = readInitPath()
        self.setGeometry(400,150,900,800)
        
        self.cw = QtGui.QWidget()
        self.centralLayout = QtGui.QVBoxLayout()
        self.timerLabel = QtGui.QLabel("")
        
        # UI properties sent to differents methods if needed
        self.UI_PROPERTIES = {}
        
        
        # INIT UI
        self._initFlowViewHeader()
        self._initFlowview()
        self._initScrollArea()
        self._initPropertyDock()
        self._initOutputDock()
        self._initGraphdataDock()
        self._initProgressbar()
        self._initToolBar()
        self._initToolBarButtons()
        self._initMenus()
        self.statusBar().showMessage('Ready')
        
        self.tabifyDockWidget(self.outputDock, self.graphDataDock)
        
        self.outputDock.raise_()
        self.propertyDock.raise_()
        
        self.cw.setLayout(self.centralLayout)
        self.setCentralWidget(self.cw)
        
        # Options
        self.jobOptions = {"None":None}
        
    def _initMenus(self):
        
        self.menu = self.menuBar()
        
        #File action
        self.fileMenu = self.menu.addMenu("File")

        self.openFile = QtGui.QAction("Open file", self)
        self.openFile.setIcon(QtGui.QIcon(self.parentPath + r"/icons/open.png"))
        self.openFile.triggered.connect(self.flowView.loadFlowview)
        
        self.saveFile = QtGui.QAction("Save file", self)
        self.saveFile.setIcon(QtGui.QIcon(self.parentPath + r"/icons/save.png"))
        self.saveFile.triggered.connect(self.flowView.saveFlowview)
        
        self.newFlowview = QtGui.QAction("New Flowview", self)
        self.newFlowview.setIcon(QtGui.QIcon(self.parentPath + r"/icons/newDocument.png"))
        self.newFlowview.triggered.connect(self.createNewFlow)
        
        self.exitMenuAction = QtGui.QAction("Exit", self)
        self.exitMenuAction.setIcon(QtGui.QIcon(self.parentPath + r"/icons/exit.png"))
        self.exitMenuAction.triggered.connect(self.close)
        
        self.updatePathAction = QtGui.QAction("Update software paths", self)
        self.updatePathAction.triggered.connect(self.updatePath)
        self.fileMenu.addAction(self.openFile)
        self.fileMenu.addAction(self.saveFile)
        self.fileMenu.addAction(self.newFlowview)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.updatePathAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitMenuAction)
        
        # Jobs
        self.jobsMenu = self.menu.addMenu("Jobs")
        
        self.addMayaJobMenu = QtGui.QAction("Add Maya Job", self)
        self.addMayaJobMenu.setIcon(QtGui.QIcon(self.parentPath + r"/icons/maya.png"))
        
        self.addHoudiniJobMenu = QtGui.QAction("Add Houdini Job", self)
        self.addHoudiniJobMenu.setIcon(QtGui.QIcon(self.parentPath + r"/icons/houdini.png"))
        
        self.addNukeJobMenu = QtGui.QAction("Add Nuke Job", self)
        self.addNukeJobMenu.setIcon(QtGui.QIcon(self.parentPath + r"/icons/nuke.png"))

        self.addPythonJobMenu = QtGui.QAction("Add Python Job", self)
        self.addPythonJobMenu.setIcon(QtGui.QIcon(self.parentPath + r"/icons/python.png"))
        
        self.addBatchJobMenu = QtGui.QAction("Add Batch Job", self)
        self.addBatchJobMenu.setIcon(QtGui.QIcon(self.parentPath + r"/icons/batch.png"))
        
        self.showFlowViewHeader = QtGui.QAction("Show Flowview Infos", self)
        self.showFlowViewHeader.setCheckable(True)
        self.showFlowViewHeader.setChecked(True)
        self.showFlowViewHeader.triggered.connect(lambda: self.displayFlowViewHeader(self.showFlowViewHeader.isChecked()))
        
        self.autoCleanTmpScript = QtGui.QAction("Auto Clean Generated Python Script", self)
        self.autoCleanTmpScript.setCheckable(True)
        self.autoCleanTmpScript.setChecked(True)
        self.autoCleanTmpScript.triggered.connect(lambda: self.updateCleanPyMode(self.autoCleanTmpScript.isChecked()))
        
        self.cleanTmp = QtGui.QAction("Clean temporary files", self)
        self.cleanTmp.triggered.connect(self.cleanTmpFiles)
        self.cleanTmp.setIcon(QtGui.QIcon(self.parentPath + r"/icons/trashbin.png"))
        
        self.jobsMenu.addAction(self.addMayaJob)
        self.jobsMenu.addAction(self.addHoudiniJob)
        self.jobsMenu.addAction(self.addNukeJob)
        self.jobsMenu.addAction(self.addPythonJob)
        self.jobsMenu.addAction(self.addBatchJob)
        self.jobsMenu.addSeparator()
        self.jobsMenu.addAction(self.showFlowViewHeader)
        self.jobsMenu.addSeparator()
        self.jobsMenu.addAction(self.autoCleanTmpScript)
        self.jobsMenu.addAction(self.cleanTmp)
        
        # About
        self.aboutMenu = self.menu.addMenu("About")
        
        self.about = QtGui.QAction("About hman", self)
        self.about.setIcon(QtGui.QIcon(self.parentPath + r"/icons/hman_small.png"))
        
        self.checkUpdate = QtGui.QAction("Check Updates", self)
        
        self.showHelp = QtGui.QAction("Help", self)
        self.showHelp.setIcon(QtGui.QIcon(self.parentPath + r"/icons/help.png"))
        self.showHelp.triggered.connect(lambda: webbrowser.open("http://guillaumejobst.blogspot.fr/p/hman.html"))
        
        self.aboutMenu.addAction(self.about)
        #self.aboutMenu.addAction(self.checkUpdate)
        self.aboutMenu.addAction(self.showHelp)
        
        self.UI_PROPERTIES["clean_py"] = self.autoCleanTmpScript.isChecked()
        
    def _initToolBarButtons(self):
        
        if not self.softwareLoaded["MAYA_PATH"]:
            self.addMayaJob.setEnabled(False)
            
        if not self.softwareLoaded["HOUDINI_PATH"]:
            self.addHoudiniJob.setEnabled(False)
            
        if not self.softwareLoaded["NUKE_PATH"]:
            self.addNukeJob.setEnabled(False)
            
    def _initToolBar(self):
        
        # Software found
        self.software =  readInitPath()
        
        # Toolbar
        self.toolbar = QtGui.QToolBar()
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolbar)
        
        # New Document Button
        self.newdocbtn = QtGui.QAction("Create a new flowview", self)
        self.newdocbtn.setIcon(QtGui.QIcon(self.parentPath + r"/icons/newDocument.png"))
        self.newdocbtn.triggered.connect(self.createNewFlow)
        self.newdocbtn.setStatusTip("Create a new flowview")
        
        # Open Document Button
        self.openDocBtn = QtGui.QAction("Open a flowview file", self)
        self.openDocBtn.triggered.connect(self.flowView.loadFlowview)
        self.openDocBtn.setIcon(QtGui.QIcon(self.parentPath + r"/icons/open.png"))
        self.openDocBtn.setStatusTip("Open a flowview file")
        
        # Save Document Button
        self.saveDocBtn = QtGui.QAction("Save current flowview", self)
        self.saveDocBtn.setIcon(QtGui.QIcon(self.parentPath + r"/icons/save.png"))
        self.saveDocBtn.triggered.connect(self.flowView.saveFlowview)
        self.saveDocBtn.setStatusTip("Save current flowview")
        
        # Maya button
        self.addMayaJob = QtGui.QAction("Add Maya Job", self)
        self.addMayaJob.setIcon(QtGui.QIcon(self.parentPath + r"/icons/maya.png"))
        self.addMayaJob.setStatusTip("Add a Maya job")
        self.addMayaJob.triggered.connect(lambda: self.addJobToFLowView(JobTypes.MAYA))
        
        # Houdini button
        self.addHoudiniJob = QtGui.QAction("Add Houdini Job", self)
        self.addHoudiniJob.setIcon(QtGui.QIcon(self.parentPath + r"/icons/houdini.png"))
        self.addHoudiniJob.setStatusTip("Add a Houdini job")
        self.addHoudiniJob.triggered.connect(lambda: self.addJobToFLowView(JobTypes.HOUDINI))
        
        # Nuke button
        self.addNukeJob = QtGui.QAction("Add Nuke Job", self)
        self.addNukeJob.setIcon(QtGui.QIcon(self.parentPath + r"/icons/nuke.png"))
        self.addNukeJob.setStatusTip("Add a Nuke job")
        self.addNukeJob.triggered.connect(lambda: self.addJobToFLowView(JobTypes.NUKE))
        
        # Python button
        self.addPythonJob = QtGui.QAction("Add Python Job", self)
        self.addPythonJob.setIcon(QtGui.QIcon(self.parentPath + r"/icons/python.png"))
        self.addPythonJob.setStatusTip("Add a Python job")
        self.addPythonJob.triggered.connect(lambda: self.addJobToFLowView(JobTypes.PYTHON))
        
        # Batch button
        self.addBatchJob = QtGui.QAction("Add Batch Job", self)
        self.addBatchJob.setIcon(QtGui.QIcon(self.parentPath + r"/icons/batch.png"))
        self.addBatchJob.setStatusTip("Add a Batch file job")
        self.addBatchJob.triggered.connect(lambda: self.addJobToFLowView(JobTypes.BATCH))
        
        # Clear jobs button
        self.clearJobs = QtGui.QAction("Clear Jobs", self)
        self.clearJobs.setIcon(QtGui.QIcon(self.parentPath + r"/icons/clear.png"))
        self.clearJobs.setStatusTip("Clear all jobs")
        self.clearJobs.triggered.connect(self.clearJobsFromFlowView)
        
        # About button
        self.aboutBtn = QtGui.QAction("About", self)
        self.aboutBtn.setIcon(QtGui.QIcon(self.parentPath + r"/icons/hman_large.png"))
        self.aboutBtn.setStatusTip("About")
        
        # Quit button
        self.quitBtn = QtGui.QAction("Quit hman", self)
        self.quitBtn.setIcon(QtGui.QIcon(self.parentPath + r"/icons/exit.png"))
        self.quitBtn.setStatusTip("Quit hman")
        self.quitBtn.triggered.connect(self.close)
        
        self.toolbar.addAction(self.newdocbtn)
        self.toolbar.addAction(self.saveDocBtn)
        self.toolbar.addAction(self.openDocBtn)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.addMayaJob)
        self.toolbar.addAction(self.addHoudiniJob)
        self.toolbar.addAction(self.addNukeJob)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.addPythonJob)
        self.toolbar.addAction(self.addBatchJob)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.clearJobs)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.aboutBtn)
        self.toolbar.addAction(self.quitBtn)
        
    def _initFlowview(self):
        self.flowView = FlowView(self.UI_PROPERTIES, parent=self)
    
    def _initFlowViewHeader(self):
        
        # FlowView Label
        flowlabellay = QtGui.QHBoxLayout()
        flowlabellay.setSpacing(5)
        
        self.flowLabel = QtGui.QLabel("Flow View: - New -", self)
        self.flowLabel.setObjectName("flowLabel")
        self.flowLabel.setAlignment(QtCore.Qt.AlignHCenter)
        
        self.editFlowlabelBtn = QtGui.QPushButton("")
        self.editFlowlabelBtn.setFixedWidth(22)
        self.editFlowlabelBtn.setFixedHeight(22)
        self.editFlowlabelBtn.setFlat(True)
        self.editFlowlabelBtn.setIcon(QtGui.QIcon(self.parentPath + r"/icons/edit.png"))
        self.editFlowlabelBtn.setIconSize(QtCore.QSize(18,18))
        self.editFlowlabelBtn.setToolTip("Edit flowview's name")
        self.editFlowlabelBtn.clicked.connect(self.editFlowViewLabel)
        
        flowlabellay.addWidget(self.flowLabel)
        flowlabellay.addWidget(self.editFlowlabelBtn)
        
        self.centralLayout.addItem(flowlabellay)
        
        # Flowview header
        self.flowviewHeader = QtGui.QHBoxLayout()
        self.flowviewHeader.setAlignment(QtCore.Qt.AlignHCenter)
        self.flowviewHeader.setSpacing(20)
        
        self.flowviewHeaderJobs = QtGui.QLabel("Number of job(s): 0")
        self.flowviewHeaderJobs.setFixedHeight(15)
        self.flowviewHeaderJobs.setObjectName("flowviewheader")
        
        self.flowviewHeaderWarning = QtGui.QLabel("Warning(s): 0")
        self.flowviewHeaderWarning.setFixedHeight(15)
        self.flowviewHeaderWarning.setObjectName("flowviewheader")
        
        self.flowviewHeader.addWidget(self.flowviewHeaderJobs)
        self.flowviewHeader.addWidget(self.flowviewHeaderWarning)
        
        self.centralLayout.addItem(self.flowviewHeader)
        
    def _initScrollArea(self):
        
        
        self.scrollView = QtGui.QScrollArea(self)
        self.scrollView.setWidget(self.flowView)
        self.scrollView.setWidgetResizable(True)
        self.scrollView.setMinimumWidth(385)
        self.centralLayout.addWidget(self.scrollView)
    
    def _initPropertyDock(self):
        
        self.propertyDock = PropertyDock(self.UI_PROPERTIES, self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.propertyDock)
        self.flowView.linkToPropertiesDock(self.propertyDock)
        self.propertyDock.linkToFlowView(self.flowView)
        
    def _initOutputDock(self):
        
        self.outputDock = OutputDock(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.outputDock)
        self.propertyDock.linkToOutputDock(self.outputDock)
        self.flowView.linkToOutputDock(self.outputDock)
    
    def _initGraphdataDock(self):
        
        self.graphDataDock = GraphdataDock(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.graphDataDock)
        
    def _initProgressbar(self):
        
        progressInfoLay = QtGui.QHBoxLayout()
        self.progressInfo = QtGui.QLabel("Ready")
        self.progressInfo.setAlignment(QtCore.Qt.AlignLeft)
        self.timerLabel.setAlignment(QtCore.Qt.AlignRight)
        
        progressInfoLay.addWidget(self.progressInfo)
        progressInfoLay.addWidget(self.timerLabel)
        
        self.progressBarActivity = QtGui.QProgressBar()
        self.progressBarActivity.setFixedHeight(5)
        self.progressBarActivity.setObjectName("progressActivity")
        
        progressBarLay = QtGui.QHBoxLayout()
        progressBarLay.setSpacing(5)
                
        self.progressBar = QtGui.QProgressBar()
        self.progressBar.setFixedHeight(17)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)
        
        self.cancelFlow = QtGui.QPushButton("")
        self.cancelFlow.setStatusTip("Cancel current rendering flowview or job")
        self.cancelFlow.setFlat(True)
        self.cancelFlow.setIcon(QtGui.QIcon(self.parentPath + r"/icons/remove.png"))
        self.cancelFlow.setFixedSize(QtCore.QSize(18,18))
        self.cancelFlow.setIconSize(QtCore.QSize(15,15))
        self.cancelFlow.clicked.connect(self.flowView.cancelFlowrender)
        self.cancelFlow.setEnabled(False)
        
        progressBarLay.addWidget(self.progressBar)
        progressBarLay.addWidget(self.cancelFlow)
        
        self.centralLayout.addItem(progressInfoLay)
        self.centralLayout.addWidget(self.progressBarActivity)
        self.centralLayout.addItem(progressBarLay)
        
    # Update UI from flowview
    def _ui_updateProgressBar(self, step):
        
        newStep = self.progressBar.value() + int(step)
        if newStep > 100:
            newStep = 100
        
        self.progressBar.setValue(newStep)
        
    def _ui_resetProgressBar(self):
        self.progressBar.setMaximum(100)
        self.progressBar.setMinimum(0)
        self.progressBar.setValue(0)
        
    def _ui_enableActivityMonitor(self, enable=True):
        
        if enable:
            self.progressBarActivity.setMinimum(0)
            self.progressBarActivity.setMaximum(0)
        else:
            self.progressBarActivity.setMinimum(0)
            self.progressBarActivity.setMaximum(100)
        
    def _ui_progressBarToActivityMonitor(self, enable=True):
        
        if enable:
            self.progressBar.setMaximum(0)
            self.progressBar.setMinimum(0)
            self.cancelFlow.setEnabled(True)
        else:
            self._ui_resetProgressBar()
            self.cancelFlow.setEnabled(False)
            
    def _ui_setInfoMessage(self, msg, toOutput=False):
        
        if toOutput:
            utils.LogW.writeLog(self.outputDock.output, msg)
        
        if "<b>" in msg:
            msg = msg.replace("</b></font>", "")
            msg = msg.split("<b>")[1]
            
        self.progressInfo.setText(str(msg))
        
    def _ui_disableButton(self, enable=False):
        
        self.addNukeJob.setEnabled(enable)
        self.addHoudiniJob.setEnabled(enable)
        self.addMayaJob.setEnabled(enable)
        self.addBatchJob.setEnabled(enable)
        self.addPythonJob.setEnabled(enable)
        
        self.addNukeJobMenu.setEnabled(enable)
        self.addHoudiniJobMenu.setEnabled(enable)
        self.addMayaJobMenu.setEnabled(enable)
        self.addBatchJobMenu.setEnabled(enable)
        self.addPythonJobMenu.setEnabled(enable)        
        
        self.clearJobs.setEnabled(enable)
        self.openDocBtn.setEnabled(enable)
        self.saveDocBtn.setEnabled(enable)
        self.newdocbtn.setEnabled(enable)
        
        self.openFile.setEnabled(enable)
        self.saveFile.setEnabled(enable)
        self.newFlowview.setEnabled(enable)
        
        if enable:
            self._initToolBarButtons()
            
    def displayFlowViewHeader(self, enable):
        self.flowviewHeaderJobs.setVisible(enable)
        self.flowviewHeaderWarning.setVisible(enable)
        
    def updateCleanPyMode(self, toggle):
        self.UI_PROPERTIES["clean_py"] = toggle
        
    def cleanTmpFiles(self):
        
        tmpFolder = os.path.dirname(os.path.dirname(__file__)) + "\\_pytmp"
        
        c = 0
        for f in os.listdir(tmpFolder):
            os.remove(tmpFolder + "\\" + f)
            c += 1
        self.outputDock.output.append(utils.ErrorStr.ErrorStr.INFO + str(c) + " temporary file(s) deleted.")
    
    def addJobToFLowView(self, jobtype):
        '''
            Add a job widget to the flowview
        '''
        
        job_id = len(self.flowView.listJobs())
        
        
        if jobtype == JobTypes.MAYA:
            self.flowView.addJob(MayaJobWidget(self.propertyDock, job_id, self.flowView, self.outputDock.output, self.UI_PROPERTIES, parent=self.flowView))
            
        elif jobtype == JobTypes.NUKE:
            self.flowView.addJob(NukeJobWidget(self.propertyDock, job_id, self.flowView, self.outputDock.output, self.UI_PROPERTIES, parent=self.flowView))
            
        elif jobtype == JobTypes.HOUDINI:
            self.flowView.addJob(HoudiniJobWidget( self.propertyDock, job_id, self.flowView, self.outputDock.output, self.UI_PROPERTIES, parent=self.flowView))
            
        elif jobtype == JobTypes.PYTHON:
            self.flowView.addJob(PythonJobWidget( self.propertyDock, job_id, self.flowView, self.outputDock.output, parent=self.flowView))
            
        elif jobtype == JobTypes.BATCH:
            self.flowView.addJob(BatchJobWidget( self.propertyDock, job_id, self.flowView, self.outputDock.output, parent=self.flowView))
        
    def clearJobsFromFlowView(self):
        self.flowView.clearJobs()
        self.propertyDock.hideProperties(clear=True)
        
    def editFlowViewLabel(self):
        
        text, ok = QtGui.QInputDialog.getText(self, 'Flowview name', 
            'Enter a new name:')
        
        if ok and text:
            self.flowLabel.setText("Flowview: " + str(text))
            
    
    def createNewFlow(self):
        
        try:
            with open(os.path.dirname(os.path.dirname(__file__)) + "\\pythoninter.txt", 'r') as inf:
                datas = inf.readlines()
                
            datas = [d for d in datas if not d.startswith("#")]
            inter = datas[0].split("=")[-1]
            
            if inter == "DEFAULT":
                subprocess.Popen("python " + os.path.dirname(os.path.dirname(__file__)) + "\\hman.py")
            else:
                subprocess.Popen(inter + " " + os.path.dirname(os.path.dirname(__file__)) + "\\hman.py")
            
        except Exception as e:
            print str(e)
            
    def updatePath(self):
        
        picker = PathPicker(self.version)
        picker.linkToMainUi(self)
        picker.exec_()