import os

from IO_path import readInitPath

from PyQt4 import QtGui
from PyQt4 import QtCore

from utils import LogW
from utils.ErrorStr import ErrorStr

DARK_STYLE = os.path.dirname(os.path.dirname(__file__)) + "\\dark.style"
ICON_PATH = os.path.dirname(os.path.dirname(__file__)) + "\\icons"
        
def loadNukeScript(nuke_script):
    '''
        Read a nuke script and fetch all write node.
        This does not use nuke's python.
    '''
    
    NUKE_PATH = readInitPath()["NUKE_PATH"]
    
    if NUKE_PATH:
        if os.path.exists(nuke_script):
            
            datas = []
            outNodeTmp = []
            
            with open(nuke_script, 'r') as nk:
                datas = nk.readlines()

            for i in range(len(datas)):
                
                if datas[i].endswith("{\n"):
                    tmp = []
                    
                    tmp.append(datas[i].replace("{\n","").replace(" ",""))
                    
                    k = 1
                    while not datas[i+k].endswith("}\n"):
                        tmp.append(datas[i+k])
                        k+=1
                        
                    outNodeTmp.append(tmp)  
            
            outWriteNodes = []
            for n in outNodeTmp:
                if n[0] == "Write":
                    for k in n:
                        if k.replace(" ", "").startswith("name"):
                            outWriteNodes.append(k.split("name")[1].replace(" ", "").replace("\n",""))

    return outWriteNodes
        

class PickNukeNode(QtGui.QDialog):
    
    def __init__(self, nuke_script, inTime, output, parent=None):
        QtGui.QDialog.__init__(self, parent=parent)
        
        self.output = output
        self.nodes = loadNukeScript(nuke_script)
        with open(DARK_STYLE,"r") as style:
            self.setStyleSheet(style.read())
            
        self.setWindowTitle("Pick a nuke write node")
        self.setWindowIcon(QtGui.QIcon(ICON_PATH + "\\nuke.png"))
        
        self.SELECTED_NODE = None
        
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setSpacing(10)
        
        self.headerLabel = QtGui.QLabel("Pick a write node:")
        mainLayout.addWidget(self.headerLabel)
        self.writeNodesMenu = QtGui.QListWidget()
        
        if not self.nodes:
            self.noNodesLabel = QtGui.QLabel("No Write nodes found in file:\n"+nuke_script)
            mainLayout.addWidget(self.noNodesLabel)
        else:
            self.writeNodesMenu.addItems(self.nodes)
            mainLayout.addWidget(self.writeNodesMenu)
            
        btnsLayout = QtGui.QHBoxLayout()
        btnsLayout.setSpacing(10)
        
        self.OK = QtGui.QPushButton("Ok")
        self.OK.clicked.connect(self.confirm)
        self.OK.setObjectName("pushbutton")
        self.CANCEL = QtGui.QPushButton("Cancel")
        self.CANCEL.clicked.connect(self.cancel)
        self.CANCEL.setObjectName("pushbutton")
        
        btnsLayout.addWidget(self.OK)
        btnsLayout.addWidget(self.CANCEL)
        
        mainLayout.addItem(btnsLayout)
        
        self.setLayout(mainLayout)
        
    def confirm(self):
        self.SELECTED_NODE = self.writeNodesMenu.currentItem().text()
        self.close()
    
    def cancel(self):
        self.SELECTED_NODE = None
        self.close()