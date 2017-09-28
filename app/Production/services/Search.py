# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email : 289012724@qq.com
'''

from ...common import _dataBaseUtil, _formOperateUtil
from flask import request
from flask_login import current_user
from sqlalchemy import desc

_getOper = _dataBaseUtil.GetPartial("Production")
_getForm = _formOperateUtil.GetPartial("Production")


class Search(object):
    def __init__(self):
        object.__init__(self)
        self.__requstForm = None
        self.__operType = None

    @property
    def OperType(self):
        return self.__operType

    @OperType.setter
    def OperType(self, value):
        self.__operType = value

    def CheckFrom(self, form):
        if form.is_submitted() or request.method.upper() == "POST":
            if form.validate_on_submit():
                return True
            else:
                return form.errors
        return False

    def _fun(self, query, model, form, key, isEqual=True):
        if not isinstance(form, dict):
            _obj = form.data
        else:
            _obj = form

        data = _obj.get(key)
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

    def _ROLLLOSS(self):
        state, form = self._ROLLOUT()
        if state == 3:
            form.roll_type.data = u"报损"
            form.reason.label.text = u'报损原因'
        return state, form

    def _ROLLOUT(self):
        _oper = _getOper("rollout")
        form = _getForm('RollOutSearch')
        if self.CheckFrom(form):
            model = _oper.model
            _query = model.query
            _query = self._fun(_query, model, form, "tickets", False)
            _query = self._fun(_query, model, form, "notice", False)
            _query = self._fun(_query, model, form, "notice_a", False)
            _query = self._fun(_query, model, form, "operator_id")
            _query = self._fun(_query, model, form, "reason")
            _query = self._fun(_query, model, form, "roll_type")
            if form.dateFrom.data:
                _query = _query.filter(model.date >= form.dateFrom.data,
                                       model.date <= form.dateTo.data)
            model = _query.order_by(desc(model.date)).all()
            if model:
                _data = _oper.get_data(model, True)[-1]
                return 1, _dataBaseUtil.ResOk(_data)
            else:
                return 2, _dataBaseUtil.ResError("未获得相关条件的数据")
        else:
            form.date.data = _dataBaseUtil.CurrentDateStr
            form.roll_type.data = u'转出'
            return 3, form

    def _ROLLBACK(self):
        _oper = _getOper("rollback")
        form = _getForm('RollBackSearch')
        if self.CheckFrom(form):
            model = _oper.model
            _query = model.query
            _query = self._fun(_query, model, form, "tickets", False)
            _query = self._fun(_query, model, form, "notice", False)
            _query = self._fun(_query, model, form, "notice_a", False)
            _query = self._fun(_query, model, form, "customer_id")
            _query = self._fun(_query, model, form, "operator_id")
            _query = self._fun(_query, model, form, "reason")

            if form.dateFrom.data:
                _query = _query.filter(model.date >= form.dateFrom.data,
                                       model.date <= form.dateTo.data)
            model = _query.order_by(desc(model.date)).all()
            if model:
                _data = _oper.get_data(model, True)[-1]
                return 1, _dataBaseUtil.ResOk(_data)
            else:
                return 2, _dataBaseUtil.ResError("未获得相关条件的数据")
        else:
            choices = _dataBaseUtil.GetDataByUrl("CustomerChoice", "User")()
            choices = [(str(c[0]), c[1]) for c in choices]
            choices.insert(0, ("", ""))
            form.customer_id.choices = choices
            form.date.data = _dataBaseUtil.CurrentDateStr
            return 3, form

    def __get_stock_id(self, form):
        _oper = _getForm("Stock")
        model = _oper.model
        _query = model.query
        _query = self._fun(_query, model, form, "category")
        _query = self._fun(_query, model, form, "car_number", False)
        _query = self._fun(_query, model, form, "name", False)
        _query = self._fun(_query, model, form, "support_id")
        model = _query.all()
        if model:
            return [_m.id for _m in model]
        return None

    def _SELL(self):
        _oper = _getOper("sell")
        form = _getForm('SellSearch')
        if self.CheckFrom(form):
            model = _oper.model
            _query = model.query
            _query = self._fun(_query, model, form, "tickets", False)
            _query = self._fun(_query, model, form, "notice", False)
            _query = self._fun(_query, model, form, "notice_a", False)
            _query = self._fun(_query, model, form, "customer_id")
            _query = self._fun(_query, model, form, "operator_id")
            _query = self._fun(_query, model, form, "sell_type")
            if form.dateFrom.data:
                _query = _query.filter(model.date >= form.dateFrom.data,
                                       model.date <= form.dateTo.data)
            if form.priceFrom.data:
                _query = _query.filter(model.price >= form.priceFrom.data,
                                       model.price <= form.priceTo.data)
            model = _query.order_by(desc(model.date)).all()
            if model:
                _data = _oper.get_data(model, True)[-1]
                return 1, _dataBaseUtil.ResOk(_data)
            else:
                return 2, _dataBaseUtil.ResError("未获得相关条件的数据")
        else:
            choices = _dataBaseUtil.GetDataByUrl("CustomerChoice", "User")()
            choices = [(str(c[0]), c[1]) for c in choices]
            choices.insert(0, ("", ""))
            form.customer_id.choices = choices
            form.date.data = _dataBaseUtil.CurrentDateStr
            return 3, form

    def _STOCK(self):
        _oper = _getOper("stock")
        form = _getForm('StockSearch')
        if self.CheckFrom(form):
            model = _oper.model
            _query = model.query
            _query = self._fun(_query, model, form, "tickets", False)
            _query = self._fun(_query, model, form, "brand_id", False)
            _query = self._fun(_query, model, form, "standard", False)
            _query = self._fun(_query, model, form, "car_number", False)
            _query = self._fun(_query, model, form, "category")
            _query = self._fun(_query, model, form, "support_id")
            _query = self._fun(_query, model, form, "operator_id")
            _query = self._fun(_query, model, form, "notice", False)
            _query = self._fun(_query, model, form, "notice_a", False)
            _query = self._fun(_query, model, form, "isout")
            if form.dateFrom.data:
                _query = _query.filter(model.date >= form.dateFrom.data,
                                       model.date <= form.dateTo.data)
            if form.priceFrom.data:
                _query = _query.filter(model.price >= form.priceFrom.data,
                                       model.price <= form.priceTo.data)
            model = _query.order_by(desc(model.date)).all()
            if model:
                _data = _oper.get_data(model, True)[-1]
                [_l.update({'isout': ["否", "是"][_m.isout]}) for _l, _m in zip(_data, model)]
                return 1, _dataBaseUtil.ResOk(_data)
            else:
                return 2, _dataBaseUtil.ResError("未获得相关条件的数据")
        else:
            choices = _dataBaseUtil.GetDataByUrl("SupportChoice", "User")()
            choices = [(str(c[0]), c[1]) for c in choices]
            choices.insert(0, ("", ""))
            form.support_id.choices = choices
            form.date.data = _dataBaseUtil.CurrentDateStr
            return 3, form

    def SearchModel(self, OperType):
        self.OperType = OperType
        method = self.__getattribute__("_%s" % self.OperType.upper())
        return method()

    def __GetBackSell(self, model):
        _roll_backs = []
        for _one in model:
            rolls = _one.roll_backs.all()
            total = sum([_r.number for _r in rolls] or [0])
            _roll_backs.append(total)
        data = _getOper("sell").get_data(model, True)[-1]
        _okDat = []
        for ids, _one in enumerate(data):
            _number_back = _roll_backs[ids]
            if float(_number_back) < float(_one.get("number")):
                _one['number_back'] = _number_back
                _okDat.append(_one)
        return _okDat

    def LoadSellInfo(self, sell_id):
        _oper = _getOper("sell")
        model = _dataBaseUtil.getModel(_oper, id=sell_id)
        if model:
            model = model[0]
            rolls = model.roll_backs.all()
            total = sum([_r.number for _r in rolls] or [0])
            number = model.number - total
            return _dataBaseUtil.ResOk({"number": number, 'price': model.price})
        return _dataBaseUtil.ResError(u"获取模型失败")

    def LoadFilterSell(self, **kwargs):
        self.OperType = "sell"
        _oper = _getOper(self.OperType)
        model = _oper.model
        _query = model.query
        _query = self._fun(_query, model, kwargs, "customer_id")
        _query = self._fun(_query, model, kwargs, "tickets", False)
        models = _query.filter(model.date >= kwargs.get('dateFrom'),
                               model.date <= kwargs.get("dateTo")).all()
        if models:
            return _dataBaseUtil.ResOk(self.__GetBackSell(models))
        else:
            return _dataBaseUtil.ResError(u"未能获得符合条件的数据")

    def _one_moth_day(self, date):
        return _dataBaseUtil.GetInitPrevDate(date, 1)

    def LoadBackSell(self, **kwargs):
        self.OperType = "sell"
        _oper = _getOper(self.OperType)
        model = _oper.model
        _query = model.query
        if current_user.username not in ['admin', 'auditor']:
            _query = self._fun(_query, model, kwargs, "operator_id")
        prev = self._one_moth_day(kwargs.get('date'))
        _query = _query.filter(model.date >= prev, model.date <= kwargs.get('date'))
        _query = _query.filter(model.customer_id == kwargs.get("customer_id"))
        models = _query.all()
        if models:
            return _dataBaseUtil.ResOk(self.__GetBackSell(models))
        return _dataBaseUtil.ResError(u"未能获得符合条件的数据")

    def LoadAllProduction(self, operType):
        self.OperType = operType
        _oper = _getOper(self.OperType)
        models = _LoadProdution().Main(self.OperType)
        if models:
            state, model = _oper.get_data(models, True)
            if self.OperType == 'stock':
                [_l.update({'isout': ["否", "是"][_m.isout]}) for _l, _m in zip(model, models)]
            if state and model:
                return model
        return []


class _LoadProdution(object):
    """
    @attention: 加载初始化中页面中的数据
    """

    def _get_3_moth(self, model, curentData):
        prev = _dataBaseUtil.GetInitPrevDate(curentData)
        _query = model.query.filter(model.date >= prev,
                                    model.date <= curentData)
        _query = _query.order_by(desc(model.date))
        return _query

    def _stock(self, **kwargs):
        _oper = _getOper("stock")
        _model = _oper.model
        query = self._get_3_moth(_model, _dataBaseUtil.CurrentDateStr)
        if current_user.username not in ['admin', 'auditor']:
            kwargs['operator_id'] = current_user.id

        for key, val in kwargs.items():
            eval_string = "query.filter_by(%s='%s')" % (key, val)
            query = eval(eval_string)
        models = query.all()
        return models

    def _current(self, operType, **kwargs):
        if current_user.username not in ['admin', 'auditor']:
            kwargs['operator_id'] = current_user.id
        _oper = _getOper(operType)
        _model = _oper.model
        query = self._get_3_moth(_model, _dataBaseUtil.CurrentDateStr)
        for key, val in kwargs.items():
            eval_string = "query.filter_by(%s='%s')" % (key, val)
            query = eval(eval_string)
        model = query.all()
        return model

    def Main(self, operType, **kwargs):
        if operType == "stock":
            return self._stock()
        elif operType == "sell":
            return self._current(operType)
        elif operType == "rollout":
            return self._current(operType, roll_type=u'转出')
        elif operType == 'rollloss':
            return self._current(operType, roll_type=u'报损')
        else:
            return self._current(operType)


_searchUtil = Search()
