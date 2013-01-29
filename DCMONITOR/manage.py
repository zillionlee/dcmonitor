#!/usr/bin/env python
import os
import sys


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DCMONITOR.settings")


    from monitor.execsql import RunThreading
    t1 = RunThreading(300)
    t1.setDaemon(True)
    t1.start()

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


'''
    from monitor.execscripts import TimeDaemon,SQLexec
    t1 = TimeDaemon(60)
    t2 = SQLexec(60)
    t1.setDaemon(True)
    t2.setDaemon(True)
    t1.start()
    time.sleep(2)
    t2.start()
'''




