# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''
from ...common.ExcelToPdf   import Excel, AppQueue
from ..page_config          import page_table_configs
from ...common              import _dataBaseUtil    as dataUtil
import os
from flask                  import current_app,request
from flask_login            import current_user
RowStart = (4,1)
RowNumber= 25
Last     = (RowStart[0]+RowNumber,2)
Custemer = (6,5)
TelePhone= (8,5)
DateFrom = (10,5)
DateTo   = (10,8)
Bill     = (12,5)
LastBill = (14,5)
CurrBill = (16,5)
Total    = (5,10,12)
class WriteToExcel(object):
    def __init__(self):
        object.__init__(self)
    
    def WriteIndex(self,data,total):
        sheetName = 1
        self.__excel.setCell(sheetName,Custemer[0],Custemer[1],data[0])
        self.__excel.setCell(sheetName,TelePhone[0],TelePhone[1],data[1])
        self.__excel.setCell(sheetName,DateFrom[0],DateFrom[1],data[2])
        self.__excel.setCell(sheetName,DateTo[0],DateTo[1],data[3])
        self.__excel.setCell(sheetName,Bill[0],Bill[1],data[4])
        self.__excel.setCell(sheetName,LastBill[0],LastBill[1],data[5])
        self.__excel.setCell(sheetName,CurrBill[0],CurrBill[1],data[6])
        _row   = Total[0]
        _totalS= self.__excel.getCell(sheetName,_row,Total[1]).replace("$","%s"%total)
        _currS = self.__excel.getCell(sheetName,_row,Total[2]).replace("$","%s"%1)
        self.__excel.setCell(sheetName,_row,Total[1],_totalS)
        self.__excel.setCell(sheetName,_row,Total[2],_currS)
        
    def WriteTitle(self,sheet,current,total,colEnd):
        _row = RowStart[0] - 2
        data = dataUtil.CurrentDateStr
        self.__excel.setCell(sheet,_row,2,data)
        _totalS= self.__excel.getCell(sheet,_row,colEnd-1).replace("$","%s"%total)
        _currS = self.__excel.getCell(sheet,_row,colEnd).replace("$","%s"%current)
        self.__excel.setCell(sheet,_row,colEnd-1,_totalS)
        self.__excel.setCell(sheet,_row,colEnd,_currS)
        self.__excel.setCell(sheet,Last[0],Last[1],current_user.username)
        
    def GetPageNumber(self,data):
        _len = len(data) / RowNumber
        if _len * RowNumber < len(data):
            _len += 1
        return _len
    
    def WriteToExcel(self,indexData,data,fileName):
        self.__excel.open(fileName)
        _len   = self.GetPageNumber(data)
        _total = _len + 1
        self.WriteIndex(indexData,_total)
        [self.__excel.AppendSheetByTemp() for ids in range(_len-1)]
        for index in range(1,_len+1):
            sheet = index + 1
            if index == 1:
                _data = data[:RowNumber]
            elif index == len(_len):
                _data = data[(index)*RowNumber:]
            else:
                _data = data[(index)*RowNumber:(index+1)*RowNumber]
            self.__excel.setRange(sheet, RowStart[0], RowStart[1],_data)
            self.__excel.xlBook.Worksheets(sheet).Name = "%02d"%(sheet) 
            self.WriteTitle(sheet, sheet, _len+1, len(_data[0]))
        self.__excel.save()
        self.__excel.close()
        
    def __get_file(self, fileName):
        return current_app.config.get("DOWNLOAD_FILE") + "/" + fileName
        
    def get_file_name(self, operType, isGbk=False):
        date = dataUtil.CurrentDateStr
        if isGbk:
            _userOpt = dataUtil.getDataBase("UserOperate", "User")
            username = dataUtil.getModel(_userOpt, id=self.ReqData.get("userName"))[0]
            _name = username.username
            fileName = u"%s_%s_%s.xlsx" % (date, _name, u"对账单")
        else:
            fileName = u"%s_%s_%s.xlsx" % (date, self.ReqData.get("userName"), operType)
        return fileName
    
    def get_true_str(self, one):
        try:
            one = str(one)
        except:
            pass
        return one
    
    def Main(self,operType,indexData,data,fileName=None):
        self.ReqData = request.form.to_dict()
        self.__excel = Excel(AppQueue.GetApp())
        _temp        = self.__get_file("base_template/%s.xlsx"%operType)
        self.__excel.open(_temp)
        fileName     = fileName or self.get_file_name(operType)
        _fileName    = self.__get_file(fileName)
        self.__excel.save(_fileName)
        self.WriteToExcel(indexData,data, _fileName)
        return fileName
