import os
import time

from PyQt4 import QtGui
from PyQt4 import QtCore

from main.JobWidget import SoftPropertiesWidget
from houdiniHman.LoadHip import PickHouNode

from utils import LogW
from utils.ErrorStr import ErrorStr

class BatchProperties(SoftPropertiesWidget):
    
    def __init__(self, jobWidget, output):
        SoftPropertiesWidget.__init__(self)
        
        self.jobWidget = jobWidget
        self.output = output
        
        self.batchPropertiesLayout = QtGui.QVBoxLayout()
        self.batchPropertiesLayout.setSpacing(10)
        
        # Wait toggle
        self.waitEnd = QtGui.QCheckBox("Wait for end of process")
        self.waitEnd.setChecked(self.jobWidget.properties["wait"])
        self.waitEnd.clicked.connect(self.updateWaitToggle)
        
        self.batchPropertiesLayout.addWidget(self.waitEnd)
        
        # Override file
        self.overrideFile = QtGui.QCheckBox("Use command instead of file")
        self.overrideFile.setChecked(self.jobWidget.properties["use_command"])
        self.overrideFile.clicked.connect(lambda: self.enableCommand(self.overrideFile.isChecked()))
        
        self.batchPropertiesLayout.addWidget(self.overrideFile)
                
        commandLayout = QtGui.QHBoxLayout()
        commandLayout.setSpacing(10)
        self.commandLabel = QtGui.QLabel("Command:")
        self.commandLabel.setFixedWidth(50)
        self.commandLine = QtGui.QLineEdit(self.jobWidget.properties["command"])
        self.commandLine.returnPressed.connect(self.updateCommand)
        self.commandLine.focusOutEvent = self.updateCommand
        
        commandLayout.addWidget(self.commandLabel)
        commandLayout.addWidget(self.commandLine)
        
        self.batchPropertiesLayout.addItem(commandLayout)
        
        # Args layout
        self.args = []
        for i in range(5):
            arg = ArgLayout(i, self.jobWidget)
            self.batchPropertiesLayout.addItem(arg)
            self.args.append(arg)
        
        # Launch button
        self.renderCurrentBtn.setText("Launch Bat Command")
        self.renderCurrentBtn.setObjectName("pushbutton")
        self.renderCurrentBtn.clicked.connect(self.jobWidget.renderCurrent)
        self.updateButtonVisibility()
        self.batchPropertiesLayout.addWidget(self.renderCurrentBtn)
        
        self.setLayout(self.batchPropertiesLayout)
        
        self.enableCommand(self.jobWidget.properties["use_command"])
        
    def updateCommand(self, e=None):
        self.jobWidget.properties["command"] = str(self.commandLine.text())
        self.jobWidget.updateWarning()
        self.updateButtonVisibility()
        
    def updateWaitToggle(self):
        self.jobWidget.properties["wait"] = self.waitEnd.isChecked()
        
    def enableCommand(self, toggle):
        
        for i in self.args:
            i.enableArgs(toggle)
            
        self.commandLabel.setEnabled(toggle)
        self.commandLine.setEnabled(toggle)
        
        self.jobWidget.properties["use_command"] = toggle
        self.jobWidget.updateWarning()
        self.updateButtonVisibility()
        
    def updateButtonVisibility(self):
        
        if self.jobWidget.properties["use_command"] and self.jobWidget.properties["command"]:
            self.renderCurrentBtn.setEnabled(True)
        
        else:
            if not os.path.exists(self.jobWidget.properties["file_path"]):
                self.renderCurrentBtn.setEnabled(False)
            else:
                self.renderCurrentBtn.setEnabled(True)
                
    def updateCurrentJobBtnVisibility(self, enable=True):
        self.updateButtonVisibility()
        
class ArgLayout(QtGui.QHBoxLayout):
    
    def __init__(self, ID, jobWidget):
        QtGui.QHBoxLayout.__init__(self)
        
        self.setSpacing(10)
        self.ID = ID
        self.jobWidget = jobWidget
        
        self.argLayout = QtGui.QHBoxLayout()
        self.argLayout.setSpacing(10)
        self.argLabel = QtGui.QLabel("arg #" + str(ID+1) + ":")
        self.argLabel.setFixedWidth(50)
        self.argLine = QtGui.QLineEdit(self.jobWidget.properties["args"][ID])
        self.argLine.returnPressed.connect(lambda: self.updateArg(self.argLine.text()))
        self.argLine.focusOutEvent = self.updateArg
        
        self.addWidget(self.argLabel)
        self.addWidget(self.argLine)
    
    def updateArg(self, e=None):
        self.jobWidget.properties["args"][self.ID] = str(self.argLine.text())
        
    def getArg(self):
        return str(self.argLine.text())
    
    def enableArgs(self, enable=True):
        self.argLabel.setEnabled(enable)
        self.argLine.setEnabled(enable)