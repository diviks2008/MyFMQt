# Files Manager MyFMQt_v8
## Description:
    MyFMQt_v8.py is a file manager with minimal functionality.
    The main feature is fast navigation through text, photo and video files with preview
    
## Software requirements:
    The application requires python3 to run.
    Run the following command to install the required dependencies:
    for Debian, Ubuntu:
    sudo apt install python3-pyqt5

## To run the application:
    1. Download MyFMQt_v8.py from the GitHub repository.
    2. Go to the folder where the file was downloaded.
    3. Run the following command in the console:
    python3 MyFMQt_v8.py

## Navigating with the mouse:
    1. Double-click the folder name - navigate to the selected folder.
    2. Double-click the file - opens the file in the default application.
    3. One click on a text file or picture - a preview of the file contents.
    4. Right-click on the address bar - call the folder selection context menu
    5. Right-click on the file list - call the file context menu
    6. Right-click on the text field - call the context menu

## Keyboard navigation:
    Up and Down arrow keys - move through the list
    Enter - go to the selected folder, or go to a new address specified in the address bar
    F1 - in the text field print help
    Ctrl+R - Refresh File List
    Alt+U - go to parent folder
    Delete - delete selected files

## Features:
    1. Column "Name" - by default sorting by name
    2. Column "Size" - if a folder, then this is Items/Dirs/Files in the folder
    3. Text file preview mode is limited to 300 lines.
       To read the full contents of a file, double click on the file name.
    4. To change the order of the columns:
       Grab the title with the mouse and drag it.
    5. Chmod - non-recursive change of access rights of selected items
    6. Chmod by maska - RECURSIVE change of access rights of selected elements
