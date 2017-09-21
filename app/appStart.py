# usr/bin/env
# -*- coding:utf-8 -*-
"""
@version: triweb version 1.0
@author: shuiyaoyao
@contact: 289012724@qq.com
@software: PyCharm
@file: __init__.py.py
"""
from . import app, basedir, database
import os
from flask import render_template, \
    url_for, request, redirect, jsonify
from flask_login import current_user


def filter_css_js():
    if "static" in request.url:
        return True


@app.before_request
def must_login():
    if not filter_css_js():
        if request.url == url_for('User.change_pass', _external=True) or \
                        request.url == url_for('User.login', _external=True):
            pass
        else:
            if not current_user.is_authenticated:
                return redirect(url_for('User.login'))


# @app.errorhandler(404)
def error_404(state):
    return render_template("error.html"), 404


# @app.errorhandler(500)
def error_500(state):
    return render_template("error.html"), 500


@app.route('/index')
def index():
    return render_template('index.html', current_user=current_user, date=_dataBaseUtil.CurrentDateStr)


@app.route('/data', methods=['GET', 'POST'])
def load_data():
    data = {'data': [['2016-01-02', 'hello', 'name']] * 100}
    return jsonify(data)


@app.route('/config')
def config():
    data = {"sProcessing": "处理中...",
            "sLengthMenu": "显示 _MENU_ 项结果",
            "sZeroRecords": "没有匹配结果",
            "sInfo": "显示第 _START_ 至 _END_ 项结果，共 _TOTAL_ 项",
            "sInfoEmpty": "显示第 0 至 0 项结果，共 0 项",
            "sInfoFiltered": "(由 _MAX_ 项结果过滤)",
            "sInfoPostFix": "",
            "sSearch": "搜索:",
            "sUrl": "",
            "sEmptyTable": "表中数据为空",
            "sLoadingRecords": "载入中...",
            "sInfoThousands": ",",
            "oPaginate": {
                "sFirst": "首页",
                "sPrevious": "上页",
                "sNext": "下页",
                "sLast": "末页"
            },
            "oAria": {
                "sSortAscending": ": 以升序排列此列",
                "sSortDescending": ": 以降序排列此列"
            }
            }
    return jsonify(data)


from common import _dataBaseUtil
