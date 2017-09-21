# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''
from ...common              import _dataBaseUtil    as dataUtil
from ...common              import _formOperateUtil as formUtil
from ...common.ExcelToPdf   import Excel, AppQueue, ExcelToPdf
from ...Finance.services    import BillService
from flask                  import request, make_response, send_file
from ..page_config          import page_table_configs
from flask_login            import current_user
import os
from flask                  import current_app, session, jsonify
from WriteToExcel           import WriteToExcel
from ZipFile                import ZipDownFile
from sqlalchemy             import desc
import time


_Bom = "Bom"
_user = "User"
_getOper = dataUtil.GetPartial("Production")
_getForm = formUtil.GetPartial(_Bom)
_userOpt = dataUtil.getDataBase("UserOperate", _user)
_BillService = BillService.BillService()
class Search(object):
    def __init__(self):
        object.__init__(self)
        self.__pageNumber = 1
        self.__pageSize = 20
        self.DateFrom = None
        self.DateTo = None
        self.ReqData = None
        
    @property
    def FormError(self):return self.__formError
    @FormError.setter
    def FormError(self, value):self.__formError = value
    @property
    def PageNumber(self):return self.__pageNumber
    @PageNumber.setter
    def PageNumber(self, value):self.__pageNumber = int(value)
    @property
    def PageSize(self):return self.__pageSize
    @PageSize.setter
    def PageSize(self, value):self.__pageSize = int(value)
    
    def CheckFrom(self, form):
        self.FormError = None
        if form.is_submitted() or request.method.upper() == "POST":
            if form.validate_on_submit():
                return True
            self.FormError = form.errors
        return False
    
    def _fun(self, query, model, form, key, isEqual=True):
        if not isinstance(form, dict):
            _obj = form.data
        else:
            _obj = form
        data = _obj.get(key)
        if data:
            if isinstance(data, basestring):
                data = data.replace("*", "%")
            if key.endswith("id"):data = int(data)
            _type = getattr(model, key)
            if isEqual:query = query.filter(_type == data)
            else:query = query.filter(_type.like("%s" % data))
        return query
    
    def __get__search(self, pageNumber, pageSize, oper):
        limit = pageSize
        if pageNumber > 0:
            offset = (pageNumber - 1) * pageSize
        else:
            offset = 0
        _model = oper.Model
        _query = _model.query
        _query = _query.limit(limit).offset(offset)
        return _query
    
    def __get_date_filter(self, _oper):
        model = _oper.Model
        query = model.query
        if self.DateFrom:
            query = query.filter(model.date >= self.DateFrom)
        if self.DateTo:
            query = query.filter(model.date <= self.DateTo)
        return query
    
    def get_sell_money(self, sell):
        """
        @attention: 获取销售的付款信息
        """
        _oper = _getOper("money")
        money = dataUtil.getModel(_oper, id=sell.money_id)[0]
        return money.price
    
    def get_roll_money(self, roll):
        """
        @attention: 获取退款中的付款信息
        """
        _oper = dataUtil.getDataBase("money", "Production")
        money = dataUtil.getModel(_oper, id=roll.money_id)[0]
        return money.price
    
    def get_back_data(self):
        _oper = _getOper("rollback")
        query = self.__get_date_filter(_oper)
        if self.ReqData.get("username"):
            self.ReqData['customer_id'] = self.ReqData.get("username")
            query = self._fun(query, _oper.Model, self.ReqData, "customer_id", True)
        models = query.all() or []
        sells = [model.sell for model in models]
        _oper = _getOper("sell")
        _data = _oper.get_data(sells, True)[-1]
        for _m, _d in zip(models, _data):
            _d['number'] = -_m.number 
            _d['money_id'] = self.get_roll_money(_m)
            _d["total_price"] = _d.get("number") * _m.sell.price 
            _d['bill_money'] = _d.get("total_price") - _d.get('money_id') 
        return _data
    
    def sort(self, one, two):
        if one.get("date") > two.get("date"):
            return 1
        elif one.get('date') == two.get("date"):
            return 0
        else:
            return -1
        
    def cstbill(self):
        """
        @attention: 生成客户对账单数据
        在销售的过程中,只管用户退了多少货，卖了多少货
        """
        _oper = _getOper("sell")
        query = self.__get_date_filter(_oper)
        if self.ReqData.get("username"):
            self.ReqData['customer_id'] = self.ReqData.get("username")
            query = self._fun(query, _oper.Model, self.ReqData, "customer_id", True)
        model = query.all()
        _data = []
        if model:
            _data = _oper.get_data(model, True)[-1]
            for _m, _d in zip(model, _data):
                _d['number'] = _m.number 
                _d['money_id'] = self.get_sell_money(_m)
                _d["total_price"] = _d.get("number") * _m.price 
                _d['bill_money'] = _d.get("total_price") - _d.get('money_id') 
        back_data = self.get_back_data()
        _data.extend(back_data)
        _data.sort(self.sort)
        if _data:
            return dataUtil.ResOk({'length':len(_data), 'data':_data})
        else:
            return dataUtil.ResError("不存在--{0}---的对账数据")
                
    def sptbill(self):
        """
        @attention: 生成供应商对账单数据
        """
        _oper = _getOper("stock")
        query = self.__get_date_filter(_oper)
        if self.ReqData.get("username"):
            self.ReqData['support_id'] = self.ReqData.get("username")
            query = self._fun(query, _oper.Model, self.ReqData, "support_id", True)
        model = query.all()
        if model:
            _data = _oper.get_data(model, True)[-1]
            for _d in _data:
                _d['all_money'] = float(_d.get('number')) * float(_d.get("price"))
            return dataUtil.ResOk(({'length':len(_data), 'data':_data}))
        return dataUtil.ResError(u"不存在--{0}---的对账数据")
    
    def Main(self, operType,reqdata=None):
        #此处位置记得传入reqdate 因为后面可能会导致这个失效
        self.ReqData = reqdata or request.form.to_dict()
        self.DateFrom = self.ReqData.get("dateFrom")
        self.DateTo = self.ReqData.get("dateTo")
        return getattr(self, operType)()

    def get_page_config(self, operType):
        config = page_table_configs.get(operType.lower())
        data = [(one.get("field"), one.get("title"))for one in config]
        column = [one[0] for one in data ]
        first = [one[1] for one in data ]
        return first, column
    
    def get_data(self, operType):
        """
        @attention: 获取生成的账单数据和表头的信息
        """
        data = self.Main(operType,self.ReqData)
        if not data.get('state'):
            data = []
        else:
            data = data.get("msg")
            data = data.get("data")
        first, column = self.get_page_config(operType)
        _result = [first]
        [_result.append([one.get(col) for col in column]) for one in data]
        return _result

    
    def __get_file(self, fileName):
        path = current_app.config.get("DOWNLOAD_FILE")
        if not os.path.exists(path):
            os.mkdir(path)
        return path + "/" + fileName
        
    def get_file_name(self, operType, isGbk=True):
        #文件名称安装结束日期来确定
        date = self.ReqData.get("dateTo")
        date = date.split("-")
        date = "%s-%s"%(date[0],date[1])
        if isGbk:
            username = dataUtil.getModel(_userOpt, id=self.ReqData.get("username"))[0]
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
    
    def get_curent_rebund_money(self,customer_id,dateFrom):
        """
        @attention: 获取当前月份的还款信息
        """
        _oper = dataUtil.getDataBase('bill', 'Finance')
        date  = _BillService.GetBillDate(dateFrom)
        moth_money = 0
        if _BillService.HasBill(customer_id,date):
            state,_model = _oper.get(date=date)
            if state and _model:
                moth_money = _oper.GetBillAllMoney(_model[0].id)
            else:
                self.error_info = _model
        return moth_money
    
    def _update_bill(self,_ses,model,total_money,next_money):
        model.total_money = total_money
        model.next_money  = next_money
        model.level_money = total_money - next_money
        model.has_filled  = 1
        _ses.add(model)
        try:_ses.commit()
        except Exception,e:
            self.error_info = dataUtil.ResError("生成对账单信息,失败:%s" % e)
                    
    def _add_new(self,_ses,bill_date,total_money,next_money,customer_id):
        data= {
               "date":bill_date,
               "total_money":total_money,
               "next_money":next_money,
               "level_money":total_money - next_money,
               "customer_id":customer_id,
               "operator_id":current_user.id,
               "has_filled":1,
               }
        _BillService.AddNew(_ses,**data)
        try:
            _ses.commit()
        except Exception,e:
            self.error_info = dataUtil.ResError("生成对账单信息,失败:%s" % e)
             
    def generate_bill(self,total_money,next_money,customer_id,bill_date):
        """
        @attention: 获取账单数据,当传入的日期区间在账单数据库中有记录的时候,
        会覆盖掉以前的数据
        @param total_bill:当前计算的账单的总值 
        """
        _oper = dataUtil.getDataBase('bill', 'Finance')
        _ses = _oper.Session
        if _BillService.HasBill(customer_id,bill_date):
            state ,model = _oper.get(date= bill_date,customer_id=customer_id)
            if state and model:
                self._update_bill(_ses, model[0], total_money, next_money)
            else:
                self.error_info = dataUtil.ResError("生成对账单信息,失败:%s" % model)
        else:
            self._add_new(_ses,bill_date,total_money,next_money,customer_id)
                
        
    def _get_total_data(self, data):
        """
        @attention: 获取账单最后的合计项目
        @param data: 账单数据 
        """
        if data:
            _last = ["-"] * len(data[0])
            _last[8:10] = [0.0] * 2
            _last[0] = u"合计"
            _last[-1] = ""
            _fun = lambda cell, index:float(cell[index])
            _n = _r = _t = 0
            for cell in data:
                _r += _fun(cell, 10)
                _n += _fun(cell, 7)
                _t += _fun(cell, 11)
            _last[7] = _n
            _last[10] = _r
            _last[11] = _t
            data.append(_last)
        
    
    def get_current_date_from(self, dataTo):
        dataFrom = self.ReqData.get("dateFrom")
        _from = dataTo.split("-")
        _from[-1] = "01"
        _from = "-".join(_from)
        self.ReqData['dateFrom'] = _from
        return dataFrom
    
    def get_current_moth_bill(self, operType, dataTo):
        """
        @attention: 获取当月的账单数据
        """
        data = self.get_data(operType)[1:]
        bill = sum([float(cell[-2]) for cell in data])
        return bill, data
    
    def check_from_data(self, operType):
        """
        @attention: 检测账单的开始时间是否正确,
        @param operType: 操作类型 
        """
        self.ReqData = request.form.to_dict()
        _current = self.ReqData.get('dateFrom')
        _last = self.get_last_date()
        if not _current.endswith("01"):
            self.error_info = dataUtil.ResError(u"输入的账单开始日期不对,开始日期为每月的一号")
    
    def adjust_prev_bill(self):
        """
        @attention: 自动计算之前未计算过的月份结余值
        """
        _oper = dataUtil.getDataBase('bill', 'Finance')
        customer_id = self.ReqData.get("username")
        not_filled_bill = _oper.GetLastNotFillBill(customer_id)
        if not_filled_bill is not None:
            _ses = _oper.Session
            [_oper.UpdateBillNew(_ses,model.id) for model in not_filled_bill]
            try:
                _ses.commit()
            except:
                self.error_info = dataUtil.ResError(u"结转上月的账单数据失败")
    
    def get_excel_data(self, operType):
        """
        @attention: 将数据到处为excel 格式，在这个时候会生成一个账单数据项目
        @param operType: 操作类型,供应商账单还是客户账单 
        """
        user_id = self.ReqData["username"] or self.ReqData.get("userName")
        dateTo  = self.ReqData.get("dateTo")
        _bill_date_from = _BillService.GetBillDate(dateTo)
        dateFrom = self.ReqData.get("dateFrom")
        
        self.error_info = None
        # 结转上一次未付款的账单
        self.adjust_prev_bill()
        if self.error_info is not None:
            return self.error_info
        
        # 检测账单开始的时间是否是每月的一号,当需要跨时间的时候,不可行
        self.check_from_data(operType)
        if self.error_info is not None:
            return self.error_info
        
        # 此处位置会将用户输入的开始日期调整为 截至日期的当月的第一天
        # 将日期调整到当月的第一天,以便计算本月的账单信息
        moth_moeny = self.get_curent_rebund_money(user_id,_bill_date_from)
        if self.error_info is not None:
            return self.error_info
        
        # 获取当前月份的账单额和传入的日期的账单明细
        # 获取当月数据的时候会清除掉之前的 self.ReqData 所有这个地方需要加上
        self.ReqData['dateFrom'] = _bill_date_from
        self.ReqData['username'] = user_id
        bill, data = self.get_current_moth_bill(operType,self.ReqData.get("dateTo"))
        #计算非当前月区间的所有数据明细
        if _bill_date_from != dateFrom:
            self.ReqData["dateFrom"] = dateFrom
            data = self.get_data(operType)[1:]
        self.ReqData['username']=self.ReqData['customer_id']=user_id
        _user = _userOpt.get(id=user_id)[-1][0]
        _userName = _user.username
        _telephone = _user.telephone
        
        # 获取上个月的账单信息
        # 获取用户传入的时间的上一个月数据
        _oper = dataUtil.getDataBase('bill', 'Finance')
        lastbill = _oper.GetPrevMoney(user_id,_bill_date_from)
        # 上次付款后余留的钱,加上上一次付款到此次开始时间段未结的账
        # 当前账单存储的应该是用户实际需要还的钱
        # 当前的账单数据 - 上月的余留 - 当月还款
        
        # 客户的钱
        lastbill = moth_moeny - lastbill 
        
        #我的钱
        currbill = bill - lastbill
        
        # 在数据库中生成对账单
        self.generate_bill(bill,moth_moeny,user_id,_bill_date_from)
        if self.error_info is not None:
            return self.error_info
        # 获取合计数据
        self._get_total_data(data)
        dateTo = self.ReqData.get("dateTo")
        indexdata = [_userName, _telephone, dateFrom, dateTo, bill, -lastbill, currbill]
        name = self.get_file_name(operType, True)
        execl = WriteToExcel().Main(operType, indexdata, data, name)
        return dataUtil.ResOk(execl)
        
    def down_load_excel(self, operType):
        """
        @attention: 导出excel 报表
        """
        state = self.get_excel_data(operType)
        self.MoveOk(self._filter_execl)
        if state.get("state"):
            return dataUtil.ResOkJson("%s" % state.get("msg")) 
        else:
            return jsonify(state)
    
    def get_pdf_data(self, operType):
        state = self.get_excel_data(operType)
        if state.get("state"):
            fileName = state.get("msg")
            _fileName = self.__get_file(fileName)
            ExcelToPdf().Main([_fileName])
#             self.DeletFile(fileName)
            self.MoveOk(self._filter_execl)
            fileName = fileName.replace(".xlsx", ".pdf")
            return dataUtil.ResOk("%s" % fileName)
        else:
            return dataUtil.ResError(state.get("msg"))
        
    def down_load_pdf(self, operType):
        """
        @attention: 导出pdf 报表
        """
        return jsonify(self.get_pdf_data(operType))
        
    
    def _filter_execl(self, fileName):
        state = ".xlsx" in fileName and "cstbill" not in fileName
        return state
    
    def _filter_pdf(self, fileName):
        state = ".pdf" in  fileName or self._filter_execl(fileName)
        return state 
    
    def _get_all_user(self, operType):
        if operType == 'cstbill':
            users = dataUtil.GetDataByUrl("CustomerChoice", "User")
        else:
            users = dataUtil.GetDataByUrl("SupportChoice", "User")
        user_id = [user[0] for user in users()]
        return user_id
    
    def get_log_file(self):
        path = current_app.config.get("DOWNLOAD_FILE")
        log = os.path.join(path, u"%s对账单错误日志.log" % current_user.username)
        fp = open(log, "w")
        return fp
    
    def _get_zip_name(self, operType):
        name = self.ReqData.get("dateTo").split("-")[1]
        return u"%s月份对账单数据.zip" % (name)  # ,operType)
    
    def _start_translate(self, users, function, operType):
        """
        @attention: 开始生成指定格式的对账单数据
        """
        _is_wrong = False
        logfile = self.get_log_file()
        for user_id in users:
            self.ReqData['username'] = int(user_id)
            self.ReqData["customer_id"] = int(user_id)
            try:
                result = function(operType)
                if not result.get("state"):
                    logfile.write(result.get("msg") + "\r\n")
                    _is_wrong = True
            except Exception,e:
                _is_wrong = True
                logfile.write("%s"%e+"\r\n")
        logfile.close()
        return _is_wrong
    
    def _base_bat(self, operType, function):
        """
        @attention: 指定批量生成对账单数据
        """
        all_user = self._get_all_user(operType)
        logfile = self.get_log_file()
        _is_wrong = self._start_translate(all_user, function, operType)
#         name = self._get_zip_name(operType)
#         name = self._get_zip_name(operType).split(".")[0]
        name = self._create_folder()
        logname = logfile.name
        logfile.close()
        if _is_wrong:
            msg = u"有部分用户的对账单未生成,请查看:%s文件中的%s,正在下载..." % \
                (name, logfile.name)
        else:
            msg = u"%s" % name
            os.remove(logname)
        return dataUtil.ResOk(msg)
    
    def _bat_excel(self, operType):
        return self._base_bat(operType, self.get_excel_data)

    def _bat_pdf(self, operType):
        return self._base_bat(operType, self.get_pdf_data)
    
    def _create_folder(self):
        name = self.ReqData.get('dateTo').split("-")
        folder = u"%s-%s月份对账单" % (name[0], name[1])
        return folder
    
    def MoveOk(self, _filter):
        DOWNLOAD_FILE = current_app.config.get("DOWNLOAD_FILE")
        command = "cd /d %s \r\n" % DOWNLOAD_FILE
        folder = self._create_folder()
        foler = self._create_folder()
        path = os.path.join(DOWNLOAD_FILE, foler)
        if not os.path.exists(path):
            os.mkdir(path)
        fp = open(DOWNLOAD_FILE + "rm.bat", "w")
        fp.write("@ECHO OFF\r\n")
        fp.write(command)
        fp.write("move *.pdf  ./%s \r\n" % folder.encode("cp936"))
        fp.write("move *.xlsx  ./%s \r\n" % folder.encode("cp936"))
        fp.close()
        os.system(DOWNLOAD_FILE + "rm.bat")
        os.remove(DOWNLOAD_FILE + "rm.bat")
        return folder
        
    def _dispater(self, operType, function, _filter):
#         zipName = self._get_zip_name(operType)
#         folder  = self._create_folder()
#         _zip     = ZipDownFile()
#         _zip._filter = _filter
#         _file   = _zip.Main(folder)
        result = function(operType)
        folder = self.MoveOk(_filter)
        result['zip'] = folder
        return jsonify(result)
    
    def down_load_bat_excel(self, operType):
        """
        @attention: 批量生成对账单
        """
        return self._dispater(operType, self._bat_excel, self._filter_execl)
    
    def down_load_bat_pdf(self, operType):
        """
        @attention: 批量生成pdf对账单
        """
        return self._dispater(operType, self._bat_pdf, self._filter_pdf)
    
    
    def DwonOk(self, operType, fileName, downName):
        """
        @attention: 下载数据
        @param operType: 用户当前的操作类型
        @param fileName: static download 文件夹下面的文件名
        @param downName: 下载后重命名的文件名 
        """
        if fileName.endswith(".zip"):
            fileName = fileName.split("_")[0] + u"月份对账单.zip"
        else:
            fileName = self.__get_file(fileName)
        response = make_response(send_file(fileName, 'zip'))
        response.headers["content_type"] = "application/octet-stream"
        response.headers["Content-Disposition"] = "attachment; filename=%s;" % downName.encode("utf-8")
        return response
    
    def DeletFile(self, fileName):
        """
        @attention: 删除static download 文件夹下面的文件
        @param fileName: 文件名称 
        """
        fileName = self.__get_file(fileName)
        os.remove(fileName)
        return dataUtil.ResOkJson("ok")
    
    def DwonLoad(self):
        self.ReqData = request.form.to_dict()
        operType = self.ReqData.get("operType")
        fileType = self.ReqData.get("fileType")
        return getattr(self, "down_load_%s" % fileType.lower())(operType)
    
    def get_last_date(self):
        """
        @attention: 获取用户上次还款的截至日期
        """
        if not self.ReqData:
            self.ReqData = request.form.to_dict()
        customer_id = self.ReqData.get("customer_id") or self.ReqData.get("username")
        _oper = dataUtil.getDataBase('bill', 'Finance')
        model = _oper.GetPreEndDate(customer_id)
        if model:
            dateFrom = dataUtil.GetPrevData(str(model[0].date), 1)
            dateFrom = dateFrom.split("-")
            if dateFrom[1] =="1":
                moth = 12
                year = int(dateFrom[0])-1
            else:
                moth = int(dateFrom[1]) - 1
                year = dateFrom[0]
            dateFrom ="%s-%s-01"%(year,moth)
        else:
            dateFrom = dataUtil.CurrentDateStr.split("-")
            dateFrom[-1] = "01"
            dateFrom = "-".join(dateFrom)
        return dateFrom
    
    def has_bill(self):
        """
        @attention: 检测选择的开始时间是否已经计算过了账单,
        当用户已经还过款的时候，给予提示
        """
        return dataUtil.ResOkJson(u"日期有效")
    
    def get_sub_cell(self, _model):
        models = _model.all()
        return sum([cell.money_price for cell in models] or [0])
    
    def get_last_prev_bill(self,user_id,date):
        _oper  = dataUtil.getDataBase("bill", "Finance")
        model  = _oper.Model
        _query = model.query.filter(model.customer_id == user_id,
                                    model.date<date).limit(1)
        model = _query.all()
        if model:
            model = model[0]
            bill  = model.total_money
            date  = model.date
            prev  = self.get_prev_bill(model.customer_id, date)
            return bill + prev
        return 0
    
    def get_prev_bill(self, user_id, date):
        """
        @attention: 获取上月账单余额数据
        """
        _oper = dataUtil.getDataBase("bill", "Finance")
        data  = _oper.GetPrevMoney(user_id,date)
        return data
    
    def get_bills_info(self,start,end, user_id=None):
        """
        @attention:  获取账单信息
        @param date: 账单名 格式 2017-01-01
        @param user_id: 用户id号  
        """
        _oper = dataUtil.getDataBase("bill", "Finance")
        query = _oper.Model.query.filter(_oper.Model.date>=start,
                                         _oper.Model.date<=end)
        if user_id:
            query = query.filter(_oper.Model.customer_id == user_id)
        model = query.all()
        return model
    
    def get_bill_date(self,date):
        if date.count("-") == 2:
            date = _BillService.GetBillDate(date)
        else:
            date += "-01"
        return date
    
    def get_current_bill(self, user_id, start,end):
        """
        @attention:  获取当月的账单
        """
        model = self.get_bills_info(start,end, user_id)
        data = []
        if model:
            _oper = dataUtil.getDataBase("bill", "Finance")
            data = _oper.get_data(model, True)[-1]
            _ses = _oper.Session
            for _m, _d in zip(model, data):
                date = _d.get("date")
                _d["p_total"]   = self.get_last_prev_bill(_m.customer_id,date)
                _d["prev_money"] = self.get_prev_bill(_m.customer_id, date)
                _d['rebund'] = self.get_sub_cell(_m.rebund)
                _d['rebate'] = self.get_sub_cell(_m.rebate)
                _d["writeOff"] = self.get_sub_cell(_m.writeOff)
                _rebund_all    = _d['rebund']+_d['rebate']+_d['writeOff']
                _d['cell_money'] = _d['total_money']+_d["prev_money"]- _rebund_all
                if _rebund_all != _m.next_money:
                    _m.next_money = _rebund_all
                    _m.level_money= _m.total_money - _rebund_all
                    _ses.add(_m)
            try:
                _ses.commit()
            except Exception,e:
                print e
                print u"查看账单时,自动更新当月还款记录失败,请联系管理员"
        return data
    
    def bill_to_dict(self, data):
        _dict = {}
        for cell in data:
            _dict[cell.get('customer_id')] = cell
        return _dict
    
    def get_bill_data(self,user_id,start,end):
        curent = self.get_current_bill(user_id,start, end)
        if curent:
            return dataUtil.ResOk({'length':len(curent), 'data':curent})
        return dataUtil.ResError(u"未能获取该时间段的账单数据")
    
    def get_bills(self):
        self.ReqData = request.form.to_dict()
        self.DateTo = self.ReqData.get("dateTo")
        self.DateFrom = self.ReqData.get("dateFrom")
        #=======================================================================
        # 获取传入的日期，并通过日期来确定用户选择的是几月的
        #=======================================================================
        user_id = self.ReqData.get("username")
        if not (user_id and int(user_id) > 0):
            user_id = None
        start= self.get_bill_date(self.DateFrom)
        end = self.get_bill_date(self.DateTo)
        return jsonify(self.get_bill_data(user_id,start, end))
    
    def delete_bill_manager(self):
        """
        @attention: 返回时间段的账单数据并删除
        """
        self.ReqData = request.form.to_dict()
        _oper = dataUtil.getDataBase("bill", "Finance")
        _oper.delete_model(self.ReqData.get("bill_id"))
        state = _oper.delete()[0]
        if not state:
            return dataUtil.ResErrorJson(u"删除数据失败")
        return dataUtil.ResOkJson(u"删除数据成功")
    
    def load_all(self, oper):
        if oper.lower() == 'bill_manager':
            date = dataUtil.CurrentDateStr.split("-")
            date = "%s-%s-01"%(date[0],date[1])
            data = self.get_bill_data(None,date,date)
            if data.get("state"):
                data = data.get("msg").get("data")
            else: 
                data = []
        else:
            data = []
        return data
    
    def WriteError(self,error):
        down = current_app.config.get("DOWNLOAD_FILE")
        _log = "%s_calculate_bill.log"%(current_user.username)
        _file= os.path.join(down,_log)
        fp  = open(_file,"w+")
        string ="\r\n".join(error)
        fp.write(string)
        fp.close()
        
    def calculate_bill(self):
        self.ReqData = request.form.to_dict()
        start = self.ReqData.get("dateFrom")
        end   = self.ReqData.get("dateTo")
        userId= self.ReqData.get("customer_id")
        if not start:
            return dataUtil.ResErrorJson(u"请选择开始日期")
        else:
            errors = _BillService.UpdateBillAll(start, end, userId)
            if not errors:
                return dataUtil.ResOkJson(u"重新计算所有的账单信息,成功")
            else:
                _fileName = self.WriteError(errors)
                return dataUtil.ResErrorJson(u"计算部分账单信息成功,请查看%中的错误信息"%_fileName)
            
_searchUtil = Search()

