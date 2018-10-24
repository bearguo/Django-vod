from django.conf.urls import url
from django.views.decorators.cache import cache_page
from .views import *
cache_time = 1
urlpatterns = [
    url(r'^channels$', cache_page(cache_time)(ChannelListAPIView.as_view()), name='channels'),
    url(r'^shared$', cache_page(cache_time)(SharedChannelListAPIView.as_view()), name='shared_channel'),
     url(r'^programs$', cache_page(cache_time)(ProgramListAPIView.as_view()), name='programs'),
]
