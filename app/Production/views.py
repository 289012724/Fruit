# -*- coding:utf-8 -*-
"""
@version: triweb version 1.0
@author: shuiyaoyao
@contact: 289012724@qq.com
@software: PyCharm
@file: views.py
@time: 2016/7/11 0011
"""
from .                          import Production
from flask                      import render_template, jsonify, request
from ..common                   import json_return
from flask_login                import current_user
from .services.InitPage         import _initPageUtil
from .services.ModifyPage       import _modifyPageUtil
from .services.DeleteModel      import _deleteModelUtil
from .services.ModifyCell       import _modifyCellUtil
from .services.Search           import _searchUtil
from ..common.DataBaseOperate   import _dataBaseUtil as _dataUtil
from ..Finance.services.BillService import _BillService

_getOper = _dataUtil.GetPartial("Production")

def __add_model(form, _oper, errorMsg=u"失败"):
    state, model = _oper.add_model(form)
    if state and model:
        state, model = _oper.add()
        if state and model:
            _data = _oper.get_data(model, True)[-1]
            return jsonify(_dataUtil.ResOk(_data))
    return  jsonify(_dataUtil.ResError(errorMsg))

@Production.route('/stock', methods=['GET', 'POST'])
def stock():
    state, form, date = _initPageUtil.GetStockPage()
    if state:
        form.operator_id.data = current_user.id
        _operate = _getOper("stock")
        return __add_model(form, _operate, u"添加入库信息失败")
    if _initPageUtil.FormError is not None:
        return jsonify(_dataUtil.ResError(_initPageUtil.FormError))
    form.operator_id.data = current_user.username
    return render_template('Production/stock.html', form=form, date=date)

#===============================================================================
# 添加 销售，转出，报损和退货信息 都需要考虑更新入库的状态
#===============================================================================
def GetStock(stockId, isOut):
    stock = _getOper("stock")
    state, model = stock.get(id=stockId)
    if state and model:
        model = model[0]
        model.isout = isOut
        return model
    else:
        print state, model, "获取入库信息失败"
        return None

def _delete_moeny(moeny_id):
    if moeny_id != 1:
        _oper = _getOper("money")
        _oper.delete_model(id=moeny_id)
        _oper.delete()
    
def _adjust_bill(cuer, cdate):
    return _BillService.UpdateAllByTotal(cuer, cdate, cuer, cdate)

def _add_sell(form, stock_num):
    _oper = _getOper("sell")
    state, model = _oper.add_model(form)
    if state and model:
        if stock_num == model.number:isout = 1
        else:isout = 0 
        stock = GetStock(model.stock_id, isout)
        if not stock:
            _delete_moeny(model.money_id)
            return _dataUtil.ResErrorJson(u"不存在选择的入库信息")
        _oper.ModelList = stock
        state, models = _oper.add()
        if state and models:
            cuer = model.customer_id
            cdate = model.date.strftime("%Y-%m-%d")
            if _adjust_bill(cuer, cdate):
                state, data = _oper.get_data([model], True)
                return _dataUtil.ResOkJson(data)
            else:
                return _dataUtil.ResErrorJson(_BillService.GetError())
        else:
            _delete_moeny(model.money_id)
            _dataUtil.ResErrorJson(u"添加销售信息失败%s"%models)
    else:
        _delete_moeny(model.money_id)
        return _dataUtil.ResErrorJson(u"销售信息的数据格式不正确:%s"%model)
    
def CheckStockDate(stock_id,date):
    _stock = _getOper("stock").get(id=stock_id)[-1][0]
    date1 = _stock.date.strftime("%Y-%m-%d")
    if _dataUtil.IsLessDate(date,date1):
        return True,_dataUtil.ResErrorJson(u"选择日期小于入库日期,请修正")
    return False,None

def TranslateSell(form,stock_num):
    state,error = CheckStockDate(form.stock_id.data, form.date.data)
    if state:return error
    money_id = _initPageUtil.AddMoney(form)
    if money_id:
        form.money_id.data = money_id
        form.operator_id.data = current_user.id
        return _add_sell(form,stock_num)
    return _dataUtil.ResErrorJson(u"添加销售信息失败-->添加销售的付款信息失败")
    
@Production.route('/sell', methods=['GET', 'POST'])
def sell():
    state, form, money, date, stock_name_and_id = _initPageUtil.GetSellPage()
    if state:
        stock_id = form.stock_id.data
        stock_num = _getOper("stock").GetAbsTotal(stock_id)
        if form.number.data > stock_num:
            return _dataUtil.ResErrorJson(u'输入的数量大于库存数量,请修正')
        else:
            return TranslateSell(form, stock_num)
    if _initPageUtil.FormError is not None:
        return jsonify(_dataUtil.ResError(form.errors))
    form.operator_id.data = current_user.username
    return render_template('Production/sell.html', form=form, money=money, date=date, stock_name_and_id=stock_name_and_id)

@Production.route("/load_filter_sell_info", methods=['GET', "POST"])
def load_filter_sell_info():
    sell_id = request.form.get('sell_id')
    return jsonify(_searchUtil.LoadSellInfo(sell_id))

@Production.route("/load_filter_sells", methods=['GET', "POST"])
def load_filter_sells():
    kwargs = request.form.to_dict()
    data = _searchUtil.LoadFilterSell(**kwargs)
    return jsonify(data)

@Production.route("/load_back_sells", methods=['GET', "POST"])
def load_back_sells():
    data = _searchUtil.LoadBackSell(operator_id=current_user.id, customer_id=request.form.get("customer_id"),
                                      date=_dataUtil.CurrentDateStr)
    if data.get("state"):
        return jsonify(data.get('msg'))
    return jsonify([])




def _roll_back_sell(form,_oper,model):
    state,sell = _getOper('sell').get(id=model.sell_id)
    if state and sell:sell = sell[0]
    else:
        _delete_moeny(model.money_id)
        return _dataUtil.ResError(u"不存在选择的销售信息")
    
    date1 = sell.date.strftime("%Y-%m-%d")
    date2 = form.date.data
    if _dataUtil.IsLessDate(date2,date1):
        return _dataUtil.ResError(u"退货日期小于销售日期,请修正")
    
    stock = sell.stock
    stock.isout = 0
    _oper.ModelList = stock
    state, models = _oper.add()
    if state and models:
        cuer = model.customer_id
        cdate = model.date.strftime("%Y-%m-%d")
        if _adjust_bill(cuer, cdate):
            _data = _oper.get_data([model], True)[-1]
            return _dataUtil.ResOk(_data)
        else:
            return _dataUtil.ResOk(_BillService.GetError())
    else:
        _delete_moeny(model.money_id)
        return _dataUtil.ResError(u"保存退款商品信息有误 %s"%models)
        
def TranslateRollBack(form):
    money_id = _initPageUtil.AddMoney(form, True)
    if money_id:
        form.operator_id.data = current_user.id
        form.money_id.data = money_id
        _oper = _getOper("rollback")
        state, model = _oper.add_model(form)
        if state and model:
            return _roll_back_sell(form,_oper,model)
        else:
            _delete_moeny(model.money_id)
            return _dataUtil.ResError(u"退款新数据格式不正确")
    return _dataUtil.ResError(u"保存退货商品信息失败--->保存退款信息失败")

@Production.route("/roll_back", methods=['GET', "POST"])
def roll_back():
    state, form , money = _initPageUtil.GetRollBackPage()
    if state:
        sell_id = form.sell_id.data
        _sell_num = _getOper("sell").get_snap_number(sell_id) 
        if form.number.data > _sell_num:
            return jsonify(_dataUtil.ResErrorJson(u'输入的数量大于可退的销售数量,请修正'))
        else:
            return jsonify(TranslateRollBack(form))
    if _initPageUtil.FormError is not None:
        return jsonify(_dataUtil.ResError(_initPageUtil.FormError))
    form.operator_id.data = current_user.username
    return render_template("Production/roll_back.html", form=form, money=money, date=_dataUtil.CurrentDateStr)

def TranslateRollOut(form, stock_num):
    state,error = CheckStockDate(form.stock_id.data, form.date.data)
    if state :return error
    _oper = _getOper("rollout")
    state, model = _oper.add_model(form)
    if state and model:
        if stock_num == model.number:isout = 1
        else:isout = 0 
        stock = GetStock(model.stock_id, isout)
        if stock:
            _oper.ModelList = stock
            state, models = _oper.add()
            if state and models:
                state, data = _oper.get_data([model], True)
                return _dataUtil.ResOkJson(data)
            else:
                print models
    return _dataUtil.ResErrorJson(u"添加转出信息失败")

@Production.route("/roll_out", methods=['GET', 'POST'])
def roll_out():
    state, form, date = _initPageUtil.GetRollOutPage()
    if state:
        form.operator_id.data = current_user.id
        stock_num = _getOper("stock").GetAbsTotal(form.stock_id.data)
        if form.number.data > stock_num:
            return _dataUtil.ResErrorJson(u'输入的数量大于库存数量,请修正')
        else:
            return TranslateRollOut(form, stock_num)
    if _initPageUtil.FormError is not None:
        return jsonify(form.errors)
    form.operator_id.data = current_user.username
    form.roll_type.data = u"转出"
    return render_template("Production/roll_out.html", form=form, date=date)

@Production.route("/roll_loss", methods=['GET', 'POST'])
def roll_loss():
    """
    @attention: 当前只负责将页面返回给客户端，具体的操作由 roll_out 执行
    """
    form, date = _initPageUtil.GetRollOutPage()[1:]
    form.operator_id.data = current_user.username
    form.roll_type.data = u"报损"
    form.reason.label.text = u"报损原因"
    return render_template("Production/roll_loss.html", form=form, date=date)

#===============================================================================
# 修改相关数据
#===============================================================================
def _get_modify_rollout(productionId, templateName):
    form, name_id, date = _modifyPageUtil.GetRollOutPage(productionId)
    form.operator_id.data = current_user.username
    form.roll_type.data = u"转出"
    return render_template("Production/%s.html" % templateName, form=form, name_id=name_id, date=date)

# roll_back
def _get_modify_rollback(productionId):
    form, money, date, name_id = _modifyPageUtil.GetRollBackPage(productionId)
    form.operator_id.data = current_user.username
    return render_template("Production/roll_back.html", form=form, money=money, date=date, name_id=name_id)

# sell
def _get_modify_sell(productionId):
    form, money, date, name_id = _modifyPageUtil.GetSellPage(productionId)
    return render_template('Production/sell.html', form=form, money=money, date=date, name_id=name_id)

# stock
def _get_modify_stock(productionId):
    form, date = _modifyPageUtil.GetStockPage(productionId)
    return render_template('Production/stock.html', form=form, date=date)


def _get_modify_data(operType, production_id):
    if operType == "stock":
        return _get_modify_stock(production_id)
    if operType == "sell":
        return _get_modify_sell(production_id)
    if operType == "rollback":
        return _get_modify_rollback(production_id)
    if operType in ["rollout"]:
        return _get_modify_rollout(production_id, 'roll_out')
    if operType in ["rollloss"]:
        return _get_modify_rollout(production_id, "roll_loss")


@Production.route('/modify/<string:operType>/<int:production_id>', methods=['GET', 'POST'])
def modify(operType, production_id):
    _data = _get_modify_data(operType, production_id)
    return _data

@Production.route('/modify_cell', methods=['POST', 'GET'])
def modify_cell():
    _datas = request.form.to_dict()
    _datas["operator_id"] = current_user.id
    data = _modifyCellUtil.UpateModel(_datas)
    return data

#===============================================================================
# 删除相关的操作
#===============================================================================
@Production.route("/delete_production/check_delete_state", methods=['GET', 'POST'])
@json_return
def delete_check_state():
    operType = request.form.get("operType")
    productionId = request.form.get("productionId")
    state = _deleteModelUtil.CheckState(operType, productionId)
    return state

@Production.route('/delete_production/<string:operType>', methods=['GET', 'POST'])
@json_return
def delete_production(operType):
    goodsId = request.form.get('production_id')
    state = _deleteModelUtil.DeleteModels(operType, goodsId)
    return state

#===============================================================================
# 搜索相关的操作
#===============================================================================
@Production.route("/search/<string:operType>", methods=['GET', 'POST'])
def search(operType):
    _id, data = _searchUtil.SearchModel(operType)
    if _id == 3:
        if current_user.username in ['admin', 'autitor']:
            choices = _dataUtil.GetDataByUrl("UserChocieAll", "User")()
            choices = [(str(c[0]), c[1]) for c in choices]
            choices.insert(0, ("", ""))
            data.operator_id.choices = choices
        else:
            data.operator_id.choices = [(current_user.id, current_user.username)]
        return render_template("Production/search/%s.html" % operType, form=data, operType=operType)
    else:
        return jsonify(data)

#===============================================================================
# 初始化的 datagrid 页面
#===============================================================================
def get_operTypeIndex(operType):
    return ["stock", "sell", "rollback", "rollout", "rollloss"].index(operType)
    
@Production.route('/load_datagrid/<string:operType>', methods=['GET', 'POST'])
def load_datagrid(operType):
    operateIndex = get_operTypeIndex(operType)
    return render_template('Production/table_datagrid.html', operType=operType, operTypeIndex=operateIndex)

#===============================================================================
# restful 相关的操作 ， 对于有页面交互需求的 ，当前返回的不是 responese 的json
# 而是python 对象，因而用用页面来操作会有问题
#===============================================================================
import view_infos

