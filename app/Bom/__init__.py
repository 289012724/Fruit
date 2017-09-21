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

Bom = Blueprint('Bom', __name__, url_prefix='/Bom')

from . import  forms,views