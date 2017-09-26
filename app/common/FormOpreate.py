# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''
import SingleTon
from _types         import types
from functools      import partial

class FormOpreate(SingleTon.SingleTon):
    def __init__(self):
        SingleTon.SingleTon.__init__(self)
        self.__form        = {}
        self.__blueprint   = None
        
    @property
    def Blueprint(self):return self.__blueprint
    
    @Blueprint.setter
    @types(basestring)
    def Blueprint(self,value):self.BluePrint = value
    
    
    def getBlueprint(self,blueprint):
        if blueprint:self.BluePrint = blueprint
        return self.BluePrint
    
    @property
    def Forms(self):return self.__form
    
    
    def setForm(self,key,value,blueprint=None):
        """
        @attention: append data to diction 
        @param key: data key
        @param value: flask_wtform 
        @param blueprint: blueprint name   
        """
        blueprint = self.getBlueprint(blueprint)
        
        if not self.Forms.has_key(self.BluePrint):
            self.Forms[self.BluePrint]={}
        
        if not self.Forms.get(self.BluePrint).has_key(key):
            self.Forms.get(self.BluePrint)[key] = value
        else:
            print "key exist",self.BluePrint,key,value
    
    def getForm(self,key,blueprint=None):
        """
        @attention: get the flask_wtform object by form name
        @param key: form name
        @param blueprint: blueprint name  
        """
        blueprint= self.getBlueprint(blueprint)
        if self.Forms.has_key(blueprint):
            _obj = self.Forms.get(blueprint)
            if _obj.has_key(key):
                return _obj.get(key)()
        print "key not exist",blueprint,key
            
            
    def Register(self,blueprint,*args,**kwgs):
        """
        @attention: register the form data
        @param blueprint: blueprint name
        @param *arg: args
        @param **kwargs: kwargs  
        """
        self.BluePrint = blueprint
        if not self.Forms.has_key(self.BluePrint):
            self.Forms[blueprint] = {}
        if args:
            _data  = [(c.__name__,c) for c in args]
            kwgs.update(_data)
        [self.setForm(key,value)for key,value in kwgs.items()]    
    
    def _setFormDataByModel(self,form,data):
        """
        @attention: set the form data 
        @param form: flask_wtform
        @param  data: orm model
        """
        for key in form.data.keys():
            if hasattr(data, key):
                getattr(form,key).data = getattr(data,key)
    
    def _setFormDataByDict(self,form,data):
        """
        @attention: set the form data
        @param form: flask_wtform
        @param data: diction data  
        """
        for key in form.__dict__.keys():
            if data.has_key(key):
                getattr(form,key).data = data.get(key)
        print form
        
    def setFormData(self,form,data):
        """
        @attention: set the form data
        @param form: flask_wtform
        @param data: diction or model object  
        """
        if isinstance(data,dict):
            self._setFormDataByDict(form, data)
        else:
            self._setFormDataByModel(form, data)
    
    def GetPartial(self,blueprint):
        """
        @attention: get the partial agent
        @param blueprint: blueprint name
        """
        return partial(self.getForm,blueprint=blueprint)
    
_formOperateUtil = FormOpreate()
