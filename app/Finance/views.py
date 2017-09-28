# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''

from . import Finance
from flask import render_template, jsonify, request
from flask_login import current_user
from .services.InitPage import _initPageUtil


@Finance.route("/rebund", methods=['POST', 'GET'])
def rebund():
    state, data, date = _initPageUtil.GetRebund()
    if state: return jsonify(data)
    data.operator_id.data = current_user.username
    return render_template("Finance/rebund.html", form=data, date=date, operType="rebund")


@Finance.route("/writeoff", methods=['POST', 'GET'])
def writeoff():
    state, data, date = _initPageUtil.GetRebate("writeoff")
    if state: return jsonify(data)
    data.operator_id.data = current_user.username
    return render_template("Finance/rebate.html", form=data, date=date, operType="writeoff")


@Finance.route("/rebate", methods=['POST', 'GET'])
def rebate():
    state, data, date = _initPageUtil.GetRebate("rebate")
    if state: return jsonify(data)
    data.operator_id.data = current_user.username
    return render_template("Finance/rebate.html", form=data, date=date, operType="rebate")


@Finance.route("/modify/<string:operType>/<int:dataId>", methods=['POST', 'GET'])
def modify(operType, dataId):
    state, data, date = _initPageUtil.Modify(operType, dataId)
    if state:
        return jsonify(data)
    if operType != "writeoff":
        temp = "Finance/%s.html" % (operType)
    else:
        temp = "Finance/rebate.html"
    return render_template(temp, form=data, date=date, operType=operType)


@Finance.route("/delete_data", methods=['POST', 'GET'])
def delete_data():
    data = request.form.to_dict()
    return jsonify(_initPageUtil.DeleteCell(data))


@Finance.route("/search/<string:operType>", methods=['POST', 'GET'])
def search(operType):
    state, form = _initPageUtil.Search(operType)
    if state:
        return jsonify(form)
    return render_template("Finance/search.html", form=form, operType=operType)


import view_info
