# usr/bin/env
# -*- coding:utf-8 -*-
"""
@version: triweb version 1.0
@author: shuiyaoyao
@contact: 289012724@qq.com
@software: PyCharm
@file: forms.py
@time: 2016/7/4 0004 10:57
"""
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DateField, SelectField
from wtforms.validators import DataRequired, EqualTo, Length


class UserLogin(Form):
    username = StringField(u'用户名', validators=[DataRequired(u'请输入用户名')])
    password = PasswordField(u'密　码', validators=[DataRequired(u'请输入密码')])
    operate_date = DateField(u"日　期", format='%Y-%m-%d')
    operate_moth = StringField(u"显　示", default='3')
    remember = BooleanField(u'记住我')
    submit = SubmitField(u'登陆')


class DepartmentRegister(Form):
    name = StringField(U'部门名', validators=[Length(min=2, max=120, message=u'部门名输入的长度需要在 4~12个字内')])
    description = TextAreaField(U'描　述')
    type = StringField(u'department', validators=[DataRequired()])
    submit = SubmitField(u'立即创建')


class UserRegister(Form):
    username = StringField(u'用 户 名', validators=[Length(min=2, max=120, message=u'用户名输入的长度需要在 4~12个字内')])
    password = PasswordField(u'设置密码', validators=[Length(min=6, max=16, message=u'密码输入的长度需要在 6~16个字内')])
    department = SelectField(u'部　门', choices=[])
    telephone = StringField(u'电　话')
    type = StringField(u'user', validators=[DataRequired()])
    state = SelectField(u"状　态", choices=((u"活跃", u"活跃"), (u"休眠", u"休眠")), default=u"活跃")
    submit = SubmitField(u'立即添加')


class ChangePassForm(Form):
    password = PasswordField(u'新 密 码', validators=[DataRequired(u'请输入密码')])
    confirm = PasswordField(u'确认密码', validators=[EqualTo('password', message=u'输入的密码不一致')])
    submit = SubmitField(u'确认')


class UserSearchForm(Form):
    username = StringField(u"用户名")
    department_id = SelectField(u"部　门")
    state = SelectField(u"状　态", choices=[("", ""), (u"活跃", u"活跃"), (u"休眠", u"休眠")])
    submit = SubmitField(u'确认')


class DepartmentSearchForm(Form):
    name = StringField(u"部门名称")
    description = TextAreaField(u"描　述")
    submit = SubmitField(u'确认')


from ..common import _formOperateUtil

_data = (UserLogin, DepartmentRegister,
         UserRegister, ChangePassForm,
         UserSearchForm, DepartmentSearchForm)
_formOperateUtil.Register("User", *_data)
