# usr/bin/env
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
from ..common._annotation import json_return
from .services.InitPage import _initPageUtil
from .services.DeleteModel import _deleteModelUtil
from .services.Search import _searchUtil
from ..common import _dataBaseUtil
import page_config
from flask import request
from services.UpLoadDataBase import UpLoadDataBase


@Production.route('/load_all_production/<string:operType>', methods=['GET', 'POST'])
@json_return
def load_all_production(operType):
    """
    @attention: 加载当前类型相关的商品信息
    @param operType: 商品的类型 
    """
    return _searchUtil.LoadAllProduction(operType)


@Production.route("/roll_back_sell_column", methods=['GET', "POST"])
@json_return
def roll_back_sell_column():
    """
    @attention: 获取在退货界面中的销售商品显示列内容
    """
    return page_config.roll_back_sell_column


@Production.route('/get_stock_columns')
@json_return
def get_stock_columns():
    """
    @attention: 获取在销售和转出,报损界面中显示的入库商品信息列
    """
    return page_config.page_table_configs["stock_column"]


@Production.route('/table_config/<string:operType>')
@json_return
def table_config(operType):
    """
    @attention: 根据传入的类型获得在界面中显示的单元格内容
    @param operType: 商品的类型
    """
    return page_config.page_table_configs[operType]


@Production.route('/Production/get_count_price')
@json_return
def get_count_price():
    """
    @attention: 获取当前商品入库时的价格以及可操作的数量
    """
    return _initPageUtil.GetSellCount()


@Production.route("/get_stock", methods=['GET', 'POST'])
@json_return
def get_stock():
    """
    @attention: 获取可以操作的所有商品信息
    """
    return _initPageUtil.GetStocks()


@Production.route("/check_delete_user/<string:roleType>/<int:userId>/")
def check_delete_user(roleType, userId):
    """
    @attention: 检测传入的用户是否可以删去,对于不可以删除的用户，当前只能设置用户的状态
    @param roleType: 传入的用户类型 。 用户 或则 部门
    @param userId: 用户id号  
    """
    data = _deleteModelUtil.CheckDeleteUser(userId, roleType)
    if data: return True


@Production.route("/customer_choices", methods=['POST', 'GET'])
@json_return
def sell_customer_id():
    data = _dataBaseUtil.GetDataByUrl("CustomerChoice", "User")()
    data = [{'id': _c[0], 'username': _c[1]} for _c in data]
    return data


@Production.route("/user_option_choice/<string:userType>", methods=['POST', 'GET'])
def user_option_choice(userType):
    return _initPageUtil.GetUserOption(userType)


@Production.route("/upload_file", methods=['POST', 'GET'])
def upload_file():
    return UpLoadDataBase().importData()


@Production.route("/export_file", methods=['POST', 'GET'])
def export_file():
    is_ok = UpLoadDataBase().dumpData()
    return is_ok


@Production.route("/export_ok_file", methods=['POST', 'GET'])
def export_ok_file():
    is_ok = UpLoadDataBase().downLoad()
    return is_ok


@Production.route("/delete_down_ok", methods=['POST', 'GET'])
def delete_down_ok():
    UpLoadDataBase().delete_down_ok_file()
    return "ok"
