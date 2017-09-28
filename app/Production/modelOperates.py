# usr/bin/env
# -*- coding:utf-8 -*-
"""
@version: triweb version 1.0
@author: shuiyaoyao
@contact: 289012724@qq.com
@software: PyCharm
@file: modelOperate.py
@time: 2016/7/11 0011
"""
import models
from ..common import exception_show_class
from ..common import BaseOperate, _dataBaseUtil

user_op = _dataBaseUtil.getDataBase("UserOperate", "User")

DataFormat = "%Y-%m-%d"


class StockOperate(BaseOperate):
    def __init__(self):
        BaseOperate.__init__(self)
        self.Model = models.stock
        self.Column = ['date', 'tickets', 'name',
                       'number', 'price',
                       'brand_id', 'standard',
                       'car_number', 'category',
                       'support_id', 'operator_id', 'notice',
                       'notice_a']

    @exception_show_class
    def get_sells(self, stock_id):
        model = self.get(id=int(stock_id))[-1]
        sells = model[0].sells.all()
        return True, sells

    def _get_row(self, model, _key):
        rows = [("all_money", float(model.number) * float(model.price))]
        for cell in _key:
            if cell in ['support_id', 'operator_id']:
                state, data = user_op.get(id=getattr(model, cell))
                if state and data:
                    data = data[0].username
            else:
                data = getattr(model, cell)
            if cell == "date":
                data = data.strftime(DataFormat)

            rows.append((cell, data))
        return rows

    def GetTotal(self, uid):
        """
        @attention: 获取入库商品卖出和报损的总数
        """
        model = self.get(id=uid)[-1][0]
        _f = lambda obj: sum([_c.number for _c in obj])
        sells = _f(model.sells) or 0
        rolls = _f(model.rolls) or 0
        total = sells + rolls
        return total

    def GetAbsTotal(self, uid):
        """
        @attention: 获取商品的绝对数量
        """
        model = self.get(id=uid)[-1][0]
        sell_roll = self.GetTotal(uid)
        b_num = 0
        for sell in model.sells:
            b_num += sum([b.number for b in sell.roll_backs] or [0])
        return model.number - sell_roll + b_num

    def SetOut(self, model, over=1):
        """
        @attention: 更新商品卖完的状态
        """
        model.isout = over
        self.ModelList = model
        return self.update()

    def UpdateOutState(self, uid):
        """
        @attention: 根据商品的ID号更新商品卖完的状态
        """
        model = self.get(id=uid)[-1][0]
        if model.isout == 1:
            return self.SetOut(model, 0)[0]
        return True


class MoneyOperate(BaseOperate):
    def __init__(self):
        BaseOperate.__init__(self)
        self.Model = models.money
        self.Column = ['money_type', 'tickets', 'price', 'user_id', 'date']

    def delete_model(self, uid):
        if uid != 1:
            self.ModelList = self.Model.query.filter_by(id=uid).first()
        return True, None


def get_money(uid):
    state, data = MoneyOperate().get(id=uid)
    if state and data:
        total = 0
        for cell in data:
            total += cell.price
        return total
    else:
        return 0


def set_mongy_info(uid):
    state, data = MoneyOperate().get(id=uid)
    total = 0
    if state and data:
        for cell in data: total += cell.price
    return total


class SellOperate(BaseOperate):
    def __init__(self):
        BaseOperate.__init__(self)
        self.Model = models.sell
        self.Column = ['date', 'stock_id', 'sell_type',
                       'tickets', 'customer_id', 'price_a', 'price',
                       'number', 'money_id', 'operator_id', 'notice', 'notice_a']

    def _get_stock_info(self, stock, row):
        name = stock.name
        standard = stock.standard
        brand_id = stock.brand_id
        support_id = user_op.get(id=getattr(stock, "support_id"))[-1][0].username
        row += [('name', name),
                ("standard", standard),
                ('brand_id', brand_id),
                ('support_id', support_id)]

    def _get_row(self, model, _key):
        _row = [("total_price", float(model.number) * float(model.price))]
        for cell in _key:
            if cell == 'stock_id':
                self._get_stock_info(model.stock, _row)
                continue
            if cell == 'money_id':
                data = set_mongy_info(getattr(model, cell))
            elif cell in ['customer_id', 'operator_id']:
                data = user_op.get(id=getattr(model, cell))[-1]
                data = data[0].username
            else:
                data = getattr(model, cell)

            if cell == "date":
                data = data.strftime(DataFormat)
            _row.append((cell, data))
        return _row

    def get_roll_back(self, uid):
        """
        @attention: 获取退货商品模型
        """
        _model = self.get(id=uid)[-1][0]
        return _model.roll_backs.all()

    def get_roll_back_number(self, uid):
        """
        @attention:  获取销售商品的退货总数
        """
        backs = self.get_roll_back(uid)
        b_num = sum([back.number for back in backs] or [0])
        return b_num

    def get_snap_number(self, uid):
        b_num = self.get_roll_back_number(uid)
        model = self.get(id=uid)[-1][0]
        return model.number - b_num


class RollOutOperate(BaseOperate):
    def __init__(self):
        BaseOperate.__init__(self)
        self.Model = models.roll_out
        self.Column = ['date', 'tickets', 'roll_type', 'stock_id', 'number', 'operator_id', 'notice', 'notice_a']

    def _get_stock_info(self, row, model):
        stock = model.stock
        row.append(("stock_id", stock.name))
        row.append(("stock_notice", stock.notice))

    def _get_row(self, model, _key):
        _row = []
        for cell in _key:
            if cell == 'stock_id':
                self._get_stock_info(_row, model)
            elif cell == 'operator_id':
                data = user_op.get(id=getattr(model, cell))[-1]
                data = data[0].username
                _row.append((cell, data))
            else:
                data = getattr(model, cell)
                if cell == "date":
                    data = data.strftime(DataFormat)
                _row.append((cell, data))
        return _row


class RollBackOperate(BaseOperate):
    def __init__(self):
        BaseOperate.__init__(self)
        self.Model = models.roll_back
        self.Column = ['date', 'tickets', 'sell_id',
                       'number', 'notice', 'notice_a',
                       'money_id', 'customer_id', "operator_id"]

    def __get_sell_info(self, model, _row):
        sell_id = model.sell.tickets
        sell_name = model.sell.stock.name
        _row.extend([("sell_id", sell_id),
                     ("sell_id_k", model.sell.id),
                     ("name", sell_name)])

    def _get_row(self, model, _key):
        _row = []
        _cols = ['id'] + self.Column
        for cell in _cols:
            if cell == "sell_id":
                self.__get_sell_info(model, _row)
            else:
                if cell == 'money_id':
                    data = -set_mongy_info(getattr(model, cell))
                elif cell in ['customer_id', 'operator_id']:
                    user_id = getattr(model, cell)
                    user = user_op.get(id=user_id)[-1][0]
                    data = user.username
                else:
                    data = getattr(model, cell)
                if cell == "date":
                    try:
                        data = data.strftime(DataFormat)
                    except:
                        data = data
                _row.append((cell, data))
        return _row


_data = (("stock", StockOperate),
         ("sell", SellOperate),
         ("rollout", RollOutOperate),
         ("rollloss", RollOutOperate),
         ("rollback", RollBackOperate),
         ("money", MoneyOperate))

_dataBaseUtil.Register("Production", **dict(_data))
