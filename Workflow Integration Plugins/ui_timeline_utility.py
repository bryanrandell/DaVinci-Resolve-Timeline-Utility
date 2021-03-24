#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Timeline Utility. Requires DaVinci Resolve Studio 17
# Copyright (c) 2020 Bryan Randell

import sys

# import DaVinciResolveScript
#try:
#    import DaVinciResolveScript as dvr
#    resolve = dvr.scriptapp('Resolve')
#except:
#    from python_utils.python_get_resolve import GetResolve
#    resolve = GetResolve()

from python_utils.export_timeline_audio_sync import timeline_sync_export

def add_popup_window(popup_string):
    # ui IDs
    dialogID = "com.blackmagicdesign.resolve.dialog"
    buttonID = 'Button_OK'

    dialog = dispatcher.AddWindow({'ID': dialogID, 'Geometry': [100, 100, 300, 200], 'WindowTitle': "Dialog", "WindowFlags" : {"Window" : True, "WindowStaysOnTopHint" : True},},
                                  ui.VGroup([
                                  ui.Label({'Text': popup_string,
                                            'Weight': 0.2,
                                            'Font': ui.Font({'Family': "Times New Roman"})}),
                                  ui.HGroup({'Weight': 0.1},[
                                  ui.Button({'ID': buttonID, 'Text': 'OK',})
                                  ])]))
    def OnClosedialog(ev):
        dialog.Hide()

    dialog.On[dialogID].Close = OnClosedialog
    dialog.On[buttonID].Clicked = OnClosedialog
    dialog.Show()
    # dispatcher.RunLoop()
    return dialog, dialog.GetItems()


# Row Creation
def list_row_creation(current_project, tree_item, tree_timelineID):
    for timeline_index in range(current_project.GetTimelineCount()):
        item_row = tree_item[tree_timelineID].NewItem()
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
        tree_item[tree_timelineID].AddTopLevelItem(item_row)


def list_row_creation_filtered(current_project, tree_item, filter_string, tree_timelineID):
    for timeline_index in range(current_project.GetTimelineCount()):
        item_row = tree_item[tree_timelineID].NewItem()
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
            tree_item[tree_timelineID].AddTopLevelItem(item_row)


project_manager = resolve.GetProjectManager()
current_project = project_manager.GetCurrentProject()
print(current_project.GetName())

# some element IDs
winID = "com.blackmagicdesign.resolve.timeline_utility"	# should be unique for single instancing
line_edit_searchID = 'LineEditSearch'
button_refreshID = 'Button_Refresh'
tree_timelineID = 'Tree_Timeline'
button_exportID = 'Button_Export'

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
header = '<html><body><h1 style="horizontal-align:middle;">'
header = header + '<b>DaVinci Resolve Timeline Utility</b>'
header = header + '</h1></body></html>'


# define the window UI layout
main_window = dispatcher.AddWindow({'ID': winID, 'Geometry': [100, 100, 600, 500], 'WindowTitle': "DaVinci Resolve Timeline Utility", },
    ui.VGroup([
      ui.Label({'Text': header, 'Weight': 0.1, 'Font': ui.Font({'Family': "Times New Roman"})}),

    ui.HGroup({ 'Weight': 0.1 }, [
      ui.LineEdit({'ID': line_edit_searchID, 'Text': '', 'PlaceholderText': 'Filter Timelines by Name', }),
      ui.Button({'ID': button_refreshID, 'Text': 'Refresh List'},)
      ]),

      ui.Label({'Text': 'Timeline List', 'Weight': 0.1, 'Font': ui.Font({'Family': "Times New Roman", 'PixelSize': 24})}),
      ui.Tree({'ID': tree_timelineID, 'SortingEnabled': True, 'Events' : {'ItemDoubleClicked': True, 'ItemClicked': True}, }),

    ui.HGroup({ 'Weight': 0.1 }, [
      ui.Button({'ID': button_exportID, 'Text': 'Export Timeline as Individual clips Hack'},)
      ]),
    ui.Label({'Text': 'In order to export hack your timeline'
                })
    ]))


# Tree Item definition
main_window_item = main_window.GetItems()

# Header/Column Creation
column_header = main_window_item[tree_timelineID].NewItem()
column_header.Text[0] = 'Index'
column_header.Text[1] = 'Name'
column_header.Text[2] = 'Number of Video Clips'
column_header.Text[3] = 'Resolution'
column_header.Text[4] = 'Frame Rate'


main_window_item[tree_timelineID].SetHeaderItem(column_header)
main_window_item[tree_timelineID].ColumnCount = 5
main_window_item[tree_timelineID].ColumnWidth[0] = 100

list_row_creation(current_project, main_window_item, tree_timelineID)


# Functions for Event handlers
def OnClose(ev):
    dispatcher.ExitLoop()

def OnClickRefresh(ev):
    """
    Clear the timeline list and loop over timeline indexes
    :param ev:
    :return:
    """
    main_window_item[tree_timelineID].Clear()
    list_row_creation(current_project, main_window_item, tree_timelineID)
    print('List Refreshed')

# def OnClickFilter(ev):
#     print(tree_item['LineEditSearch'].SelectedText())

def OnTextChanged(ev):
    # print('test has changed')
    main_window_item[tree_timelineID].Clear()
    list_row_creation_filtered(current_project,
                               main_window_item,
                               main_window_item[line_edit_searchID].Text,
                               tree_timelineID)

def OnClickTree(ev):
    print(main_window_item[tree_timelineID].CurrentItem().Text[0])
    current_project.SetCurrentTimeline(current_project.GetTimelineByIndex(int(main_window_item[tree_timelineID].CurrentItem().Text[0])))

def OnClickExport(ev):
    print('exporting timeline...')
    # directory = fusion.RequestDir('C:\\')
    # print(directory)
    job_ready_count = timeline_sync_export(dvr)

    if job_ready_count == 0:
        _, _ = add_popup_window("Didn't find any Job Ready in the Render Queue")
    else:
        _, _ = add_popup_window('Timeline successfully exported')


def OnClickExplorer(ev):
    directory = fusion.RequestDir('C:\\')
    print(directory)

# assign event handlers
main_window.On[winID].Close = OnClose
main_window.On[line_edit_searchID].TextChanged = OnTextChanged
main_window.On[tree_timelineID].ItemClicked = OnClickTree
main_window.On[button_refreshID].Clicked = OnClickRefresh
# main_window.On['Button_Filter'].Clicked = OnClickFilter
main_window.On[button_exportID].Clicked = OnClickExport
# main_window.On['Tree'].ItemDoubleClicked = OnDoubleClickTree


# Main dispatcher loop
main_window.Show()
dispatcher.RunLoop()
