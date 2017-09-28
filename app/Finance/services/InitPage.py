# -*- coding:utf-8 -*-
'''
@author: shuiyaoyao
@email  : 289012724@qq.com
'''
from ...common import _dataBaseUtil    as dataUtil
from ...common import _formOperateUtil as formUtil
from flask import request
from flask_login import current_user
from sqlalchemy import desc
import copy
from BillService import _BillService

_finance = "Finance"
_user = "User"
_getOper = dataUtil.GetPartial(_finance)
_getForm = formUtil.GetPartial(_finance)
DateFormat = '%Y-%m-%d'


# ===============================================================================
# 在账单数据处理的过程中关闭开启所有的事务操作
# ===============================================================================
# 所有的还款和往来数据都绑定到最新的账单上面,不用管其他任何数据
# 先尝试添加和更新 还款数据 ，然后在自动更新对账单的影响，如果更新账单失败，尝试回滚
# 如果回滚失败，则致命性失败，需要重新录入数据,然后在自动计算当月的账单信息
# ===============================================================================
class InitPage:
    @property
    def FormError(self):
        return self.__formError

    @FormError.setter
    def FormError(self, value):
        self.__formError = value

    def CheckFrom(self, form):
        self.FormError = None
        if form.is_submitted() or request.method.upper() == "POST":
            if form.validate_on_submit():
                return True
            self.FormError = form.errors
        return False

    def GetBillDate(self, date):
        """
        @attention: 生产单的唯一标记号
        @param date: 时间节点
        """
        return _BillService.GetBillDate(date)

    def GetBillChoices(self, userid):
        """
        @attention: 获取当前的账单信息
        @param userid: 用户id号 
        """
        _oper = _getOper("bill")
        models = _oper.GetLast12Model(userid)
        data = [{'id': model.id, 'tickets': model.tickets} for model in models]
        return data

    def GetCustomerChoices(self):
        """
        @attention: 获取用户选择项目
        """
        data = dataUtil.GetDataByUrl("CustomerChoice", "User")()
        _ok = [{"id": cell[0], 'username': cell[1]} for cell in data]
        return _ok

    def _add_model(self, _ses, model, date):
        date = self.GetModelDate(model)
        date = _BillService.GetBillDate(date)
        bill = _BillService.GetBill(model.customer_id, date)
        if not bill:
            return

        model.bill_id = bill.id
        _ses.add(model)
        try:
            _ses.commit()
            cuser = model.customer_id
            if not self._adjust_bill(cuser, date, cuser, date):
                self.error = dataUtil.ResError(_BillService.GetError())
        except Exception, e:
            _ses.delete(bill)
            _ses.commit()
            self.error = dataUtil.ResError(u"添加信息失败")

    def _add_new(self, _ses, model):
        """
        @attention: 向数据库中添加新的账单信息
        """
        price = model.money_price
        opt = model.operator_id
        user = model.customer_id
        date = self.GetModelDate(model)
        date = _BillService.GetBillDate(date)
        if _BillService.AddNew(_ses, date=date, next_money=price,
                               level_money=-price, operator_id=opt, customer_id=user):
            try:
                _ses.commit()
                self._add_model(_ses, model, date)
            except Exception, e:
                print e, u"添加新的账单失败"
                self.error = dataUtil.ResError(u"保存数据失败")

    def _adjust_bill(self, cuser, cdate, ouser, odate):
        return _BillService.UpdateAllByNext(cuser, cdate, ouser, odate)

    def get_model_bill_id(self, model):
        date = self.GetModelDate(model)
        date = _BillService.GetBillDate(date)
        bill = _BillService.GetBill(model.customer_id, date)
        model.bill_id = bill.id

    def _toUpdate(self, _ses, model, ouser, odate):
        self.get_model_bill_id(model)
        cuser = model.customer_id
        cdate = self.GetModelDate(model)
        _ses.add(model)
        try:
            _ses.commit()
            if not self._adjust_bill(cuser, cdate, ouser, odate):
                self.error = dataUtil.ResError(_BillService.GetError())
        except Exception, e:
            print e
            self.error = dataUtil.ResError(u"更新数据失败")

    def GetModelDate(self, model):
        try:
            return model.date.strftime("%Y-%m-%d")
        except:
            try:
                return model.date()
            except:
                return "%s" % model.date

    def _has_bill(self, user_id, date):
        return _BillService.HasBill(user_id, date)

    def dispatcher(self, _ses, model, old_user, date):
        if self._has_bill(model.customer_id, self.GetModelDate(model)):
            self._toUpdate(_ses, model, old_user, date)
        else:
            self.error = dataUtil.ResError(u"未获得相关账单信息,不能更新此条还款信息,请联系开发人员")

    def add_model_dispatcher(self, _ses, model):
        if self._has_bill(model.customer_id, self.GetModelDate(model)):
            self.get_model_bill_id(model)
            _ses.add(model)
            try:
                _ses.commit()
                cuser = model.customer_id
                date = self.GetModelDate(model)
                if not self._adjust_bill(cuser, date, cuser, date):
                    self.error = dataUtil.ResError(_BillService.GetError())
            except:
                self.error = dataUtil.ResError(u"添加数据失败")
        else:
            self._add_new(_ses, model)

    def __add_model(self, _oper, model):
        """
        @attention:  在添加数据的时候,报需要添加的模型添加到事务中
        """
        _ses = _oper.Session
        self.error = None
        self.add_model_dispatcher(_ses, model)
        if self.error is not None:
            return self.error
        data = _oper.get_data([model], True)[-1]
        data = dataUtil.ResOk(data)
        return data

    def GetRebund(self):
        """
        @attention: 生成用户还款的信息,当用户的还款信息添加成功的时候,
        更新用户的下月还款数据
        """
        form = _getForm("RefundForm")
        date = dataUtil.CurrentDateStr
        flag = False
        if self.CheckFrom(form):
            form.operator_id.data = current_user.id
            _oper = _getOper("rebund")
            state, model = _oper.add_model(form)
            if state and model:
                form = self.__add_model(_oper, model)
                _oper.init_modelList()
            else:
                form = dataUtil.ResError(u"添加客户还款信息失败")
                print model
            flag = True
        if self.FormError:
            flag = True
        return flag, form, date

    def GetRebate(self, operType):
        """
        @attention: 生成用户冲销和折扣的信息,
        当用户的冲销和折扣添加成功的时候,更新用户的下月还款数据
        """
        date = dataUtil.CurrentDateStr
        if operType == 'rebate':
            form = _getForm("RebateForm")
        else:
            form = _getForm("WriteOffForm")
        flag = False
        if self.CheckFrom(form):
            _oper = _getOper(operType)
            form.operator_id.data = current_user.id
            state, model = _oper.add_model(form)
            if state and model:
                form = self.__add_model(_oper, model)
                _oper.init_modelList()
            else:
                form = dataUtil.ResError(u"添加信息失败")
            flag = True
        if self.FormError:
            flag = True
        return flag, form, date

    def _get_moth_day(self, current):
        year, moth = [int(c) for c in current.split("-")][:-1]
        if moth > 3:
            moth = int(moth) - 3
        else:
            year -= 1
            moth = [10, 11, 12][moth - 1]
        prev = "%s-%02d-01" % (year, moth)
        return prev

    def _get_3_moth(self, model, curentData):
        prev = self._get_moth_day(curentData)
        _query = model.query.filter(model.date >= prev,
                                    model.date <= curentData)
        _query = _query.order_by(desc(model.date))
        return _query

    def GetAllData(self, operType):
        """
        @attention: 获取用户当前日期输入的财务数据
        """
        _oper = _getOper(operType.lower())
        model = _oper.model
        _query = self._get_3_moth(model, dataUtil.CurrentDateStr)
        if current_user.username not in ['admin', 'author']:
            _query = _query.filter(model.operator_id == current_user.id)
        model = _query.order_by(desc(model.date)).all()
        if model:
            data = _oper.get_data(model, True)[-1]
            return data
        return []

    def _adjust_bill_money(self, _ses, model):
        bill = model.bill
        bill.next_money -= model.money_price
        bill.level_money = bill.total_money - bill.next_money
        return bill

    def _delete_cell(self, _oper, model):
        """
        @attention: 在删除的过程中，不把需要删除的模型添加到事务中
        在模型删除的过程中，先尝试去更新关联的数据,
        同时已经付款的状态标记值不变
        """
        _ses = _oper.Session
        bill = self._adjust_bill_money(_ses, model)
        _ses.delete(model)
        _ses.add(bill)
        try:
            _ses.commit()
            return dataUtil.ResOk(u"删除数据成功")
        except Exception, e:
            print e
            return dataUtil.ResError(u"删除数据失败")

    def DeleteCell(self, _dictData):
        """
        @attention: 删除一个财务数据
        @param _dictData:类型和id号 
        """
        operType = _dictData.get("operType")
        data_id = _dictData.get("production_id")
        if not (operType and data_id):
            return dataUtil.ResError(u"选择的数据有误")

        _oper = _getOper(operType)
        state, model = _oper.delete_model(data_id)
        if state and model:
            return self._delete_cell(_oper, model)
        else:
            return dataUtil.ResError(u"删除数据失败")

    def __updateBill(self, _oper, model, ouser, odate):
        """
        @attention: 当用户更新了财务中的数据的时候需要更新当前账单数据,
        以及后面有关联的数据
        @param cell_model:当前修正的数据
        @param _prev_price:之前的数据
        """
        _ses = _oper.Session
        self.dispatcher(_ses, model, ouser, odate)
        if self.error is not None:
            return self.error

        _data = _oper.get_data([model], True)[-1]
        form = dataUtil.ResOk(_data)
        return form

    def __getModifyModel(self, operType, dataId):
        """
        @attention: 获取修正对象的数据和模型
        @param operType: 修正的类型
        @param dataId:修正数据的id号
        """
        _oper = _getOper(operType)
        _model = dataUtil.getModel(_oper, id=dataId)
        _data = _oper.get_data(_model, True)[-1][0]
        return _oper, _data, _model

    def _get_modify_form(self, _oper, _model, _data, form):
        """
        @attention: 获取修改页面
        """
        _state = False
        date = _data.get("date")
        data = _oper.get_data(_model, True)[-1][0]
        data.pop('date')
        formUtil.setFormData(form, data)
        form.operator_id.data = data.get("operator_id")
        return date

    def UpdateDispatcher(self, _oper, model, ouser, odate):
        """
        @attention: 模型修改分发器
        """
        self.error = None
        form = self.__updateBill(_oper, model, ouser, odate)
        # 最后将模型操作对象清空
        _oper.init_modelList()
        return form

    def GetOperateForm(self, operType):
        _form = {'rebund': "RefundForm",
                 "writeoff": 'WriteOffForm',
                 "rebate": "RebateForm"}
        form = _getForm(_form.get(operType.lower()))
        return form

    def Modify(self, operType, dataId):
        """
        @attention: 修正财务数据,修正的时候会更新账单数据
        @param operType: 修正的类型
        @param dataId:修正数据的id号
        
        """
        form = self.GetOperateForm(operType)
        form.customer_id.choices = dataUtil.GetDataByUrl("CustomerChoice", "User")()
        _oper, _data, _model = self.__getModifyModel(operType, dataId)
        _state, date = True, None
        if self.CheckFrom(form):
            form.operator_id.data = current_user.id
            if _model:
                model = _model[0]
                form.bill_id.data = model.bill.id
                ouser = model.customer_id
                odate = self.GetModelDate(model)
                # 保存起来以便失败可以用
                self._temp = copy.deepcopy(model)
                state, model = _oper.update_model(model, form)
                if state and model:
                    form = self.UpdateDispatcher(_oper, model, ouser, odate)
                else:
                    print model
                    form = dataUtil.ResError(u"更新模型失败")
            else:
                form = dataUtil.ResError(u"选择的模型不存在,请刷新后在操作")
        else:
            _state = False
            date = self._get_modify_form(_oper, _model, _data, form)
        return _state, form, date

    # ===========================================================================
    # 财务数据搜索
    # ===========================================================================
    def _fun(self, query, model, form, key, isEqual=True):
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
            if isEqual:
                query = query.filter(_type == data)
            else:
                query = query.filter(_type.like("%s" % data))
        return query

    def Search(self, operType):
        form = _getForm("SearchForm")
        if self.CheckFrom(form):
            _oper = _getOper(operType.lower())
            model = _oper.model
            _query = model.query
            _query = self._fun(_query, model, form, "tickets", False)
            _query = self._fun(_query, model, form, "notice", False)
            if form.operator_id.data != -1:
                _query = self._fun(_query, model, form, "operator_id")
            if form.customer_id.data != -1:
                _query = self._fun(_query, model, form, "customer_id")
            if form.dateFrom.data:
                _query = _query.filter(model.date >= form.dateFrom.data,
                                       model.date <= form.dateTo.data)
            if operType.lower() != "rebund":
                _query = self._fun(_query, model, form, "description", False)
            models = _query.all()
            if models:
                state, model = _oper.get_data(models, True)
                if state and model:
                    return True, dataUtil.ResOk(model)
                else:
                    return True, dataUtil.ResError(u"获取数据失败,请检查与之对应的账单是否已经被删除?")
            else:
                return True, dataUtil.ResError(u"没有符合条件的数据")
        if self.FormError:
            return True, dataUtil.ResError(self.FormError)
        form.dateDefault.data = dataUtil.CurrentDateStr
        if operType == "rebate":
            form.description.label.text = u"折扣说明"
        return False, form


_initPageUtil = InitPage()
