# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''

from ...common import exception_show_class
from ...common import _dataBaseUtil as dataUtil
from ...Finance.services.BillService import _BillService

_getOper = dataUtil.GetPartial("Production")


class DeleteModel(object):
    def __init__(self):
        object.__init__(self)
        self.__operType = None
        self.__goodsId = None

    @property
    def OperType(self):
        return self.__operType

    @OperType.setter
    def OperType(self, value):
        self.__operType = value

    @property
    def GoodsId(self):
        return self.__goodsId

    @GoodsId.setter
    def GoodsId(self, value):
        self.__goodsId = value

    def DeleteStock(self, model, _session):
        _oper = _getOper("sell")
        sells = _oper.get(stock_id=model.id)[-1]
        # 添加销售相关的关联数据关系,更新相关的账单
        [self.DeleteSellPro(model, _session) for model in sells]

    def get_money_model(self, money_id):
        _oper = _getOper("money")
        _money = _oper.get(id=money_id)[-1]
        return _money[0]

    def get_bill(self, date, user_id):
        _oper = dataUtil.getDataBase("bill", 'Finance')
        bill_date = _BillService.GetBillDate(date)
        state, model = _oper.get(customer_id=user_id, date=bill_date)
        if state and model:
            return model[0]

    def get_bills(self, date, user_id, price):
        model = self.get_bill(date, user_id)
        if model and model.has_filled == 1:
            model.total_money += price
            model.level_money = model.total_money - model.next_money
            print price, model.total_money, model.level_money
            return model
        return None

    def DeleteSellPro(self, model, _session):
        """
        @attention: 开启删除事务处理
        @param model:需要删除的销售商品
        @param _session:当前会话  
        @note: 在删除的过程中会删除相关连的数据,如果相关联的数据删除失败
        则需要去手动检测到底是什么数据删除失败可能存在的情况,在删除商品数据的时候，
        因为存在关联删除,所有后面不在需要在向删除session 中添加数据
        1 入库商品已经被删除，当前页面存在的不是最新数据
        """
        total = model.number * model.price
        _money1 = self.get_money_model(model.money_id)
        if _money1.id != 1:
            _price3 = _money1.price
            total -= _price3
            _session.delete(_money1)
        date = model.date.strftime("%Y-%m-%d")
        bill = self.get_bills(date, model.customer_id, -total)
        if bill: _session.add(bill)
        # 删除关联的退货信息和更新相关的账单
        [self.DeleteRollback(back, _session) for back in model.roll_backs]

    def DeleteRollback(self, model, _session):
        money = self.get_money_model(model.money_id)
        total = model.sell.price * model.number
        if money.id != 1:
            _session.delete(money)
            total = (money.price + total)
        bill = self.get_bills(model.date.strftime("%Y-%m-%d"), model.customer_id, total)
        if bill: _session.add(bill)

    #     @exception_show_class
    def DeleteModels(self, operType, productionId):
        """
        @attention: 删除数据
        @param operType:商品类型
        @param productionId:产品ID号  
        """
        self.OperType = operType
        self.GoodsId = productionId
        _oper = _getOper(self.OperType)
        _session = _oper.Session
        model = dataUtil.getModel(_oper, id=self.GoodsId)
        if not model:
            return dataUtil.ResError(u"删除数据失败,不存在选择的商品,请刷新页面")

        model = model[0]
        if self.OperType in ['sell', 'rollout', 'rollloss']:
            model.stock.isout = 0
        if self.OperType == 'sell':
            self.DeleteSellPro(model, _session)
        elif self.OperType == "stock":
            self.DeleteStock(model, _session)
        elif self.OperType == 'rollback':
            self.DeleteRollback(model, _session)

        _session.delete(model)
        try:
            _session.commit()
        except:
            return dataUtil.ResError(u"删除数据失败")
        return dataUtil.ResOk(u"删除数据成功")

    def __check_sell(self, model):
        """
        @attention: 检测是否存在退货信息
        """
        ok = model.roll_backs.all()
        if ok:
            return dataUtil.ResError("存在关联数据,是否仍然继续删除?")
        return dataUtil.ResOk("ok")

    def __check_stock(self, model):
        """
        @attention: 检测是有转出或则销售信息
        """
        ok = model.sells.all() or model.rolls.all()
        if ok:
            return dataUtil.ResError(u"存在关联数据,是否仍然继续删除?")
        return dataUtil.ResOk("ok")

    def CheckState(self, operType, productionId):
        """
        @attention: 检测入库商品或则销售的商品是否可以删除,如果存在关联数据
        则不能删除,这个位置没有加入对已经出账的信息进行检查
        @param operType: 操作的类型
        @param productionId:商品ID号  
        """
        self.OperType = operType
        self.GoodsId = productionId
        _oper = _getOper(self.OperType)
        _model = dataUtil.getModel(_oper, id=self.GoodsId)
        if not _model:
            return dataUtil.ResError(u"不存在数据行")

        if self.OperType == 'stock':
            return self.__check_stock(_model[0])
        elif self.OperType == "sell":
            return self.__check_sell(_model[0])
        else:
            return dataUtil.ResOk("ok")

    def __check_stock_id(self, userId):
        """
        @attention: 检测是否存在供应商提供的入库商品信息
        @param userId: 供应商ID号 
        """
        return dataUtil.getModel(_getOper('stock'), support_id=userId)

    def __check_operate_id(self, userId, roleType):
        """
        @attention: 检测是否存在某客户的相关数据
        @param userId: 用户ID号
        @param roleType:用户的类型  
        """
        if roleType == "customer":
            has_sell = dataUtil.getModel(_getOper("sell"), customer_id=userId)
            has_roll = False
            has_stock = False
        else:
            has_sell = dataUtil.getModel(_getOper("sell"), operator_id=userId)
            has_roll = dataUtil.getModel(_getOper("rollout"), operator_id=userId)
            has_stock = dataUtil.getModel(_getOper("stock"), operator_id=userId)
        return has_roll or has_sell or has_stock

    def CheckDeleteUser(self, userId, roleType):
        """
        @attention: 检测当前的数据是否可以删除,指代的是是否可以删除当前的用户数据
        对于商品数据，任何时候都可以删除，删除了之后，会自动将关联的商品数据删除掉
        @param userId:当前用户id号
        @param roleType: 当前的操作类型 部门还是用户
        """
        if roleType == "supporter":
            return self.__check_stock_id(userId)
        return self.__check_operate_id(userId, roleType)


_deleteModelUtil = DeleteModel()
