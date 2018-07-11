#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2018 Andy Lewis                                                   #
# --------------------------------------------------------------------------- #
# This program is part of Brywidgets                                          #
# Brywidgets isfree software; you can redistribute it and/or modify it        #
# under the terms of the GNU General Public License as published by the Free  #
# Software Foundation, either version 3 of the License, or (at your option)   #
# any later version.                                                          #
# This program is distributed in the hope that it will be useful, but WITHOUT #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       #
# FITNESS FOR A PARTICULAR PURPOSE.                                           #
# See the GNU General Public License for more details.                        #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <https://www.gnu.org/licenses/>.      #

from browser import document, window, ajax, alert, confirm
import browser.html as html
import os

#Utility function
def delete(element):
    element.parentNode.removeChild(element)
    del element

#Colour utility functions

def rgbtotuple(colour):
    return tuple([int(x) for x in colour[4:-1].split(",")])

def rgbtohwb(colour):
    if isinstance(colour, str): colour = rgbtotuple(colour)
    maxc = max(colour); maxi = colour.index(maxc)
    minc = min(colour); mini = colour.index(minc)
    whitealpha = minc/maxc
    blackalpha = 1 - maxc/255
   
    hue = (R, G, B) = (0, 255, 255) if maxc==minc else tuple(int(255*(c-minc)/(maxc-minc)) for c in colour)
    if R == 255: huenumber = G if B==0 else (256*5)+255-B
    elif G == 255: huenumber = (256*2)+B if R==0 else (256)+255-R
    elif B == 255: huenumber = (256*4)+R if G==0 else (256*3)+255-G
    
    return hue, huenumber, whitealpha, blackalpha

def hwbtorgb(hue, whitealpha, blackalpha):
    if isinstance(hue, int):
        i = hue % 256
        if hue < 256: (R, G, B) = (255, i, 0)
        elif 256 <= hue < 256*2: (R, G, B) = (255-i,255,0)
        elif 256*2 <= hue < 256*3: (R, G, B) = (0,255,i)
        elif 256*3 <= hue < 256*4: (R, G, B) = (0,255-i,255)
        elif 256*4 <= hue < 256*5: (R, G, B) = (i,0,255)
        elif 256*5 <= hue < 256*6: (R, G, B) = (255,0,255-i)
        hue = (R, G, B)
    colour = tuple(int((1-blackalpha)*(C*(1-whitealpha)+255*whitealpha)) for C in hue)
    return hue, colour

class Notebook(html.DIV):
    '''A tabbed set of pages; switch between pages by clicking on a tab.
    To use, create pages by subclassing (or instantiating) NotebookPage, then create the notebook.
    For example:
        page1 = NotebookPage("First page", "lightgreen")
        page2 = NotebookPage("Second page", "powderblue")
        nb = Notebook([page1, page2])'''

    def __init__(self, pagelist):
        html.DIV.__init__(self, "", Class="notebook")
        self.tabrow = html.DIV("", Class="notebooktabrow")
        self <= self.tabrow
        self.pagelist = []
        for page in pagelist: self.addpage(page)
    
    def addpage(self, page):
        self <= page
        tab = NotebookTab(self, len(self.pagelist), page.title)
        tab.style.backgroundColor = page.style.backgroundColor
        self.tabrow <= tab
        page.style.display="block" if len(self.pagelist)==0 else "none"
        self.pagelist.append(page)

class NotebookPage(html.DIV):
    '''A page in a notebook.  Create with a title (which appears on its tab), and a background colour.
    Optionally include content at creation time, or else add it later.'''
    def __init__(self, title, bgcolour, content=None, id=None):
        html.DIV.__init__(self, "", Class="notebookpage")
        self.style.backgroundColor = bgcolour
        self.title = title
        if id: self.id = id
        if content: self <= content

    def update(self):
        pass

class NotebookTab(html.DIV):
    '''Not intended to be created by end user.
    A tab at the top of a NotebookPage.'''
    def __init__(self, notebook, index, title):
        html.DIV.__init__(self, html.P(title), Class="notebooktab")
        self.notebook = notebook
        self.index = index
        self.bind("click", self.select)
        
    def select(self, event):
        for p in self.notebook.pagelist:
            p.style.display="none"
        self.notebook.pagelist[self.index].style.display="block"
        self.notebook.pagelist[self.index].update()

class DropDown(html.SELECT):
    '''Dropdown list of options.
    Required parameters:
    choices: a list of options
    onchange: function to be called when the user chooses a different option.  Takes the change event as argument.
    Optional parameters:
    initialchoice: index (counting from 0) of the inital choice.'''
    def __init__(self, choices, onchange, initialchoice=None, id=None):
        html.SELECT.__init__(self, "", Class="dropdown")
        self <= (html.OPTION(text) for text in choices)
        self.bind("change", onchange)
        if initialchoice: self.selectedIndex = initialchoice
        if id: self.id = id

class ListBox(html.SELECT):
    '''List of options (all shown unless the number to show is given in which case a scroll bar is used).
    Required parameters
    choices: a list of options
    onchange: function to be called when the user chooses a different option.  Takes the change event as argument.
    Optional parameters:
    size: number of choices to be displayed
    initialchoice: index (counting from 0) of the inital choice.'''
    def __init__(self, choices, onchange, size=None, initialchoice=None, id=None):
        html.SELECT.__init__(self, "", Class="listbox")
        self <= (html.OPTION(text) for text in choices)
        self.bind("change", onchange)
        self.size = size if size else len(choices)
        self.selectedIndex = initialchoice if initialchoice else -1
        if id: self.id = id

class InputBox(html.INPUT):
    '''Standard input box. Parameters:
    enterkeyaction: function to use if the Enter key is pressed. Takes the keypress event as argument.'''
    def __init__(self, enterkeyaction, id=None):
        html.INPUT.__init__(self, id=id)
        self.enterkeyaction = enterkeyaction
        self.bind("keypress", self.onKeypress)

    def onKeypress(self, event):
        if event.keyCode != 13: return
        self.enterkeyaction(event)

class Panel(html.DIV):
    '''Just a container with a default border. Optional parameters:
    items: contents of the panel
    title: heading at the top of the panel. '''
    def __init__(self, items=None, title=None, id=None):
        html.DIV.__init__(self, "", Class="panel")
        if id: self.id = id
        if title: self <= html.P(title, Class="paneltitle")
        if items: self <= items

class RowPanel(html.DIV):
    '''Container which lays its contents out in a row. Optional parameter:
    items: contents of the panel'''
    def __init__(self, items=None, id=None):
        html.DIV.__init__(self, "", Class="rowpanel")
        if items: self <= items
        if id: self.id = id

class ColumnPanel(html.DIV):
    '''Container which lays its contents out in a column. Optional parameter:
    items: contents of the panel'''
    def __init__(self, items=None, id=None):
        html.DIV.__init__(self, "", Class="columnpanel")
        if items: self <= items
        if id: self.id = id

class GridPanel(html.DIV):
    '''Container which lays its contents out in a specified grid.
    Required parameters:
    columns, rows: size of the grid
    Optional parameter:
    items: contents of the grid'''
    def __init__(self, columns, rows, items=None, id=None):
        html.DIV.__init__(self, "", Class="gridpanel")
        self.style.gridTemplateColumns = " ".join(["auto"]*columns)
        self.style.gridTemplateRows = " ".join(["auto"]*rows)
        if items: self <= items
        if id: self.id = id

class Button(html.BUTTON):
    '''Button with text (or blank).
    Required parameters:
    text: Text of the button (could be empty string)
    handler:  Function to be called on click. This function takes the click event as argument.
    Optional parameters:
    bgcolour: background colour
    tooltip: text displayed when hovering over the button'''
    def __init__(self, text, handler, bgcolour=None, tooltip=None, id=None):
        html.BUTTON.__init__(self, text, type="button", Class="button")
        self.bind("click", handler)
        if bgcolour: self.style.backgroundColor = bgcolour
        if tooltip: self.title = tooltip
        if id: self.id = id

class ImageButton(Button):
    '''Button with an image.
    Required parameters:
    icon: the path to its image
    handler:  Function to be called on click. This function takes the click event as argument.
    Optional parameters:
    bgcolour: background colour (default is light grey)
    tooltip: text displayed when hovering over the button'''
    def __init__(self, icon, handler, bgcolour=None, tooltip=None, id=None):
        Button.__init__(self, "", handler, bgcolour, tooltip, id)
        self <= html.IMG(src=icon)
        self.className = "imagebutton"

class ToggleButton(Button):
    '''Button which remains depressed when clicked, until clicked again or raised by other means.
    For parameters see Button.'''
    def __init__(self, text, handler, bgcolour=None, tooltip=None, id=None):
        Button.__init__(self, text, self.onClick, bgcolour, tooltip, id)
        self.className = "togglebutton"
        self._selected = None
        self.selected = False
        self.handler = handler
    
    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, selected):
        self._selected = selected
        if self.selected:
            self.style.borderTopColor = self.style.borderLeftColor = "grey"
            self.style.borderBottomColor = self.style.borderRightColor = "white"
        else:
           self.style.borderTopColor = self.style.borderLeftColor = "white"
           self.style.borderBottomColor = self.style.borderRightColor = "grey"

    def onClick(self, event):
        self.selected = False if self.selected else True
        self.handler(event)

class ToggleImageButton(ToggleButton):
    '''Button with an image.  The button remains depressed when clicked, until clicked again or raised by other means.
    For parameters see ImageButton.'''
    def __init__(self, icon, handler, bgcolour=None, tooltip=None, id=None):
        ToggleButton.__init__(self, "", handler, bgcolour, tooltip, id)
        self <= html.IMG(src=icon)
        self.className = "toggleimagebutton"

class ColourPickerButton(html.BUTTON):
    '''Button which opens a colour picker, and then takes on the colour which is selected.
    Required parameters:
    returnaction: function to be called after a colour is selected
    This function takes two arguments: the colour selected, and the id of the button (which could be None).
    Optional parameters:
    initialcolour: initial background colour of the button (in rgb() format).'''
    def __init__(self, returnaction, label="", initialcolour=None, id=None):
        html.BUTTON.__init__(self, label, type="button", title="Open Colour Picker...", Class="button")
        self.style.backgroundColor = initialcolour if initialcolour else "rgb(211, 211, 211)"
        if id: self.id = id
        self.bind("click", self.onClick)
        self.returnaction = returnaction
    
    def onClick(self, event):
        global colourpickerdialog
        if not colourpickerdialog: colourpickerdialog = ColourPickerDialog(self.onChange)
        colourpickerdialog.setupfromcolour(self.style.backgroundColor)
        colourpickerdialog.show()

    def onChange(self, colour):
        self.style.backgroundColor = colour
        self.returnaction(colour, self.id)
        
        
class ColourPickerImageButton(html.BUTTON):
    '''Button with an image, which opens a colour picker.
    Required parameters:
    icon: the path to its image
    returnaction: function to be called after a colour is selected. This function takes one argument: the colour selected.''' 
    def __init__(self, icon, returnaction, id=None):
        html.BUTTON.__init__(self, html.IMG(src=icon), type="button", title="Open Colour Picker...", Class="imagebutton")
        self.bind("click", self.onClick)
        self.returnaction = returnaction
        if id: self.id = id
    
    def onClick(self, event):
        global colourpickerdialog
        if not colourpickerdialog: colourpickerdialog = ColourPickerDialog(self.returnaction)
        colourpickerdialog.show()
    
class FileOpenButton(html.BUTTON):
    '''Button which opens a dialog for opening a file.
    Required parameters:
    returnaction: function to be called after the file is opened.
    This function takes two arguments: the contents and the name of the file which was opened.
    Optional parameters:
    extlist: a list of file extensions which should be displayed in the dialog.  If omitted, all files will be displayed.
    initialfolder: the path to the folder initially displayed in the dialog.''' 
    def __init__(self, returnaction, extlist=[], initialfolder=".", id=None):
        global fileopendialog
        html.BUTTON.__init__(self, html.IMG(src="brywidgets/Open.png"), type="button", title="Open File...", id=id, Class="imagebutton")
        self.bind("click", self.onClick)
        if not fileopendialog: fileopendialog = FileOpenDialog(returnaction, extlist)
        self.initialfolder = initialfolder
        if id: self.id = id
    
    def onClick(self, event):
        fileopendialog.open(self.initialfolder)
    
class FileSaveAsButton(html.BUTTON):
    '''Button which opens a dialog for saving a file.
    Required parameter:
    preparefile: function which returns a string with the contents of the file to be saved. This function takes no arguments.
    Optional parameters:
    returnaction: function to be called after the file is opened.
    This function takes two arguments: the contents and the name of the file which was opened.
    defaultextension: extension which will be appended to the filename given if not already present.
    initialfolder: the path to the folder initially displayed in the dialog.''' 
    def __init__(self, preparefile, returnaction=None, extlist=[], defaultextension=None, initialfolder=".", id=None):
        global filesavedialog
        html.BUTTON.__init__(self, html.IMG(src="brywidgets/SaveAs.png"), type="button", title="Save File As...", id=id, Class="imagebutton")
        self.bind("click", self.onClick)
        if not filesavedialog: filesavedialog = FileSaveDialog(returnaction, extlist, defaultextension)
        self.initialfolder = initialfolder
        self.preparefile = preparefile
        if id: self.id = id
    
    def onClick(self, event):
        filesavedialog.filetosave = self.preparefile()
        filesavedialog.open(self.initialfolder)
    
class FileSaveButton(html.BUTTON):
    '''If the currently open file already has a name, this button re-saves the file with that name.
    Otherwise it opens a dialog for saving a file.
    Required parameter:
    preparefile: function which returns a string with the contents of the file to be saved. This function takes no argguments.
    Optional parameters:
    returnaction: function to be called after the file is opened.
    This function takes two arguments: the contents and the name of the file which was opened.
    extlist: a list of file extensions which should be displayed in the dialog.  If omitted, all files will be displayed.
    defaultextension: extension which will be appended to the filename given if not already present.
    initialfolder: the path to the folder initially displayed in the dialog.''' 
    def __init__(self, preparefile, returnaction=None, extlist=[], defaultextension=None, initialfolder=".", id=None):
        global filesavedialog
        html.BUTTON.__init__(self, html.IMG(src="brywidgets/Save.png"), type="button", title="Save File", id=id, Class="imagebutton")
        self.bind("click", self.onClick)
        if not filesavedialog: filesavedialog = FileSaveDialog(returnaction, extlist, defaultextension)
        self.initialfolder = initialfolder
        self.preparefile = preparefile
        if id: self.id = id

    def onClick(self, event):
        filesavedialog.filetosave = self.preparefile()
        if filesavedialog.filename:
            filesavedialog.autosave()
        else:
            filesavedialog.open(self.initialfolder)
    
class UserFileOpenButton(FileOpenButton):
    '''Same as FileOpenButton, but requires a user to have their own folder to save files in - ie to be logged in.
    For the parameters, see FileOpenButton.'''
    def __init__(self, returnaction, extlist=[], id=None):
        FileOpenButton.__init__(self, returnaction, extlist, id=id)
    
    def onClick(self, event):
        if currentuser is None:
            alert("In order to save or open files, you need to log in.\nPlease click the login button.")
        else:
            fileopendialog.open("./users/"+currentuser)

class UserFileSaveAsButton(FileSaveAsButton):
    '''Same as FilesaveAsButton, but requires a user to have their own folder to save files in - ie to be logged in.
    For the parameters, see FileSaveAsButton.'''
    def __init__(self, preparefile, returnaction=None, extlist=[], defaultextension=None, id=None):
        FileSaveAsButton.__init__(self, preparefile, returnaction, extlist, defaultextension, id=id)
    
    def onClick(self, event):
        if currentuser is None:
            alert("In order to save or open files, you need to log in.\nPlease click the login button.")
        else:
            filesavedialog.filetosave = self.preparefile()
            filesavedialog.open("./users/"+currentuser)
    
class UserFileSaveButton(FileSaveButton):
    '''Same as FileSaveButton, but requires a user to have their own folder to save files in - ie to be logged in.
    For the parameters, see FileSaveButton.'''
    def __init__(self, preparefile, returnaction=None, extlist=[], defaultextension=None, id=None):
        FileSaveButton.__init__(self, preparefile, returnaction, extlist, defaultextension, id=id)
    
    def onClick(self, event):
        if currentuser is None:
            alert("In order to save or open files, you need to log in.\nPlease click the login button.")
        else:
            filesavedialog.filetosave = self.preparefile()
            if filesavedialog.filename:
                filesavedialog.autosave()
            else:
                filesavedialog.open("./users/"+currentuser)
    
class LoginButton(html.BUTTON):
    '''Button which opens a dialog asking the user to supply their username.
    Optional parameter:
    returnaction: function to be called on returning from the dialog after a successful login.
    This function takes one argument - the username.'''
    def __init__(self, returnaction=None, id=None):
        global logindialog
        html.BUTTON.__init__(self, html.IMG(src="brywidgets/login.png"), type="button", title="Log In...", Class="imagebutton")
        self.bind("click", self.onClick)
        if not logindialog: logindialog = LoginDialog("Please type your username below:", returnaction)
        if id: self.id = id
    
    def onClick(self, event):
        logindialog.open()

class ImageFromSVGButton(html.BUTTON):
    '''Button which opens an Overlaypanel showing a png image created from an SVG image.
    Required paraemter:
    svgimage: the image to be converted to png.'''
    def __init__(self, svgimage, id=None):
        html.BUTTON.__init__(self, html.IMG(src="brywidgets/Copy.png"), type="button", title="Copy or Save...", Class="imagebutton")
        self.bind("click", self.onClick)
        self.svgimage = svgimage

    def onClick(self, event):
        global imagefromsvg
        if not imagefromsvg: imagefromsvg = ImageFromSVG()
        imagefromsvg.show()
        imagefromsvg.SVGtoPNG(self.svgimage)

class Overlay(html.DIV):
    '''Not intended to be created by end user'''
    def __init__(self, contents):
        html.DIV.__init__(self, contents, Class="overlay")

class OverlayPanel(html.DIV):
    '''An overlay page which fills the browser window (unlike a dialog box).
    Required parameter: title (text for the title bar).'''
    def __init__(self, title, id=None):
        html.DIV.__init__(self, "", Class="overlaypanel")
        if id: self.id=id
        self.overlay = Overlay(self)
        closebutton = html.IMG(src="brywidgets/closebutton.png", Class = "closebutton")
        closebutton.bind("click", self.close)
        titlebar = html.DIV([title, closebutton], Class="titlebar")
        self <= titlebar
        document <= self.overlay
    
    def show(self):
        self.overlay.style.visibility = "visible"

    def hide(self):
        self.overlay.style.visibility = "hidden"
    
    def close(self, event):
        self.hide()

class ImageFromSVG(OverlayPanel):
    '''Not intended to be created by end user.  To use, include an ImageFromSVGButton in the page.'''    
    def __init__(self):
        OverlayPanel.__init__(self, "Right click to copy or save image")
        self.canvas = html.CANVAS(id="canvascopy")
        self <= self.canvas

    def drawimage(self, event):
        ctx = self.canvas.getContext("2d")
        ctx.drawImage(self.svgimage, 0, 0)
        png = self.canvas.toDataURL("image/png")
        self.pngimage = html.IMG(src=png, id="pngcopy")
        self <= self.pngimage
        window.URL.revokeObjectURL(png)

    def SVGtoPNG(self, SVG):
        xmls = window.XMLSerializer.new()
        svgString = xmls.serializeToString(SVG)
        self.canvas.attrs["width"] = SVG.attrs["width"]
        self.canvas.attrs["height"] = SVG.attrs["height"]
        self.svgimage = html.IMG()
        self.svgimage.bind("load", self.drawimage)
        self.svgimage.src = 'data:image/svg+xml; charset=utf8, '+window.encodeURIComponent(svgString);
    
    def close(self, event):
        delete(self.pngimage)
        self.hide()
    
class DialogBox(html.DIV):
    '''An overlay in the middle of the browser window.
    Required parameter: title (text for the title bar).'''
    def __init__(self, title, returnaction=None, content=None, id=None):
        html.DIV.__init__(self, "", Class="dialogbox")
        self.returnaction = returnaction
        if id: self.id=id
        self.overlay = Overlay(self)
        closebutton = html.IMG(src="brywidgets/closebutton.png", Class = "closebutton")
        closebutton.bind("click", self.close)
        titlebar = html.DIV([title, closebutton], Class="titlebar")
        self <= titlebar
        if content: self <= content
        document <= self.overlay
    
    def show(self):
        self.overlay.style.visibility = "visible"

    def hide(self):
        self.overlay.style.visibility = "hidden"
    
    def close(self, event):
        self.hide()

class LoginDialog(DialogBox):
    '''Not intended to be created by end user.  To use, include a LoginButton in the page.'''    
    def __init__(self, loginmessage, returnaction=None, id=None):
        DialogBox.__init__(self, "Log In", id=id)
        self.returnaction = returnaction
        self <= html.P(loginmessage)
        self.loginbox = InputBox(self.checkuserexists, id="loginbox")
        self <= self.loginbox
        self <= Button("Log In", self.checkuserexists)
        self <= html.HR()
        self <= html.P("Don't have a username?\nClick below to create one")
        self <= Button("Create username", self.openusernamedialog)
    
    def open(self):
        self.show()
        self.loginbox.focus()

    def checkuserexists(self, event):
        def oncomplete(request):
            global currentuser
            response = request.text.strip()
            if response == "True":
                self.hide()
                currentuser = username
                if self.returnaction: self.returnaction(username)
            else:
                alert("Sorry - this username does not exist.")
        username = self.loginbox.value
        request = ajax.ajax()
        request.bind("complete", oncomplete)
        request.open("POST", "brywidgets/checkfolderexists.cgi", True)
        request.set_header('content-type','application/x-www-form-urlencoded')
        request.send({"username":username})

    def openusernamedialog(self, event):
        global usernamedialog
        message = """Your username should consist of letters and numbers only.<br />
        Choose something which you will remember but other people will not guess"""
        if not usernamedialog: usernamedialog = UsernameDialog(message, self.returnaction)
        self.hide()
        usernamedialog.open()
        
class UsernameDialog(DialogBox):
    '''Not intended to be created by end user.'''    
    def __init__(self, message, returnaction=None, id=None):
        DialogBox.__init__(self, "Create User Name", id=id)
        self.returnaction = returnaction
        self <= html.P(message)
        self.usernamebox = InputBox(self.checkuserexists, id="usernamebox")
        self <= self.usernamebox
        self <= Button("Create Username", self.checkuserexists)

    def open(self):
        self.show()
        self.usernamebox.focus()

    def checkuserexists(self, event):
        def oncomplete(request):
            response = request.text.strip()
            if response == "True":
                alert("Sorry - this username is already in use.")
            else:
                self.hide()
                self.createusername(username)
        username = self.usernamebox.value
        request = ajax.ajax()
        request.bind("complete", oncomplete)
        request.open("POST", "brywidgets/checkfolderexists.cgi", True)
        request.set_header('content-type','application/x-www-form-urlencoded')
        request.send({"username":username})
            
    def createusername(self, username):
        def oncomplete(request):
            global currentuser
            response = request.text.strip()
            if response == "OK":
                currentuser = username
                if self.returnaction: self.returnaction(username)
                alert("Username created.  You are now logged in.")
        request = ajax.ajax()
        request.bind("complete", oncomplete)
        request.open("POST", "brywidgets/createfolder.cgi", True)
        request.set_header('content-type','application/x-www-form-urlencoded')
        request.send({"username":username})

class FileDialog(DialogBox):
    '''Not intended to be created by end user.  Base class for all file dialogs.'''    
    def __init__(self, title, returnaction=None, extlist=[], id=None):
        DialogBox.__init__(self, title, returnaction, id=id)
        self.path = None
        self.extlist = extlist
        
        self.fileinput = html.INPUT(id="fileinput")
        self <= self.fileinput
        self.filelistbox = html.UL(id="filelistbox")
        self <= self.filelistbox

    def open(self, initialfolder="."):
        if currentuser or self.path is None: self.path = [initialfolder]
        self.getfilelist("/".join(self.path))
        self.show()

    def onitemclick(self, event):
        for item in self.filelistbox.select("li"): item.style.backgroundColor = "white"
        event.target.style.backgroundColor = "skyblue"
        if event.target.className != "parentfolder":
            self.fileinput.value = event.target.text
    
    def onfolderdoubleclick(self, event):
        self.path.append(event.target.text)
        self.getfilelist("/".join(self.path))
        self.fileinput.value = ""
    
    def onfiledoubleclick(self, event):
        pass

    def onupdoubleclick(self, event):
        self.path.pop()
        self.getfilelist("/".join(self.path))
        self.fileinput.value = ""
    
    def getfilelist(self, folder):
        request = ajax.ajax()
        request.bind("complete", self.populatebox)
        request.open("POST", "brywidgets/sendfilelist.cgi", True)
        request.set_header('content-type','application/x-www-form-urlencoded')
        request.send({"folder":folder})
    
    def populatebox(self, request):
        folderlist, filelist = request.text.strip().split(chr(30))
        self.folderlist = folderlist.split(chr(31))
        self.filelist = filelist.split(chr(31))
        if self.extlist: self.filelist = [filename for filename in self.filelist if filename.split(".")[-1] in self.extlist]

        self.filelistbox.text = ""
        if len(self.path) > 1:
            upalevel = html.LI("[Up a level]", Class="parentfolder")
            upalevel.bind("dblclick", self.onupdoubleclick)
            self.filelistbox <= upalevel
        self.filelistbox <= (html.LI(x, Class="foldername") for x in self.folderlist)
        self.filelistbox <= (html.LI(x, Class="filename") for x in self.filelist)
        for item in self.filelistbox.select("li"): item.bind("click", self.onitemclick)
        for item in self.filelistbox.select("li.foldername"): item.bind("dblclick", self.onfolderdoubleclick)
        for item in self.filelistbox.select("li.filename"): item.bind("dblclick", self.onfiledoubleclick)
    
class FileOpenDialog(FileDialog):
    '''Not intended to be created by end user.  To use, include a (User)FileOpenButton in the page.'''    
    def __init__(self, returnaction=None, extlist=[]):
        FileDialog.__init__(self, "Open File", returnaction, extlist, id="fileopendialog")
        self <= html.DIV(Button("Open", self.onopenbutton), id="buttondiv")

    def onfiledoubleclick(self, event):
        filename = event.target.text
        self.path.append(filename)
        filepath = "/".join(self.path)
        f = open(filepath).read()
        self.path.pop()
        filesavedialog.filename = filename
        filesavedialog.path = self.path
        self.hide()
        self.returnaction(f, filename)
    
    def onopenbutton(self, event):
        filename = self.fileinput.value
        self.path.append(filename)
        filepath = "/".join(self.path)
        if filename in self.folderlist:
            self.getfilelist(filepath)
        else:
            f = open(filepath).read()
            self.path.pop()
            filesavedialog.filename = filename
            filesavedialog.path = self.path
            self.hide()
            self.returnaction(f, filename)

class FileSaveDialog(FileDialog):
    '''Not intended to be created by end user.  To use, include a (User)FileSaveAsButton in the page.'''    
    def __init__(self, returnaction=None, extlist=[], defaultextension=None):
        FileDialog.__init__(self, "Save File", returnaction, extlist, id="filesavedialog")
        self.filename = None
        self.filetosave = None
        self.defaultextension = defaultextension
        self <= html.DIV(Button("Save", self.onsavebutton), id="buttondiv")

    def onsavebutton(self, event):
        filename = self.fileinput.value
        if filename == "":
            alert("No name given for the file")
            return
        if self.defaultextension:
            ext = "."+self.defaultextension
            if filename[-4:] != ext: filename += ext
        self.path.append(filename)
        filepath = "/".join(self.path)
        if filename in self.folderlist:
            self.getfilelist(filepath)
        else:
            if filename in self.filelist:
                response = confirm("File exists. Overwrite?")
                if response is False:
                    self.path.pop()
                    return
            self.savefile(filepath, self.filetosave)
            self.filename = filename
            self.path.pop()
            self.hide()
            self.returnaction(filename)
        
    def autosave(self):
        self.path.append(self.filename)
        filepath = "/".join(self.path)
        self.savefile(filepath, self.filetosave)
        self.path.pop()
        self.hide()
        self.returnaction(self.filename)
        
    def savefile(self, filepath, filetosave):
        request = ajax.ajax()
        #request.bind("complete", self.closedialog)
        request.open("POST", "brywidgets/savefile.cgi", True)
        request.set_header('content-type','application/x-www-form-urlencoded')
        request.send({"filepath":filepath, "filetosave":filetosave})

    def closedialog(self, request):
        self.hide()

class ColourPickerDialog(DialogBox):
    '''Not intended to be created by end user.  To use, include a ColourPicker(Image)Button in the page.'''    
    def __init__(self, returnaction=None):
        DialogBox.__init__(self, "Colour Picker", returnaction, id="colourpickerdialog")       
        self.basecolourbox = html.DIV("", id="basecolourbox")
        self.basecolourbox <= html.IMG(src="brywidgets/whitemask.png", id="whitemask")
        self.basecolourbox <= html.IMG(src="brywidgets/blackmask.png", id="blackmask")
        self.colourpointer = html.IMG(src="brywidgets/circle.png", id="colourpointer")
        self.basecolourbox <= self.colourpointer
        self.basecolourbox.bind("click", self.selectcolour)
        self <= self.basecolourbox
        
        hueswatch = html.DIV(html.IMG(src="brywidgets/hues.png", id="hues"), id="hueswatch")
        self.huepointer = html.IMG(src="brywidgets/circle.png", id="huepointer")
        hueswatch <= self.huepointer
        hueswatch.bind("click", self.selecthue)
        self <= hueswatch
        
        self.colourdemo = html.DIV("", id="colourdemo")
        self <= self.colourdemo
        self <= Button("Select", self.onSelect, id="colourpickerselect")
        
        self.setupfromcolour("rgb(0, 255, 255)")
        
    def selecthue(self, event):
        hueswatch = event.currentTarget.getBoundingClientRect()
        x, y = int(event.clientX - hueswatch.left), int(event.clientY- hueswatch.top)
        (self.huepointer.left, self.huepointer.top) = (x-5, y-5) 
        huenumber = x*6+y//8
        
        self.hue, self.colour = hwbtorgb(huenumber, self.whitealpha, self.blackalpha)
        self.basecolourbox.style.backgroundColor = "rgb({},{},{})".format(*self.hue)
        self.colourdemo.style.backgroundColor = "rgb({},{},{})".format(*self.colour)
    
    def selectcolour(self, event):
        x, y = event.clientX - event.currentTarget.getBoundingClientRect().left, event.clientY- event.currentTarget.getBoundingClientRect().top
        (self.colourpointer.left, self.colourpointer.top) = (x-5, y-5) 
        (self.whitealpha, self.blackalpha) = (x/255, y/255)
        hue, self.colour = hwbtorgb(self.hue, self.whitealpha, self.blackalpha)
        self.colourdemo.style.backgroundColor = "rgb({},{},{})".format(*self.colour)
    
    def setupfromcolour(self, colour):
        self.colour = rgbtotuple(colour)
        self.colourdemo.style.backgroundColor = colour
        
        self.hue, huenumber, self.whitealpha, self.blackalpha = rgbtohwb(colour)

        self.basecolourbox.style.backgroundColor = "rgb({},{},{})".format(*self.hue)
        (x, y) = (int(self.whitealpha*255), int(self.blackalpha*255))
        (self.colourpointer.left, self.colourpointer.top) = (x-5, y-5) 

        (x, y) = (huenumber//6, (huenumber%6)*8)
        (self.huepointer.left, self.huepointer.top) = (x-5, y-5)
        
    def onSelect(self, event):
        self.hide()
        self.returnaction("rgb({}, {}, {})".format(*self.colour))

document.select("head")[0] <= html.LINK(rel="stylesheet", href="brywidgets/widgetset.css", type="text/css")
colourpickerdialog = None
fileopendialog = None
filesavedialog = None
logindialog = None
usernamedialog = None
currentuser = None
imagefromsvg = None
