# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''

from InitPage import dataUtil, formUtil
from functools import partial

_getOper = partial(dataUtil.getDataBase, blueprint="Production")
_getForm = partial(formUtil.getForm, blueprint="Production")


class ModifyPage(object):
    def __init__(self):
        object.__init__(self)

    def GetCellData(self, operType, productionId):
        """
        @attention: 获取商品数据
        @param operType:操作类型
        @param productionId:产品编号  
        """
        _oper = _getOper(operType)
        model = _oper.get(id=productionId)[-1]
        _data = _oper.get_data(model, True)[-1]
        if not _data:
            return {}

        _data = _data[0]
        if _data.has_key("support_id"):
            try:
                _data['support_id'] = model[0].support_id
            except:
                pass
        elif _data.has_key("customer_id"):
            try:
                _data['customer_id'] = model[0].customer_id
            except:
                pass
        return _data

    def GetStockPage(self, idx):
        data = self.GetCellData("stock", idx)
        if data.has_key("unit"):
            data.pop("unit")

        form = _getForm("StockForm")
        date = data.pop('date')
        formUtil.setFormData(form, data)
        return form, date

    def GetMoneyInfo(self, moneyid):
        models = dataUtil.getModel(_getOper("money"), id=moneyid)
        total = 0
        types = u'现金'
        if models:
            for model in models:
                total += float(model.price)
                types = model.money_type
        return total, types

    def GetSellPage(self, productionId):
        form = _getForm("SellForm")
        money = _getForm("MoneyForm")
        moneytype = [u"现金", u"支付宝", u"微信", u"转账", u"支票"]
        money.money_type.choices = [(idx, cell) for idx, cell in enumerate(moneytype)]
        _data = self.GetCellData("sell", productionId)
        date = _data['date']
        _model = dataUtil.getModel(_getOper("sell"), id=productionId)[0]
        total, types = self.GetMoneyInfo(_model.money_id)
        money.money_type.data = types
        money.price.data = total
        _data.pop('date'), _data.pop('money_id')
        formUtil.setFormData(form, _data)
        form.customer_id.data = _model.customer_id
        stock_name_and_id = "%s@%s" % (
            _model.stock.name, _model.stock.id)
        return form, money, date, stock_name_and_id

    def GetRollBackPage(self, productionId):
        form = _getForm("RollBack")
        money = _getForm("MoneyForm")
        moneytype = [u"现金", u"支付宝", u"微信", u"转账", u"支票"]
        money.money_type.choices = [(idx, cell) for idx, cell in enumerate(moneytype)]
        _data = self.GetCellData("rollback", productionId)
        date = _data['date']
        _model = dataUtil.getModel(_getOper("rollback"), id=productionId)[0]
        total, types = self.GetMoneyInfo(_model.money_id)
        money.money_type.data = types
        money.price.data = total
        _data.pop('date'), _data.pop('money_id')
        formUtil.setFormData(form, _data)

        name_id = "%s@%s" % (_model.sell.stock.name, _model.sell.id)
        form.customer_id.data = _model.customer_id
        return form, money, date, name_id

    def GetRollOutPage(self, productionId):
        form = _getForm("RollOut")
        _data = self.GetCellData("rollout", productionId)
        date = _data['date']
        _model = dataUtil.getModel(_getOper("rollout"), id=productionId)[0]
        _data.pop('date')
        formUtil.setFormData(form, _data)
        name_id = "%s@%s" % (_model.stock.name, _model.stock.id)
        return form, name_id, date


_modifyPageUtil = ModifyPage()
