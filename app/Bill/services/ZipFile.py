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

    def zip(self, file_name):
        destination = zipfile.ZipFile(self.dirPath, "w")
        for each in self.files:
            print "Zip file %s...to %s" % (each, file_name)
            name = os.path.split(each)[-1]
            destination.write(each, name)
        destination.close()
        print "Zip folder succeed!"

    def _filter(self, file_name):
        return True

    def walk_file(self):
        parent = os.path.dirname(self.dirPath)
        print parent
        for root, dir, files in os.walk(parent, 0):
            print files
            for _file in files:
                _path = os.path.join(root, _file)
                if self._filter(_path) and not _file.endswith(".zip"):
                    self.files.append(_path)

    def main(self, file_name, direction=None):
        if direction is None:
            direction = down_load
        direction = os.path.join(direction, "%s" % file_name)
        self.dirPath = direction
        self.walk_file()
        self.Move()
        for name in self.files:
            path = os.path.join(down_load, name)
            if os.path.exists(path):
                os.remove(path)
                #         self.zipFile(fileName)
        return self.dirPath


if __name__ == '__main__':
    print ZipDownFile().main(u"2份对账单.zip")
