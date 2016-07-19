# -*- coding: utf-8 -*-

__author__ = 'Simshang'
__mail__ = 'shang.yan@foxmail.com'
__date__ = '2016-06-14'
__version = 0.1

import os
import sys
import shutil
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
        # print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

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

    def move(self,src,bakDir):
        if os.path.isfile(src):
            try:
                shutil.copy(src,bakDir)
            except:
                pass
        elif os.path.isdir(src):
            for item in os.listdir(src):
                itemsrc = os.path.join(src,item)
                self.move(itemsrc,bakDir)


    def upload(self, src,dstDir):
        try:
            filetype, filename = self.__filetype(src)
        except:
            pass
        #self.initEnv()
        if filetype == _LOCAL_DIR:
            self.srcDir = src
            self.uploadDir(self.srcDir,dstDir)
        elif filetype == _LOCAL_FILE:
            try:
                uploader.ftp.cwd(dstDir)
            except:
                uploader.ftp.mkd(dstDir)
                uploader.ftp.cwd(dstDir)
            self.uploadFile(src, filename)

        #self.clearEnv()

'''
ftp_config={
    "ip":"FTP Server IP",
    "user":"Username",
    "password":"Password"
}
'''

ftp_config={
    "ip":"123.206.27.134",
    "user":"ftpuser",
    "password":"shang"
}


# 指定本地目录
srcDir = "D:\\ftpProject\\test"
backupDir = "D:\\ftpProject\\testBackup"

# 指定多个远程目录
dstDirs=[
    "/home/ftpuser/upload/MIAOPAI/PKU/VIDEO"
]


if __name__ == '__main__':
    while 1:
        tempDir = os.listdir(srcDir)
        uploader = Uploader()

        dateTemp = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        timeDir = backupDir + '\\' + dateTemp
        if not os.path.exists(timeDir):
            os.makedirs(timeDir)
        else:
            pass

        uploader.setFtpParams(ftp_config["ip"], ftp_config["user"], ftp_config["password"])
        uploader.initEnv()

        for dstDirsNum in range(len(dstDirs)):
            for localNum in range(len(tempDir)):
                Dir = srcDir + '\\' + tempDir[localNum]
                # uploader.upload(srcDir, dstDirs[dstDirsNum])

                if os.path.isfile(Dir):
                    uploader.upload(Dir, dstDirs[dstDirsNum])
                else:
                    dstdir = dstDirs[dstDirsNum] +'/'+ tempDir[localNum]
                    try:
                        uploader.ftp.cwd(dstDirs[dstDirsNum])
                    except:
                        uploader.ftp.mkd(dstDirs[dstDirsNum])
                        uploader.ftp.cwd(dstDirs[dstDirsNum])
                    uploader.upload(Dir,tempDir[localNum])

        uploader.clearEnv()

        for delNum in range(len(tempDir)):
            Dirs = srcDir + "\\" + tempDir[delNum]

            uploader.move(Dirs,timeDir)
            uploader.delete(Dirs)
            try:
                os.rmdir(Dirs)
            except:
                pass

        print "This task is done!\n----------------------------\nWaiting for next task ......\n"
        # 设置轮询时间
        time.sleep(10)