# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''

from . import Bom
from flask import render_template, jsonify
from .services.Search import _searchUtil
from .page_config import page_table_configs
from ..common import _dataBaseUtil    as dataUtil


@Bom.route("/search/<string:operType>", methods=['GET', 'POST'])
def search(operType):
    data = _searchUtil.Main(operType)
    return jsonify(data)


@Bom.route("/load_all/<string:operType>", methods=['GET', 'POST'])
def load_all(operType):
    data = _searchUtil.LoadInitData(operType)
    return jsonify(data)


@Bom.route("/table_config/<string:operType>", methods=['GET', 'POST'])
def table_config(operType):
    table = page_table_configs.get(operType.lower())
    return jsonify(table)


@Bom.route('/load_datagrid/<string:operType>', methods=['GET', 'POST'])
def load_datagrid(operType):
    return render_template('/Bom/table_datagrid.html', operType=operType, date=dataUtil.CurrentDateStr)


@Bom.route("/download", methods=['GET', 'POST'])
def down_load():
    return _searchUtil.DwonLoad()


@Bom.route("/download_ok/<string:operType>/<string:name>", methods=['GET', 'POST'])
def down_load_ok(operType, name):
    return _searchUtil.DwonOk(operType, name)


@Bom.route("/download_delete/<string:fileName>", methods=['GET', 'POST'])
def down_load_delete(fileName):
    return _searchUtil.DeletFile(fileName)
