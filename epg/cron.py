from vodmanagement.models import Vod
from urllib import parse
from epg.utils import download_m3u8_files
from pathlib import Path
import pymysql
import os
import threading
from retry import retry
import configparser
import mysite.settings as settings
import threading

def get_program():
    os.system("echo $(date) >> auto_record.log")
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
    p = threading.Thread(target=auto_record, args=(title, channel_id))
    p.start()
    #auto_record(title, channel_id)

@retry(tries=30, delay=5*60)
def auto_record(title, channel_id):
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
        for i in range(0,len(title)):
            url = []
            program_title = []
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
                raise Exception("No match program")
                    
            for i in range(0,len(url)):
                m3u8_file_path = parse.urlparse(url[i]).path  # /CCTV1/20180124/123456.m3u8
                new_record = Vod(
                        title=program_title[i],
                        video=settings.RECORD_MEDIA_FOLDER + m3u8_file_path
                        )
                new_record.save()
                #p = threading.Thread(target=download_m3u8_files, args=(new_record.id, url, settings.RECORD_MEDIA_ROOT,))
                download_m3u8_files(new_record.id, url[i], settings.RECORD_MEDIA_ROOT)
    finally:
        db.close()
