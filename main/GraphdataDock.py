import os
import pickle
from PyQt4 import QtGui
from PyQt4 import QtCore

MATPLOTLIB_IMPORTED = False

try:
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    MATPLOTLIB_IMPORTED = True
    
except ImportError:
    pass
    
ICONPATH = os.path.dirname(os.path.dirname(__file__))
TMP_GRAPHDATA = os.path.dirname(os.path.dirname(__file__)) + "\\_pytmp\\graphdata.tmp"

class GraphdataDock(QtGui.QDockWidget):
    
    def __init__(self, parent=None):
        
        QtGui.QDockWidget.__init__(self, parent=parent)
        
        self.setFeatures(QtGui.QDockWidget.DockWidgetMovable|
                         QtGui.QDockWidget.DockWidgetFloatable)
        
        self.setMinimumWidth(400)
        self.setWindowTitle("Graph Data")
        
        self.graphDataWidget = QtGui.QWidget()
        self.graphDataLayout = QtGui.QVBoxLayout()
        self.graphDataLayout.setAlignment(QtCore.Qt.AlignTop)
        self.graphDataLayout.setSpacing(10)
        
        self.MATPLOTLIB_IMPORTED = MATPLOTLIB_IMPORTED
        
        # Check if matplotlib is found
        if MATPLOTLIB_IMPORTED:
        
            self.optionsLayout = QtGui.QHBoxLayout()
            self.optionsLayout.setSpacing(10)
            
            self.enableGraphDataCheck = QtGui.QCheckBox("Enable Graph Data")
            self.enableGraphDataCheck.setChecked(False)
            self.enableGraphDataCheck.clicked.connect(lambda: self.enableGraphData(False,False))
            self.optionsLayout.addWidget(self.enableGraphDataCheck)
            
            self.refreshGraph = QtGui.QPushButton("Refresh Graph")
            self.refreshGraph.setObjectName("pushbutton")
            self.refreshGraph.clicked.connect(lambda: self.refreshGraphData(external=True))
            self.optionsLayout.addWidget(self.refreshGraph)
            
            self.graphDataLayout.addItem(self.optionsLayout)
            
            # Graphdata layout
            self.figureLayout = QtGui.QVBoxLayout()
            self.figureWidget = QtGui.QWidget()
            
            self.figure = plt.figure()
            self.canvas = FigureCanvas(self.figure)
            
            self.figureLayout.addWidget(self.canvas)
            self.figureWidget.setLayout(self.figureLayout)
            
            self.graphDataLayout.addWidget(self.figureWidget)
            
            # Info layout (min / max)
            self.bottomLayout = QtGui.QHBoxLayout()
            self.bottomLayout.setMargin(5)
            self.bottomLayout.setSpacing(10)
            
            self.infoLayout = QtGui.QVBoxLayout()
            self.infoLayout.setMargin(5)
            self.infoLayout.setSpacing(5)
            
            self.maxTimeLabel = QtGui.QLabel("Max rendering time: -")
            self.minTimeLabel = QtGui.QLabel("Min rendering time: -")
            
            self.infoLayout.addWidget(self.maxTimeLabel)
            self.infoLayout.addWidget(self.minTimeLabel)
            
            self.bottomLayout.addItem(self.infoLayout)
            
            self.saveBtn = QtGui.QPushButton("")
            self.saveBtn.setFlat(True)
            self.saveBtn.setFixedSize(QtCore.QSize(40,40))
            self.saveBtn.setIcon(QtGui.QIcon(ICONPATH + "\\icons\\save.png"))
            self.saveBtn.setIconSize(QtCore.QSize(32,32))
            self.saveBtn.clicked.connect(self.saveGraphToPng)
            self.bottomLayout.addWidget(self.saveBtn)
            
            self.graphDataLayout.addItem(self.bottomLayout)
            self.graphDataWidget.setLayout(self.graphDataLayout)

        else:
            
            warningLayout = QtGui.QHBoxLayout()
            warningLayout.setSpacing(20)
            
            warningPix = QtGui.QPixmap(ICONPATH + "\\icons\\warning.png")
            warningLbl = QtGui.QLabel()
            warningLbl.setFixedSize(QtCore.QSize(32,32))
            warningLbl.setPixmap(warningPix)
            
            warningLayout.addWidget(warningLbl)
            
            matplotlibNotImportedLay = QtGui.QVBoxLayout()
            matplotlibNotImportedLay.setMargin(20)
            matplotlibNotImportedLay.setAlignment(QtCore.Qt.AlignTop)
            
            warningLabel = QtGui.QLabel("Graph Data not available.\nmatplotlib module can not be imported.\nCheck you matplotlib version in the ../libs folder.")
            warningLayout.addWidget(warningLabel)
            
            matplotlibNotImportedLay.addItem(warningLayout)
            
            self.graphDataWidget.setLayout(matplotlibNotImportedLay)
            
        self.setWidget(self.graphDataWidget)
        
        if MATPLOTLIB_IMPORTED:
            self.enableGraphData()
        
    def enableGraphData(self, override=False, overrideValue=False):
        
        if override:
            toggle = overrideValue
        else:
            toggle = self.enableGraphDataCheck.isChecked()
            
        self.figureWidget.setVisible(toggle)
        self.maxTimeLabel.setVisible(toggle)
        self.minTimeLabel.setVisible(toggle)
        self.refreshGraph.setVisible(toggle)
        self.saveBtn.setVisible(toggle)
        
        if toggle:
            self.refreshGraphData()
            
        else:
            self.setMinimumHeight(10)
        
    def refreshGraphData(self, datas=None, external=False):
        
        if external:
            if os.path.exists(TMP_GRAPHDATA):
                datas = None
                with open(TMP_GRAPHDATA, 'rb') as handle:
                    datas = pickle.load(handle)
                    
            else:
                datas = [[0,1,2], [0,0,0]]
        
        
        if datas:
            
            self.graph = self.figure.add_subplot(111)
            self.graph.hold(False)
            plt.subplots_adjust(top= 0.9, bottom = 0.15)
            
            self.graph.plot(datas[0], datas[1], 'o-')
            self.graph.axis([0, int(max(datas[0])), 0, int(max(datas[1])+(max(datas[1])*0.1))+1])
            self.graph.set_xticks(datas[0])
            self.graph.set_xlabel("Job number")
            self.graph.set_ylabel("Rendering time (seconds)")
    
            self.canvas.draw()
            
            # Min / Max labels update
            maxTime = max(datas[1])
            maxIndex = datas[1].index(maxTime)
            self.maxTimeLabel.setText("Max rendering time: {0:.2f} seconds, job number: {1}".format(maxTime, maxIndex))
            
            minTime = min(datas[1])
            minIndex = datas[1].index(minTime)
            self.minTimeLabel.setText("Min rendering time: {0:.2f} seconds, job number: {1}".format(minTime, minIndex))
            
            # Resize UI
            self.setMinimumHeight(415)
            
    def saveGraphToPng(self):
        
        p = QtGui.QFileDialog.getSaveFileName(parent=None, filter = ".png image files (*.png)")
        print p
        if not p:
            return
        self.figure.savefig(str(p))
        