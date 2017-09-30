# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''
from ...common import _dataBaseUtil    as dataUtil
from ...common import _formOperateUtil as formUtil
from ...common.ExcelToPdf import Excel, AppQueue, ExcelToPdf
from ...Finance.services import BillService
from flask import request, make_response, send_file
from ..page_config import page_table_configs
from flask_login import current_user
import os
from flask import current_app, session, jsonify
from WriteToExcel import WriteToExcel
from ZipFile import ZipDownFile
from sqlalchemy import desc
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
    def form_error(self):
        return self.__formError

    @form_error.setter
    def form_error(self, value):
        self.__formError = value

    @property
    def page_number(self):
        return self.__pageNumber

    @page_number.setter
    def page_number(self, value):
        self.__pageNumber = int(value)

    @property
    def page_size(self):
        return self.__pageSize

    @page_size.setter
    def page_size(self, value):
        self.__pageSize = int(value)

    def check_form(self, form):
        self.form_error = None
        if form.is_submitted() or request.method.upper() == "POST":
            if form.validate_on_submit():
                return True
            self.form_error = form.errors
        return False

    def _fun(self, query, model, form, key, equal=True):
        if not isinstance(form, dict):
            _obj = form.data
        else:
            _obj = form
        data = _obj.get(key)
        if data:
            if isinstance(data, basestring):
                data = data.replace("*", "%")
            if key.endswith("id"): data = int(data)
            _type = getattr(model, key)
            if equal:
                query = query.filter(_type == data)
            else:
                query = query.filter(_type.like("%s" % data))
        return query

    def __get__search(self, page_number, page_size, operate):
        limit = page_size
        if page_number > 0:
            offset = (page_number - 1) * page_size
        else:
            offset = 0
        _model = operate.model
        _query = _model.query
        _query = _query.limit(limit).offset(offset)
        return _query

    def __get_date_filter(self, operate):
        model = operate.model
        query = model.query
        if self.DateFrom:
            query = query.filter(model.date >= self.DateFrom)
        if self.DateTo:
            query = query.filter(model.date <= self.DateTo)
        return query

    @staticmethod
    def get_sell_money(sell):
        """
        @attention: 获取销售的付款信息
        """
        money = dataUtil.getModel(_getOper("money"), id=sell.money_id)[0]
        return money.price

    @staticmethod
    def get_roll_money(roll):
        """
        @attention: 获取退款中的付款信息
        """
        money = dataUtil.getModel(dataUtil.getDataBase("money", "Production"), id=roll.money_id)[0]
        return money.price

    def get_back_data(self):
        operate = _getOper("rollback")
        query = self.__get_date_filter(operate)
        if self.ReqData.get("username"):
            self.ReqData['customer_id'] = self.ReqData.get("username")
            query = self._fun(query, operate.model, self.ReqData, "customer_id", True)
        models = query.all() or []
        sells = [model.sell for model in models]
        operate = _getOper("sell")
        _data = operate.get_data(sells, True)[-1]
        for _m, _d in zip(models, _data):
            _d['number'] = -_m.number
            _d['money_id'] = self.get_roll_money(_m)
            _d["total_price"] = _d.get("number") * _m.sell.price
            _d['bill_money'] = _d.get("total_price") - _d.get('money_id')
        return _data

    @staticmethod
    def sort(one, two):
        if one.get("date") > two.get("date"):
            return 1
        elif one.get('date') == two.get("date"):
            return 0
        else:
            return -1

    def cst_bill(self):
        """
        @attention: 生成客户对账单数据
        在销售的过程中,只管用户退了多少货，卖了多少货
        """
        operate = _getOper("sell")
        query = self.__get_date_filter(operate)
        if self.ReqData.get("username"):
            self.ReqData['customer_id'] = self.ReqData.get("username")
            query = self._fun(query, operate.model, self.ReqData, "customer_id", True)
        model = query.all()
        _data = []
        if model:
            _data = operate.get_data(model, True)[-1]
            for _m, _d in zip(model, _data):
                _d['number'] = _m.number
                _d['money_id'] = self.get_sell_money(_m)
                _d["total_price"] = _d.get("number") * _m.price
                _d['bill_money'] = _d.get("total_price") - _d.get('money_id')
        back_data = self.get_back_data()
        _data.extend(back_data)
        _data.sort(self.sort)
        if _data:
            return dataUtil.ResOk({'length': len(_data), 'data': _data})
        else:
            return dataUtil.ResError("不存在--{0}---的对账数据")

    def spt_bill(self):
        """
        @attention: 生成供应商对账单数据
        """
        operate = _getOper("stock")
        query = self.__get_date_filter(operate)
        if self.ReqData.get("username"):
            self.ReqData['support_id'] = self.ReqData.get("username")
            query = self._fun(query, operate.model, self.ReqData, "support_id", True)
        model = query.all()
        if model:
            _data = operate.get_data(model, True)[-1]
            for _d in _data:
                _d['all_money'] = float(_d.get('number')) * float(_d.get("price"))
            return dataUtil.ResOk(({'length': len(_data), 'data': _data}))
        return dataUtil.ResError(u"不存在--{0}---的对账数据")

    def main(self, operete_type, request_data=None):
        # 此处位置记得传入reqdate 因为后面可能会导致这个失效
        self.ReqData = request_data or request.form.to_dict()
        self.DateFrom = self.ReqData.get("dateFrom")
        self.DateTo = self.ReqData.get("dateTo")
        return getattr(self, operete_type)()

    @staticmethod
    def get_page_config(operate_type):
        config = page_table_configs.get(operate_type.lower())
        data = [(one.get("field"), one.get("title")) for one in config]
        column = [one[0] for one in data]
        first = [one[1] for one in data]
        return first, column

    def get_data(self, operate_type):
        """
        @attention: 获取生成的账单数据和表头的信息
        """
        data = self.main(operate_type, self.ReqData)
        if not data.get('state'):
            data = []
        else:
            data = data.get("msg")
            data = data.get("data")
        first, column = self.get_page_config(operate_type)
        _result = [first]
        [_result.append([one.get(col) for col in column]) for one in data]
        return _result

    @staticmethod
    def __get_file(file_name):
        path = current_app.config.get("DOWNLOAD_FILE")
        if not os.path.exists(path):
            os.mkdir(path)
        return path + "/" + file_name

    def get_file_name(self, operate_type, gbk=True):
        # 文件名称安装结束日期来确定
        date = self.ReqData.get("dateTo")
        date = date.split("-")
        date = "%s-%s" % (date[0], date[1])
        if gbk:
            username = dataUtil.getModel(_userOpt, id=self.ReqData.get("username"))[0]
            _name = username.username
            file_name = u"%s_%s_%s.xlsx" % (date, _name, u"对账单")
        else:
            file_name = u"%s_%s_%s.xlsx" % (date, self.ReqData.get("userName"), operate_type)
        return file_name

    @staticmethod
    def get_true_str(one):
        try:
            one = str(one)
        except:
            pass
        return one

    def get_current_rebund_money(self, customer_id, date_from):
        """
        @attention: 获取当前月份的还款信息
        """
        operate = dataUtil.getDataBase('bill', 'Finance')
        date = _BillService.get_bill_date(date_from)
        moth_money = 0
        if _BillService.has_bill(customer_id, date):
            state, _model = operate.get(date=date)
            if state and _model:
                moth_money = operate.get_bill_all_money(_model[0].id)
            else:
                self.error_info = _model
        return moth_money

    def _update_bill(self, _ses, model, total_money, next_money):
        model.total_money = total_money
        model.next_money = next_money
        model.level_money = total_money - next_money
        model.has_filled = 1
        _ses.add(model)
        try:
            _ses.commit()
        except Exception, e:
            self.error_info = dataUtil.ResError("生成对账单信息,失败:%s" % e)

    def _add_new(self, _ses, bill_date, total_money, next_money, customer_id):
        data = {
            "date": bill_date,
            "total_money": total_money,
            "next_money": next_money,
            "level_money": total_money - next_money,
            "customer_id": customer_id,
            "operator_id": current_user.id,
            "has_filled": 1,
        }
        _BillService.add_new(_ses, **data)
        try:
            _ses.commit()
        except Exception, e:
            self.error_info = dataUtil.ResError("生成对账单信息,失败:%s" % e)

    def generate_bill(self, total_money, next_money, customer_id, bill_date):
        """
        @attention: 获取账单数据,当传入的日期区间在账单数据库中有记录的时候,
        会覆盖掉以前的数据
        """
        _oper = dataUtil.getDataBase('bill', 'Finance')
        _ses = _oper.Session
        if _BillService.has_bill(customer_id, bill_date):
            state, model = _oper.get(date=bill_date, customer_id=customer_id)
            if state and model:
                self._update_bill(_ses, model[0], total_money, next_money)
            else:
                self.error_info = dataUtil.ResError("生成对账单信息,失败:%s" % model)
        else:
            self._add_new(_ses, bill_date, total_money, next_money, customer_id)

    @staticmethod
    def _get_total_data(data):
        """
        @attention: 获取账单最后的合计项目
        @param data: 账单数据 
        """
        if data:
            _last = ["-"] * len(data[0])
            _last[8:10] = [0.0] * 2
            _last[0] = u"合计"
            _last[-1] = ""
            _fun = lambda cell, index: float(cell[index])
            _n = _r = _t = 0
            for cell in data:
                _r += _fun(cell, 10)
                _n += _fun(cell, 7)
                _t += _fun(cell, 11)
            _last[7] = _n
            _last[10] = _r
            _last[11] = _t
            data.append(_last)

    def get_current_date_from(self, date_to):
        _from = date_to.split("-")
        _from[-1] = "01"
        _from = "-".join(_from)
        self.ReqData['dateFrom'] = _from
        return self.ReqData.get("dateFrom")

    def get_current_moth_bill(self, operate_type, dataTo):
        """
        @attention: 获取当月的账单数据
        """
        data = self.get_data(operate_type)[1:]
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
        operate = dataUtil.getDataBase('bill', 'Finance')
        customer_id = self.ReqData.get("username")
        not_filled_bill = operate.get_last_not_fill_bill(customer_id)
        if not_filled_bill is not None:
            _ses = operate.Session
            [operate.update_bill_new(_ses, model.id) for model in not_filled_bill]
            try:
                _ses.commit()
            except:
                self.error_info = dataUtil.ResError(u"结转上月的账单数据失败")

    def get_excel_data(self, operate_type):
        """
        @attention: 将数据到处为excel 格式，在这个时候会生成一个账单数据项目
        @param operate_type: 操作类型,供应商账单还是客户账单 
        """
        user_id = self.ReqData["username"] or self.ReqData.get("userName")
        date_to = self.ReqData.get("dateTo")
        _bill_date_from = _BillService.get_bill_date(date_to)
        date_from = self.ReqData.get("dateFrom")

        self.error_info = None
        # 结转上一次未付款的账单
        self.adjust_prev_bill()
        if self.error_info is not None:
            return self.error_info

        # 检测账单开始的时间是否是每月的一号,当需要跨时间的时候,不可行
        self.check_from_data(operate_type)
        if self.error_info is not None:
            return self.error_info

        # 此处位置会将用户输入的开始日期调整为 截至日期的当月的第一天
        # 将日期调整到当月的第一天,以便计算本月的账单信息
        moth_money = self.get_current_rebund_money(user_id, _bill_date_from)
        if self.error_info is not None:
            return self.error_info

        # 获取当前月份的账单额和传入的日期的账单明细
        # 获取当月数据的时候会清除掉之前的 self.ReqData 所有这个地方需要加上
        self.ReqData['dateFrom'] = _bill_date_from
        self.ReqData['username'] = user_id
        bill, data = self.get_current_moth_bill(operate_type, self.ReqData.get("dateTo"))
        # 计算非当前月区间的所有数据明细
        if _bill_date_from != date_from:
            self.ReqData["dateFrom"] = date_from
            data = self.get_data(operate_type)[1:]
        self.ReqData['username'] = self.ReqData['customer_id'] = user_id
        _user = _userOpt.get(id=user_id)[-1][0]
        _userName = _user.username
        _telephone = _user.telephone

        # 获取上个月的账单信息
        # 获取用户传入的时间的上一个月数据
        operate = dataUtil.getDataBase('bill', 'Finance')
        last_bill = operate.get_prev_money(user_id, _bill_date_from)
        # 上次付款后余留的钱,加上上一次付款到此次开始时间段未结的账
        # 当前账单存储的应该是用户实际需要还的钱
        # 当前的账单数据 - 上月的余留 - 当月还款

        # 客户的钱
        last_bill = moth_money - last_bill

        # 我的钱
        current_bill = bill - last_bill

        # 在数据库中生成对账单
        self.generate_bill(bill, moth_money, user_id, _bill_date_from)
        if self.error_info is not None:
            return self.error_info
        # 获取合计数据
        self._get_total_data(data)
        date_to = self.ReqData.get("dateTo")
        index_data = [_userName, _telephone, date_from, date_to, bill, -last_bill, current_bill]
        name = self.get_file_name(operate_type, True)
        execl = WriteToExcel().Main(operate_type, index_data, data, name)
        return dataUtil.ResOk(execl)

    def down_load_excel(self, operate_type):
        """
        @attention: 导出excel 报表
        """
        state = self.get_excel_data(operate_type)
        self.move_ok(self._filter_execl)
        if state.get("state"):
            return dataUtil.ResOkJson("%s" % state.get("msg"))
        else:
            return jsonify(state)

    def get_pdf_data(self, operate_type):
        state = self.get_excel_data(operate_type)
        if state.get("state"):
            file_name = state.get("msg")
            _fileName = self.__get_file(file_name)
            ExcelToPdf().Main([_fileName])
            self.move_ok(self._filter_execl)
            file_name = file_name.replace(".xlsx", ".pdf")
            return dataUtil.ResOk("%s" % file_name)
        else:
            return dataUtil.ResError(state.get("msg"))

    def down_load_pdf(self, operate_type):
        """
        @attention: 导出pdf 报表
        """
        return jsonify(self.get_pdf_data(operate_type))

    @staticmethod
    def _filter_execl(file_name):
        state = ".xlsx" in file_name and "cstbill" not in file_name
        return state

    def _filter_pdf(self, file_name):
        state = ".pdf" in file_name or self._filter_execl(file_name)
        return state

    @staticmethod
    def _get_all_user(operate_type):
        if operate_type == 'cstbill':
            users = dataUtil.GetDataByUrl("CustomerChoice", "User")
        else:
            users = dataUtil.GetDataByUrl("SupportChoice", "User")
        user_id = [user[0] for user in users()]
        return user_id

    @staticmethod
    def get_log_file():
        path = current_app.config.get("DOWNLOAD_FILE")
        log = os.path.join(path, u"%s对账单错误日志.log" % current_user.username)
        fp = open(log, "w")
        return fp

    def _get_zip_name(self, operType):
        name = self.ReqData.get("dateTo").split("-")[1]
        return u"%s月份对账单数据.zip" % (name)  # ,operType)

    def _start_translate(self, users, func, operate_type):
        """
        @attention: 开始生成指定格式的对账单数据
        """
        _is_wrong = False
        logfile = self.get_log_file()
        for user_id in users:
            self.ReqData['username'] = int(user_id)
            self.ReqData["customer_id"] = int(user_id)
            try:
                result = func(operate_type)
                if not result.get("state"):
                    logfile.write(result.get("msg") + "\r\n")
                    _is_wrong = True
            except Exception, e:
                _is_wrong = True
                logfile.write("%s" % e + "\r\n")
        logfile.close()
        return _is_wrong

    def _base_bat(self, operate_type, func):
        """
        @attention: 指定批量生成对账单数据
        """
        all_user = self._get_all_user(operate_type)
        logfile = self.get_log_file()
        _is_wrong = self._start_translate(all_user, func, operate_type)
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

    def _bat_excel(self, operate_type):
        return self._base_bat(operate_type, self.get_excel_data)

    def _bat_pdf(self, operate_type):
        return self._base_bat(operate_type, self.get_pdf_data)

    def _create_folder(self):
        name = self.ReqData.get('dateTo').split("-")
        folder = u"%s-%s月份对账单" % (name[0], name[1])
        return folder

    def move_ok(self, _filter):
        DOWNLOAD_FILE = current_app.config.get("DOWNLOAD_FILE")
        command = "cd /d %s \r\n" % DOWNLOAD_FILE
        folder = self._create_folder()
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

    def _dispatcher(self, operate_type, func, _filter):
        #         zipName = self._get_zip_name(operType)
        #         folder  = self._create_folder()
        #         _zip     = ZipDownFile()
        #         _zip._filter = _filter
        #         _file   = _zip.Main(folder)
        result = func(operate_type)
        folder = self.move_ok(_filter)
        result['zip'] = folder
        return jsonify(result)

    def down_load_bat_excel(self, operate_type):
        """
        @attention: 批量生成对账单
        """
        return self._dispatcher(operate_type, self._bat_excel, self._filter_execl)

    def down_load_bat_pdf(self, operate_type):
        """
        @attention: 批量生成pdf对账单
        """
        return self._dispatcher(operate_type, self._bat_pdf, self._filter_pdf)

    def down_ok(self, operType, file_name, down_name):
        """
        @attention: 下载数据
        @param operType: 用户当前的操作类型
        @param file_name: static download 文件夹下面的文件名
        @param down_name: 下载后重命名的文件名 
        """
        if file_name.endswith(".zip"):
            file_name = file_name.split("_")[0] + u"月份对账单.zip"
        else:
            file_name = self.__get_file(file_name)
        response = make_response(send_file(file_name, 'zip'))
        response.headers["content_type"] = "application/octet-stream"
        response.headers["Content-Disposition"] = "attachment; filename=%s;" % down_name.encode("utf-8")
        return response

    def delete_file(self, file_name):
        """
        @attention: 删除static download 文件夹下面的文件
        @param file_name: 文件名称 
        """
        file_name = self.__get_file(file_name)
        os.remove(file_name)
        return dataUtil.ResOkJson("ok")

    def download(self):
        self.ReqData = request.form.to_dict()
        return getattr(self, "down_load_%s" % self.ReqData.get("fileType").lower())(self.ReqData.get("operType"))

    def get_last_date(self):
        """
        @attention: 获取用户上次还款的截至日期
        """
        if not self.ReqData:
            self.ReqData = request.form.to_dict()
        customer_id = self.ReqData.get("customer_id") or self.ReqData.get("username")
        operate = dataUtil.getDataBase('bill', 'Finance')
        model = operate.get_pre_end_date(customer_id)
        if model:
            date_from = dataUtil.GetPrevData(str(model[0].date), 1)
            date_from = date_from.split("-")
            if date_from[1] == "1":
                moth = 12
                year = int(date_from[0]) - 1
            else:
                moth = int(date_from[1]) - 1
                year = date_from[0]
            date_from = "%s-%s-01" % (year, moth)
        else:
            date_from = dataUtil.CurrentDateStr.split("-")
            date_from[-1] = "01"
            date_from = "-".join(date_from)
        return date_from

    @staticmethod
    def has_bill():
        """
        @attention: 检测选择的开始时间是否已经计算过了账单,
        当用户已经还过款的时候，给予提示
        """
        return dataUtil.ResOkJson(u"日期有效")

    @staticmethod
    def get_sub_cell(_model):
        models = _model.all()
        return sum([cell.money_price for cell in models] or [0])

    def get_last_prev_bill(self, user_id, date):
        model = dataUtil.getDataBase("bill", "Finance").model
        _query = model.query.filter(model.customer_id == user_id,
                                    model.date < date).limit(1)
        model = _query.all()
        if model:
            model = model[0]
            bill = model.total_money
            date = model.date
            prev = self.get_prev_bill(model.customer_id, date)
            return bill + prev
        return 0

    @staticmethod
    def get_prev_bill(user_id, date):
        """
        @attention: 获取上月账单余额数据
        """
        data = dataUtil.getDataBase("bill", "Finance").get_prev_money(user_id, date)
        return data

    @staticmethod
    def get_bills_info(start, end, user_id=None):
        """
        @attention:  获取账单信息
        @param date: 账单名 格式 2017-01-01
        @param user_id: 用户id号  
        """
        operate = dataUtil.getDataBase("bill", "Finance")
        query = operate.model.query.filter(operate.model.date >= start,
                                           operate.model.date <= end)
        if user_id:
            query = query.filter(operate.model.customer_id == user_id)
        model = query.all()
        return model

    @staticmethod
    def get_bill_date(date):
        if date.count("-") == 2:
            date = _BillService.get_bill_date(date)
        else:
            date += "-01"
        return date

    def get_current_bill(self, user_id, start, end):
        """
        @attention:  获取当月的账单
        """
        model = self.get_bills_info(start, end, user_id)
        data = []
        if model:
            operate = dataUtil.getDataBase("bill", "Finance")
            data = operate.get_data(model, True)[-1]
            _ses = operate.Session
            for _m, _d in zip(model, data):
                date = _d.get("date")
                _d["p_total"] = self.get_last_prev_bill(_m.customer_id, date)
                _d["prev_money"] = self.get_prev_bill(_m.customer_id, date)
                _d['rebund'] = self.get_sub_cell(_m.rebund)
                _d['rebate'] = self.get_sub_cell(_m.rebate)
                _d["writeOff"] = self.get_sub_cell(_m.writeOff)
                _rebund_all = _d['rebund'] + _d['rebate'] + _d['writeOff']
                _d['cell_money'] = _d['total_money'] + _d["prev_money"] - _rebund_all
                if _rebund_all != _m.next_money:
                    _m.next_money = _rebund_all
                    _m.level_money = _m.total_money - _rebund_all
                    _ses.add(_m)
            try:
                _ses.commit()
            except Exception, e:
                print e
                print u"查看账单时,自动更新当月还款记录失败,请联系管理员"
        return data

    @staticmethod
    def bill_to_dict(data):
        _dict = {}
        for cell in data:
            _dict[cell.get('customer_id')] = cell
        return _dict

    def get_bill_data(self, user_id, start, end):
        current = self.get_current_bill(user_id, start, end)
        if current:
            return dataUtil.ResOk({'length': len(current), 'data': current})
        return dataUtil.ResError(u"未能获取该时间段的账单数据")

    def get_bills(self):
        self.ReqData = request.form.to_dict()
        self.DateTo = self.ReqData.get("dateTo")
        self.DateFrom = self.ReqData.get("dateFrom")
        # =======================================================================
        # 获取传入的日期，并通过日期来确定用户选择的是几月的
        # =======================================================================
        user_id = self.ReqData.get("username")
        if not (user_id and int(user_id) > 0):
            user_id = None
        start = self.get_bill_date(self.DateFrom)
        end = self.get_bill_date(self.DateTo)
        return jsonify(self.get_bill_data(user_id, start, end))

    def delete_bill_manager(self):
        """
        @attention: 返回时间段的账单数据并删除
        """
        self.ReqData = request.form.to_dict()
        operate = dataUtil.getDataBase("bill", "Finance")
        operate.delete_model(self.ReqData.get("bill_id"))
        state = operate.delete()[0]
        if not state:
            return dataUtil.ResErrorJson(u"删除数据失败")
        return dataUtil.ResOkJson(u"删除数据成功")

    def load_all(self, operate):
        if operate.lower() != 'bill_manager':
            return []

        date = dataUtil.CurrentDateStr.split("-")
        date = "%s-%s-01" % (date[0], date[1])
        data = self.get_bill_data(None, date, date)
        if data.get("state"):
            return data.get("msg").get("data")
        return []

    @staticmethod
    def write_error(error):
        down = current_app.config.get("DOWNLOAD_FILE")
        _log = "%s_calculate_bill.log" % (current_user.username)
        _file = os.path.join(down, _log)
        fp = open(_file, "w+")
        string = "\r\n".join(error)
        fp.write(string)
        fp.close()
        return _log

    def calculate_bill(self):
        self.ReqData = request.form.to_dict()
        start = self.ReqData.get("dateFrom")
        end = self.ReqData.get("dateTo")
        user_id = self.ReqData.get("customer_id")
        if not start:
            return dataUtil.ResErrorJson(u"请选择开始日期")
        errors = _BillService.update_bill_all(start, end, user_id)
        if not errors:
            return dataUtil.ResOkJson(u"重新计算所有的账单信息,成功")

        return dataUtil.ResErrorJson(u"计算部分账单信息成功,请查看%中的错误信息" % self.write_error(errors))


_searchUtil = Search()
