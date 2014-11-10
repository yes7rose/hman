import os

from PyQt4 import QtCore
from PyQt4 import QtGui

from IO_path import readInitPath
from IO_path import writeInitPath

class PathPicker(QtGui.QDialog):
    '''
        UI used to setup path for software.  
    '''
     
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent=parent)
        
        self.setWindowTitle("Hman path picker") 
        style = os.path.dirname(__file__) + "\\dark.style"
        style = style.replace("\\main","")
        
        with open( style ,"r") as style:
            self.setStyleSheet(style.read())
            
        self.mainUI = None
        self.CANCEL = False
         
        # Out value
        self.outSoftwarePath = {"MAYA_PATH":False,
                        "HOUDINI_PATH":False,
                        "NUKE_PATH":False}
         
        # Fetch path
        path = readInitPath()
        
        mayaPathDefault = ""
        if path["MAYA_PATH"]:
            mayaPathDefault = path["MAYA_PATH"]
            self.outSoftwarePath["MAYA_PATH"] = path["MAYA_PATH"]
             
        houdiniPathDefault = ""
        if path["HOUDINI_PATH"]:
            houdiniPathDefault = path["HOUDINI_PATH"]
            self.outSoftwarePath["HOUDINI_PATH"] = path["HOUDINI_PATH"]
             
        nukePathDefault = ""
        if path["NUKE_PATH"]:
            nukePathDefault = path["NUKE_PATH"]
            self.outSoftwarePath["NUKE_PATH"] = path["NUKE_PATH"]
        
        # Master layout
        masterLay = QtGui.QHBoxLayout()
        masterLay.setSpacing(10)
        
        # Construct UI
        self.setMinimumWidth(850)
        self.setWindowIcon(QtGui.QIcon(os.path.dirname(os.path.dirname(__file__)) + "\\icons\\hman_small.png"))
        cw = QtGui.QWidget()
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setSpacing(10)
        
        logo = QtGui.QLabel("")
        logo.setFixedSize(QtCore.QSize(150,180))
        pixIco = QtGui.QPixmap(os.path.dirname(os.path.dirname(__file__)) + "\\icons\\hman_logo.png")
        #pixIco = pixIco.scaled(100, 100)
        logo.setPixmap(pixIco)
        
        masterLay.addWidget(logo)
         
        self.mainLabel = QtGui.QLabel("Enter software path, keep blank of not installed:")
         
        # Maya info
        mayaLayout = QtGui.QHBoxLayout()
        mayaLayout.setSpacing(10)
        mayaLabel = QtGui.QLabel("Maya Path:")
        mayaLabel.setFixedWidth(70)
        self.mayaPath = QtGui.QLineEdit(mayaPathDefault)
        self.mayaPath.textChanged.connect(lambda: self.changeText(self.mayaPath, "MAYA"))
        self.mayaBtn = QtGui.QPushButton("Pick Maya Path")
        self.mayaBtn.setFixedWidth(100)
        self.mayaBtn.setObjectName("pushbutton")
        self.mayaBtn.clicked.connect(lambda: self.pickPath(self.mayaPath, "Maya"))
        mayaLayout.addWidget(mayaLabel)
        mayaLayout.addWidget(self.mayaPath)
        mayaLayout.addWidget(self.mayaBtn)
         
        # Houdini info
        houdiniLayout = QtGui.QHBoxLayout()
        houdiniLayout.setSpacing(10)
        houdiniLabel = QtGui.QLabel("Houdini Path:")
        houdiniLabel.setFixedWidth(70)
        self.houdiniPath = QtGui.QLineEdit(houdiniPathDefault)
        self.houdiniPath.textChanged.connect(lambda: self.changeText(self.houdiniPath, "HOUDINI"))
        self.houdiniBtn = QtGui.QPushButton("Pick Houdini Path")
        self.houdiniBtn.clicked.connect(lambda: self.pickPath(self.houdiniPath, "Houdini"))
        self.houdiniBtn.setFixedWidth(100)
        self.houdiniBtn.setObjectName("pushbutton")
        houdiniLayout.addWidget(houdiniLabel)
        houdiniLayout.addWidget(self.houdiniPath)
        houdiniLayout.addWidget(self.houdiniBtn)
         
        # nuke info
        nukeLayout = QtGui.QHBoxLayout()
        nukeLayout.setSpacing(10)
        nukeLabel = QtGui.QLabel("Nuke Path:")
        nukeLabel.setFixedWidth(70)
        self.nukePath = QtGui.QLineEdit(nukePathDefault)
        self.nukePath.textChanged.connect(lambda: self.changeText(self.nukePath, "NUKE"))
        self.nukeBtn = QtGui.QPushButton("Pick nuke Path")
        self.nukeBtn.setFixedWidth(100)
        self.nukeBtn.clicked.connect(lambda: self.pickPath(self.nukePath, "nuke"))
        self.nukeBtn.setObjectName("pushbutton")
        nukeLayout.addWidget(nukeLabel)
        nukeLayout.addWidget(self.nukePath)
        nukeLayout.addWidget(self.nukeBtn)
         
        # Ok / Cancel layout
        layoutBtn = QtGui.QHBoxLayout()
        layoutBtn.setSpacing(10)
        self.okBtn = QtGui.QPushButton("Ok")
        self.okBtn.setFixedWidth(120)
        self.okBtn.clicked.connect(self.ok)
        self.okBtn.setObjectName("pushbutton")
        self.cancelBtn = QtGui.QPushButton("Cancel")
        self.cancelBtn.setFixedWidth(120)
        self.cancelBtn.clicked.connect(self.cancel)
        self.cancelBtn.setObjectName("pushbutton")
        layoutBtn.addWidget(self.okBtn)
        layoutBtn.addWidget(self.cancelBtn)
        layoutBtn.setAlignment(QtCore.Qt.AlignRight)
         
        mainLayout.addWidget(self.mainLabel)
        mainLayout.addItem(mayaLayout)
        mainLayout.addItem(houdiniLayout)
        mainLayout.addItem(nukeLayout)
        mainLayout.addItem(layoutBtn)
        
        masterLay.addItem(mainLayout)
         
        cw.setLayout(masterLay)
        self.setLayout(masterLay)
        #self.setCentralWidget(cw)
         
     
    def pickPath(self, pathtype, softName):
        '''
            Pick a folder path ui.
        '''
        p = QtGui.QFileDialog.getExistingDirectory(self, "Select install {0} path".format(softName))
        if p:
            pathtype.setText(p)
            self.outSoftwarePath[softName.upper() + "_PATH"] = str(p)

    def changeText(self, lineEdit, name):
        '''
            Event when text change, for copy/past for instance.
        '''
        self.outSoftwarePath[name+"_PATH"] = str(lineEdit.text())


    def ok(self):
        '''
            Check if path are valid and close the ui if valid.
        '''
        
        pathResult = []
        for i in [self.mayaPath, self.houdiniPath, self.nukePath]:
            if os.path.exists(i.text()):
                pathResult.append(str(i.text()))
            else:
                pathResult.append(False)
        
        # Check if at least one path is valid
        if not any(pathResult):
            warnPop = QtGui.QMessageBox(self)
            warnPop.setWindowTitle("Path error")
            warnPop.setText("ERROR: At least one of the path must be valid.")
            warnPop.exec_()
            
        else:
            # Restart app
            self.close()
            writeInitPath(self.outSoftwarePath)
            
            if self.mainUI:
                newpath = readInitPath()
                if newpath["MAYA_PATH"]:
                    self.mainUI.addMayaJobMenu.setEnabled(True)
                    self.mainUI.addMayaJob.setEnabled(True)
                else:
                    self.mainUI.addMayaJobMenu.setEnabled(False)
                    self.mainUI.addMayaJob.setEnabled(False)
                    
                    
                if newpath["HOUDINI_PATH"]:
                    self.mainUI.addHoudiniJobMenu.setEnabled(True)
                    self.mainUI.addHoudiniJob.setEnabled(True)
                else:
                    self.mainUI.addHoudiniJobMenu.setEnabled(False)
                    self.mainUI.addHoudiniJob.setEnabled(False)
                    
                if newpath["NUKE_PATH"]:
                    self.mainUI.addNukeJobMenu.setEnabled(True)
                    self.mainUI.addNukeJob.setEnabled(True)
                else:
                    self.mainUI.addNukeJobMenu.setEnabled(False)
                    self.mainUI.addNukeJob.setEnabled(False)
         
    def cancel(self):
        '''
            Close the ui (cancelled).
        '''
        self.CANCEL = True
        self.close()
        
    def linkToMainUi(self, mainUi):
        self.mainUI = mainUi