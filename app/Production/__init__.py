# usr/bin/env
# -*- coding:utf-8 -*-
"""
@version: triweb version 1.0
@author: shuiyaoyao
@contact: 289012724@qq.com
@software: PyCharm
@file: __init__.py.py
@time: 2016/7/11 0011
"""
from flask import Blueprint

Production = Blueprint('Production', __name__, url_prefix='/Production')

from . import  modelOperates,forms, models, views
