from __future__ import absolute_import

import os
import time

from main.OutputDock import OutputDock

def writeLog(output, msg, writeout=True, printout=False):
    
    
    # Check output type, dock or output field
    if isinstance(output, OutputDock):
        output = output.output
    
    # Append to output
    if output:
        output.append(msg)
    
    # Write output txt
    if "<b>" in msg:
        msg = msg.replace("</b></font>", "")
        msg = msg.split("<b>")[1]
    
    if printout:
        print(msg)
    
    if writeout:
        outputLog = os.path.dirname(os.path.dirname(__file__)) + "\\hman_log.log"
        
        if not os.path.exists(outputLog):
            with open(outputLog, 'w') as log:
                log.write("******** Log created: {0} ********\n".format(time.ctime()))
                

        with open(outputLog, 'a') as log:
            log.write(time.ctime() + ": " + msg + "\n")