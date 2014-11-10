from __future__ import absolute_import

import os
import time

from PyQt4 import QtGui
from PyQt4 import QtCore

from main.JobWidget import SoftPropertiesWidget

from .LoadMayaFile import PickMayaNode

from utils import LogW
from utils.ErrorStr import ErrorStr

iconsPath = os.path.dirname(os.path.dirname(__file__)) + "\\icons\\"

class MayaProperties(SoftPropertiesWidget):
    
    def __init__(self, jobWidget, output, UI_PROPERTIES):
        SoftPropertiesWidget.__init__(self)
        
        self.mayaPropertiesLayout = QtGui.QVBoxLayout()
        self.mayaPropertiesLayout.setSpacing(10)
        self.mayaPropertiesLayout.setAlignment(QtCore.Qt.AlignTop)
        
        self.jobWidget = jobWidget
        self.output = output
        self.UI_PROPERTIES = UI_PROPERTIES

        self._initMayaPropertiesLayout()
        self.setLayout(self.mayaPropertiesLayout)
        
    def _initMayaPropertiesLayout(self):
        
        warnLabel = QtGui.QLabel("Rendering Maya file: File should be save as .ma \n(.mb supported for Maya Software renderer)")
        self.mayaPropertiesLayout.addWidget(warnLabel)
        
        MAYA_ACTIONS = ["Render Scene", "Export obj"]
        
        # Action widgets
        actionLayout = QtGui.QHBoxLayout()
        actionLayout.setAlignment(QtCore.Qt.AlignLeft)
        actionLayout.setSpacing(10)
        
        self.actionLabel = QtGui.QLabel("Select a type of job:")
        
        self.mayaAction = QtGui.QComboBox()
        self.mayaAction.addItems(MAYA_ACTIONS)
        self.mayaAction.setCurrentIndex(MAYA_ACTIONS.index(self.jobWidget.properties["job_type"]))
        self.mayaAction.currentIndexChanged.connect(self._changeJobType)
        
        actionLayout.addWidget(self.actionLabel)
        actionLayout.addWidget(self.mayaAction)
        
        self.mayaPropertiesLayout.addItem(actionLayout)
        
        # Pick a camera
        pickCameraLayout = QtGui.QHBoxLayout()
        pickCameraLayout.setAlignment(QtCore.Qt.AlignLeft)
        pickCameraLayout.setSpacing(10)
        self.overrideCamera = QtGui.QCheckBox("Override Camera")
        self.overrideCamera.setChecked(self.jobWidget.properties["override_camera"])
        self.overrideCamera.clicked.connect(self._changeOverrideCamera)
        
        if not self.jobWidget.properties["camera"]:
            lbl = "Camera: - None -"
        else:
            lbl = "camera: " + self.jobWidget.properties["camera"]
            
        self.cameraLabel = QtGui.QLabel(lbl)
        
        self.pickCamera = QtGui.QPushButton("")
        self.pickCamera.setFlat(True)
        self.pickCamera.setObjectName("flatbuttonicon")
        self.pickCamera.setFixedSize(QtCore.QSize(35,35))
        self.pickCamera.setIcon(QtGui.QIcon(iconsPath + "pickCam.png"))
        self.pickCamera.setIconSize(QtCore.QSize(32,32))
        self.pickCamera.setToolTip("Pick a camera from maya scene")
        self.pickCamera.clicked.connect(lambda: self._pickMayaNode("camera"))
        
        pickCameraLayout.addWidget(self.overrideCamera)
        pickCameraLayout.addWidget(self.cameraLabel)
        pickCameraLayout.addWidget(self.pickCamera)
        
        self.mayaPropertiesLayout.addItem(pickCameraLayout)
        
        # Pick a render layer
        pickRenderLayerLay = QtGui.QHBoxLayout()
        pickRenderLayerLay.setAlignment(QtCore.Qt.AlignLeft)
        pickRenderLayerLay.setSpacing(10)
        self.overrideLayer = QtGui.QCheckBox("Override Render Layer")
        self.overrideLayer.setChecked(self.jobWidget.properties["override_render_layer"])
        self.overrideLayer.clicked.connect(self._changeOverrideLayers)
        
        if not self.jobWidget.properties["render_layer"]:
            lbl = "Render Layer: - Default -"
        else:
            lbl = "Render Layer: " + str(self.jobWidget.properties["render_layer"]).replace("[","").replace("]","")
            
        self.renderLayerLabel = QtGui.QLabel(lbl)
        
        self.pickRenderLayer = QtGui.QPushButton("")
        self.pickRenderLayer.setFlat(True)
        self.pickRenderLayer.setObjectName("flatbuttonicon")
        self.pickRenderLayer.setFixedSize(QtCore.QSize(35,35))
        self.pickRenderLayer.setIcon(QtGui.QIcon(iconsPath + "pickLayer.png"))
        self.pickRenderLayer.setIconSize(QtCore.QSize(32,32))
        self.pickRenderLayer.setToolTip("Pick a render layer from maya scene")
        self.pickRenderLayer.clicked.connect(lambda: self._pickMayaNode("render_layer"))
        
        pickRenderLayerLay.addWidget(self.overrideLayer)
        pickRenderLayerLay.addWidget(self.renderLayerLabel)
        pickRenderLayerLay.addWidget(self.pickRenderLayer)
        
        self.mayaPropertiesLayout.addItem(pickRenderLayerLay)
        
        # Pick mesh
        pickMeshLay = QtGui.QHBoxLayout()
        pickMeshLay.setSpacing(10)
        pickMeshLay.setAlignment(QtCore.Qt.AlignLeft)
        
        if not self.jobWidget.properties["object_to_export"]:
            lbl = "Mesh: - None -"
        else:
            lbl = "Mesh: " + str(self.jobWidget.properties["object_to_export"]).replace("[","").replace("]","")
            
        self.meshLabel = QtGui.QLabel(lbl)
        
        self.pickMesh = QtGui.QPushButton("")
        self.pickMesh.setFlat(True)
        self.pickMesh.setObjectName("flatbuttonicon")
        self.pickMesh.setFixedSize(QtCore.QSize(35,35))
        self.pickMesh.setIcon(QtGui.QIcon(iconsPath + "pickMesh.png"))
        self.pickMesh.setIconSize(QtCore.QSize(32,32))
        self.pickMesh.setToolTip("Pick a mesh from maya scene")
        self.pickMesh.clicked.connect(lambda: self._pickMayaNode("mesh"))
        
        pickMeshLay.addWidget(self.meshLabel)
        pickMeshLay.addWidget(self.pickMesh)
        
        self.mayaPropertiesLayout.addItem(pickMeshLay)
        
        # Output path
        outputPathLayout = QtGui.QHBoxLayout()
        outputPathLayout.setSpacing(10)
        
        self.overrideOuputPath = QtGui.QCheckBox("Output folder:")
        self.overrideOuputPath.setChecked(self.jobWidget.properties["override_output_path"])
        self.overrideOuputPath.clicked.connect(self._changeOverrideOutput)
        
        if self.mayaAction.currentIndex() == 0:
            self.outputPath = QtGui.QLineEdit(self.jobWidget.properties["render_outputpath"])
        elif self.mayaAction.currentIndex() == 1 :
            self.outputPath = QtGui.QLineEdit(self.jobWidget.properties["obj_outputpath"])
            
        self.outputPath.returnPressed.connect(lambda: self._changeOutputPath(self.outputPath.text(), self.mayaAction.currentIndex()))
        self.pickOutputPath = QtGui.QPushButton("")
        self.pickOutputPath.setFlat(True)
        self.pickOutputPath.setIcon(QtGui.QIcon(iconsPath + "pickfolder.png"))
        self.pickOutputPath.setFixedSize(QtCore.QSize(25,25))
        self.pickOutputPath.setIconSize(QtCore.QSize(20,20))
        self.pickOutputPath.clicked.connect(lambda: self._pickOutputPath(self.mayaAction.currentIndex()))
        
        outputPathLayout.addWidget(self.overrideOuputPath)
        outputPathLayout.addWidget(self.outputPath)
        outputPathLayout.addWidget(self.pickOutputPath)
        
        self.mayaPropertiesLayout.addItem(outputPathLayout)
        
        # Render scene button
        self.renderCurrentBtn = QtGui.QPushButton("Render Maya Scene")
        self.renderCurrentBtn.setObjectName("pushbutton")
        self.renderCurrentBtn.clicked.connect(self.jobWidget.renderCurrent)
        self.mayaPropertiesLayout.addWidget(self.renderCurrentBtn)
        
        self.updateUIstate()
        if self.jobWidget.WARNING:
            self.renderCurrentBtn.setEnabled(False)
        else:
            self.renderCurrentBtn.setEnabled(True)
            
    def _pickMayaNode(self, mode):
        
        filePath = self.jobWidget.properties["file_path"]
        if os.path.exists(filePath):
            
            inTime = time.time()
            
            ui = PickMayaNode(filePath, inTime, self.output, mode, self.UI_PROPERTIES)
            ui.exec_()
            
            if ui.SELECTED_NODE:
                if mode == "camera":
                    self.cameraLabel.setText("Camera: " + ui.SELECTED_NODE[0])
                    self.jobWidget.properties["camera"] = ui.SELECTED_NODE[0]
                    
                elif mode == "render_layer":
                    if "defaultRenderLayer" not in ui.SELECTED_NODE:
                        self.renderLayerLabel.setText("Render Layer: " + str(ui.SELECTED_NODE).replace("[","").replace("]",""))
                        self.jobWidget.properties["render_layer"] = ui.SELECTED_NODE
                    else:
                        self.renderLayerLabel.setText("Render Layer: - Default -")
                        self.jobWidget.properties["render_layer"] = ""
                        
                elif mode =="mesh":
                    self.jobWidget.properties["object_to_export"] = ui.SELECTED_NODE
                    self.meshLabel.setText("Mesh: " + str(ui.SELECTED_NODE).replace("[","").replace("]",""))
        else:
            LogW.writeLog(self.output, ErrorStr.ERROR + "File not foundn enter a valid File Path.")
            
        self.jobWidget.updateWarning()
        if self.jobWidget.WARNING:
            self.renderCurrentBtn.setEnabled(False)
        else:
            self.renderCurrentBtn.setEnabled(True)
            
    def updateUIstate(self):
        
        if self.jobWidget.properties["job_type"] == "Render Scene":
            self._enablePickRendering()
            self._enablePickMesh(False)
            self.overrideOuputPath.setText("Override Output folder:")
            
        elif self.jobWidget.properties["job_type"] == "Export obj":
            self._enablePickRendering(False)
            self._enablePickMesh()
            self.overrideOuputPath.setText("Output path to .obj:")
            
        if self.jobWidget.WARNING:
            self.renderCurrentBtn.setEnabled(False)
        else:
            self.renderCurrentBtn.setEnabled(True)
            
    def _enablePickRendering(self, enable=True):
        
        self.overrideCamera.setEnabled(enable)
        self.cameraLabel.setEnabled(enable)
        self.pickCamera.setEnabled(enable)
        self.overrideLayer.setEnabled(enable)
        self.pickRenderLayer.setEnabled(enable)
        self.renderLayerLabel.setEnabled(enable)
        
    def _enablePickMesh(self, enable=True):
        
        self.pickMesh.setEnabled(enable)
        self.meshLabel.setEnabled(enable)
        
    def _changeJobType(self):
        
        if self.mayaAction.currentIndex() == 0:
            self.jobWidget.properties["job_type"] = "Render Scene"
            self.outputPath.setText(self.jobWidget.properties["render_outputpath"])
        elif self.mayaAction.currentIndex() == 1:
            self.jobWidget.properties["job_type"] = "Export obj"
            self.outputPath.setText(self.jobWidget.properties["obj_outputpath"])
            
        self.updateUIstate()
        self.jobWidget.updateWarning()
        if self.jobWidget.WARNING:
            self.renderCurrentBtn.setEnabled(False)
        else:
            self.renderCurrentBtn.setEnabled(True)
        
    def _changeOverrideCamera(self):
        
        self.jobWidget.properties["override_camera"] = self.overrideCamera.isChecked()
        self.jobWidget.updateWarning()
        if self.jobWidget.WARNING:
            self.renderCurrentBtn.setEnabled(False)
        else:
            self.renderCurrentBtn.setEnabled(True)
            
    def _changeOverrideLayers(self):
        
        self.jobWidget.properties["override_render_layer"] = self.overrideLayer.isChecked()
        self.jobWidget.updateWarning()
        if self.jobWidget.WARNING:
            self.renderCurrentBtn.setEnabled(False)
        else:
            self.renderCurrentBtn.setEnabled(True)
            
    def _changeOverrideOutput(self):
        
        self.jobWidget.properties["override_output_path"] = self.overrideOuputPath.isChecked()
        self.jobWidget.updateWarning()
        if self.jobWidget.WARNING:
            self.renderCurrentBtn.setEnabled(False)
        else:
            self.renderCurrentBtn.setEnabled(True)
            
    def _pickOutputPath(self, mode):
        
        if mode == 0:
            p = QtGui.QFileDialog.getExistingDirectory(parent=None)
            if p:
                self.jobWidget.properties["render_outputpath"] = str(p)
                self.outputPath.setText(str(p))
                
        elif mode == 1:
            f = "Geometry"
            file_type = "*.obj"
            
            p = QtGui.QFileDialog.getSaveFileName(parent=None, filter = "{0} Files ({1})".format(f, file_type))
            if p:
                self.jobWidget.properties["obj_outputpath"] = str(p)
                self.outputPath.setText(str(p))
                
        self.jobWidget.updateWarning()
        if self.jobWidget.WARNING:
            self.renderCurrentBtn.setEnabled(False)
        else:
            self.renderCurrentBtn.setEnabled(True)
            
    def _changeOutputPath(self, output_path, mode):
        
        if mode == 0:
            self.jobWidget.properties["render_outputpath"] = output_path
        elif mode == 1:
            self.jobWidget.properties["obj_outputpath"] = output_path
            
        self.jobWidget.updateWarning()
        if self.jobWidget.WARNING:
            self.renderCurrentBtn.setEnabled(False)
        else:
            self.renderCurrentBtn.setEnabled(True)