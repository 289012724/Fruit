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
        model = dataUtil.getModel(_userOper, id=user_id)
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
    _cust = []
    _cust1 = _departOper.get(name=u"客户")[-1]
    _supp = _departOper.get(name=u"供应商")[-1]
    _cust.extend(_cust1)
    _cust.extend(_supp)
    _ids = [_c for _c in _cust if _c]
    state, models = _departOper.get_users(id=None)
    if state and models:
        models = [_m for _m in models if _m.department not in _ids]
    else:
        models = []
    return models


@User.route("/user_info/UserWorker", methods=['POST', 'GET'])
def UserWorker():
    """
    @attention: get all the operator names that  state property is true 
    """
    models = Workers()
    data = get_model_data(_userOper, models)
    return data


@User.route("/worker_choice/")
def UserChoice():
    """
    @attention: delete "休眠状态的用户"
    """
    workers = Workers()
    workers = get_model_data(_userOper, workers)
    return [(user['id'], user['username']) for user in workers
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
        model = dataUtil.getModel(_departOper, id=department_id)
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
    model = _departOper.model
    models = model.query.filter(~model.name.in_([u"客户", u"供应商"])).all()
    return [(int(_m.id), _m.name) for _m in models]


@User.route("department_choice_customer")
def DepartmentChoiceCustomer():
    model = _departOper.model
    models = model.query.filter(model.name.in_([u"客户"])).all()
    return [(int(_m.id), _m.name) for _m in models]


@User.route("department_choice_supportor")
def DepartmentChoiceSupportor():
    model = _departOper.model
    models = model.query.filter(model.name.in_([u"供应商"])).all()
    return [(int(_m.id), _m.name) for _m in models]
