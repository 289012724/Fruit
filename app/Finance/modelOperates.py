# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''

import models
from ..common import BaseOperate, _dataBaseUtil
from sqlalchemy import desc

user_op = _dataBaseUtil.getDataBase("UserOperate", "User")
DataFormat = "%Y-%m-%d"


class RebundOperate(BaseOperate):
    def __init__(self):
        BaseOperate.__init__(self)
        self.Model = models.Rebund
        self.Column = ['date', 'tickets', 'money_type', 'money_price', 'customer_id', "operator_id", "bill_id",
                       'notice']

    def _get_row(self, model, _key):
        _row = []
        for cell in _key:
            if cell in ["customer_id", "operator_id"]:
                state, data = user_op.get(id=getattr(model, cell))
                if state and data:
                    data = data[0].username
            elif cell == 'bill_id':
                bill = model.bill.query.all()[0]
                data = bill.date.strftime(DataFormat)
            else:
                data = getattr(model, cell)
            if cell == "date":
                data = data.strftime(DataFormat)
            _row.append((cell, data))
        return _row


class RebateOperate(BaseOperate):
    def __init__(self):
        BaseOperate.__init__(self)
        self.Model = models.Rebate
        self.Column = ['date', 'tickets', 'money_price', 'customer_id', "operator_id", "bill_id", 'description',
                       'notice']

    def _get_row(self, model, _key):
        _row = []
        for cell in _key:
            if cell in ["customer_id", "operator_id"]:
                data = user_op.get(id=getattr(model, cell))[-1]
                data = data[0].username
            elif cell == 'bill_id':
                bill = model.bill.query.all()[0]
                data = bill.date.strftime(DataFormat)
            else:
                data = getattr(model, cell)
            if cell == "date":
                data = data.strftime(DataFormat)
            _row.append((cell, data))
        return _row


class WriteOffOperate(RebateOperate):
    def __init__(self):
        RebateOperate.__init__(self)
        self.Model = models.WriteOff


class BillOperate(BaseOperate):
    def __init__(self):
        BaseOperate.__init__(self)
        self.Model = models.Bill
        self.Column = ['date', 'total_money',
                       "next_money", 'level_money',
                       "customer_id", "operator_id",
                       "has_filled"]

    def _get_row(self, model, _key):
        _row = []
        for cell in _key:
            if cell in ["customer_id", "operator_id"]:
                state, data = user_op.get(id=getattr(model, cell))
                if state and data:
                    data = data[0].username
                else:
                    data = "未知"
            elif cell in ["has_filled"]:
                data = getattr(model, cell)
                if float(data) == 0:
                    data = "否"
                else:
                    data = "是"
            else:
                data = getattr(model, cell)
            if cell in ['date_from', 'date']:
                data = data.strftime(DataFormat)
            _row.append((cell, data))
        return _row

    @staticmethod
    def get_bill_date(self, date_from):
        date = date_from.split("-")
        date[-1] = "01"
        date = "-".join(date)
        return date

    def get_prev_money(self, customer_id, dateFrom):
        """
        @attention: 获取该用户上次预留下来的预付款
        @param customer_id:用户id号
        @param dateFrom: 用户选择的开始月份时间 
        """
        dateFrom = "%s" % dateFrom
        dateFrom = self.get_bill_date(dateFrom)
        _query = self.Model.query
        _query = _query.filter(self.Model.customer_id == customer_id,
                               self.Model.date < dateFrom)
        models = _query.all()
        level_money = 0
        if models:
            level_money = sum([model.level_money for model in models] or [0])
        return level_money

    def get_current_bill_money(self, customer_id, dateFrom):
        """
        @attention: 获取用户到目前为止的结余信息
        """
        date = self.get_bill_date(dateFrom)
        _prev = self.get_prev_money(customer_id, dateFrom)
        _query = self.Model.query.filter(self.Model.customer_id == customer_id)
        _query = _query.filter(self.Model.date == date)
        model = _query.all()
        if model:
            data = model.total_money - _prev
        else:
            data = None
        return data

    def get_last12_model(self, customer_id):
        """
        @attention: 获取该用户最近的12笔账单
        """
        _query = self.Model.query.filter(self.Model.customer_id == customer_id)
        _query = _query.order_by(desc(self.Model.date)).limit(12)
        model = _query.all()
        return model

    def get_pre_end_date(self, customer_id):
        """
        @attention: 获取用户上一次生成对账单的日期
        @param customer_id:用户id号
        """
        _query = self.Model.query.filter(self.Model.customer_id == customer_id)
        _query = _query.filter(self.Model.has_filled == 1) \
            .order_by(desc(self.Model.date)) \
            .limit(1)
        _model = _query.all()
        return _model

    def get_bill_all_money(self, bill_id):
        model = self.get(id=bill_id)[-1]
        model = model[0]
        rebund = model.rebund.all()
        rebate = model.rebate.all()
        writeOff = model.writeOff.all()
        _ok = rebund + rebate + writeOff
        total = sum([cell.money_price for cell in _ok] or [0])
        return total

    def update_bill(self, bill_id, total_money=None):
        """
        @attention: 自动计算本月差额值
        @param bill_id: 账单编号
        """
        model = self.get(id=int(bill_id))[-1]
        model = model[0]
        model.total_money = total_money or model.total_money
        model.next_money = self.get_bill_all_money(bill_id)
        model.level_money = model.total_money - model.next_money
        self.ModelList = model
        return self.update()

    def update_bill_new(self, session, bill_id, total_money=None):
        model = self.get(id=int(bill_id))[-1]
        model = model[0]
        model.total_money = total_money or model.total_money
        model.next_money = self.get_bill_all_money(bill_id)
        model.level_money = model.total_money - model.next_money
        session.add(model)

    def update_by_rebund(self, session, bill_id, snap):
        """
        @attention: 更新用户当月的还款数据
        """
        model = self.get(id=int(bill_id))[-1]
        model = model[0]
        model.next_money += snap
        model.level_money = model.total_money - model.next_money
        session.add(model)

    def update_by_total(self, session, bill_id, snap):
        """
        @attention: 更新当月的账单信息
        """
        model = self.get(id=int(bill_id))[-1]
        model = model[0]
        model.total_money += snap
        model.level_money = model.total_money - model.next_money
        session.add(model)

    def get_last_not_fill_bill(self, customer_id):
        """
        @attention: 获取未生成过对账单的账单数据
        """
        model = self.Model
        query = model.query.filter(model.customer_id == customer_id,
                                   model.has_filled == 0)
        return query.all() or []

    def check_delete_state(self, customer_id, bill_name):
        state, model = self.get(customer_id=customer_id, tickets=bill_name)
        if state and model:
            model = model[0]
            if model.has_filled == 1:
                return False


_data = (("rebund", RebundOperate),
         ("rebate", RebateOperate),
         ('writeoff', WriteOffOperate),
         ("bill", BillOperate))
_dataBaseUtil.Register("Finance", **dict(_data))
