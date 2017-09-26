# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''


from flask_wtf      import Form
from flask          import jsonify
import time,datetime
import json
import hashlib
import functools
import SingleTon


    
def set_form_data(form,_data):
    for key,value in _data.items():
        if form.data.has_key(key):
            setattr(getattr(form,key),'data',value)
        else:
            print "%s not in form %s"%(key,form)
    return form

def current_datetime():
    date = "%s" % (time.strftime('%Y-%m-%d', time.localtime()))
    return date

def str_to_datatime(string):
    return datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S").date()
    
def struct_time(data):
    if isinstance(data,str):
        _data = time.strptime("%s"%data, "%Y-%m-%d %H:%M:%S")
    else:
        _data = time.strftime("%Y-%m-%d",data)
    return  _data

def load_json_data(data):
    data = json.loads(data)
    return data

def load_data_list(args):
    _data = []
    def _f(_c):
        if isinstance(_c,list):map(_f,_c)
        else:_data.append(_c)
    map(_f,args)
    return _data
            
def md5_data(data):
    md = hashlib.md5()
    md.update(data)
    return md.hexdigest()

def _form_arg(form, model):
    item_keys = form.data.keys()
    _data     = form.data
    for key in item_keys:
        try:
            _data[key] = _data[key].strip()
        except:
            pass
    return _data


def form_data_class(function):
    @functools.wraps(function)
    def wrapper(self, arg, model):
        _data = arg
        if isinstance(arg[0], Form):
            _data = _form_arg(arg[0], model)
        return function(self, _data, model)

    return wrapper





def json_return(function):
    @functools.wraps(function)
    def wrapper(*arg,**kwargs):
        return jsonify(function(*arg,**kwargs))
    return wrapper


def _get_arg_by_dict(_dict,parames):
    _datas = []
    for _k in parames:
        if _dict.has_key(_k):
            _datas.append(_dict.get(_k))
    return _datas

def _get_by_arg(arg, parames):
    _data = []
    for _carg in arg:
        if isinstance(_carg,Form):
            _carg = _carg.data
        if isinstance(_carg,dict):
            _data.extend(_get_arg_by_dict(_carg,parames))
        elif isinstance(_carg,list) or isinstance(_carg,tuple):
            _data.extend(_carg)
        else:
            _data.append(_carg)
    return _data

#===============================================================================
# set the model property if the input data has model property key
#===============================================================================
def get_parameters(function):
    @functools.wraps(function)
    def wrapper(self, *arg, **kwargs):
        _data = _get_by_arg(arg, self.Column)
        [_data.append(kwargs[key]) 
         for key in self.Column 
         if kwargs.has_key(key)]
        _data = tuple(_data)
        return function(self, *_data, **kwargs)
    return wrapper

def exception_show_class(function):
    @functools.wraps(function)
    def wrapper(self, *arg, **kwargs):
        try:
            return function(self, *arg, **kwargs)
        except Exception, e:
            return False, e.message
    return wrapper





