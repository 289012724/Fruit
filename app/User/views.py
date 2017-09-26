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
from .                      import User
from flask_login            import login_user, current_user, logout_user
from flask                  import render_template, redirect, url_for, request, jsonify, flash
from ..                     import load_manager

from ..common               import json_return
from ..common               import _dataBaseUtil as dataUtil

from .services.InitPage     import _initPage
from functools              import partial
from flask                  import session
from .page_config           import page_table_configs
from ..                     import basedir
import time
blueprint     = "User"
_getOper      =  partial(dataUtil.getDataBase,blueprint=blueprint)

@load_manager.user_loader
def load_user(user_id):
    _oper= _getOper("UserOperate")
    user = dataUtil.getModel(_oper,id=int(user_id))
    if user:
        return user[0]
    return None

@User.route("/operate_date")
def operate_date():
    return "%s"%session[current_user.username]

@User.route("/load_init_moth",methods=['POST','GET'])
def load_init_moth():
    return jsonify(session.get(current_user.username+'_moth') or 0)

@User.route("/modifyDate",methods=['POST','GET'])
def modifyDate():
    date = request.form.get("date")
    struct= dataUtil.TimestampToStruct(dataUtil.MakeTime(date))
    session[current_user.username] = time.strftime("%a, %d %b %Y %H:%M:%S GMT",struct)
    session[current_user.username+"_moth"]= request.form.get("moth") 
    return jsonify(date)

@User.route('/login', methods=['POST', 'GET'])
def login():
    _isok,_str = _initPage.check_license(basedir)
    state,form,model  = _initPage.GetLogin()
    if state and _isok:
        if model:
            if model.state !=u"休眠":
                session[model.username] = form.operate_date.data
                session[model.username+"_moth"] = form.operate_moth.data
                login_user(model, remember=False)
                return jsonify(dataUtil.ResOk(url_for("index")))
            else:
                return dataUtil.ResErrorJson("休眠状态的用户不能登录系统")
        else:
            return jsonify(dataUtil.ResError(u"用户或密码错误"))
    return render_template('User/login.html', form=form,state=_isok,_str=_str)
        

@User.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop(current_user.username,None)
    logout_user()
    return redirect(url_for('.login'))


@User.route('/addUser/<string:roleType>', methods=['POST', 'GET'])
@json_return
def add_user(roleType):
    data = _initPage.GetRegister(request.form.get("operType"))
    return data


@User.route('/deleteUser/<string:roleType>', methods=['POST', 'GET'])
def delete_user(roleType):
    state      = _initPage.Delete(roleType)
    if state:
        return jsonify(dataUtil.ResOk(u"删除成功"))
    else:
        return jsonify(dataUtil.ResError(u"删除失败"))


@User.route('/changePass', methods=['POST', 'GET'])
def change_pass():
    state,form = _initPage.ChangePass()
    if state:
        return redirect(url_for('.login'))
    else:
        return render_template('User/change_pass.html', form=form,username=current_user.username)

@User.route("/resetPass/<int:userId>",methods=["POST","GET"])
def resetPass(userId):
    state,form,model = _initPage.ReSetPass(userId)
    if state:
        return "1"
    else:
        target = url_for(".resetPass",userId=userId)
        return render_template('User/resetPass.html', target = target,form=form,username=model.username)


@User.route('/modfiy_data/<string:roleType>', methods=['GET', 'POST'])
def modify_data(roleType):
    model = _initPage.ModifyCell(roleType)
    if model:
        if roleType.lower()=='department':
            key = 'name'
        else:
            key = "username"
        message = u'修改--%s--成功' % model[key]
        _data = [1, model, message]
    else:
        _data = [2, {''}, u'修改失败']
    return jsonify(_data)


@User.route('/modify/<string:roleType>/<int:user_id>', methods=['POST', 'GET'])
def modify(roleType, user_id):
    form, choices =  _initPage.GetRegisterPage(roleType,user_id)        
    targetUrl     = url_for('.modify_data', roleType=roleType)
    return render_template('User/register.html',
                           form=form, choices=choices,
                           roleType=roleType,
                           targetUrl=targetUrl, _modify=True, user_id=user_id)



@User.route('/page_control/<string:roleType>', methods=['GET', 'POST'])
def get_index_page(roleType):
    form, choices = _initPage.GetRegisterPage(roleType,-1)
    targetUrl = url_for('.add_user', roleType=form.type)
    if roleType == "User":
        form.password.data = "888888"
    return render_template('User/register.html',
                           form=form, choices=choices,
                           roleType=roleType, targetUrl=targetUrl,
                           _modify=False,operType=roleType)


@User.route('/load_all/<string:roleType>', methods=['GET', 'POST'])
@json_return
def load_all_user(roleType):
    return _initPage.LoadData(roleType)


@User.route('/table_config/<string:roleType>')
@json_return
def table_config(roleType):
    _key = roleType.lower()
    if roleType.lower() != "department":
        _key = "user"
    return page_table_configs.get(_key)

@User.route('/load_datagrid/<string:roleType>')
def load_datagrid(roleType):
    return render_template("User/table_datagrid.html",roleType=roleType)


@User.route('/load_user/<int:user_id>')
def get_user_by_id(user_id):
    _oper = _getOper("UserOperate")
    model = dataUtil.getModel(_oper,id=user_id)
    if model:
        return model[0].username
    return ""


@User.route('/all_users/<string:roleType>')
@json_return
def all_users(roleType):
    _ids  = ["User","Custemer","Supporter"].index(roleType) or 0
    name  = _initPage.GetAllSupportName(_ids)
    return name

@User.route("/search/<string:roleType>",methods=['GET', 'POST'])
def search(roleType):
    roleType = roleType.lower()
    state,formOrData = _initPage.UserSearch(roleType)
    if state:
        return jsonify(formOrData)
    else:
        return render_template("User/search.html",form=formOrData,roleType=roleType)
    
import view_infos

