def jobToolTips(jobType, ID, file_path, descrition):
    
    msg = ""
    msg += "Job: " + jobType + "\n"
    msg += "ID: " + str(ID)  + "\n"
    msg += "-"*16 + "\n"
    msg += "File: " + file_path + "\n"
    msg += "-"*16 + "\n"
    msg += descrition
    
    return msg