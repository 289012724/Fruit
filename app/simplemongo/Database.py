#!/usr/bin/env python  
# encoding: utf-8  
# ----------------------------------------------
#
#   
#
# ----------------------------------------------
""" 
@author: MicoMeter
@time: 2017/9/15 下午4:21 
"""
from pymongo import MongoClient
from bson.objectid import ObjectId


class Database:
    def __init__(self):
        self.__con = None
        self.__app = None

    def init_app(self, app):
        self.__con = MongoClient(host="localhost", port=app.config["PORT"])
        self.__app = app

    def get_database(self):
        return self.__con[self.__app.config["DATABASE"] or "test"]

    def __init_db(self):
        db = self.get_database()
        db.departments.insert({
            "name": "admin",
            "description": "系统管理",
        })
        db.departments.insert(
            {
                "name": "custemer",
                "description": "客户",
            }
        )
        db.departments.insert(
            {
                "name": "supporter",
                "description": "客户",
            }
        )
        db.departments.insert(
            {
                "name": "user",
                "description": "员工",
            }
        )
        db.users.insert({
            "username": "admin",
            "password": "e10adc3949ba59abbe56e057f20f883e",
            "department": "admin",
            "telephone": "",
            "state": "活跃",
        })

    def default_init(self):
        db = self.get_database()
        if db.users.find().count() == 0:
            self.__init_db()
