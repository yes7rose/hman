import os
import subprocess

def readInitPath(fromMainUI = False):
    '''
        Check if path in path.inf are valid.
    '''
     
    outPath = {"MAYA_PATH":False,
               "HOUDINI_PATH":False,
               "NUKE_PATH":False}
    
    if fromMainUI:
        INF_PATH = os.path.dirname(os.path.dirname(__file__)) + os.sep + "path.inf"
    else:
        INF_PATH = os.path.dirname(__file__) + os.sep + "path.inf"
        
        
    if not os.path.exists(INF_PATH):
        with open(INF_PATH, "w") as inf:
            inf.writelines(["MAYA_PATH=\n", "HOUDINI_PATH=\n", "NUKE_PATH=\n"])
            
    else:
        with open(INF_PATH, "r") as inf:
            datas = inf.readlines()
        if len(datas) < 3:
            with open(INF_PATH, "w") as inf:
                inf.writelines(["MAYA_PATH=\n", "HOUDINI_PATH=\n", "NUKE_PATH=\n"])
     
    try:
        
        with open(INF_PATH,'r') as f:
            lines = f.readlines()
 
            maya_path = lines[0].split("=")[1].replace("\n", "")
            if os.path.exists(maya_path) and "Maya" in maya_path:
                outPath["MAYA_PATH"] = maya_path
             
            houdini_path = lines[1].split("=")[1].replace("\n", "")
            if os.path.exists(houdini_path) and "Houdini" in houdini_path:
                outPath["HOUDINI_PATH"] = houdini_path
                 
            nuke_path = lines[2].split("=")[1].replace("\n", "")   
            if os.path.exists(nuke_path) and "Nuke" in nuke_path:
                outPath["NUKE_PATH"] = nuke_path
             
    except IOError as e:
        print(str(e))
         
    return outPath


def writeInitPath(outPath):
    '''
        Write path in path.inf
    '''
    
    tmp_readLines = []
    try:
        
        # Read lines from the inf
        with open("path.inf",'r') as f:
            tmp_readLines = f.readlines()
        
        # Clean readline
        readlines = []
        for line in tmp_readLines:
            readlines.append(line.split("=")[1].replace("\n",""))
        
        # Write new lines (replace if found in readlines, keep otherwise).
        with open("path.inf",'w') as f:
            
            if not readlines[0]:
                if outPath["MAYA_PATH"]:
                    f.write("MAYA=" + outPath["MAYA_PATH"] + "\n")
                else:
                    f.write("MAYA=\n")
            else:
                if outPath["MAYA_PATH"]:
                    f.write("MAYA=" + outPath["MAYA_PATH"] + "\n")
                else:
                    f.write(readlines[0])
                    
            if not readlines[1]:
                if outPath["HOUDINI_PATH"]:
                    f.write("HOUDINI=" + outPath["HOUDINI_PATH"] + "\n")
                else:
                    f.write("HOUDINI=\n")
            else:
                if outPath["HOUDINI_PATH"]:
                    f.write("HOUDINI=" + outPath["HOUDINI_PATH"] + "\n")
                else:
                    f.write(readlines[1])
                    
            if not readlines[2]:
                if outPath["NUKE_PATH"]:
                    f.write("NUKE=" + outPath["NUKE_PATH"] + "\n")
                else:
                    f.write("NUKE=\n")
            else:
                if outPath["NUKE_PATH"]:
                    f.write("NUKE=" + outPath["NUKE_PATH"] + "\n")
                else:
                    f.write(readlines[2])
             
    except IOError as e:
        print(str(e))