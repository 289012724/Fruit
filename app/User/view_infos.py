# usr/bin/env
# -*- coding:utf-8 -*-
"""
@version: triweb version 1.0
@author: shuiyaoyao
@contact: 289012724@qq.com
@software: PyCharm
@time: 2016/10/08 10:57
"""
from . import User
from ..common._annotation import json_return
from ..common.DataBaseOperate import _dataBaseUtil as dataUtil
from functools import partial

blueprint = "User"
_getOper = partial(dataUtil.getDataBase, blueprint=blueprint)
_userOper = _getOper("UserOperate")
_departOper = _getOper("DepartmentOperate")


def get_model_data(operate, model):
    state, data = operate.get_data(model, True)
    if state and data:
        return data
    return {}


@User.route("/user_info/user/<int:user_id>", methods=['POST', 'GET'])
def UserInfo(user_id):
    if user_id != 0:
        model = dataUtil.getModel(_userOper, _id=user_id)
    else:
        model = dataUtil.getModel(_userOper)
    return get_model_data(_userOper, model)


@User.route("/user_info/user/<string:username>")
def UserByName(username):
    model = dataUtil.getModel(_userOper, username=username)
    return get_model_data(_userOper, model)


@User.route("/user_info/department/<int:department_id>", methods=['POST', 'GET'])
def UserByDepartment(department_id):
    model = dataUtil.getModel(_userOper, department_id=department_id)
    return get_model_data(_userOper, model)


def CheckState(modelData):
    """
    @attention: 1:活跃,0休眠
    """
    return modelData.get("state") == u"活跃"


def Workers():
    state, models = _userOper.get(department=u"员工")
    print(111, state, models)
    return models or []


@User.route("/user_info/UserWorker", methods=['POST', 'GET'])
def UserWorker():
    """
    @attention: get all the operator names that  state property is true 
    """
    models = Workers()
    data = get_model_data(_userOper, models)
    print(data)
    return data


@User.route("/worker_choice/")
def UserChoice():
    """
    @attention: delete "休眠状态的用户"
    """
    workers = Workers()
    workers = get_model_data(_userOper, workers)
    return [(user['_id'], user['username']) for user in workers
            if CheckState(user)]


@User.route("/customer_choice_all/")
def UserChocieAll():
    """
    @attention: delete "休眠状态的用户"
    """
    workers = Workers()
    workers = get_model_data(_userOper, workers)
    return [(user['id'], user['username']) for user in workers]


def __Choices(department_name):
    ids = dataUtil.GetDataByUrl("DepartmentId", blueprint)(department_name)
    _users = dataUtil.GetDataByUrl("UserByDepartment", blueprint)(ids)
    return [(user['id'], user['username'])
            for user in _users if CheckState(user)]


@User.route("/customer_choice/")
def CustomerChoice():
    return __Choices(u"客户")


@User.route("/customer_choice/")
def SupportChoice():
    return __Choices(u"供应商")


@User.route("/department_info/department/<int:department_id>", methods=['POST', 'GET'])
def DepartmentInfo(department_id):
    if department_id != 0:
        model = dataUtil.getModel(_departOper, _id=department_id)
    else:
        model = dataUtil.getModel(_departOper)
    data = get_model_data(_departOper, model)
    return data


@User.route("/department_info/name/<string:name>", methods=["POST", "GET"])
def DepartmentId(department_name):
    if department_name:
        model = dataUtil.getModel(_departOper, name=department_name)
        if model:
            return model[0].id
    return None


@User.route("department_choice")
def DepartmentChocie():
    return [(u"员工", u"员工")]


@User.route("department_choice_customer")
def DepartmentChoiceCustomer():
    return [(u"客户", u"客户")]


@User.route("department_choice_supportor")
def DepartmentChoiceSupportor():
    return [(u"供应商", u"供应商")]
