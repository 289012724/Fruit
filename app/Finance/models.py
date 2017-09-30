# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''
from .. import database as db


class Rebund(db.Model):
    __tablename__ = 'fruit_bill_rebund'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime)
    tickets = db.Column(db.String(20))
    money_type = db.Column(db.String(20))
    money_price = db.Column(db.Float(2))
    customer_id = db.Column(db.Integer)
    operator_id = db.Column(db.Integer)
    bill_id = db.Column(db.Integer, db.ForeignKey('fruit_bill_bill.id'))
    notice = db.Column(db.Text(2048))

    def Init(self, arg):
        self.date, self.tickets, self.money_type, \
        self.money_price, self.customer_id, self.operator_id, self.bill_id, self.notice = arg


class Rebate(db.Model):
    __tablename__ = 'fruit_bill_rebate'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime)
    tickets = db.Column(db.String(20))
    money_price = db.Column(db.Float(2))
    customer_id = db.Column(db.Integer)
    operator_id = db.Column(db.Integer)
    bill_id = db.Column(db.Integer, db.ForeignKey('fruit_bill_bill.id'))
    description = db.Column(db.Text(2048))
    notice = db.Column(db.Text(2048))

    def Init(self, arg):
        self.date, self.tickets, self.money_price, self.customer_id, \
        self.operator_id, self.bill_id, self.description, self.notice = arg


class WriteOff(db.Model):
    __tablename__ = 'fruit_bill_writeoff'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime)
    tickets = db.Column(db.String(20))
    money_price = db.Column(db.Float(2))
    customer_id = db.Column(db.Integer)
    operator_id = db.Column(db.Integer)
    bill_id = db.Column(db.Integer, db.ForeignKey('fruit_bill_bill.id'))
    description = db.Column(db.Text(2048))
    notice = db.Column(db.Text(2048))

    def Init(self, arg):
        self.date, self.tickets, self.money_price, self.customer_id, \
        self.operator_id, self.bill_id, self.description, self.notice = arg


# ===============================================================================
# 在生产客户对账表的时候会同时生产一张与之相关的账单记录
# 当还过一次款会更新账单记录中的本月结转信息
# 在计算用户应该给的总账单的时候，根据结转信息计算
# ===============================================================================
class Bill(db.Model):
    __tablename__ = 'fruit_bill_bill'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime)
    total_money = db.Column(db.Float(2), default=0)  # 当前月份销售数据
    next_money = db.Column(db.Float(2), default=0)  # 本月的还款合计信息
    level_money = db.Column(db.Float(2), default=0)  # 本月的结转信息
    rebund = db.relationship('Rebund', backref='bill', lazy='dynamic')
    rebate = db.relationship('Rebate', backref='bill', lazy='dynamic')
    writeOff = db.relationship('WriteOff', backref='bill', lazy='dynamic')
    has_filled = db.Column(db.Integer, default=0)  # 保存是否已经出过对账单在确定是否要改
    customer_id = db.Column(db.Integer)
    operator_id = db.Column(db.Integer)

    def Init(self, arg):
        self.date, self.total_money, \
        self.next_money, self.level_money, \
        self.customer_id, self.operator_id = arg

    def __str__(self):
        return "<Bill: id:%s data%s>" % (self.id, self.date.strftime("%Y-%m-%d"))
