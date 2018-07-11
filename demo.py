from browser import document, html
import brywidgets as ws
from data import artistdict

#####Event handlers for the various controls#####
def showartist(event):
    song = event.target.value
    document["artist"].text = song + " was recorded by " + artistdict[song]

def countsongs(event):
    artist = event.target.value
    document["songcount"].text = "Number of songs by " + artist +": " + str(list(artistdict.values()).count(artist))
    
def changecolour(colour, id):
    panel1.style.backgroundColor=colour
    
def showfile(filecontent, filename):
    document["usertext"].value = filecontent
    document["filename"].text = filename

def showfilename(filename):
    document["filename"].text = filename

def gettext():
    return document["usertext"].value

#################################################
#    Code for building the page starts here.    #
#################################################

page1 = ws.NotebookPage("Demo", "powderblue", id="page1")
page2 = ws.NotebookPage("Brython code", "khaki", html.TEXTAREA(open("demo.py").read()), id="page2")
page3 = ws.NotebookPage("CSS", "lightgreen", html.TEXTAREA(open("demo.css").read()), id="page3")
page4 = ws.NotebookPage("HTML", "lightpink", html.TEXTAREA(open("demo.html").read()), id="page4")
document <= ws.Notebook([page1, page2, page3, page4])

page1 <= (html.H1("Brywidgets Demo"),
            html.P("""This page is a demo of most of the widgets in the brywidgets module. 
                The whole page is a Notebook with 4 tabs - the other 3 tabs show the files which create this page. 
                This page contains a RowPanel with two Panels each containing a ColumnPanel.
                The buttons on the right are laid out using GridPanels"""))

panel1 = ws.Panel(title="The 100 greatest singles of all time - click to find the artist", id="panel1")
panel1 <= ws.ColumnPanel([html.P("(This Panel shows a ListBox, a Dropdown, and a ColourPickerButton.)"),
            html.DIV([ws.ListBox(artistdict.keys(), showartist, 10), html.P(id="artist"),
            ws.DropDown(sorted(set(artistdict.values())), countsongs), html.P(id="songcount"),
            ws.ColourPickerButton(changecolour, "Choose Colour")])])

panel2 = ws.Panel(title="Opening and saving files", id="panel2")
panel2 <= ws.ColumnPanel([html.P("(This is a FileOpenButton, FileSaveButton and FileSaveAsButton)"),
            ws.GridPanel(3, 1, [ws.FileOpenButton(showfile, initialfolder="users/demo"),
                ws.FileSaveButton(gettext, showfilename, initialfolder="users/demo"), 
                ws.FileSaveAsButton(gettext, showfilename, initialfolder="users/demo")]),
            html.P("Untitled", id="filename"),
            html.TEXTAREA(id="usertext"),
            html.P("""(This is a LoginButton, UserFileOpenButton, UserFileSaveButton and UserFileSaveAsButton.
            The user has to be logged in to open or save files with these buttons.)"""),
            ws.GridPanel(3, 2, [ws.LoginButton(), html.DIV(), html.DIV(),
                ws.UserFileOpenButton(showfile),
                ws.UserFileSaveButton(gettext, showfilename), 
                ws.UserFileSaveAsButton(gettext, showfilename)])])

page1 <= ws.RowPanel([panel1, panel2])
