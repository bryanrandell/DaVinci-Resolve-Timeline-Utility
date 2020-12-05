#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Timeline Utility. Requires DaVinci Resolve Studio 17.
# Copyright (c) 2020 Bryan Randell

import sys

# import DaVinciResolveScript
try:
    import DaVinciResolveScript as dvr
    resolve = dvr.scriptapp('Resolve')
except:
    from python_utils.python_get_resolve import GetResolve
    resolve = GetResolve()

# Row Creation
def list_row_creation(current_project, tree_item):
    for timeline_index in range(current_project.GetTimelineCount()):
        item_row = tree_item['Tree_Timeline'].NewItem()
        item_row.Text[0] = '{}'.format(timeline_index + 1)
        item_row.Text[1] = '{}'.format(current_project.GetTimelineByIndex(timeline_index + 1).GetName())
        item_row.Text[2] = '{}'.format(len(current_project.GetTimelineByIndex(timeline_index + 1).GetItemListInTrack('Video', 1)))
        item_row.Text[3] = '{}/{}'.format(current_project.GetTimelineByIndex(timeline_index + 1).GetSetting('timelineResolutionWidth'),
                                          current_project.GetTimelineByIndex(timeline_index + 1).GetSetting('timelineResolutionHeight'))
        item_row.Text[4] = current_project.GetTimelineByIndex(timeline_index + 1).GetSetting('timelineFrameRate')
        print(item_row.Text[0])
        print(item_row.Text[1])
        print(item_row.Text[2])
        print(item_row.Text[3])
        print(item_row.Text[4])
        tree_item['Tree_Timeline'].AddTopLevelItem(item_row)


def list_row_creation_filtered(current_project, tree_item, filter_string):
    for timeline_index in range(current_project.GetTimelineCount()):
        item_row = tree_item['Tree_Timeline'].NewItem()
        item_row.Text[0] = '{}'.format(timeline_index + 1)
        item_row.Text[1] = '{}'.format(current_project.GetTimelineByIndex(timeline_index + 1).GetName())
        item_row.Text[2] = '{}'.format(len(current_project.GetTimelineByIndex(timeline_index + 1).GetItemListInTrack('Video', 1)))
        item_row.Text[3] = '{}/{}'.format(current_project.GetTimelineByIndex(timeline_index + 1).GetSetting('timelineResolutionWidth'),
                                          current_project.GetTimelineByIndex(timeline_index + 1).GetSetting('timelineResolutionHeight'))
        item_row.Text[4] = current_project.GetTimelineByIndex(timeline_index + 1).GetSetting('timelineFrameRate')
        print(item_row.Text[0])
        print(item_row.Text[1])
        print(item_row.Text[2])
        print(item_row.Text[3])
        print(item_row.Text[4])
        if current_project.GetTimelineByIndex(timeline_index + 1).GetName().lower().find(filter_string) != -1:
            tree_item['Tree_Timeline'].AddTopLevelItem(item_row)


project_manager = resolve.GetProjectManager()
current_project = project_manager.GetCurrentProject()
print(current_project.GetName())

# some element IDs
winID = "com.blackmagicdesign.resolve.test_ui"	# should be unique for single instancing

# calling DavinciResolve UI in Workflow Integration
ui = fusion.UIManager
dispatcher = bmd.UIDispatcher(ui)

# check for existing instance
main_window = ui.FindWindow(winID)
if main_window:
    main_window.Show()
    main_window.Raise()
    exit()

# otherwise, we set up a new window, with HTML header (using the Examples logo.png)
header = '<html><body><h1 style="vertical-align:middle;">'
header = header + '<b>DaVinci Resolve Timeline Utility</b>'
header = header + '</h1></body></html>'


# define the window UI layout
main_window = dispatcher.AddWindow({'ID': winID, 'Geometry': [100, 100, 600, 500], 'WindowTitle': "DaVinci Resolve Timeline Utility", },
    ui.VGroup([
      ui.Label({'Text': header, 'Weight': 0.1, 'Font': ui.Font({'Family': "Times New Roman"})}),

      ui.LineEdit({'ID': 'LineEditSearch', 'Text': '', 'PlaceholderText': 'Filter Timelines by Name', }),

      ui.Label({'Text': 'Timeline List', 'Weight': 0.1, 'Font': ui.Font({'Family': "Times New Roman"})}),
      ui.Tree({'ID': 'Tree_Timeline', 'SortingEnabled': True, 'Events' : {'ItemDoubleClicked': True, 'ItemClicked': True}, }),

      ui.HGroup({ 'Weight': 0.1 }, [
      ui.Button({'ID': 'Button_Refresh', 'Text': 'Refresh List'},)
      ])]))


# Tree Item definition
tree_item = main_window.GetItems()

# Header/Column Creation
column_header = tree_item['Tree_Timeline'].NewItem()
column_header.Text[0] = 'Index'
column_header.Text[1] = 'Name'
column_header.Text[2] = 'Number of Video Clips'
column_header.Text[3] = 'Resolution'
column_header.Text[4] = 'Frame Rate'


tree_item['Tree_Timeline'].SetHeaderItem(column_header)
tree_item['Tree_Timeline'].ColumnCount = 5
tree_item['Tree_Timeline'].ColumnWidth[0] = 100

list_row_creation(current_project, tree_item)


# Functions for Event handlers
def OnClose(ev):
    dispatcher.ExitLoop()

def OnClickRefresh(ev):
    """
    Clear the timeline list and loop over timeline indexes
    :param ev:
    :return:
    """
    tree_item['Tree_Timeline'].Clear()
    list_row_creation(current_project, tree_item)
    print('List Refreshed')

def OnClickFilter(ev):
    print(tree_item['LineEditSearch'].SelectedText())

def OnTextChanged(ev):
    print('test has changed')
    tree_item['Tree_Timeline'].Clear()
    list_row_creation_filtered(current_project, tree_item, tree_item['LineEditSearch'].Text)


def OnClickTree(ev):
    print(tree_item['Tree_Timeline'].CurrentItem().Text[0])
    current_project.SetCurrentTimeline(current_project.GetTimelineByIndex(int(tree_item['Tree_Timeline'].CurrentItem().Text[0])))


# assign event handlers
main_window.On[winID].Close = OnClose
main_window.On['Tree_Timeline'].ItemClicked = OnClickTree
main_window.On['Button_Refresh'].Clicked = OnClickRefresh
main_window.On['Button_Filter'].Clicked = OnClickFilter
main_window.On['LineEditSearch'].TextChanged = OnTextChanged
# main_window.On['Tree'].ItemDoubleClicked = OnDoubleClickTree


# Main dispatcher loop
main_window.Show()
dispatcher.RunLoop()
