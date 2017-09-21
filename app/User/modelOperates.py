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
import pyModels
from ..common import md5_data
from ..common.ModelOperateNew import BaseOperate


class UserOperate(BaseOperate):
    def __init__(self):
        BaseOperate.__init__(self)
        self.Model = pyModels.user

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
        self.Model = pyModels.department

    def get_users(self, id=None):
        if id is None:
            _, departments = self.get()
            users = []
            for model in departments:
                state, models = UserOperate().get(department=model.name)
                if state:
                    users += models
            return True, users
        else:
            state, model = self.get(_id=id)
            if state and model:
                model = model[0]
                return True, UserOperate().get(department=model.name)
            return False, []


from ..common import _dataBaseUtil

_data = (UserOperate, DepartmentOperate)
_dataBaseUtil.Register("User", *_data)
