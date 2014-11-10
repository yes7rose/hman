import os
import time

from PyQt4 import QtGui
from PyQt4 import QtCore

from main.JobWidget import SoftPropertiesWidget
from nukeHman.initNuke import PickNukeNode

from utils import LogW
from utils.ErrorStr import ErrorStr

iconsPath = os.path.dirname(os.path.dirname(__file__)) + "\\icons\\"

class NukeProperties(SoftPropertiesWidget):
    
    def __init__(self, jobWidget, output):
        SoftPropertiesWidget.__init__(self)
        
        self.nukePropertiesLayout = QtGui.QVBoxLayout()
        self.nukePropertiesLayout.setAlignment(QtCore.Qt.AlignTop)
        
        self.jobWidget = jobWidget
        self.output = output

        self._initNukeProperties()
        self.updateBtnVisibility()
        self.setLayout(self.nukePropertiesLayout)
        
    def _initNukeProperties(self):
        
        # Render node layout
        renderNodeLay = QtGui.QHBoxLayout()
        renderNodeLay.setSpacing(10)
        renderNodeLay.setAlignment(QtCore.Qt.AlignLeft)
        
        if not self.jobWidget.properties["render_node"]:
            msg = "- None -"
        else:
            msg = self.jobWidget.properties["render_node"]
            
        self.renderTypeLabel = QtGui.QLabel("Render Node: " + msg)
        
        self.pickRenderNode = QtGui.QPushButton("")
        self.pickRenderNode.setFlat(True)
        self.pickRenderNode.setObjectName("flatbuttonicon")
        self.pickRenderNode.setIcon(QtGui.QIcon(iconsPath + "picknode.png"))
        self.pickRenderNode.setFixedSize(QtCore.QSize(35,35))
        self.pickRenderNode.setIconSize(QtCore.QSize(32,32))
        self.pickRenderNode.clicked.connect(self._pickRenderNode)
                
        renderNodeLay.addWidget(self.renderTypeLabel)
        renderNodeLay.addWidget(self.pickRenderNode)
        
        self.nukePropertiesLayout.addItem(renderNodeLay)
        
        # Output path
        outputPathLayout = QtGui.QHBoxLayout()
        outputPathLayout.setSpacing(10)
        
        self.outputPathLabel = QtGui.QLabel("Output Path:")
        self.outputPathLine = QtGui.QLineEdit(self.jobWidget.properties["output_path"])
        self.pickOutputPath = QtGui.QPushButton("")
        self.pickOutputPath.setFlat(True)
        self.pickOutputPath.setIcon(QtGui.QIcon(iconsPath + "pickfolder.png"))
        self.pickOutputPath.setFixedSize(QtCore.QSize(25,25))
        self.pickOutputPath.setIconSize(QtCore.QSize(20,20))
        self.pickOutputPath.clicked.connect(self._pickOutputPath)
        
        if self.jobWidget.properties["render_node"]:
            self.outputPathLabel.setEnabled(True)
            self.outputPathLine.setEnabled(True)
            self.pickOutputPath.setEnabled(True)
        else:
            self.outputPathLabel.setEnabled(False)
            self.outputPathLine.setEnabled(False)
            self.pickOutputPath.setEnabled(False)
        
        
        outputPathLayout.addWidget(self.outputPathLabel)
        outputPathLayout.addWidget(self.outputPathLine)
        outputPathLayout.addWidget(self.pickOutputPath)
        
        self.nukePropertiesLayout.addItem(outputPathLayout)
        
        # Render button
        self.renderCurrentBtn.setText("Render Current Nuke Script")
        self.renderCurrentBtn.setObjectName("pushbutton")
        self.renderCurrentBtn.clicked.connect(self.jobWidget.renderCurrent)
        self.nukePropertiesLayout.addWidget(self.renderCurrentBtn)
        
    def _pickRenderNode(self):
        
        filePath = self.jobWidget.properties["file_path"]
        if os.path.exists(filePath):
            inTime = time.time()
            ui = PickNukeNode(filePath, inTime, self.output)
            ui.exec_()
            
            if ui.SELECTED_NODE:
                self.jobWidget.properties["render_node"] = ui.SELECTED_NODE
                self.renderTypeLabel.setText("Render Node: " + ui.SELECTED_NODE)
                self.jobWidget.updateWarning()
                self.updateBtnVisibility()
                

                self.outputPathLabel.setEnabled(True)
                self.outputPathLine.setEnabled(True)
                self.pickOutputPath.setEnabled(True)
            else:
                self.outputPathLabel.setEnabled(False)
                self.outputPathLine.setEnabled(False)
                self.pickOutputPath.setEnabled(False)
            
        else:
            LogW.writeLog(self.output, ErrorStr.ERROR + "File not foundn enter a valid File Path.")
            
    def _pickOutputPath(self):
        
        p = QtGui.QFileDialog.getSaveFileName(parent=None, filter = "Images Files (*)")
        if p:
            self.outputPathLine.setText(str(p))
            self.jobWidget.properties["output_path"] = str(p)
            
    def updateBtnVisibility(self):
        
        if not self.jobWidget.properties["file_path"] or not self.jobWidget.properties["render_node"]:
            self.renderCurrentBtn.setEnabled(False)
        else:
            self.renderCurrentBtn.setEnabled(True)
        