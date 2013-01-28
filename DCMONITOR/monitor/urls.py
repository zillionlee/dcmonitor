#__author__ = 'ziliangl'
from monitor.views import archive
from django.conf.urls import patterns, include, url



urlpatterns = patterns('',

    url(r'^$', archive),
)
