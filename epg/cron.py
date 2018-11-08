from epg.models import Program
from vodmanagement.models import Vod
from mysite import settings
from urllib import parse
from epg.utils import download_m3u8_files
from pathlib import Path
import pymysql
import os
import threading

def auto_record():
    print("-------------------auto_record start-----------------------")
    db = pymysql.connect(
        host = os.getenv('TSRTMP_DB_HOST', os.getenv('DJANGO_DB_HOST', '')),
        user = 'root',
        password = '123',
        charset = 'utf8mb4',
        db = 'tsrtmp'
    )
    try:
        with db.cursor() as cursor:
            sql = '''\
            SELECT event_id FROM program \
            WHERE channel_id = "CCTV1" \
            AND title = "新闻联播“ \
            AND start_time LIKE "%19:00:00" \
            AND TO_DAYS(start_time)=TO_DAYS(NOW()) '''
            cursor.execute(sql)
            event_id = cursor.fetchall()
    finally:
        db.close()
    data = Program.objects.get(event_id=event_id)
    m3u8_file_path = parse.urlparse(data.url).path  # /CCTV1/20180124/123456.m3u8
    mp4_file_path = Path(m3u8_file_path).parent / Path(data.title).with_suffix('.mp4') # /CCTV1/20180124/<title>.mp4
    new_record = Vod(
            title=data.title,
            video=settings.RECORD_MEDIA_FOLDER + str(mp4_file_path)
            )
    new_record.save()
    p = threading.Thread(target=download_m3u8_files, args=(new_record.id, data.url, settings.RECORD_MEDIA_ROOT, data.title))  
    p.start()
    print("-------------------------auto_record finish-----------------------")

if __name__ ==" __main__":
    auto_record