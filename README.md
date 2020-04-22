# brywidgets

## New in version 0.2.0

There is now a "zero install" option available (see Introduction below). This means the project is no longer dependent on its own external CSS file.

There is also one new widget: a `spincontrol` (to provide a more consistent interface, since browsers vary greatly in how they handle `<input type="number">`). 

## Introduction

A collection of widgets for including in Brython projects.

For a demo, see [this page](http://mathsanswers.org.uk/oddments/brywidgets/demo.html), which illustrates most of the functionality.

To use, there are two options:

If you don't need to use the file saving/opening or user login features described in the final section below, the "zero install" option is to include a line in the `head` section of your html file (probably just after the lines which load brython itself):
```
<script src="https://cdn.jsdelivr.net/gh/andy31lewis/brywidgets@0.2.0/brywidgets.brython.js"></script>
```
Or if you do need those features, download the zip, and move the `brywidgets` and `users` folders into your own project folder. (If you wish, you can delete the user `demo` from within the `users` folder.)

In either case, just include `import brywidgets` in your brython file and you are ready to use the widgets in your code.  
(I use `import brywidgets as ws` to make references to the widgets shorter.)

So far, the following widgets are included:

## Containers for laying out content

### Notebook, NotebookPage
A Notebook is a collection of tabbed pages; click on a tab to switch from one page to another.
```
Notebook(pagelist=[], tabheight="2em", id=None)  
NotebookPage(title, bgcolour, content=None, tabwidth="10%", id=None)
```
Notes on parameters:  
`pagelist`: a list of `NotebookPages`.  
`title`: title of the page (which appears on its tab).  
`bgcolour`: background colour of the page (and also of its tab).  
`content`: optionally include content on the page at creation time, or else add it later.
`tabheight`, `tabwidth` The height of the tabs is automatically set to accomodate 1 line of text, but can be adjusted by specifying the parameter `tabheight` in CSS units.  
The width of each tab is automatically set to 10% (so that 10 tabs can be accommodated, but can be adjusted by setting the parameter `tabwidth` in CSS units, or setting it to `None`.

For external CSS styling, use classes `.notebook`, `.notebookpage` and `.notebooktabrow`, or give each page an id and use `#(pageid)` and `#(pageid)_tab`.

### Panel
This is just a div with a default border and optional title.
```
Panel(items=None, border="1px solid white", align=None, title=None, id=None)
```
Optional parameters:  
`items`: list of the contents of the panel.  
`border`: border of the panel, in CSS format (use `None` for no border, or to keep whatever is set in external CSS).  
`align`: text-align, in CSS format.  
`title`: heading at the top of the panel.

### RowPanel, ColumnPanel
These organise the elements they contain in either a row or a column (using `display: flex` internally).
```
RowPanel(items=None, id=None)
ColumnPanel(items=None, id=None)
```

### GridPanel
These organise their contents in a grid of a specified size (using `display: grid` internally).
```
GridPanel(columns, rows, items=None, id=None)
```
Notes on parameters:  
`columns`, `rows`: size of the grid.  
`items`: list of the contents of the grid.

## Buttons that open a dialog box

### ColourPickerButton, ColourPickerImageButton
These open a simple colour picker dialog. (This might become redundant if all browsers start supporting `<input type="color">`.)
```
ColourPickerButton(returnaction, label='', initialcolour=None, id=None)
```
This Button takes on the colour which is selected.  
Required parameter:  
`returnaction`: function to be called after a colour is selected.
This function takes two arguments: the colour selected, and the id of the button (which could be None).  
Optional parameters:  
`label`: Text on the button  
`initialcolour`: initial background colour of the button (in `rgb(R, G, B)` format).  If omitted the default colour `rgb(242, 241, 240)` is used.
```
ColourPickerImageButton(icon, returnaction, id=None)
```
Notes on parameters:  
`icon`: the path to the image on the button.  
`returnaction`: function to be called after a colour is selected. This function takes one argument: the colour selected.

### ImageFromSVGButton
Opens an OverlayPanel containing a png image converted from an SVG image, so that it can be copied or saved by right-clicking.
```
ImageFromSVGButton(svgimage, id=None)
```
Parameter:
`svgimage`: the image to be converted to png.

## Other Buttons

### Button, ImageButton, ToggleButton, ToggleImageButton
These are fairly self-explanatory; a ToggleButton remains depressed when clicked, until clicked again (or raised elsewhere in code).
```
Button(text, handler, bgcolour=None, tooltip=None, id=None)  
ImageButton(icon, handler, bgcolour=None, tooltip=None, id=None)  
ToggleButton(text, handler, bgcolour=None, tooltip=None, id=None)  
ToggleImageButton(icon, handler, bgcolour=None, tooltip=None, id=None)
```
Notes on parameters:  
`text`: Text of the button (could be empty string).  
`icon`: the path to the image on the button.  
`handler`:  Function to be called on click. This function takes the click event as argument.  
`bgcolour`: background colour of the button.  
`tooltip`: text displayed when hovering over the button.

## Other Controls

### DropDown, ListBox
Choose an option from a list. For a DropDown, only one is visible at first; for a ListBox all are shown unless the `size` parameter is used, in which case a scroll bar is used.
```
DropDown(choices, onchange, initialchoice=None, id=None)  
ListBox(choices, onchange, size=None, initialchoice=None, id=None)
```
Required parameters:  
`choices`: a list of options.  
`onchange`: function to be called when the user chooses a different option.  Takes the change event as argument.  
Optional parameters:  
`size`: number of choices to be displayed (for `ListBox`).  
`initialchoice`: index (counting from 0) of the initial choice.  

For external CSS styling use class `.dropdown` or `.listbox`, or give the control an id and use #(id).

### InputBox
A standard ```<input>```, with a handler for when the Enter key is pressed.
```
InputBox(enterkeyaction, id=None)
```
Required parameter:  
`enterkeyaction`: function to be called if the Enter key is pressed. Takes the keypress event as argument.  
Optional parameter:  
`style`: dictionary containing any CSS styling required.

###SpinControl
Control showning an initial (integer) value, and buttons to increase or decrease it.  
```
SpinControl(initialvalue, minvalue, maxvalue, action, id=None)
```
Required parameters:  
`initialvalue`: initial value of the control.  
`minvalue`, `maxvalue`: values beyond which the control cannot be decreased or increased.  
`action`: function to be called when the value is changed. Takes one parameter, the current value of the control.

## The following widgets are not available with the "zero install" option - see Introduction above

### FileOpenButton, FileSaveButton, FileSaveAsButton
These enable saving files on the server.  At present the files have to be converted into a string format before saving (eg using `pickle`).
```
FileOpenButton(returnaction, extlist=[], initialfolder='.', id=None)
```
Required parameters:  
`returnaction`: function to be called after the file is opened.
This function takes two arguments: the contents and the name of the file which was opened.  
Optional parameters:  
`extlist`: a list of file extensions which should be displayed in the dialog.  If omitted, all files will be displayed.  
`initialfolder`: the path to the folder initially displayed in the dialog.
```
FileSaveAsButton(preparefile, returnaction=None, extlist=[], defaultextension=None, initialfolder='.', id=None)
```
Required parameter:  
`preparefile`: function which returns a string with the contents of the file to be saved. This function takes no arguments.  
Optional parameters:  
`returnaction`: function to be called after the file is saved.
This function takes one argument: the name of the file which was opened.  
`defaultextension`: extension which will be appended to the filename given if not already present.  
`initialfolder`: the path to the folder initially displayed in the dialog.
```
FileSaveButton(preparefile, returnaction=None, extlist=[], defaultextension=None, initialfolder='.', id=None)
```
If the currently open file already has a name, this button re-saves the file with that name.  Otherwise it opens a dialog for saving a file.  
For parameters, see `FileSaveAsButton`.

### UserFileOpenButton, UserFileSaveButton, UserFileSaveAsButton, LoginButton
These work as above, but require the user to log in before saving or opening a file.  The username system is simple: each user has a folder inside a folder called ```users``` to save their own files in.  Checking whether a username exists is simply a matter of checking whether a folder of that name exists.  This will be fine for up to a few thousand users, but won't scale beyond that.
```
UserFileOpenButton(returnaction, extlist=[], id=None)
UserFileSaveAsButton(preparefile, returnaction=None, extlist=[], defaultextension=None, id=None)
UserFileSaveButton(preparefile, returnaction=None, extlist=[], defaultextension=None, id=None)
```
For the parameters, see above.

