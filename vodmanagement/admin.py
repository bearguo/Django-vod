import datetime
import threading
from pathlib import Path
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.core.management import call_command
from django.core import serializers as django_serializers
from django.http import HttpResponse
from django.contrib import messages
from uuslug import uuslug
from vodmanagement import ffmpy
import m3u8

from vodmanagement.forms import RestoreForm, CategoryAdminForm, VodForm, MultipleUploadForm
from vodmanagement.models import (
    Vod,
    VideoCategory,
    MultipleUpload,
    Restore,
    FileDirectory,
    VideoRegion
)
from vodmanagement.utils import *


class VideoFormatFilter(SimpleListFilter):
    title = '视频格式'  # or use _('country') for translated title
    parameter_name = 'video'

    def lookups(self, request, model_admin):
        video_suffixs = set([Path(c.video.name).suffix for c in model_admin.model.objects.all()])
        return [(c, c) for c in video_suffixs if c]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(video__endswith=self.value())


@admin.register(Vod)
class VodModelAdmin(admin.ModelAdmin):
    list_display = ['title', 'select_name', 'image_tag', 'category', 'definition', 'year', 'region',
                    'view_count', 'timestamp', 'colored_active', 'video_format']  # image_tag
    list_display_links = ['title', 'image_tag', 'timestamp']  # image_tag
    list_editable = ['category', 'select_name', 'definition']
    list_filter = ['year', 'category', VideoFormatFilter]
    # filter_horizontal = ['video_list']
    # fields = ('image_tag',)
    # readonly_fields = ('image_tag',)
    search_fields = ['title', 'description', 'search_word']
    actions = ['delete_hard', 'copy_objects', 'clear_view_count', 'activate_vod', 'deactivate_vod', 'backup',
               'backup_all', 'transcoding']
    form = VodForm
    fieldsets = [
        ('描述', {'fields': ['category', 'save_path', 'year', 'region', 'description', 'select_name', 'active']}),
        ('文件', {'fields': ['image', 'video', 'title']}),
        ('视频列表', {'fields': ['video_list']}),
        ('高级', {'fields': ['slug', 'search_word'], 'classes': ['collapse']})
    ]
    change_form_template = 'vodmanagement/change_form.html'
    add_form_template = 'vodmanagement/change_form.html'

    def save_model(self, request, obj, form, change):
        # obj.creator = request.user
        super(VodModelAdmin, self).save_model(request, obj, form, change)
    
    def delete_model(self, request, object):
        try:
            delete_hard(object.image.path)
        except:
            pass
        try:
            delete_hard(object.video.path)
        except:
            pass
        object.delete()
    
    def delete_hard(self, request, queryset):
        for obj in queryset:
            try:
                delete_hard(obj.image.path)
            except:
                pass
            try:
                if os.path.splitext(str(obj.video))[1] == '.m3u8':
                    obj_ts=(m3u8.load(str(obj.video.path))).files

                    for ts_file in obj_ts:
                        try:
                            ts_path = Path(os.path.dirname(obj.video.path)) / Path(ts_file)
                            os.remove(ts_path)
                        except:
                            pass
                delete_hard(obj.video.path)   
            except:
                pass
            obj.delete()

    delete_hard.short_description = '删除硬盘上的文件'

    def copy_objects(self, request, queryset):
        for obj in queryset:
            for i in range(4):
                new_obj = obj
                new_obj.pk = None
                # new_obj.slug = create_slug(new_obj)
                new_obj.slug = uuslug(new_obj.title, instance=new_obj)
                new_obj.save()
        self.message_user(request, '%s item successfully copyed.' % queryset.count()
                          , messages.SUCCESS)

    def activate_vod(self, request, queryset):
        for item in queryset:
            item.active = 1
            item.save()
        self.message_user(request, '%s个节目成功激活.' % queryset.count()
                          , messages.SUCCESS)

    activate_vod.short_description = '激活节目列表'

    def deactivate_vod(self, request, queryset):
        for item in queryset:
            item.active = 0
            item.save()
        self.message_user(request, '%s个节目成功取消激活.' % queryset.count()
                          , messages.SUCCESS)

    deactivate_vod.short_description = '取消激活节目'

    def clear_view_count(self, request, queryset):
        queryset.update(view_count=0)
        self.message_user(request, '%s item successfully cleared view count.' % queryset.count()
                          , messages.SUCCESS)
    clear_view_count.short_description = '重置播放次数'

    def backup(self, request, queryset):
        response = HttpResponse(content_type='text/plain')
        file_name = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '-backup.json'
        response['Content-Disposition'] = 'attachment; filename=%s' % file_name
        directory = Path(settings.MEDIA_ROOT) / 'backup'
        full_file_name = directory / file_name
        directory.mkdir(parents=True, exist_ok=True)
        data = django_serializers.serialize('json', queryset)
        full_file_name.open('w').write(data)
        response.write(full_file_name.open('rb').read())
        return response

    backup.short_description = '备份选中节目'

    def backup_all(self, request, queryset):
        response = HttpResponse(content_type='text/plain')
        file_name = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '-backup.json'
        response['Content-Disposition'] = 'attachment; filename=%s' % file_name
        directory = Path(settings.MEDIA_ROOT) / 'backup'
        full_file_name = directory / file_name
        directory.mkdir(parents=True, exist_ok=True)
        full_file_name.open('w').write('')
        call_command('dumpdata', 'vodmanagement', '-o', str(full_file_name))  # 使用Django提供的命令行工具备份数据
        response.write(full_file_name.open('rb').read())
        return response

    backup_all.short_description = '备份所有节目'

    def transcoding(self, request, queryset):
        def ff(obj):
            video_path=obj.video.name
            recent_path=os.getcwd()
            print(video_path)
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
                obj.video.path = video_name_new
                obj.save()
            print(str(obj.video.path))

        for obj in queryset:
            if os.path.splitext(str(obj.video))[1] != '.mp4':
                p = threading.Thread(target = ff,args = (obj,))
                p.start()
        self.message_user(request, '视频已提交后台转码'
                          , messages.SUCCESS)

    transcoding.short_description = '转为mp4'


@admin.register(VideoCategory)
class VideoCategoryModelAdmin(admin.ModelAdmin):
    list_display = ['category_description', 'colored_level', 'type', 'isSecret']
    list_editable = ['isSecret']
    search_fields = ['name']
    filter_horizontal = ['subset']
    ordering = ['level']
    form = CategoryAdminForm
    fieldsets = [
        ('描述', {'fields': ['name', 'level', 'subset']}),
        ('高级', {'fields': ['isSecret', 'type'], 'classes': ['collapse']})
    ]

    def category_description(self, obj):
        return str(obj)

    category_description.short_description = '分类名称'


class LinkModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_editable = ['category']


@admin.register(MultipleUpload)
class MultipleUploadModelAdmin(admin.ModelAdmin):
    form = MultipleUploadForm
    change_form_template = 'vodmanagement/MultipleUpload/change_form.html'
    add_form_template = 'vodmanagement/MultipleUpload/change_form.html'


@admin.register(Restore)
class RestoreModelAdmin(admin.ModelAdmin):
    form = RestoreForm
    change_form_template = 'vodmanagement/change_form.html'
    add_form_template = 'vodmanagement/change_form.html'


admin.site.register(FileDirectory)
admin.site.register(VideoRegion)
