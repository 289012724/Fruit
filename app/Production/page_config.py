# usr/bin/env
# -*- coding:utf-8 -*-
"""
@version: triweb version 1.0
@author: shuiyaoyao
@contact: 289012724@qq.com
@time: 
"""
import copy
_sell = [{'field': 'id', 'title': u'编号', 'width': 60},
         {'field': 'date', 'title': u'销售时间', 'width': 80},
         {'field': 'tickets', 'title': u'凭据号', 'width': 80},
         {'field': 'name', 'title': u'品名', 'width': 80},
         {'field': 'brand_id', 'title': u'品牌', 'width': 80},
         {'field': 'standard', 'title': u'规格', 'width': 80},
         {'field': 'sell_type', 'title': u'类别', 'width': 40},
         {'field': 'customer_id', 'title': u'客户', 'width': 60},
         {'field': 'support_id', 'title': u'供货商', 'width': 60},
         {'field': 'operator_id', 'title': u'经办人', 'width': 60},
         {'field': 'number', 'title': u'数量', 'width': 50},
         {'field': 'price', 'title': u'单价', 'width': 80,"formatter":"1"},
         {'field': 'price_a', 'title': u'备注单价', 'width': 80,"formatter":"1"},
         {'field':'total_price','title':u'总价','width':120,"formatter":"1"},
         {'field': 'money_id', 'title': u'已收货款', 'width': 80,"formatter":"1"},
         {'field': 'notice', 'title': u'备注', 'width': 100}, 
         {'field': 'notice_a', 'title': u'备注A', 'width': 80} 
         ]
_stock = [{'field': 'id', 'title': u'编号', 'width': 60},
         {'field': 'date', 'title': u'入库时间', 'width': 80},
         {'field': 'tickets', 'title': u'凭据号', 'width': 100},
         {'field': 'name', 'title': u'品名', 'width': 100},
         {'field': 'brand_id', 'title': u'品牌', 'width': 100},
         {'field': 'standard', 'title': u'规格', 'width': 100},
         {'field': 'car_number', 'title': u'车牌柜号', 'width': 80},
         {'field': 'category', 'title': u'类别', 'width': 60},
         {'field': 'support_id', 'title': u'供货商', 'width': 60},
         {'field': 'notice', 'title': u'入库备注', 'width': 100},
         {'field': 'notice_a', 'title': u'备注A', 'width': 80},
         {'field': 'number', 'title': u'数量', 'width': 60},
         {'field': 'price', 'title': u'单价', 'width': 80,"formatter":"1"},
         {'field': 'all_money', 'title': u'金额', 'width': 100,"formatter":"1"},
         {'field': 'operator_id', 'title': u'经办人', 'width': 60},
         {'field': 'isout', 'title': u'已售完', 'width': 60},
         ]
_roll_back = [{'field': 'id', 'title': u'编号', 'width': 60},
              {'field': 'date', 'title': u'退货时间', 'width': 80},
              {'field': 'tickets', 'title': u'凭证号', 'width': 80},
              {'field': 'customer_id', 'title': u'客户', 'width': 80},
              {'field': 'name', 'title': u'品名', 'width': 80},
              {'field': 'sell_id', 'title': u'销售凭证', 'width': 80},
              {'field': 'number', 'title': u'数量', 'width': 80},
              {'field': 'money_id', 'title': u'已退货款', 'width': 80},
              {'field': 'reason', 'title': u'退货原因', 'width': 120},
              {'field': 'notice', 'title': u'备注', 'width': 100},
              {'field': 'notice_a', 'title': u'备注A', 'width': 80},
              {'field': 'operator_id', 'title': u'经办人', 'width': 80},
              {'field': 'sell_id_k', 'title': u'销售编号', 'width': 60},
              ]

_roll_out  = [{'field': 'id', 'title': u'编号', 'width': 60},
              {'field': 'date', 'title': u'转出时间', 'width': 100},
              {'field': 'tickets', 'title': u'凭证号', 'width': 100},
              {'field': 'stock_id', 'title': u'品名', 'width': 80},
              {'field': 'reason', 'title': u'转出原因', 'width': 100},
              {'field': 'number', 'title': u'数量', 'width': 80},
              {'field': 'operator_id', 'title': u'经办人', 'width': 80},
              {'field': 'notice', 'title': u'备注', 'width': 100},
              {'field': 'notice_a', 'title': u'备注A', 'width': 80},
              {'field': 'stock_notice', 'title': u'入库备注', 'width': 100}
            ]
_roll_out_1 = copy.deepcopy(_roll_out)
_roll_out_1[1]['title'] =u'报损时间'
_roll_out_1[4]['title'] =u'报损原因'

_stock_column = [{'field': 'id', 'title': u'编号', 'width': 60},
            {'field': 'date', 'title': u'日期', 'width': 100},
            {'field': 'name', 'title': u'品名', 'width': 100},
            {'field': 'brand_id', 'title': u"品牌", 'width': 60},
            {'field': 'standard', 'title': u'规格', 'width': 100},
            {'field': 'category', 'title': u'类别', 'width': 40},
            {'field': 'car_number', 'title': u'车牌柜号', 'width': 60},
            {'field': 'support_id', 'title': u'供应商', 'width': 60},
            {'field': 'notice', 'title': u'备注', 'width': 80},
            {'field': 'notice_a', 'title': u'备注A', 'width': 80}
            ]

roll_back_sell_column=[
    {'field': 'id', 'title': u'编号', 'width': 60},
    {'field': 'date', 'title': u'销售时间', 'width': 100},
    {'field': 'customer_id', 'title': u'客户', 'width': 80},
    {'field': 'name', 'title': u'品名', 'width': 80},
    {'field': 'tickets', 'title': u'凭据号', 'width': 80},
    {'field': 'number', 'title': u'销售数量', 'width': 80},
    {'field': 'number_back', 'title': u'已退数量', 'width': 80},
    ]

def addCenter(cell):
    for _c in cell:
        if _c.get("field")=="id":
            _c.update({'hidden':True})
        _c.update({'align':'center'})
    return cell

page_table_configs ={
    "stock_column":addCenter(_stock_column),
    "stock":addCenter(_stock),
    "sell":addCenter(_sell),
    "rollout":addCenter(_roll_out),
    "rollback":addCenter(_roll_back),
    "rollloss":addCenter(_roll_out_1)
    }
