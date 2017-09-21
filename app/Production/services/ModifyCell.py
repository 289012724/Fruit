# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email : 289012724@qq.com
'''

from ...common          import _dataBaseUtil
from functools          import partial
import copy
from ...Finance.services.BillService import _BillService

_getOper = partial(_dataBaseUtil.getDataBase, blueprint="Production")

class ModifyCell(object):
    def __init__(self):
        object.__init__(self)
        self.__requstForm = None
        self.__model = None
        self.__blueprint = None
        self.__productionId = None
    @property    
    def RequstForm(self):return self.__requstForm
    
    @RequstForm.setter
    def RequstForm(self, value):
        self.__requstForm = value
        self.ProductionId = self.RequstForm.get('production_id')
        dataId = int(self.RequstForm.get('data_id'))
        self.Model = _dataBaseUtil.getModel(_getOper(self.ProductionId), id=dataId)[0]
        
    @property
    def Model(self):return self.__model
    @Model.setter
    def Model(self, value):self.__model = value  
    @property
    def BluePrint(self):return self.__blueprint
    @BluePrint.setter
    def BluePrint(self, value):self.__blueprint = value
    @property
    def ProductionId(self):return self.__productionId
    @ProductionId.setter
    def ProductionId(self, value):self.__productionId = value
    
    
    def __update_new(self, _ses, data):
        """
        @attention: 更新账单金额
        """
        _oper =_getOper("money")
        _moneyModel = self.GetMoneyModel(self.Model.money_id)
        state, model = _oper.update_model(_moneyModel, **data)
        if state and model:
            _oper.init_modelList()
            _ses.add(_moneyModel)
            self.RequstForm['money_id'] = model.money_id
        else:
            self.error = _dataBaseUtil.ResErrorJson(u"更新价格失败%s" % model)

    def __add_new(self,data):
        _oper = _getOper("money")
        state, model = _oper.add_model(**data)
        if state and model:
            state, model = _oper.add()
            if state and model:
                # 因为在存入数据库的时候需要将Money_id存储所以必须先新建金钱账单
                self.RequstForm['money_id'] = model[0].id
            else:
                self.error = _dataBaseUtil.ResErrorJson(u"更新价格失败%s" % model)
        else:
            self.error = _dataBaseUtil.ResErrorJson(u"更新价格输入参数有误%s" % model)
    
    def GetMoneyModel(self,moeny_id):
        _money = _getOper("money")
        _moneyModel = _dataBaseUtil.getModel(_money, id=moeny_id)
        return _moneyModel[0]
    
    def __add_new_money(self, _ses, operType, sellId):
        money = self.RequstForm.get('money_id').split("@")
        _dict = {
                 "money_type":money[0],
                'tickets':self.RequstForm.get('tickets'),
                "price":money[1],
                "user_id":int(self.RequstForm.get('customer_id')),
                "date":self.RequstForm.get('date')
            }
        if self.Model.money_id != 1:
            self.__update_new(_ses,_dict)
        else:
            self.__add_new(_dict)
           
    def ModifyMoney(self, _ses, operType, sellId):
        """
        @attention: 修改付款数据
        @param operType: 操作类型
        @param sellId: 商品编号 
        """
        _money = _getOper("money")
        model = self.Model
        _moneyModel = self.GetMoneyModel(self.Model.money_id)
        # 记录下最原始的金额数据,以便后面可以回滚
        money = self.RequstForm.get('money_id').split("@")
        if float(money[-1]) == 0:
            self.RequstForm['money_id'] = 1
            if model.money_id != 1:
                _ses.delete(_moneyModel)
        else:
            self.__add_new_money(_ses, operType, sellId)
        
    def IsOk(self, state, model=True):
        return state and model
    
    def UpdateStock(self, stock):
        _stock = _getOper("stock")
        stock_n = _stock.GetAbsTotal(stock.id)
        if stock_n == 0:
            _stock.SetOut(stock, 1)
        elif stock_n < 0:
            return False
        else:
            _stock.SetOut(stock, 0)
        return True
    
    def UpateStockData(self, modelOpt):
        """
        @attention: 修改入库的数据信息
        """
        stock_n = modelOpt.GetAbsTotal(self.Model.id)
        if stock_n == 0 and int(self.RequstForm.get("number")) < self.Model.number:
            return _dataBaseUtil.ResErrorJson(u"入库数量少于已经卖出的数量,请修正")
        state, model = modelOpt.update_model(self.Model, self.RequstForm)
        if self.IsOk(state, model):
            if stock_n == 0:modelOpt.SetOut(model, 1)
            else:modelOpt.SetOut(model, 0)
            _data = modelOpt.get_data([model], True)[-1]
            return _dataBaseUtil.ResOkJson(_data)
        return _dataBaseUtil.ResErrorJson(u"修改内容失败")
    
    #===========================================================================
    # 更新退货信息
    #===========================================================================
    def _get_roll_back_stock(self):
        """
        @attention: 获取退货对入库商品做的关联影响
        """
        stock= self.Model.sell.stock
        _abs = _getOper("stock").GetAbsTotal(stock.id)
        old  = self.Model.number
        new  = self.RequstForm.get("number")
        level= _abs + new - old
        if level == 0:
            stock.isout = 1
        else:
            stock.isout = 0
        return stock
    
    def _updateBack(self, modelOpt):
        _ses = modelOpt.Session
        # 修正付款信息对退货的影响
        self.ModifyMoney(_ses, "rollback", self.Model.id)
        if self.error is not None:
            return self.error
        data = self._updateBase(_ses,self._get_roll_back_stock)
        if self.error is not None:
            return self.roll_back()
        else:
            return data
    
    def UpdateRollBack(self, modelOpt):
        """
        @attention:  修正退货的信息
        """
        sell = self.Model.sell
        total_b = _getOper("sell").get_snap_number(sell.id)
        snap = total_b + self.Model.number
        if int(self.RequstForm.get("number")) > snap:
            return _dataBaseUtil.ResErrorJson(u"输入的数量超过可退数量,请修正")
        else:
            return self._updateBack(modelOpt)
    
    def GetModelDate(self, model):
        """
        @attention:  获取模型日期时间
        """
        date = model.date()
        return date
    
    def _get_model_info(self):
        """
        @attention: 获取正常的销售模型数据
        """
        model = self.modelOpt.get(id=self.Model.id)[-1]
        sate, data = self.modelOpt.get_data(model, True)
        if sate and data:
            return _dataBaseUtil.ResOkJson(data)
        else:
            return _dataBaseUtil.ResErrorJson(u"获取数据失败,请刷新页面")
    
    def _adjust_bill(self, cuser, cdate, ouser, odate):
        if _BillService.UpdateAllByTotal(cuser, cdate, ouser, odate):
            return self._get_model_info()
        else:
            self.error = _dataBaseUtil.ResErrorJson(_BillService.GetError())

    def _updateBase(self, _ses,stockMethod):
        """
        @attention: 基础的销售数据和账单数据
        """
        # 先做账单之间的修正,后面模型的内容会更新
        ouser = self.Model.customer_id
        odate = self.GetModelDate(self.Model.date)
        cuser = self.RequstForm.get("customer_id")
        cdate = self.RequstForm.get("date")
        state, model = self.modelOpt.update_model(self.Model, self.RequstForm)
        if state and model:
            self.modelOpt.init_modelList()
            stock = stockMethod()
            _ses.add(stock)
            _ses.add(model)
            try:
                _ses.commit()
                return self._adjust_bill(cuser, cdate, ouser, odate)
            except Exception, e:
                self.error = _dataBaseUtil.ResErrorJson(u"更新销售信息失败%s" % e)
        else:
            self.error = _dataBaseUtil.ResErrorJson(u"更新数据失败:%s" % model)
  
    def roll_back(self):return self.error

    def GetUserName(self,userid):
        _oper = _dataBaseUtil.getDataBase("UserOperate","User")
        _model= _oper.get(id=userid)[-1][0]
        return _model
    def CheckSellNumber(self,modelOpt):
        rollback_number = modelOpt.get_roll_back_number(self.Model.id)
        if float(self.RequstForm.get("number")) < rollback_number:
            self.error = _dataBaseUtil.ResErrorJson(u"销售数量小于退货数量,请修正")

        if self.Model.customer_id != self.RequstForm.get("customer_id"):
            roll_back = self.Model.roll_backs.all()
            if roll_back:
                self.error = _dataBaseUtil.ResErrorJson(u"存在与该销售数据有关的退货信息,不可修改客户名称")

    def UpdateSell(self, modelOpt):
        # 因用户价格修改导致的更新
        self.CheckSellNumber(modelOpt)
        if self.error is not None:
            return self.error
        _ses = modelOpt.Session
        self.ModifyMoney(_ses, "sell", self.Model.id)
        if self.error is not None:
            return self.error
        data = self._updateBase(_ses,self.GetTrueStockState)
        if self.error is not None:
            return self.roll_back()
        else:
            return data
    
    def GetTrueStockState(self):
        stock = self.Model.stock
        if self.GetStockLevel() == 0:
            stock.isout = 1
        else:
            stock.isout = 0
        return stock
        
    def UpdateRoll(self,modelOpt):
        state, model = modelOpt.update_model(self.Model, self.RequstForm)
        if self.IsOk(state, model):
            modelOpt.ModelList = self.GetTrueStockState()
            state, models = modelOpt.update()
            if state and models:
                _data = modelOpt.get_data([model], True)[-1]
                return _dataBaseUtil.ResOkJson(_data)
            else:
                return _dataBaseUtil.ResErrorJson(u"修改内容失败:%s" % models)
        return _dataBaseUtil.ResErrorJson(u"修改内容失败")
    
    def GetStockLevel(self):
        stock = self.Model.stock
        stock_n = _getOper("stock").GetAbsTotal(stock.id)
        total = stock_n + self.Model.number
        level = total - float(self.RequstForm.get("number"))
        return level
    
    
    def UpdateSellAndRoll(self, modelOpt):
        """
        @attention: 修正销售和转出/报损的信息
        """
        
        level = self.GetStockLevel()
        if level < 0:
            return _dataBaseUtil.ResErrorJson(u"输入数量大于库存数量,请修正")
        if self.ProductionId == "sell":
            roll_back = _getOper("sell").get_roll_back_number(self.Model.id)
            if roll_back == self.Model.number and self.RequstForm.get("number") < self.Model.number:
                return _dataBaseUtil.ResErrorJson(u"输入的数量小于已经退货的数量,请修正")
            return self.UpdateSell(modelOpt)
        else:
            return self.UpdateRoll(modelOpt)
    
    def CheckeDataRBack(self,msg):
        stockDate = self.Model.sell.date.strftime("%Y-%m-%d")
        inputDate = self.RequstForm.get("date")
        if _dataBaseUtil.IsLessDate(inputDate,stockDate):
            return False,_dataBaseUtil.ResErrorJson(msg)
        else:
            return True,None

    def CheckeDataStock(self,msg):
        stockDate = self.Model.stock.date.strftime("%Y-%m-%d")
        inputDate = self.RequstForm.get("date")
        if _dataBaseUtil.IsLessDate(inputDate,stockDate):
            return False,_dataBaseUtil.ResErrorJson(msg)
        else:
            return True,None

    def UpateModel(self, requestForm):
        """
        @attention: 修改数据项,同时需要修正入库的标记
        """
        self.error = None
        self.RequstForm = requestForm
        self.RequstForm['number'] = int(self.RequstForm.get("number"))
        self.modelOpt = _getOper(self.ProductionId)

        if self.ProductionId in ["rollout", "rollloss", "sell"]:
            state,error =self.CheckeDataStock(u"选择的日期小于入库日期,请修正")
            if not state:
                return error
            else:
                return self.UpdateSellAndRoll(self.modelOpt)
        elif self.ProductionId == "rollback":
            state,error =self.CheckeDataRBack(u"选择的日期小于销售的日期,请修正")
            if not state:
                return error
            else:
                return self.UpdateRollBack(self.modelOpt)
        else:
            return self.UpateStockData(self.modelOpt)

_modifyCellUtil = ModifyCell()

        
