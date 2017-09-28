# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''
from flask import jsonify


class Response(object):
    """
    @attention: use to return the url response object or json
    msg:respon datas 
    state: true or false
    flag : some flag data, default is None
    __str__ : return msg json data
    """

    def __init__(self):
        self.__state = None
        self.__msg = None
        self.__stateFlag = None

    @property
    def msg(self): return self.__msg

    @msg.setter
    def msg(self, value): self.__msg = value

    @property
    def state(self): return self.__msg

    @state.setter
    def state(self, value): self.__state = value

    @property
    def flag(self): return self.__stateFlag

    @flag.setter
    def flag(self, value): self.__stateFlag = value

    def __set(self, *args):
        self.state, self.msg, self.flag = args

    def ResOk(self, msg, flag=None):
        """
        @attention:  response ok data 
        @param msg:  response data
        @param flag: response flag  
        """
        self.__set(True, msg, flag)

    def ResErr(self, msg, flag=None):
        """
        @attention: response error data
        @param msg: response data
        @param flag: response flag  
        """
        self.__set(False, msg, flag)

    def __str__(self):
        return jsonify(self.msg)
