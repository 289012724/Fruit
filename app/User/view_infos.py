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
_getOperate = partial(dataUtil.getDataBase, blueprint=blueprint)
_userOperate = _getOperate("UserOperate")
_departOperate = _getOperate("DepartmentOperate")


def get_model_data(operate, model):
    state, data = operate.get_data(model, True)
    if state and data:
        return data
    return {}


@User.route("/user_info/user/<int:user_id>", methods=['POST', 'GET'])
def user_info(user_id):
    if user_id != 0:
        model = dataUtil.getModel(_userOperate, id=user_id)
    else:
        model = dataUtil.getModel(_userOperate)
    return get_model_data(_userOperate, model)


@User.route("/user_info/user/<string:username>")
def user_by_name(username):
    model = dataUtil.getModel(_userOperate, username=username)
    return get_model_data(_userOperate, model)


@User.route("/user_info/department/<int:department_id>", methods=['POST', 'GET'])
def user_by_department(department_id):
    model = dataUtil.getModel(_userOperate, department_id=department_id)
    return get_model_data(_userOperate, model)


def check_state(model):
    """
    @attention: 1:活跃,0休眠
    """
    return model.get("state") == u"活跃"


def workers():
    customer = []
    customer1 = _departOperate.get(name=u"客户")[-1]
    _supp = _departOperate.get(name=u"供应商")[-1]
    customer.extend(customer1)
    customer.extend(_supp)
    _ids = [_c for _c in customer if _c]
    state, models = _departOperate.get_users(id=None)
    if not (state and models):
        return []
    return [_m for _m in models if _m.department not in _ids]


@User.route("/user_info/UserWorker", methods=['POST', 'GET'])
def user_worker():
    """
    @attention: get all the operator names that  state property is true 
    """
    models = workers()
    data = get_model_data(_userOperate, models)
    return data


@User.route("/worker_choice/")
def user_choice():
    """
    @attention: delete "休眠状态的用户"
    """
    _workers = workers()
    _workers = get_model_data(_userOperate, _workers)
    return [(user['id'], user['username']) for user in _workers
            if check_state(user)]


@User.route("/customer_choice_all/")
def user_choice_all():
    """
    @attention: delete "休眠状态的用户"
    """
    _workers = workers()
    _workers = get_model_data(_userOperate, _workers)
    return [(user['id'], user['username']) for user in _workers]


def __choices(department_name):
    ids = dataUtil.GetDataByUrl("DepartmentId", blueprint)(department_name)
    _users = dataUtil.GetDataByUrl("UserByDepartment", blueprint)(ids)
    return [(user['id'], user['username'])
            for user in _users if check_state(user)]


@User.route("/customer_choice/")
def customer_choice():
    return __choices(u"客户")


@User.route("/customer_choice/")
def support_choice():
    return __choices(u"供应商")


@User.route("/department_info/department/<int:department_id>", methods=['POST', 'GET'])
def department_info(department_id):
    if department_id != 0:
        model = dataUtil.getModel(_departOperate, id=department_id)
    else:
        model = dataUtil.getModel(_departOperate)
    data = get_model_data(_departOperate, model)
    return data


@User.route("/department_info/name/<string:name>", methods=["POST", "GET"])
def department_id(department_name):
    if department_name:
        model = dataUtil.getModel(_departOperate, name=department_name)
        if model:
            return model[0].id
    return None


@User.route("DepartmentChoice")
def department_choice():
    model = _departOperate.Model
    models = model.query.filter(~model.name.in_([u"客户", u"供应商"])).all()
    return [(int(_m.id), _m.name) for _m in models]


@User.route("DepartmentChoiceCustomer")
def department_choice_customer():
    model = _departOperate.Model
    models = model.query.filter(model.name.in_([u"客户"])).all()
    return [(int(_m.id), _m.name) for _m in models]


@User.route("DepartmentChoiceSupporter")
def department_choice_supporter():
    model = _departOperate.Model
    models = model.query.filter(model.name.in_([u"供应商"])).all()
    return [(int(_m.id), _m.name) for _m in models]
