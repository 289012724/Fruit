# usr/bin/env
# -*- coding:utf-8 -*-
"""
@version: triweb version 1.0
@author: shuiyaoyao
@contact: 289012724@qq.com
@software: PyCharm
@file: models.py
@time: 2016/7/11 0011
"""
from .. import database as db

class stock(db.Model):
    __tablename__ = 'fruit_stocks'
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date        = db.Column(db.DateTime)
    tickets     = db.Column(db.String(15))
    name        = db.Column(db.String(120))
    number      = db.Column(db.SmallInteger)
    price       = db.Column(db.Float(2))
    brand_id    = db.Column(db.String(120))
    standard    = db.Column(db.String(120))
    car_number  = db.Column(db.String(20))
    category    = db.Column(db.Enum(u'代销', u'购进'))
    support_id  = db.Column(db.Integer)
    operator_id = db.Column(db.Integer)
    notice      = db.Column(db.Text(2408))
    notice_a    = db.Column(db.Text(2048))
    isout       = db.Column(db.SmallInteger,default=0)
    sells       = db.relationship('sell',backref='stock', cascade="delete", lazy='dynamic')
    rolls       = db.relationship('roll_out', backref='stock', cascade="delete",lazy='dynamic')
    
    def __str__(self):
        return "%r-%s" % (self.id, self.name)

    def Init(self, arg):
        self.date, self.tickets, self.name, self.number, \
        self.price, self.brands_id, self.standard, self.car_number, \
        self.category, self.support_id, self.operator_id, self.notice,\
        self.notice_a = arg


class money(db.Model):
    __tablename__ = 'fruit_moneys'
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    money_type  = db.Column(db.Enum(u"现金",u"支付宝",u"微信",u"转账",u"支票"))
    tickets     = db.Column(db.String(15))
    price       = db.Column(db.Float(2))
    user_id     = db.Column(db.Integer)
    date        = db.Column(db.DateTime)

    def Init(self, arg):
        self.money_type, self.tickets, self.price, self.user_id, self.date = arg

    def __str__(self):
        return "%r-%r-%r" % (self.id,self.money_type.encode('UTF-8'),self.price)


class sell(db.Model):
    __tablename__ = 'fruit_sells'
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date        = db.Column(db.DateTime)
    stock_id    = db.Column(db.Integer, db.ForeignKey('fruit_stocks.id'))
    sell_type   = db.Column(db.Enum(u'销售', u'代销'))
    tickets     = db.Column(db.String(15))
    customer_id = db.Column(db.Integer)
    price       = db.Column(db.Float(2))
    price_a     = db.Column(db.Float(2))
    number      = db.Column(db.SmallInteger)
    money_id    = db.Column(db.Integer)
    operator_id = db.Column(db.Integer)
    notice      = db.Column(db.Text(2048))
    notice_a    = db.Column(db.Text(2048))
    roll_backs  = db.relationship('roll_back', backref='sell', cascade="delete",lazy='dynamic')
    def __str__(self):
        return "%r--%s" % (self.id,self.date)

    def Init(self, arg):
        self.date, self.stock_id, self.sell_type, \
        self.tickets, self.customer_id, self.price_a,self.price, \
        self.number, self.money_id, self.operator_id, self.notice,\
        self.notice_a = arg


class roll_out(db.Model):
    __tablename__ = 'fruit_roll_outs'
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date        = db.Column(db.DateTime)
    tickets     = db.Column(db.String(15))
    roll_type   = db.Column(db.Enum(u'报损', u'转出'))
    stock_id    = db.Column(db.Integer, db.ForeignKey('fruit_stocks.id'))
    number      = db.Column(db.SmallInteger)
    operator_id = db.Column(db.Integer)
    reason      = db.Column(db.Text(2048))
    notice      = db.Column(db.Text(2048))
    notice_a    = db.Column(db.Text(2048))
    def __str__(self):
        return '%r--%r--%r' % (self.id, self.tickets, self.number)

    def Init(self, arg):
        self.date, self.tickets, self.roll_type,self.stock_id,self.number,\
        self.operator_id,self.notice,self.notice_a = arg


class roll_back(db.Model):
    __tablename__ = 'fruit_roll_backs'
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date        = db.Column(db.DateTime)
    roll_type   = db.Column(db.String(20), default=u'退货')
    tickets     = db.Column(db.String(15))
    sell_id     = db.Column(db.Integer, db.ForeignKey('fruit_sells.id'))
    number      = db.Column(db.SmallInteger)
    money_id    = db.Column(db.Integer)
    customer_id = db.Column(db.Integer)
    operator_id = db.Column(db.Integer)
    notice      = db.Column(db.Text(2048))
    notice_a    = db.Column(db.Text(2048))
    
    def __str__(self):
        return '%r--%r--%r' % (self.id, self.tickets, self.number)

    def Init(self, arg):
        self.date, self.tickets, self.sell_id, \
        self.number, self.notice,self.notice_a,self.money_id,\
        self.customer_id,self.operator_id = arg
