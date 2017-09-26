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
_getOper = partial(dataUtil.getDataBase, blueprint=blueprint)

_userOper = _getOper("UserOperate")
_departOper = _getOper("DepartmentOperate")


class InitPage(object):
    def __init__(self):
        self.__userId = None
        self.__operateType = None
        self.__formError = []

    @property
    def UserId(self):
        return self.__userId

    @UserId.setter
    @types(long, True)
    def UserId(self, value):
        self.__userId = value

    @property
    def OperateType(self):
        return self.__operateType

    @OperateType.setter
    def OperateType(self, value):
        self.__operateType = value

    @property
    def FormError(self):
        return self.__formError

    @FormError.setter
    def FormError(self, value):
        self.__formError = value

    def CheckFrom(self, form):
        self.FormError = None
        if form.is_submitted() or request.method.upper() == "POST":
            if form.validate_on_submit():
                return True
            self.FormError = form.errors
        return False

    def GetLogin(self):
        """
        @attention: 获取用户登录信息
        """
        LoginForm = _getForm("UserLogin")
        if not self.CheckFrom(LoginForm):
            return False, LoginForm, None

        username = LoginForm.username.data.strip()
        password = LoginForm.password.data.strip()
        state, user = _userOper.check_password(username, password)
        if state and user:
            return True, LoginForm, user[0]
        return True, LoginForm, None

    def _add_department(self, form):
        """
        @attention: 添加部门
        """
        _has_model = _departOper.get(name=form.name.data.strip())[-1]
        if _has_model:
            return u"失败,该部门已经存在%s" % form.name.data, None

        _departOper.add_model(form)
        state, model = _departOper.add()
        if state and model:
            return u'成功', model[0]
        return u"添加部门失败", None

    def _add_user(self, form):
        """
        @attention: 添加用户
        """
        depart_id = int(form.department_id.data)
        if not depart_id:
            return 2, u'部门不存在，请先联系管理员创建该部门', None

        form.department_id.data = depart_id
        username = form.username.data
        model = dataUtil.getModel(_userOper, username=username, department_id=depart_id)
        if model:
            return 2, u'失败,该用户名已经被使用,请重新输入用户名', 0

        form.password.data = md5_data(form.password.data)
        st, model = _userOper.add_model(form)
        if not (st and model):
            return 2, u"添加用户失败,请联系系统管理员", 0

        state, models = _userOper.add()
        if not (state and models):
            return 2, u"添加用户失败,写入数据库失败", 0

        return 1, u'成功', models[0]

    def get_department_chocies(self, roleType):
        """
        @attention: 获取部门选项
        @param roleType: 操作类型 
        """
        _dict = {"user": "DepartmentChocie",
                 "custemer": "DepartmentChoiceCustomer",
                 "supporter": "DepartmentChoiceSupportor"
                 }
        return dataUtil.GetDataByUrl(_dict[roleType.strip().encode("utf-8")],
                                     blueprint)()

    def __get_register_data(self, form):
        is_user = form.type.data == "user"
        if is_user:
            form.department_id.choices = self.get_department_chocies(self.OperateType)
        self.CheckFrom(form)
        _data = [0, self.FormError]

        if self.FormError:
            return _data

        if is_user:
            if self.OperateType != "user": form.password.data = " "
            index, flag, model = self._add_user(form)
            message = u'添加--%s--%s' % (form.username.data, flag)
            if model:
                _info = _userOper.get_data([model], True)[-1]
                _info[0]['department_id'] = model.department.name
                return [index, _info[0], message]
            return [2, {}, message]

        flag, model = self._add_department(form)
        message = u'添加--%s--%s' % (form.name.data, flag)
        if model:
            _info = _departOper.get_data([model], True)[-1]
            return [1, _info[0], message]
        return [2, {}, message]

    def GetRegister(self, operType):
        """
        @attention: register model
        @param roleType: role type 
        """
        self.OperateType = operType.lower().strip()
        _formName = "UserRegister"
        if self.OperateType == "department":
            _formName = "DepartmentRegister"
        return self.__get_register_data(_getForm(_formName))

    def __get_register_page(self, RegistForm):
        def department():
            if self.UserId != -1:
                model = dataUtil.getModel(_departOper, id=self.UserId)
                model = _departOper.get_data(model, True)[-1][0]
                set_form_data(RegistForm, model)
            else:
                RegistForm.description.data = ""

            choices = ""
            RegistForm.type = 'department'
            return RegistForm, choices

        def user():
            if self.UserId != -1:
                model = dataUtil.getModel(_userOper, id=self.UserId)
                _model = _userOper.get_data(model, True)[-1][0]
                set_form_data(RegistForm, _model)

            choices = self.get_department_chocies(self.OperateType)
            RegistForm.type = 'user'
            RegistForm.department_id.choices = choices
            return RegistForm, choices

        if self.OperateType == "department":
            return department()
        return user()

    def GetRegisterPage(self, roleType, user_id):
        """
        @attention: get register page
        @param roleType: role type 
        """
        self.OperateType = roleType.lower()
        self.UserId = user_id
        _formName = "UserRegister"
        if self.OperateType == "department":
            _formName = "DepartmentRegister"
        return self.__get_register_page(_getForm(_formName))

    def __CheckUser(self, user):
        _fun = dataUtil.GetDataByUrl("check_delete_user", "Production")
        data = _fun(self.OperateType, user.id)
        return data

    def __ChcekDepartment(self, department):
        users = department.users.all()
        for user in users:
            _ok = self.__CheckUser(user)
            if _ok:
                return True
        return False

    def Delete(self, roleType):
        """
        @attention: delete the model by type
        @param roleType: role type 
        @note: when delete a user or department if there is some relation data,
        do nothing,else delete selected data
        """

        self.OperateType = roleType.lower()
        self.UserId = int(request.form.get('user_id'))
        state = False
        if self.OperateType == "department":
            model = _departOper.get(id=self.UserId)[-1]
            if model and not self.__ChcekDepartment(model[0]):
                _departOper.delete_model(self.UserId)
                state = _departOper.delete()[0]
            return state

        model = _userOper.get(id=self.UserId)[-1]
        if model and not self.__CheckUser(model[0]):
            _userOper.delete_model(self.UserId)
            state = _userOper.delete()[0]
        return state

        # ===========================================================================

    # change worker pass
    # ===========================================================================
    def ChangePass(self):
        changForm = _getForm("ChangePassForm")
        if self.CheckFrom(changForm):
            model = current_user
            password = changForm.password.data
            state, models = _userOper.change_password(model, password)
            return state and models, changForm
        return None, changForm

    def ReSetPass(self, userId):
        model = dataUtil.getModel(_userOper, id=userId)[0]
        changForm = _getForm("ChangePassForm")
        if self.CheckFrom(changForm):
            password = changForm.password.data
            state, models = _userOper.change_password(model, password)
            return state and models, changForm, model
        return None, changForm, model

    # ===========================================================================
    # modify the model
    # ===========================================================================
    def _modify_user(self):
        """
        @attention: 修改用户的时候会将其密码改掉,因而后面需要将密码重置为之前的
        """
        model = dataUtil.getModel(_userOper, id=self.UserId)[0]
        form = _getForm("UserRegister")
        _userOper.update_model(model, form)
        department_name = _departOper.get(id=form.department_id.data)[-1][0].name
        state, model = _userOper.update()
        if state and model:
            model[0].password = model.password
            _userOper.ModelList = model[0]
            _userOper.update()
            state, data = _userOper.get_data(model, True)
            if state and data:
                data = data[0]
                data['department_id'] = department_name
                return data

    def _modify_department(self):
        form = _getForm("DepartmentRegister")
        model = dataUtil.getModel(_departOper, id=self.UserId)[0]
        _departOper.update_model(model, form)
        state, model = _departOper.update()
        if state and model:
            state, data = _departOper.get_data(model, True)
            if state and data:
                return data[0]

    def ModifyCell(self, roleType):
        """
        @attention: modify the target model
        @param roleType: operate role type 
        """
        self.OperateType = roleType.lower()
        self.UserId = int(request.form.get('_prevname'))
        if self.OperateType != "department":
            return self._modify_user()
        return self._modify_department()

    def GetAllSupportName(self, department):
        """
        @attention: get all the department usernames
        @param department: the user flag 0 worker,1 customer,2 supporter
        """
        customer = dataUtil.getModel(_departOper, name=u'客户')
        _supporter = dataUtil.getModel(_departOper, name=u'供应商')
        _data = [None, customer[0].id, _supporter[0].id]
        state, models = _departOper.get_users(id=_data[department])
        if state and models and department == 0:
            customer.extend(_supporter)
            models = [model for model in models if model.department not in customer]
        name = [model.username for model in models]
        return name

    def UserSearch(self, roleType):
        roleType = roleType.lower()
        if roleType == "department":
            form = _getForm("DepartmentSearchForm")
        else:
            form = _getForm("UserSearchForm")
            if roleType == 'user':
                choices = dataUtil.GetDataByUrl("DepartmentChocie", blueprint)()
                choices = [(str(cell[0]), cell[1]) for cell in choices]
                choices.insert(0, ("", ""))

            if roleType == "customer":
                ids = dataUtil.GetDataByUrl("DepartmentId", blueprint)(u"客户")
                choices = [(str(ids), u"客户")]

            if roleType == "supporter":
                ids = dataUtil.GetDataByUrl("DepartmentId", blueprint)(u"供应商")
                choices = [(str(ids), u"供应商")]

            form.department_id.choices = choices

        def _fun(query, model, form, key, isEqual=True):
            data = form.data.get(key)
            if data:
                if isinstance(data, basestring):
                    data = data.replace("*", "%")
                if key.endswith("id"): data = int(data)
                _type = getattr(model, key)
                if isEqual:
                    query = query.filter(_type == data)
                else:
                    query = query.filter(_type.like("%s" % data))
            return query

        if self.CheckFrom(form):
            if roleType == "department":
                model = _departOper.Model
                query = model.query
                query = _fun(query, model, form, "name", False)
                query = _fun(query, model, form, "description", False)
                models = query.all()
                state, model = _departOper.get_data(models, True)
            else:
                model = _userOper.Model
                query = _fun(model.query, model, form, "username", False)
                if roleType != "user" or form.data.get("department_id"):
                    query = _fun(query, model, form, "department_id")
                else:
                    customer = dataUtil.GetDataByUrl("DepartmentId", blueprint)(u"客户")
                    supporter = dataUtil.GetDataByUrl("DepartmentId", blueprint)(u"供应商")
                    query = query.filter(~model.department_id.in_((customer, supporter)))
                models = _fun(query, model, form, "state").all()
                state, model = _userOper.get_data(models, True)
            return True, model
        return False, form

    def _sortId(self, one, two):
        _1 = int(one['id'])
        _2 = int(two['id'])
        if _1 > _2:
            return 1
        else:
            return -1

    def LoadData(self, roleType):
        """
        @attention: load the role type user or department infomation
        @param roleType: role type  
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

        data = getattr(_inner(), roleType.lower())()
        if data:
            data.sort(self._sortId)
        return data

    def check_license(self, basedir):
        state, _str = BaseControl.GetLincece(basedir)
        return state, _str


_initPage = InitPage()
