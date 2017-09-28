# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''

from BaseModelOperate import BaseOperate
from Response import Response

_res = Response()


class BaseModelOperateNew(BaseOperate):
    """
    @attention: 用于包装旧的 BaseModelOperate 类型
    在返回类型中加入类 自动转json的实现,当在系统内部使用的时候还是 对象
    ,在输入到浏览器的过程中自动将数据转为json格式
    """

    def __new_res(self, state, model):
        if state:
            _obj = _res.ResOk(model)
        else:
            _obj = _res.ResErr(model)

    def add(self):
        state, model = BaseOperate.add(self)
        return self.__new_res(state, model)

    def add_model(self, *args, **kwargs):
        state, model = BaseOperate.add_model(self, *args, **kwargs)
        return self.__new_res(state, model)

    def update_model(self, model, *arg, **kwargs):
        state, model = BaseOperate.update_model(self, model, *arg, **kwargs)
        return self.__new_res(state, model)

    def update(self):
        state, model = BaseOperate.update(self)
        return self.__new_res(state, model)

    def delete_model(self, ids):
        state, model = BaseOperate.delete_model(self, ids)
        return self.__new_res(state, model)

    def delete(self):
        state, model = BaseOperate.delete(self)
        return self.__new_res(state, model)

    def get(self, **kwargs):
        state, model = BaseOperate.get(self, **kwargs)
        return self.__new_res(state, model)

    def get_data(self, models, is_dict=False):
        state, model = BaseOperate.get_data(self, models, is_dict)
        return self.__new_res(state, model)
