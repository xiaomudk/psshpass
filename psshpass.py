#!/usr/bin/env python
#coding:utf-8

import paramiko
import threading
import time
import sys
import os
import getopt

#远程登陆，传文件，下载文件

def info():
    """
    version info
    """
    print "parallel ssh program"
    print "version:1.0.0"
    print "author:xiaomu"
    print "xiaomudk@gmail.com"

def usage():
    """
    usage
    """
    print "Usage:"
    print "psshpass [options]... command"
    print "\t-h\t\t host_file"
    print "\t-H\t\t [user@]host[:port]"
    print "\t-l\t\t set default user(default:root)"
    print "\t-p\t\t set default password"
    print "\t-P\t\t set default Port(default:22)"
    print "\t-t\t\t timeout (default:60s),0 mean no timeout"
    print "\t-c\t\t maximum number of concurrent connections (default:1)"
    print "\t-x\t\t host,host,...  set node exclusion list on command line,This option may be used in combination with any other of the node selection options"
    print "\t-d\t\t host file directory, Conflicts with -h and -H options"
    print "\t-g\t\t groupname      target hosts in psshpass group 'groupname'"
    print "\t-X\t\t groupname      exclude hosts in psshpass group 'groupname',This option may be used in combination with any other of the node selection options "
    print "\t-o\t\t output filename"
    print "\t\t\t --version"
    print "\t\t\t --help"

#####
#读文件并执行shell
def func(ip,cmd):

    port = 50022
    username = 'root'
    password = 'xiaomu.110'

    paramiko.util.log_to_file('paramiko.log')
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())    
    s.connect(hostname = ip,port=port,username=username, password=password,key_filename='mf_zhuxixi')    
    stdin,stdout,stderr=s.exec_command(cmd)    
    print ip,'------------------------'
    print stderr.read()
    print stdout.read()    
    s.close()
    sem.release()
    



if __name__ == '__main__':
    #得到程序运行目录
    root_dir = os.path.abspath(os.path.dirname(__file__))

    #引入环境变量，让python查找模块的时候到本目录查找
    sys.path.append(root_dir)    

    #判断参数至少有一个
    if len(sys.argv) <=1:
        print "\033[31;1m[Error]===>请指定参数\033[0m"
        usage()
        sys.exit(0)

    #输入参数错误引起的异常
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h:H:l:p:P:t:c:x:d:g:X:o:',
        ["help","version",])
    except getopt.GetoptError,e:
        print "\033[31;1m[Error]===>",e,"\033[0m"
        usage()
        sys.exit(0)

    host = None
    hosts = None
    user = 'root'
    password = None 
    Port = 22
    timeout = 60
    #concurrent connections
    maxThread=1
    exclude_hosts = None
    exclude_group = None
    hosts_dir = None
    hosts_group = None
    output = None

    for op, value in opts:
        if op == '-h':
            host = value
        elif op == '-H':
            hosts = value
        elif op == '-l':
            user = value
        elif op == '-p':
            password = value
        elif op == '-P':
            Port = value
        elif op == '-t':
            timeout= value
        elif op == '-c':   #x d g X o 
            maxThread = value
        elif op == '-x':   #x d g X o 
            exclude_hosts = value
        elif op == '-d':   #x d g X o 
            hosts_dir = value
        elif op == '-g':   #x d g X o 
            hosts_group = value
        elif op == '-X':   #x d g X o 
            exclude_group = value
        elif op == '-o':   #x d g X o 
            output = value
        elif op == '--help':
            usage()
            sys.exit(0)
        elif op == '--version':
            info()
            sys.exit(0)
        else:
            usage()
            sys.exit(0)

    usage()
    sys.exit(0)
    #定义线程数
    maxThread=1

    serverlist_file = 'server_list.txt'

    sem=threading.BoundedSemaphore(maxThread)

    cmd = "ifconfig"
    
   #请用rU来读取（强烈推荐），即U通用换行模式（Universal new line mode）。该模式会把所有的换行符（\r \n \r\n）替换为\n。
    with open(serverlist_file,'rU') as f:
        # print f.readlines()
        for i in  f.readlines():
            i = i.strip()
            sem.acquire()
            threading.Thread(target=func,args=(i,cmd,)).start()

    for a in range(maxThread):   
                sem.acquire();
