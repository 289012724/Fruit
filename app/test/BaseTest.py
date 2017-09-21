# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''
import sys
import os

from flask                  import *
from ..config               import config
from flask_sqlalchemy       import SQLAlchemy

database     = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    database.init_app(app)
    return app

app     = create_app('development')

    
        