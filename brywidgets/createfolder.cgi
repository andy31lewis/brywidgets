#! /usr/bin/python
# -*- coding: utf-8 -*-
import os
import cgi
import cgitb; cgitb.enable()

form = cgi.FieldStorage()
username = form.getfirst("username")

os.mkdir("../users/"+username)

print "Content-Type: text/html\n\n"
print "OK"
