# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''
from ...common import _dataBaseUtil    as dataUtil
from ...common import _formOperateUtil as formUtil
from ...common.ExcelToPdf import Excel, AppQueue, ExcelToPdf
from flask import request, make_response, send_file
from ..page_config import page_table_configs
from flask_login import current_user
import os
from flask import current_app

_Bom = "Bom"
_user = "User"
_getOper = dataUtil.GetPartial("Production")
_getForm = formUtil.GetPartial(_Bom)
_userOpt = dataUtil.getDataBase("UserOperate", _user)


class Search(object):
    def __init__(self):
        object.__init__(self)
        self.__pageNumber = 1
        self.__pageSize = 20
        self.DateFrom = None
        self.DateTo = None
        self.ReqData = None

    @property
    def form_error(self):
        return self.__formError

    @form_error.setter
    def form_error(self, value):
        self.__formError = value

    @property
    def page_number(self):
        return self.__pageNumber

    @page_number.setter
    def page_number(self, value):
        self.__pageNumber = int(value)

    @property
    def page_size(self):
        return self.__pageSize

    @page_size.setter
    def page_size(self, value):
        self.__pageSize = int(value)

    def check_form(self, form):
        self.form_error = None
        if form.is_submitted() or request.method.upper() == "POST":
            if form.validate_on_submit():
                return True
            self.form_error = form.errors
        return False

    def _fun(self, query, model, form, key, is_equal=True):
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
            if is_equal:
                query = query.filter(_type == data)
            else:
                query = query.filter(_type.like("%s" % data))
        return query

    @staticmethod
    def __get__search(self, page_number, page_size, operate):
        limit = page_size
        if page_number > 0:
            offset = (page_number - 1) * page_size
        else:
            offset = 0
        _model = operate.model
        _query = _model.query
        _query = _query.limit(limit).offset(offset)
        return _query

    def __get_date_filter(self, operate):
        model = operate.model
        query = model.query
        if self.DateFrom:
            query = query.filter(model.date >= self.DateFrom)
        if self.DateTo:
            query = query.filter(model.date <= self.DateTo)
        return query

    def __get_current_rollout(self, stock):
        """
        @attention: 获取当日转出的数量
        """
        model = _getOper("rollout").model
        query = stock.rolls.filter(model.date >= self.DateFrom,
                                   model.date <= self.DateTo).filter(model.roll_type == u'转出')
        numbers = sum([_r.number for _r in query.all()] or [0])
        return numbers

    def __get_current_rollloss(self, stock):
        """
        @attention: 获取当日报损的数量
        """
        model = _getOper("rollloss").model
        query = stock.rolls.filter(model.date >= self.DateFrom,
                                   model.date <= self.DateTo).filter(model.roll_type == u'报损')
        numbers = sum([_r.number for _r in query.all()] or [0])
        return numbers

    def __get_loss_out(self, stock):
        """
        @attention: 获取昨日的转出和报损的数量
        """
        model = _getOper("rollloss").model
        query = stock.rolls.filter(model.date < self.DateFrom)
        _lt = sum([_r.number for _r in query.all()] or [0])
        return _lt

    def __get_current_sell(self, stock):
        """
        @attention: 获取当日买出的商品
        @return:  今日卖出数量 和 昨日卖出数量
        """
        model = _getOper("sell").model
        query = stock.sells.filter(model.date >= self.DateFrom, model.date <= self.DateTo)
        numbers = sum([sell.number for sell in query.all()] or [0])
        _lt = stock.sells.filter(model.date < self.DateFrom)
        _lt_num = sum([sell.number for sell in _lt.all()] or [0])
        return numbers, _lt_num

    def __get_current_back_all_stock(self):
        """
        @attention:  获取当日退货的商品
        """
        _oper = _getOper("rollback")
        self.DateFrom = self.ReqData.get("dateFrom")
        query = self.__get_date_filter(_oper)
        backs = query.all()
        stock = [back.sell.stock for back in backs]
        return stock

    def __get_current_roll_all_stock(self, operate_type):
        """
        @attention: 获取当日转出的商品/报损的商品
        """
        operate = _getOper(operate_type)
        self.DateFrom = self.ReqData.get("dateFrom")
        query = self.__get_date_filter(operate)
        rolls = query.all()
        stock = [roll.stock for roll in rolls]
        return stock

    def __get_current_sell_all_stock(self):
        """
        @attention: 获取当日买出的商品的入库信息
        """
        self.DateFrom = self.ReqData.get("dateFrom")
        query = self.__get_date_filter(_getOper("sell"))
        sells = query.all()
        stock = [sell.stock for sell in sells]
        return stock

    @staticmethod
    def __sort_stock(self, one, two):
        if one.id > two.id:
            return 1
        return -1

    def __get_current_stock(self):
        """
        @attention: 获取今日入库的商品
        """
        _query = self.__get_date_filter(_getOper("stock"))
        models = _query.all()
        return models

    def __get_stock(self):
        """
        @attention: 获取截至到今日所有的存储信息
        """
        operate = _getOper("stock")
        self.DateFrom = None
        _query = self.__get_date_filter(operate)
        # 截至到今日仍然没有卖出的商品
        models = _query.filter(operate.model.isout == 0).all()
        # 今日卖出的商品
        _sells = self.__get_current_sell_all_stock()
        # 今日转出和报损的商品
        _roll_O = self.__get_current_roll_all_stock("rollout")
        # 今日退货的商品
        _roll_b = self.__get_current_back_all_stock()
        _sells.extend(_roll_O)
        _sells.extend(_roll_b)
        for _sell in _sells:
            if _sell not in models:
                models.append(_sell)
        models.sort(self.__sort_stock)
        return models

    @staticmethod
    def __get_slice_data(self, data):
        return data

    def __get_prev_back_number(self, stock):
        """
        @attention: 获取昨日的退货信息
        """
        model = _getOper("rollback").model
        sells = stock.sells.all()
        backs = []
        for sell in sells:
            backs.extend(sell.roll_backs.filter(model.date < self.DateFrom).all())
        return sum([back.number for back in backs] or [0])

    def __get_current_back_number(self, stock):
        """
        @attention: 获取今日的退货信息
        """
        model = _getOper("rollback").model
        sells = stock.sells.all()
        backs = []
        for sell in sells:
            backs.extend(sell.roll_backs.filter(model.date >= self.DateFrom, model.date <= self.DateTo).all())
        return sum([back.number for back in backs] or [0])

    def __get_all_data(self):
        self.page_number = self.ReqData.get("pageNumber")
        self.page_size = self.ReqData.get("pageSize")
        self.DateTo = self.ReqData.get("dateTo")

        # 今天所有交互的商品
        stocks = self.__get_stock()
        data = _getOper("stock").get_data(stocks, True)[-1]
        self.DateFrom = self.ReqData.get("dateFrom")
        current_stock = self.__get_current_stock()
        for one, stock in zip(data, stocks):
            sells, _lt_sell = self.__get_current_sell(stock)
            b_num = self.__get_current_back_number(stock)
            rollloss = self.__get_current_rollloss(stock)
            rollout = self.__get_current_rollout(stock)
            _lt_roll = self.__get_loss_out(stock)
            if stock in current_stock:
                one["stock"] = stock.number
                one["prestock"] = 0
                one['sell'] = sells
                one['rollout'] = rollout
                one['rollloss'] = rollloss
                one['curstock'] = one['stock'] - sells - rollloss - rollout + b_num
                one['rollback'] = b_num
            else:
                b_num = self.__get_current_back_number(stock)
                _lt_b = self.__get_prev_back_number(stock)
                one['stock'] = 0
                one['sell'] = sells
                one['rollout'] = rollout
                one['rollloss'] = rollloss
                one['prestock'] = stock.number - _lt_sell - _lt_roll + _lt_b
                one['curstock'] = one['prestock'] - sells - rollloss - rollout + b_num
                one["rollback"] = b_num
        return data

    def get_all_info(self):
        data = self.__get_all_data()
        return len(data), self.__get_slice_data(data)

    def buy_or_sell(self):
        length, _data = self.get_all_info()
        for cell in _data:
            cell['total_price'] = float(cell.get("price") or 0) * float(cell.get("curstock") or 0)
        return dataUtil.ResOk({'data': _data, 'length': length})

    @staticmethod
    def __get_has_money(self, sell):
        _money = _getOper("money")
        _model = dataUtil.getModel(_money, id=sell.money_id)[0]
        return _model.price

    @staticmethod
    def __get__roll_back_number(self, sell):
        roll_back = sell.roll_backs.all()
        number = sum([_r.number for _r in roll_back] or [0])
        return number

    # ===========================================================================
    # 商品销售表
    # ===========================================================================
    @staticmethod
    def __get_sell_stock_info(self, one, stock):
        one['name'] = stock.name
        one['brand_id'] = stock.brand_id
        one['standard'] = stock.standard
        one['car_number'] = stock.car_number
        one['category'] = stock.category
        one['stock_notice'] = stock.notice
        one['support_id'] = _userOpt.get(id=stock.support_id)[-1][0].username
        one['stock_price'] = stock.price

    def __get_roll_back(self):
        """
        @attention: 获取商品的退货信息
        """
        _query = self.__get_date_filter(_getOper("rollback"))
        models = _query.all()
        sells = [roll.sell for roll in models]
        return sells, models

    def __sell_back(self):
        """
        @attention: 退货信息中销售数量为0
        """
        sells, backs = self.__get_roll_back()  # 退货的销售信息
        data = _getOper("sell").get_data(sells, True)[-1]
        for one, back in zip(data, backs):
            stock = back.sell.stock
            self.__get_sell_stock_info(one, stock)
            one['rollNumber'] = -back.number
            one['has_get'] = self.__get_has_money(back) or 0.0
            _price = back.sell.price
            one['all_price'] = _price * one['rollNumber']
            one['for_get'] = one['all_price']
            one['number'] = 0
            one['price'] = _price
        return data

    def __sell(self):
        """
        @attention:  销售表中退货数量为 0 
        """
        self.page_number = self.ReqData.get("pageNumber")
        self.page_size = self.ReqData.get("pageSize")
        self.DateFrom = self.ReqData.get("dateFrom")
        self.DateTo = self.ReqData.get("dateTo")
        operate = _getOper("sell")
        _query = self.__get_date_filter(operate)
        models = _query.all()
        _sells = operate.get_data(models, True)[-1] or []
        for one, model in zip(_sells, models):
            stock = model.stock
            self.__get_sell_stock_info(one, stock)
            one['rollNumber'] = 0
            one['has_get'] = self.__get_has_money(model) or 0.0
            _price = model.price
            one['all_price'] = _price * model.number
            one['for_get'] = model.number * _price
            one['price'] = _price
        # 获取商品退货产生的销售信息
        data = self.__sell_back() or []
        _sells.extend(data)
        return _sells

    def sell(self):
        _sells = self.__sell()
        return dataUtil.ResOk({'data': _sells, 'length': len(_sells)})

    def get_agent_roll(self, stock, roll_type):
        operate = _getOper("rollout")
        models = stock.rolls.filter(operate.model.roll_type == roll_type).all()
        data = operate.get_data(models, True)[-1]
        for one, model in zip(data, models):
            self.__get_sell_stock_info(one, model.stock)
            one["number"] = model.number
            one['price'] = 0
            one["_type"] = roll_type
            one["all_price"] = one.get("number") * one.get("price")
        return data

    def get_agent_roll_out(self, stock):
        return self.get_agent_roll(stock, u"转出")

    def get_agent_roll_loss(self, stock):
        return self.get_agent_roll(stock, u"报损")

    def get_agent_roll_back(self, stock):
        sells = stock.sells
        _back = []
        for sell in sells:
            _back.extend(sell.roll_backs)
        _oper = _getOper("rollback")
        data = _oper.get_data(_back, True)[-1]
        for one, model in zip(data, _back):
            self.__get_sell_stock_info(one, model.sell.stock)
            one["number"] = -model.number
            one['price'] = model.sell.price_a
            one["_type"] = u"退货"
            one["all_price"] = one.get("number") * one.get("price")
        return data

    def get_agent_sell(self, stock):
        models = stock.sells
        data = _getOper("sell").get_data(models, True)[-1]
        for one, model in zip(data, models):
            self.__get_sell_stock_info(one, model.stock)
            one["number"] = model.number
            one['price'] = model.price_a
            one["_type"] = u"销售"
            one["all_price"] = one.get("number") * one.get("price")
        return data

    def get_agent_stock(self):
        query = self.__get_date_filter(_oper)
        models = query.all()
        data = _getOper("stock").get_data(models, True)[-1]
        for one in data:
            one["number"] = - one.get("number")
            one["_type"] = u"入库"
            one["stock_notice"] = one["notice"]
            one["notice"] = ""
            one["all_price"] = one.get("number") * one.get("price")
        for stock in models:
            data.extend(self.get_agent_sell(stock))
            data.extend(self.get_agent_roll_back(stock))
            data.extend(self.get_agent_roll_out(stock))
            data.extend(self.get_agent_roll_loss(stock))
        return data

    # ===========================================================================
    # 代销明细表
    # ===========================================================================
    def agent(self):
        """
        @attention: 代销的商品价格使用备注价格 price_a
        """
        self.page_number = self.ReqData.get("pageNumber")
        self.page_size = self.ReqData.get("pageSize")
        self.DateFrom = self.ReqData.get("dateFrom")
        self.DateTo = self.ReqData.get("dateTo")
        data = self.get_agent_stock()
        _sells = filter(lambda one: one.get("category").encode("UTF-8") == "代销", data)
        return dataUtil.ResOk({'data': _sells, 'length': len(_sells)})

    @staticmethod
    def sort_result(self, one, two):
        _date1 = one.get("date")
        _date2 = two.get("date")
        if dataUtil.IsLessDate(_date1, _date2):
            return 1
        else:
            return -1

    # ===========================================================================
    # 利润表
    # ===========================================================================
    def _profit_roll_loss(self):
        """
        @attention: 获取报损产生的利润信息
        """
        operate = _getOper("rollloss")
        _query = self.__get_date_filter(operate)
        rolls = _query.all()
        data = operate.get_data(rolls, True)[-1]
        for one, roll in zip(data, rolls):
            stock = roll.stock
            self.__get_sell_stock_info(one, roll.stock)
            _number = roll.number
            one['all_number'] = _number
            one['price'] = 0
            one['sell_all'] = 0
            one['stock_all'] = _number * stock.price
            one['all_price'] = one['sell_all'] - one['stock_all']
            one['_type'] = u"报损"
            one['customer_id'] = u"报损"
        return data

    def _profit_back(self):
        """
        @attention: 退货信息中销售数量为0
        """
        sells, backs = self.__get_roll_back()  # 退货的销售信息
        data = _getOper("sell").get_data(sells, True)[-1]
        for one, back in zip(data, backs):
            sell = back.sell
            stock = sell.stock
            self.__get_sell_stock_info(one, stock)
            _number = back.number
            one['all_number'] = -back.number
            one['sell_all'] = _number * sell.price
            one['stock_all'] = _number * stock.price
            one['all_price'] = _number * (stock.price - sell.price)
            one['_type'] = u"退货"
        return data

    def profit(self):
        self.page_number = self.ReqData.get("pageNumber")
        self.page_size = self.ReqData.get("pageSize")
        self.DateFrom = self.ReqData.get("dateFrom")
        self.DateTo = self.ReqData.get("dateTo")
        operate = _getOper("sell")
        _query = self.__get_date_filter(operate)
        models = _query.all()
        _sells = operate.get_data(models, True)[-1]
        for one, model in zip(_sells, models):
            stock = model.stock
            self.__get_sell_stock_info(one, stock)
            _number = model.number
            one['sell_all'] = _number * model.price
            one['stock_all'] = _number * stock.price
            one["all_number"] = _number
            one["all_price"] = _number * (model.price - stock.price)
            one['_type'] = u"销售"
        _b_sell = self._profit_back() or []
        _r_loss = self._profit_roll_loss() or []
        _sells.extend(_b_sell)
        _sells.extend(_r_loss)
        _sells = filter(lambda one: one.get("category").encode("UTF-8") == "购进", _sells)
        return dataUtil.ResOk({'data': _sells, 'length': len(_sells)})

    def main(self, operate_type):
        self.ReqData = request.form.to_dict()
        data = getattr(self, operate_type)()
        _ds = data.get("msg").get("data")
        if _ds:
            _ds.sort(self.sort_result)
            data['msg']['data'] = _ds
        return data

    def load_init_data(self, operate_type):
        dateTo = dataUtil.CurrentDateStr
        if "buyorsell" == operate_type.lower():
            date_from = dataUtil.GetInitPrevDate(dateTo, 0)
        else:
            date_from = dataUtil.GetInitPrevDate(dateTo, 0)
        self.ReqData = {'pageSize': 1000, 'pageNumber': 1, 'dateFrom': date_from, "dateTo": dateTo}
        _ds = getattr(self, operate_type)().get("msg").get('data')
        _ds.sort(self.sort_result)
        return _ds

    @staticmethod
    def get_page_config(self, operate_type):
        config = page_table_configs.get(operate_type.lower())
        data = [(one.get("field"), one.get("title")) for one in config]
        column = [one[0] for one in data]
        first = [one[1] for one in data]
        return first, column

    def get_data(self, operate_type):
        first, column = self.get_page_config(operate_type)
        _result = [first]
        [_result.append([one.get(col) for col in column]) for one in self.main(operate_type).get('msg').get("data")]
        return _result

    @staticmethod
    def __get_file(self, file_name):
        return current_app.config.get("DOWNLOAD_FILE") + "/" + file_name

    @staticmethod
    def get_file_name(self, operate_type, gbk=False):
        data = {"sell": u"销售表", "profit": u'利润表',
                "agent": u"代销表", "buyorsell": u"进销存表"}
        if gbk:
            file_name = "%s_%s_%s.xlsx" % (dataUtil.CurrentDateStr,
                                           current_user.username,
                                           data.get(operate_type))
        else:
            file_name = "%s_%s_%s.xlsx" % (dataUtil.CurrentDateStr,
                                           current_user.id,
                                           operate_type)
        return file_name

    @staticmethod
    def get_true_str(self, one):
        try:
            one = str(one)
        except:
            pass
        return one

    def down_load_excel(self, operate_type):
        data = self.get_data(operate_type)
        _Excel = Excel(AppQueue.GetApp())
        _Excel.open()
        file_name = self.get_file_name(operate_type)
        _fileName = self.__get_file(file_name)
        _Excel.WriteDataToExcelNull(data, file_name)
        _Excel.save(_fileName)
        _Excel.close()
        return dataUtil.ResOkJson("%s" % file_name)

    def down_load_pdf(self, operate_type):
        self.down_load_excel(operate_type)
        file_name = self.get_file_name(operate_type)
        ExcelToPdf().Main([self.__get_file(file_name)])
        self.delete_file(file_name)
        file_name = file_name.replace(".xlsx", ".pdf")
        return dataUtil.ResOkJson("%s" % file_name)

    def down_ok(self, operate_type, file_name):
        last = file_name.split(".")[1]
        _fileName = self.__get_file(file_name)
        _fileName = _fileName.split(".")[0] + "." + last
        _name = self.get_file_name(operate_type, True).split(".")[0] + "." + last
        response = make_response(send_file(_fileName))
        response.headers["content_type"] = "application/octet-stream"
        response.headers["Content-Disposition"] = "attachment; filename=%s;" % _name.encode("utf-8")
        return response

    def delete_file(self, file_name):
        file_name = self.__get_file(file_name)
        try:
            os.remove(file_name)
            return dataUtil.ResOkJson("ok")
        except:
            return dataUtil.ResErrorJson("移除文件失败:%s" % file_name)

    def download(self):
        self.ReqData = request.form.to_dict()
        return getattr(self, "down_load_%s" % self.ReqData.get("fileType").lower())(self.ReqData.get("operType"))


_searchUtil = Search()
