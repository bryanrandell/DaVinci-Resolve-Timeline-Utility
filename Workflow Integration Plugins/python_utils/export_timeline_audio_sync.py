#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Timeline Utility. Requires DaVinci Resolve Studio 17
# Copyright (c) 2020 Bryan Randell

# from python_get_resolve import GetResolve

import os
import time

try:
    import DaVinciResolveScript as dvr
    resolve = dvr.scriptapp('Resolve')
except:
    from python_utils.python_get_resolve import GetResolve
    resolve = GetResolve()


def create_job_status_dict(current_project):
    job_id_statut_dict = {}
    for index in current_project.GetRenderJobs():
        job_id_statut_dict[current_project.GetRenderJobs()[index]['JobId']] = current_project.GetRenderJobStatus(current_project.GetRenderJobs()[index]['JobId'])
    return job_id_statut_dict

def timeline_sync_export(bmd):

    resolve = bmd.scriptapp('Resolve')
    project_manager = resolve.GetProjectManager()
    current_project = project_manager.GetCurrentProject()


    # timeline = current_project.GetCurrentTimeline()
    # track_item = timeline_sync.GetItemsInTrack('Video', 1) #Only on video 1 track

    timeline = current_project.GetCurrentTimeline()
    clips = timeline.GetItemListInTrack('Video', 1)
    clip_mediapool = clips[0].GetMediaPoolItem()
    # for prop in clip_mediapool.GetClipProperty():
    #     print(prop, clip_mediapool.GetClipProperty()[prop])


    job_id_statut_dict = create_job_status_dict(current_project)

    job_ready_count = 0
    for job_id in job_id_statut_dict:
        if 'Ready' in job_id_statut_dict[job_id]['JobStatus']:
            job_ready_count += 1

            # todo find a better code to make a sub directory
            sub_folder = "{}/{}".format(current_project.GetRenderJobs()[1]['TargetDir'], timeline.GetName())
            if not os.path.exists(sub_folder):
                os.mkdir(sub_folder)

            current_project.SetCurrentRenderMode(1)
            current_project.SetRenderSettings({"SelectAllFrames": False,
                                            "TargetDir": sub_folder})

            job_id_timeline_list = []
            for nb_item in timeline.GetItemsInTrack('Video', 1):
                if nb_item == 1:
                    mark_in = timeline.GetStartFrame()
                else:
                    mark_in = timeline.GetItemsInTrack('Video', 1)[nb_item - 1].GetEnd()
                mark_out = timeline.GetItemsInTrack('Video', 1)[nb_item].GetEnd() - 1
                custom_name = timeline.GetItemsInTrack('Video', 1)[nb_item].GetName().split('.')[0]
                current_project.SetRenderSettings()
                current_project.SetRenderSettings({"MarkIn": mark_in,
                                                "MarkOut": mark_out,
                                               "CustomName": custom_name})
                job_id_timeline = current_project.AddRenderJob()
                job_id_timeline_list.append(job_id_timeline)

            jobs = current_project.GetRenderJobs()
            print(job_id_timeline_list)
            current_project.StartRendering(job_id_timeline_list)


            while current_project.IsRenderingInProgress():
                time.sleep(1)


            print('Finished Rendering {}'.format(timeline.GetName()))
            print(job_id_timeline_list)
            # Deleting all the jobs
            for job_id_to_delete in job_id_timeline_list:
                current_project.DeleteRenderJob(job_id_to_delete)


            # while current_project.IsRenderingInProgress():
            #     time.sleep(1)
        else:
            print('')

    if job_ready_count == 0:
        print("Didn't find any Job Ready in the Render Queue")

    return job_ready_count

if __name__ == "__main__":
    timeline_sync_export()
