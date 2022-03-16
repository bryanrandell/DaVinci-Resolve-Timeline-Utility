#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Timeline Utility. Requires DaVinci Resolve Studio 17
# Copyright (c) 2020 Bryan Randell

# import DaVinciResolveScript
#try:
#    import DaVinciResolveScript as dvr
#    resolve = dvr.scriptapp('Resolve')
#except:
# from python_utils.python_get_resolve import GetResolve
# resolve = GetResolve()

# from export_timeline_audio_sync import timeline_sync_export
import subprocess

from python_utils.all_utils_davinci import timeline_sync_export, delete_useless_sound_tracks, \
    copy_grade_current_trackItem_to_all_item_in_current_timeline, rename_rendered_files_with_meta, \
    create_timelines_by_reel_in_current_folder, prepare_video_item_to_frameio

def write_to_clipboard(output):
    process = subprocess.Popen(
        'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
    process.communicate(output.encode('utf-8'))


def add_popup_window(popup_string):
    # ui IDs
    dialogID = "com.blackmagicdesign.resolve.dialog"
    buttonID = 'Button_OK'

    dialog = dispatcher.AddWindow({'ID': dialogID,
                                   'Geometry': [100, 100, 300, 200],
                                   'WindowTitle': "Dialog",
                                   "WindowFlags" : {"Window" : True, "WindowStaysOnTopHint" : True},},
                                  ui.VGroup([ui.Label({'Text': popup_string,
                                                       'Weight': 0.2,
                                                       'Font': ui.Font({'Family': "Times New Roman"})}),
                                             ui.HGroup({'Weight': 0.1},[ ui.Button({'ID': buttonID, 'Text': 'OK',})])]))

    def OnClosedialog(ev):
        dialog.Hide()

    dialog.On[dialogID].Close = OnClosedialog
    dialog.On[buttonID].Clicked = OnClosedialog
    dialog.Show()
    # dispatcher.RunLoop()
    return dialog, dialog.GetItems()


def add_popup_window_with_choice(popup_string):
    # ui IDs
    dialogID = "com.blackmagicdesign.resolve.dialog"
    button_okID = 'Button_OK'
    button_cancelID = "Button_Cancel"



    dialog = dispatcher.AddWindow({'ID': dialogID, 'Geometry': [100, 100, 300, 200], 'WindowTitle': "Dialog", "WindowFlags" : {"Window" : True, "WindowStaysOnTopHint" : True},},
                                  ui.VGroup({'Weight': 0.2},[
                                  ui.Label({'Text': popup_string,
                                            'Weight': 0.3,
                                            'Font': ui.Font({'Family': "Times New Roman"})}),
                                  ui.HGroup({'Weight': 0.1},[
                                  ui.Button({'ID': button_okID, 'Text': 'OK', }),
                                  ui.Button({'ID': button_cancelID, 'Text': 'Cancel',})
                                  ])]))
    def OnClosedialog(ev):
        dialog.Hide()


    def OnClickOk(ev):
        dialog.Hide()
        number_of_sound_clip_delete = delete_useless_sound_tracks()
        _, _ = add_popup_window("Delete {} Sound Clip".format(number_of_sound_clip_delete))



    dialog.On[dialogID].Close = OnClosedialog
    dialog.On[button_cancelID].Clicked = OnClosedialog
    dialog.On[button_okID].Clicked = OnClickOk
    dialog.Show()
    # dispatcher.RunLoop()
    return dialog, dialog.GetItems()

def get_dictionary_timeline_by_day():
    dict = {}
    for day_folder in current_project_root_folder.GetSubFolderList():
        if day_folder.GetName().startswith('DAY'):
            for item in day_folder.GetClipList():
                if item.GetClipProperty()['Type'] == 'Timeline':
                    dict[item.GetName()] = day_folder.GetName()
    return dict

#todo too long to loop over a big project, not usable yet
def get_timeline_day_folder(timeline_item):
    root = current_project_mediapool.GetRootFolder()
    for day_folder in root.GetSubFolderList():
        if day_folder.GetName().startswith('DAY'):
            for item in day_folder.GetClipList():
                if timeline_item.GetName() == item.GetName() and item.GetClipProperty()['Type'] == 'Timeline':
                    return day_folder.GetName()


# Row Creation
def list_row_creation(current_project, tree_item, tree_timelineID, number_of_item_to_show = 50):
    global dict_timeline_by_day
    dict_timeline_by_day = get_dictionary_timeline_by_day()
    # todo make this variable modifialable by an edit line

    for timeline_index in range(current_project.GetTimelineCount()):
        #todo replace this by an edit line for choosing the number of timeline to show
        if timeline_index < (current_project.GetTimelineCount() - number_of_item_to_show):
            continue
        item_row = tree_item[tree_timelineID].NewItem()
        item_row.Text[0] = '{:03d}'.format(timeline_index + 1)
        item_row.Text[1] = '{}'.format(current_project.GetTimelineByIndex(timeline_index + 1).GetName())
        item_row.Text[2] = '{:03d}'.format(len(current_project.GetTimelineByIndex(timeline_index + 1).GetItemListInTrack('Video', 1)))
        item_row.Text[3] = '{}/{}'.format(current_project.GetTimelineByIndex(timeline_index + 1).GetSetting('timelineResolutionWidth'),
                                          current_project.GetTimelineByIndex(timeline_index + 1).GetSetting('timelineResolutionHeight'))
        item_row.Text[4] = "{}".format(current_project.GetTimelineByIndex(timeline_index + 1).GetSetting('timelineFrameRate'))
        item_row.Text[5] = "{}".format(current_project.GetTimelineByIndex(timeline_index + 1).GetEndFrame() -
                                       current_project.GetTimelineByIndex(timeline_index + 1).GetStartFrame())
        # item_row.Text[6] = dict_timeline_by_day[current_project.GetTimelineByIndex(timeline_index + 1).GetName()]

        tree_item[tree_timelineID].AddTopLevelItem(item_row)


def list_row_creation_filtered(current_project, tree_item, filter_string, tree_timelineID, number_of_item_to_show = 50):
    for timeline_index in range(current_project.GetTimelineCount()):
        #todo replace this by an edit line for choosing the number of timeline to show
        if timeline_index < (current_project.GetTimelineCount() - number_of_item_to_show):
            continue

        item_row = tree_item[tree_timelineID].NewItem()
        item_row.Text[0] = '{:03d}'.format(timeline_index + 1)
        item_row.Text[1] = '{}'.format(current_project.GetTimelineByIndex(timeline_index + 1).GetName())
        item_row.Text[2] = '{:03d}'.format(len(current_project.GetTimelineByIndex(timeline_index + 1).GetItemListInTrack('Video', 1)))
        item_row.Text[3] = '{}/{}'.format(current_project.GetTimelineByIndex(timeline_index + 1).GetSetting('timelineResolutionWidth'),
                                          current_project.GetTimelineByIndex(timeline_index + 1).GetSetting('timelineResolutionHeight'))
        item_row.Text[4] = "{}".format(current_project.GetTimelineByIndex(timeline_index + 1).GetSetting('timelineFrameRate'))
        item_row.Text[5] = "{}".format(current_project.GetTimelineByIndex(timeline_index + 1).GetEndFrame() -
                                       current_project.GetTimelineByIndex(timeline_index + 1).GetStartFrame())
        # item_row.Text[6] = dict_timeline_by_day[current_project.GetTimelineByIndex(timeline_index + 1).GetName()]

        if current_project.GetTimelineByIndex(timeline_index + 1).GetName().find(filter_string) != -1:
            tree_item[tree_timelineID].AddTopLevelItem(item_row)


project_manager = resolve.GetProjectManager()
current_project = project_manager.GetCurrentProject()
current_project_mediapool = current_project.GetMediaPool()
current_project_root_folder = current_project_mediapool.GetRootFolder()
print(current_project.GetName())

# some element IDs
winID = "com.blackmagicdesign.resolve.timeline_utility"	# should be unique for single instancing
line_edit_searchID = 'LineEditSearch'
line_edit_number_of_timelines = "LineEditNumberOfTimelines"
button_refreshID = 'Button_Refresh'
tree_timelineID = 'Tree_Timeline'
button_exportID = 'Button_Export'
button_createtimelineID = 'Button_Create_Timeline'
button_single_clip_export_hackID = "Button_Single_Clip_Export_Hack"
button_delete_useless_sound_clipID = "Button_Delete_Useless_Sound_Clip"
button_copy_grade_current_item_to_timelineID = "Button_Copy_Grade_Current_Item_To_Timeline"
# button_color_traceID = "Button_Color_Trace"
button_prepare_timeline_to_frameioID = "ButtonPrepareTimelineToFrameio"
tabID = 'TAB_ID'

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
main_window = dispatcher.AddWindow({'ID': winID,
                                    'Geometry': [100, 100, 600, 500],
                                    'WindowTitle': "DaVinci Resolve Timeline Utility", },
    ui.VGroup([
    # ui.VGroup([
    #   ui.TabBar({'ID' : tabID},
    #             ui.Stack({"ID" : "MyStack"}),
    #                 ui.Label({'Text': 'TAB BAR TEXT ',
    #                           'Weight': 0.1,
    #                           'Font': ui.Font({'Family': "Times New Roman", 'PixelSize': 24})}))
    #             ]
    #             ),

    ui.HGroup({ 'Weight': 0.1 }, [
      ui.LineEdit({'ID': line_edit_searchID, 'Text': '',
                   'PlaceholderText': 'Filter Timelines by Name',
                   'Events': {'EditingFinished' : True}}),
      ui.Button({'ID': button_refreshID, 'Text': 'Refresh List'},)
      ]),
    ui.HGroup({ 'Weight': 0.1 }, [
      ui.Label({'Text': 'Timeline List ',
                'Weight': 0.1,
                'Font': ui.Font({'Family': "Times New Roman", 'PixelSize': 24})}),
      ui.Label({'Text': 'Timeline List ',
                'Weight': 0.1,
                'Font': ui.Font({'Family': "Times New Roman", 'PixelSize': 14})}),
      ui.LineEdit({'ID': line_edit_number_of_timelines, 'Text': '50',
                     'PlaceholderText': 'Show X Timeline',
                     'Events': {'EditingFinished': True}}),
        ]),
      ui.Tree({'ID': tree_timelineID,
               'SortingEnabled': True,
               'Events' : {'ItemDoubleClicked': True, 'ItemClicked': True}, }),

    ui.HGroup({ 'Weight': 0.1 }, [
      ui.Button({'ID': button_exportID, 'Text': 'Export And Rename Clip With Meta'},),
      ui.Button({'ID': button_createtimelineID, 'Text': 'Create Timelines from current folder'},)]),
    ui.HGroup({ 'Weight': 0.1 }, [
      ui.Button({'ID': button_single_clip_export_hackID, 'Text': 'Export Single Clip Hack'},),
      ui.Button({'ID': button_delete_useless_sound_clipID, 'Text': 'Delete clips keep Only 2 firsts tracks'},)
      ]),
    ui.HGroup({'Weight': 0.1}, [
        ui.Button({'ID': button_copy_grade_current_item_to_timelineID, 'Text': 'Copy Current Grade To Timeline'}, ),
        ui.Button({'ID': button_prepare_timeline_to_frameioID, 'Text': 'Prepare Timeline To FrameIO'}, )
    ])
    ]))


# Tree Item definition
main_window_item = main_window.GetItems()
# main_window.SetPaletteColor(100,10,20)
# main_window_item[tabID].AddTab('test')
# main_window_item[tabID].AddTab('test1')
# main_window_item[tabID].AddTab('test2')

# main_window_item[tabID]

# Header/Column Creation
column_header = main_window_item[tree_timelineID].NewItem()
column_header.Text[0] = 'Index'
column_header.Text[1] = 'Name'
column_header.Text[2] = 'Number of Video Clips'
column_header.Text[3] = 'Resolution'
column_header.Text[4] = 'Frame Rate'
column_header.Text[5] = 'Lenght in Frames'
# column_header.Text[6] = 'Shooting Day'



main_window_item[tree_timelineID].SetHeaderItem(column_header)
main_window_item[tree_timelineID].ColumnCount = 6
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
    number_of_item_to_show = int(main_window_item[line_edit_number_of_timelines].Text)
    main_window_item[tree_timelineID].Clear()
    # main_window_item[tree_timelineID].Update()
    list_row_creation_filtered(current_project,
                               main_window_item,
                               main_window_item[line_edit_searchID].Text,
                               tree_timelineID,
                               number_of_item_to_show)
    print('List Refreshed')

# def OnClickFilter(ev):
#     print(tree_item['LineEditSearch'].SelectedText())

def OnTextChanged(ev):
    # print('test has changed')
    main_window_item[tree_timelineID].Clear()
    number_of_item_to_show = int(main_window_item[line_edit_number_of_timelines].Text)
    list_row_creation_filtered(current_project,
                               main_window_item,
                               main_window_item[line_edit_searchID].Text,
                               tree_timelineID,
                               number_of_item_to_show)

def OnEditFinishedItemToShow(ev):
    main_window_item[tree_timelineID].Clear()
    number_of_item_to_show = int(main_window_item[line_edit_number_of_timelines].Text)
    list_row_creation_filtered(current_project,
                               main_window_item,
                               main_window_item[line_edit_searchID].Text,
                               tree_timelineID,
                               number_of_item_to_show)

def OnClickTree(ev):
    # print(main_window_item[tree_timelineID].CurrentItem().Text[0])
    current_project.SetCurrentTimeline(current_project.GetTimelineByIndex(int(main_window_item[tree_timelineID].CurrentItem().Text[0])))

def OnDoubleClickTree(ev):
    write_to_clipboard(main_window_item[tree_timelineID].CurrentItem().Text[1])
    # print('double clicked')


def OnClickExport(ev):
    print('exporting timeline...')
    # directory = fusion.RequestDir('C:\\')
    # print(directory)
    # job_ready_count = timeline_sync_export(dvr)
    job_ready_num = rename_rendered_files_with_meta(resolve)

    if job_ready_num == 0:
        _, _ = add_popup_window("Didn't find any Job Ready in the Render Queue")
    else:
        _, _ = add_popup_window('Timeline successfully exported')

def OnClickCreateTimeline(ev):
    num_timeline_created = create_timelines_by_reel_in_current_folder(resolve)
    if num_timeline_created == 0:
        _, _ = add_popup_window("Didn't create any timeline")
    else:
        _, _ = add_popup_window('Create {} Timeline'.format(num_timeline_created))

def OnClickExportSingleClipHack(ev):
    job_ready_count = timeline_sync_export(resolve)
    print("export hack done with {} job done".format(job_ready_count))

def OnClickDeleteUselessSoundTracks(ev):
    _, _ = add_popup_window_with_choice("Are You sure you want to delete useless sound clips ?")


def OnClickCopyCurrentGradeToTimeline(ev):
    copy_grade_current_trackItem_to_all_item_in_current_timeline()

def OnClickPrepareTimelineToFrameio(ev):
    prepare_video_item_to_frameio(current_project.GetCurrentTimeline())

def OnClickExplorer(ev):
    directory = fusion.RequestDir('C:\\')
    print(directory)

# assign event handlers
main_window.On[winID].Close = OnClose
#todo find how this works
main_window.On[line_edit_searchID].EditingFinished = OnTextChanged
main_window.On[line_edit_number_of_timelines].EditingFinished = OnEditFinishedItemToShow
main_window.On[tree_timelineID].ItemClicked = OnClickTree
main_window.On[tree_timelineID].ItemDoubleClicked = OnDoubleClickTree
main_window.On[button_refreshID].Clicked = OnClickRefresh
main_window.On[button_exportID].Clicked = OnClickExport
main_window.On[button_createtimelineID].Clicked = OnClickCreateTimeline
main_window.On[button_single_clip_export_hackID].Clicked = OnClickExportSingleClipHack
main_window.On[button_delete_useless_sound_clipID].Clicked = OnClickDeleteUselessSoundTracks
main_window.On[button_copy_grade_current_item_to_timelineID].Clicked = OnClickCopyCurrentGradeToTimeline
main_window.On[button_prepare_timeline_to_frameioID].Clicked = OnClickPrepareTimelineToFrameio

# Main dispatcher loop
main_window.Show()
dispatcher.RunLoop()
