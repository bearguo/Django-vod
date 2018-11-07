import logging
import m3u8
from pathlib import Path
from time import sleep
from urllib.parse import urlparse, urljoin, quote, unquote
from urllib.request import urlretrieve, pathname2url
from vodmanagement.models import Vod
import ffmpy

def download_m3u8_files(id,url_str,dest_dir):
    obj = Vod.objects.get(id=id) 
    print(tag_url)
    video_path = Path(dest_dir) / Path(urlparse(url_str).path).with_suffix('.mp4')
    print(video_path)
    transcode = ffmpy.FFmpeg(
        inputs={str(url_str) : '-y'},
        outputs = {video_path : '-vcodec h264 -acodec aac -threads 2'}
        )
    print(transcode.cmd)
    try:
        if transcode.run == 0:
            obj.active = 1
            obj.save
    except:
        logging.error('Download m3u8(%s) files failed' % url_str)

'''
def download_m3u8_files(id, url_str, dest_dir):
    try:
        instance = Vod.objects.get(id=id)
        url = urlparse(url_str)
        m3u8_root = url.path
        m3u8_host_url = url.scheme + '://' + url.netloc
        m3u8_full_path = Path(dest_dir) / Path(m3u8_root[1:])
        m3u8_full_path.parent.mkdir(parents=True, exist_ok=True)
        file_path, message = urlretrieve(url_str, str(m3u8_full_path))
        with m3u8_full_path.open() as m3u8_file:
            m3u8_obj = m3u8.loads(m3u8_file.read())
            total_files = len(m3u8_obj.files)
            for index, ts_file in enumerate(m3u8_obj.files):
                ts_url = urljoin(m3u8_host_url, pathname2url(str(Path(m3u8_root).parent / Path(ts_file))))
                ts_full_path = m3u8_full_path.parent / Path(ts_file)
                ts_full_path.parent.mkdir(parents=True, exist_ok=True)
                status = download_ts_file(ts_url, str(ts_full_path))
                if status is not None:
                    instance.progress = int(index / total_files * 100)
                    print(instance.progress)
                    instance.save()
            instance.active = 1
            instance.save()
    except Exception as e:
        logging.error('Download m3u8(%s) files failed' % (url_str,))
        logging.exception(e)


def download_ts_file(url, dest_path):
    retry = 5
    while retry:
        try:
            urlretrieve(url, str(dest_path))
            return url
        except Exception as e:
            msg = url + ' download failed! '
            logging.error(msg)
            logging.exception(e)
            sleep(1)
            retry -= 1
    return None
'''