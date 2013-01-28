# coding=utf-8
from django.template import loader,Context
from django.http import HttpResponse
from monitor.models import JobsPost,JobsRun
import datetime


def archive(request):
    posts = JobsPost.objects.all()
    #db = DBConnectionPost.objects.all()
    jobs = JobsRun.objects.filter(RunDate=datetime.date.today())  #以后要改取当天数据

    t = loader.get_template('archive.html')
    c = Context({'posts':posts,'jobs':jobs})

    return  HttpResponse(t.render(c))


