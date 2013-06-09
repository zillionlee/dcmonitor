# -*- coding: UTF-8 -*-
'''
发送txt文本邮件
'''
import smtplib
import sys
from email.mime.text import MIMEText

mail_host="220.181.12.17"  #设置服务器
mail_user="123"    #用户名
mail_pass="123"   #口令
mail_postfix="163.com"  #发件箱的后缀

def send_mail(to_list,sub,content):
    me="数据库监控"+"<"+mail_user+"@"+mail_postfix+">"
    msg = MIMEText(content,_subtype='plain',_charset='gb2312')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = str(to_list)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user,mail_pass)
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        return True
    except Exception, e:
        print str(e)
        return False

if __name__ == '__main__':
    mailto_list=['abc@gmail.com',]
    if send_mail(mailto_list,"hello","hello world！啦啦啦啦啦"):
        print "发送成功"
    else:
        print "发送失败"