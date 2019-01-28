import configparser
import datetime
import os
import threading
import time
from pathlib import Path
from urllib import parse

import pymysql
from DBUtils.PooledDB import PooledDB
from retry import retry

import mysite.settings as settings
from epg.utils import download_m3u8_files
from vodmanagement.models import VideoCategory, Vod
from vodmanagement.utils import delete_vod

pool_tsrtmp = PooledDB(
        pymysql,
        5,
        host = os.getenv('TSRTMP_DB_HOST', os.getenv('DJANGO_DB_HOST', '')),
        user = 'root',
        password = '123',
        charset = 'utf8mb4',
        db = 'tsrtmp'
    )

pool_vod = PooledDB(
        pymysql,
        5,
        host = os.getenv('DJANGO_DB_HOST', ''),
        user = 'root',
        password = '123',
        charset = 'utf8mb4',
        db = 'vod'
    )

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
def get_record_info(title, channel_id, db):
    print(datetime.datetime.now())
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
        print("No match program")
        raise Exception("No match program")
    return url, program_title


def record_video(url, program_title):               
    for i in range(0,len(url)):
        try:
            m3u8_file_path = parse.urlparse(url[i]).path  # /CCTV1/20180124/123456.m3u8
            video_path = settings.RECORD_MEDIA_FOLDER + m3u8_file_path
            new_record = Vod(
                    title = time.strftime("%Y-%m-%d",time.localtime()) + program_title[i],
                    video = video_path,
                    category_id = get_category_id(),
                    image =  str(Path(video_path).parents[0] / 'xinwenlianbo.jpg'),
                    )
            new_record.save()
            #p = threading.Thread(target=download_m3u8_files, args=(new_record.id, url[i], settings.RECORD_MEDIA_ROOT,))
            #p.start()
            download_m3u8_files(new_record.id, url[i], settings.RECORD_MEDIA_ROOT)
            source = settings.STATIC_ROOT +'/xinwenlianbo.jpg'
            target = str(Path(settings.RECORD_MEDIA_ROOT + m3u8_file_path).parent) + '/xinwenlianbo.jpg'
            os.system('cp -f %s %s'%(source,target))
        except Exception as e:
            print(e)
            raise e

def auto_record(): 
    db = pool_tsrtmp.connection()
    title, channel_id = get_program()
    url, program_title = get_record_info(title, channel_id, db)
    record_video(url, program_title)
    db.close()

def get_category_id():
    try:
        db = pool_vod.connection()
    except Exception():
        print('No Route To Host')
    else:
        with db.cursor() as cursor:
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
    finally:
        db.close()

def auto_del():
    id = get_category_id()
    try:
        db = pool_vod.connection()
    except Exception():
        print('No Route To Host')
    else:
        with db.cursor() as cursor:
            sql = 'SELECT id FROM vodmanagement_vod \
                    WHERE category_id = %d  \
                    AND TO_DAYS(NOW())-TO_DAYS(timestamp)>7' \
                    % id
            cursor.execute(sql)
            for obj in cursor.fetchall():
                video_id = obj[0]
                instance = Vod.objects.get(id=video_id)
                delete_vod(instance)
        print('successfully deleted auto_record video')
    finally:
        db.close()
