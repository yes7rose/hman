import os
import subprocess
import random

from PyQt4 import QtGui
from PyQt4 import QtCore

from utils.JobToolTips import jobToolTips

from IO_path import readInitPath

from houdiniHman.CreateHoudiniRenderScript import createHoudiniRenderScript
from houdiniHman.CreateHoudiniRenderScript import deleteHoudiniRenderScript

from nukeHman.CreateNukeRenderScript import createNukeRenderScript
from nukeHman.CreateNukeRenderScript import deleteNukeRenderScript

from mayaHman.LoadMayaFile import exportObjScript
from mayaHman.LoadMayaFile import cleanTmpMayaFile


iconsPath = os.path.dirname(os.path.dirname(__file__)) + "\\icons\\"
SCRIPT_PATH = os.path.dirname(os.path.dirname(__file__)) + "\\_pytmp"

DARK_STYLE = os.path.dirname(os.path.dirname(__file__)) + "\\dark.style"

class JobWidget(QtGui.QWidget):
    
    def __init__(self, jobType, propertyDock, job_id, flowView, output, UI_PROPERTIES, parent=None):

        QtGui.QWidget.__init__(self, parent=parent)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        
        self.isBypassed = False
        
        self.output = output
        
        # Output info
        self.ERROR = ""
        self.OUT = ""
        self.WARNING = True
        
        # Common job properties
        self.HEIGHT = 120
        self.WIDTH = 350
        self.setFixedWidth(self.WIDTH+5)
        self.setFixedHeight(self.HEIGHT+5)
        
        # UI 
        self.propertyDock = propertyDock
        self.flowView = flowView
        
        self.iconName = "maya.png"
        
        # ID
        self.ID = job_id
        
        # per jobs attrib
        self.jobType = jobType
        self.file_filter = "*"
        self.properties = {"file_path":"",
                           "start_frame":0,
                           "end_frame":100,
                           "description":"",
                           "output_path":"",
                           "override_frames":False,
                           "override_output_path":False,
                           "isbypassed":False}
        
        self.setToolTip(jobToolTips(self.jobType, self.ID, self.properties["file_path"], self.properties["description"]))
        
        # set current color and outline
        self.BG_COLOR = Colors.DEFAULT_BG
        self.DEFAULT_BG_COLOR = Colors.DEFAULT_BG
        self.OUTLINE_COLOR = Colors.DEFAULT_OUT
        self.OUTLINE_SIZE = 1.0
        
        # Default warning
        self.warningTxt = "Warning:\n"
        
        ##########
        # Layout #
        ##########

        # Common buttons
        buttonLayout = QtGui.QHBoxLayout()
        
        commonButtonLayout = QtGui.QHBoxLayout()
        commonButtonLayout.setSpacing(1)
        commonButtonLayout.setAlignment(QtCore.Qt.AlignRight)
        upDownLayout = QtGui.QHBoxLayout()
        upDownLayout.setSpacing(10)
        upDownLayout.setAlignment(QtCore.Qt.AlignLeft)
        
        # Warning icon
        self.warning = QtGui.QLabel("")
        self.warning.setFixedSize(QtCore.QSize(30,30))
        warningPix = QtGui.QPixmap(iconsPath + "warning.png")
        warningPix = warningPix.scaled(18, 18)
        self.warning.setPixmap(warningPix)
        self.warning.setToolTip(self.warningTxt)
        
        self.bypass = QtGui.QPushButton("")
        self.bypass.setIcon(QtGui.QIcon(iconsPath+"green_light.png"))
        self.bypass.setFlat(True)
        self.bypass.setObjectName("flatbutton")
        self.bypass.setChecked(False)
        self.bypass.clicked.connect(self.bypassWidget)
        self.bypass.setToolTip("Disable this node")
        
        self.deleteJob = QtGui.QPushButton("")
        self.deleteJob.setFixedSize(32,32)
        self.deleteJob.setFlat(True)
        self.deleteJob.setIcon(QtGui.QIcon(iconsPath + "remove.png"))
        self.deleteJob.setObjectName("flatbutton")
        self.deleteJob.setIconSize(QtCore.QSize(20,20))
        self.deleteJob.clicked.connect(self.removeJob)
        self.deleteJob.setToolTip("Remove this job")
        
        commonButtonLayout.addWidget(self.warning)
        commonButtonLayout.addWidget(self.bypass)
        commonButtonLayout.addWidget(self.deleteJob)
        
        self.upBtn = QtGui.QPushButton("")
        self.upBtn.setFlat(True)
        self.upBtn.setObjectName("flatbutton")
        self.upBtn.setIcon(QtGui.QIcon(iconsPath + "upArrow.png"))
        self.upBtn.setIconSize(QtCore.QSize(22,22))
        self.upBtn.setFixedSize(24,24)
        self.upBtn.setToolTip("Move job up")
        self.upBtn.clicked.connect(lambda: self.moveWidget(self.ID, "up"))
        
        
        self.downBtn = QtGui.QPushButton("")
        self.downBtn.setFixedSize(24,24)
        self.downBtn.setFlat(True)
        self.downBtn.setObjectName("flatbutton")
        self.downBtn.setIcon(QtGui.QIcon(iconsPath + "downArrow.png"))
        self.downBtn.setIconSize(QtCore.QSize(22,22))
        self.downBtn.setToolTip("Move job down")
        self.downBtn.clicked.connect(lambda: self.moveWidget(self.ID, "down"))
        
        upDownLayout.addWidget(self.upBtn)
        upDownLayout.addWidget(self.downBtn)
        
        # Icon 
        self.iconLabel = QtGui.QLabel("")
        self.iconLabel.setFixedWidth(32)
        self.iconLabel.setFixedHeight(32)
        
        pixMap = QtGui.QPixmap(iconsPath + self.jobType.lower() + ".png")
        pixMap = pixMap.scaled(32, 32,)
        self.iconLabel.setPixmap(pixMap)

        buttonLayout.addItem(upDownLayout)
        buttonLayout.addWidget(self.iconLabel)
        buttonLayout.addItem(commonButtonLayout)
        
        # Jobs Type
        self.jobTypeLabel = QtGui.QLabel("Job type: " + self.jobType)
        self.jobTypeLabel.setAlignment(QtCore.Qt.AlignHCenter)
        
        # Header
        header = QtGui.QVBoxLayout()
        header.setSpacing(15)
        header.addWidget(self.jobTypeLabel)
        header.addItem(buttonLayout)
        
        # Path Label
        self.pathLabel = QtGui.QLabel("Path: None")
        
        # Render button
        renderButtonLay = QtGui.QHBoxLayout()
        renderButtonLay.setAlignment(QtCore.Qt.AlignHCenter)
        self.renderJob = QtGui.QPushButton("Render")
        self.renderJob.setObjectName("widgetFlatButton")
        self.renderJob.setFixedWidth(100)
        self.renderJob.setFixedHeight(25)
        renderButtonLay.addWidget(self.renderJob)
        self.renderJob.clicked.connect(self.render)
        
        # Set layout
        mainLayout.addItem(header)
        mainLayout.addWidget(self.pathLabel)
        mainLayout.addItem(renderButtonLay)

        self.setLayout(mainLayout)
    
    # Draw BG methode
    def paintEvent(self, event):
 
        qp = QtGui.QPainter()
        qp.begin(self)
        self._drawBG(qp)
        qp.setRenderHint(QtGui.QPainter.Antialiasing)
        qp.end()
         
    def _drawBG(self, qp):
        
        pen = QtGui.QPen(self.OUTLINE_COLOR, self.OUTLINE_SIZE)
        qp.setPen(pen)
        
        brush = QtGui.QBrush(self.BG_COLOR)
        
        qp.setBrush(brush)
        qp.drawRoundedRect(0,0, self.WIDTH, self.HEIGHT, 10.0, 10.0)
        
    def selectWidget(self):
        
        for n in self.flowView.listJobs():
            n.unselectWidget()
        self.OUTLINE_COLOR = Colors.OUTLINE_SELECTED
        self.repaint()
        self.setFocus()
        
    def unselectWidget(self):
        
        self.OUTLINE_COLOR = Colors.DEFAULT_OUT
        self.repaint()
    
    def updatePathInfo(self, file_path):
        '''
            Update the path label on widget.
        '''
        if len(file_path) > 50:
            out = file_path[0:20] + " [...] " + file_path[-20:]
        else:
            out = file_path
        
        self.pathLabel.setText("File Path: " + str(out))
        self.setToolTip(jobToolTips(self.jobType, self.ID, self.properties["file_path"], self.properties["description"]))
    
    def bypassWidget(self):
        
        if self.isBypassed:
            self.properties["isbypassed"] = False
            self.isBypassed = False
            self.BG_COLOR = self.DEFAULT_BG_COLOR
            self.repaint()
            self.renderJob.setEnabled(True)
            self.iconLabel.setEnabled(True)
            self.warning.setEnabled(True)
            self.bypass.setIcon(QtGui.QIcon(iconsPath+"green_light.png"))
            self.bypass.setToolTip("Disable this node")
            
        else:
            self.properties["isbypassed"] = True
            self.isBypassed = True
            self.BG_COLOR = Colors.BYPASS_BG
            self.repaint()
            self.renderJob.setEnabled(False)
            self.iconLabel.setEnabled(False)
            self.warning.setEnabled(False)
            self.bypass.setIcon(QtGui.QIcon(iconsPath+"yellow_light.png"))
            self.bypass.setToolTip("Enable this node")
            
    def moveWidget(self, ID, button):
        '''
            move a widget up or down
        '''
        
        # Update job list
        jobList = list(self.flowView.jobs)
        
        if button == "up":
            if ID == 0:
                return
            
            else:
                curID = jobList[ID]
                upID = jobList[ID - 1]
                
                jobList[ID] = upID
                jobList[ ID - 1] = curID
                
        else:
            if button == "down":
                if ID + 1 == len(self.flowView.jobs):
                    return
                else:
                    curID = jobList[ID]
                    upID = jobList[ID + 1]
                    
                    jobList[ID] = upID
                    jobList[ ID + 1] = curID
            
        
        self.flowView.updateFlowview(jobList)
        
    def render(self):
        '''
            Launch the flowview rendering from this widget
        '''
        self.flowView.renderFlow(self.ID)
        
    def renderCurrent(self):
        '''
            Render current widget node, launched from UI
        '''
        self.flowView.renderCurrentJob(self.ID)        
    
    def _renderCurrent(self):
        '''
            Render current widget node, launched from Worker Thread
        '''
        return
    
    def removeJob(self):
        '''
            Remove this widget
        '''
        self.flowView.removeJob(self.ID)
        
    def updateWarning(self, override_hide_warning=False):
        
        if override_hide_warning:
            self.warning.setVisible(False)
            self.WARNING = False
            return
        
        if not self.properties["file_path"] or not os.path.exists(self.properties["file_path"]):
            self.warningTxt += "    - " + self.jobType.lower() + " file not selected or not valid."
            self.warning.setToolTip(self.warningTxt)
            self.warning.setVisible(True)
            self.WARNING = True
        else:
            self.warning.setVisible(False)
            self.WARNING = False
            
        self.flowView.updateFlowviewHeader()
            
    def catchProcessInfo(self, p):
        '''
            Catch info or error from batch process
        '''
        
        error = p.stderr
        out = p.stdout

        if error:
            errorOut = error.readlines()
            if len(errorOut) > 0:
                msg = "Job ID: " + str(self.ID) + ", type: '" + str(self.jobType) + "', error: "
                for line in errorOut:
                    msg += str(line.rstrip())
                
                self.ERROR = msg
        
        if out:
            if not error:
                if out.readlines():
                    msg = "Job ID: " + str(self.ID) + ", type: '" + str(self.jobType) + "': "
                    for line in out.readlines():
                        msg += line.rstrip()
                    
                    self.OUT = msg
        
    def mousePressEvent(self, event):
        '''
            Click on the widget
        '''
        self.selectWidget()
        self.propertyDock.showProperties(self)
        
    def keyPressEvent(self, e):
        
        if e.key() == QtCore.Qt.Key_Delete:
            self.removeJob()
            
        elif e.key() == QtCore.Qt.Key_H:
            self.bypassWidget()

class MayaJobWidget(JobWidget):
    
    def __init__(self, propertyDock, job_id, flowView, output, UI_PROPERTIES, parent=None):
        JobWidget.__init__(self, "Maya", propertyDock, job_id, flowView, output, UI_PROPERTIES, parent=parent)
        
        self.jobType = JobTypes.MAYA
        self.iconName = "maya.png"
        self.file_filter = "*.mb *.ma"
        
        self.BG_COLOR = Colors.MAYA_JOB_BG
        self.DEFAULT_BG_COLOR = self.BG_COLOR
        
        self.properties["job_type"] = "Render Scene"
        self.properties["override_camera"] = False
        self.properties["camera"] = ""
        self.properties["override_render_layer"] = False
        self.properties["render_layer"] = ""
        self.properties["object_to_export"] = []
        self.properties["render_outputpath"] = ""
        self.properties["obj_outputpath"] = ""
        
        self.UI_PROPERTIES = UI_PROPERTIES
        
        self.updateWarning()
        
    def updateWarning(self, override_hide_warning=False):
        
        self.warningTxt = ""
        self.WARNING = False
        
        if override_hide_warning:
            self.warning.setVisible(False)
            self.WARNING = False
            return
        
        if not self.properties["file_path"] or not os.path.exists(self.properties["file_path"]):
            self.warningTxt += "    - " + self.jobType.lower() + " file not selected or not valid.\n"
            self.WARNING = True
        
        if self.properties["job_type"] == "Render Scene":
            if self.properties["override_output_path"] and not os.path.exists(self.properties["render_outputpath"]):
                self.warningTxt += "    - Render output path not valid.\n"
                self.WARNING = True
        
        if self.properties["job_type"] == "Export obj":
            if self.properties["obj_outputpath"] == "" or not os.path.exists(self.properties["obj_outputpath"]):
                self.warningTxt += "    - Object output path empty or not valid.\n"
                self.WARNING = True
                
            if not self.properties["object_to_export"]:
                self.warningTxt += "    - Mesh to export not selected\n"
            
        if self.WARNING:
            self.warning.setVisible(True)
            self.warning.setToolTip(self.warningTxt)
            self.WARNING = True
            
        else:
            self.warning.setVisible(False)
            
        self.flowView.updateFlowviewHeader()
        
    def _renderCurrent(self):
        
        # Render a scene
        if self.properties["job_type"] == "Render Scene":
            
            MAYA_RENDER = '"'+ readInitPath()["MAYA_PATH"] + "\\bin\\render.exe" + '" '
            
            allFlags = [MAYA_RENDER]
            
            if self.properties["override_frames"]:
                MAYA_RENDER += "-s " + str(float(self.properties["start_frame"]))
                MAYA_RENDER += " -e " + str(float(self.properties["end_frame"]))
                MAYA_RENDER += " -b 1.0"
                MAYA_RENDER += " -fnc 3"
                MAYA_RENDER += " -pad " + str(len(str(self.properties["end_frame"]))) + " "
                
            if self.properties["override_camera"] and self.properties["camera"]:
                MAYA_RENDER += '-cam "' + str(self.properties["camera"]) + '" '
                
            if self.properties["override_render_layer"] and self.properties["render_layer"]:
                MAYA_RENDER += '-rl "' + str(self.properties["render_layer"]).replace(",","").replace("[","").replace("]","").replace("'","") + '" '
                
            if self.properties["override_output_path"] and self.properties["render_outputpath"]:
                MAYA_RENDER += "-rd " + '"' + self.properties["render_outputpath"].replace("/","\\") + '"'
                
            MAYA_RENDER += ' "' + self.properties["file_path"].replace("/","\\") + '"'
            
            with open(SCRIPT_PATH + "\\mayajobrendertmp.bat", 'w') as bat:
                bat.write(MAYA_RENDER)
            
            os.system(SCRIPT_PATH + "\\mayajobrendertmp.bat")
        
        # Export obj job
        elif self.properties["job_type"] == "Export obj":
            
            # Generate python script
            exportObjScript(self.properties["object_to_export"],
                            self.properties["obj_outputpath"],
                            self.properties["file_path"])
            
            MAYAPY = '"' + readInitPath()["MAYA_PATH"] + "\\bin\\mayapy.exe" + '"'
            
            with open(SCRIPT_PATH + "\\mayaExportObjTmp.bat", 'w') as bat:
                bat.write(MAYAPY + ' "' + SCRIPT_PATH + "\\exportObjTmp.py" +'"')
            
            os.system(SCRIPT_PATH + "\\mayaExportObjTmp.bat")
        
        if self.UI_PROPERTIES["clean_py"]:
            cleanTmpMayaFile()
            
            
class HoudiniJobWidget(JobWidget):
    
    def __init__(self, propertyDock, job_id, flowView, output, UI_PROPERTIES, parent=None):
        JobWidget.__init__(self, "Houdini", propertyDock, job_id, flowView, output, UI_PROPERTIES, parent=parent)
        
        self.jobType = JobTypes.HOUDINI
        self.file_filter = "*.hip *.hiplc *.hipnc"
        
        self.BG_COLOR = Colors.HOUDINI_JOB_BG
        self.DEFAULT_BG_COLOR = self.BG_COLOR
        
        self.UI_PROPERTIES = UI_PROPERTIES
        
        # Houdini properties default values
        self.properties["render_node"] = ""
        self.properties["render_node_type"] = None
        self.properties["show_pixel_sample"] = False
        self.properties["show_output_path"] = False
        self.properties["pixel_sample"] = [0,0]
        
        self.updateWarning()
        
        
        
    # Default warning message
    def updateWarning(self):
        
        errorFound = False
        self.warningTxt = "Warning:\n"
        
        if not self.properties["file_path"]:
            self.warningTxt += "    - " + self.jobType.lower() + " file not selected or not valid.\n"
            self.warning.setToolTip(self.warningTxt)
            errorFound = True
            self.WARNING = True
            
        if not self.properties["render_node"]:
            self.warningTxt += "    - Render node not selected."
            self.warning.setToolTip(self.warningTxt)
            errorFound = True
            self.WARNING = True
        
        if not errorFound:
            self.warning.setVisible(False)
            self.WARNING = False
            
        self.flowView.updateFlowviewHeader()
    
    def _renderCurrent(self):
        '''
            Render current job launched from Worker Thread
        '''
        
        session_key = random.randint(1,100)
        
        createHoudiniRenderScript(self.ID, session_key, self.properties)
        
        scriptPath = SCRIPT_PATH + "\\renderHoudiniScript_s{0}_id{1}.py".format(session_key, self.ID)
        hythonPath = readInitPath()["HOUDINI_PATH"] + "\\bin\\hython.exe"
        
        p = subprocess.Popen([hythonPath, scriptPath])
        p.wait()
        self.catchProcessInfo(p)
        if self.UI_PROPERTIES["clean_py"]:
            deleteHoudiniRenderScript(self.ID, session_key)
            
        
class NukeJobWidget(JobWidget):
    
    def __init__(self, propertyDock, job_id, flowView, output, UI_PROPERTIES, parent=None):
        JobWidget.__init__(self, "Nuke", propertyDock, job_id, flowView, output, UI_PROPERTIES, parent=parent)
        
        self.jobType = JobTypes.NUKE
        self.file_filter = "*.nk"
        
        self.BG_COLOR = Colors.NUKE_JOB_BG
        self.DEFAULT_BG_COLOR = self.BG_COLOR
        
        self.UI_PROPERTIES = UI_PROPERTIES
        
        self.properties["render_node"] = ""
        
        self.updateWarning()
        
    # Default warning message
    def updateWarning(self):
        
        errorFound = False
        self.warningTxt = "Warning:\n"
        
        if not self.properties["file_path"]:
            self.warningTxt += "    - " + self.jobType.lower() + " file not selected or not valid.\n"
            self.warning.setToolTip(self.warningTxt)
            errorFound = True
            self.WARNING = True
            
        if not self.properties["render_node"]:
            self.warningTxt += "    - Render node not selected."
            self.warning.setToolTip(self.warningTxt)
            errorFound = True
            self.WARNING = True
        
        if not errorFound:
            self.warning.setVisible(False)
            self.WARNING = False
            
        self.flowView.updateFlowviewHeader()
            
    def _renderCurrent(self):
        
        session_key = random.randint(1,100)
        createNukeRenderScript(self.ID, session_key, self.properties)
        
        scriptPath = SCRIPT_PATH + "\\renderNukeScript_s{0}_id{1}.py".format(session_key, self.ID)
        nukePythonPath = readInitPath()["NUKE_PATH"] + "\\python.exe"

        p = subprocess.Popen([nukePythonPath, scriptPath], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        p.wait()
        self.catchProcessInfo(p)
        
        if self.UI_PROPERTIES["clean_py"]:
            deleteNukeRenderScript(self.ID, session_key)   
        
class PythonJobWidget(JobWidget):
    
    def __init__(self, propertyDock, job_id, flowView, output, parent=None):
        JobWidget.__init__(self, "Python", propertyDock, job_id, flowView, output, UI_PROPERTIES=None, parent=parent)
        self.jobType = JobTypes.PYTHON
        self.file_filter = "*.py"
        self.BG_COLOR = Colors.PYTHON_JOB_BG
        self.DEFAULT_BG_COLOR = self.BG_COLOR
        
        self.properties["interpreter"] = ""
        
        self.updateWarning()
    
    def updateWarning(self):
        
        errorFound = False
        self.warningTxt = "Warning:\n"
        
        if not self.properties["interpreter"] or not os.path.exists(self.properties["interpreter"]):
            self.warningTxt += "    - " + self.jobType.lower() + " interpreter not selected or not valid.\n"
            self.warning.setToolTip(self.warningTxt)
            errorFound = True
            self.WARNING = True
            
        if not self.properties["file_path"] or not os.path.exists(self.properties["file_path"]):
            self.warningTxt += "    - Python file not selected or not valid."
            self.warning.setToolTip(self.warningTxt)
            errorFound = True
            self.WARNING = True
        
        if not errorFound:
            self.warning.setVisible(False)
            self.WARNING = False
        else:
            self.warning.setVisible(True)
            self.WARNING = True
            
        self.flowView.updateFlowviewHeader()
        
    def _renderCurrent(self):
        p = subprocess.call([self.properties["interpreter"], self.properties["file_path"]])
        p.wait()
        self.catchProcessInfo(p)
        
        
class BatchJobWidget(JobWidget):
    
    def __init__(self, propertyDock, job_id, flowView, output, parent=None):
        JobWidget.__init__(self, "Batch", propertyDock, job_id, flowView, output, UI_PROPERTIES=None, parent=parent)
        
        self.jobType = JobTypes.BATCH
        self.file_filter = "*.bat"
        
        self.BG_COLOR = Colors.BATCH_JOB_BG
        self.DEFAULT_BG_COLOR = self.BG_COLOR
        
        # Batch related properties
        self.properties["use_command"] = False
        self.properties["wait"] = False
        self.properties["command"] = ""
        self.properties["args"] = ["","","","","","",""]
        
        self.updateWarning()
        
    def updateWarning(self):
        
        errorFound = False
        self.warningTxt = "Warning:\n"
        
        if not self.properties["use_command"] and not os.path.exists(self.properties["file_path"]):
            self.warningTxt += "    - " + self.jobType.lower() + " file not selected or not valid.\n"
            self.warning.setToolTip(self.warningTxt)
            errorFound = True
            self.WARNING = True
            
        if self.properties["use_command"] and not self.properties["command"]:
            self.warningTxt += "    - Batch command empty or not valid."
            self.warning.setToolTip(self.warningTxt)
            errorFound = True
            self.WARNING = True
            
        if not errorFound:
            self.warning.setVisible(False)
            self.WARNING = False
        else:
            self.warning.setVisible(True)
            self.WARNING = True
            
        self.flowView.updateFlowviewHeader()
            
    def _renderCurrent(self):
        
        if self.properties["use_command"]:
        
            cmdList = [self.properties["command"]]
            cmdList += [n for n in self.properties["args"] if n]
            
        else:
            
            cmdList = [self.properties["file_path"]]
        p = subprocess.Popen(cmdList, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        if self.properties["wait"]:
            p.wait()
            
        self.catchProcessInfo(p)
        
        
        
class SoftPropertiesWidget(QtGui.QWidget):
    '''
        Utilities class used to check if a software properties
        widget is displayed in the properties dock.
    '''
    def __init__(self):
        QtGui.QWidget.__init__(self)
        
        self.renderCurrentLabel = "Render Current Job"
        
        self.renderCurrentBtn = QtGui.QPushButton(self.renderCurrentLabel)
        
        self.FILE_PATH_IS_VALID = False
        
    def updateCurrentJobBtnVisibility(self, enable=True):
        
        self.renderCurrentBtn.setEnabled(enable)
        
class Colors():
    
    DEFAULT_BG = QtGui.QColor(110,110,130)
    DEFAULT_OUT = QtGui.QColor(10,10,10)
    
    MAYA_JOB_BG = QtGui.QColor(180,50,50)
    HOUDINI_JOB_BG = QtGui.QColor(190,80,55)
    NUKE_JOB_BG = QtGui.QColor(165,150,40)
    PYTHON_JOB_BG = QtGui.QColor(40,60,130)
    BATCH_JOB_BG = QtGui.QColor(60,60,80)
    
    BYPASS_BG = QtGui.QColor(55,55,55)
    
    OUTLINE_SELECTED = QtGui.QColor(255,255,255)
    ERROR = (200,0,0)
    GREEN = (0,200,0)
    BLUE = (0,0,200)

class JobTypes():
    
    MAYA = "Maya"
    HOUDINI = "Houdini"
    NUKE = "Nuke"
    PYTHON = "Python"
    BATCH = "Batch"
    NONE = None
    