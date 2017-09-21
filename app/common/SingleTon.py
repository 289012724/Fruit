# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''
class SingleTon(object):
    _instance = None
    def __new__(cls,*arg,**karwgs):
        if cls._instance is None:
            cls._instance = object.__new__(cls,*arg,**karwgs)
        return cls._instance
    

