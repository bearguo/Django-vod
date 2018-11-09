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
    cf = configparser.ConfigParser()
    config_file = Path(settings.BASE_DIR) / 'conf' / 'auto_record.conf'
    cf.read(str(config_file))
    title = []
    channel_id = []
    if len(cf.sections()) == 0:
        return
    else:
        for obj in cf.sections():
            title.append(cf.get(obj, 'title'))
            channel_id.append(cf.get(obj,'channel_id'))
    p = threading.Thread(target=auto_record, args=(title, channel_id))
    p.start
    #auto_record(title, channel_id)

@retry(tries=3, delay=1800)
def auto_record(title, channel_id):
    try:
        db = pymysql.connect(
            host = os.getenv('TSRTMP_DB_HOST', os.getenv('DJANGO_DB_HOST', '')),
            user = 'root',
            password = '123',
            charset = 'utf8mb4',
            db = 'tsrtmp'
        )
    except Exception:
        print("No route to host")
    else:
        for i in range(0,len(title)):
            try:
                with db.cursor() as cursor:
                    sql = '\
                    SELECT url,title FROM program \
                    WHERE title LIKE %s \
                    AND channel_id = %s \
                    AND finished = 1 \
                    AND TO_DAYS(NOW())-TO_DAYS(start_time) = 1 ' \
                    % (title[i], channel_id[i])
                cursor.execute(sql)
                url,program_title = cursor.fetchone()
            except Exception:
                print("url not exist")
            else:
                m3u8_file_path = parse.urlparse(url).path  # /CCTV1/20180124/123456.m3u8
                new_record = Vod(
                        title=program_title,
                        video=settings.RECORD_MEDIA_FOLDER + m3u8_file_path
                        )
                new_record.save()
                #p = threading.Thread(target=download_m3u8_files, args=(new_record.id, url, settings.RECORD_MEDIA_ROOT,))
                download_m3u8_files(new_record.id, url, settings.RECORD_MEDIA_ROOT)  
                #p.start()
    finally:
        db.close()

if __name__ ==" __main__":
    auto_record