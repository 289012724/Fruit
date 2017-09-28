# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''

from flask_wtf import Form
from wtforms import StringField, SelectField, DateTimeField, TextAreaField, FloatField, SubmitField
from ..common import _formOperateUtil


class BaseForm(Form):
    dateFrom = DateTimeField(u'时间(从)', format='%Y-%m-%d')
    dateTo = DateTimeField(u'时间(到)', format='%Y-%m-%d')
    date = StringField(u"默认时间")
    submit = SubmitField(u'确定')


class BuyOrSellBom(BaseForm):
    supportor_id = SelectField(u"供应商", coerce=int, choices=[])
    categroy = SelectField(u"类别", choices=[(u"购进", u"购进"), (u"代销", u"代销")])


_datas = (BuyOrSellBom,)
_formOperateUtil.Register("Bom", *_datas)
