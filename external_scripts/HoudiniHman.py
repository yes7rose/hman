import hou
import pickle
import os

# This script can be using in an Houdini shelf.
# Copy this file in $HOME/houdinixx.x/scripts/python
# Right click on a shelf and create a new tool
#
# Write these lines of python :
# import HoudiniHman
# HoudiniHman.makeFile()
#
# Then select a node ( "rop_comp", "rop_geometry", "ifd" )
# and click on that new tool, this allows you to create
# a job .hman file and can be read from hman directly.
#
# More infos: www.guillaume-j.com


def makeHmanFile():
    
    RENDER_NODES_TYPE = ["rop_comp", "rop_geometry", "ifd"]
    
    selNode = hou.selectedNodes()
    if not selNode:
        hou.ui.displayMessage("Nothing is selected.")
        return
    
    if selNode[0].type().name() not in RENDER_NODES_TYPE:
        msg = "Node can be only:\n"
        for n in RENDER_NODES_TYPE:
            msg += "   - " + n + "\n"
        hou.ui.displayMessage(msg)
        return
    
    node = selNode[0]
    nodeType = node.type().name()
    
    # Init properties
    properties = {}
    properties["isbypassed"] = False
    properties["show_pixel_sample"] = False
    properties["render_node"] = node.path()
    properties["pixel_sample"] = [4,4]
    properties["show_output_path"] = True
    
    if nodeType == "rop_geometry":
        pathParm = "sopoutput"
        
    elif nodeType == "rop_comp":
        pathParm = "copoutput"

    elif nodeType == "ifd":
        pathParm = "vm_picture"
        properties["show_pixel_sample"] = True
        properties["pixel_sample"] = [node.parm("vm_samplesx").eval(), node.parm("vm_samplesy").eval()]
    
    # Frame range
    if node.parm("trange").eval() != 0:
        properties["override_frames"] = False
    else:
        properties["override_frames"] = True
        properties["start_frame"] = node.parm("f1").eval()
        properties["end_frame"] = node.parm("f2").eval()
        

    properties["output_path"] = node.parm(pathParm).eval()
    properties["file_path"] = hou.hipFile.path()
    
    ask = hou.ui.selectFile(title="Save as", pattern="*.hman", chooser_mode=hou.fileChooserMode.Write)
    if not ask:
        return
    
    if os.path.exists(ask):
        warn = hou.ui.displayMessage("Warning, file already exists, replace it ?", buttons=["Yes", "No"])
        if warn == 1:
            return
    
    label = ask.replace(".hman", "").split("/")[-1]
    properties["description"] = label
    
    if not ask.endswith(".hman"):
        ask += ".hman"
        
    job = [label, {"ID":0, "jobtype":"Houdini", "properties":properties}]
    
    with open(ask, "wb") as f:
        pickle.dump(job, f)
    
    print(ask + " created.")
    