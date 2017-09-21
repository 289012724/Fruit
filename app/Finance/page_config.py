# usr/bin/env
# -*- coding:utf-8 -*-
"""
@version: triweb version 1.0
@author: shuiyaoyao
@contact: 289012724@qq.com
@time: 

"""
import copy
_rebund = [
         {'field': 'id', 'title': u'编号', 'width': 60},
         {'field': 'date', 'title': u'还款时间', 'width': 100},
         {'field': 'customer_id', 'title': u'客户', 'width': 80},
         {'field': 'tickets', 'title': u'凭据号', 'width': 100},
         {'field': 'money_type', 'title': u'还款类型', 'width': 100},
         {'field': 'money_price', 'title': u'还款金额', 'width': 80},
         {'field': 'operator_id', 'title': u'经办人', 'width': 80},
         {'field': 'bill_id', 'title': u'账单号', 'width': 130},
         {'field': 'notice', 'title': u'备注', 'width': 100}, 
         ]

_rebate  = [
         {'field': 'id', 'title': u'编号', 'width': 60},
         {'field': 'date', 'title': u'折扣时间', 'width': 100},
         {'field': 'customer_id', 'title': u'客户', 'width': 80},
         {'field': 'tickets', 'title': u'凭据号', 'width': 100},
         {'field': 'money_price', 'title': u'折扣金额', 'width': 100},
         {'field': 'description', 'title': u'折扣说明', 'width': 150},
         {'field': 'operator_id', 'title': u'经办人', 'width': 80},
         {'field': 'bill_id', 'title': u'账单号', 'width': 130},
         {'field': 'notice', 'title': u'备注', 'width': 100}, 
         ]

_writeoff = copy.deepcopy(_rebate)
_writeoff[1]['title']  = u'冲销时间'
_writeoff[4]['title']  = u'冲销金额'
_writeoff[5]['title']  = u'冲销说明'

def addCenter(cell):
    for _c in cell:
        if _c.get("field")=="id":
            _c.update({'hidden':True})
        _c.update({'align':'center'})
    return cell
page_table_configs ={
    "rebund":addCenter(_rebund),
    "rebate":addCenter(_rebate),
    "writeoff":addCenter(_writeoff)
    }
