# usr/bin/env
# -*- coding:utf-8 -*-
"""
@version: triweb version 1.0
@author: shuiyaoyao
@contact: 289012724@qq.com
@software: PyCharm
@file: forms.py
@time: 2016/7/11 0011
"""
from flask_wtf          import Form
from wtforms.validators import DataRequired, Length
from wtforms            import StringField, SelectField, DateTimeField, TextAreaField, FloatField, SubmitField

class BaseForm(Form):
    notice      = TextAreaField(u'备注')
    notice_a    = TextAreaField(u"备注A")
    submit      = SubmitField(u'确定')
    

class StockForm(BaseForm):
    date        = DateTimeField(u'入库时间', format='%Y-%m-%d')
    tickets     = StringField(u'凭据号',      validators=[Length(min=3, max=15, message=u'凭据号长度范围 3-15')])
    name        = StringField(u'商品名称',    validators=[Length(min=1, max=120, message=u'商品名称有误')])
    number      = StringField(u'数量',        validators=[DataRequired(u'请输入商品数量')])
    price       = FloatField(u'价格')
    brand_id    = StringField(u'品牌')
    standard    = StringField(u'规格')
    car_number  = StringField(u'车牌柜号')
    category    = SelectField(u'销售类型',    choices=[( u'购进', u'购进'), (u'代销', u'代销')])
    support_id  = StringField(u'供应商')
    operator_id = StringField(u'经办人')



class MoneyForm(Form):
    date        = DateTimeField(u'时间', format='%Y-%m-%d')
    money_type  = SelectField(u'类型', choices = [(idx,cell ) 
                            for idx ,cell in enumerate([u"现金",
                            u"支付宝",u"微信",u"转账",u"支票"])])
    tickets     = StringField(u'单号')
    user_id     = SelectField(u"付款人")
    price       = FloatField(u'金额')

class SellForm(BaseForm):
    date        = DateTimeField(u'销售日期',  format='%Y-%m-%d')
    stock_id    = StringField(u'入库信息',    validators=[DataRequired(u"请选择入库单号")])
    sell_type   = SelectField(u'销售类型',    validators=[DataRequired(u'请选择销售类型')], choices=[(u"销售",u"销售"), (u"代销",u"代销")])
    tickets     = StringField(u'凭证号',      validators=[DataRequired(u"请输入凭证号")])
    customer_id = StringField(u"客户",        validators=[DataRequired(u"请选择客户")])
    price       = FloatField(u'销售单价',     validators=[DataRequired(u"请输入销售单价")])
    price_a     = FloatField(u'备注单价',     validators=[DataRequired(u"请输入销售单价")])
    number      = FloatField(u"销售数量",     validators=[DataRequired(u"请输入销售数量")])
    money_id    = StringField(u"付款单号")
    operator_id = StringField(u'经办人')


class RollOut(BaseForm):
    date        = DateTimeField(u"日期",      format='%Y-%m-%d')
    tickets     = StringField(u"凭证号",      validators=[DataRequired(u"请输入凭证号")])
    roll_type   = SelectField(u"类型",     validators=[DataRequired(u"请选择类型")], choices=[(u'转出',u'转出'), (u"报损",u"报损")])
    stock_id    = StringField(u"入库单号",    validators=[DataRequired(u"请选择入库单号")])
    number      = FloatField(u"数量",         validators=[DataRequired(u"请输入数量")])
    operator_id = StringField(u'经办人')
    reason      = TextAreaField(u'转出原因')


class RollBack(BaseForm):
    date        = DateTimeField(u"日期",      format='%Y-%m-%d')
    tickets     = StringField(u"凭证号",      validators=[DataRequired(u"请输入凭证号")])
    sell_id     = StringField(u"销售商品")
    number      = FloatField(u"退货数量",         validators=[DataRequired(u"请输入数量")])
    money_id    = StringField(u"退款单号",    validators=[DataRequired(u"请输入退款信息")])
    customer_id = StringField(u"客户")
    operator_id = StringField(u'经办人')
    reason      = TextAreaField(u'退货原因')

class BaseSearch(BaseForm):
    dateFrom    = DateTimeField(u"日期(从)",      format='%Y-%m-%d')
    dateTo      = DateTimeField(u"日期(到)",      format='%Y-%m-%d')
    tickets     = StringField(u"凭证号")
    operator_id = SelectField(u'经办人', coerce=str,choices=[])
    date        = StringField(u"默认日期")
     
class StockSearch(BaseSearch):
    brand_id    = StringField(u"品牌")
    priceFrom   = FloatField(u'价格(从)')
    priceTo     = FloatField(u'价格(到)')
    standard    = StringField(u'规格')
    car_number  = StringField(u'车牌柜号')
    category    = SelectField(u'销售类型',choices=[('',''),( u'购进', u'购进'), (u'代销', u'代销')])
    support_id  = SelectField(u'供应商',coerce=str,choices=[])
    isout       = SelectField(u"销售状态",choices=[(0,u'销售中..'),(1,u"已售完"),('','')])

class SellSearch(BaseSearch):
    priceFrom   = FloatField(u'价格(从)')
    priceTo     = FloatField(u'价格(到)')
    customer_id = SelectField(u'客户',  coerce=str,choices=[])
    sell_type   = SelectField(u'销售类型',choices=[('',''),(u"销售",u"销售"), (u"代销",u"代销")])
    
class RollBackSearch(BaseSearch):
    customer_id = SelectField(u"客户",   coerce=str,choices=[])
    reason      = TextAreaField(u'退货原因')
    
class RollOutSearch(BaseSearch):
    reason      = TextAreaField(u'转出原因')
    roll_type   = StringField(u"类型")
from ..common        import _formOperateUtil

_datas = (StockForm,SellForm,RollOut,RollBack, MoneyForm,
          StockSearch,SellSearch,RollBackSearch,RollOutSearch)
_formOperateUtil.Register("Production",*_datas)


