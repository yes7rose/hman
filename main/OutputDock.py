from PyQt4 import QtGui

class OutputDock(QtGui.QDockWidget):
    
    def __init__(self, parent=None):
        
        QtGui.QDockWidget.__init__(self, parent=parent)
        
        self.setMinimumWidth(400)
        self.setWindowTitle("Output")
        
        self.setFeatures(QtGui.QDockWidget.DockWidgetMovable|
                         QtGui.QDockWidget.DockWidgetFloatable)
    
        dockLay = QtGui.QVBoxLayout()
        dockLay.setSpacing(10)
        dockWidget = QtGui.QWidget()
        
        self.output = QtGui.QTextEdit()
        self.output.setReadOnly(True)
        dockLay.addWidget(self.output)
        
        self.clearOutputBtn = QtGui.QPushButton("Clear Output")
        self.clearOutputBtn.setObjectName("pushbutton")
        self.clearOutputBtn.clicked.connect(self.output.clear)
        dockLay.addWidget(self.clearOutputBtn)
        
        dockWidget.setLayout(dockLay)
        self.setWidget(dockWidget)
        
    def writeLog(self, msg):
        '''
            Write a given message in the ouput view
        '''
        self.output.append(msg)