# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''

from ...common import types, md5_data, set_form_data
from ...common import _dataBaseUtil    as dataUtil
from ...common import _formOperateUtil as formUtil
from ...common import BaseControl
from flask import request
from flask_login import current_user
from functools import partial

blueprint = "User"
_getForm = partial(formUtil.getForm, blueprint=blueprint)
_getOperate = partial(dataUtil.getDataBase, blueprint=blueprint)

_userOperate = _getOperate("UserOperate")
_departOperate = _getOperate("DepartmentOperate")


class InitPage(object):
    def __init__(self):
        self.__userId = None
        self.__operateType = None
        self.__formError = []

    @property
    def user_id(self):
        return self.__userId

    @user_id.setter
    @types(long, True)
    def user_id(self, value):
        self.__userId = value

    @property
    def operate_type(self):
        return self.__operateType

    @operate_type.setter
    def operate_type(self, value):
        self.__operateType = value

    @property
    def form_error(self):
        return self.__formError

    @form_error.setter
    def form_error(self, value):
        self.__formError = value

    def check_form(self, form):
        self.form_error = None
        if form.is_submitted() or request.method.upper() == "POST":
            if form.validate_on_submit():
                return True
            self.form_error = form.errors
        return False

    def get_login(self):
        """
        @attention: 获取用户登录信息
        """
        login_form = _getForm("UserLogin")
        if not self.check_form(login_form):
            return False, login_form, None

        username = login_form.username.data.strip()
        password = login_form.password.data.strip()
        state, user = _userOperate.check_password(username, password)
        if state and user:
            return True, login_form, user[0]
        return True, login_form, None

    @staticmethod
    def _add_department(self, form):
        """
        @attention: 添加部门
        """
        _has_model = _departOperate.get(name=form.name.data.strip())[-1]
        if _has_model:
            return u"失败,该部门已经存在%s" % form.name.data, None

        _departOperate.add_model(form)
        state, model = _departOperate.add()
        if state and model:
            return u'成功', model[0]
        return u"添加部门失败", None

    @staticmethod
    def _add_user(self, form):
        """
        @attention: 添加用户
        """
        depart_id = int(form.department_id.data)
        if not depart_id:
            return 2, u'部门不存在，请先联系管理员创建该部门', None

        form.department_id.data = depart_id
        username = form.username.data
        model = dataUtil.getModel(_userOperate, username=username, department_id=depart_id)
        if model:
            return 2, u'失败,该用户名已经被使用,请重新输入用户名', 0

        form.password.data = md5_data(form.password.data)
        st, model = _userOperate.add_model(form)
        if not (st and model):
            return 2, u"添加用户失败,请联系系统管理员", 0

        state, models = _userOperate.add()
        if not (state and models):
            return 2, u"添加用户失败,写入数据库失败", 0

        return 1, u'成功', models[0]

    @staticmethod
    def get_department_choice(self, role_type):
        """
        @attention: 获取部门选项
        @param role_type: 操作类型 
        """
        _dict = {"user": "DepartmentChocie",
                 "custemer": "DepartmentChoiceCustomer",
                 "supporter": "DepartmentChoiceSupportor"
                 }
        return dataUtil.GetDataByUrl(_dict[role_type.strip().encode("utf-8")],
                                     blueprint)()

    def __get_register_data(self, form):
        is_user = form.type.data == "user"
        if is_user:
            form.department_id.choices = self.get_department_choice(self.operate_type)
        self.check_form(form)
        _data = [0, self.form_error]

        if self.form_error:
            return _data

        if is_user:
            if self.operate_type != "user": form.password.data = " "
            index, flag, model = self._add_user(form)
            message = u'添加--%s--%s' % (form.username.data, flag)
            if model:
                _info = _userOperate.get_data([model], True)[-1]
                _info[0]['department_id'] = model.department.name
                return [index, _info[0], message]
            return [2, {}, message]

        flag, model = self._add_department(form)
        message = u'添加--%s--%s' % (form.name.data, flag)
        if model:
            _info = _departOperate.get_data([model], True)[-1]
            return [1, _info[0], message]
        return [2, {}, message]

    def register(self, operate_type):
        """
        @attention: register model
        @param roleType: role type 
        """
        self.operate_type = operate_type.lower().strip()
        _formName = "UserRegister"
        if self.operate_type == "department":
            _formName = "DepartmentRegister"
        return self.__get_register_data(_getForm(_formName))

    def __get_register_page(self, reg_form):
        def department():
            if self.user_id != -1:
                model = dataUtil.getModel(_departOperate, id=self.user_id)
                model = _departOperate.get_data(model, True)[-1][0]
                set_form_data(reg_form, model)
            else:
                reg_form.description.data = ""

            choices = ""
            reg_form.type = 'department'
            return reg_form, choices

        def user():
            if self.user_id != -1:
                model = dataUtil.getModel(_userOperate, id=self.user_id)
                _model = _userOperate.get_data(model, True)[-1][0]
                set_form_data(reg_form, _model)

            choices = self.get_department_choice(self.operate_type)
            reg_form.type = 'user'
            reg_form.department_id.choices = choices
            return reg_form, choices

        if self.operate_type == "department":
            return department()
        return user()

    def register_page(self, role_type, user_id):
        """
        @attention: get register page
        """
        self.operate_type = role_type.lower()
        self.user_id = user_id
        _formName = "UserRegister"
        if self.operate_type == "department":
            _formName = "DepartmentRegister"
        return self.__get_register_page(_getForm(_formName))

    def __check_user(self, user):
        _fun = dataUtil.GetDataByUrl("check_delete_user", "Production")
        data = _fun(self.operate_type, user.id)
        return data

    def __check_department(self, department):
        users = department.users.all()
        for user in users:
            _ok = self.__check_user(user)
            if _ok:
                return True
        return False

    def delete(self, role_type):
        """
        @attention: delete the model by type
        @param role_type: role type 
        @note: when delete a user or department if there is some relation data,
        do nothing,else delete selected data
        """

        self.operate_type = role_type.lower()
        self.user_id = int(request.form.get('user_id'))
        state = False
        if self.operate_type == "department":
            model = _departOperate.get(id=self.user_id)[-1]
            if model and not self.__check_department(model[0]):
                _departOperate.delete_model(self.user_id)
                state = _departOperate.delete()[0]
            return state

        model = _userOperate.get(id=self.user_id)[-1]
        if model and not self.__check_user(model[0]):
            _userOperate.delete_model(self.user_id)
            state = _userOperate.delete()[0]
        return state

    # ===========================================================================
    # change worker pass
    # ===========================================================================
    def change_pass(self):
        change_form = _getForm("ChangePassForm")
        if self.check_form(change_form):
            model = current_user
            password = change_form.password.data
            state, models = _userOperate.change_password(model, password)
            return state and models, change_form
        return None, change_form

    def reset_pass(self, user_id):
        model = dataUtil.getModel(_userOperate, id=user_id)[0]
        change_form = _getForm("ChangePassForm")
        if self.check_form(change_form):
            password = change_form.password.data
            state, models = _userOperate.change_password(model, password)
            return state and models, change_form, model
        return None, change_form, model

    # ===========================================================================
    # modify the model
    # ===========================================================================
    def _modify_user(self):
        """
        @attention: 修改用户的时候会将其密码改掉,因而后面需要将密码重置为之前的
        """
        model = dataUtil.getModel(_userOperate, id=self.user_id)[0]
        form = _getForm("UserRegister")
        _userOperate.update_model(model, form)
        department_name = _departOperate.get(id=form.department_id.data)[-1][0].name
        state, model = _userOperate.update()
        if state and model:
            model[0].password = model.password
            _userOperate.ModelList = model[0]
            _userOperate.update()
            state, data = _userOperate.get_data(model, True)
            if state and data:
                data = data[0]
                data['department_id'] = department_name
                return data

    def _modify_department(self):
        form = _getForm("DepartmentRegister")
        model = dataUtil.getModel(_departOperate, id=self.user_id)[0]
        _departOperate.update_model(model, form)
        state, model = _departOperate.update()
        if state and model:
            state, data = _departOperate.get_data(model, True)
            if state and data:
                return data[0]

    def modify_cell(self, roleType):
        """
        @attention: modify the target model
        @param roleType: operate role type 
        """
        self.operate_type = roleType.lower()
        self.user_id = int(request.form.get('_prevname'))
        if self.operate_type != "department":
            return self._modify_user()
        return self._modify_department()

    @staticmethod
    def get_supporter_name(self, department):
        """
        @attention: get all the department usernames
        @param department: the user flag 0 worker,1 customer,2 supporter
        """
        customer = dataUtil.getModel(_departOperate, name=u'客户')
        _supporter = dataUtil.getModel(_departOperate, name=u'供应商')
        _data = [None, customer[0].id, _supporter[0].id]
        state, models = _departOperate.get_users(id=_data[department])
        if state and models and department == 0:
            customer.extend(_supporter)
            models = [model for model in models if model.department not in customer]
        name = [model.username for model in models]
        return name

    def user_search(self, role_type):
        role_type = role_type.lower()
        if role_type == "department":
            form = _getForm("DepartmentSearchForm")
        else:
            form = _getForm("UserSearchForm")
            if role_type == 'user':
                choices = dataUtil.GetDataByUrl("DepartmentChocie", blueprint)()
                choices = [(str(cell[0]), cell[1]) for cell in choices]
                choices.insert(0, ("", ""))

            if role_type == "customer":
                ids = dataUtil.GetDataByUrl("DepartmentId", blueprint)(u"客户")
                choices = [(str(ids), u"客户")]

            if role_type == "supporter":
                ids = dataUtil.GetDataByUrl("DepartmentId", blueprint)(u"供应商")
                choices = [(str(ids), u"供应商")]

            form.department_id.choices = choices

        def _fun(query, model, form, key, equal=True):
            data = form.data.get(key)
            if not data:
                return query
            if isinstance(data, basestring):
                data = data.replace("*", "%")
            if key.endswith("id"):
                data = int(data)
            _type = getattr(model, key)
            if equal:
                return query.filter(_type == data)
            return query.filter(_type.like("%s" % data))

        if self.check_form(form):
            if role_type == "department":
                model = _departOperate.model
                query = model.query
                query = _fun(query, model, form, "name", False)
                query = _fun(query, model, form, "description", False)
                models = query.all()
                state, model = _departOperate.get_data(models, True)
            else:
                model = _userOperate.model
                query = _fun(model.query, model, form, "username", False)
                if role_type != "user" or form.data.get("department_id"):
                    query = _fun(query, model, form, "department_id")
                else:
                    customer = dataUtil.GetDataByUrl("DepartmentId", blueprint)(u"客户")
                    supporter = dataUtil.GetDataByUrl("DepartmentId", blueprint)(u"供应商")
                    query = query.filter(~model.department_id.in_((customer, supporter)))
                models = _fun(query, model, form, "state").all()
                state, model = _userOperate.get_data(models, True)
            return True, model
        return False, form

    @staticmethod
    def _sort(self, one, two):
        _1 = int(one['id'])
        _2 = int(two['id'])
        if _1 > _2:
            return 1
        else:
            return -1

    def load_data(self, role_type):
        """
        @attention: load the role type user or department infomation
        @param role_type: role type  
        """

        class _inner:
            def _f(self, department_name):
                _id = dataUtil.GetDataByUrl("DepartmentId", blueprint)(department_name)
                if _id:
                    return dataUtil.GetDataByUrl("UserByDepartment", blueprint)(_id)
                return [{}]

            def custemer(self):
                return self._f(u"客户")

            def supporter(self):
                return self._f(u"供应商")

            def user(self):
                return dataUtil.GetDataByUrl("UserWorker", blueprint)()

            def department(self):
                return dataUtil.GetDataByUrl("DepartmentInfo", blueprint)(0)

        data = getattr(_inner(), role_type.lower())()
        if data:
            data.sort(self._sort)
        return data

    @staticmethod
    def check_license(self, basedir):
        state, _str = BaseControl.GetLincece(basedir)
        return state, _str


_initPage = InitPage()
