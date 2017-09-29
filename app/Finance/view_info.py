# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''

from . import Finance
from flask import render_template, jsonify, request
from flask_login import current_user
from .services.InitPage import _initPageUtil
from ..common import json_return
import page_config


def get_operate_type_index(operType):
    return ["rebund", 'writeoff', 'rebate'].index(operType)


@Finance.route('/load_datagrid/<string:operType>', methods=['GET', 'POST'])
def load_data_grid(operType):
    return render_template('Finance/table_datagrid.html', operType=operType, operTypeIndex=get_operate_type_index(operType))


@Finance.route("/load_all/<string:operType>", methods=['POST', 'GET'])
@json_return
def load_all(operType):
    return _initPageUtil.get_all_data(operType)


@Finance.route("/table_config/<string:operType>", methods=['POST', 'GET'])
@json_return
def table_config(operType):
    return page_config.page_table_configs.get(operType)


@Finance.route("/get_bill_choices/<string:username>", methods=['POST', 'GET'])
@json_return
def get_bill_choices(username):
    return _initPageUtil.get_bill_choices(username)


@Finance.route("/get_customer_choices/", methods=['POST', 'GET'])
@json_return
def get_customer_choices():
    return _initPageUtil.get_customer_choices()
