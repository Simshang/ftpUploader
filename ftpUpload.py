# -*- coding: utf-8 -*-

__author__ = 'Simshang'
__mail__ = 'shang.yan@foxmail.com'
__date__ = '2016-06-14'
__version = 0.1

import os
import sys
import time
from ftplib import FTP

_LOCAL_FILE = 'FILE'
_LOCAL_DIR = 'DIR'


class Uploader(object):
    '''
    @note: upload local file or dirs recursively to ftp server
    '''

    def __init__(self):
        self.ftp = None

    def __del__(self):
        pass

    def setFtpParams(self, ip, username, pwd, port=21, timeout=60):
        self.ip = ip
        self.uname = username
        self.pwd = pwd
        self.port = port
        self.timeout = timeout

    def initEnv(self):
        if self.ftp is None:
            self.ftp = FTP()
            print '### connect ftp server: %s ...' % self.ip
            self.ftp.connect(self.ip, self.port, self.timeout)
            self.ftp.login(self.uname, self.pwd)
            print self.ftp.getwelcome()

    def clearEnv(self):
        if self.ftp:
            self.ftp.close()
            print '### disconnect ftp server: %s!' % self.ip
            self.ftp = None

    def uploadDir(self, localdir='./', remotedir='./'):
        if not os.path.isdir(localdir):
            return
        try:
            self.ftp.cwd(remotedir)
        except:
            self.ftp.mkd(remotedir)
            self.ftp.cwd(remotedir)
        for file in os.listdir(localdir):
            src = os.path.join(localdir, file)
            DstDir = remotedir + '/' + file
            if os.path.isfile(src):
                self.uploadFile(src, file)
            elif os.path.isdir(src):
                try:
                    self.ftp.mkd(file)
                except:
                    sys.stderr.write('!!! %s is existed \n' % DstDir)
                self.uploadDir(src, file)
        self.ftp.cwd('..')

    def uploadFile(self, localpath, remotepath='./'):
        if not os.path.isfile(localpath):
            return
        self.ftp.storbinary('STOR ' + remotepath, open(localpath, 'rb'))

        confirmFile = localpath+'.ok'
        okfile = open(confirmFile,'w')
        okfile.close()
        loadConfirmFile = remotepath + '.ok'
        self.ftp.storbinary('STOR ' + loadConfirmFile, open(localpath, 'rb'))
        os.remove(confirmFile)

        print '+++ upload %s to %s:%s is finished' % (localpath, self.ip, remotepath)

    def __filetype(self, src):
        if os.path.isfile(src):
            index = src.rfind('\\')
            if index == -1:
                index = src.rfind('/')
            return _LOCAL_FILE, src[index + 1:]
        elif os.path.isdir(src):
            return _LOCAL_DIR, ''

    def delete(self,src):
        if os.path.isfile(src):
            try:
                os.remove(src)
            except:
                pass
        elif os.path.isdir(src):
            for item in os.listdir(src):
                itemsrc = os.path.join(src, item)
                self.delete(itemsrc)
                if os.path.isdir(itemsrc):
                    os.rmdir(itemsrc)


    def upload(self, src,dstDir):
        filetype, filename = self.__filetype(src)
        self.initEnv()
        if filetype == _LOCAL_DIR:
            self.srcDir = src
            self.uploadDir(self.srcDir,dstDir)
        elif filetype == _LOCAL_FILE:

            dstfile = dstDir + '/' + filename
            try:
                self.ftp.cwd(dstDir)
            except:
                self.ftp.mkd(dstDir)
                self.ftp.cwd(dstDir)
            self.uploadFile(src, filename)

        self.clearEnv()


ftp_config={
    "ip":"FTP Server IP",
    "user":"Username",
    "password":"Password"
}


# 指定本地目录
srcDir = "D:\\test"
# 指定多个远程目录
dstDirs=[
    "./a",
    "./b"
]


if __name__ == '__main__':
    while 1:
        tempDir = os.listdir(srcDir)
        uploader = Uploader()
        uploader.setFtpParams(ftp_config["ip"], ftp_config["user"], ftp_config["password"])
        for dstDirsNum in range(len(dstDirs)):
            for localNum in range(len(tempDir)):
                Dir = srcDir + '\\' + tempDir[localNum]
                if os.path.isfile(Dir):
                    uploader.upload(Dir, dstDirs[dstDirsNum])
                else:
                    uploader.upload(srcDir,dstDirs[dstDirsNum])

        for delNum in range(len(tempDir)):
            Dirs = srcDir + "\\" + tempDir[delNum]
            uploader.delete(Dirs)
            try:
                os.rmdir(Dirs)
            except:
                pass
        print "本次任务成完成.\n--------------------------------------------\n"
        # 设置轮询时间
        time.sleep(10)



