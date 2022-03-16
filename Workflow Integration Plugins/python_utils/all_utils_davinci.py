#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Timeline Utility. Requires DaVinci Resolve Studio 17
# Copyright (c) 2020 Bryan Randell

# from python_get_resolve import GetResolve
import os
import time
import shutil

import dictionary as dictionary

from .ffmpeg_command_line import runFFmpeg, buildFFmpegCommand
"""
video_change_timecode_dict["input_file"],
"-metadata",
video_change_timecode_dict["timecode"],
"-codec",
"copy",
video_change_timecode_dict["output_file"],
"&&",
video_change_timecode_dict["output_file"],
video_change_timecode_dict["input_file"]
"""

video_change_timecode_dict = {}

# try:
#     import DaVinciResolveScript as dvr
#     resolve = dvr.scriptapp('Resolve')
# except:
#     from python_get_resolve import GetResolve
#     resolve = GetResolve()

def prepare_video_item_to_frameio(current_timeline):
    current_timeline_list_items = current_timeline.GetItemListInTrack('Video', 1)
    for item in current_timeline_list_items:
        if item.GetMediaPoolItem().GetClipProperty()['Resolution'] == "6054x3192"or \
                item.GetMediaPoolItem().GetClipProperty()['Resolution'] == "6052x3192":
            item.SetProperty("CropTop", 25.0)
            item.SetProperty("CropBottom", 25.0)
            print("{} cropped".format(item.GetName()))
        elif item.GetMediaPoolItem().GetClipProperty()['Resolution'] == "6048x4032":
            item.SetProperty("ZoomX", 113.0)
            item.SetProperty("ZoomY", 113.0)
            print("{} resized".format(item.GetName()))
        else:
            print("{} has unknown resolution".format(item.GetName()))
            print("resolution  = {}".format(item.GetMediaPoolItem().GetClipProperty()['Resolution']))


def copy_grade_current_trackItem_to_all_item_in_current_timeline(resolve):
    resolve = resolve
    resolve.OpenPage('color')
    project_manager = resolve.GetProjectManager()
    current_project = project_manager.GetCurrentProject()
    timeline = current_project.GetCurrentTimeline()
    track_item_list = timeline.GetItemListInTrack('video', 1)
    current_video_item = timeline.GetCurrentVideoItem()
    return current_video_item.CopyGrades(track_item_list)


def delete_useless_sound_tracks(resolve):
    resolve = resolve
    resolve.OpenPage('media')
    project_manager = resolve.GetProjectManager()
    current_project = project_manager.GetCurrentProject()
    clip_mediapool = current_project.GetMediaPool()
    current_folder = clip_mediapool.GetCurrentFolder()
    clip_list = current_folder.GetClipList()
    clip_list_to_delete = []
    for clip in clip_list:
        if clip.GetName().lower().endswith('wav'):
            if clip.GetName().split('.')[0].endswith(('01', '02')):
                #print('Clip Not to delete => ', clip.GetName())
                continue

            else:
                clip_list_to_delete.append(clip)
                #print('Clip to delete => ', clip.GetName().split('.')[0], clip.GetName().split('.')[0].endswith(('01', '02')))
        else:
            #print('Found no Sound Clip to delete => ', clip.GetName())
            continue

    print(len(clip_list_to_delete))
    clip_mediapool.DeleteClips(clip_list_to_delete)

    return len(clip_list_to_delete)

# todo implement a different solution to extract scene and clap from davinci clip meta
def create_new_filename_with_sound_meta(clip):

    scene_letters = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "O", "P", "Q", "R", "S", "T", "U",
                     "V", "W", "X", "Y", "Z", " ")
    if clip.GetMediaPoolItem().GetClipProperty()['Scene'] != "":

    #todo non logical, useless logic for clap variable
        if any(letter in clip.GetMediaPoolItem().GetClipProperty()['Scene'] for letter in scene_letters):
            scene = clip.GetMediaPoolItem().GetClipProperty()['Scene'][:4]
            if len(clip.GetMediaPoolItem().GetClipProperty()['Scene']) < 6:
                clap = clip.GetMediaPoolItem().GetClipProperty()['Scene'][4:]
            elif len(clip.GetMediaPoolItem().GetClipProperty()['Scene']) > 6:
                clap = clip.GetMediaPoolItem().GetClipProperty()['Scene'][4:]
            else:
                clap = clip.GetMediaPoolItem().GetClipProperty()['Scene'][4:]

        else:
            scene = clip.GetMediaPoolItem().GetClipProperty()['Scene'][:3]
            if len(clip.GetMediaPoolItem().GetClipProperty()['Scene']) < 6:
                clap = clip.GetMediaPoolItem().GetClipProperty()['Scene'][3:]
            elif len(clip.GetMediaPoolItem().GetClipProperty()['Scene']) > 6:
                clap = clip.GetMediaPoolItem().GetClipProperty()['Scene'][3:]
            else:
                clap = clip.GetMediaPoolItem().GetClipProperty()['Scene'][3:]

        take = clip.GetMediaPoolItem().GetClipProperty()['Take'][1:]
        camera = clip.GetName()[0]

        # using : columns to replace / in the filepath
        new_filename = "{}:{}-{} CAM_{}".format(scene, clap, take, camera)

    else:
        new_filename = clip.GetName().split('.')[0]

    return new_filename

def create_job_status_dict(current_project):
    job_id_statut_dict = {}
    for index in current_project.GetRenderJobs():
        job_id_statut_dict[current_project.GetRenderJobs()[index]['JobId']] = current_project.GetRenderJobStatus(current_project.GetRenderJobs()[index]['JobId'])
    return job_id_statut_dict

def get_timelines_list(project_object):
    timelines_list = []
    for timeline_index in range(int(project_object.GetTimelineCount())):
        timelines_list.append(project_object.GetTimelineByIndex(float(timeline_index + 1)))
    return timelines_list


def get_timeline_from_current_job(timelines_list, current_job):
    for timeline in timelines_list:
        if timeline.GetName() == current_job['TimelineName']:
            return timeline




def timeline_sync_export(resolve):
    resolve = resolve

    project_manager = resolve.GetProjectManager()
    current_project = project_manager.GetCurrentProject()

    timelines_list = get_timelines_list(current_project)
    job_id_statut_dict = create_job_status_dict(current_project)
    dictionary_filename_with_tc = {}
    job_ready_count = 0
    for job_id in job_id_statut_dict:
        for current_job in current_project.GetRenderJobList():
            if current_job['JobId'] == job_id:
                print(current_job['JobId'], job_id)
                if 'Ready' in job_id_statut_dict[job_id]['JobStatus']:
                    job_ready_count += 1
                    # current_job = current_project.GetRenderJobs(job_id)[job_ready_count]
                    print('CURRENT JOBS ', current_project.GetRenderJobs(job_id))
                    current_job_timeline = get_timeline_from_current_job(timelines_list, current_job)
                    print('TIMELINE CURRENT ', current_job_timeline.GetName())
                    is_current_timeline_is_current_job = current_project.SetCurrentTimeline(current_job_timeline)

                    if is_current_timeline_is_current_job == False:
                        print("Cannot make job timeline the Current timeline")
                        break

                    # todo find a better code to make a sub directory
                    # sub_folder = "{}/{}".format(current_project.GetRenderJobs()[1]['TargetDir'], "CAMERA-{}".format(timeline.GetName()[0]))
                    sub_folder = "{}/{}".format(current_job['TargetDir'], current_job_timeline.GetName())


                    if not os.path.exists(sub_folder):
                        os.mkdir(sub_folder)

                    current_project.SetCurrentRenderMode(1)
                    current_project.SetRenderSettings({"SelectAllFrames": False,
                                                    "TargetDir": sub_folder})

                    job_id_timeline_list = []
                    for nb_item in current_job_timeline.GetItemsInTrack('Video', 1):
                        if nb_item == 1:
                            mark_in = current_job_timeline.GetStartFrame()
                        else:
                            mark_in = current_job_timeline.GetItemsInTrack('Video', 1)[nb_item - 1].GetEnd()
                        mark_out = current_job_timeline.GetItemsInTrack('Video', 1)[nb_item].GetEnd() - 1


                        custom_temp_name = create_new_filename_with_sound_meta(current_job_timeline.GetItemsInTrack('Video', 1)[nb_item]) + "_temp_"
                        custom_name_extension = custom_temp_name + "." + get_file_extension_from_job_settings(current_job)
                        custom_name_path = os.path.join(sub_folder, custom_name_extension)
                        dictionary_filename_with_tc[custom_name_path] = current_job_timeline.GetItemsInTrack('Video', 1)[nb_item].GetMediaPoolItem().GetClipProperty()['Start TC']
                        current_project.SetRenderSettings()
                        current_project.SetRenderSettings({"MarkIn": mark_in,
                                                        "MarkOut": mark_out,
                                                       "CustomName": custom_temp_name})
                        job_id_timeline = current_project.AddRenderJob()
                        job_id_timeline_list.append(job_id_timeline)

                    jobs = current_project.GetRenderJobs()

                    current_project.StartRendering(job_id_timeline_list)


                    while current_project.IsRenderingInProgress():
                        time.sleep(1)


                    print('Finished Rendering {}'.format(current_job_timeline.GetName()))

                    # Deleting all the temporary jobs
                    for job_id_to_delete in job_id_timeline_list:
                        current_project.DeleteRenderJob(job_id_to_delete)

                    current_project.DeleteRenderJob(job_id)
                    print("Done JOB {}".format(job_id))

                    # run ffmpeg to copy timecode from mediapool file to the render file
                    for temp_video_path in dictionary_filename_with_tc:
                        runFFmpeg(buildFFmpegCommand(temp_video_path, dictionary_filename_with_tc[temp_video_path]))
                        print("Copy TC from original video at path {}  the transcoded".format(temp_video_path))
                        # suppress the temporary file create with render to keep only the video file with good timecode
                        if os.path.exists(temp_video_path):
                            os.remove(temp_video_path)
                        else:
                            print("The file {} does not exist".format(temp_video_path))

                else:
                    print('Job {} is Not Ready'.format(job_id))

    if job_ready_count == 0:
        print("Didn't find any Job Ready in the Render Queue")
    else:
        print(dictionary_filename_with_tc)

    return job_ready_count



def apply_lut_to_all_item_in_timeline(timeline, lut_path):
    item_list = timeline.GetItemListInTrack('Video', 1)
    for item in item_list:
        # item.SetLUT(1, '_THE REUNION/LUT_2021_NUIT.cube')
        item.SetLUT(0, lut_path)

def get_file_extension_from_job_settings(current_job):
    if current_job['VideoFormat'] == 'QuickTime':
        return 'mov'
    elif current_job['VideoFormat'] == 'Avi':
        return 'avi'
    elif current_job['VideoFormat'] == 'MP4':
        return 'mp4'
    elif current_job['VideoFormat'] == 'MXF OP-Atom':
        return 'mxf'
    elif current_job['VideoFormat'] == 'MXF OPA1':
        return 'mxf'
    else:
        # return print('No known extension file found')
        return None


def get_timelines_list(project_object):
    timelines_list = []
    for timeline_index in range(int(project_object.GetTimelineCount())):
        timelines_list.append(project_object.GetTimelineByIndex(float(timeline_index + 1)))
    return timelines_list


def get_timeline_from_current_job(timelines_list, current_job):
    for timeline in timelines_list:
        if timeline.GetName() == current_job['TimelineName']:
            return timeline

def create_new_filename_upgrade(clip, file_extension):

    scene = clip.GetMediaPoolItem().GetClipProperty()['Scene'][:3]
    clap = clip.GetMediaPoolItem().GetClipProperty()['Scene'][3:]
    take = clip.GetMediaPoolItem().GetClipProperty()['Take'][1:]
    camera = clip.GetName()[0]

    new_filename = "{}:{}-{} CAM_{}.{}".format(scene, # using : columns to replace / in the filepath
                                     clap,
                                     take,
                                     camera,
                                     file_extension
                                     )

    return new_filename


def rename_rendered_files_with_meta(resolve):
    resolve = resolve
    project_manager = resolve.GetProjectManager()
    current_project = project_manager.GetCurrentProject()
    print("Current Project is {}".format(current_project.GetName()))
    resolve.OpenPage('deliver')
    job_ready_num = 0
    jobs = current_project.GetRenderJobs()
    timelines_list = get_timelines_list(current_project)
    for job in jobs:
        job_id = jobs[job]['JobId']
        job_status = current_project.GetRenderJobStatus(job_id)['JobStatus']
        job_timeline = jobs[job]['TimelineName']
        if job_status == 'Ready': # and job_timeline[-7:] == 'FRAMEIO':
            print(job_status)
            job_ready_num += 1
    # if len(timelines_list) > 0 and len(jobs) > 0:
    #     print("Starting to render {} jobs with {} timelines".format(len(timelines_list), len(jobs)))
    #     for job_index in jobs:
            current_job = jobs[job]
    #         if "Cancelled" or "Complete" in current_project.GetRenderJobStatus(job_index):
    #             print("This job is not Ready, skipping it")
    #             continue
            file_extension = get_file_extension_from_job_settings(current_job)
            path_transcode = current_job['TargetDir']
            current_job_name = current_job['RenderJobName']
            current_project.StartRendering(job_id)

            print('Rendering {} Please Wait...'.format(current_job_name))
            while current_project.IsRenderingInProgress():
                time.sleep(1)
            print('Finished Rendering {}'.format(current_job_name))

            print('Starting to copy and renaming files from the metadata infos...')
            timeline_from_current_job = get_timeline_from_current_job(timelines_list, current_job)
            track_items = timeline_from_current_job.GetItemsInTrack('video', 1.0)

            for item in track_items:
                clip = track_items[item]

                new_filename = create_new_filename_upgrade(clip, file_extension)

                for _, _, files in os.walk(path_transcode):
                    for file in files:
                        if clip.GetName()[:-3] == file[:-3]:
                            shutil.copy(os.path.join(path_transcode, file), os.path.join(path_transcode, new_filename))
                            # os.rename(os.path.join(path_transcode, file), os.path.join(path_transcode, new_filename))

                print('Copy {}'.format(clip.GetName()))

            print('Finished with {}'.format(current_job_name))

        print('DONE')


    else:
        print("Found {} jobs with {} timelines".format(len(timelines_list), len(jobs)))

    return job_ready_num


def create_timelines_by_reel_in_current_folder(resolve):
    resolve = resolve
    project_manager = resolve.GetProjectManager()
    current_project = project_manager.GetCurrentProject()
    print("Current Project is {}".format(current_project.GetName()))
    resolve.OpenPage('media')
    mediapool = current_project.GetMediaPool()
    current_folder = mediapool.GetCurrentFolder()
    number_of_timelines_created = 0
    for sub_folder in current_folder.GetSubFolders():
        sub_folder_clip_list = current_folder.GetSubFolders()[sub_folder].GetClipList()
        num_of_clips_in_sub_folder = len(current_folder.GetSubFolders()[sub_folder].GetClipList())
        counter_clips_in_sub_folder = 1
        timeline_reel_dict = {}
        same_reel_clip_list = []
        # todo change this to put the previous inside the loop in case of an if statement cf-> pb with different paths
        previous_reel = sub_folder_clip_list[0].GetClipProperty()['File Path'].split("/")[-4]
        for clip in sub_folder_clip_list:
            reel = clip.GetClipProperty()['File Path'].split("/")[-4]

            if previous_reel == reel:

                same_reel_clip_list.append(clip)

            if previous_reel != reel:
                timeline_reel_dict[previous_reel] = same_reel_clip_list
                same_reel_clip_list = []
                same_reel_clip_list.append(clip)

            previous_reel = reel
            counter_clips_in_sub_folder += 1

            if counter_clips_in_sub_folder == num_of_clips_in_sub_folder:
                same_reel_clip_list.append(clip)
                timeline_reel_dict[previous_reel] = same_reel_clip_list

        if current_folder.GetSubFolders()[sub_folder].GetName().lower() == 'edit':
            for reel_name in timeline_reel_dict:
                mediapool.CreateTimelineFromClips(reel_name, timeline_reel_dict[reel_name])
                number_of_timelines_created += 1
                print(reel_name)

        elif current_folder.GetSubFolders()[sub_folder].GetName().lower() == 'frameio':
            for reel_name in timeline_reel_dict:
                mediapool.CreateTimelineFromClips("{}_FRAMEIO".format(reel_name[:4]), timeline_reel_dict[reel_name])
                number_of_timelines_created += 1
                print("{}_FRAMEIO".format(reel_name[:4]))

        else:
            print('Error, didnt find neither frameio nor edit folDer' )
            break

    return number_of_timelines_created


if __name__ == "__main__":
    timeline_sync_export()
