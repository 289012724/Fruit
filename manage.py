# -*- coding:utf-8 -*-
# usr/bin/env
"""
@version: triweb version 1.0
@author: shuiyaoyao
@contact: 289012724@qq.com
@software: PyCharm
@file: manage.py.py
@time: 2016/7/6 0006
"""
from app import app, database
from app.User.models import department, user
from flask_script import Manager, Shell
from app.User.modelOperates import UserOperate, DepartmentOperate

# def make_shell_context():
#     return dict(app=app, db=database, User=user, Role=department, operate=UserOperate(),
#                 depart=DepartmentOperate())
#
#
# manager = Manager(app)
# manager.add_command('shell', Shell(make_context=make_shell_context))

# if __name__ == '__main__':
app.run(host="0.0.0.0", port=5000)
