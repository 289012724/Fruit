# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''

from .                          import Finance
from flask                      import render_template, jsonify, request
from flask_login                import current_user
from .services.InitPage         import _initPageUtil
from ..common                   import json_return
import page_config


def get_operTypeIndex(operType):
    return["rebund",'writeoff','rebate'].index(operType)
    
@Finance.route('/load_datagrid/<string:operType>', methods=['GET', 'POST'])
def load_datagrid(operType):
    operateIndex = get_operTypeIndex(operType)
    return render_template('Finance/table_datagrid.html', operType=operType,operTypeIndex = operateIndex)


@Finance.route("/load_all/<string:operType>",methods=['POST','GET'])
@json_return
def load_all(operType):
    data = _initPageUtil.GetAllData(operType)
    return data

@Finance.route("/table_config/<string:operType>",methods=['POST','GET'])
@json_return
def table_config(operType):
    return page_config.page_table_configs.get(operType)


@Finance.route("/get_bill_choices/<string:username>",methods=['POST','GET'])
@json_return
def get_bill_choices(username):
    return _initPageUtil.GetBillChoices(username)

@Finance.route("/get_customer_choices/",methods=['POST','GET'])
@json_return
def get_customer_choices():
    return _initPageUtil.GetCustomerChoices()
    
