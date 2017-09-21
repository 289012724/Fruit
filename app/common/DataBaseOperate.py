# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email : 289012724@qq.com
'''

import SingleTon
from _types import types
from flask import current_app, session
from flask import jsonify
from flask_login import current_user
from functools import partial
import time


class _DataBaseOperate(SingleTon.SingleTon):
    def __init__(self):
        SingleTon.SingleTon.__init__(self)
        self.__databaseMap = {}
        self.__blueprint = None

    def ResOk(self, msg):
        return {"state": True, 'msg': msg}

    def ResError(self, msg):
        if isinstance(msg, dict):
            _error = ""
            for _k, _v in msg.items():
                _error += "%s:%s" % (_k, ",".join(_v))
        elif isinstance(msg, list):
            _error = ";".join(msg)
        else:
            _error = msg
        return {'state': False, "msg": _error}

    def ResOkJson(self, msg):
        return jsonify(self.ResOk(msg))

    def ResErrorJson(self, msg):
        return jsonify(self.ResError(msg))

    @property
    def CurrentDate(self):
        if session.has_key(current_user.username):
            _time = session.get(current_user.username)
            GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
            _time = time.strptime("%s" % _time, GMT_FORMAT)
        else:
            _time = time.localtime()
        return _time

    @property
    def CurrentDateStr(self):
        return self.FormatTime(self.CurrentDate)

    def MakeTime(self, timeStr, _format="%Y-%m-%d %H:%M:%S"):
        """
        @attention: 获取对应格式日期的时间戳
        @param timeStr: 日期字符串
        @param _format: 日期的格式  
        """
        try:
            struct = time.strptime(timeStr, _format)
        except:
            struct = time.strptime(timeStr, "%Y-%m-%d")
        return time.mktime(struct)

    def FormatTime(self, timeObj):
        """
        @attention: 将日期结构数据格式化输出
        """
        return time.strftime("%Y-%m-%d", timeObj)

    def TimestampToStruct(self, timestamp):
        """
        @attention: 将时间戳转化为日期结构体
        """
        return time.localtime(timestamp)

    def IsLessDate(self, firstStr, second):
        firstStr = str(firstStr)
        second = str(second)
        _ts1 = self.MakeTime(firstStr)
        _ts2 = self.MakeTime(second)
        return float(_ts1) < float(_ts2)

    def GetPrevData(self, timeStr, day=0, hour=0, _format="%Y-%m-%d %H:%M:%S"):
        _stamp = self.MakeTime(timeStr, _format)
        _number = day * 24 + hour
        _stamp += _number * 3600
        _time = self.TimestampToStruct(_stamp)
        return self.FormatTime(_time)

    def GetInitPrevDate(self, timeStr, day=None):
        """
        @attention: 获取系统初始化的是设置的显示数据月份
        """
        if day is None:
            day = session.get(current_user.username + "_moth") or 0
        day = float(day)
        if day == 0:
            return timeStr
        else:
            day = day * 31
            stamp = self.MakeTime(timeStr)
            prev = stamp - day * 24 * 3600
            prev = self.FormatTime(self.TimestampToStruct(prev))
            return prev

    @property
    def Blueprint(self):
        return self.__blueprint

    @Blueprint.setter
    @types(basestring)
    def Blueprint(self, value):
        self.BluePrint = value

    @property
    def DataBaseMap(self):
        return self.__databaseMap

    def getBlueprint(self, blueprint):
        if blueprint: self.BluePrint = blueprint
        return self.BluePrint

    def Register(self, blueprint, *args, **kwgs):
        self.BluePrint = blueprint
        if not self.DataBaseMap.has_key(blueprint):
            self.DataBaseMap[blueprint] = {}
        if args:
            _data = [(c.__name__, c) for c in args]
            kwgs.update(_data)
        [self.setDataBaseMap(key, value, self.BluePrint) for key, value in kwgs.items()]

    def GetDataByUrl(self, controllerName, blueprint):
        if blueprint:
            controllerName = "%s.%s" % (blueprint, controllerName)
        app = current_app._get_current_object()
        method = app.view_functions[controllerName]
        return method

    def setDataBaseMap(self, key, value, blueprint):
        if not self.__databaseMap.has_key(blueprint):
            self.__databaseMap[blueprint] = {}
        _obj = self.__databaseMap.get(blueprint)
        if _obj.has_key(key):
            print "key exist", key
        else:
            _obj[key] = value

    def getDataBase(self, key, blueprint=None):
        blueprint = self.getBlueprint(blueprint)
        if self.DataBaseMap.has_key(blueprint):
            _obj = self.DataBaseMap.get(blueprint)
            if _obj.has_key(key):
                return _obj.get(key)()
        print "key not exist", blueprint, key

    def getModel(self, dataBase, **kwgs):
        if dataBase:
            state, model = dataBase.get(**kwgs)
            if state and model:
                return model

    def GetPartial(self, blueprint):
        return partial(self.getDataBase, blueprint=blueprint)


_dataBaseUtil = _DataBaseOperate()
