# coding=utf-8
__author__ = 'ziliangl'
from monitor.models import JobsPost,DBConnectionPost,JobsRun
import threading
import time
import datetime
import cx_Oracle
import MySQLdb
from monitor.sendmail import send_mail
#记录已到执行时间的JobsPost的ID和时间差


class EXECThread(threading.Thread):
    def __init__(self,interval):
        threading.Thread.__init__(self,name= 'exec')
        self.interval = interval
        self.isstop = False
        self.timedict = {}
        #self.today = datetime.date.today()

    def computeTime(self):
        Jobs = JobsPost.objects.filter(isusing=True)
        dt = datetime.datetime.now().strftime('%Y-%m-%d')
        now = datetime.datetime.now()
        for job in Jobs:
            dtime = datetime.datetime.strptime(dt+' '+str(job.exectime),'%Y-%m-%d %X')
            if dtime >= now:
                timedel = (dtime - now).seconds
                if timedel < self.interval*1.5 :
                    self.timedict[job.id] = timedel
        print 'time   ',time.ctime(),self.timedict
        print [job.id for job in Jobs]

        sortedlist = self.sorteddic(self.timedict)
        jobs = JobsRun.objects.filter(iswarning=True)
        for i in jobs:
            sortedlist.append((i.jobid_id,0))
        print 'sqlexec',time.ctime(),sortedlist
        for key in sortedlist:
            time.sleep(key[1])
            job = JobsPost.objects.get(id=key[0])
            job_sqlcount = int(self.sqlexec(job))
            job_iswarning = False
            job_warningmessage2 = ''
            if job_sqlcount>=job.minvalue and job_sqlcount<=job.maxvalue:
                job_warningmessage2 = '数据量正常'
            elif job_sqlcount == -3:
                job_iswarning = True
                job_warningmessage2 = 'sql执行结果返回值不为数字类型'
            elif job_sqlcount == -2:
                job_iswarning = True
                job_warningmessage2 = '不支持该种数据库类型'
            elif job_sqlcount == -1:
                job_iswarning = True
                job_warningmessage2 = '数据库访问失败，请检查数据库链接、网络、数据库是否正常'
            elif job_sqlcount == 0 :
                job_iswarning = True
                job_warningmessage2 = '查询数据为空，请检查数据库来源是否正常'
            elif job_sqlcount < job.minvalue:
                job_iswarning = True
                job_warningmessage2 = '数据量小于正常值，请检查数据库来源是否正常'
            elif job_sqlcount > job.maxvalue:
                job_iswarning = True
                job_warningmessage2 = '数据量大于正常值，请检查最大正常值设置是否合理'
            else :
                pass
            job_warningmessage = '本次查询共返回 ' + str(job_sqlcount) +' 条结果;' + job_warningmessage2
            job_RunTime = datetime.datetime.now()
            JobsRun.objects.filter(jobid=job,RunDate=datetime.date.today()).update(RunTime = job_RunTime,
                iswarning=job_iswarning,
                warningmessage=job_warningmessage )
            #----------发送邮件---------
            if job_iswarning==True and job.needsendmail==True:
                send_mail(job.manager,"数据库监控",job_warningmessage)
            #-------------------------

    def JobRuns_initialization(self):
        """
        如果新加记录在JobRuns表里不存在，则初始化一条新记录
                """
        Jobs = JobsPost.objects.filter(isusing=True)
        for job in Jobs:
            jobrun = JobsRun.objects.filter(RunDate =datetime.date.today(),jobid=job )
            if jobrun == []:
                job_new = JobsRun(jobid=job,
                    iswarning=False,
                    RunDate = datetime.date.today(),
                    RunTime = datetime.datetime.now(),
                    warningmessage='未到达指定运行时间' )
                job_new.save()

    def run(self):
        self.JobRuns_initialization()
        self.computeTime()

    def stop(self):
        self.isstop = True

    def sqlexec(self,job):
        """
        查询数据库,
        如果返回值为-1，说明数据库连接失败；
        如果返回值为-2，说明数据库类型未知；
        如果返回值为-3，说明sql执行结果返回值不为int或者long类型；
        """
        db = DBConnectionPost.objects.get(dbconnectionname = job.dbconnectionname)
        try:
            if db.dbengine == 'oracle':
                con = db.dbhost +':' + str(db.dbport) +'/' + db.dbname
                dbconn = cx_Oracle.connect(db.dbuser,db.dbpassword,con)
                cursor = dbconn.cursor()
                cursor.execute(job.sqltext)
                r = cursor.fetchall()
                cursor.close()
                dbconn.close()
                if str(type(r[0][0])) == "<type 'int'>" or str(type(r[0][0])) == "<type 'long'>":
                    return r[0][0]
                else:
                    return -3
            elif db.dbengine == 'mysql':
                dbconn = MySQLdb.connect(host=db.dbhost,user=db.dbuser,passwd=db.dbpassword,db=db.dbname,charset='utf8')
                cursor = dbconn.cursor()
                cursor.execute(job.sqltext)
                r = cursor.fetchall()
                cursor.close()
                dbconn.close()
                if str(type(r[0][0])) == "<type 'int'>" or str(type(r[0][0])) == "<type 'long'>":
                    return r[0][0]
                else:
                    return -3
            else:
                return -2
        except Exception:
            return -1
        finally:
            pass

    def sorteddic(self,timedict):
        if len(timedict) > 1 :
            sorteddict = sorted(timedict.iteritems(),key=lambda x:x[1],reverse=False)
            lis =[(sorteddict[0][0],sorteddict[0][1])]
            for i in range(1,len(sorteddict)):
                lis.append((sorteddict[i][0],sorteddict[i][1] -sorteddict[i-1][1]))
            return lis
        else:
            return [i for i in timedict.iteritems()]




class RunThreading(threading.Thread):
    def __init__(self,interval):
        threading.Thread.__init__(self,name= 'runthreading')
        self.interval = interval
    def run(self):
        while True:
            t1 = EXECThread(self.interval)
            t1.start()
            print "Start"
            time.sleep(self.interval)
            if t1.isAlive():
                t1.stop()
            print "Over!!!"





