# -*- coding:utf-8 -*-
'''
@email:289012724@qq.com
@author: shuiyaoyao
@telephone:13587045516
'''
from ...common import _dataBaseUtil as dataUtil

_finance = "Finance"
_getOper = dataUtil.GetPartial(_finance)
_billOpt = _getOper("bill")
DateFormat = "%Y-%m-%d"
_user = dataUtil.getDataBase("UserOperate", "User")


class BillService(object):
    """
    @attention:  处理账单相关的创建更新和修改
    """

    def GetBillDate(self, date):
        """
        @attention: 生产单的唯一标记号
        @param date: 时间节点
        """
        try:
            date = date.split("-")
        except:
            date = date.strftime("%Y-%m-%d")
            date = date.split("-")
        date[-1] = "01"
        date = "-".join(date)
        return date

    def HasBill(self, customer_id, date):
        """
        @attention: 检测是否存在对应的账单信息
        """
        _oper = _getOper("bill")
        date = self.GetBillDate(date)
        state, model = _oper.get(customer_id=customer_id, date=date)
        if state and model:
            return True

    def __new_bill(self, kwargs):
        date = kwargs.get("date")
        total_money = kwargs.get("total_money") or 0
        next_money = kwargs.get("next_money") or 0
        level_money = total_money - next_money
        operator_id = kwargs.get("operator_id")
        customer_id = kwargs.get("customer_id")
        has_filled = kwargs.get("has_filled") or 0
        bill = _getOper("bill").model()
        bill.Init((date, total_money, next_money, level_money,
                   customer_id, operator_id))
        bill.has_filled = has_filled
        return bill

    def AddNew(self, _ses, **kwargs):
        """
        @attention: 向数据库中添加新的账单信息
        """
        try:
            bill = self.__new_bill(kwargs)
            _ses.add(bill)
            return True
        except Exception, e:
            print "输入的参数有误", e
            return False

    def UpdateModel(self, _ses, date, money_price):
        _oper = _getOper("bill")
        date = self.GetBillDate(date)
        state, model = _oper.get(date == date)
        if state and model:
            self.UpdateByRebund(_ses, model[0].id, money_price)
            return True

    def get_sell_money(self, sell):
        """
        @attention: 获取销售的付款信息
        """
        _oper = dataUtil.getDataBase("money", "Production")
        state, model = _oper.get(id=sell.money_id)
        if state and model:
            return model[0].price
        print state, model
        return 0

    def get_roll_money(self, roll):
        """
        @attention: 获取退款中的付款信息
        """
        _oper = dataUtil.getDataBase("money", "Production")
        money = dataUtil.getModel(_oper, id=roll.money_id)[0]
        return money.price

    def __get_date_filter(self, _oper, start, end):
        model = _oper.model
        query = model.query
        query = query.filter(model.date >= start, model.date < end)
        return query

    def __get_bill_date(self, bill):
        oriDate = bill.date.strftime(DateFormat)
        starts = oriDate.split("-")
        year, moth, date = [int(c) for c in starts]
        if moth == 12:
            year += 1
            moth = 1
        else:
            moth += 1
        end = "%s-%s-%s" % (year, moth, date)
        return oriDate, end

    def get_back_total(self, bill):
        """
        @attention: 获取当月用户退的货的数据
        end 是指的下个月的一号 ，不计算在当月的范围内
        """
        start, end = self.__get_bill_date(bill)
        customer_id = bill.customer_id
        _oper = dataUtil.getDataBase("rollback", "Production")
        query = self.__get_date_filter(_oper, start, end)
        query = query.filter(_oper.model.customer_id == customer_id)
        models = query.all()
        rmoney = [self.get_roll_money(model) for model in models] or [0]
        rmoney = sum(rmoney)
        _price = [model.sell.price * model.number for model in models] or [0]
        _price = sum(_price)
        backData = -(rmoney + _price)
        return backData

    def get_sell_total(self, bill):
        """
        @attention: 获取当月销售给用户的数据
        """
        start, end = self.__get_bill_date(bill)
        customer_id = bill.customer_id
        _oper = dataUtil.getDataBase("sell", "Production")
        query = self.__get_date_filter(_oper, start, end)
        query = query.filter(_oper.model.customer_id == customer_id)
        models = query.all()
        rmoney = [self.get_sell_money(model) for model in models] or [0]
        rmoney = sum(rmoney)
        _price = [model.price * model.number for model in models] or [0]
        _price = sum(_price)
        return _price - rmoney

    def _update_bill_total(self, bill):
        """
        @将对账单的更新加入到事务中
        """
        sell = self.get_sell_total(bill)
        back = self.get_back_total(bill)
        total_money = sell + back
        bill.total_money = total_money
        bill.level_money = bill.total_money - bill.next_money
        return True

    def _update_bill_next(self, bill):
        bill.next_money = _billOpt.GetBillAllMoney(bill.id)
        bill.level_money = bill.total_money - bill.next_money
        return True

    def _is_update(self, bill):
        date = bill.date.strftime(DateFormat)
        dateN = dataUtil.CurrentDateStr
        date1 = self.GetBillDate(date)
        date2 = self.GetBillDate(dateN)
        if bill.has_filled != 0:
            return True

        stamp1 = dataUtil.MakeTime(date1)
        stamp2 = dataUtil.MakeTime(date2)
        if stamp1 == stamp2:
            return False
        return True

    def UpdateBillTotal(self, bill):
        """
        @attention: update the has filled bill
        """
        if self.idCode != 1:
            return self._update_bill_next(bill)

        if self._is_update(bill):
            return self._update_bill_total(bill)

    def UpdateOneBill(self, _ses, bill_o, bill_n):
        if bill_n and self.UpdateBillTotal(bill_n):
            _ses.add(bill_n)
        if bill_o and self.UpdateBillTotal(bill_o):
            _ses.add(bill_o)

    def UpdateTwoBill(self, _ses, bill_o, bill_n):
        if bill_n.id != bill_o.id:
            if self.UpdateBillTotal(bill_o):
                _ses.add(bill_o)
            if self.UpdateBillTotal(bill_n):
                _ses.add(bill_n)
        else:
            if self.UpdateBillTotal(bill_o):
                _ses.add(bill_o)

    def GetBill(self, customer_id, date):
        model = _billOpt.model
        query = model.query.filter(model.customer_id == customer_id,
                                   model.date == date)
        models = query.all()
        if models:
            return models[0]

    def _SetError(self, bill_o, bill_n):
        self.error = ""
        if bill_o and bill_n and bill_n.id == bill_o.id:
            user = _user.get(id=bill_o.customer_id)[-1][0]
            self.error += u"请手动更新%s,%s的对账单" % (user.username, bill_o.date.strftime("%Y-%m-%d"))
        else:
            if bill_o:
                user = _user.get(id=bill_o.customer_id)[-1][0]
                self.error += u"请手动更新%s,%s的对账单" % (user.username, bill_o.date.strftime("%Y-%m-%d"))
            if bill_n:
                user = _user.get(id=bill_n.customer_id)[-1][0]
                self.error += u"请手动更新%s,%s的对账单" % (user.username, bill_n.date.strftime("%Y-%m-%d"))

    def UpdateAllBill(self, curent_user, current_date, old_user, old_date):
        _ses = _billOpt.Session
        current_date = self.GetBillDate(current_date)
        old_date = self.GetBillDate(old_date)
        bill_o = self.GetBill(old_user, old_date)
        bill_n = self.GetBill(curent_user, current_date)
        self._SetError(bill_o, bill_n)
        if bill_n and bill_o:
            self.UpdateTwoBill(_ses, bill_o, bill_n)
        else:
            self.UpdateOneBill(_ses, bill_o, bill_n)
        try:
            _ses.commit()
            return True
        except Exception, e:
            print e

    def UpdateAllByTotal(self, curent_user, current_date, old_user, old_date):
        """
        @attention: 因销售状态更改导致的修正
        """
        self.idCode = 1
        return self.UpdateAllBill(curent_user, current_date, old_user, old_date)

    def UpdateAllByNext(self, curent_user, current_date, old_user, old_date):
        """
        @attention: 因还款导致的修正
        """
        self.idCode = 2
        return self.UpdateAllBill(curent_user, current_date, old_user, old_date)

    def GetError(self):
        if hasattr(self, "error"):
            return self.error
        return ""

    def GetBillError(self, bill):
        user = _user.get(id=bill.customer_id)[-1][0]
        date = bill.date.strftime("%Y-%m-%d")
        error = "计算用户:%s  日期:%s 的账单失败,错误原因:" % (user, date)
        return error

    def UpdateAllOneBill(self, bill):
        sell = self.get_sell_total(bill)
        back = self.get_back_total(bill)
        total_money = sell + back
        bill.total_money = total_money
        bill.next_money = _billOpt.GetBillAllMoney(bill.id)
        bill.level_money = bill.total_money - bill.next_money
        _billOpt.ModelList = bill
        return _billOpt.update()

    def GetToUpdateBill(self, start, end, userId):
        model = _billOpt.model
        query = model.query.filter(model.date >= start)
        if end:
            query = query.filter(model.date <= end)
        if userId:
            query = query.fitler(model.customer_id == userId)
        return query.all()

    def UpdateBillAll(self, start, end=None, userId=None):
        errors = []
        if end: end = self.GetBillDate(end)
        models = self.GetToUpdateBill(start, end, userId)
        for bill in models:
            start, model = self.UpdateAllOneBill(bill)
            if not (start and model):
                _err = self.GetBillError(bill)
                _err += model
                errors.append(_err)
        return errors


_BillService = BillService()
