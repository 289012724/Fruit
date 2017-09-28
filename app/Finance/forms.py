# usr/bin/env
# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''
from flask_wtf import Form
from wtforms import StringField, SelectField, DateTimeField, TextAreaField, FloatField, SubmitField
from ..common import _formOperateUtil


class BaseForm(Form):
    tickets = StringField(u"凭据号")
    customer_id = StringField(u"客户")
    operator_id = StringField(u"经办人")
    notice = TextAreaField(u'备注')
    date = DateTimeField(u'时间', format='%Y-%m-%d')
    bill_id = StringField(u"账单号")
    submit = SubmitField(u'确定')


class RefundForm(BaseForm):
    """
    @attention: 客户还款
    """
    money_type = SelectField(u'付款类型', choices=[(cell, cell)
                                               for idx, cell in enumerate([u"现金",
                                                                           u"支付宝", u"微信", u"转账", u"支票"])])
    money_price = FloatField(u"金额")


class WriteOffForm(BaseForm):
    """
    @attention: 账单冲销
    """
    money_price = FloatField(u"冲销金额")
    description = TextAreaField(u'冲销说明')


class RebateForm(BaseForm):
    """
    @attention: 现金折扣
    """
    money_price = FloatField(u"现金折扣")
    description = TextAreaField(u'折扣说明')


class SearchForm(BaseForm):
    tickets = StringField(u"凭据号")
    customer_id = StringField(u"客户")
    #     operator_id = SelectField(u"经办人",coerce=int,choices=[])
    notice = TextAreaField(u'备注')
    description = TextAreaField(u'冲销说明')
    dateFrom = DateTimeField(u'时间(从)', format='%Y-%m-%d')
    dateTo = DateTimeField(u'时间(到)', format='%Y-%m-%d')
    dateDefault = StringField(u"默认时间")
    submit = SubmitField(u'确定')


_datas = (RefundForm, WriteOffForm, RebateForm, SearchForm)
_formOperateUtil.Register("Finance", *_datas)
