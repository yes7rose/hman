from PyQt4 import QtGui
from PyQt4 import QtCore

class GraphdataDock(QtGui.QDockWidget):
    
    def __init__(self, parent=None):
        
        QtGui.QDockWidget.__init__(self, parent=parent)
        
        self.setMinimumWidth(400)
        self.setWindowTitle("Graph Data")
        
        self.setFeatures(QtGui.QDockWidget.DockWidgetMovable|
                         QtGui.QDockWidget.DockWidgetFloatable)