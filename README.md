hman
====

hman Houdini MAya Nuke jobs management tool.<br>
This tool allows the user to create stack of jobs and run them one after the other.<br>
Jobs can be: <br>
    - Maya jobs ( rendering scene or exporting meshes in .obj )<br>
    - Houdini jobs ( rendering nodes: cop, rop_output, mantra )<br>
    - Nuke Jobs ( write output from write node )<br>
    - Python Jobs ( executes python file with given python interpreter )<br>
    - Batch job ( Execute batch commands on win platform )<br>
<br>
Simply run hman.py to launch the tool ( be sure you have python installed and in your PATH )<br>
<br>
Hman doesn't use software custom python directly ( hython or maya.cmds etc. ) but generates scripts and run them
with proper interpreters. This means it can be used with all version of python 2.x, just be sure you have the 
right version of PyQt4 in the libs directoy.<br>
<br>
More infos : http://guillaumejobst.blogspot.fr/p/hman.html<br>
Created by Guillaume Jobst<br>
Email: contact@guillaume-j.com<br>
