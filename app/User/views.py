# usr/bin/env
# -*- coding:utf-8 -*-
"""
@version: triweb version 1.0
@author: shuiyaoyao
@contact: 289012724@qq.com
@software: PyCharm
@file: views.py
@time: 2016/7/4 0004  10:57
"""
from . import User
from flask_login import login_user, current_user, logout_user
from flask import render_template, redirect, url_for, request, jsonify
from .. import load_manager

from ..common import json_return
from ..common import _dataBaseUtil as dataUtil

from .services.InitPage import _initPage
from functools import partial
from flask import session
from .page_config import page_table_configs
from .. import basedir
import time

_getOperate = partial(dataUtil.getDataBase, blueprint="User")


@load_manager.user_loader
def load_user(user_id):
    user = dataUtil.getModel(_getOperate("UserOperate"), id=int(user_id))
    if user:
        return user[0]
    return None


@User.route("/operate_date")
def operate_date():
    return "%s" % session[current_user.username]


@User.route("/load_init_moth", methods=['POST', 'GET'])
def load_init_moth():
    return jsonify(session.get(current_user.username + '_moth') or 0)


@User.route("/modifyDate", methods=['POST', 'GET'])
def modifyDate():
    date = request.form.get("date")
    session[current_user.username] = time.strftime("%a, %d %b %Y %H:%M:%S GMT",
                                                   dataUtil.TimestampToStruct(dataUtil.MakeTime(date)))
    session[current_user.username + "_moth"] = request.form.get("moth")
    return jsonify(date)


@User.route('/login', methods=['POST', 'GET'])
def login():
    ok, _str = _initPage.check_license(basedir)
    state, form, model = _initPage.get_login()

    if not (state and ok):
        return render_template('User/login.html', form=form, state=ok, _str=_str)

    if not model:
        return jsonify(dataUtil.ResError(u"用户或密码错误"))

    if model.state == u"休眠":
        return dataUtil.ResErrorJson("休眠状态的用户不能登录系统")

    session[model.username] = form.operate_date.data
    session[model.username + "_moth"] = form.operate_moth.data
    login_user(model, remember=False)
    return dataUtil.ResOkJson(url_for("index"))


@User.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop(current_user.username, None)
    logout_user()
    return redirect(url_for('.login'))


@User.route('/addUser/<string:roleType>', methods=['POST', 'GET'])
@json_return
def add_user(roleType):
    data = _initPage.register(request.form.get("operType"))
    return data


@User.route('/deleteUser/<string:roleType>', methods=['POST', 'GET'])
def delete_user(roleType):
    state = _initPage.delete(roleType)
    if state:
        return dataUtil.ResOkJson(u"删除成功")
    return dataUtil.ResErrorJson(u"删除失败")


@User.route('/changePass', methods=['POST', 'GET'])
def change_pass():
    state, form = _initPage.change_pass()
    if state:
        return redirect(url_for('.login'))
    return render_template('User/change_pass.html', form=form, username=current_user.username)


@User.route("/resetPass/<int:userId>", methods=["POST", "GET"])
def resetPass(userId):
    state, form, model = _initPage.reset_pass(userId)
    if state:
        return "1"
    target = url_for(".resetPass", userId=userId)
    return render_template('User/resetPass.html', target=target, form=form, username=model.username)


@User.route('/modfiy_data/<string:roleType>', methods=['GET', 'POST'])
def modify_data(roleType):
    model = _initPage.modify_cell(roleType)
    if not model:
        return jsonify([2, {''}, u'修改失败'])

    if roleType.lower() == 'department':
        key = 'name'
    else:
        key = "username"
    message = u'修改--%s--成功' % model[key]
    return jsonify([1, model, message])


@User.route('/modify/<string:roleType>/<int:user_id>', methods=['POST', 'GET'])
def modify(roleType, user_id):
    form, choices = _initPage.register_page(roleType, user_id)
    return render_template('User/register.html',
                           form=form, choices=choices,
                           roleType=roleType,
                           targetUrl=url_for('.modify_data', roleType=roleType),
                           _modify=True, user_id=user_id)


@User.route('/page_control/<string:roleType>', methods=['GET', 'POST'])
def get_index_page(roleType):
    form, choices = _initPage.register_page(roleType, -1)
    if roleType == "User":
        form.password.data = "888888"
    return render_template('User/register.html',
                           form=form, choices=choices,
                           roleType=roleType,
                           targetUrl=url_for('.add_user', roleType=form.type),
                           _modify=False, operType=roleType)


@User.route('/load_all/<string:roleType>', methods=['GET', 'POST'])
@json_return
def load_all_user(roleType):
    return _initPage.load_data(roleType)


@User.route('/table_config/<string:roleType>')
@json_return
def table_config(roleType):
    _key = roleType.lower()
    if roleType.lower() != "department":
        _key = "user"
    return page_table_configs.get(_key)


@User.route('/load_datagrid/<string:roleType>')
def load_datagrid(roleType):
    return render_template("User/table_datagrid.html", roleType=roleType)


@User.route('/load_user/<int:user_id>')
def get_user_by_id(user_id):
    model = dataUtil.getModel(_getOperate("UserOperate"), id=user_id)
    if model:
        return model[0].username
    return ""


@User.route('/all_users/<string:roleType>')
@json_return
def all_users(roleType):
    _ids = ["User", "Custemer", "Supporter"].index(roleType) or 0
    name = _initPage.get_supporter_name(_ids)
    return name


@User.route("/search/<string:roleType>", methods=['GET', 'POST'])
def search(roleType):
    roleType = roleType.lower()
    state, formOrData = _initPage.user_search(roleType)
    if state:
        return jsonify(formOrData)
    return render_template("User/search.html", form=formOrData, roleType=roleType)


import view_infos
