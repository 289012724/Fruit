# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''

import functools

data = {'int':[int,long],"long":[int,long]}


def _is_int(_test,value):
    for _c in value:
        if isinstance(_test,_c):
            return True
    return False

def _isinstance(value,types):
    if isinstance(value,types):
        return True
    return False

def types(types,isCls=False):
    def _wrapper(function):
        @functools.wraps(function)
        def wrapper(*arg,**kwargs):
            arg = list(arg)
            arg.extend(kwargs.values())  
            self=  arg[0]  
            if isCls:arg = arg[1:]      
            _name= types.__name__.split("'")[-1].split("'")[0]
            if _name in data:
                _f    = _is_int
                _t    = data[_name]
            else:
                _f    = _isinstance
                _t    = types
            if [_c for _c in arg if not _f(_c,_t)]:
                print "input should method:%s, param %s"% (function.__name__,types)
                print "input data:",arg
            else:
                if isCls:
                    return function(self,*tuple(arg))
                return function(*tuple(arg))
        return wrapper
    return _wrapper



