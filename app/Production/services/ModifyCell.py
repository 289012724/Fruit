# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email : 289012724@qq.com
'''

from ...common import _dataBaseUtil
from functools import partial
import copy
from ...Finance.services.BillService import _BillService

_getOperate = partial(_dataBaseUtil.getDataBase, blueprint="Production")


class ModifyCell(object):
    def __init__(self):
        object.__init__(self)
        self.__requestForm = None
        self.__model = None
        self.__blueprint = None
        self.__productionId = None
        self.error = None
        self.operate = None

    @property
    def request_form(self):
        return self.__requestForm

    @request_form.setter
    def request_form(self, value):
        self.__requestForm = value
        self.production_id = self.request_form.get('production_id')
        self.model = _dataBaseUtil.getModel(_getOperate(self.production_id), id=int(self.request_form.get('data_id')))[0]

    @property
    def model(self):
        return self.__model

    @model.setter
    def model(self, value):
        self.__model = value

    @property
    def blueprint(self):
        return self.__blueprint

    @blueprint.setter
    def blueprint(self, value):
        self.__blueprint = value

    @property
    def production_id(self):
        return self.__productionId

    @production_id.setter
    def production_id(self, value):
        self.__productionId = value

    def __update_new(self, _ses, data):
        """
        @attention: 更新账单金额
        """
        operate = _getOperate("money")
        _moneyModel = self.get_money_model(self.model.money_id)
        state, model = operate.update_model(_moneyModel, **data)
        if state and model:
            operate.init_modelList()
            _ses.add(_moneyModel)
            self.request_form['money_id'] = model.money_id
        else:
            self.error = _dataBaseUtil.ResErrorJson(u"更新价格失败%s" % model)

    def __add_new(self, data):
        operate = _getOperate("money")
        state, model = operate.add_model(**data)
        if state and model:
            state, model = operate.add()
            if state and model:
                # 因为在存入数据库的时候需要将Money_id存储所以必须先新建金钱账单
                self.request_form['money_id'] = model[0].id
            else:
                self.error = _dataBaseUtil.ResErrorJson(u"更新价格失败%s" % model)
        else:
            self.error = _dataBaseUtil.ResErrorJson(u"更新价格输入参数有误%s" % model)

    @staticmethod
    def get_money_model(uid):
        _money = _getOperate("money")
        _moneyModel = _dataBaseUtil.getModel(_money, id=uid)
        return _moneyModel[0]

    def __add_new_money(self, _ses):
        money = self.request_form.get('money_id').split("@")
        _dict = {
            "money_type": money[0],
            'tickets': self.request_form.get('tickets'),
            "price": money[1],
            "user_id": int(self.request_form.get('customer_id')),
            "date": self.request_form.get('date')
        }
        if self.model.money_id != 1:
            self.__update_new(_ses, _dict)
        else:
            self.__add_new(_dict)

    def modify_money(self, session, operate_type, sell_id):
        model = self.model
        _moneyModel = self.get_money_model(self.model.money_id)
        # 记录下最原始的金额数据,以便后面可以回滚
        money = self.request_form.get('money_id').split("@")
        if float(money[-1]) == 0:
            self.request_form['money_id'] = 1
            if model.money_id != 1:
                session.delete(_moneyModel)
        else:
            self.__add_new_money(session, operate_type, sell_id)

    @staticmethod
    def is_ok(state, model=True):
        return state and model

    @staticmethod
    def update_stock(stock):
        _stock = _getOperate("stock")
        stock_n = _stock.GetAbsTotal(stock.id)
        if stock_n == 0:
            _stock.SetOut(stock, 1)
        elif stock_n < 0:
            return False
        else:
            _stock.SetOut(stock, 0)
        return True

    def update_stock_data(self, operate):
        """
        @attention: 修改入库的数据信息
        """
        stock_n = operate.GetAbsTotal(self.model.id)
        if stock_n == 0 and int(self.request_form.get("number")) < self.model.number:
            return _dataBaseUtil.ResErrorJson(u"入库数量少于已经卖出的数量,请修正")

        state, model = operate.update_model(self.model, self.request_form)
        if not self.is_ok(state, model):
            return _dataBaseUtil.ResErrorJson(u"修改内容失败")

        operate.SetOut(model, 0)
        if stock_n == 0:
            operate.SetOut(model, 1)

        _data = operate.get_data([model], True)[-1]
        return _dataBaseUtil.ResOkJson(_data)

    # ===========================================================================
    # 更新退货信息
    # ===========================================================================
    def _get_roll_back_stock(self):
        """
        @attention: 获取退货对入库商品做的关联影响
        """
        stock = self.model.sell.stock
        _abs = _getOperate("stock").GetAbsTotal(stock.id)
        old = self.model.number
        new = self.request_form.get("number")
        level = _abs + new - old
        stock.isout = 0
        if level == 0:
            stock.isout = 1
        return stock

    def _update_back(self, operate):
        # 修正付款信息对退货的影响
        self.modify_money(operate.Session, "rollback", self.model.id)
        if self.error is not None:
            return self.error
        data = self._base_update(operate.Session, self._get_roll_back_stock)
        if self.error is not None:
            return self.roll_back()
        return data

    def update_roll_back(self, operate):
        """
        @attention:  修正退货的信息
        """
        sell = self.model.sell
        total_b = _getOperate("sell").get_snap_number(sell.id)
        snap = total_b + self.model.number
        if int(self.request_form.get("number")) > snap:
            return _dataBaseUtil.ResErrorJson(u"输入的数量超过可退数量,请修正")
        return self._update_back(operate)

    @staticmethod
    def get_model_date(model):
        """
        @attention:  获取模型日期时间
        """
        return model.date()

    def _get_model_info(self):
        """
        @attention: 获取正常的销售模型数据
        """
        model = self.operate.get(id=self.model.id)[-1]
        sate, data = self.operate.get_data(model, True)
        if sate and data:
            return _dataBaseUtil.ResOkJson(data)
        return _dataBaseUtil.ResErrorJson(u"获取数据失败,请刷新页面")

    def _adjust_bill(self, current_user, current_date, old_user, old_date):
        if _BillService.update_all_by_total(current_user, current_date, old_user, old_date):
            return self._get_model_info()
        self.error = _dataBaseUtil.ResErrorJson(_BillService.get_error())

    def _base_update(self, _ses, method):
        """
        @attention: 基础的销售数据和账单数据
        """
        # 先做账单之间的修正,后面模型的内容会更新
        old_user = self.model.customer_id
        old_date = self.get_model_date(self.model.date)
        current_user = self.request_form.get("customer_id")
        current_date = self.request_form.get("date")
        state, model = self.operate.update_model(self.model, self.request_form)
        if not (state and model):
            self.error = _dataBaseUtil.ResErrorJson(u"更新数据失败:%s" % model)
            return

        self.operate.init_modelList()
        stock = method()
        _ses.add(stock)
        _ses.add(model)
        try:
            _ses.commit()
            return self._adjust_bill(current_user, current_date, old_user, old_date)
        except Exception, e:
            self.error = _dataBaseUtil.ResErrorJson(u"更新销售信息失败%s" % e)

    def roll_back(self):
        return self.error

    @staticmethod
    def get_user_name(uid):
        return _dataBaseUtil.getDataBase("UserOperate", "User").get(id=uid)[-1][0]

    def check_sell_number(self, operate):
        rollback_number = operate.get_roll_back_number(self.model.id)
        if float(self.request_form.get("number")) < rollback_number:
            self.error = _dataBaseUtil.ResErrorJson(u"销售数量小于退货数量,请修正")

        if self.model.customer_id != self.request_form.get("customer_id"):
            roll_back = self.model.roll_backs.all()
            if roll_back:
                self.error = _dataBaseUtil.ResErrorJson(u"存在与该销售数据有关的退货信息,不可修改客户名称")

    def update_sell(self, operate):
        # 因用户价格修改导致的更新
        self.check_sell_number(operate)
        if self.error is not None:
            return self.error

        _ses = operate.Session
        self.modify_money(_ses, "sell", self.model.id)
        if self.error is not None:
            return self.error

        data = self._base_update(_ses, self.get_stock_state)
        if self.error is not None:
            return self.roll_back()
        return data

    def get_stock_state(self):
        stock = self.model.stock
        stock.isout = 0
        if self.get_stock_level() == 0:
            stock.isout = 1
        return stock

    def update_roll(self, operate):
        state, model = operate.update_model(self.model, self.request_form)
        if not self.is_ok(state, model):
            return _dataBaseUtil.ResErrorJson(u"修改内容失败")

        operate.ModelList = self.get_stock_state()
        state, models = operate.update()
        if not (state and models):
            return _dataBaseUtil.ResErrorJson(u"修改内容失败:%s" % models)

        _data = operate.get_data([model], True)[-1]
        return _dataBaseUtil.ResOkJson(_data)

    def get_stock_level(self):
        stock = self.model.stock
        stock_n = _getOperate("stock").GetAbsTotal(stock.id)
        total = stock_n + self.model.number
        level = total - float(self.request_form.get("number"))
        return level

    def update_sell_and_roll(self, operate):
        """
        @attention: 修正销售和转出/报损的信息
        """

        level = self.get_stock_level()
        if level < 0:
            return _dataBaseUtil.ResErrorJson(u"输入数量大于库存数量,请修正")

        if self.production_id == "sell":
            roll_back = _getOperate("sell").get_roll_back_number(self.model.id)
            if roll_back == self.model.number and self.request_form.get("number") < self.model.number:
                return _dataBaseUtil.ResErrorJson(u"输入的数量小于已经退货的数量,请修正")
            return self.update_sell(operate)
        return self.update_roll(operate)

    def __check_date(self, msg, model):
        stock_date = model.date.strftime("%Y-%m-%d")
        input_date = self.request_form.get("date")

        if _dataBaseUtil.IsLessDate(input_date, stock_date):
            return False, _dataBaseUtil.ResErrorJson(msg)
        return True, None

    def check_date_roll_back(self, msg):
        return self.__check_date(msg, self.model.sell)

    def check_date_stock(self, msg):
        return self.__check_date(msg, self.model.stock)

    def update_model(self, request_form):
        """
        @attention: 修改数据项,同时需要修正入库的标记
        """
        self.error = None
        self.request_form = request_form
        self.request_form['number'] = int(self.request_form.get("number"))
        self.operate = _getOperate(self.production_id)

        if self.production_id in ["rollout", "rollloss", "sell"]:
            state, error = self.check_date_stock(u"选择的日期小于入库日期,请修正")
            if not state:
                return error
            return self.update_sell_and_roll(self.operate)

        elif self.production_id == "rollback":
            state, error = self.check_date_roll_back(u"选择的日期小于销售的日期,请修正")
            if not state:
                return error
            return self.update_roll_back(self.operate)

        return self.update_stock_data(self.operate)


_modifyCellUtil = ModifyCell()
