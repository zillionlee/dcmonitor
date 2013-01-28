# coding=utf-8
__author__ = 'ziliangl'
from monitor.models import JobsPost,DBConnectionPost,JobsRun
import threading
import time
import datetime
import cx_Oracle
import MySQLdb
#记录已到执行时间的JobsPost的ID和时间差

monitor = {'lock':threading.Lock(),'zero':'23:59:59','timedict':{}}
class TimeDaemon(threading.Thread):
    def __init__(self,interval):
        threading.Thread.__init__(self,name= 'timedaemon')
        self.interval = interval
        self.isstop = False
    def compute(self):
        Jobs =list(JobsPost.objects.filter(isusing=True))
        dt = datetime.datetime.now().strftime('%Y-%m-%d')
        now = datetime.datetime.now()
        #加锁
        monitor['lock'].acquire()
        monitor['timedict'] = {}
        for job in Jobs:
            dtime = datetime.datetime.strptime(dt+' '+str(job.exectime),'%Y-%m-%d %X')
            if dtime > now:
                timedel = (dtime - now).seconds
                if timedel < self.interval*1.5 :
                    monitor['timedict'][job.id] = timedel
        print 'time   ',time.ctime(),monitor['timedict']
        print [job.id for job in Jobs]
        monitor['lock'].release()

    def run(self):
        while not self.isstop:
            self.compute()
            time.sleep(self.interval)
    def stop(self):
        self.isstop = True


class SQLexec(threading.Thread):
    def __init__(self,interval):
        threading.Thread.__init__(self,name= 'sqlexec')
        self.interval = interval
        self.isstop = False
    def run(self):
        while not self.isstop:
            self.compute()
            #如果到底特定时间点（0点），数据将刷新

            time.sleep(self.interval)
    def stop(self):
        self.isstop = True

    def sqlexec(self,job):
        #job = JobsPost.objects.get(id=1)
        """
        查询数据库,
        如果返回值为-1，说明数据库连接失败；
        如果返回值为-2，说明数据库类型未知；
        如果返回值为-3，说明sql执行结果返回值不为int类型；
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
                if str(type(r[0][0])) == "<type 'int'>":
                    return r[0][0]
                else:
                    return -3
            elif db.dbengine == 'mysql':
                dbconn = MySQLdb.connect(host=db.dbhost,user=db.dbuser,passwd=db.dbpassword,db=db.dbname,charset='utf8')
                cursor = dbconn.cursor()
                cursor.execute(job.sqltext)
                r = cursor.fetchall()
                cursor.close()
                if str(type(r[0][0])) == "<type 'int'>":
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

    def compute(self):
        monitor['lock'].acquire()
        sortedlist = self.sorteddic(monitor['timedict'])  #返回一个[(jobid,与前一个job执行时间间隔),(,)]的list
        print 'sqlexec',time.ctime(),monitor['timedict']
        monitor['lock'].release()

        #如果iswarning = True ，就将有警告的job加入到sortedlist中
        jobs = list(JobsRun.objects.filter(iswarning=True))
        for i in jobs:
            sortedlist.append((i.jobid_id,0))
            print 'sqlexec',time.ctime(),sortedlist

        for key in sortedlist:
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
            job_new = JobsRun(jobid=job,iswarning=job_iswarning,warningmessage=job_warningmessage )
            job_new.save()
            time.sleep(key[1])



class EXEC(threading.Thread):
    def __init__(self,interval):
        threading.Thread.__init__(self,name= 'timedaemon')
        self.interval = interval

    def run(self):
        while True:
            t1 = TimeDaemon(60)
            t2 = SQLexec(60)
            t1.setDaemon(True)
            t2.setDaemon(True)
            t1.start()
            time.sleep(2)
            t2.start()
            t1.stop()

