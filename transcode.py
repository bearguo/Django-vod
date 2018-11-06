import vodmanagement.ffmpy as ffmpy
import os
from pathlib import Path
import logging
def ff(obj):
    video_path=obj.video.name
    recent_path=os.getcwd()
    os.chdir('/')
    video_abspath=obj.video.path
    transcode = ffmpy.FFmpeg(
        inputs={str(obj.video.path) : '-y'},
        outputs = {str(Path(obj.video.path).with_suffix('.mp4')) : '-vcodec h264 -acodec aac -threads 2'}
        )
    os.chdir(recent_path)
    if transcode.run() == 0:
        logging.debug("transcode",str(obj.video.path))
        os.remove(str(video_abspath))
        video_name_new = Path(video_path).with_suffix('.mp4')
        obj.video.name = str(video_name_new)
        obj.save()
        