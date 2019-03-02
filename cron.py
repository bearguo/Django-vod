import configparser
import datetime
import os
import threading
from pathlib import Path
from urllib import parse

from retry import retry

import mysite.settings as settings
from epg.models import Program
from epg.utils import download_m3u8_files
from vodmanagement.models import VideoCategory, Vod
from vodmanagement.utils import delete_vod

category_id_file = config_file = Path(settings.BASE_DIR) / 'conf' / 'category_id.txt'


def get_program():
    cf = configparser.ConfigParser()
    config_file = Path(settings.BASE_DIR) / 'conf' / 'auto_record.conf'
    cf.read(str(config_file), encoding="utf-8")
    title = []
    channel_id = []
    if len(cf.sections()) == 0:
        return title, channel_id
    else:
        for obj in cf.sections():
            title.append(cf.get(obj, 'title'))
            channel_id.append(cf.get(obj,'channel_id'))
    return title, channel_id

@retry(tries=30, delay=5*60)
def get_record_info(title, channel_id):
    url = []
    program_title = []
    for i in range(0,len(title)):
        obj = Program.objects.filter(
            title=title[i],
            finished='1',
            channel_id=channel_id[i],
            start_time__startswith=datetime.date.today()
        )
    if len(obj) == 0:
        print('No matched program')
        raise Exception('No matched program')
    else:
        for i in obj:
            url.append(i.url) 
            program_title.append(i.title)
        return url, program_title

def record_video(url, program_title):               
    for i in range(0,len(url)):
        try:
            m3u8_file_path = parse.urlparse(url[i]).path  # /CCTV1/20180124/123456.m3u8
            video_path = settings.RECORD_MEDIA_FOLDER + m3u8_file_path
            if not os.path.exists(category_id_file):
                get_category_id()
            with open(category_id_file,'r', encoding='utf-8') as f:
                category_id = f.read()
            new_record = Vod(
                    title = str(datetime.date.today()) + program_title[i],
                    video = video_path,
                    category_id = category_id,
                    image =  str(Path(video_path).parents[0] / 'xinwenlianbo.jpg'),
                    )
            new_record.save()
            download_m3u8_files(new_record.id, url[i], settings.RECORD_MEDIA_ROOT)
            source = settings.STATIC_ROOT +'/xinwenlianbo.jpg'
            target = str(Path(settings.RECORD_MEDIA_ROOT + m3u8_file_path).parent) + '/xinwenlianbo.jpg'
            Path(target).parent.mkdir(exist_ok=True, parents=True)
            os.system('cp -f %s %s'%(source,target))
        except Exception as e:
            print(e)
            raise e

def get_category_id():
    with open(category_id_file,'w', encoding='utf-8') as f:
        try:
            obj = VideoCategory.objects.get(name='自动录制')
        except Exception:
            new_category = VideoCategory(name = '自动录制',)
            new_category.save()
            f.write(str(new_category.id))
        else:
            f.write(str(obj.id))
    

def auto_record(): 
    title, channel_id = get_program()
    url, program_title = get_record_info(title, channel_id)
    record_video(url, program_title)

def auto_del():
    if not os.path.exists(category_id_file):
        get_category_id()
    with open(category_id_file,'r', encoding='utf-8') as f:
        auto_record_id = f.read
    now = datetime.datetime.now()
    delta = datetime.timedelta(days=7)
    obj = Vod.objects.filter(category_id=auto_record_id, timestamp__lt=(now - delta))
    for i in obj:
        i.delete()
