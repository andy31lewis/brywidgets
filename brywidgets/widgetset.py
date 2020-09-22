#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2018-2020 Andy Lewis                                                   #
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

from browser import document, window, alert, confirm
import browser.html as html
import browser.ajax as ajax
from .images import *

#head = document.select("head")[0]
#head.insertAdjacentElement("afterbegin", html.LINK(rel="stylesheet", href="brywidgets/widgetset.css", type="text/css"))

#Utility functions
def delete(element):
    element.parentNode.removeChild(element)
    del element

def gettextwidth(text, font="12pt Arial"):
    canvas = html.CANVAS()
    ctx = canvas.getContext("2d")
    ctx.font = font
    return ctx.measureText(text).width

#Colour utility functions

def rgbtotuple(colour):
    return tuple([int(x) for x in colour[4:-1].split(",")])

def tupletohex(colourtuple):
    return "#"+''.join(format(n, '02x') for n in colourtuple)

def hextotuple(hexcolour):
    return tuple(int(hexcolour[i:i+2], 16) for i in [1, 3, 5])

def rgbtohwb(colour):
    if isinstance(colour, str): colour = rgbtotuple(colour)
    maxc = max(colour); maxi = colour.index(maxc)
    minc = min(colour); mini = colour.index(minc)
    whitealpha = 1 if maxc == 0 else minc/maxc
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

class Global():
    alertStyle = "standard"
    promptStyle = "standard"

class Notebook(html.DIV):
    '''A tabbed set of pages; switch between pages by clicking on a tab.
    To use, create pages by subclassing (or instantiating) NotebookPage, then create the notebook.
    For example:
        page1 = NotebookPage("First page", "lightgreen")
        page2 = NotebookPage("Second page", "powderblue")
        nb = Notebook([page1, page2])
    More pages can be added using nb.addpage.
    The height of the tabs is automatically set to accomodate 1 line of text, but can be adjusted
    by specifying the parameter tabheight in CSS units.'''

    def __init__(self, pagelist=[], tabheight="2em", className=None, id=None):
        html.DIV.__init__(self, "", Class="notebook")
        self.clearfloat = html.DIV(style={"clear":"both"})
        self.tabrow = html.DIV(self.clearfloat, Class="notebooktabrow", style={"text-align":"center"})
        self.tabheight = tabheight
        self <= self.tabrow
        self.pagelist = []
        for page in pagelist: self.addpage(page)
        if className: self.classList.add(className)
        if id: self.id = id

    def addpage(self, page):
        self <= page
        tab = NotebookTab(self, len(self.pagelist), page.title, self.tabheight, page.tabwidth)
        tab.style.backgroundColor = page.style.backgroundColor
        if page.id: tab.id = page.id+"_tab"
        self.tabrow.insertBefore(tab, self.clearfloat)
        page.style.display="block" if len(self.pagelist)==0 else "none"
        self.pagelist.append(page)

class NotebookPage(html.DIV):
    '''A page in a notebook.  Create with a title (which appears on its tab), and a background colour.
    Optionally include content at creation time, or else add it later.
    For external CSS styling of pages use class .notebookpage, or give each page an id and use #(pageid).
    Set the width of the tab using CSS, or set it to None to use external CSS styling,
    either for class .notebooktab or id #(pageid)_tab'''
    def __init__(self, title, bgcolour, content=None, tabwidth="10%", className=None, id=None):
        html.DIV.__init__(self, "", style={"background-color":bgcolour}, Class="notebookpage")
        self.title = title
        self.tabwidth = tabwidth
        if className: self.classList.add(className)
        if id: self.id = id
        if content: self <= content

    def update(self):
        pass

class NotebookTab(html.DIV):
    '''Not intended to be created by end user.
    A tab at the top of a NotebookPage.'''
    def __init__(self, notebook, index, title, height, width):
        html.DIV.__init__(self, html.P(title, style={"margin":"0.4em"}), Class="notebooktab", style={"height":height, "float":"left", "cursor":"pointer"})
        if width: self.style.width = width
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
    initialchoice: index (counting from 0) of the inital choice.
    For external CSS styling use class .dropdown, or give the dropdown an id and use #(id).'''
    def __init__(self, choices, onchange, initialchoice=None, className=None, id=None):
        html.SELECT.__init__(self, "", Class="dropdown")
        self <= (html.OPTION(text) for text in choices)
        self.bind("change", onchange)
        if initialchoice: self.selectedIndex = initialchoice
        if className: self.classList.add(className)
        if id: self.id = id

class ListBox(html.SELECT):
    '''List of options (all shown unless the number to show is given in which case a scroll bar is used).
    Required parameters
    choices: a list of options
    onchange: function to be called when the user chooses a different option.  Takes the change event as argument.
    Optional parameters:
    size: number of choices to be displayed
    initialchoice: index (counting from 0) of the inital choice.
    For external CSS styling use class .listbox, or give the listbox an id and use #(id).'''
    def __init__(self, choices, onchange, size=None, initialchoice=None, className=None, id=None):
        html.SELECT.__init__(self, "", Class="listbox")
        self <= (html.OPTION(text) for text in choices)
        self.bind("change", onchange)
        self.size = size if size else len(choices)
        self.selectedIndex = initialchoice if initialchoice else -1
        if className: self.classList.add(className)
        if id: self.id = id

class InputBox(html.INPUT):
    '''Standard input box.
    Required parameter:
    enterkeyaction: function to be called if the Enter key is pressed. Takes the string value of the input as argument.
    Optional parameter:
    style: dictionary containing any CSS styling required'''
    def __init__(self, enterkeyaction, style=None, className=None, id=None):
        html.INPUT.__init__(self, Class="inputbox")
        if style: self.style = style
        self.enterkeyaction = enterkeyaction
        self.bind("keypress", self.onKeypress)
        if className: self.classList.add(className)
        if id: self.id = id

    def onKeypress(self, event):
        if event.keyCode != 13: return
        self.enterkeyaction(self.value)

class SpinControl(html.DIV):
    '''Control showning an initial (integer) value, and buttons to increase or decrease it.
    Required parameters:
    initialvalue
    minvalue, maxvalue: values beyond which the control cannot be decreased or increased
    action: function to be called when the value is changed. Takes one parameter, the current value of the control.
    Optional parameter:
    stepvalue: the amount by which the value is increased or decreased (default is 1)'''
    def __init__(self, initialvalue, minvalue, maxvalue, action, stepvalue=1, className=None, id=None):
        decrease = html.IMG(src=minus_b64, id="minus", style={"height":"100%", "float":"left"})
        decrease.bind("click", self.ondecrease)
        increase = html.IMG(src=plus_b64, id="plus", style={"height":"100%", "float":"right"})
        increase.bind("click", self.onincrease)
        self.currentvalue = initialvalue
        self.stepvalue = stepvalue
        self.minvalue = minvalue
        self.maxvalue = maxvalue
        widthems = max(len(str(minvalue)), len(str(maxvalue)))*0.6 + 3
        self.valuespan = html.SPAN(str(self.currentvalue), style={"cursor":"default"})
        styledict = {"border":"1px solid blue", "height":"1.1em", "width":f"{widthems}em", "text-align":"center"}
        html.DIV.__init__(self,[decrease, self.valuespan, increase], Class="spincontrol", style=styledict)
        self.action = action
        if className: self.classList.add(className)
        if id: self.id = id

    def setValue(self, n):
        self.currentvalue = n
        self.valuespan.text = str(self.currentvalue)

    def ondecrease(self, event):
        if self.currentvalue-self.stepvalue >= self.minvalue: self.currentvalue -= self.stepvalue
        self.valuespan.text = str(self.currentvalue)
        self.action(self.currentvalue)

    def onincrease(self, event):
        if self.currentvalue+self.stepvalue <= self.maxvalue: self.currentvalue += self.stepvalue
        self.valuespan.text = str(self.currentvalue)
        self.action(self.currentvalue)

class Panel(html.DIV):
    '''Just a container with a default border. Optional parameters:
    items: contents of the panel
    border: border of the panel, in CSS format (use None for no border or to set in external spreadsheet)
    align: text-align, in CSS format
    title: heading at the top of the panel. '''
    def __init__(self, items=None, border="1px solid white", align=None, title=None, className=None, id=None):
        html.DIV.__init__(self, "", Class="panel")
        if className: self.classList.add(className)
        if id: self.id = id
        if border: self.style.border = border
        if align: self.style.textAlign = align
        if title: self <= html.P(title, Class="paneltitle")
        if items: self <= items

class RowPanel(html.DIV):
    '''Container which lays its contents out in a row. Optional parameter:
    items: contents of the panel'''
    def __init__(self, items=None, className=None, id=None):
        html.DIV.__init__(self, "", Class="rowpanel", style={"display":"flex"})
        if items: self <= items
        if className: self.classList.add(className)
        if id: self.id = id

class ColumnPanel(html.DIV):
    '''Container which lays its contents out in a column. Optional parameter:
    items: contents of the panel'''
    def __init__(self, items=None, className=None, id=None):
        html.DIV.__init__(self, "", Class="columnpanel", style={"display":"flex", "flex-direction":"column"})
        if items: self <= items
        if className: self.classList.add(className)
        if id: self.id = id

class GridPanel(html.DIV):
    '''Container which lays its contents out in a specified grid.
    Required parameters:
    columns, rows: size of the grid
    Optional parameter:
    items: contents of the grid'''
    def __init__(self, columns, rows, items=None, className=None, id=None):
        html.DIV.__init__(self, "", Class="gridpanel", style={"display":"grid", "justify-content":"center", "align-items":"center"})
        self.style.gridTemplateColumns = " ".join(["auto"]*columns)
        self.style.gridTemplateRows = " ".join(["auto"]*rows)
        if items: self <= items
        if className: self.classList.add(className)
        if id: self.id = id

class Button(html.BUTTON):
    '''Button with text (or blank).
    Required parameters:
    text: Text of the button (could be empty string)
    handler:  Function to be called on click. This function takes the click event as argument.
    Optional parameters:
    bgcolour: background colour of the button.
    tooltip: text displayed when hovering over the button'''
    def __init__(self, text, handler, bgcolour=None, tooltip=None, className=None, id=None):
        html.BUTTON.__init__(self, text, type="button", Class="button")
        self.bind("click", handler)
        if bgcolour: self.style.backgroundColor = bgcolour
        if tooltip: self.title = tooltip
        if className: self.classList.add(className)
        if id: self.id = id

class ImageButton(Button):
    '''Button with an image.
    Required parameters:
    icon: the path to its image
    handler:  Function to be called on click. This function takes the click event as argument.
    Optional parameters:
    bgcolour: background colour of the button.
    tooltip: text displayed when hovering over the button'''
    def __init__(self, icon, handler, bgcolour=None, tooltip=None, className=None, id=None):
        Button.__init__(self, "", handler, bgcolour, tooltip, className, id)
        self <= html.IMG(src=icon, style={"margin":"0px"})
        self.classList.add("imagebutton")

class ToggleButton(Button):
    '''Button which remains depressed when clicked, until clicked again or raised by other means.
    For parameters see Button.'''
    def __init__(self, text, handler, bgcolour=None, tooltip=None, className=None, id=None):
        Button.__init__(self, text, self.onClick, bgcolour, tooltip, className, id)
        self.classList.add("togglebutton")
        #self._selected = None
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
    def __init__(self, icon, handler, bgcolour=None, tooltip=None, className=None, id=None):
        ToggleButton.__init__(self, "", handler, bgcolour, tooltip, className, id)
        #self.style.padding = "0px"
        self <= html.IMG(src=icon)
        self.classList.add("toggleimagebutton")

class RadioButton(html.SPAN):
    def __init__(self, radiogroup, radioid, label, selected=False, tooltip=None, action=None, className=None, id=None):
        html.SPAN.__init__(self)
        if className: self.classList.add(className)
        objid = id if id else f"{radiogroup}_{radioid}"
        self.button = html.INPUT(type="radio", name=radiogroup, value=radioid, id=objid)
        self.label = html.LABEL(label)
        self.label.attrs["for"] = objid
        self <= [self.button, self.label]
        if selected: self.button.checked = True
        if tooltip:
            self.button.title = tooltip
            self.label.title = tooltip
        if action: self.button.bind("change", action)

class CheckBox(html.SPAN):
    def __init__(self, label, objid, selected=False, tooltip=None, action=None, className=None):
        html.SPAN.__init__(self)
        self.button = html.INPUT(type="checkbox", name=objid, id=objid)
        self.label = html.LABEL(label)
        self.label.attrs["for"] = objid
        self <= [self.button, self.label]
        if selected: self.button.checked = True
        if tooltip:
            self.button.title = tooltip
            self.label.title = tooltip
        if action: self.button.bind("change", action)
        if className: self.classList.add(className)

class ColourPickerButton(html.BUTTON):
    '''Button which opens a colour picker, and then takes on the colour which is selected.
    Required parameter:
    returnaction: function to be called after a colour is selected
    This function takes two arguments: the colour selected, and the id of the button (which could be None).
    Optional parameters:
    label: Text on the button
    initialcolour: initial background colour of the button (in rgb() format). If omitted the default colour rgb(242, 241, 240) is used.'''
    def __init__(self, returnaction, label="", initialcolour=None, className=None, id=None):
        html.BUTTON.__init__(self, label, type="button", title="Open Colour Picker...", Class="button")
        self.classList.add("colourpickerbutton")
        if className: self.classList.add(className)
        self.style.backgroundColor = initialcolour if initialcolour else "rgb(242, 241, 240)"
        if id: self.id = id
        self.bind("click", self.onClick)
        self.returnaction = returnaction

    def onClick(self, event):
        global colourpickerdialog
        if not colourpickerdialog:
            colourpickerdialog = ColourPickerDialog()
            colourpickerdialog.recentcolours[0].style.backgroundColor = self.style.backgroundColor
            colourpickerdialog.recent[0] = rgbtotuple(self.style.backgroundColor)
        colourpickerdialog.returnaction = self.onChange
        colourpickerdialog.setupfromtuple(rgbtotuple(self.style.backgroundColor))
        colourpickerdialog.show()

    def onChange(self, colour):
        self.style.backgroundColor = colour
        self.returnaction(colour, self.id)

class ColourPickerImageButton(html.BUTTON):
    '''Button with an image, which opens a colour picker.
    Required parameters:
    icon: the path to its image
    returnaction: function to be called after a colour is selected. This function takes one argument: the colour selected.'''
    def __init__(self, icon, returnaction, className=None, id=None):
        html.BUTTON.__init__(self, html.IMG(src=icon), type="button", title="Open Colour Picker...", Class="imagebutton")
        self.classList.add("colourpickerimagebutton")
        if className: self.classList.add(className)
        self.bind("click", self.onClick)
        self.returnaction = returnaction
        if id: self.id = id

    def onClick(self, event):
        global colourpickerdialog
        if not colourpickerdialog: colourpickerdialog = ColourPickerDialog()
        colourpickerdialog.returnaction = self.returnaction
        colourpickerdialog.show()

class ImageFromSVGButton(html.BUTTON):
    '''Button which opens an OverlayPanel showing a png image created from an SVG image.
    Required parameter:
    svgimage: the image to be converted to png.'''
    def __init__(self, svgimage, preprocess=None, className=None, id=None):
        html.BUTTON.__init__(self, html.IMG(src=copy_b64), type="button", title="Copy or Save...", Class="imagebutton")
        self.bind("click", self.onClick)
        self.svgimage = svgimage
        self.preprocess = preprocess if preprocess else None
        if className: self.classList.add(className)
        if id: self.id = id

    def onClick(self, event):
        global imagefromsvg
        if self.preprocess: self.preprocess()
        if not imagefromsvg: imagefromsvg = ImageFromSVG()
        imagefromsvg.show()
        imagefromsvg.SVGtoPNG(self.svgimage)

class Overlay(html.DIV):
    '''Not intended to be created by end user'''
    def __init__(self, contents):
        styledict = {"position":"fixed", "top":"0px", "bottom":"0px", "left":"0px", "right":"0px", "visibility":"hidden", "background-color":"transparent", "display":"flex", "align-items":"center"}
        html.DIV.__init__(self, contents, style=styledict, Class="overlay")

class OverlayPanel(html.DIV):
    '''An overlay page which fills the browser window (unlike a dialog box).
    Required parameter: title (text for the title bar).
    Optional parameter:
    style:  If this is set to "standard", the panel will be light grey with a dark grey titlebar.
            If not set, styling can be done using an external CSS stylesheet for classes .overlaypanel and .titlebar
    Available methods: show, hide, close (the last two are identical unless amended in a subclass).'''
    def __init__(self, title, style=None, id=None):
        overlaystyle = {"position":"absolute", "top":"0px", "left":"0px", "width":"100%", "height":"100%"}
        titlebarstyle = {"position":"relative", "width":"100%", "height":"1.2em", "text-align":"center"}
        if style:
            if style == "standard":
                style = {"background-color":"lightgrey", "text-align":"center", "padding-bottom":"0.5em"}
                titlebarstyle.update({"background-color":"grey", "color":"white"})
            overlaystyle.update(style)
        html.DIV.__init__(self, "", style=overlaystyle, Class="overlaypanel")
        if id: self.id=id
        self.overlay = Overlay(self)
        closebuttonstyle = {"position":"absolute", "top":"0px", "right":"0px", "height":"100%"}
        closebutton = html.IMG(src=closebutton_b64, style=closebuttonstyle, Class = "closebutton")
        closebutton.bind("click", self.close)
        titlebar = html.DIV([title, closebutton], style=titlebarstyle, Class="titlebar")
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
        OverlayPanel.__init__(self, "Right click to copy or save image", style="standard")
        self.canvas = html.CANVAS(id="canvascopy")
        #self <= self.canvas
        #self.pngimage = html.IMG(id="pngcopy")
        #self <= self.pngimage

    def drawimage(self, event):
        ctx = self.canvas.getContext("2d")
        ctx.drawImage(self.svgimage, 0, 0)
        self.canvas.toBlob(self.copyimage)

    def copyimage(self, blob):
        #def copycompleted(value):  ***navigator.clipboard only available over https***
        #    print(value)
        #    alert("The tessellation should have been copied to the clipboard ready to paste into a document, email etc.\n\n"+
        #        "Alternatively, right-click or long-press on this page to save it.")
        blobURL = window.URL.createObjectURL(blob)
        self.pngimage = html.IMG(src=blobURL, id="pngcopy")
        self <= self.pngimage
        #self.pngimage.attrs["src"] = blobURL
        #try:
        #    clip = window.ClipboardItem.new({'image/png': blob})
        #except AttributeError:
        #    return
        #window.navigator.clipboard.write([clip]).then(copycompleted)
        #window.URL.revokeObjectURL(blobURL)

    def SVGtoPNG(self, SVG):
        xmls = window.XMLSerializer.new()
        svgString = xmls.serializeToString(SVG)
        self.canvas.attrs["width"] = SVG.attrs["width"]
        self.canvas.attrs["height"] = SVG.attrs["height"]
        self.svgimage = html.IMG()
        self.svgimage.bind("load", self.drawimage)
        self.svgimage.attrs["src"] = 'data:image/svg+xml; charset=utf8, '+window.encodeURIComponent(svgString);

    def close(self, event):
        delete(self.pngimage)
        self.hide()

class DialogBox(html.DIV):
    '''An overlay in the middle of the browser window.
    Required parameter: title (text for the title bar).
    Optional parameters:
    returnaction: A function to be called when the dialog is finished with
    content: The content of the box
    style:  If this is set to "standard", the panel will be light grey with a dark grey titlebar.
            If not set, styling can be done using an external CSS stylesheet for classes .dialogbox and .titlebar
    size: a tuple (width, height) in CSS units.
    Available methods: show, hide, close (the last two are identical unless amended in a subclass).'''
    def __init__(self, title, returnaction=None, content=None, style=None, size=None, id=None):
        dialogstyle = {"position":"relative", "z-index":"1", "margin":"auto"}
        titlebarstyle = {"position":"relative", "width":"100%", "height":"1.3em", "text-align":"center"}
        if style:
            if style == "standard":
                style = {"width":"33%", "background-color":"lightgrey", "border":"1px solid grey", "text-align":"center", "padding-bottom":"0.5em"}
                titlebarstyle.update({"background-color":"grey", "color":"white"})
            dialogstyle.update(style)
        if size:
            (width, height) = size
            dialogstyle["width"] = width
            dialogstyle["height"] = height
        html.DIV.__init__(self, "", style=dialogstyle, Class="dialogbox")
        closebuttonstyle = {"position":"absolute", "top":"0px", "right":"0px", "height":"100%"}
        self.closebutton = html.IMG(src=closebutton_b64, style=closebuttonstyle, Class = "closebutton", id="closebutton")
        self.closebutton.bind("click", self.close)
        self.titletext = html.SPAN(title)
        titlebar = html.DIV([self.titletext, self.closebutton], style=titlebarstyle, Class="titlebar")
        self <= titlebar
        if content: self <= content
        self.returnaction = returnaction
        if id: self.id=id
        self.overlay = Overlay(self)
        document <= self.overlay

    def show(self):
        self.overlay.style.visibility = "visible"

    def hide(self):
        self.overlay.style.visibility = "hidden"

    def close(self, event):
        self.hide()

class AlertDialog(DialogBox):
    '''Not intended to be created by end user.  Use the showalert() function to display an alert.'''
    def __init__(self):
        self.messagediv = html.DIV(style={"background-color":"inherit", "margin":"1em 1em 3em 1em"})
        super().__init__("Message", content=self.messagediv, style=Global.alertStyle, id="alertdialog")
        self.okbutton = Button("OK", self.close)
        self.okbutton.style = {"position":"absolute", "right":"5px", "bottom":"5px"}
        self <= self.okbutton

    def showmessage(self, message, title=None):
        self.messagediv.innerHTML = message.replace("\n", "<br/>\n")
        if title: self.titletext.innerHTML = title
        self.show()
        self.okbutton.focus()

class PromptDialog(DialogBox):
    '''Not intended to be created by end user.  Use the showprompt() function to display a prompt dialog.'''
    def __init__(self):
        self.question = html.P(style={"margin-right":"1em"}, id="query")
        self.entrybox = html.INPUT(id="reply")
        self.entrybox.bind("keypress", self.onKeypress)
        self.querydiv = html.DIV([self.question, self.entrybox], style={"background-color":"inherit", "margin-top":"1em", "margin-bottom":"3em"})
        super().__init__("Query", content=self.querydiv, style=Global.promptStyle, id="promptdialog")
        okbutton = Button("OK", self.respond)
        okbutton.style = {"position":"absolute", "right":"5px", "bottom":"5px"}
        self <= okbutton
        self.closebutton.unbind("click")
        self.closebutton.bind("click", self.respond)

    def onKeypress(self, event):
        if event.keyCode == 13: self.respond(event)

    def showquery(self, message, action=None, title=None, default=None):
        self.question.innerHTML = message
        if title: self.titletext.innerHTML = title
        if default: self.entrybox.value = default
        self.action = action
        self.show()
        self.entrybox.focus()

    def respond(self, event):
        if event.target.id == "closebutton":
            userinput = False
        else:
            userinput = self.entrybox.value
            if not userinput: return
        super().close(event)
        if self.action: self.action(userinput)

class ColourPickerDialog(DialogBox):
    '''Not intended to be created by end user.  To use, include a ColourPicker(Image)Button in the page.'''
    def __init__(self, returnaction=None):
        def position(left, top, width=None, height=None):
            posdict = {"position":"absolute", "top":f"{top}px", "left":f"{left}px"}
            if width: posdict["width"] = f"{width}px"
            if height: posdict["height"] = f"{height}px"
            return posdict
        DialogBox.__init__(self, "Colour Picker", returnaction, size = ("380px", "360px"), style="standard")
        imgstyle = position(0, 0)
        self.basecolourbox = html.DIV("", style=position(10, 30, 256, 256))
        self.basecolourbox <= html.IMG(src=whitemask_b64, style=imgstyle)
        self.basecolourbox <= html.IMG(src=blackmask_b64, style=imgstyle)
        self.colourpointer = html.IMG(src=circle_b64, style=imgstyle)
        self.basecolourbox <= self.colourpointer
        self.basecolourbox.bind("click", self.selectcolour)
        self <= self.basecolourbox

        hueswatch = html.DIV(html.IMG(src=hues_b64, style=imgstyle), style=position(10, 300, 256, 48))
        self.huepointer = html.IMG(src=circle_b64, style=imgstyle)
        hueswatch <= self.huepointer
        hueswatch.bind("click", self.selecthue)
        self <= hueswatch

        self.hexcolourbox = InputBox(self.onhexinput, style=position(280, 30, 80))
        self <= self.hexcolourbox
        self.colourdemo = html.DIV("", style=position(286, 70, 70, 30))
        self <= self.colourdemo
        self <= (selectbutton := Button("Select", self.onSelect))
        selectbutton.style=position(286, 110, 70)
        selectbutton.style.margin = "0px"
        self.recentcolours = [html.DIV("", id=f"recent{i}", style=position(280+30*(i%3), 150+30*(i//3), 25, 25)) for i in range(15)]
        for i in range(15):
            self.recentcolours[i].style = {"border":"1px solid black", "background-color":"white"}
            self.recentcolours[i].bind("click", self.onrecentchoice)
        self <= self.recentcolours
        self.recent = [(255, 255, 255)] * 15
        self.setupfromtuple((0, 255, 255))

    def onhexinput(self, hexcolour):
        self.setupfromtuple(hextotuple(hexcolour))

    def onrecentchoice(self, event):
        i = int(event.target.id[6:])
        self.setupfromtuple(self.recent[i])


    def selecthue(self, event):
        hueswatch = event.currentTarget.getBoundingClientRect()
        x, y = int(event.clientX - hueswatch.left), int(event.clientY- hueswatch.top)
        (self.huepointer.left, self.huepointer.top) = (x-5, y-5)
        huenumber = x*6+y//8

        self.hue, self.colour = hwbtorgb(huenumber, self.whitealpha, self.blackalpha)
        self.basecolourbox.style.backgroundColor = "rgb({},{},{})".format(*self.hue)
        self.colourdemo.style.backgroundColor = "rgb({},{},{})".format(*self.colour)
        self.hexcolourbox.value = tupletohex(self.colour)

    def selectcolour(self, event):
        x, y = event.clientX - event.currentTarget.getBoundingClientRect().left, event.clientY- event.currentTarget.getBoundingClientRect().top
        (self.colourpointer.left, self.colourpointer.top) = (int(x)-5, int(y)-5)
        (self.whitealpha, self.blackalpha) = (x/255, y/255)
        hue, self.colour = hwbtorgb(self.hue, self.whitealpha, self.blackalpha)
        self.colourdemo.style.backgroundColor = "rgb({},{},{})".format(*self.colour)
        self.hexcolourbox.value = tupletohex(self.colour)

    def setupfromtuple(self, colour):
        self.colour = colour
        self.colourdemo.style.backgroundColor = "rgb({},{},{})".format(*colour)
        self.hexcolourbox.value = tupletohex(self.colour)

        self.hue, huenumber, self.whitealpha, self.blackalpha = rgbtohwb(colour)

        self.basecolourbox.style.backgroundColor = "rgb({},{},{})".format(*self.hue)
        (x, y) = (int(self.whitealpha*255), int(self.blackalpha*255))
        (self.colourpointer.left, self.colourpointer.top) = (x-5, y-5)

        (x, y) = (huenumber//6, (huenumber%6)*8)
        (self.huepointer.left, self.huepointer.top) = (x-5, y-5)

    def onSelect(self, event):
        if self.colour not in self.recent: self.recent = [self.colour]+self.recent[:-1]
        for i in range(15):
            self.recentcolours[i].style.backgroundColor = "rgb({},{},{})".format(*self.recent[i])
        self.hide()
        self.returnaction("rgb({}, {}, {})".format(*self.colour))

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
        html.BUTTON.__init__(self, html.IMG(src=open_b64), type="button", title="Open File...", id=id, Class="imagebutton")
        self.classList.add("fileopenbutton")
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
    returnaction: function to be called after the file is saved.
        This function takes one argument: the name of the file which was saved.
    extlist: a list of file extensions which should be displayed in the dialog.  If omitted, all files will be displayed.
    defaultextension: extension which will be appended to the filename given if not already present.
    initialfolder: the path to the folder initially displayed in the dialog.'''
    def __init__(self, preparefile, returnaction=None, extlist=[], defaultextension=None, initialfolder=".", id=None):
        global filesavedialog
        html.BUTTON.__init__(self, html.IMG(src=saveas_b64), type="button", title="Save File As...", id=id, Class="imagebutton")
        self.classList.add("filesaveasbutton")
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
    For parameters see FileSaveAsButton.'''
    def __init__(self, preparefile, returnaction=None, extlist=[], defaultextension=None, initialfolder=".", id=None):
        global filesavedialog
        html.BUTTON.__init__(self, html.IMG(src=save_b64), type="button", title="Save File", id=id, Class="imagebutton")
        self.classList.add("filesavebutton")
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
        self.classList.add("userfilebutton")

    def onClick(self, event):
        if currentuser is None:
            showalert("In order to save or open files, you need to log in.\nPlease click the login button.")
        else:
            fileopendialog.open("./users/"+currentuser)

class UserFileSaveAsButton(FileSaveAsButton):
    '''Same as FilesaveAsButton, but requires a user to have their own folder to save files in - ie to be logged in.
    For the parameters, see FileSaveAsButton.'''
    def __init__(self, preparefile, returnaction=None, extlist=[], defaultextension=None, id=None):
        FileSaveAsButton.__init__(self, preparefile, returnaction, extlist, defaultextension, id=id)
        self.classList.add("userfilebutton")

    def onClick(self, event):
        if currentuser is None:
            showalert("In order to save or open files, you need to log in.\nPlease click the login button.")
        else:
            filesavedialog.filetosave = self.preparefile()
            filesavedialog.open("./users/"+currentuser)

class UserFileSaveButton(FileSaveButton):
    '''Same as FileSaveButton, but requires a user to have their own folder to save files in - ie to be logged in.
    For the parameters, see FileSaveAsButton.'''
    def __init__(self, preparefile, returnaction=None, extlist=[], defaultextension=None, id=None):
        FileSaveButton.__init__(self, preparefile, returnaction, extlist, defaultextension, id=id)
        self.classList.add("userfilebutton")

    def onClick(self, event):
        if currentuser is None:
            showalert("In order to save or open files, you need to log in.\nPlease click the login button.")
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
        html.BUTTON.__init__(self, html.IMG(src=login_b64), type="button", title="Log In...", Class="imagebutton")
        self.classList.add("loginbutton")
        self.bind("click", self.onClick)
        if not logindialog: logindialog = LoginDialog("Please type your username below:", returnaction)
        if id: self.id = id

    def onClick(self, event):
        logindialog.open()

class LoginDialog(DialogBox):
    '''Not intended to be created by end user.  To use, include a LoginButton in the page.'''
    def __init__(self, loginmessage, returnaction=None, id=None):
        DialogBox.__init__(self, "Log In", style="standard", id=id)
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
                showalert("Sorry - this username does not exist.")
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
        DialogBox.__init__(self, "Create User Name", style="standard", id=id)
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
                showalert("Sorry - this username is already in use.")
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
                showalert("Username created.  You are now logged in.")
        request = ajax.ajax()
        request.bind("complete", oncomplete)
        request.open("POST", "brywidgets/createfolder.cgi", True)
        request.set_header('content-type','application/x-www-form-urlencoded')
        request.send({"username":username})

class FileDialog(DialogBox):
    '''Not intended to be created by end user.  Base class for all file dialogs.'''
    def __init__(self, title, returnaction=None, extlist=[], id=None):
        DialogBox.__init__(self, title, returnaction, style="standard", id=id)
        self.path = None
        self.extlist = extlist
        basestyle = {"display":"block", "width":"90%", "padding":"0.1em", "margin":"0.1em auto"}
        self.fileinput = html.INPUT(style=basestyle)
        liststyle = {**basestyle, "background-color":"white", "border":"1px solid black", "height":"70vh", "overflow":"auto", "white-space":"nowrap"}
        self.filelistbox = html.UL(style=liststyle)
        self.buttonarea = html.DIV(style={**basestyle, "text-align":"right"})
        self <= (self.fileinput, self.filelistbox, self.buttonarea)

    def open(self, initialfolder="."):
        if currentuser or self.path is None: self.path = [initialfolder]
        self.getfilelist("/".join(self.path))
        self.show()
        self.fileinput.focus()

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
        listitemstyle = {"text-align":"left", "list-style":"none", "padding":"0px 0px 0px 20px", "margin":"0px", "cursor":"default"}
        if len(self.path) > 1:
            listitemstyle["background"] = f"url({uparrow_b64}) no-repeat left top"
            self.filelistbox <= (upalevel := html.LI("[Up a level]", Class="parentfolder", style=listitemstyle))
            upalevel.bind("dblclick", self.onupdoubleclick)
        listitemstyle["background"] = f"url({folder_b64}) no-repeat left top"
        for x in self.folderlist:
            self.filelistbox <= (item := html.LI(x, style=listitemstyle))
            item.bind("click", self.onitemclick)
            item.bind("dblclick", self.onfolderdoubleclick)
        listitemstyle["background"] = f"url({file_b64}) no-repeat left top"
        for x in self.filelist:
            self.filelistbox <= (item := html.LI(x, style=listitemstyle))
            item.bind("click", self.onitemclick)
            item.bind("dblclick", self.onfiledoubleclick)

class FileOpenDialog(FileDialog):
    '''Not intended to be created by end user.  To use, include a (User)FileOpenButton in the page.'''
    def __init__(self, returnaction=None, extlist=[]):
        FileDialog.__init__(self, "Open File", returnaction, extlist, id="fileopendialog")
        self.buttonarea <= Button("Open", self.onopenbutton)

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
        if filename == "": return
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
    '''Not intended to be created by end user.  To use, include a (User)FileSave(As)Button in the page.'''
    def __init__(self, returnaction=None, extlist=[], defaultextension=None):
        FileDialog.__init__(self, "Save File", returnaction, extlist, id="filesavedialog")
        self.buttonarea <= Button("Save", self.onsavebutton)
        self.filename = None
        self.filetosave = None
        self.defaultextension = defaultextension

    def onsavebutton(self, event):
        filename = self.fileinput.value
        if filename == "":
            showalert("No name given for the file")
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

def showalert(message, title=None):
    '''Similar to javascript alert function.
    By default, standard dialog box styling will be used.
    If the variable Global.alertStyle is set to None, the alert will be styled using CSS styling for the .dialogbox class.
    If desired, this can be overridden by setting up styling for the id #alertdialog.'''
    global alertdialog
    try:
        alertdialog.showmessage(message, title)
    except NameError:
        alertdialog = AlertDialog()
        alertdialog.showmessage(message, title)

def showprompt(message, action=None, title=None, default=None):
    '''Similar to javascript prompt function.
    default is the text which will appear in the prompt box by default.
    By default, standard dialog box styling will be used.
    If the variable Global.promptStyle is set to None,  the prompt will be styled using CSS styling for the .dialogbox class.
    If desired, this can be overridden by setting up styling for the id #promptdialog.'''
    global promptdialog
    try:
        promptdialog.showquery(message, action, title, default)
    except NameError:
        promptdialog = PromptDialog()
        promptdialog.showquery(message, action, title, default)

colourpickerdialog = None
fileopendialog = None
filesavedialog = None
logindialog = None
usernamedialog = None
currentuser = None
imagefromsvg = None
