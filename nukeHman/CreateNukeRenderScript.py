import os

SCRIPT_PATH = os.path.dirname(os.path.dirname(__file__)) + "\\_pytmp"

def createNukeRenderScript(ID, session_key, properties):
    '''
        Generate a python script for the nuke job rendering.
    '''
    
    with open(SCRIPT_PATH + "\\renderNukeScript_s{0}_id{1}.py".format(session_key, ID), 'w') as py:
        
        py.write("import nuke\n")
        py.write("nuke.scriptOpen('{0}')\n".format(properties["file_path"]))
        py.write("n = nuke.toNode('{0}')\n".format(properties["render_node"]))
        
        # Change output path
        if properties["output_path"]:
            py.write("n['file'].setValue('{0}')\n".format(properties["output_path"]))
        
        if not properties["override_frames"]:
            properties["end_frame"] = 0
            properties["start_frame"] = 0
            
        sharpPattern = '#'* len(str(properties["end_frame"]))
        
        py.write("if not '#' in n['file'].value():\n")
        py.write("    tmp = n['file'].value().split('.')\n")
        py.write("    p = '.'.join(tmp[0:-1] + ['{0}'] + [tmp[-1]])\n".format(sharpPattern))
        py.write("    n['file'].setValue(p)\n")
            
        py.write("if n['file'].value():\n")
        py.write("    nuke.execute('{0}',{1},{2}, 1)\n".format(properties["render_node"], properties["start_frame"], properties["end_frame"]))
        py.write("else:\n")
        py.write("    print('No output path set for node -{0}-, rendering skiped.')\n".format(properties["render_node"]))
        py.write("nuke.scriptClose()")
        

def deleteNukeRenderScript(ID, session_key):
    '''
        Delete Nuke render script after rendering process.
    '''
    scriptPath = SCRIPT_PATH + "\\renderNukeScript_s{0}_id{1}.py".format(session_key, ID)
    
    if os.path.exists(scriptPath):
        os.remove(scriptPath)