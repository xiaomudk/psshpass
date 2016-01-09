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
    print "\t-u\t\t set default user(default:root)"
    print "\t-p\t\t set default password"
    print "\t-P\t\t set default Port(default:22)"
    print "\t-i\t\t identity_file"
    print "\t-t\t\t timeout (default:60s),0 mean no timeout"
    print "\t-c\t\t maximum number of concurrent connections (default:1)"
    print "\t-x\t\t host,host,...  set node exclusion list on command line,This option may be used in combination with any other of the node selection options"
    print "\t-d\t\t host file directory, Conflicts with -h and -H options"
    print "\t-g\t\t groupname      target hosts in psshpass group 'groupname'"
    print "\t-X\t\t groupname      exclude hosts in psshpass group 'groupname',This option may be used in combination with any other of the node selection options "
    print "\t-o\t\t output to file"
    print "\t--cmd\t\t run cmd (Can not write)"
    print "\t--cp\t\t copy file (if not --cp, is run cmd)"
    print "\t\t\t --version"
    print "\t\t\t --help"

#####
class Autossh():
    def __init__(self,hostname, port=22, username=None, password=None, key_filename=None, timeout=None):
        '''
        登陆远程主机
        '''
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.timeout = timeout
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(hostname=self.hostname, port=self.port, username=self.username, password=self.password, \
                    key_filename=self.key_filename,timeout=self.timeout)
        except Exception as e:
            print "connect %s error: %s " % (self.hostname,e)
            sys.exit(1)

    def exec_cmd(self,cmd):

        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        returncode = stdout.channel.recv_exit_status()

        #return returncode, stdout, stderr
        #print stdout.channel.recv_exit_status()
        print """
%s:{
returncode: "%s",
stdout: "\n%s",
stderr: "\n%s",
}
        """ % (self.hostname,returncode,stdout.read(),stderr.read())
        #return  returncode,stdout, stderr
        sem.release()     #释放锁
        self.close()

    def put_file(self,localfile,remotefile):
        try:
            print localfile
            print remotefile
            sftp = self.ssh.open_sftp()
            sftp.put(localfile,remotefile)
            sftp.close()
        except Exception as e:
            print 'sftp error',self.hostname,e
        finally:
            sem.release()     #释放锁
            self.close()


    def close(self):
        self.ssh.close()
    



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
        opts, args = getopt.getopt(sys.argv[1:], 'h:H:u:p:P:i:t:c:x:d:g:X:o:',
        ["cmd","cp","help","version",])
    except getopt.GetoptError,e:
        print "\033[31;1m[Error]===>",e,"\033[0m"
        usage()
        sys.exit(0)

    print '--->',opts
    print '==',args

    host = None
    host_file = None
    user = 'root'
    password = None 
    Port = 22
    key_filename=None
    timeout = 5
    #concurrent connections
    maxThread=1
    exclude_hosts = None
    exclude_group = None
    hosts_dir = None
    hosts_group = None
    output = None
    copyfile = False

    for op, value in opts:
        if op == '-h':
            host_file = value
        elif op == '-H':
            host = value
        elif op == '-u':
            user = value
        elif op == '-p':
            password = value
        elif op == '-P':
            Port = value
        elif op == '-i':
            key_filename = value
        elif op == '-t':
            timeout = value
        elif op == '-c':   #x d g X o 
            maxThread = int(value)
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
        elif op == '--cp':
            copyfile = True
        elif op == '--help':
            usage()
            sys.exit(0)
        elif op == '--version':
            info()
            sys.exit(0)
        else:
            print "\033[31;1m[Error]===>option %s not recognized:\033[0m" % op
            usage()
            sys.exit(0)

    print '1111111111'
    #定义线程数

    sem=threading.BoundedSemaphore(maxThread)

    if copyfile:
        localfile = args[0]
        remotefile = args[1]
    else:
        cmd = ' '.join(args)


   #请用rU来读取（强烈推荐），即U通用换行模式（Universal new line mode）。该模式会把所有的换行符（\r \n \r\n）替换为\n。
    with open(host_file,'rU') as f:
        # print f.readlines()
        for i in  f.readlines():
            i = i.strip()
            sem.acquire()
            conn = Autossh(hostname=i,port=Port,username=user,password=password,key_filename=key_filename,timeout=timeout)
            if copyfile:
                threading.Thread(target=conn.put_file,args=(localfile,remotefile,)).start()
            else:
                threading.Thread(target=conn.exec_cmd,args=(cmd,)).start()
                # conn.exec_cmd(cmd)


    #再次加下锁，保证上面的并发线程全部执行完（上面的锁被释放完）
    for a in range(maxThread):   
                sem.acquire();
