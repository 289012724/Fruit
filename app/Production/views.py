# -*- coding:utf-8 -*-
"""
@version: triweb version 1.0
@author: shuiyaoyao
@contact: 289012724@qq.com
@software: PyCharm
@file: views.py
@time: 2016/7/11 0011
"""
from . import Production
from flask import render_template, jsonify, request
from ..common import json_return
from flask_login import current_user
from .services.InitPage import _initPageUtil
from .services.ModifyPage import _modifyPageUtil
from .services.DeleteModel import _deleteModelUtil
from .services.ModifyCell import _modifyCellUtil
from .services.Search import _searchUtil
from ..common.DataBaseOperate import _dataBaseUtil as _dataUtil
from ..Finance.services.BillService import _BillService

_getOperate = _dataUtil.GetPartial("Production")


def __add_model(form, operate, error=u"失败"):
    state, model = operate.add_model(form)
    if not (state and model):
        return _dataUtil.ResErrorJson(error)

    state, model = operate.add()
    if not (state and model):
        return _dataUtil.ResErrorJson(error)

    _data = operate.get_data(model, True)[-1]
    return _dataUtil.ResOkJson(_data)


@Production.route('/stock', methods=['GET', 'POST'])
def stock():
    state, form, date = _initPageUtil.get_stock_gage()
    if state:
        form.operator_id.data = current_user.id
        return __add_model(form, _getOperate("stock"), u"添加入库信息失败")

    if _initPageUtil.form_error is not None:
        return _dataUtil.ResErrorJson(_initPageUtil.form_error)

    form.operator_id.data = current_user.username
    return render_template('Production/stock.html', form=form, date=date)


# ===============================================================================
# 添加 销售，转出，报损和退货信息 都需要考虑更新入库的状态
# ===============================================================================
def get_storage(uid, over):
    storage = _getOperate("stock")
    state, model = storage.get(id=uid)
    if state and model:
        model = model[0]
        model.isout = over
        return model
    return None


def _delete_money(uid):
    operate = _getOperate("money")
    operate.delete_model(uid=uid)
    operate.delete()


def _adjust_bill(current_uer, current_date):
    return _BillService.update_all_by_total(current_uer, current_date, current_uer, current_date)


def _add_sell(form, stock_num):
    operate = _getOperate("sell")
    state, model = operate.add_model(form)

    if not (state and model):
        _delete_money(form.money_id.data)
        return _dataUtil.ResErrorJson(u"销售信息的数据格式不正确:%s" % model)

    storage = get_storage(model.stock_id, 0)
    if not storage:
        _delete_money(form.money_id.data)
        return _dataUtil.ResErrorJson(u"不存在选择的入库信息")

    if stock_num == model.number:
        storage.isout = 1

    operate.ModelList = storage
    state, models = operate.add()
    if not (state and models):
        _delete_money(form.money_id.data)
        return _dataUtil.ResErrorJson(u"添加销售信息失败%s" % models)

    if not _adjust_bill(model.customer_id, model.date.strftime("%Y-%m-%d")):
        return _dataUtil.ResErrorJson(_BillService.get_error())

    state, data = operate.get_data([model], True)
    return _dataUtil.ResOkJson(data)


def check_stock_date(stock_id, date):
    _stock = _getOperate("stock").get(id=stock_id)[-1][0]
    date1 = _stock.date.strftime("%Y-%m-%d")
    if _dataUtil.IsLessDate(date, date1):
        return True, _dataUtil.ResErrorJson(u"选择日期小于入库日期,请修正")
    return False, None


def translate_sell(form, stock_num):
    state, error = check_stock_date(form.stock_id.data, form.date.data)
    if state:
        return error

    money_id = _initPageUtil.add_money(form)
    if not money_id:
        return _dataUtil.ResErrorJson(u"添加销售信息失败-->添加销售的付款信息失败")

    form.money_id.data = money_id
    form.operator_id.data = current_user.id
    return _add_sell(form, stock_num)


@Production.route('/sell', methods=['GET', 'POST'])
def sell():
    state, form, money, date, stock_name_and_id = _initPageUtil.get_sell_page()
    if state:
        stock_id = form.stock_id.data
        stock_num = _getOperate("stock").GetAbsTotal(stock_id)
        if form.number.data > stock_num:
            return _dataUtil.ResErrorJson(u'输入的数量大于库存数量,请修正')
        return translate_sell(form, stock_num)

    if _initPageUtil.form_error is not None:
        return _dataUtil.ResErrorJson(form.errors)

    form.operator_id.data = current_user.username
    return render_template('Production/sell.html', form=form, money=money, date=date,
                           stock_name_and_id=stock_name_and_id)


@Production.route("/load_filter_sell_info", methods=['GET', "POST"])
def load_filter_sell_info():
    sell_id = request.form.get('sell_id')
    return jsonify(_searchUtil.LoadSellInfo(sell_id))


@Production.route("/load_filter_sells", methods=['GET', "POST"])
@json_return
def load_filter_sells():
    return _searchUtil.LoadFilterSell(**request.form.to_dict())


@Production.route("/load_back_sells", methods=['GET', "POST"])
@json_return
def load_back_sells():
    data = _searchUtil.load_back_sell(operator_id=current_user.id,
                                      customer_id=request.form.get("customer_id"),
                                      date=_dataUtil.CurrentDateStr)
    if data.get("state"):
        return data.get('msg')
    return []


def _roll_back_sell(form, operate, model):
    state, sell = _getOperate('sell').get(id=model.sell_id)
    if not (state and sell):
        _delete_money(model.money_id)
        return _dataUtil.ResError(u"不存在选择的销售信息")

    sell = sell[0]
    date1 = sell.date.strftime("%Y-%m-%d")
    date2 = form.date.data
    if _dataUtil.IsLessDate(date2, date1):
        return _dataUtil.ResError(u"退货日期小于销售日期,请修正")

    storage = sell.stock
    storage.isout = 0
    operate.ModelList = storage
    state, models = operate.add()
    if not (state and models):
        _delete_money(model.money_id)
        return _dataUtil.ResError(u"保存退款商品信息有误 %s" % models)

    if _adjust_bill(model.customer_id, model.date.strftime("%Y-%m-%d")):
        _data = operate.get_data([model], True)[-1]
        return _dataUtil.ResOk(_data)
    return _dataUtil.ResOk(_BillService.get_error())


def translate_roll_back(form):
    money_id = _initPageUtil.add_money(form, True)
    if not money_id:
        return _dataUtil.ResError(u"保存退货商品信息失败--->保存退款信息失败")

    form.operator_id.data = current_user.id
    form.money_id.data = money_id
    operate = _getOperate("rollback")
    state, model = operate.add_model(form)
    if state and model:
        return _roll_back_sell(form, operate, model)

    _delete_money(form.money_id.data)
    return _dataUtil.ResError(u"退款数据格式不正确")


@Production.route("/roll_back", methods=['GET', "POST"])
def roll_back():
    state, form, money = _initPageUtil.get_roll_back_page()
    if state:
        if form.number.data > _getOperate("sell").get_snap_number(form.sell_id.data):
            return _dataUtil.ResErrorJson(u'输入的数量大于可退的销售数量,请修正')
        return jsonify(translate_roll_back(form))

    if _initPageUtil.form_error is not None:
        return _dataUtil.ResErrorJson(_initPageUtil.form_error)

    form.operator_id.data = current_user.username
    return render_template("Production/roll_back.html", form=form, money=money,
                           date=_dataUtil.CurrentDateStr)


def translate_roll_out(form, stock_num):
    state, error = check_stock_date(form.stock_id.data, form.date.data)
    if state:
        return error

    operate = _getOperate("rollout")
    state, model = operate.add_model(form)
    if not (state and model):
        return _dataUtil.ResErrorJson(u"添加转出信息失败")

    storage = get_storage(model.stock_id, 0)
    if not storage:
        return _dataUtil.ResErrorJson(u"添加转出信息失败,入库数据不存在")

    if stock_num == model.number:
        storage.isout = 1

    operate.ModelList = storage
    state, models = operate.add()
    if state and models:
        state, data = operate.get_data([model], True)
        return _dataUtil.ResOkJson(data)
    return _dataUtil.ResErrorJson(u"更新入库信息失败")


@Production.route("/roll_out", methods=['GET', 'POST'])
def roll_out():
    state, form, date = _initPageUtil.get_roll_out_page()
    if state:
        form.operator_id.data = current_user.id
        stock_num = _getOperate("stock").GetAbsTotal(form.stock_id.data)
        if form.number.data > stock_num:
            return _dataUtil.ResErrorJson(u'输入的数量大于库存数量,请修正')
        return translate_roll_out(form, stock_num)

    if _initPageUtil.form_error is not None:
        return jsonify(form.errors)

    form.operator_id.data = current_user.username
    form.roll_type.data = u"转出"
    return render_template("Production/roll_out.html", form=form, date=date)


@Production.route("/roll_loss", methods=['GET', 'POST'])
def roll_loss():
    """
    @attention: 当前只负责将页面返回给客户端，具体的操作由 roll_out 执行
    """
    form, date = _initPageUtil.get_roll_out_page()[1:]
    form.operator_id.data = current_user.username
    form.roll_type.data = u"报损"
    form.reason.label.text = u"报损原因"
    return render_template("Production/roll_loss.html", form=form, date=date)


# ===============================================================================
# 修改相关数据
# ===============================================================================
def _get_modify_roll_out(uid, template_name):
    form, name_id, date = _modifyPageUtil.get_roll_out_page(uid)
    form.operator_id.data = current_user.username
    form.roll_type.data = u"转出"
    return render_template("Production/%s.html" % template_name, form=form, name_id=name_id, date=date)


# roll_back
def _get_modify_rollback(uid):
    form, money, date, name_id = _modifyPageUtil.get_roll_back_page(uid)
    form.operator_id.data = current_user.username
    return render_template("Production/roll_back.html", form=form, money=money, date=date, name_id=name_id)


# sell
def _get_modify_sell(uid):
    form, money, date, name_id = _modifyPageUtil.get_sell_page(uid)
    return render_template('Production/sell.html', form=form, money=money, date=date, name_id=name_id)


# stock
def _get_modify_stock(uid):
    form, date = _modifyPageUtil.get_stock_gage(uid)
    return render_template('Production/stock.html', form=form, date=date)


def _get_modify_data(operate_type, production_id):
    if operate_type == "stock":
        return _get_modify_stock(production_id)
    if operate_type == "sell":
        return _get_modify_sell(production_id)
    if operate_type == "rollback":
        return _get_modify_rollback(production_id)
    if operate_type in ["rollout"]:
        return _get_modify_roll_out(production_id, 'roll_out')
    if operate_type in ["rollloss"]:
        return _get_modify_roll_out(production_id, "roll_loss")


@Production.route('/modify/<operType>/<int:production_id>', methods=['GET', 'POST'])
def modify(operType, production_id):
    return _get_modify_data(operType, production_id)


@Production.route('/modify_cell', methods=['POST', 'GET'])
def modify_cell():
    form_data = request.form.to_dict()
    form_data["operator_id"] = current_user.id
    return _modifyCellUtil.update_model(form_data)


# ===============================================================================
# 删除相关的操作
# ===============================================================================
@Production.route("/delete_production/check_delete_state", methods=['GET', 'POST'])
@json_return
def delete_check_state():
    return _deleteModelUtil.check_state(request.form.get("operType"),
                                        request.form.get("productionId"))


@Production.route('/delete_production/<string:operType>', methods=['GET', 'POST'])
@json_return
def delete_production(operType):
    return _deleteModelUtil.delete_models(operType, request.form.get('production_id'))


# ===============================================================================
# 搜索相关的操作
# ===============================================================================
@Production.route("/search/<string:operType>", methods=['GET', 'POST'])
def search(operType):
    _id, data = _searchUtil.SearchModel(operType)
    if _id != 3:
        jsonify(data)

    data.operator_id.choices = [(current_user.id, current_user.username)]
    if current_user.username in ['admin', 'autitor']:
        choices = _dataUtil.GetDataByUrl("UserChocieAll", "User")()
        choices = [(str(c[0]), c[1]) for c in choices]
        choices.insert(0, ("", ""))
        data.operator_id.choices = choices

    return render_template("Production/search/%s.html" % operType, form=data, operType=operType)


# ===============================================================================
# 初始化的 datagrid 页面
# ===============================================================================
def get_oper_type_index(operType):
    return ["stock", "sell", "rollback", "rollout", "rollloss"].index(operType)


@Production.route('/load_datagrid/<string:operType>', methods=['GET', 'POST'])
def load_data_grid(operType):
    return render_template('Production/table_datagrid.html', operType=operType,
                           operTypeIndex=get_oper_type_index(operType))


# ===============================================================================
# restful 相关的操作 ， 对于有页面交互需求的 ，当前返回的不是 responese 的json
# 而是python 对象，因而用用页面来操作会有问题
# ===============================================================================
import view_infos
