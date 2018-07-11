# brywidgets
A collection of widgets for including in Brython projects.

To use, download the zip, and move the brywidgets folder into your own project folder.  Then just include `import brywidgets` in your brython file.  
(I use `import brywidgets as ws` to make references to the widgets shorter.)

So far, the following widgets are included:

## Buttons that open a dialog box

### ColourPickerButton, ColourPickerImageButton
These open a simple colour picker dialog. (This might become redundant if all browsers start supporting `<input type="color">`.)
```
ColourPickerButton(returnaction, label='', initialcolour=None, id=None)
```
This Button takes on the colour which is selected.  
Notes on parameters:  
`returnaction`: function to be called after a colour is selected.
This function takes two arguments: the colour selected, and the id of the button (which could be None).  
`initialcolour`: initial background colour of the button (in `rgb(R, G, B)` format).  If omitted the default colour (LightGrey) is used.
```
ColourPickerImageButton(icon, returnaction, id=None)
```
Notes on parameters:  
`icon`: the path to the image on the button.  
`returnaction`: function to be called after a colour is selected. This function takes one argument: the colour selected.

### FileOpenButton, FileSaveButton, FileSaveAsButton
These enable saving files on the server.  At present the files have to be converted into a string format before saving (eg using `pickle`).
```
FileOpenButton(returnaction, extlist=[], initialfolder='.', id=None)
```
Notes on parameters:  
`returnaction`: function to be called after the file is opened.
This function takes two arguments: the contents and the name of the file which was opened.  
`extlist`: a list of file extensions which should be displayed in the dialog.  If omitted, all files will be displayed.  
`initialfolder`: the path to the folder initially displayed in the dialog.
```
FileSaveAsButton(preparefile, returnaction=None, extlist=[], defaultextension=None, initialfolder='.', id=None)
```
Notes on parameters:  
`preparefile`: function which returns a string with the contents of the file to be saved. This function takes no arguments.  
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
These work as above, but require the user to log in before saving or opening a file.  The username system is simple: each user has a folder inside a folder called ```users``` to save their own files in.  Checking whether a username exists is simly a matter of checking whether a folder of that name exists.  This will be fine for up to a few thousand users, but won't scale beyond that.
```
UserFileOpenButton(returnaction, extlist=[], id=None)
UserFileSaveAsButton(preparefile, returnaction=None, extlist=[], defaultextension=None, id=None)
UserFileSaveButton(preparefile, returnaction=None, extlist=[], defaultextension=None, id=None)
```
For the parameters, see above.

### ImageFromSVGButton
Opens an OverlayPanel containing a png image converted from an SVG image, so that it can be downloaded or saved by right-clicking.
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
Notes on parameters:  
`choices`: a list of options.  
`onchange`: function to be called when the user chooses a different option.  Takes the change event as argument.  
`size`: number of choices to be displayed (for `ListBox`).  
`initialchoice`: index (counting from 0) of the initial choice.  

### InputBox
A standard ```<input>```, with a handler for when the Enter key is pressed.
```
InputBox(enterkeyaction, id=None)
```
Parameter:  
`enterkeyaction`: function to use if the Enter key is pressed. Takes the keypress event as argument.

## Containers for laying out content

### Notebook, NotebookPage
A Notebook is a collection of tabbed pages; click on a tab to switch from one page to another.
```
Notebook(pagelist)
NotebookPage(title, bgcolour, content=None, id=None)
```
Notes on parameters:  
`pagelist`: a list of `NotebookPages`.  
`title`: title of the page (which appears on its tab).  
`bgcolour`: background colour of the page (and also of its tab).  
`content`: optionally include content on the page at creation time, or else add it later.

### Panel
This is just a div with a default border and optional title.
```
Panel(items=None, title=None, id=None)
```
Notes on parameters:  
`items`: list of the contents of the panel.  
`title`: heading at the top of the panel.

### RowPanel, ColumnPanel
These organise the elements they contain in either a row or a column (using `display: flex` internally).
```
RowPanel(items=None, id=None)
ColumnPanel(items=None, id=None)
```

### GridPanel
These organise their contents ina grid of a specified size (using `display: grid` internally).
```
GridPanel(columns, rows, items=None, id=None)
```
Notes on parameters:  
`columns`, `rows`: size of the grid.  
`items`: list of the contents of the grid.
