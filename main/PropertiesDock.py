from __future__ import absolute_import
import os

from PyQt4 import QtGui
from PyQt4 import QtCore

from .JobWidget import JobTypes
from .JobWidget import SoftPropertiesWidget

from houdiniHman.HoudiniProperties import HoudiniProperties
from mayaHman.MayaProperties import MayaProperties
from pythonHman.PythonProperties import PytonProperties
from nukeHman.NukeProperties import NukeProperties
from batchHman.BatchProperties import BatchProperties

from utils.JobToolTips import jobToolTips

iconsPath = os.path.dirname(os.path.dirname(__file__)) + "\\icons\\"

class PropertyDock(QtGui.QDockWidget):
    
    def __init__(self, UI_PROPERTIES, parent=None):
        
        QtGui.QDockWidget.__init__(self, parent=parent)
        
        self.output = None
        self.UI_PROPERTIES = UI_PROPERTIES
        
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        self.setWindowTitle("Properties")
        
        self.setFeatures(QtGui.QDockWidget.DockWidgetMovable|
                         QtGui.QDockWidget.DockWidgetFloatable)
        
        self.dockWidget = QtGui.QWidget()
        self.dockWidgetLayout = QtGui.QVBoxLayout()
        self.dockWidgetLayout.setAlignment(QtCore.Qt.AlignTop)
        self.dockWidget.setLayout(self.dockWidgetLayout)
        self.setWidget(self.dockWidget)
        
        self.CURRENT_ID_DISPLAYED = 0
        self.CURRENT_JOBWIDGET_DISPLAYED = None
        self.CURRENT_SOFTPROPERTIES = None
        
        # Will be initialized from main UI
        self.flowview = None
        
        self.commonPropertiesList = []
        self.initProperties()
        
        self.hideProperties()
        
        
    def initProperties(self):
        
        self.propertyWidget = QtGui.QWidget()
        self.propertyLayout = QtGui.QVBoxLayout()
        self.propertyLayout.setSpacing(15)
        self.propertyLayout.setAlignment(QtCore.Qt.AlignTop)
        
        # Job Type
        self.headerLayout = QtGui.QHBoxLayout()
        self.headerLayout.setSpacing(15)
        self.typeLabel = QtGui.QLabel("Job type: None")
        self.typeLabel.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.jobID = QtGui.QLabel("ID: X")
        self.jobID.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        
        self.clearPropertiesDock = QtGui.QPushButton("")
        self.clearPropertiesDock.setFlat(True)
        self.clearPropertiesDock.setObjectName("flatbutton")
        self.clearPropertiesDock.setIcon(QtGui.QIcon(iconsPath+"blue_clear.png"))
        self.clearPropertiesDock.setIconSize(QtCore.QSize(20,20))
        self.clearPropertiesDock.setFixedSize(24,24)
        self.clearPropertiesDock.setToolTip("Clear properties dock")
        self.clearPropertiesDock.clicked.connect(lambda: self.flowview.mousePressEvent(None))
        
        self.headerLayout.addWidget(self.typeLabel)
        self.headerLayout.addWidget(self.jobID)
        self.headerLayout.addWidget(self.clearPropertiesDock)
        
        self.commonPropertiesList.append(self.typeLabel)
        self.commonPropertiesList.append(self.jobID)
        self.commonPropertiesList.append(self.clearPropertiesDock)
        
        # Description
        descriptionLayout = QtGui.QHBoxLayout()
        descriptionLayout.setSpacing(10)
        self.descriptionLabel = QtGui.QLabel("Description:")
        self.descriptionLine = QtGui.QLineEdit("")
        self.descriptionLine.returnPressed.connect(self.confirmDecription)
        descriptionLayout.addWidget(self.descriptionLabel)
        descriptionLayout.addWidget(self.descriptionLine)
        
        self.commonPropertiesList.append(self.descriptionLabel)
        self.commonPropertiesList.append(self.descriptionLine)
        
        # Frame range
        self.frameRangeLayout = QtGui.QHBoxLayout()
        self.frameRangeLayout.setSpacing(10)
        
        self.overrideFrames = QtGui.QCheckBox("Override Frame Range")
        self.overrideFrames.clicked.connect(lambda: self._saveOverrideFrame(self.overrideFrames.isChecked()))
            
        self.frameRangeLayout.addWidget(self.overrideFrames)
        
        self.startFrame = QtGui.QSpinBox()
        self.startFrame.setMaximum(99999)
        self.startFrame.valueChanged.connect(lambda: self._saveStartFrame(self.startFrame.value()))
        self.endFrame = QtGui.QSpinBox()
        self.endFrame.setMaximum(99999)
        self.endFrame.valueChanged.connect(lambda: self._saveEndFrame(self.endFrame.value()))
        
        self.startFrameLabel = QtGui.QLabel("Start Frame:")
        self.frameRangeLayout.addWidget(self.startFrameLabel)
        self.frameRangeLayout.addWidget(self.startFrame)
        self.endFrameLabel= QtGui.QLabel("End Frame:")
        self.frameRangeLayout.addWidget(self.endFrameLabel)
        self.frameRangeLayout.addWidget(self.endFrame)
        
        self.commonPropertiesList.append(self.overrideFrames)
        self.commonPropertiesList.append(self.startFrameLabel)
        self.commonPropertiesList.append(self.endFrameLabel)
        self.commonPropertiesList.append(self.startFrame)
        self.commonPropertiesList.append(self.endFrame)
        
        # Path
        jobPathLayout = QtGui.QHBoxLayout()
        jobPathLayout.setSpacing(10)
        
        self.jobPathLabel = QtGui.QLabel("File path: ")
        self.jobPathLine = QtGui.QLineEdit("")
        self.jobPathLine.setObjectName("filepathline")
        self.jobPathLine.returnPressed.connect(lambda: self.confirmFile(self.jobPathLine.text()))
        self.jobPathBtn = QtGui.QPushButton("")
        self.jobPathBtn.setFlat(True)
        self.jobPathBtn.setIcon(QtGui.QIcon(iconsPath + "pickfolder.png"))
        self.jobPathBtn.setFixedSize(QtCore.QSize(25,25))
        self.jobPathBtn.setIconSize(QtCore.QSize(20,20))
        self.jobPathBtn.clicked.connect(lambda: self._pickFile("All", "*"))
        
        self.commonPropertiesList.append(self.jobPathLabel)
        self.commonPropertiesList.append(self.jobPathLine)
        self.commonPropertiesList.append(self.jobPathBtn)
        
        jobPathLayout.addWidget(self.jobPathLabel)
        jobPathLayout.addWidget(self.jobPathLine)
        jobPathLayout.addWidget(self.jobPathBtn)
        
        # Construct properties layout 
        self.propertyLayout.addItem(self.headerLayout)
        self.propertyLayout.addItem(descriptionLayout)
        self.propertyLayout.addItem(self.frameRangeLayout)
        self.propertyLayout.addItem(jobPathLayout)
        
        self.propertyWidget.setLayout(self.propertyLayout)
        self.dockWidgetLayout.addWidget(self.propertyWidget)

    def linkToFlowView(self, flowview):
        self.flowview = flowview
    
    def linkToOutputDock(self, output):
        self.output = output
    
    def _showCommonProperties(self, jobWidget):
        '''
            Common properties shared by all type of jobs.
        '''
        
        self.hideProperties()
        
        self.CURRENT_JOBWIDGET_DISPLAYED = jobWidget
        
        if jobWidget.jobType not in [JobTypes.BATCH, JobTypes.PYTHON]:
            self.overrideFrames.setEnabled(True)
            self.overrideFrames.setChecked(jobWidget.properties["override_frames"])
            self.endFrame.setValue(jobWidget.properties["end_frame"])
            self.startFrame.setValue(jobWidget.properties["start_frame"])
        else:
            self.overrideFrames.setEnabled(False)
            self.overrideFrames.setChecked(False)
            self.endFrame.setValue(0)
            self.startFrame.setValue(0)
        
        for n in self.commonPropertiesList:
            n.setVisible(True)
            
        self.typeLabel.setText("Job type: " + str(jobWidget.jobType))
        self.jobID.setText("ID: " + str(jobWidget.ID))
        self.jobPathLine.setText(jobWidget.properties["file_path"])
        self.descriptionLine.setText(jobWidget.properties["description"])
        
        # Update pick file button (filter)
        self.jobPathBtn.clicked.disconnect()
        self.jobPathBtn.clicked.connect(lambda: self._pickFile(jobWidget.jobType, jobWidget.file_filter))
        
        
    def hideProperties(self, clear=False):
        '''
            Hide property dock when unselected.
            If fonc if called from main UI ( clear all jobs => clear = True)
            Change the current widget displayed to None.
        '''
        self._saveCommonProperties()
        
        if clear:
            self.CURRENT_JOBWIDGET_DISPLAYED = None
        
        for n in self.commonPropertiesList:
            n.setVisible(False)
        
        # Hide software properties if any
        softProperties = []
        for i in range(self.dockWidgetLayout.count()):
            curWidg = self.dockWidgetLayout.itemAt(i).widget()
            if isinstance(curWidg, SoftPropertiesWidget):
                softProperties.append(curWidg)
        
        for i in softProperties:
            i.setParent(None)
        
    def showProperties(self, jobWidget):
        '''
            Show property dock when a jobWidget is selected
        '''
        self._showCommonProperties(jobWidget)
        
        # Add software properties
        
        if jobWidget.jobType == JobTypes.HOUDINI:
            self.CURRENT_SOFTPROPERTIES = HoudiniProperties(jobWidget, self.output, self.UI_PROPERTIES)
            self.dockWidgetLayout.addWidget(self.CURRENT_SOFTPROPERTIES)
            self.enableFrameRange(self.overrideFrames.isChecked())
            
        if jobWidget.jobType == JobTypes.MAYA:
            self.CURRENT_SOFTPROPERTIES = MayaProperties(jobWidget, self.output, self.UI_PROPERTIES)
            self.dockWidgetLayout.addWidget(self.CURRENT_SOFTPROPERTIES)
            self.enableFrameRange(self.overrideFrames.isChecked())
            
        if jobWidget.jobType == JobTypes.NUKE:
            self.CURRENT_SOFTPROPERTIES = NukeProperties(jobWidget, self.output)
            self.dockWidgetLayout.addWidget(self.CURRENT_SOFTPROPERTIES)
            self.enableFrameRange(self.overrideFrames.isChecked())
            
        if jobWidget.jobType == JobTypes.PYTHON:
            self.CURRENT_SOFTPROPERTIES = PytonProperties(jobWidget, self.output)
            self.dockWidgetLayout.addWidget(self.CURRENT_SOFTPROPERTIES)
            self.enableFrameRange(False)
            
        if jobWidget.jobType == JobTypes.BATCH:
            self.CURRENT_SOFTPROPERTIES = BatchProperties(jobWidget, self.output)
            self.dockWidgetLayout.addWidget(self.CURRENT_SOFTPROPERTIES)
            self.enableFrameRange(False)
            
    def _saveCommonProperties(self):
        
        if self.CURRENT_JOBWIDGET_DISPLAYED and self.CURRENT_JOBWIDGET_DISPLAYED in self.flowview.listJobs():
            
            self.CURRENT_JOBWIDGET_DISPLAYED.properties["file_path"] = str(self.jobPathLine.text())
            self.CURRENT_JOBWIDGET_DISPLAYED.properties["end_frame"] = int(self.endFrame.value())
            self.CURRENT_JOBWIDGET_DISPLAYED.properties["start_frame"] = int(self.startFrame.value())
            self.CURRENT_JOBWIDGET_DISPLAYED.properties["description"] = str(self.descriptionLine.text())
            self.CURRENT_JOBWIDGET_DISPLAYED.properties["override_frames"] = self.overrideFrames.isChecked()
            
            self.CURRENT_JOBWIDGET_DISPLAYED.setToolTip(jobToolTips(self.CURRENT_JOBWIDGET_DISPLAYED.jobType,
                                                                    self.CURRENT_JOBWIDGET_DISPLAYED.ID,
                                                                    str(self.jobPathLine.text()),
                                                                    str(self.descriptionLine.text())))
            
            
            self.enableFrameRange(self.overrideFrames.isChecked())
    
    # Save all frames values
    def _saveStartFrame(self, value):
        if self.CURRENT_JOBWIDGET_DISPLAYED and self.CURRENT_JOBWIDGET_DISPLAYED in self.flowview.listJobs():
            self.CURRENT_JOBWIDGET_DISPLAYED.properties["start_frame"] = int(value)
            
    def _saveEndFrame(self, value):
        if self.CURRENT_JOBWIDGET_DISPLAYED and self.CURRENT_JOBWIDGET_DISPLAYED in self.flowview.listJobs():
            self.CURRENT_JOBWIDGET_DISPLAYED.properties["end_frame"] = int(value)
            
    def _saveOverrideFrame(self, value):
        if self.CURRENT_JOBWIDGET_DISPLAYED and self.CURRENT_JOBWIDGET_DISPLAYED in self.flowview.listJobs():
            self.CURRENT_JOBWIDGET_DISPLAYED.properties["override_frames"] = int(value)
            
            if self.CURRENT_JOBWIDGET_DISPLAYED.jobType not in [JobTypes.BATCH, JobTypes.PYTHON]:
                self.enableFrameRange(value)
            
    # Save description  
    def confirmDecription(self):
        '''
            Update job's tooltip when press enter in the line edit.
        '''
        if self.CURRENT_JOBWIDGET_DISPLAYED:
            self.CURRENT_JOBWIDGET_DISPLAYED.properties["description"] = str(self.descriptionLine.text())
            self.CURRENT_JOBWIDGET_DISPLAYED.setToolTip(jobToolTips(self.CURRENT_JOBWIDGET_DISPLAYED.jobType,
                                                                    self.CURRENT_JOBWIDGET_DISPLAYED.ID,
                                                                    str(self.jobPathLine.text()),
                                                                    str(self.descriptionLine.text())))
    
    # Save file
    def confirmFile(self, txt):
        
        if self.CURRENT_JOBWIDGET_DISPLAYED:
            
            if not os.path.exists(txt):
                self.CURRENT_JOBWIDGET_DISPLAYED.properties["file_path"] = ""
                self.CURRENT_SOFTPROPERTIES.updateCurrentJobBtnVisibility(False)
            else:
                self.CURRENT_JOBWIDGET_DISPLAYED.properties["file_path"] = str(txt)
                self.CURRENT_SOFTPROPERTIES.updateCurrentJobBtnVisibility(True)
                
            self.CURRENT_JOBWIDGET_DISPLAYED.updateWarning()
            self._saveCommonProperties()
    
    def _pickFile(self, jobType, file_type):
        '''
            Pick a file according to jobType and file_type from properties
        '''
        p = QtGui.QFileDialog.getOpenFileName(parent=None, filter = "{0} Files ({1})".format(jobType, file_type))
        if p:
            self.jobPathLine.setText(str(p))
            self._saveCommonProperties()
            self.CURRENT_JOBWIDGET_DISPLAYED.updatePathInfo(p)
            if self.CURRENT_JOBWIDGET_DISPLAYED.WARNING:
                self.CURRENT_SOFTPROPERTIES.renderCurrentBtn.setEnabled(False)
            else:
                self.CURRENT_SOFTPROPERTIES.renderCurrentBtn.setEnabled(True)
                
            self.CURRENT_SOFTPROPERTIES.updateCurrentJobBtnVisibility(True)
            
        if self.CURRENT_JOBWIDGET_DISPLAYED:
            self.CURRENT_JOBWIDGET_DISPLAYED.updateWarning()
            if self.CURRENT_JOBWIDGET_DISPLAYED.WARNING:
                self.CURRENT_SOFTPROPERTIES.renderCurrentBtn.setEnabled(False)
            else:
                self.CURRENT_SOFTPROPERTIES.renderCurrentBtn.setEnabled(True)
            self.CURRENT_SOFTPROPERTIES.updateCurrentJobBtnVisibility(False)
            
    def enableFrameRange(self, enable=True):
        '''
            Enable or disable frame range widgets
        '''
        
        self.startFrame.setEnabled(enable)
        self.startFrameLabel.setEnabled(enable)
        self.endFrame.setEnabled(enable)
        self.endFrameLabel.setEnabled(enable)  
        