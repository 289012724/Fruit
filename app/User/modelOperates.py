# usr/bin/env
# -*- coding:utf-8 -*-
"""
@version: triweb version 1.0
@author: shuiyaoyao
@contact: 289012724@qq.com
@software: PyCharm
@file: modelOperates.py
@time: 2016/7/9 0009
"""
import models
from ..common import md5_data
from ..common.BaseModelOperate import BaseOperate


class UserOperate(BaseOperate):
    def __init__(self):
        BaseOperate.__init__(self)
        self.Column = ['username', 'password', 'telephone', 'department_id', "state"]
        self.Model = models.user

    def _get_row(self, model, _key):
        _row = []
        for key in _key:
            if key == 'password':
                continue
            elif key == 'department_id':
                property_data = model.department.name
            else:
                property_data = getattr(model, key)
            _row.append((key, property_data))
        return _row

    def check_password(self, username, password):
        password = md5_data(password.strip())
        state, user = self.get(username=username, password=password)
        if state and user:
            return True, user
        return False, None

    def change_password(self, model, password):
        model.password = md5_data(password)
        self.ModelList = model
        return self.update()


class DepartmentOperate(BaseOperate):
    def __init__(self):
        BaseOperate.__init__(self)
        self.Column = ['name', 'description']
        self.Model = models.department

    def get_users(self, id=None):
        if id is None:
            state, departments = self.get()
            users = []
            for model in departments:
                users += model.users.all()
            return True, users
        else:
            state, model = self.get(id=id)
            if state and model:
                model = model[0]
                return True, model.users.all()
            return False, []


from ..common import _dataBaseUtil

_data = (UserOperate, DepartmentOperate)
_dataBaseUtil.Register("User", *_data)
