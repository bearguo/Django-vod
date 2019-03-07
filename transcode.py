import ffmpy
import os
from pathlib import Path
from logutil import update_logger
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
        os.remove(str(video_abspath))
        video_name_new = Path(video_path).with_suffix('.mp4')
        obj.video.name = str(video_name_new)
        obj.save()
        update_logger.info('transcode ' + str(obj.title) + ' success')
        