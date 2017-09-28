# -*- coding:utf-8 -*-
'''
@email:289012724@qq.com
@author: shuiyaoyao
@telephone:13587045516
'''

import os, sys
import zipfile
from flask import current_app

# down_load = current_app.config.get("DOWNLOAD_FILE")
down_load = r"E:\Develop\Python\Flask\FruitCMS\app\static\DownLoad"


class ZipDownFile(object):
    def __init__(self, *args, **kwargs):
        object.__init__(self, *args, **kwargs)
        self.files = []

    def zipFile(self, fileName):
        destZip = zipfile.ZipFile(self.dirPath, "w")
        for eachfile in self.files:
            print "Zip file %s...to %s" % (eachfile, fileName)
            name = os.path.split(eachfile)[-1]
            destZip.write(eachfile, name)
        destZip.close()
        print "Zip folder succeed!"

    def _filter(self, fileName):
        return True

    def walkFile(self):
        parent = os.path.dirname(self.dirPath)
        print parent
        for root, dir, files in os.walk(parent, 0):
            print files
            for _file in files:
                _path = os.path.join(root, _file)
                if self._filter(_path) and not _file.endswith(".zip"):
                    self.files.append(_path)

    def Main_old(self, fileName, dirPath=None):
        if dirPath is None: dirPath = down_load
        dirPath = os.path.join(dirPath, "%s" % fileName)
        if not os.path.exists(dirPath):
            open(dirPath, "w").close()
        self.dirPath = dirPath
        self.walkFile()
        self.zipFile(fileName)
        return self.dirPath

    def Main(self, fileName, dirPath=None):
        if dirPath is None: dirPath = down_load
        dirPath = os.path.join(dirPath, "%s" % fileName)
        self.dirPath = dirPath
        self.walkFile()
        self.Move()
        for name in self.files:
            path = os.path.join(down_load, name)
            if os.path.exists(path):
                os.remove(path)
            #         self.zipFile(fileName)
        return self.dirPath


if __name__ == '__main__':
    print ZipDownFile().Main(u"2份对账单.zip")
