# usr/bin/env
# -*- coding:utf-8 -*-
"""
@version: triweb version 1.0
@author: shuiyaoyao
@contact: 289012724@qq.com
@software: PyCharm
@file: __init__.py.py
"""
import os
from flask import Flask
from config import config
from simplemongo.Database import Database
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

database = Database()
bootstrap = Bootstrap()
load_manager = LoginManager()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    bootstrap.init_app(app)
    database.init_app(app)
    database.init_app(app)
    load_manager.init_app(app)
    load_manager.login_view = 'User.login'
    from .User import User        as User_blueprint
    # from .Production import Production  as Pro_blueprint
    # from .Finance import Finance     as Finance_blueprint
    # from .Bom import Bom         as Bom_blueprint
    # from .Bill import Bill        as Bill_blueprint
    app.register_blueprint(User_blueprint)
    # app.register_blueprint(Pro_blueprint)
    # app.register_blueprint(Finance_blueprint)
    # app.register_blueprint(Bom_blueprint)
    # app.register_blueprint(Bill_blueprint)
    database.default_init()
    return app


basedir = os.path.abspath(os.path.dirname(__file__))
# from .common import GetLincece
#
# state, _str = GetLincece(basedir)
# if state:
app = create_app('development')
app.config["DOWNLOAD_FILE"] = basedir + "/static/Download"
import appStart
# else:
#     print _str
