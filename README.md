# brywidgets
A collection of widgets for including in Brython projects.

To use, download the zip, and move the brywidgets folder into your own project folder.  Then just include ```import brywidgets``` in your brython file.

(I use ```import brywidgets as ws``` to make references to the widgets shorter.)

So far, the following widgets are available:

## Buttons that open a dialog box

### ColourPickerButton, ColourPickerImageButton
These open a simple colour picker dialog. (This might become redundant if all browsers start supporting ```<input type="color">```.)

### FileOpenButton, FileSaveButton, FileSaveAsButton
These enable saving files on the server.  At present the files have to be converted into a string format before saving (eg using ```pickle```).

### UserFileOpenButton, UserFileSaveButton, UserFileSaveAsButton, LoginButton
These work as above, but require the user to log in before saving or opening a file.  The username system is simple: each user has a folder inside a folder called ```users``` to save their own files in.  Checking whether a username exists is simly a matter of checking whether a folder of that name exists.  This will be fine for up to a few thousand users, but won't scale beyond that.

### ImageFromSVGButton
Opens an overlay with containing a png image converted from an SVG image, so that it can be downloaded or saved by right-clicking.

## Other Buttons

### Button, ImageButton, ToggleButton, ToggleImageButton
These are fairly self-explanatory; a ToggleButton remains depressed when clicked, until clicked again (or raised elsewhere in code).

## Other Controls

### DropDown, ListBox
Choose an option from a list.

### InputBox
A standard ```<input>```, with an OnEnterKey handler.

## Containers for laying out content

### Notebook, NotebookPage
A Notebook is a collection of tabbed pages; click on a tab to switch from one page to another.

### Panel
This is just a div with a default border and optional title.

### RowPanel, ColumnPanel
These organise the elements they contain in either a row or a column (using ```display: flex``` internally).

### GridPanel
These organise their contents ina grid of a specified size (using ```display: grid``` internally).

