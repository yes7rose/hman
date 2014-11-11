import sys
import os

if os.path.dirname(__file__) + "\\libs" not in sys.path:
    sys.path.append(os.path.dirname(__file__) + "\\libs")

from PyQt4 import QtGui

from main.MainUi import HmanMainUi
from main.PathPicker import PathPicker
from IO_path import readInitPath

'''
    Run this script to run hman.
    Open the UI to setup path if needed.
'''

def main(parent=None):
    
    # Check if folder _pytmp exists
    pymp = os.path.dirname(__file__) + "\\_pytmp"
    if not os.path.exists(pymp):
        os.mkdir(pymp)
    
    outDic = readInitPath()
    pathResult = [outDic[k] for k in outDic.keys()]
    
    app = QtGui.QApplication(sys.argv)
    
    # If no path found, launch ui
    if not any(pathResult):
        
        pathPicker = PathPicker(parent)
        pathPicker.exec_()
        
        if pathPicker.CANCEL:
            return
        
    ui = HmanMainUi(parent)
    ui.show()
        
    app.exec_()

if __name__ == "__main__":
    main()