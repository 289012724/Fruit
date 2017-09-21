# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''

from flask import request, jsonify
from flask_login import current_user

from ...common import _dataBaseUtil    as dataUtil, _formOperateUtil as formUtil


_production = "Production"
_user       = "User"
_getOper    = dataUtil.GetPartial(_production)
_getForm    = formUtil.GetPartial(_production)
DateFormat  = '%Y-%m-%d'

class InitPage(object):
    def __init__(self):
        self.__formError = None
        self.a = 1
    @property
    def FormError(self):return self.__formError
                
    @FormError.setter
    def FormError(self,value):self.__formError = value

    def CheckFrom(self,form):
        self.FormError = None
        if form.is_submitted() or request.method.upper() == "POST":
            if form.validate_on_submit():
                return True
            self.FormError = form.errors
        return False
    
    def GetUserOption(self,userType):
        if userType.lower() == 'supporter':
            model = dataUtil.GetDataByUrl("SupportChoice", "User")()
        elif userType.lower()=='customer':
            model = dataUtil.GetDataByUrl("CustomerChoice", "User")()
        if model:
            _dict = [dict(zip(['id','text'],one)) for one in model]
        else:
            _dict = []
        return jsonify(_dict)
    
    def GetStockPage(self):
        """
        @attention: 获取入库页面
        """
        form = _getForm("StockForm")
        date = dataUtil.CurrentDateStr
        form.support_id.choices = dataUtil.GetDataByUrl("SupportChoice", "User")()
        if self.CheckFrom(form):
            return True,form,date
        return None,form,date
            
    def GetSellCount(self):
        """
        @attention: 获取可卖数量,以及销售的指导价格
        @note:  退过的货品也可以再销售
        """
        _stock= _getOper("stock")
        _sell = _getOper("sell")
        idx   = request.args.get('id')
        model = dataUtil.getModel(_stock,id=idx)
        _data = {}
        if model:
            model   = model[0]
            price   = model.price
            _data['stock_number'] = _stock.GetAbsTotal(idx)
            _data['stock_price']  = price
        return _data
    
    def GetStocks(self):
        """
        @attention: 获取当前正在销售的商品信息
        """
        _oper  = _getOper("stock")
        models = dataUtil.getModel(_oper,isout=0)
        if models:
            return _oper.get_data(models,True)[-1]
        return []
    
    def GetSellStock(self):
        stock_name_and_id = False
        return stock_name_and_id
    
    def GetMoneyPage(self):
        """
        @attention: 获取退货以及销售过程中的金钱交易数据
        """
        money     = _getForm("MoneyForm")
        money.price.data = 0
        return money
    
    def GetSellPage(self):
        form = _getForm("SellForm")
        date = dataUtil.CurrentDateStr
        money= self.GetMoneyPage()
        stock= self.GetSellStock()
        if self.CheckFrom(form):
            return True,form,money,date,stock
        return False,form,money,date,stock
    
    def GetRollOutPage(self):
        form = _getForm("RollOut")
        date = dataUtil.CurrentDateStr
        if self.CheckFrom(form):
            return True,form,date
        return False ,form,date
    
    def __GetBackSell(self,model):
        _roll_backs = []
        for _one in model:
            rolls = _one.roll_backs.all()
            total = sum([_r.number for _r in rolls] or [0])
            _roll_backs.append(total)
        data  = _getOper("sell").get_data(model,True)[-1]
        for ids,_one in enumerate(data):
            _one['number_back'] = _roll_backs[ids]
        return data
    
    def LoadBackSell(self,**kargs):
        _oper = _getOper("sell")
        model = _oper.get(**kargs)
        if model[0] and model[1]:
            _datas = self.__GetBackSell(model[1])
            return _datas
        return []
    
    def AddMoney(self,form,isplus=False):
        """
        @attention: 添加付款信息
        """
        money_id = form.money_id.data.split("@")
        _type    = money_id[0]
        _price   = float(("%s"%money_id[1]).strip("-"))
        if isplus:_price = - _price
        
        _ticket  = form.tickets.data
        _customer= form.customer_id.data
        date     = form.date.data
        if _price == 0:
            return 1
        else:
            _oper = _getOper("money")
            _oper.add_model(
                            money_type=_type,
                            tickets=_ticket,
                            price = _price,
                            user_id = _customer,
                            date=date
                            )
            state,model = _oper.add()
            if state and model:return model[0].id
            
    def _GetUserByName(self,username):
        """
        @attention: 通过名字获取ID编号
        """
        data = dataUtil.GetDataByUrl("UserByName","User")(username)
        if data:data = data[0]
        return data.get('id')
        
    def _GetUserById(self,userId):
        """
        @attention: 通过ID编号获取名字
        """
        data = dataUtil.GetDataByUrl("UserInfo","User")(userId)
        if data:data = data[0]
        return data.get('username')
     
    def GetRollBackPage(self):
        form = _getForm("RollBack")
        money= self.GetMoneyPage()
        money.money_type.label.text = u"退款类型"
        money.price.label.text      = u"退款金额"
        if self.CheckFrom(form):
            return True,form,money
        return False,form,money

_initPageUtil = InitPage()


    