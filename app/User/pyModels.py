#!/usr/bin/env python  
# encoding: utf-8  
# ----------------------------------------------
#
#   
#
# ----------------------------------------------
""" 
@author: MicoMeter
@time: 2017/9/15 下午4:39 
"""

# usr/bin/env
# -*- coding:utf-8 -*-
"""
@version: triweb version 1.0
@author: shuiyaoyao
@contact: 289012724@qq.com
@software: PyCharm
@file: models.py
@time: 2016/7/4 0004 10:57
"""
from .. import database as db
from ..simplemongo import Document
from ..common import md5_data, objectId_to_string
from bson.objectid import ObjectId
from flask_login import UserMixin


class department(Document, UserMixin):
    col = db.get_database()["departments"]
    struct = {
        'id': ObjectId,
        'name': str,
        'description': str,
    }

    @classmethod
    @objectId_to_string
    def Init(cls, **arg):
        return cls.new(**arg)


class user(Document, UserMixin):
    col = db.get_database()["users"]
    struct = {
        'id': ObjectId,
        'username': str,
        'password': str,
        'telephone': str,
        'department': str,
        'state': str,
    }

    @classmethod
    @objectId_to_string
    def Init(cls, **arg):
        if arg["password"] and len(arg["password"]) != 32:
            arg["password"] = md5_data(arg["password"])
        data = cls.new(**arg)
        return data
