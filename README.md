# Davinci-Resolve-Timeline-Utility

## Description
A plugin which opens a window with all the timeline for the current project listed, you can select a timeline inside Davinci by clicking into the list.
You can also filter the timelines by name. Can be helpfull when you have to manage a lot of timelines in a project.
I could implement a lot of over function, don't hesitate to ask, if you have some ideas.

## Needs Davinci Resolve 17

## Installation
If you never installed a Workflow Itegration Plugin in Davinci, 
put the folder Workflow Integration Plugin in "%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\" (On Windows) or 
"/Library/Application Support/Blackmagic Design/DaVinci Resolve" (on Mac OS) Not the User Library but the Library in Macintosh HD. If you have already a Workflow Integration Plugin folder,
put the "ui_timeline_utility.py" file and "python_utils" folder inside the latter.
Then finally restart Davinci Resolve if it was opened.

## Usage 
In Davinci Resolve go to Workspace > Workflow Integration click on ui_timeline_utility it will open a small window.
The "Export Single Clip Hack" button makes possible to export a timeline's clip individually with all the single clip option available, including the sound manually synced in the timeline and the timecode is copy in the metadata of the file thanks to ffmpeg (it's a workaround for know cause resolve scriptapp doesn't handles timecode in render for the moment).
Export single clip hack handles prores exports and mxf op-atom (didn't test yet on other format).

## Requirement
You need ffmpeg (version 5.0) installed, type "brew install ffmpeg" in the terminal on macos.
Or go to https://ffmpeg.org/download.html to get executable files for mac/linux or windows.
