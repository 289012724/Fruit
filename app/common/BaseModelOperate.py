# usr/bin/env
# -*- coding:utf-8 -*-
"""
@version: triweb version 1.0
@author: shuiyaoyao
@contact: 289012724@qq.com
@software: PyCharm
@file: BaseModelOperate.py
@time: 2016/7/11 0011
"""
from .. import database
from ._annotation import exception_show_class, get_parameters


class BaseOperate(object):
    def __init__(self):
        object.__init__(self)
        self.__column_name = []
        self.__modelList = []
        self.__model = None

    def init_modelList(self):
        """
        @attention: database base operate set init model list to []
        """
        self.__modelList = []

    @property
    def Column(self):
        """
        @attention: use to get the model column name
        @return:  column name not contain id
        """
        return self.__column_name

    @Column.setter
    def Column(self, value):
        """
        @attention: use to set the model column name
        @param  value: column name list 
        """
        self.__column_name = value

    @property
    def ModelList(self):
        """
        @attention: use to get the set model list object
        @return: model list
        """
        return self.__modelList

    @ModelList.setter
    def ModelList(self, value):
        """
        @attention: use to append the model to modellist
        """
        if not isinstance(value, list): value = [value]
        self.ModelList.extend(value)

    @property
    def Model(self):
        """
        @attention:  use to get the model object
        """
        return self.__model

    @Model.setter
    def Model(self, value):
        """
        @attention: use to set the model model
        """
        self.__model = value

    @exception_show_class
    @get_parameters
    def add_model(self, *args, **kwargs):
        """
        @attention:  set the model information and append to model list
        @param *args:  *args
        @param **kwargs: **kwargs
        @return: append last model
        """
        self.ModelList = self.Model()
        model = self.ModelList[-1]
        [setattr(model, column, value) for column, value in zip(self.Column, args)]
        return True, model

    @exception_show_class
    def add(self):
        """
        @attention:  excute the session add function and commit
        @return: ModelList 
        """
        _model = self.ModelList[:]
        database.session.add_all(_model)
        self.init_modelList()
        database.session.commit()
        return True, _model

    @get_parameters
    def _get_parameters(self, *arg, **kwargs):
        return tuple(arg)

    @exception_show_class
    def update_model(self, model, *arg, **kwargs):
        arg = self._get_parameters(*tuple(arg), **kwargs)
        model.Init(arg)
        self.ModelList = model
        return True, self.ModelList[-1]

    def update(self):
        """
        @attention:  excute session update function
        """
        return self.add()

    @exception_show_class
    def delete_model(self, id):
        """
        @attention:  use to set delete model and append to the model list
        """
        self.ModelList = self.Model.query.filter_by(id=id).first()
        return True, self.ModelList[-1]

    @exception_show_class
    def delete(self):
        """
        @attention:  execute session delete operate
        """
        _model = self.ModelList[:]
        [database.session.delete(model) for model in _model]
        self.init_modelList()
        database.session.commit()
        return True, _model

    @property
    def Session(self):
        return database.session

    @exception_show_class
    def get(self, **kwargs):
        """
        @attention:  get use input filter data
        @param **kwargs: filter information dict 
        """
        query = self.Model.query
        for key, value in kwargs.items():
            eval_string = "query.filter_by(%s='%s')" % (key, value)
            query = eval(eval_string)
        return True, query.all()

    def _get_row_data(self, is_dict, _row):
        if is_dict:
            _row = dict(_row)
        else:
            _row = [cell[1] for cell in _row]
        return _row

    def _get_row(self, model, _key):
        return [(key, getattr(model, key)) for key in _key]

    @exception_show_class
    def get_data(self, models, is_dict=False):
        if models:
            _key, _data = ['id'] + self.Column, []
            for model in models:
                _row = self._get_row(model, _key)
                _row = self._get_row_data(is_dict, _row)
                _data.append(_row)
            return True, _data
        return True, []
