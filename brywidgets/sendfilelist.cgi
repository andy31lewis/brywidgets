#! /usr/bin/python
# -*- coding: utf-8 -*-
import os
import cgi
import cgitb; cgitb.enable()

form = cgi.FieldStorage()
folder = "../"+form.getfirst("folder")
dirlist = os.listdir(folder)
dirlist.sort()
folderlist = [d for d in dirlist if os.path.isdir(folder+"/"+d)]
filelist = [d for d in dirlist if not os.path.isdir(folder+"/"+d)]

print "Content-Type: text/html\n\n"
print chr(30).join([chr(31).join(folderlist), chr(31).join(filelist)])
