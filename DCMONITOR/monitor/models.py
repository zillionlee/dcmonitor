# coding=utf-8
from django.db import models
from django.contrib import admin

# Create your models here.
#记录数据库连接
class DBConnectionPost(models.Model):
    DB_CHOICES = (
        ('oracle','oracle'),
        ('mysql','mysql')
    )
    dbconnectionname = models.CharField(max_length=20,primary_key=True,verbose_name=u'连接名')
    dbengine = models.CharField(max_length=20,choices=DB_CHOICES ,default='oracle',verbose_name=u'数据库类型')    #选择连接数据库类型
    dbname = models.CharField(max_length=20,verbose_name=u'数据库名')          #oracle里面的为SERVICE_NAME，mysql里面的为DATABASE_NAME
    dbuser = models.CharField(max_length=20,verbose_name=u'用户')
    dbpassword = models.CharField(max_length=30,verbose_name=u'密码')
    dbhost = models.IPAddressField(verbose_name=u'IP地址')
    dbport = models.IntegerField(verbose_name=u'端口号')
    def __unicode__(self):
        return self.dbconnectionname
    class Meta:
        verbose_name_plural  = u'数据库连接管理'

class DBConnectionPostAdmin(admin.ModelAdmin):
    list_display = ('dbconnectionname','dbengine','dbuser','dbhost','dbport')
    search_fields = ('dbhost','dbconnectionname','dbuser',)

#任务计划
class JobsPost(models.Model):
    jobid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50,verbose_name=u'标题')
    isusing = models.BooleanField(default=True,verbose_name=u'是否启用')
    sqltext = models.TextField()
    description = models.CharField(max_length=500,blank=True,null=True,verbose_name=u'描述')
    minvalue = models.BigIntegerField(default=1,verbose_name=u'最小正常值')
    maxvalue = models.BigIntegerField(default=1000000000,verbose_name=u'最大正常值')    #1billion
    dbconnectionname = models.ForeignKey(DBConnectionPost,verbose_name=u'连接数据库')
    exectime = models.TimeField(verbose_name=u'执行时间')
    needsendmail = models.BooleanField(default=False,verbose_name=u'需要邮件提醒')
    manager = models.CharField(max_length=500,blank=True,null=True,verbose_name=u'收件人(请以“;”分割)')
    def __unicode__(self):
        return str(self.jobid)
    class Meta:
        ordering = ('-exectime',)
        verbose_name_plural  = u'计划任务'

class JobsPostAdmin(admin.ModelAdmin):
    list_display = ('title','description','sqltext','dbconnectionname','exectime')
    search_fields = ('description','sqltext','title',)

#这个要改，记录每天的job运行情况
class JobsRun(models.Model):
    jobid = models.ForeignKey(JobsPost,verbose_name=u'任务ID')
    iswarning = models.BooleanField(default=False,verbose_name=u'是否警告')
    RunDate = models.DateField(null=False,verbose_name=u'运行日期')
    RunTime = models.TimeField(blank=True,null=True,verbose_name=u'运行时间')
    warningmessage = models.CharField(max_length=500,blank=True,null=True,verbose_name=u'警告信息')
    class Meta:
        unique_together = (("jobid","RunDate"),)
        verbose_name_plural  = u'任务执行情况'
class JobsRunAdmin(admin.ModelAdmin):
    list_display = ('id','jobid','RunDate','warningmessage',)
    search_fields = ('-RunDate','-id')


admin.site.register(JobsPost,JobsPostAdmin)
admin.site.register(DBConnectionPost,DBConnectionPostAdmin)
admin.site.register(JobsRun,JobsRunAdmin)