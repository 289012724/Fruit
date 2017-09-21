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
from bson.objectid import ObjectId


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
        print(args, kwargs)
        self.ModelList = self.Model.Init(**kwargs)
        return True, self.ModelList[-1]

    @exception_show_class
    def add(self):
        """
        @attention:  excute the session add function and commit
        @return: ModelList 
        """
        _model = self.ModelList[:]
        for _cell in self.ModelList:
            _cell.save()
        self.init_modelList()
        return True, _model

    @get_parameters
    def _get_parameters(self, *arg, **kwargs):
        return tuple(arg)

    @exception_show_class
    def update_model(self, model, *arg, **kwargs):
        model.Init(kwargs)
        self.ModelList = model
        return True, self.ModelList[-1]

    def update(self):
        """
        @attention:  excute session update function
        """
        for _cell in self.ModelList:
            _cell.update()
        _model = self.ModelList[:]
        self.init_modelList()
        return True, _model

    @exception_show_class
    def delete_model(self, _id):
        """
        @attention:  use to set delete model and append to the model list
        """
        self.ModelList = _id
        return self.get(_id=_id)

    @exception_show_class
    def delete(self):
        """
        @attention:  execute session delete operate
        """
        for _id in self.ModelList:
            model = self.Model({"_id": ObjectId(_id)}, True)
            model.remove()
        self.init_modelList()
        return True, []

    @property
    def Session(self):
        return database.session

    def get(self, **kwargs):
        """
        @attention:  get use input filter data
        @param **kwargs: filter information dict 
        """
        if kwargs.has_key("_id"):
            try:
                kwargs["_id"] = ObjectId(kwargs["_id"])
            except:
                pass
        query = self.Model.find(kwargs)
        return query.count() != 0, [cell for cell in query]

    @exception_show_class
    def get_data(self, models, is_dict=False):
        if models:
            return True, models
        return True, []
