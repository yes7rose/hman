import os
import time

from PyQt4 import QtGui
from PyQt4 import QtCore


from main.JobWidget import SoftPropertiesWidget
from houdiniHman.LoadHip import PickHouNode

from utils import LogW
from utils.ErrorStr import ErrorStr

class PytonProperties(SoftPropertiesWidget):
    
    def __init__(self, jobWidget, output):
        SoftPropertiesWidget.__init__(self)
        
        self.pythonPropertiesLayout = QtGui.QVBoxLayout()
        self.pythonPropertiesLayout.setAlignment(QtCore.Qt.AlignTop)
        
        self.jobWidget = jobWidget
        self.output = output

        self._initPythonPropertiesLayout()
        self.setLayout(self.pythonPropertiesLayout)
        
    def _initPythonPropertiesLayout(self):
        
        # Interpreter
        interpreterLayout = QtGui.QHBoxLayout()
        interpreterLayout.setSpacing(10)
        
        self.interpreterLabel = QtGui.QLabel("Python Interpreter:")
        self.interpreterPath = QtGui.QLineEdit(self.jobWidget.properties["interpreter"])
        self.interpreterPath.returnPressed.connect(lambda: self.updateInterpreterFile(str(self.interpreterPath.text())))
        self.pickInterpreterBtn = QtGui.QPushButton("Pick")
        self.pickInterpreterBtn.clicked.connect(self.pickInterpreter)
        
        interpreterLayout.addWidget(self.interpreterLabel)
        interpreterLayout.addWidget(self.interpreterPath)
        interpreterLayout.addWidget(self.pickInterpreterBtn)
        
        # Launch script
        self.launchScript = QtGui.QPushButton("Execute Current Script")
        self.launchScript.setObjectName("pushbutton")
        self.launchScript.clicked.connect(self.jobWidget.renderCurrent)
        self.updateButtonVisibility()
        
        self.pythonPropertiesLayout.addItem(interpreterLayout)
        self.pythonPropertiesLayout.addWidget(self.launchScript)
    
    def pickInterpreter(self):
        
        p = QtGui.QFileDialog.getOpenFileName(parent=None, filter = "Python Interpreter (*.exe)")
        if p:
            self.interpreterPath.setText(str(p))
            self.jobWidget.properties["interpreter"] = str(p)
            self.updateButtonVisibility()
    
    def pickPythonFile(self):
        
        p = QtGui.QFileDialog.getOpenFileName(parent=None, filter = "Python Files (*.py)")
        if p:
            self.pythonFilePath.setText(str(p))
            self.jobWidget.properties["file_path"] = str(p)
            self.updateButtonVisibility()
                
    def updateButtonVisibility(self):
        
        if self.jobWidget.properties["interpreter"] != "" and self.jobWidget.properties["file_path"] != "":
            self.launchScript.setEnabled(True)
            
            if not os.path.exists(self.jobWidget.properties["interpreter"]) or not os.path.exists(self.jobWidget.properties["file_path"]):
                self.launchScript.setEnabled(False)    
        else:
            self.launchScript.setEnabled(False)
            
        self.jobWidget.updateWarning()
    
    def updateInterpreterFile(self, p):
        
        self.jobWidget.properties["interpreter"] = str(self.interpreterPath.text())
        self.updateButtonVisibility()
    
    def updatePythonFile(self, p):
        
        self.jobWidget.properties["file_path"] = str(self.pythonFilePath.text())
        self.updateButtonVisibility()
    