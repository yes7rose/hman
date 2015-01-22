import sys
import os

if os.path.dirname(__file__) + "\\libs" not in sys.path:
    sys.path.append(os.path.dirname(__file__) + "\\libs")

from PyQt4 import QtGui

from main.MainUi import HmanMainUi
from main.PathPicker import PathPicker
from IO_path import readInitPath
from utils import LogW

'''
    Init the path.inf.
    Read the path.inf, if no path are set
    open the UI to setup path.
    Path must be valid install path.
'''

def main(parent=None):
    
    # Check if folder _pytmp exists
    pymp = os.path.dirname(__file__) + "\\_pytmp"
    if not os.path.exists(pymp):
        os.mkdir(pymp)
    
    # Check hman version
    version = "version"
    with open(version, "r") as v:
        version = v.readline()
        msg = "INFO: "
        msg += "Launching hman version: " + version
        LogW.writeLog(None, msg, printout=True)
    
    outDic = readInitPath()
    pathResult = [outDic[k] for k in outDic.keys()]
    
    # Taskbar icon fix for windows 7
    try:
        import ctypes
        myappid = u'hman'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass
    
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(os.path.dirname(__file__)+"\\icons\\hman_small.png"))
    
    # If no path found, launch ui
    if not any(pathResult):
        
        pathPicker = PathPicker(version, parent)
        pathPicker.exec_()
        
        if pathPicker.CANCEL:
            return
        
    ui = HmanMainUi(version, parent)
    ui.show()
        
    app.exec_()

if __name__ == "__main__":
    main()