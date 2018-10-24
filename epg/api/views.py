from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from epg.api.serializers import *
from epg.models import Channel, Program

class ChannelListAPIView(ListAPIView):
    queryset = Channel.objects.all()
    permission_classes = [AllowAny]
    serializer_class = ChannelListSerializer

class SharedChannelListAPIView(ListAPIView):
    queryset = Channel.objects.filter(shared=1)
    permission_classes = [AllowAny]
    serializer_class = SharedChannelListSerializer

class ProgramListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProgramListSerializer
    '''
    def get_queryset(self, *args, **kwargs):
        main_category = self.request.query_params.get('main_category')
        queryset_list = get_all_videos(main_category)
        category = checked_query_param(self.request.query_params.get('category'))
        year = checked_query_param(self.request.query_params.get('year'))
        region = checked_query_param(self.request.query_params.get('region'))
        queryset_list = get_filter_videos(queryset_list, category=category, year=year, region=region)
        search = self.request.GET.get("search")
        if search is not None and search != '':
            queryset_list = queryset_list.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        return queryset_list
    '''
    def get_queryset(self, *args, **kwargs):
        channel = self.request.query_params.get('channel')
        length = self.request.query_params.get('length')
        
        try:
            length_int = int(length)
        except:
            length_int = 4
        query_set = Program.objects.filter(channel=channel)[:length_int]
        return query_set[:length_int]
        