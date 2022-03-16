"""
get a dict for changing meta from a video by copying the codec from ffmpeg and add metadata argument
"""

import subprocess

ffmpeg = "/usr/local/bin/ffmpeg"

def grabUserInput():
    path = "/Users/bryanrandell/Movies/export_test/"
    input_file = "Untitled.mov"
    output_file = "Untitled_copy.mov"
    new_timecode = "01:00:00:01"
    video_change_timecode_dict = {}

    video_change_timecode_dict["input_file"] = "{}{}".format(path, input_file)
    video_change_timecode_dict["output_file"] = "{}{}".format(path, output_file)
    video_change_timecode_dict["timecode"] = 'timecode="{}"'.format(new_timecode)

    return video_change_timecode_dict

def depreciated_buildFFmpegCommand(video_change_timecode_dict=grabUserInput()):
    """
    build the command line for ffmpeg
    :param video_change_timecode_dict:
    :return:
    """
    commands_list = [
        ffmpeg,
        "-i",
        video_change_timecode_dict["input_file"],
        "-metadata",
        video_change_timecode_dict["timecode"],
        "-codec",
        "copy",
        video_change_timecode_dict["output_file"],
        "&&",
        video_change_timecode_dict["output_file"],
        video_change_timecode_dict["input_file"]
    ]

    return commands_list

def buildFFmpegCommand(temp_file_path, timecode):
    """
    build the command line for ffmpeg
    :param video_change_timecode_dict:
    :return:
    """
    output_file_path = temp_file_path.split("_temp_")[0] + temp_file_path.split("_temp_")[1]
    commands_list = [
        ffmpeg,
        "-i",
        temp_file_path,
        "-metadata",
        'timecode={}'.format(timecode),
        "-codec",
        "copy",
        output_file_path
        # "&&",
        # "mv",
        # output_file_path,
        # temp_file_path
    ]

    return commands_list

def runFFmpeg(commands):
    """
    run the ffmpeg in the terminal
    :param commands:
    :return:
    """

    print(commands)
    if subprocess.run(commands).returncode == 0:
        print ("FFmpeg Script Ran Successfully")
    else:
        print ("There was an error running your FFmpeg script")

if __name__ == "__main__":
    runFFmpeg(buildFFmpegCommand())
