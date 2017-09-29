# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''

from . import Bill
from flask import render_template, jsonify
from .services.Search import _searchUtil
from .page_config import page_table_configs
from ..common import _dataBaseUtil    as dataUtil


@Bill.route("/search/<string:operType>", methods=['GET', 'POST'])
def search(operType):
    data = _searchUtil.main(operType)
    return jsonify(data)


@Bill.route("/load_all/<string:operType>", methods=['GET', 'POST'])
def load_all(operType):
    data = _searchUtil.load_all(operType)
    return jsonify(data)


@Bill.route("/table_config/<string:operType>", methods=['GET', 'POST'])
def table_config(operType):
    table = page_table_configs.get(operType.lower())
    return jsonify(table)


@Bill.route('/load_datagrid/<string:operType>', methods=['GET', 'POST'])
def load_datagrid(operType):
    return render_template('/Bill/table_datagrid.html', operType=operType, date=dataUtil.CurrentDateStr)


@Bill.route("/user_option/<string:operType>", methods=['GET', 'POST'])
def user_option(operType):
    if operType == 'cstbill':
        model = dataUtil.GetDataByUrl("CustomerChoice", "User")()
    if operType == "sptbill":
        model = dataUtil.GetDataByUrl("SupportChoice", "User")()
    _dict = [dict(zip(['id', 'text'], one)) for one in model]
    return jsonify(_dict)


@Bill.route("/download", methods=['GET', 'POST'])
def down_load():
    return _searchUtil.download()


@Bill.route("/download_ok/<string:operType>/<string:name>/<string:dwname>", methods=['GET', 'POST'])
def down_load_ok(operType, name, dwname):
    return _searchUtil.down_ok(operType, name, dwname)


@Bill.route("/download_delete/<string:fileName>", methods=['GET', 'POST'])
def down_load_delete(fileName):
    return _searchUtil.delete_file(fileName)


@Bill.route("/prev_date", methods=['GET', 'POST'])
def get_last_date():
    return _searchUtil.get_last_date()


@Bill.route("/has_bill", methods=['GET', 'POST'])
def check_has_bill():
    return _searchUtil.has_bill()


@Bill.route("/bill_manager")
def bill_manager():
    date = dataUtil.CurrentDateStr.split("-")
    date[-1] = "01"
    date = "-".join(date)
    return render_template("Bill/manager.html", operType="bill_manager", date=date)


@Bill.route("/get_bills", methods=['GET', 'POST'])
def get_bills():
    return _searchUtil.get_bills()


@Bill.route("/delete_bill", methods=['POST'])
def delete_bill():
    return _searchUtil.delete_bill_manager()


@Bill.route("/calculate_bill", methods=['POST'])
def calculate_bill():
    return _searchUtil.calculate_bill()
