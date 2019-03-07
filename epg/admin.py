import threading
from pathlib import Path
from urllib import parse
from urllib.request import urlopen

from django.contrib import admin, messages
from django.urls import reverse
from django.utils.safestring import mark_safe

from epg.models import Channel, Program
from epg.utils import download_m3u8_files
from mysite import settings
from vodmanagement.models import Vod
from logutil import update_logger


@admin.register(Channel)
class ChannelModelAdmin(admin.ModelAdmin):
    list_display = ['channel_id', 'channel_name', 'rtmp_url', 'shared']
    list_display_links = ['channel_id']  # image_tag
    list_editable = ['channel_name', 'rtmp_url']
    search_fields = ['channel_id', 'channel_name']
    actions = ['share_channel', 'stop_share_channel']

    def share_channel(self, request, queryset):
        for obj in queryset:
            obj.shared = 1
            obj.save()
        self.message_user(request, '%s个频道已共享.' % queryset.count()
                          , messages.SUCCESS)

    share_channel.short_description = '共享频道'

    def stop_share_channel(self, request, queryset):
        for obj in queryset:
            obj.shared = 0
            obj.save()
        self.message_user(request, '%s个频道取消共享.' % queryset.count()
                          , messages.SUCCESS)

    stop_share_channel.short_description = '取消共享频道'
            




@admin.register(Program)
class ProgramModelAdmin(admin.ModelAdmin):
    """
    Program admin site view
    """
    list_display = ['channel', 'title', 'start_time', 'end_time', 'url']
    list_display_links = ['channel']
    list_filter = ['finished', 'channel']
    search_fields = ['title']
    actions = ['record', 'get_category_id']

    def get_queryset(self, request):
        return super(ProgramModelAdmin, self).get_queryset(request).filter(finished=1)

    def record(self, request, queryset):
        legal_program_cnt = 0
        for program in queryset:
            try:
                m3u8_file_path = parse.urlparse(program.url).path  # /CCTV1/20180124/123456.m3u8
            #    mp4_file_path = Path(m3u8_file_path).parent / Path(program.title).with_suffix('.mp4') # /CCTV1/20180124/<title>.mp4
                urlopen(program.url, timeout=5)
            except Exception as e:
                update_logger.error(e)
                self.message_user(request, '%s 转点播失败 请检查录播的网址是否可以访问'%(program.title), messages.ERROR)
                continue
            new_record = Vod(
                title=program.title,
                video=settings.RECORD_MEDIA_FOLDER + m3u8_file_path
                )
            new_record.save()
            p = threading.Thread(target=download_m3u8_files, args=(new_record.id, program.url, settings.RECORD_MEDIA_ROOT))
            p.start()
            legal_program_cnt += 1
        record_url = reverse('admin:vodmanagement_vod_changelist')
        self.message_user(request, mark_safe('%s/%s 个节目正在转成点播,转换进度请到<a href="%s">录制节目</a>处查看。'%(legal_program_cnt,queryset.count(),record_url))
                          , messages.SUCCESS)

    record.short_description = '转为点播'
