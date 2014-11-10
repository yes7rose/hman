hman
====

hman Houdini MAya Nuke jobs management tool.
This tool allows the user to create stack of jobs and run them one after the other.
Jobs can be either Maya jobs ( rendering scene or exporting meshes in .obj )
Houdini jobs ( rendering nodes: cop, rop_output, mantra )
Nuke Jobs ( write output from write node )
Python Jobs ( executes python file with given python interpreter )
Batch job ( Execute batch commands on win platform )

Hman doesn't use software custom python directly ( hython or maya.cmds etc. ) but generates scripts and run them
with proper interpreters. This means it can be used with all version of python 2.x, just be sure you have the 
right version of PyQt4 in the libs directoy.

More infos : http://guillaumejobst.blogspot.fr/p/hman.html
Created by Guillaume Jobst
Email: contact@guillaume-j.com
