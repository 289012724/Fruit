# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''

from ...common import exception_show_class
from ...common import _dataBaseUtil as dataUtil
from ...Finance.services.BillService import _BillService

_getOperate = dataUtil.GetPartial("Production")


class DeleteModel(object):
    def __init__(self):
        object.__init__(self)
        self.__operate_type = None
        self.__goodsId = None

    @property
    def operate_type(self):
        return self.__operate_type

    @operate_type.setter
    def operate_type(self, value):
        self.__operate_type = value

    @property
    def good_ids(self):
        return self.__goodsId

    @good_ids.setter
    def good_ids(self, value):
        self.__goodsId = value

    def delete_storage(self, model, _session):
        sells = _getOperate("sell").get(stock_id=model.id)[-1]
        # 添加销售相关的关联数据关系,更新相关的账单
        [self.delete_sells(model, _session) for model in sells]

    @staticmethod
    def get_money_model(self, uid):
        _money = _getOperate("money").get(id=uid)[-1]
        return _money[0]

    @staticmethod
    def get_bill(self, date, user_id):
        state, model = dataUtil.getDataBase("bill", 'Finance').get(customer_id=user_id,
                                                                   date=_BillService.get_bill_date(date))
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

    def delete_sells(self, model, _session):
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
        [self.delete_roll_back(back, _session) for back in model.roll_backs]

    def delete_roll_back(self, model, _session):
        money = self.get_money_model(model.money_id)
        total = model.sell.price * model.number
        if money.id != 1:
            _session.delete(money)
            total = (money.price + total)
        bill = self.get_bills(model.date.strftime("%Y-%m-%d"), model.customer_id, total)
        if bill: _session.add(bill)

    @exception_show_class
    def delete_models(self, operate_type, uid):
        """
        @attention: 删除数据
        @param operate_type:商品类型
        @param uid:产品ID号  
        """
        self.operate_type = operate_type
        self.good_ids = uid
        operate = _getOperate(self.operate_type)
        _session = operate.Session
        model = dataUtil.getModel(operate, id=self.good_ids)
        if not model:
            return dataUtil.ResError(u"删除数据失败,不存在选择的商品,请刷新页面")

        model = model[0]
        if self.operate_type in ['sell', 'rollout', 'rollloss']:
            model.stock.isout = 0
        if self.operate_type == 'sell':
            self.delete_sells(model, _session)
        elif self.operate_type == "stock":
            self.delete_storage(model, _session)
        elif self.operate_type == 'rollback':
            self.delete_roll_back(model, _session)

        _session.delete(model)
        try:
            _session.commit()
        except:
            return dataUtil.ResError(u"删除数据失败")
        return dataUtil.ResOk(u"删除数据成功")

    @staticmethod
    def __check_sell(self, model):
        """
        @attention: 检测是否存在退货信息
        """
        ok = model.roll_backs.all()
        if ok:
            return dataUtil.ResError("存在关联数据,是否仍然继续删除?")
        return dataUtil.ResOk("ok")

    @staticmethod
    def __check_stock(self, model):
        """
        @attention: 检测是有转出或则销售信息
        """
        ok = model.sells.all() or model.rolls.all()
        if ok:
            return dataUtil.ResError(u"存在关联数据,是否仍然继续删除?")
        return dataUtil.ResOk("ok")

    def check_state(self, operate_type, uid):
        """
        @attention: 检测入库商品或则销售的商品是否可以删除,如果存在关联数据
        则不能删除,这个位置没有加入对已经出账的信息进行检查
        @param operate_type: 操作的类型
        @param uid:商品ID号  
        """
        self.operate_type = operate_type
        self.good_ids = uid
        _model = dataUtil.getModel(_getOperate(self.operate_type), id=self.good_ids)
        if not _model:
            return dataUtil.ResError(u"不存在数据行")

        if self.operate_type == 'stock':
            return self.__check_stock(_model[0])

        if self.operate_type == "sell":
            return self.__check_sell(_model[0])

        else:
            return dataUtil.ResOk("ok")

    @staticmethod
    def __check_stock_id(self, user_id):
        """
        @attention: 检测是否存在供应商提供的入库商品信息
        @param user_id: 供应商ID号 
        """
        return dataUtil.getModel(_getOperate('stock'), support_id=user_id)

    @staticmethod
    def __check_operate_id(self, user_id, role_type):
        """
        @attention: 检测是否存在某客户的相关数据
        @param user_id: 用户ID号
        @param role_type:用户的类型  
        """
        if role_type == "customer":
            has_sell = dataUtil.getModel(_getOperate("sell"), customer_id=user_id)
            has_roll = False
            has_stock = False
        else:
            has_sell = dataUtil.getModel(_getOperate("sell"), operator_id=user_id)
            has_roll = dataUtil.getModel(_getOperate("rollout"), operator_id=user_id)
            has_stock = dataUtil.getModel(_getOperate("stock"), operator_id=user_id)
        return has_roll or has_sell or has_stock

    def can_delete_user(self, user_id, role_type):
        """
        @attention: 检测当前的数据是否可以删除,指代的是是否可以删除当前的用户数据
        对于商品数据，任何时候都可以删除，删除了之后，会自动将关联的商品数据删除掉
        @param user_id:当前用户id号
        @param role_type: 当前的操作类型 部门还是用户
        """
        if role_type.lower() == "supporter":
            return self.__check_stock_id(user_id)
        return self.__check_operate_id(user_id, role_type)


_deleteModelUtil = DeleteModel()
