#coding=utf-8
__author__ = 'ziliangl'
#后台运行脚本，

if __name__=="__main__":
    import os
    import sys
    project_path= os.path.abspath(os.path.dirname(__file__)).replace('\\','/')
    print project_path
    if project_path not in sys.path :
        sys.path.append(project_path)
        #sys.path.append(os.path.join(project_path,'../').replace('\\','/'))
        sys.path.append(os.path.join(project_path,'DCMONITOR/').replace('\\','/'))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DCMONITOR.settings")
    print sys.path
    from monitor.execsql import RunThreading
    t1 = RunThreading(300)
    #t1.setDaemon(True)
    t1.start()

