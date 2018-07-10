#! /usr/bin/python
# -*- coding: utf-8 -*-
import os.path
import cgi
import cgitb; cgitb.enable()

form = cgi.FieldStorage()
filepath = "../"+form.getfirst("filepath")
filetosave = form.getfirst("filetosave")
g = open(filepath, "w")
g.write(filetosave)
g.close()

size = os.path.getsize(filepath)   
print "Content-Type: text/html\n\n"
if size == 0:
    print "NO"
else:
    print "OK"
