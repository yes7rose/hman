import os

SCRIPT_PATH = os.path.dirname(os.path.dirname(__file__)) + "\\_pytmp"

def createHoudiniRenderScript(ID, session_key, properties):
    '''
        Generate houdini rendering script
    '''
    if not os.path.exists(SCRIPT_PATH): os.mkdir(SCRIPT_PATH)
    
    with open(SCRIPT_PATH + "\\renderHoudiniScript_s{0}_id{1}.py".format(session_key, ID), 'w') as py:
        py.write("import hou\n")
        py.write("try:\n")
        py.write("    hou.hipFile.load('"+properties["file_path"]+"')\n")
        py.write("    n = hou.node('"+properties["render_node"]+"')\n")
        
        # Override output path
        if properties["output_path"]:
            pathParm = ""
            if properties["render_node_type"] == "rop_geometry":
                pathParm = "sopoutput"
            elif properties["render_node_type"] == "rop_comp":
                pathParm = "copoutput"
            elif properties["render_node_type"] == "ifd":
                pathParm = "vm_picture"
            
            outPath = properties["output_path"]
            if properties["override_frames"]:
                tmp = properties["output_path"].split(".")
                outPath = tmp[0] + ".$F" + str(len(str(properties["end_frame"]))) + "." + tmp[1]
                
            py.write("    n.parm('" + pathParm + "').set('" + outPath + "')\n")
            
        # Override frame range
        if properties["override_frames"]:
            py.write("    n.parm('trange').set(1)\n")
            py.write("    n.parm('f1').set("+str(properties["start_frame"])+")\n")
            py.write("    n.parm('f2').set("+str(properties["end_frame"])+")\n")

                
        py.write("    n.render()\n")
        py.write("except Exception as e:\n")
        py.write("    print('ERROR rendering houdini script')\n")
        py.write("    print(str(e))")
        
def deleteHoudiniRenderScript(ID, session_key):
    '''
        Delete houdini rendering script
    '''
    if not os.path.exists(SCRIPT_PATH): os.mkdir(SCRIPT_PATH)
    
    scriptPath = SCRIPT_PATH + "\\renderHoudiniScript_s{0}_id{1}.py".format(session_key, ID)
    
    if os.path.exists(scriptPath):
        os.remove(scriptPath)