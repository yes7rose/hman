import urllib2
import os
from utils.LogW import writeLog
from utils.ErrorStr import ErrorStr

from PyQt4 import QtGui

DARK_STYLE = os.path.dirname(os.path.dirname(__file__)) + "\\dark.style"

def checkVersion(curVer, output):
    
    curVer = [ int(c) for c in curVer.split(".")]
    response = urllib2.urlopen('https://raw.githubusercontent.com/GJpy/hman/master/version')
    version = response.read().replace("\n", "")
    version = [ int(c) for c in version.split(".")]
    
    msg = ErrorStr.INFO + "New version available: {0}.{1}.{2} ".format(version[0], version[1], version[2])
    downloadLink = '<a href="https://github.com/GJpy/hman"><font color="yellow">Download hman latest version</font></a>'
    msg += downloadLink
    if curVer[0] < version[0]:
        writeLog(output, msg)
        return
    
    if curVer[1] < version[1]:
        writeLog(output, msg)
        return
    
    if curVer[2] < version[2]:
        writeLog(output, msg)
        output.insertHtml(downloadLink)
        return
    
    msg = ErrorStr.INFO + "hman already up to date."
    writeLog(output, msg)
    
def about(curVer):
    
    msg = "hman version {0}\n\n".format(curVer)
    msg += "Created by Guillaume Jobst\n"
    msg += "Web: www.guillaume-j.com\n"
    msg += "Email: contact@guillaume-j.com"
    
    ask = QtGui.QMessageBox(QtGui.QMessageBox.Information,"About", msg)
    ask.setWindowIcon(QtGui.QIcon(os.path.dirname(os.path.dirname(__file__)) + "\\icons\\hman_small.png"))
    pix = QtGui.QPixmap(os.path.dirname(os.path.dirname(__file__)) + "\\icons\\hman_logo.png")
    ask.setIconPixmap(pix)
    with open(DARK_STYLE, 'r') as style:
        ask.setStyleSheet(style.read())
        
    ask.addButton(QtGui.QMessageBox.Ok)
    ask.exec_()
    