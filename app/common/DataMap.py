# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''

from .SingleTon import SingleTon
from ._types    import types

class DataMap(SingleTon):
    def __init__(self):
        SingleTon.__init__(self)
        self.__dataBaseMap = {}
        self.__formMap     = {}
    
    @types(list)
    def setMap(self,value):
        """
        @attention: set the target data diction
        @param value: list object
        @return: none 
        """
        _obj = self.__temp_obj
        for ids,val in enumerate(value):
            if _obj.has_key(ids):
                print "key exist",ids,val
            else:
                _obj[ids] = val
    @property
    def dataBaseMap(self):self.__dataBaseMap
    
    @dataBaseMap.setter
    def dataBaseMap(self,value):
        self.__temp_obj = self.__dataBaseMap
        self.setMap(value)
    
    @property
    def formMap(self):return self.__formMap
    
        
    @formMap.setter
    @types(list)
    def formMap(self,value):
        self.__temp_obj = self.__formMap
        self.setMap(value)
    