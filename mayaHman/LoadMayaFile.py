import sys
import os
import time
import subprocess
import pickle

from IO_path import readInitPath

from PyQt4 import QtGui


SCRIPT_PATH = os.path.dirname(os.path.dirname(__file__)) + "\\_pytmp"

def loadMayaFile(file_path, mode, UI_PROPERTIES):
    
    if file_path.endswith(".mb"):
        return _loadMB(file_path, mode)
    elif file_path.endswith(".ma"):
        return _loadMA(file_path, mode)
    else:
        print("Not a valid file")
        return None
    
    if UI_PROPERTIES["clean_py"]:
        cleanTmpMayaFile()
    
def _loadMA(file_path, mode):
    '''
        Load and read maya ascii file as text and extract
        Datas according to mode ('camera' or 'mesh')
    '''
    if not os.path.exists(file_path):
        return
    
    with open(file_path, 'r') as ma:
        
        data_read = ma.readlines()
    
    datasNode = []
    render_layers = []
    for d in data_read:
        
        # Fetch camera or mesh
        if d.startswith("createNode " + mode):
            datasNode.append(d.replace("\n", "").replace("-s ","").replace(";",""))
        
        # Fetch render layers
        elif d.startswith("createNode renderLayer "):
            render_layers.append(d.replace("\n", "").replace("-n", "").replace(";", "").replace('"','').replace("createNode renderLayer", "").replace(" ",""))
    
    outData = {}
    
    outCamData = {}
    for data in datasNode:
        outCamData[ data.split(" ")[5].replace('"','') ] =  data.split(" ")[3].replace('"','')
        
    outRenderLayerData = {}
    for data in render_layers:
        outRenderLayerData[data] = data
    
    outData["nodes"] = outCamData
    outData["render_layer"] = outRenderLayerData
    
    return outData

def _loadMB(file_path, mode):
    '''
        Load a mb file format with generated python script and mayapy
    '''
    mayapy = readInitPath()["MAYA_PATH"] + "\\bin\\mayapy.exe"
    
    _loadMBScript(file_path, mode)
    script = SCRIPT_PATH  + "\\tmpread_mb.py"
    
    p = subprocess.Popen([mayapy, script])
    p.wait()
    
    # Fetch dic data
    pickleData =SCRIPT_PATH + "\\tmpread_mb_{0}.out".format(mode)
    with open(pickleData, 'rb') as handle:
        mayaDatas = pickle.load(handle)
    
    outData = {}
    tmpNode = {}
    if mayaDatas[0]:
        for i in mayaDatas[0]:
            tmpNode[i] = i
    else:
        tmpNode["None"] = "None"
        
    tmpLayer = {}
    for i in mayaDatas[1]:
        tmpLayer[i] = i
        
    outData["nodes"] = tmpNode
    outData["render_layer"] = tmpLayer
    
    return outData

def _loadMBScript(file_path, mode):
    '''
        Generate python script to read data from (camera or mesh)
    '''
        
    with open(SCRIPT_PATH + "\\tmpread_mb.py", 'w') as py:
        py.write("import maya.standalone\n")
        py.write("import pickle\n")
        py.write("maya.standalone.initialize(name='python')\n")
        py.write("import maya.cmds as cmds\n")
        py.write("cmds.file('{0}', open=True)\n".format(file_path))
        py.write("dataNodes = cmds.ls(type='{0}')\n".format(mode))
        py.write("dataNodes = cmds.listRelatives(dataNodes, parent=True, fullPath=False)\n")
        py.write("renderLayers = cmds.ls(type='renderLayer')\n")
        py.write('with open("{0}" + "\\\\tmpread_mb_{1}.out", "wb") as f:\n'.format(SCRIPT_PATH, mode))
        py.write('    pickle.dump([dataNodes, renderLayers], f)')

def exportObjScript(objectList, outFile, mayaFile):
    
    with open(SCRIPT_PATH + "\\exportObjTmp.py", 'w') as py:
        py.write("import maya.standalone\n")
        py.write("maya.standalone.initialize(name='python')\n")
        py.write("import maya.cmds as cmds\n")
        py.write("cmds.file('{0}', open=True)\n".format(mayaFile))
        py.write("cmds.loadPlugin('objExport')\n")
        py.write("for obj in {0}:\n".format(objectList))
        py.write("   cmds.select(obj, add=True)\n")
        py.write("cmds.file('{0}', type='OBJexport', es=True)\n".format(outFile))
        
def cleanTmpMayaFile():
    '''
        Clean temp maya files .out and .py
    '''
    readScript = SCRIPT_PATH + "\\tmpread_mb.py"
    readDataCamera = SCRIPT_PATH + "\\tmpread_mb_camera.out"
    readDataMesh = SCRIPT_PATH + "\\tmpread_mb_mesh.out"
    exportObjTmp = SCRIPT_PATH + "\\exportObjTmp.py"
    mayaExportObjTmp = SCRIPT_PATH + "\\mayaExportObjTmp.bat"
    mayajobrendertmp = SCRIPT_PATH + "\\mayajobrendertmp.bat"
    
    if os.path.exists(readScript):
        os.remove(readScript)
        
    if os.path.exists(readDataCamera):
        os.remove(readDataCamera)
        
    if os.path.exists(readDataMesh):
        os.remove(readDataMesh)
        
    if os.path.exists(exportObjTmp):
        os.remove(exportObjTmp)
        
    if os.path.exists(mayaExportObjTmp):
        os.remove(mayaExportObjTmp)
        
    if os.path.exists(mayajobrendertmp):
        os.remove(mayajobrendertmp)

class PickMayaNode(QtGui.QDialog):
    
    def __init__(self, file_path, inTime, output, mode, UI_PROPERTIES, parent=None):
        QtGui.QDialog.__init__(self, parent=parent)
        
        self.output = output
        self.datas = loadMayaFile(file_path, mode, UI_PROPERTIES)
        
        if mode == "render_layer":
            self.nodes = self.datas["render_layer"]
        else:
            self.nodes = self.datas["nodes"]
        
        self.SELECTED_NODE = None
        
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setSpacing(10)
        
        self.headerLabel = QtGui.QLabel("Pick a {0}:".format(mode))
        if self.nodes:
            mainLayout.addWidget(self.headerLabel)
        self.writeNodesMenu = QtGui.QListWidget()
        
        if mode == 'mesh' or mode == "render_layer":
            self.writeNodesMenu.setSelectionMode(QtGui.QListView.MultiSelection)
        
        if not self.nodes:
            self.noNodesLabel = QtGui.QLabel("No {0} found in file:\n".format(mode) + file_path)
            mainLayout.addWidget(self.noNodesLabel)
        else:
            self.writeNodesMenu.addItems(self.nodes.keys())
            mainLayout.addWidget(self.writeNodesMenu)
            
        btnsLayout = QtGui.QHBoxLayout()
        btnsLayout.setSpacing(10)
        
        self.OK = QtGui.QPushButton("Ok")
        self.OK.clicked.connect(self.confirm)
        self.CANCEL = QtGui.QPushButton("Cancel")
        self.CANCEL.clicked.connect(self.cancel)
        
        btnsLayout.addWidget(self.OK)
        if self.nodes:
            btnsLayout.addWidget(self.CANCEL)
        
        mainLayout.addItem(btnsLayout)
        
        self.setLayout(mainLayout)
        
    def confirm(self):
        if self.writeNodesMenu.currentItem():
            self.SELECTED_NODE = [str(n.text()) for n in self.writeNodesMenu.selectedItems() if n]
        self.close()
    
    def cancel(self):
        self.SELECTED_NODE = None
        self.close()