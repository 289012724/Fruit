# usr/bin/env
# -*- coding:utf-8 -*-
"""
@version: triweb version 1.0
@author: shuiyaoyao
@contact: 289012724@qq.com
@software: PyCharm
@file: __init__.py.py
@time: 2016/7/4 0004 下午 10:55
"""
from flask import Blueprint
User = Blueprint('User', __name__, url_prefix='/User')
from . import modelOperates
from . import models
from . import views
from . import forms


