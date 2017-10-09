# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''

from InitPage import dataUtil, formUtil
from functools import partial

_getOperate = partial(dataUtil.getDataBase, blueprint="Production")
_getForm = partial(formUtil.getForm, blueprint="Production")


class ModifyPage(object):
    def __init__(self):
        object.__init__(self)

    @staticmethod
    def get_cell_data(operate_type, uid):
        """
        @attention: 获取商品数据
        @param operate_type:操作类型
        @param uid:产品编号  
        """
        operate = _getOperate(operate_type)
        model = operate.get(id=uid)[-1]
        _data = operate.get_data(model, True)[-1]
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

    def get_stock_page(self, uid):
        data = self.get_cell_data("stock", uid)
        if data.has_key("unit"):
            data.pop("unit")

        form = _getForm("StockForm")
        date = data.pop('date')
        formUtil.setFormData(form, data)
        return form, date

    @staticmethod
    def get_money_info(uid):
        models = dataUtil.getModel(_getOperate("money"), id=uid)
        total = 0
        types = u'现金'
        if models:
            for model in models:
                total += float(model.price)
                types = model.money_type
        return total, types

    def get_sell_page(self, uid):
        form = _getForm("SellForm")
        money = _getForm("MoneyForm")
        money_type = [u"现金", u"支付宝", u"微信", u"转账", u"支票"]
        money.money_type.choices = [(idx, cell) for idx, cell in enumerate(money_type)]
        _data = self.get_cell_data("sell", uid)
        date = _data['date']
        _model = dataUtil.getModel(_getOperate("sell"), id=uid)[0]
        total, types = self.get_money_info(_model.money_id)
        money.money_type.data = types
        money.price.data = total
        _data.pop('date'), _data.pop('money_id')
        formUtil.setFormData(form, _data)
        form.customer_id.data = _model.customer_id
        stock_name_and_id = "%s@%s" % (
            _model.stock.name, _model.stock.id)
        return form, money, date, stock_name_and_id

    def get_roll_back_page(self, uid):
        form = _getForm("RollBack")
        money = _getForm("MoneyForm")
        money_type = [u"现金", u"支付宝", u"微信", u"转账", u"支票"]
        money.money_type.choices = [(idx, cell) for idx, cell in enumerate(money_type)]
        _data = self.get_cell_data("rollback", uid)
        date = _data['date']
        _model = dataUtil.getModel(_getOperate("rollback"), id=uid)[0]
        total, types = self.get_money_info(_model.money_id)
        money.money_type.data = types
        money.price.data = total
        _data.pop('date'), _data.pop('money_id')
        formUtil.setFormData(form, _data)

        name_id = "%s@%s" % (_model.sell.stock.name, _model.sell.id)
        form.customer_id.data = _model.customer_id
        return form, money, date, name_id

    def get_roll_out_page(self, uid):
        form = _getForm("RollOut")
        _data = self.get_cell_data("rollout", uid)
        date = _data['date']
        _model = dataUtil.getModel(_getOperate("rollout"), id=uid)[0]
        _data.pop('date')
        formUtil.setFormData(form, _data)
        name_id = "%s@%s" % (_model.stock.name, _model.stock.id)
        return form, name_id, date


_modifyPageUtil = ModifyPage()
