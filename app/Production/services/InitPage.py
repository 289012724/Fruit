# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''

from flask import request, jsonify
from flask_login import current_user

from ...common import _dataBaseUtil    as dataUtil, _formOperateUtil as formUtil

_production = "Production"
_user = "User"
_getOperate = dataUtil.GetPartial(_production)
_getForm = formUtil.GetPartial(_production)
DateFormat = '%Y-%m-%d'


class InitPage(object):
    def __init__(self):
        self.__formError = None
        self.a = 1

    @property
    def form_error(self):
        return self.__formError

    @form_error.setter
    def form_error(self, value):
        self.__formError = value

    def check_from(self, form):
        self.form_error = None
        if form.is_submitted() or request.method.upper() == "POST":
            if form.validate_on_submit():
                return True
            self.form_error = form.errors
        return False

    @staticmethod
    def get_user_choice(self, user_type):
        if user_type.lower() == 'supporter':
            model = dataUtil.GetDataByUrl("SupportChoice", "User")()
        elif user_type.lower() == 'customer':
            model = dataUtil.GetDataByUrl("CustomerChoice", "User")()
        if model:
            _dict = [dict(zip(['id', 'text'], one)) for one in model]
        else:
            _dict = []
        return jsonify(_dict)

    def get_stock_gage(self):
        """
        @attention: 获取入库页面
        """
        form = _getForm("StockForm")
        date = dataUtil.CurrentDateStr
        form.support_id.choices = dataUtil.GetDataByUrl("SupportChoice", "User")()
        if self.check_from(form):
            return True, form, date
        return None, form, date

    @staticmethod
    def get_sell_count(self):
        """
        @attention: 获取可卖数量,以及销售的指导价格
        @note:  退过的货品也可以再销售
        """
        _stock = _getOperate("stock")
        idx = request.args.get('id')
        model = dataUtil.getModel(_stock, id=idx)
        _data = {}
        if model:
            model = model[0]
            price = model.price
            _data['stock_number'] = _stock.GetAbsTotal(idx)
            _data['stock_price'] = price
        return _data

    @staticmethod
    def get_stocks(self):
        """
        @attention: 获取当前正在销售的商品信息
        """
        operate = _getOperate("stock")
        models = dataUtil.getModel(operate, isout=0)
        if models:
            return operate.get_data(models, True)[-1]
        return []

    @staticmethod
    def get_sell_stock(self):
        stock_name_and_id = False
        return stock_name_and_id

    @staticmethod
    def get_money_page(self):
        """
        @attention: 获取退货以及销售过程中的金钱交易数据
        """
        money = _getForm("MoneyForm")
        money.price.data = 0
        return money

    def get_sell_page(self):
        form = _getForm("SellForm")
        date = dataUtil.CurrentDateStr
        money = self.get_money_page()
        stock = self.get_sell_stock()
        if self.check_from(form):
            return True, form, money, date, stock
        return False, form, money, date, stock

    def get_roll_out_page(self):
        form = _getForm("RollOut")
        date = dataUtil.CurrentDateStr
        if self.check_from(form):
            return True, form, date
        return False, form, date

    def get_roll_back_page(self):
        form = _getForm("RollBack")
        money = self.get_money_page()
        money.money_type.label.text = u"退款类型"
        money.price.label.text = u"退款金额"
        if self.check_from(form):
            return True, form, money
        return False, form, money

    @staticmethod
    def __get_back_sell(self, model):
        _roll_backs = []
        for _one in model:
            rolls = _one.roll_backs.all()
            total = sum([_r.number for _r in rolls] or [0])
            _roll_backs.append(total)
        data = _getOperate("sell").get_data(model, True)[-1]
        for ids, _one in enumerate(data):
            _one['number_back'] = _roll_backs[ids]
        return data

    def load_back_sell(self, **kargs):
        model = _getOperate("sell").get(**kargs)
        if model[0] and model[1]:
            return self.__get_back_sell(model[1])
        return []

    @staticmethod
    def add_money(self, form, add=False):
        """
        @attention: 添加付款信息
        """
        money_id = form.money_id.data.split("@")
        _type = money_id[0]
        _price = float(("%s" % money_id[1]).strip("-"))
        if add:
            _price = - _price

        _ticket = form.tickets.data
        _customer = form.customer_id.data
        date = form.date.data
        if _price == 0:
            return 1

        operate = _getOperate("money")
        operate.add_model(
            money_type=_type,
            tickets=_ticket,
            price=_price,
            user_id=_customer,
            date=date
        )
        state, model = operate.add()
        if state and model:
            return model[0].id

    @staticmethod
    def _get_user_by_name(self, username):
        """
        @attention: 通过名字获取ID编号
        """
        data = dataUtil.GetDataByUrl("UserByName", "User")(username)
        if data:
            data = data[0]
        return data.get('id')

    @staticmethod
    def _get_user_by_id(self, uid):
        """
        @attention: 通过ID编号获取名字
        """
        data = dataUtil.GetDataByUrl("UserInfo", "User")(uid)
        if data:
            data = data[0]
        return data.get('username')


_initPageUtil = InitPage()
