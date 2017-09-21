# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''
from flask import Blueprint

Bill = Blueprint("Bill",__name__,url_prefix="/Bill")

from . import views