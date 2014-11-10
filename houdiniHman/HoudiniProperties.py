import os
import time

from PyQt4 import QtGui
from PyQt4 import QtCore

from main.JobWidget import SoftPropertiesWidget
from houdiniHman.LoadHip import PickHouNode

from utils import LogW
from utils.ErrorStr import ErrorStr

iconsPath = os.path.dirname(os.path.dirname(__file__)) + "\\icons\\"

class HoudiniProperties(SoftPropertiesWidget):
    
    COMP_OUT_FILES = '*.pic *.pic.Z *.pic.gz *.rat *.dsm *.picnc *.piclc *.rgb *.rgba *.sgi *.tif *.tif3 *.tif16 *.tif32 *.tiff *.yuv *.pix *.als *.cin *.kdk *.jpg *.jpeg *.exr *.png *.si *.tga *.vst *.vtg *.rla *.rla16 *.rlb *.rlb16 *.bmp *.hdr *.ptx *.ptex *.ies *.qtl *.tx *.tex *.env'
    GEO_OUT_FILES = '*'
    RENDER_OUT_FILES = '*'
    
    def __init__(self, jobWidget, output, UI_PROPERTIES):
        SoftPropertiesWidget.__init__(self)
        
        self.UI_PROPERTIES = UI_PROPERTIES
        
        self.houdiniPropertiesLayout = QtGui.QVBoxLayout()
        self.houdiniPropertiesLayout.setAlignment(QtCore.Qt.AlignTop)
        
        self.jobWidget = jobWidget
        self.output = output

        self._initHoudiniProperties()
        self.setLayout(self.houdiniPropertiesLayout)

    def _initHoudiniProperties(self):
        
        self.outputPath_Widgets = []
        self.pixelSampleWidgets = []
        
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
        
        # Output path
        outputPathLayout = QtGui.QHBoxLayout()
        outputPathLayout.setSpacing(10)
        
        self.outputPathLabel = QtGui.QLabel("Output path:")
        self.outputPath = QtGui.QLineEdit(self.jobWidget.properties["output_path"])
        self.outputPath.returnPressed.connect(lambda: self._changeOutputPath(self.outputPath.text()))
        self.pickOutputPath = QtGui.QPushButton("")
        self.pickOutputPath.setFlat(True)
        self.pickOutputPath.setIcon(QtGui.QIcon(iconsPath + "pickfolder.png"))
        self.pickOutputPath.setFixedSize(QtCore.QSize(25,25))
        self.pickOutputPath.setIconSize(QtCore.QSize(20,20))
        self.pickOutputPath.clicked.connect(self._pickOutputPath)
        
        self.outputPath_Widgets.append(self.outputPathLabel)
        self.outputPath_Widgets.append(self.outputPath)
        self.outputPath_Widgets.append(self.pickOutputPath)
        
        outputPathLayout.addWidget(self.outputPathLabel)
        outputPathLayout.addWidget(self.outputPath)
        outputPathLayout.addWidget(self.pickOutputPath)
        
        # Pixel filter
        pixelFilterLayout = QtGui.QHBoxLayout()
        pixelFilterLayout.setSpacing(10)
        
        self.pixFilterLabel = QtGui.QLabel("Pixel Sample:")
        self.pixFilterX = QtGui.QSpinBox()
        self.pixFilterX.valueChanged.connect(lambda: self._changePixSample(self.pixFilterX.value(), "X"))
        self.pixFilterX.setValue(self.jobWidget.properties["pixel_sample"][0])
        self.pixFilterY = QtGui.QSpinBox()
        self.pixFilterY.valueChanged.connect(lambda: self._changePixSample(self.pixFilterY.value(), "Y"))
        self.pixFilterY.setValue(self.jobWidget.properties["pixel_sample"][1])
        
        self.pixelSampleWidgets.append(self.pixFilterLabel)
        self.pixelSampleWidgets.append(self.pixFilterX)
        self.pixelSampleWidgets.append(self.pixFilterY)
        
        pixelFilterLayout.addWidget(self.pixFilterLabel)
        pixelFilterLayout.addWidget(self.pixFilterX)
        pixelFilterLayout.addWidget(self.pixFilterY)
        
        # Render current job button
        self.renderCurrentBtn.setText("Render Current Hip File")
        self.renderCurrentBtn.setObjectName("pushbutton")
        self.renderCurrentBtn.clicked.connect(self.jobWidget.renderCurrent)
        if self.jobWidget.properties["file_path"]:
            self.renderCurrentBtn.setEnabled(True)
        else:
            self.renderCurrentBtn.setEnabled(False)
        
        # Construc layout
        self.houdiniPropertiesLayout.addItem(renderNodeLay)
        self.houdiniPropertiesLayout.addItem(outputPathLayout)
        self.houdiniPropertiesLayout.addItem(pixelFilterLayout)
        self.houdiniPropertiesLayout.addWidget(self.renderCurrentBtn)
        
        # Hide properties which needs to have render node set
        self.enablePixelSample(self.jobWidget.properties["show_pixel_sample"])
        self.enableOutputPath(self.jobWidget.properties["show_output_path"])
    
    def enablePixelSample(self, enable=True):
        for n in self.pixelSampleWidgets:
            n.setEnabled(enable)
            
    def enableOutputPath(self, enable=True):
        for n in self.outputPath_Widgets:
            n.setEnabled(enable)
            
    def _changePixSample(self, value, coord):
        
        if coord == "X":
            self.jobWidget.properties["pixel_sample"][0] = value
        else:
            self.jobWidget.properties["pixel_sample"][1] = value
                    
    def _pickOutputPath(self):
        
        node_type = self.jobWidget.properties["render_node_type"]
        
        if node_type == "rop_comp":
            f = "Images"
            file_type = self.COMP_OUT_FILES
        elif node_type == "rop_geometry":
            f = "Geometry"
            file_type = self.GEO_OUT_FILES
        elif node_type == "ifd":
            f = "Images"
            file_type = self.RENDER_OUT_FILES
            
        else:
            f = "All"
            file_type = "*"
            
        p = QtGui.QFileDialog.getSaveFileName(parent=None, filter = "{0} Files ({1})".format(f, file_type))
        if p:
            self.outputPath.setText(str(p))
            self.jobWidget.properties["output_path"] = str(p)
        
    def _changeOutputPath(self, output_path):
        
        self.jobWidget.properties["output_path"] = output_path
        
    def _pickRenderNode(self):
        
        filePath = self.jobWidget.properties["file_path"]
        if os.path.exists(filePath):
            
            inTime = time.time()
            
            ui = PickHouNode(filePath, inTime, self.output, self.UI_PROPERTIES)
            ui.exec_()
            
            if ui.SELECTED_NODE:
                self.renderTypeLabel.setText("Render Node:  " + ui.SELECTED_NODE)
                self.jobWidget.properties["render_node"] = ui.SELECTED_NODE
                self.jobWidget.properties["render_node_type"] = ui.SELECTED_NODE_TYPE
                self.enableOutputPath(False)
                self.renderCurrentBtn.setEnabled(True)
                
                if ui.SELECTED_NODE_TYPE == "ifd":
                    self.jobWidget.properties["show_pixel_sample"] = True
                    
                    # Read pixel sample from file
                    self.pixFilterX.setValue(ui.SELECTED_PIXEL_SAMPLE[0])
                    self.pixFilterY.setValue(ui.SELECTED_PIXEL_SAMPLE[1])
                      
                    self.jobWidget.properties["pixel_sample"] = [ui.SELECTED_PIXEL_SAMPLE[0], ui.SELECTED_PIXEL_SAMPLE[1]]
                     
                    self.enablePixelSample(True)
                    
                else:
                    self.enablePixelSample(False)
                    self.jobWidget.properties["show_pixel_sample"] = False
                    
                self.enableOutputPath(True)
                self.jobWidget.properties["show_output_path"] = True
                
            else:
                self.enableOutputPath(False)
                self.enablePixelSample(False)
                self.jobWidget.properties["show_pixel_sample"] = False
                self.jobWidget.properties["show_output_path"] = False
                self.renderCurrentBtn.setEnabled(False)

            self.jobWidget.updateWarning()
        
        else:
            LogW.writeLog(self.output, ErrorStr.ERROR + "File not foundn enter a valid File Path.")