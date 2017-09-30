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
from ..common import md5_data
from flask_login import UserMixin


class department(db.Model):
    __tablename__ = 'fruit_departments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), unique=True)
    description = db.Column(db.Text)
    users = db.relationship('user', backref='department', lazy='dynamic')

    def Init(self, arg):
        self.name, self.description = arg

    def __str__(self):
        return '%r-%r' % (self.name, self.description)


class user(db.Model, UserMixin):
    __tablename__ = 'fruit_users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(32))
    telephone = db.Column(db.String(11))
    department_id = db.Column(db.Integer, db.ForeignKey('fruit_departments.id'))
    state = db.Column(db.String(20), default=u'活跃')

    def Init(self, arg):
        self.username, self.password, self.telephone, self.department_id, self.state = arg
        self.password = md5_data(self.password)

    def __str__(self):
        return 'user:%s,%s,%s' % (self.id, self.telephone, self.department_id)
