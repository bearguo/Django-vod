import configparser
import datetime
import os
import threading
from pathlib import Path
from urllib import parse
import time
import pymysql
from retry import retry

import mysite.settings as settings
from epg.utils import download_m3u8_files
from vodmanagement.models import VideoCategory, Vod


def get_program():
    cf = configparser.ConfigParser()
    config_file = Path(settings.BASE_DIR) / 'conf' / 'auto_record.conf'
    cf.read(str(config_file), encoding="utf-8")
    title = []
    channel_id = []
    if len(cf.sections()) == 0:
        return
    else:
        for obj in cf.sections():
            title.append(cf.get(obj, 'title'))
            channel_id.append(cf.get(obj,'channel_id'))
    #p = threading.Thread(target=auto_record, args=(title, channel_id))
    #p.start()
    auto_record(title, channel_id)

@retry(tries=30, delay=5*60)
def auto_record(title, channel_id):
    print(datetime.datetime.now())
    try:
        db = pymysql.connect(
            host = os.getenv('TSRTMP_DB_HOST', os.getenv('DJANGO_DB_HOST', '')),
            user = 'root',
            password = '123',
            charset = 'utf8mb4',
            db = 'tsrtmp'
        )
    except Exception():
        print("No route to host")
    else:
        url = []
        program_title = []
        for i in range(0,len(title)):
            with db.cursor() as cursor:
                sql = '\
                SELECT url,title FROM program \
                WHERE title LIKE %s \
                AND channel_id = %s \
                AND finished = 1 \
                AND TO_DAYS(NOW())=TO_DAYS(start_time)' \
                % (title[i], channel_id[i])
                cursor.execute(sql)

                for obj in cursor.fetchall():
                    url.append(obj[0])
                    program_title.append(obj[1])
        if len(url) == 0:
            print("retrying")
            raise Exception("No match program")
                    
        for i in range(0,len(url)):
            m3u8_file_path = parse.urlparse(url[i]).path  # /CCTV1/20180124/123456.m3u8
            new_record = Vod(
                    title = time.strftime("%Y-%m-%d",time.localtime()) + program_title[i],
                    video = settings.RECORD_MEDIA_FOLDER + m3u8_file_path,
                    category_id = get_category_id()
                    )
            new_record.save()
            p = threading.Thread(target=download_m3u8_files, args=(new_record.id, url[i], settings.RECORD_MEDIA_ROOT,))
            p.start()
            #download_m3u8_files(new_record.id, url[i], settings.RECORD_MEDIA_ROOT)
    finally:
        db.close()

def get_category_id():
    try:
        db2 = pymysql.connect(
            host = os.getenv('DJANGO_DB_HOST', ''),
            user = 'root',
            password = '123',
            charset = 'utf8mb4',
            db = 'vod'
        )
    except Exception():
        print('No Route To Host')
    else:
        with db2.cursor() as cursor:
            sql = 'SELECT id FROM vodmanagement_videocategory \
                    WHERE name = "自动录制" '
            cursor.execute(sql)
            if not cursor.fetchone():
                new_category = VideoCategory(
                   name = '自动录制',
                )
                new_category.save()
            cursor.execute(sql)
            return int(cursor.fetchone()[0])
