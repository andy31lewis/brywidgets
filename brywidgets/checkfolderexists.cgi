#! /usr/bin/python
# -*- coding: utf-8 -*-
import os
import cgi
import cgitb; cgitb.enable()

form = cgi.FieldStorage()
username = form.getfirst("username")
if os.path.isdir("../users/"+username):
    response = "True"
else:
    response = "False"

print "Content-Type: text/html\n\n"
print response
